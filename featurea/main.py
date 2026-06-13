from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "StudySync Backend Running"
    }


from text_extractor import extract_text_from_url
from schemas import OCRRequest
from extractor_prompt import EXTRACTOR_PROMPT

@app.post("/extract-text")
async def extract_text(request: OCRRequest) -> str:
    try:
        if not request.image_urls:
            raise HTTPException(
                status_code=400,
                detail="image_urls cannot be empty"
            )

        ans = ""

        for i, url in enumerate(request.image_urls):
            extracted_text = extract_text_from_url(
                image_url=url,
                prompt=EXTRACTOR_PROMPT,
            )

            ans += f"\n\n--- PAGE {i + 1} ---\n\n"
            ans += extracted_text.strip()

        return ans.strip()

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text extraction failed: {str(e)}"
        )
    

from grader import evaluate_answer
from rubric_fetcher import get_rubric
from schemas import GradingRequest
@app.post("/grade")
async def grade_answer(
    request: GradingRequest,
):
    try:
        rubric = get_rubric(
            subject_name=request.subject_name,
            question_type=request.question_type,
        )

        rubric = {
            **rubric,
            "max_marks": request.max_marks,
        }

        grading_json = evaluate_answer(
            student_answer=request.student_answer,
            teacher_answer=request.teacher_answer,
            rubric=rubric,
        )

        return grading_json

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Grading failed: {str(e)}",
        )
