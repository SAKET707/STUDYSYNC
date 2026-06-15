import os
import sys
import logging
import argparse
from typing import Dict, Any


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


from vectorstore.client_factory import QdrantClientFactory
from vectorstore.collections import QdrantCollectionManager
from vectorstore.qdrant_client import QdrantVectorStore



from ingestion.pdf_parser import PDFParser
from ingestion.chunker import ParentChildChunker
from ingestion.embedder import TextbookEmbedder
from ingestion.ingest import IngestionCoordinator



from config.constants import (
    COLLECTION_NAME,
    PARENT_WORD_LIMIT,
    CHILD_WORD_LIMIT,
    CHILD_OVERLAP,
    EMBEDDING_BATCH_SIZE
)

from config.chapter_mapping import BIOLOGY_CHAPTERS



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


class BulkIngestionEngine:
    """
    Bulk ingestion orchestration layer.

    Responsibilities:
        - Initialize Qdrant
        - Verify collection state
        - Process Biology PDFs
        - Execute ingestion pipeline
        - Upload vectors to Qdrant
        - Produce ingestion metrics
    """

    def __init__(self, reset_db: bool = False):

        logger.info("Initializing Qdrant infrastructure...")


        self.client = QdrantClientFactory.create()

        self.collection_manager = QdrantCollectionManager(
            client=self.client
        )

        if not self.collection_manager.cluster_health_check():
            raise ConnectionError(
                "Unable to connect to Qdrant cluster."
            )

        if reset_db:
            logger.warning(
                "Reset flag detected. Recreating collection..."
            )
            self.collection_manager.recreate_collection()
        else:
            self.collection_manager.create_collection()

        self.vector_store = QdrantVectorStore(
            client=self.client
        )



        parser = PDFParser(
            clear_headers_footers=True
        )

        chunker = ParentChildChunker(
            parent_word_limit=PARENT_WORD_LIMIT,
            child_word_limit=CHILD_WORD_LIMIT,
            child_overlap=CHILD_OVERLAP
        )

        embedder = TextbookEmbedder(
            batch_size=EMBEDDING_BATCH_SIZE
        )

        self.coordinator = IngestionCoordinator(
            parser=parser,
            chunker=chunker,
            embedder=embedder
        )

    def run_bulk_ingestion(self, folder_path: str) -> None:

        if not os.path.exists(folder_path):
            raise FileNotFoundError(
                f"Folder not found: {folder_path}"
            )

        pdf_files = sorted(
            [
                f
                for f in os.listdir(folder_path)
                if f.lower().endswith(".pdf")
            ],
            key=lambda x: int(
                x.replace("chapter", "")
                 .replace(".pdf", "")
            )
        )

        if not pdf_files:
            logger.warning(
                f"No PDFs found in {folder_path}"
            )
            return

        total_pdfs = len(pdf_files)

        logger.info(
            f"Discovered {total_pdfs} Biology PDFs."
        )

        processed_count = 0
        failed_count = 0

        total_parents = 0
        total_children = 0

        # ----------------------------------------------------------
        # Main Loop
        # ----------------------------------------------------------

        for index, filename in enumerate(pdf_files, start=1):

            if filename not in BIOLOGY_CHAPTERS:

                logger.warning(
                    f"[{index}/{total_pdfs}] "
                    f"Skipping {filename}. "
                    f"No chapter mapping found."
                )

                failed_count += 1
                continue

            chapter_metadata: Dict[str, Any] = (
                BIOLOGY_CHAPTERS[filename]
            )

            chapter_name = chapter_metadata["chapter"]
            class_number = chapter_metadata["class_number"]

            pdf_path = os.path.join(
                folder_path,
                filename
            )

            logger.info(
                f"[{index}/{total_pdfs}] "
                f"Processing '{chapter_name}'"
            )

            try:

                ingestion_result = self.coordinator.run(
                    pdf_path=pdf_path,
                    class_number=class_number,
                    subject="biology",
                    chapter=chapter_name
                )

                self.vector_store.upsert_ingestion_result(
                    ingestion_result
                )

                parent_count = len(
                    ingestion_result.embedded_parents
                )

                child_count = len(
                    ingestion_result.embedded_children
                )

                total_parents += parent_count
                total_children += child_count

                processed_count += 1

                logger.info(
                    f"[{index}/{total_pdfs}] "
                    f"{chapter_name} ✓ "
                    f"(Parents={parent_count}, "
                    f"Children={child_count})"
                )

            except Exception as e:

                logger.exception(
                    f"[{index}/{total_pdfs}] "
                    f"{chapter_name} FAILED: {e}"
                )

                failed_count += 1

        # ----------------------------------------------------------
        # Final Summary
        # ----------------------------------------------------------

        total_vectors = (
            total_parents +
            total_children
        )

        logger.info(
            "\n"
            "====================================================\n"
            "        BIOLOGY INGESTION COMPLETE\n"
            "====================================================\n"
            f"Collection Name:       {COLLECTION_NAME}\n"
            f"PDFs Found:            {total_pdfs}\n"
            f"PDFs Processed:        {processed_count}\n"
            f"PDFs Failed:           {failed_count}\n"
            f"Parent Chunks:         {total_parents}\n"
            f"Child Chunks:          {total_children}\n"
            f"Total Vectors Stored:  {total_vectors}\n"
            "====================================================\n"
        )


def main():

    parser = argparse.ArgumentParser(
        description="NCERT Biology Bulk Ingestion"
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate collection before ingestion."
    )

    args = parser.parse_args()

    biology_folder = os.path.join(
        PROJECT_ROOT,
        "biology"
    )

    engine = BulkIngestionEngine(
        reset_db=args.reset
    )

    engine.run_bulk_ingestion(
        folder_path=biology_folder
    )


if __name__ == "__main__":
    main()