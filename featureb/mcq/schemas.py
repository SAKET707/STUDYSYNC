import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class GeneratedMCQ(BaseModel):
    """
    Internal Storage, Validation & Output Layer.
    The complete object produced by the LLM. Contains the question,
    options, answers, explanations, and lineage traceability.
    """
    question_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    
    source_parent_id: Optional[str] = Field(None, description="Parent context that generated this MCQ.")
    
    question: str
    
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    
    correct_option: int = Field(..., ge=1, le=4)
    explanation: str



class MCQGenerationRequest(BaseModel):
    """
    API Input Contract.
    Triggers batch generation from a specific chapter. 
    Pagination ensures unique NCERT context chunks are fetched per request.
    """
    class_number: int = Field(..., description="NCERT Class (11 or 12).")
    chapter: str = Field(..., description="Exact chapter name for retrieval scoping.")
    
    num_questions: int = Field(default=30, ge=1, le=50, description="Number of questions to generate per request.")
    page: int = Field(default=1, ge=1, description="Pagination index to fetch subsequent context chunks.")

class MCQGenerationResult(BaseModel):
    """
    API Output Contract.
    The finalized payload containing the array of generated, validated MCQs.
    """
    mcqs: List[GeneratedMCQ] = Field(default_factory=list)