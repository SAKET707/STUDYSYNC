import logging
import uuid
from typing import List, Tuple
from ingestion.schemas import ParsedDocument, ParentChunk, ChildChunk, ChunkMetadata, ChunkType

logger = logging.getLogger(__name__)

class ParentChildChunker:
    """
    Component 2 of the Ingestion Pipeline.
    Responsibility: Slice a ParsedDocument into strongly-linked Parent and Child chunks.
    Enforces configuration safety boundaries, zero text loss, and strict traceability.
    """
    
    def __init__(
        self, 
        parent_word_limit: int = 375,  
        child_word_limit: int = 115,  
        child_overlap: int = 25        
    ):
        if child_overlap >= child_word_limit:
            logger.error(f"Configuration mismatch: child_overlap ({child_overlap}) >= child_word_limit ({child_word_limit})")
            raise ValueError("child_overlap must be strictly smaller than child_word_limit to prevent infinite processing loops.")
            
        if child_word_limit >= parent_word_limit:
            logger.error(f"Configuration mismatch: child_word_limit ({child_word_limit}) >= parent_word_limit ({parent_word_limit})")
            raise ValueError("child_word_limit must be smaller than parent_word_limit for meaningful child segmentation.")

        self.parent_word_limit = parent_word_limit
        self.child_word_limit = child_word_limit
        self.child_overlap = child_overlap

    def _split_into_parents(self, text: str) -> List[str]:
        """
        Processes text sequentially by natural paragraphs. Hard-splits monster
        blocks exceeding the target configuration parameters.
        """
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        parent_texts = []
        current_chunk = []
        current_word_count = 0
        
        for para in paragraphs:
            words_in_para = para.split()
            para_word_count = len(words_in_para)
            
            
            if para_word_count > self.parent_word_limit:
                if current_chunk:
                    parent_texts.append(" ".join(current_chunk))
                    current_chunk = []
                    current_word_count = 0
                
                for i in range(0, para_word_count, self.parent_word_limit):
                    slice_words = words_in_para[i:i + self.parent_word_limit]
                    parent_texts.append(" ".join(slice_words))
                continue
                
            if current_word_count + para_word_count > self.parent_word_limit:
                parent_texts.append(" ".join(current_chunk))
                current_chunk = [para]
                current_word_count = para_word_count
            else:
                current_chunk.append(para)
                current_word_count += para_word_count
                
        if current_chunk:
            parent_texts.append(" ".join(current_chunk))
            
        return parent_texts

    def _create_children_from_parent(self, parent_text: str) -> List[str]:
        """
        Slices text into smaller child entities using a validated sliding window step.
        Guarantees trailing structural fragments are merged to eliminate information leaks.
        """
        words = parent_text.split()
        if len(words) <= self.child_word_limit:
            return [parent_text]
            
        child_texts = []
        start = 0
        
        while start < len(words):
            end = start + self.child_word_limit
            child_slice = words[start:end]
            
            
            if len(child_slice) < self.child_word_limit:
                if child_texts:
                    child_texts[-1] = child_texts[-1] + " " + " ".join(child_slice)
                else:
                    child_texts.append(" ".join(child_slice))
                break
                
            child_texts.append(" ".join(child_slice))
            start += (self.child_word_limit - self.child_overlap)
            
        return child_texts

    def chunk_document(
        self, 
        doc: ParsedDocument, 
        document_id: str
    ) -> Tuple[List[ParentChunk], List[ChildChunk]]:
        """
        Converts a structural document instance into linked Parent and Child chunk lists.
        """
        parent_chunks: List[ParentChunk] = []
        child_chunks: List[ChildChunk] = []
        
        raw_parents = self._split_into_parents(doc.text)
        
        for p_idx, p_text in enumerate(raw_parents):
            parent_num = p_idx + 1 
            parent_uuid = str(uuid.uuid4())
            section_label = f"Section_{parent_num}"
            
            # Setup Parent Object
            parent_metadata = ChunkMetadata(
                document_id=document_id,
                class_number=doc.class_number,
                subject=doc.subject,
                chapter=doc.chapter,
                section=section_label,
                parent_index=parent_num,
                child_index=None,
                parent_id=None,
                chunk_type=ChunkType.PARENT
            )
            
            parent_chunks.append(ParentChunk(
                id=parent_uuid,
                text=p_text,
                metadata=parent_metadata
            ))
            
            
            raw_children = self._create_children_from_parent(p_text)
            
            for c_idx, c_text in enumerate(raw_children):
                child_num = c_idx + 1
                child_uuid = str(uuid.uuid4())
                
                child_metadata = ChunkMetadata(
                    document_id=document_id,
                    class_number=doc.class_number,
                    subject=doc.subject,
                    chapter=doc.chapter,
                    section=section_label,
                    parent_index=parent_num,
                    child_index=child_num,
                    parent_id=parent_uuid,
                    chunk_type=ChunkType.CHILD
                )
                
                child_chunks.append(ChildChunk(
                    id=child_uuid,
                    text=c_text,
                    metadata=child_metadata
                ))
                
        logger.info(
            f"Chunking Complete -> Ingestion Metrics Summary:"
            f"\n\tDocument ID: {document_id}"
            f"\n\tParents Stored: {len(parent_chunks)}"
            f"\n\tChildren Stored: {len(child_chunks)}"
        )
        
        return parent_chunks, child_chunks