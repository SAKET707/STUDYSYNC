import requests
from google import genai
from google.genai import types
import os
from extractor_prompt import STUDENT_EXTRACTOR_PROMPT,TEACHER_EXTRACTOR_PROMPT
from config import GEMINI_MODEL_NAME

from schemas import (
    StudentInfoInitial,
    TeacherInfoInitial,
    StudentInfoStorable,
    TeacherInfoStorable,
)


gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)


def extract_text_from_url(
    image_url: str,
    prompt: str,
) -> str:
    """
    Extract OCR text from a single image URL using Gemini.
    """

    response_http = requests.get(image_url)
    response_http.raise_for_status()

    content_type = response_http.headers.get(
        "Content-Type",
        "image/jpeg",
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=[
            prompt,
            types.Part.from_bytes(
                data=response_http.content,
                mime_type=content_type,
            ),
        ],
    )

    return response.text


def student_extractor(
    student_info: StudentInfoInitial,
) -> StudentInfoStorable:
    """
    Converts StudentInfoInitial
    ->
    StudentInfoStorable
    """

    answer = ""

    for image_url in student_info.image_urls:
        page_text = extract_text_from_url(
            image_url=image_url,
            prompt=STUDENT_EXTRACTOR_PROMPT,
        )

        answer += page_text
        answer += "\n\n"

    return StudentInfoStorable(
        student_id=student_info.student_id,
        question_id=student_info.question_id,
        question_type=student_info.question_type,
        subject_name=student_info.subject_name,
        answer=answer.strip(),
    )


def teacher_extractor(
    teacher_info: TeacherInfoInitial,
) -> TeacherInfoStorable:
    """
    Converts TeacherInfoInitial
    ->
    TeacherInfoStorable
    """

    answer = ""

    for image_url in teacher_info.image_urls:
        page_text = extract_text_from_url(
            image_url=image_url,
            prompt=TEACHER_EXTRACTOR_PROMPT,
        )

        answer += page_text
        answer += "\n\n"

    return TeacherInfoStorable(
        teacher_id=teacher_info.teacher_id,
        question_id=teacher_info.question_id,
        question_type=teacher_info.question_type,
        subject_name=teacher_info.subject_name,
        answer=answer.strip(),
    )