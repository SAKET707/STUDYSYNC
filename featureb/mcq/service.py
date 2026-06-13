import time
import logging

# Standardized plural schemas
from retrieval.schema import ChapterRetrievalRequest
from mcq.schemas import MCQGenerationRequest, MCQGenerationResult

from retrieval.retrieval_service import RetrievalService
from mcq.generator import MCQGenerator
from mcq.validator import MCQValidator
from mcq.consistency_checker import MCQConsistencyChecker
from mcq.faithfulness_checker import MCQFaithfulnessChecker

logger = logging.getLogger(__name__)

class MCQService:
    """
    Phase 4 Pipeline Orchestrator (Chapter-Based).
    Currently operating in "V1 Dev Mode" -> Evaluation gates bypassed to prevent HTTP 429 Rate Limits.
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

    def generate_mcqs(self, request: MCQGenerationRequest) -> MCQGenerationResult:
        start_time = time.time()
        logger.info(f"--- STARTING MCQ PIPELINE FOR CHAPTER: '{request.chapter}' (Page: {request.page}) ---")

        # Step 1 & 2: Retrieval
        retrieval_request = ChapterRetrievalRequest(
            class_number=request.class_number,
            chapter=request.chapter,
            page=request.page,
            context_limit=10  
        )
        
        retrieval_result = self.retrieval_service.retrieve(retrieval_request)
        
        if not retrieval_result.parent_contexts:
            logger.warning(f"Pipeline Aborted: No NCERT contexts found for chapter '{request.chapter}'.")
            return MCQGenerationResult(mcqs=[])

        # Step 3: Generation (1 LLM Call)
        generation_result = self.generator.generate(retrieval_result, request)
        initial_generated_count = len(generation_result.mcqs)
        
        if initial_generated_count == 0:
            logger.warning("Pipeline Aborted: Generator failed to produce any valid JSON MCQs.")
            return MCQGenerationResult(mcqs=[])

        # Step 4: Fast Python Validation
        validated_mcqs = self.validator.validate_batch(generation_result.mcqs)
        validated_count = len(validated_mcqs)

        # Step 5 & 6: TEMPORARILY DISABLED FOR RATE LIMITS (HTTP 429)
        # -------------------------------------------------------------
        # consistent_mcqs = self.consistency_checker.check_batch(validated_mcqs)
        consistent_mcqs = validated_mcqs
        consistent_count = len(consistent_mcqs)

        # faithful_mcqs = self.faithfulness_checker.check_batch(...)
        faithful_mcqs = consistent_mcqs
        final_count = len(faithful_mcqs)
        # -------------------------------------------------------------

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
            f"\n\tGenerated MCQs:      {initial_generated_count} (Requested: {request.num_questions})"
            f"\n\tValidated MCQs:      {validated_count}"
            f"\n\tConsistent MCQs:     [BYPASSED]"
            f"\n\tFaithful MCQs:       [BYPASSED]"
            f"\n\tFinal Yield:         {final_count}"
            f"\n\t-----------------------------------------"
            f"\n\tExecution Time:      {elapsed_time:.2f}s"
            f"\n\t========================================="
        )

        return MCQGenerationResult(mcqs=faithful_mcqs)