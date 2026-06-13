import logging
import os
import re
import fitz  
from ingestion.schemas import ParsedDocument

logger = logging.getLogger(__name__)

class PDFParser:
    """
    Component 1 of the Ingestion Pipeline.
    Responsibility: Convert a physical NCERT PDF into a raw, sanitized text block.
    Strictly follows the Single Responsibility Principle (SRP).
    """
    
    def __init__(self, clear_headers_footers: bool = True):
        self.clear_headers_footers = clear_headers_footers

    def _clean_text(self, raw_text: str, subject: str, chapter: str) -> str:
        """
        Removes recurring structural layout noise dynamically.
        Preserves diagrams, figure tokens, and source references for RAG accuracy.
        """
        if not raw_text:
            return ""
        text = re.sub(r'(\w+)-\n\s*(\w+)', r'\1\2', raw_text)
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        lines = [line.strip() for line in text.split('\n')]
        cleaned_lines = []
        for line in lines:
            if not line:
                continue
            
          
            if line.isdigit():
                continue
                
          
            if self.clear_headers_footers:
                if re.fullmatch(r"CHAPTER\s+\d+", line.upper()):
                    continue
                if line.upper() == subject.upper():
                    continue
                if line.upper() == chapter.upper():
                    continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    def parse(
        self, 
        pdf_path: str, 
        class_number: int, 
        subject: str, 
        chapter: str
    ) -> ParsedDocument:
        """
        Validates, attempts extraction, and returns a verified ParsedDocument.
        Throws clear, traceable errors if physical files or structural formats are invalid.
        """
       
        if not pdf_path.lower().endswith(".pdf"):
            logger.error(f"Invalid file extension: {pdf_path}")
            raise ValueError(f"Expected a PDF file, received: '{pdf_path}'")
            
        if not os.path.exists(pdf_path):
            logger.error(f"File path does not exist: {pdf_path}")
            raise FileNotFoundError(f"PDF target not found at: '{pdf_path}'")

        extracted_pages = []
        page_count = 0

      
        try:
            with fitz.open(pdf_path) as doc:
                page_count = len(doc)
                for page in doc:
                    page_text = page.get_text("text")
                    extracted_pages.append(page_text)
        except Exception as e:
            logger.exception(f"Fatal error occurred while extraction was running on PDF: {pdf_path}")
            raise

      
        full_raw_text = "\n".join(extracted_pages)
        clean_text = self._clean_text(full_raw_text, subject=subject, chapter=chapter)

     
        if not clean_text.strip():
            logger.error(f"Aborting ingestion. No extractable characters found inside: {pdf_path}")
            raise ValueError(f"PDF contains no extractable text or consists completely of images: {pdf_path}")

        character_count = len(clean_text)


        logger.info(
            f"\n\t=== Parsed PDF Successfully ==="
            f"\n\tChapter: {chapter}"
            f"\n\tPages: {page_count}"
            f"\n\tCharacters: {character_count}\n"
        )

        return ParsedDocument(
            class_number=class_number,
            subject=subject,
            chapter=chapter,
            text=clean_text,
            page_count=page_count,
            character_count=character_count
        )