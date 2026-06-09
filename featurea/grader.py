from schemas import EvaluationResult
import json
from groq import Groq
from config import (
    GROQ_MODEL_NAME
)
from grading_prompt import GRADING_PROMPT
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def evaluate_answer(
    rubric: dict,
    teacher_answer: str,
    student_answer: str,
) -> dict:

    user_prompt = f"""
        RUBRIC JSON:
        {json.dumps(rubric, indent=2)}

        TEACHER ANSWER:
        {teacher_answer}

        STUDENT ANSWER:
        {student_answer}
    """

    response = client.chat.completions.create(
        model=GROQ_MODEL_NAME,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": GRADING_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    content = response.choices[0].message.content
    

    try:
        grading_json = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(
            "Groq returned invalid JSON"
        ) from e

    return grading_json




def build_result(
        student_doc,
        teacher_doc,
        rubric,
    ) -> EvaluationResult:

    grading_json = evaluate_answer(
        rubric=rubric,
        teacher_answer=teacher_doc["answer"],
        student_answer=student_doc["answer"],
    )

    return EvaluationResult(
        student_id=student_doc["student_id"],
        teacher_id=teacher_doc["teacher_id"],
        question_id=student_doc["question_id"],
        subject_name=student_doc["subject_name"],
        student_text=student_doc["answer"],
        teacher_text=teacher_doc["answer"],
        max_marks=grading_json["max_marks"],
        marks_awarded=grading_json["marks_awarded"],
        rule_wise_evaluation=grading_json["rule_wise_evaluation"],
        penalties_applied=grading_json["penalties_applied"],
        final_justification=grading_json["final_justification"],
    )