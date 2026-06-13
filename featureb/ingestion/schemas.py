from enum import Enum
from typing import Optional, List, Union
from pydantic import BaseModel

class ChunkType(str, Enum):
    PARENT = "parent"
    CHILD = "child"

class ParsedDocument(BaseModel):
    class_number: int
    subject: str
    chapter: str
    text: str
    page_count: int
    character_count: int

class ChunkMetadata(BaseModel):
    document_id: str
    class_number: int
    subject: str
    chapter: str
    section: str
    parent_index: int
    child_index: Optional[int]
    parent_id: Optional[str] = None
    chunk_type: ChunkType

class ParentChunk(BaseModel):
    id: str
    text: str
    metadata: ChunkMetadata

class ChildChunk(BaseModel):
    id: str
    text: str
    metadata: ChunkMetadata

class EmbeddedChunk(BaseModel):
    chunk: Union[ParentChunk, ChildChunk]
    embedding: List[float]

class IngestionResult(BaseModel):
    """
    Component 4 Final Payload.
    The complete, validated pipeline output containing vector-mapped parent and child arrays.
    """
    document_id: str
    embedded_parents: List[EmbeddedChunk]
    embedded_children: List[EmbeddedChunk]