from pydantic import BaseModel, Field

class ChapterRetrievalRequest(BaseModel):
    """
    Retrieval Input Contract.
    Validates incoming requests to sequentially fetch bulk NCERT context
    for bulk MCQ generation, completely bypassing vector similarity search.
    """
    class_number: int = Field(..., description="NCERT textbook grade constraint (e.g., 11 or 12).")
    chapter: str = Field(..., description="Exact chapter name for database filtering.")
    
    page: int = Field(default=1, ge=1, description="Pagination index to fetch subsequent context chunks.")
    context_limit: int = Field(
        default=10, 
        ge=1, 
        le=20, 
        description="Maximum number of parent contexts to extract per page to protect LLM context windows."
    )

class ParentContext(BaseModel):
    """
    Domain Broad Context Representation.
    Captures the macro background context block paired with its unique identifier.
    (Similarity scores removed as this is now a deterministic sequential fetch).
    """
    parent_id: str = Field(..., description="The unique database identifier of the macro context block.")
    text: str = Field(..., description="The actual NCERT paragraph text.")

class RetrievalResult(BaseModel):
    """
    Retrieval Output Contract.
    The immutable payload returned by the retrieval pipeline, serving as the
    direct, structured input contract for the MCQ generation system.
    """
    class_number: int
    chapter: str
    page: int
    
    parent_contexts: list[ParentContext] = Field(
        default_factory=list,
        description="The deterministic sequence of contextual text frames handed off to the LLM."
    )