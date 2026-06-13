from pydantic import BaseModel
from typing import List


class OCRRequest(BaseModel):
    image_urls: List[str]


class GradingRequest(BaseModel):
    student_answer: str
    teacher_answer: str
    question_type: str
    subject_name: str
    max_marks: int