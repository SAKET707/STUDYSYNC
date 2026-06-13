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
    student_answer: str,
    teacher_answer: str,
    rubric: dict,
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
