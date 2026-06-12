from fastapi import FastAPI,HTTPException
from schemas import StudentInfoInitial,TeacherInfoInitial,TeacherInfoStorable
from text_extractor import student_extractor,teacher_extractor
from mongodb_writer import write_student_answer,write_teacher_answer
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

@app.post("/student/upload")
async def upload_student(
        student_info: StudentInfoInitial,
    ):
    try:
        student_doc = student_extractor(
            student_info
        )

        write_student_answer(
            student_doc
        )

        return {
            "success": True,
            "student_id": student_doc.student_id,
            "question_id": student_doc.question_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

@app.post("/teacher/upload")
async def upload_teacher(
        teacher_info : TeacherInfoInitial,
    ):
    try:
        teacher_doc = teacher_extractor(
            teacher_info
        )

        write_teacher_answer(
            teacher_doc
        )

        return {
            "success": True,
            "teacher_id": teacher_doc.teacher_id,
            "question_id": teacher_doc.question_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
@app.post("/teacher/uploadExt")
async def upload_teacher_extracted(
        teacher_info : TeacherInfoStorable
    ):
    try :
        write_teacher_answer(teacher_info)

        return {
            "success": True,
            "teacher_id": teacher_info.teacher_id,
            "question_id": teacher_info.question_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -------------
from mongodb_fetcher import (
    fetch_student_answer,
    fetch_teacher_answer
)
from rubric_fetcher import get_rubric
from grader import build_result
from mongodb_writer import (
    write_evaluation_result
)

@app.post("/evaluate")
async def evaluate(
        student_id: int,
        teacher_id: int,
        question_id: int,
    ):
    try:

        student_doc = fetch_student_answer(
            student_id=student_id,
            question_id=question_id,
        )

        teacher_doc = fetch_teacher_answer(
            teacher_id=teacher_id,
            question_id=question_id,
        )

        rubric = get_rubric(
            subject_name=student_doc["subject_name"],
            question_type=student_doc["question_type"],
        )

        result = build_result(
            student_doc=student_doc,
            teacher_doc=teacher_doc,
            rubric=rubric,
        )

        write_evaluation_result(result)

        return {
            "success": True,
            "student_id": student_id,
            "teacher_id": teacher_id,
            "question_id": question_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
    


# -------------
from mongodb_fetcher import (
    fetch_evaluation_result,
)

@app.get("/result")
async def get_result(
        student_id: int,
        teacher_id: int,
        question_id: int,
    ):
    try:

        result = fetch_evaluation_result(
            student_id=student_id,
            teacher_id=teacher_id,
            question_id=question_id,
        )

        result.pop("_id", None)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
