import time
import logging

from retrieval.chapter_fetcher import ChapterContextFetcher


from retrieval.schema import (
    ChapterRetrievalRequest,
    RetrievalResult
)

logger = logging.getLogger(__name__)

class RetrievalService:
    """
    Phase 4 Pipeline Orchestrator (Chapter-Based).
    Responsibility: Coordinate the deterministic, paginated extraction of macro 
    textbook contexts directly from the database for bulk MCQ generation.
    """

    def __init__(
        self,
        chapter_fetcher: ChapterContextFetcher
    ):
        self.chapter_fetcher = chapter_fetcher

    def retrieve(
        self, 
        request: ChapterRetrievalRequest
    ) -> RetrievalResult:
        """
        Executes the paginated fetch sequence and returns the final validated contract.
        """
        start_time = time.time()
        
        logger.info(
            f"Initiating Retrieval Pipeline for Class {request.class_number}, "
            f"Chapter: '{request.chapter}' (Page: {request.page})"
        )

      
        parent_contexts = self.chapter_fetcher.fetch_contexts(
            class_number=request.class_number,
            chapter=request.chapter,
            page=request.page,
            context_limit=request.context_limit
        )

        elapsed_time = time.time() - start_time

        
        if not parent_contexts:
            logger.warning(
                f"No retrieval matches found for chapter '{request.chapter}' "
                f"on page {request.page}. End of chapter reached or chapter missing."
            )
            return RetrievalResult(
                class_number=request.class_number,
                chapter=request.chapter,
                page=request.page,
                parent_contexts=[]
            )

       
        logger.info(
            f"\n\t========================================="
            f"\n\t       RETRIEVAL PIPELINE SUCCESS        "
            f"\n\t========================================="
            f"\n\tTarget Class:      {request.class_number}"
            f"\n\tTarget Chapter:    {request.chapter}"
            f"\n\tPage Fetched:      {request.page}"
            f"\n\tContexts Fetched:  {len(parent_contexts)} (Limit: {request.context_limit})"
            f"\n\tExecution Time:    {elapsed_time:.3f} seconds"
            f"\n\t========================================="
        )

        return RetrievalResult(
            class_number=request.class_number,
            chapter=request.chapter,
            page=request.page,
            parent_contexts=parent_contexts
        )