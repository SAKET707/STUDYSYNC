from pydantic import BaseModel
from typing import List,Any



class StudentInfoInitial(BaseModel):
    student_id:int
    question_id: int
    question_type: str
    subject_name: str
    image_urls:List[str]

class TeacherInfoInitial(BaseModel):
    teacher_id: int
    question_id: int
    question_type: str
    subject_name: str
    image_urls: List[str]


class StudentInfoStorable(BaseModel):
    student_id:int
    question_id: int
    question_type: str
    subject_name: str
    answer : str

class TeacherInfoStorable(BaseModel):
    teacher_id:int
    question_id: int
    question_type: str
    subject_name: str
    answer : str

class EvaluationResult(BaseModel):
    student_id: int
    teacher_id: int
    question_id: int
    subject_name: str
    student_text: str
    teacher_text: str
    max_marks: float
    marks_awarded: float
    rule_wise_evaluation: List[Any]
    penalties_applied: List[Any]
    final_justification: str