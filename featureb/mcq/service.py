import time
import logging
from concurrent.futures import ThreadPoolExecutor


from retrieval.schema import ChapterRetrievalRequest
from mcq.schemas import MCQGenerationRequest, MCQGenerationResult

from retrieval.retrieval_service import RetrievalService
from mcq.generator import MCQGenerator
from mcq.validator import MCQValidator
from mcq.consistency_checker import MCQConsistencyChecker
from mcq.faithfulness_checker import MCQFaithfulnessChecker


from config.redis_client import redis_client

logger = logging.getLogger(__name__)

class MCQService:
    """
    Phase 4 Pipeline Orchestrator (Chapter-Based).
    Includes Redis caching and Background Prefetching (Thread Pool) 
    to predictively generate future pages safely and efficiently.
    """
    def __init__(
        self,
        retrieval_service: RetrievalService,
        generator: MCQGenerator,
        validator: MCQValidator,
        consistency_checker: MCQConsistencyChecker,
        faithfulness_checker: MCQFaithfulnessChecker
    ):
        self.retrieval_service = retrieval_service
        self.generator = generator
        self.validator = validator
        self.consistency_checker = consistency_checker
        self.faithfulness_checker = faithfulness_checker
        
        self.prefetch_executor = ThreadPoolExecutor(max_workers=2)

    def _build_cache_key(self, request: MCQGenerationRequest) -> str:
        """
        Helper method to guarantee consistent cache keys everywhere.
        """
        safe_chapter = request.chapter.replace(" ", "_").lower()
        return (
            f"{request.class_number}:"
            f"{safe_chapter}:"
            f"{request.page}:"
            f"{request.num_questions}"
        )

    def _generate_page(self, request: MCQGenerationRequest) -> MCQGenerationResult:
        """
        Internal method: Handles the pure logic of generating a single page.
        """
        start_time = time.time()
        
        retrieval_request = ChapterRetrievalRequest(
            class_number=request.class_number,
            chapter=request.chapter,
            page=request.page,
            context_limit=4 
        )
        
        retrieval_result = self.retrieval_service.retrieve(retrieval_request)
        
        if not retrieval_result.parent_contexts:
            logger.warning(f"Pipeline Aborted: No NCERT contexts found for '{request.chapter}' (Page {request.page}).")
            return MCQGenerationResult(mcqs=[])

        generation_result = self.generator.generate(retrieval_result, request)
        initial_generated_count = len(generation_result.mcqs)
        
        if initial_generated_count == 0:
            logger.warning(f"Pipeline Aborted: Generator failed to produce MCQs for Page {request.page}.")
            return MCQGenerationResult(mcqs=[])

        validated_mcqs = self.validator.validate_batch(generation_result.mcqs)
        validated_count = len(validated_mcqs)


        consistent_mcqs = validated_mcqs
        faithful_mcqs = consistent_mcqs
        final_count = len(faithful_mcqs)

        elapsed_time = time.time() - start_time

        logger.info(
            f"\n\t========================================="
            f"\n\t       MCQ PIPELINE SUCCESS SUMMARY      "
            f"\n\t========================================="
            f"\n\tClass:               {request.class_number}"
            f"\n\tChapter:             {request.chapter}"
            f"\n\tPage:                {request.page}"
            f"\n\tContexts Retrieved:  {len(retrieval_result.parent_contexts)}"
            f"\n\t-----------------------------------------"
            f"\n\tGenerated MCQs:      {initial_generated_count} (Req: {request.num_questions})"
            f"\n\tValidated MCQs:      {validated_count}"
            f"\n\tFinal Yield:         {final_count}"
            f"\n\t-----------------------------------------"
            f"\n\tExecution Time:      {elapsed_time:.2f}s"
            f"\n\t========================================="
        )

        return MCQGenerationResult(mcqs=faithful_mcqs)

    def _prefetch_pages(self, request: MCQGenerationRequest, pages_to_prefetch: int = 2):
        """
        Background worker: Predictively generates and caches subsequent pages.
        """
        logger.info(f" Starting Background Prefetch: '{request.chapter}' (Pages {request.page + 1} to {request.page + pages_to_prefetch})")

        for next_page in range(request.page + 1, request.page + pages_to_prefetch + 1):
            prefetch_request = MCQGenerationRequest(
                class_number=request.class_number,
                chapter=request.chapter,
                page=next_page,
                num_questions=request.num_questions
            )

            cache_key = self._build_cache_key(prefetch_request)

           
            if redis_client:
                try:
                    if redis_client.exists(cache_key):
                        logger.info(f" Skipping Prefetch: Cache already exists -> {cache_key}")
                        continue
                except Exception as e:
                    logger.warning(f"Prefetch Redis check error: {e}")

            
            try:
                result = self._generate_page(prefetch_request)
            except Exception as e:
                logger.error(f" Prefetch failed for page {next_page}: {e}")
                continue

           
            if not result.mcqs:
                logger.info(f" Reached end of chapter at page {next_page}. Stopping prefetch.")
                break


            if result.mcqs and redis_client:
                try:
                    redis_client.set(
                        cache_key,
                        result.model_dump_json(),
                        ex=86400
                    )
                    logger.info(f"⚡ Prefetched & Saved -> {cache_key}")
                except Exception as e:
                    logger.warning(f"Prefetch Redis write error: {e}")

    def generate_mcqs(self, request: MCQGenerationRequest) -> MCQGenerationResult:
        """
        Public endpoint: Check cache -> generate if missing -> trigger background prefetch.
        """
        logger.info(f"--- INCOMING REQUEST: '{request.chapter}' (Page: {request.page}) ---")

     
      
        cache_key = self._build_cache_key(request)

        if redis_client:
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    logger.info(f" Redis Cache HIT -> {cache_key}")
                    return MCQGenerationResult.model_validate_json(cached_result)

                logger.info(f" Redis Cache MISS -> {cache_key}")
            except Exception as e:
                logger.warning(f"Redis cache read error: {e}")

        
       
        result = self._generate_page(request)

        
      
        if result.mcqs:
            if redis_client:
                try:
                    redis_client.set(
                        cache_key,
                        result.model_dump_json(),
                        ex=86400  
                    )
                    logger.info(f" Saved to Redis Cache -> {cache_key}")
                except Exception as e:
                    logger.warning(f"Redis cache write error: {e}")

            logger.info("Submitting background prefetch task...")
            self.prefetch_executor.submit(
                self._prefetch_pages,
                request
            )

        return result
