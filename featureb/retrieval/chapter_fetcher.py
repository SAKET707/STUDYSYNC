import logging
from typing import List


from retrieval.schema import ParentContext
from vectorstore.qdrant_client import QdrantVectorStore

logger = logging.getLogger(__name__)

class ChapterContextFetcher:
    """
    Retrieval Layer Delegator.
    Responsibility: Converts API pagination into database offsets, delegates 
    the fetch execution to the Repository layer, and MAPS the database chunks 
    into strict Retrieval Pipeline contexts.
    """

    def __init__(self, vector_store: QdrantVectorStore):
        self.vector_store = vector_store

    def fetch_contexts(
        self,
        class_number: int,
        chapter: str,
        page: int,
        context_limit: int
    ) -> List[ParentContext]:
        """
        Calculates pagination offset, fetches base chunks, and maps them to pipeline schemas.
        """
        
        offset = (page - 1) * context_limit
        
        logger.debug(
            f"Delegating Chapter Fetch -> Class: {class_number} | "
            f"Chapter: '{chapter}' | Offset: {offset} | Limit: {context_limit}"
        )

        try:
          
            base_chunks = self.vector_store.get_parent_contexts(
                class_number=class_number,
                chapter=chapter,
                offset=offset,
                limit=context_limit
            )
            
           
            parent_contexts = [
                ParentContext(parent_id=chunk.id, text=chunk.text)
                for chunk in base_chunks
            ]
            
            return parent_contexts

        except Exception as e:
            logger.error(f"Fatal error during chapter context fetch delegation: {e}")
            return []