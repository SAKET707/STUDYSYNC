from schemas import (
    StudentInfoStorable,
    TeacherInfoStorable,
    EvaluationResult
)

from mongodb_access import (
    get_student_collection,
    get_teacher_collection,
    get_evaluations_collection
)

def write_evaluation_result(
        result: EvaluationResult,
    ):
    collection = get_evaluations_collection()

    collection.update_one(
        {
            "student_id": result.student_id,
            "teacher_id": result.teacher_id,
            "question_id": result.question_id,
        },
        {
            "$set": result.model_dump()
        },
        upsert=True,
    )

def write_student_answer(
        student_data: StudentInfoStorable,
    ):
    collection = get_student_collection()

    result = collection.insert_one(
        student_data.model_dump()
    )

    return result.inserted_id


def write_teacher_answer(
        teacher_data: TeacherInfoStorable,
    ):
    collection = get_teacher_collection()

    result = collection.insert_one(
        teacher_data.model_dump()
    )

    return result.inserted_id