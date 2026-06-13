import logging
import uuid
import time
from ingestion.schemas import IngestionResult, ParsedDocument
from ingestion.pdf_parser import PDFParser
from ingestion.chunker import ParentChildChunker
from ingestion.embedder import TextbookEmbedder

logger = logging.getLogger(__name__)

class IngestionCoordinator:
    """
    Component 4: The Project Manager.
    Responsibility: Linearly coordinate specialists (Parser, Chunker, Embedder),
    profile pipeline performance, and assemble the final vectorizable payloads.
    """
    
    def __init__(
        self,
        parser: PDFParser,
        chunker: ParentChildChunker,
        embedder: TextbookEmbedder
    ):
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder

    def run(
        self,
        pdf_path: str,
        class_number: int,
        subject: str,
        chapter: str
    ) -> IngestionResult:
        """
        Executes the full ingestion pipeline end-to-end for a given textbook chapter.
        """
        start_time = time.time()
        
       
        document_id = str(uuid.uuid4())
        
        logger.info(f"Initiating ingestion pipeline framework for Doc ID: {document_id}")
        logger.info(f"Processing source file: '{pdf_path}'")

      
        parsed_doc: ParsedDocument = self.parser.parse(
            pdf_path=pdf_path,
            class_number=class_number,
            subject=subject,
            chapter=chapter
        )

     
        parent_chunks, child_chunks = self.chunker.chunk_document(
            doc=parsed_doc,
            document_id=document_id
        )

       
        logger.info(f"Structure analysis complete. Created {len(parent_chunks)} parent boundaries.")
        logger.info(f"Structure analysis complete. Created {len(child_chunks)} child windows.")

     
        logger.info(f"Enqueuing {len(parent_chunks)} parent structures to embedding engine...")
        embedded_parents = self.embedder.generate_embeddings(parent_chunks)
        
        logger.info(f"Enqueuing {len(child_chunks)} child structures to embedding engine...")
        embedded_children = self.embedder.generate_embeddings(child_chunks)

       
        elapsed_time = time.time() - start_time

        
        logger.info(
            f"\n\t========================================="
            f"\n\t       INGESTION PIPELINE SUCCESS        "
            f"\n\t========================================="
            f"\n\tDocument ID:       {document_id}"
            f"\n\tChapter Title:     {chapter}"
            f"\n\tTotal Pages:       {parsed_doc.page_count}"
            f"\n\tTotal Characters:  {parsed_doc.character_count}"
            f"\n\tParents Embedded:  {len(embedded_parents)}"
            f"\n\tChildren Embedded: {len(embedded_children)}"
            f"\n\tPipeline Run Time: {elapsed_time:.2f} seconds"
            f"\n\t========================================="
        )

       
        return IngestionResult(
            document_id=document_id,
            embedded_parents=embedded_parents,
            embedded_children=embedded_children
        )