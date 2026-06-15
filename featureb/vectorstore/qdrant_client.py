import logging
from typing import List, Optional, Union
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, ScoredPoint

from config.constants import COLLECTION_NAME, EMBEDDING_DIMENSION
from ingestion.schemas import (
    IngestionResult,
    EmbeddedChunk,
    ParentChunk,
    ChildChunk,
    ChunkMetadata,
    ChunkType
)
# Added domain model for the new retrieval architecture
from retrieval.schema import ParentContext

logger = logging.getLogger(__name__)

class QdrantVectorStore:
    """
    Data Repository Layer Module.
    Responsibility: Handle standard CRUD operations, bulk transactional upserts,
    metadata-filtered chapter browsing, and similarity lookups against the Qdrant vector space.
    """

    def __init__(self, client: QdrantClient):
        self.client = client

    def _map_chunk_to_point(self, embedded_chunk: EmbeddedChunk) -> PointStruct:
        """
        Internal Transformer Core. Maps an EmbeddedChunk into a native Qdrant PointStruct,
        ensuring the clean chunk text is preserved inside the payload field.
        """
        chunk = embedded_chunk.chunk
        metadata = chunk.metadata

        payload = {
            "text": chunk.text,  
            "document_id": metadata.document_id,
            "class_number": metadata.class_number,
            "subject": metadata.subject,
            "chapter": metadata.chapter,
            "section": metadata.section,
            "parent_index": metadata.parent_index,
            "child_index": metadata.child_index,
            "parent_id": metadata.parent_id,
            "chunk_type": metadata.chunk_type.value
        }

        return PointStruct(
            id=chunk.id,
            vector=embedded_chunk.embedding,
            payload=payload
        )

    def upsert_chunks(self, embedded_chunks: List[EmbeddedChunk]) -> None:
        """
        Executes a high-speed batch transactional write for a sequence of embedded points.
        """
        if not embedded_chunks:
            logger.warning("Upsert requested with empty embedded chunk collection.")
            return

        logger.info(f"Mapping and packing {len(embedded_chunks)} records into PointStruct vectors...")
        points = [self._map_chunk_to_point(ec) for ec in embedded_chunks]

        try:
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
                wait=True  
            )
            logger.info(f"Batch transactional upload complete for {len(points)} vector records.")
        except Exception as e:
            logger.exception(f"Fatal write failure encountered during chunk batch upsert: {e}")
            raise

    def upsert_ingestion_result(self, result: IngestionResult) -> None:
        """
        Optimized Unified Orchestration Hook. Merges Parent contexts and Child targets
        into a single consolidated list to complete ingestion in one single network call.
        """
        logger.info(f"Initiating optimized transactional dataset flush for Document ID: {result.document_id}")
        
        all_embedded_chunks = result.embedded_parents + result.embedded_children
        
        if not all_embedded_chunks:
            logger.warning(f"No payload items extracted to write for Document ID: {result.document_id}")
            return
            
        logger.info(f"Executing batch upload for a combined total of {len(all_embedded_chunks)} parent and child points.")
        self.upsert_chunks(all_embedded_chunks)
        logger.info(f"Ingestion result completely committed to Qdrant cluster for Doc ID: {result.document_id}")

    def get_parent_contexts(
        self, 
        class_number: int, 
        chapter: str, 
        offset: int, 
        limit: int
    ) -> List[ParentChunk]:
        """
        Deterministically fetches a sequence of textbook parent chunks.
        Returns base `ParentChunk` objects to keep the repository decoupled from retrieval logic.
        """
        logger.debug(f"Executing DB scroll for Class {class_number}, Chapter '{chapter}' (Offset: {offset}, Limit: {limit})")

        conditions = [
            FieldCondition(key="class_number", match=MatchValue(value=class_number)),
            FieldCondition(key="chapter", match=MatchValue(value=chapter)),
            FieldCondition(key="chunk_type", match=MatchValue(value=ChunkType.PARENT.value))
        ]
        query_filter = Filter(must=conditions)

        try:
            records, _ = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=query_filter,
                limit=10000, 
                with_payload=True,
                with_vectors=False
            )

            if not records:
                return []

          
            records.sort(key=lambda r: r.payload.get("parent_index", 0))

        
            paginated_records = records[offset : offset + limit]

            parent_chunks = []
            for record in paginated_records:
                payload = record.payload
                meta = ChunkMetadata(
                    document_id=payload.get("document_id", ""),
                    class_number=payload.get("class_number", 0),
                    subject=payload.get("subject", ""),
                    chapter=payload.get("chapter", ""),
                    section=payload.get("section", ""),
                    parent_index=payload.get("parent_index", 0),
                    child_index=payload.get("child_index", 0),
                    parent_id=payload.get("parent_id", ""),
                    chunk_type=ChunkType(payload.get("chunk_type", "parent"))
                )
                parent_chunks.append(
                    ParentChunk(id=str(record.id), text=payload.get("text", ""), metadata=meta)
                )

            return parent_chunks

        except Exception as e:
            logger.error(f"Failed to scroll and fetch parent chunks from Qdrant: {e}")
            raise

    def get_point_by_id(self, point_id: str) -> Optional[Union[ParentChunk, ChildChunk]]:
        """
        Fetches a singular specific record by its unique UUID string.
        Rebuilds the corresponding Pydantic domain chunk to keep application layer decoupled.
        """
        try:
            results = self.client.retrieve(
                collection_name=COLLECTION_NAME,
                ids=[point_id],
                with_payload=True,
                with_vectors=False
            )
            
            if not results:
                logger.warning(f"No database records found matching targeting ID: '{point_id}'")
                return None
                
            payload = results[0].payload
            
            meta = ChunkMetadata(
                document_id=payload["document_id"],
                class_number=payload["class_number"],
                subject=payload["subject"],
                chapter=payload["chapter"],
                section=payload["section"],
                parent_index=payload["parent_index"],
                child_index=payload["child_index"],
                parent_id=payload["parent_id"],
                chunk_type=ChunkType(payload["chunk_type"])
            )
            
            if meta.chunk_type == ChunkType.PARENT:
                return ParentChunk(id=point_id, text=payload["text"], metadata=meta)
            else:
                return ChildChunk(id=point_id, text=payload["text"], metadata=meta)
                
        except Exception as e:
            logger.error(f"Failed direct lookup for targeting node ID '{point_id}': {e}")
            raise

    def search(self, query_embedding: List[float], top_k: int = 20) -> List[ScoredPoint]:
        """
        Executes a basic vector similarity lookup across the absolute collection space.
        Guarded with an active query vector dimension verification check.
        """
        actual_dim = len(query_embedding) if query_embedding else 0
        if actual_dim != EMBEDDING_DIMENSION:
            logger.error(f"Vector search aborted. Expected dimension {EMBEDDING_DIMENSION}, received {actual_dim}")
            raise ValueError(f"Expected embedding dimension {EMBEDDING_DIMENSION}, received {actual_dim}")

        try:
            response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
            with_payload=True
            )
            return response.points
        except Exception as e:
            logger.error(f"Global vector sweep failed: {e}")
            raise

    def search_with_filters(
        self, 
        query_embedding: List[float], 
        class_number: Optional[int] = None,
        chapter: Optional[str] = None,
        top_k: int = 20
    ) -> List[ScoredPoint]:
        """
        Advanced Core Retrieval Hook. Automatically applies pre-filtering restrictions
        to focus searches on child nodes and completely isolate chapter contexts.
        Guarded with an active query vector dimension verification check.
        """
        actual_dim = len(query_embedding) if query_embedding else 0
        if actual_dim != EMBEDDING_DIMENSION:
            logger.error(f"Scoped vector search aborted. Expected dimension {EMBEDDING_DIMENSION}, received {actual_dim}")
            raise ValueError(f"Expected embedding dimension {EMBEDDING_DIMENSION}, received {actual_dim}")

        conditions = []
        
        conditions.append(
            FieldCondition(key="chunk_type", match=MatchValue(value=ChunkType.CHILD.value))
        )
        
        if class_number is not None:
            conditions.append(
                FieldCondition(key="class_number", match=MatchValue(value=class_number))
            )
            
        if chapter is not None:
            conditions.append(
                FieldCondition(key="chapter", match=MatchValue(value=chapter))
            )
            
        query_filter = Filter(must=conditions)
        
        logger.info(f"Executing scoped vector search sweep against {COLLECTION_NAME} (Limit: {top_k}).")
        try:
            response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True
            )
            return response.points
        except Exception as e:
            logger.error(f"Filtered vector similarity sweep execution failed: {e}")
            raise

    def delete_document(self, document_id: str) -> None:
        """
        Cleans up and removes all tracking points linked to a specific document ID.
        Prevents index duplication errors when re-ingesting content.
        """
        logger.warning(f"Initiating full index clean for historical instances matching Document ID: {document_id}")
        try:
            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=Filter(
                    must=[
                        FieldCondition(key="document_id", match=MatchValue(value=document_id))
                    ]
                )
            )
            logger.info(f"Index space successfully cleared for Document ID: {document_id}")
        except Exception as e:
            logger.error(f"Failed to clear historical records for Document ID {document_id}: {e}")
            raise