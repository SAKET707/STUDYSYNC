import logging
from fastapi import APIRouter, HTTPException

# Import strictly from the API Facade
from api.schemas import MCQGenerationRequest, MCQGenerationResult

# Import the core orchestrator
from mcq.service import MCQService

logger = logging.getLogger(__name__)

# THIS IS THE LINE PYTHON IS LOOKING FOR:
router = APIRouter(
    prefix="/api/v1/mcqs",
    tags=["MCQ Generation Engine"]
)

# Global reference for simple Dependency Injection
_mcq_service: MCQService | None = None

def register_mcq_service(service: MCQService):
    """
    Hooks the fully instantiated backend engine into the FastAPI route.
    Call this exactly once during the FastAPI app lifespan (in main.py).
    """
    global _mcq_service
    _mcq_service = service
    logger.info("MCQService successfully registered in API router.")

@router.post(
    "/generate",
    response_model=MCQGenerationResult,
    summary="Generate a batch of MCQs from a specific NCERT Chapter.",
    description="Deterministically fetches textbook context and triggers the multi-stage LLM pipeline to generate strictly validated, NTA-standard NEET Biology MCQs."
)
def generate_mcqs(request: MCQGenerationRequest):
    """
    HTTP POST Endpoint for Chapter-based MCQ Generation.
    """
    if _mcq_service is None:
        logger.error("API call rejected: MCQService is not initialized.")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: MCQ Service not initialized."
        )

    logger.info(f"API Request Received -> Generate {request.num_questions} MCQs for Class {request.class_number}, Chapter: '{request.chapter}' (Page {request.page}).")

    try:
        # Pass the validated Pydantic model directly to the orchestrator
        result = _mcq_service.generate_mcqs(request)
        return result

    except Exception as e:
        logger.exception(f"Unhandled exception during API MCQ generation: {e}")
        # Return a clean 500 error to the client instead of crashing the server
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during pipeline execution: {str(e)}"
        )