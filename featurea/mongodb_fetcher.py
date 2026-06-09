from mongodb_access import (
    get_student_collection,
    get_teacher_collection,
    get_evaluations_collection
)


def fetch_student_answer(
        student_id: int,
        question_id: int,
    ):
    collection = get_student_collection()

    doc = collection.find_one(
        {
            "student_id": student_id,
            "question_id": question_id,
        }
    )

    if doc is None:
        raise ValueError(
            f"Student answer not found: "
            f"student_id={student_id}, "
            f"question_id={question_id}"
        )

    return doc


def fetch_teacher_answer(
        teacher_id: int,
        question_id: int,
    ):
    collection = get_teacher_collection()

    doc = collection.find_one(
        {
            "teacher_id": teacher_id,
            "question_id": question_id,
        }
    )

    if doc is None:
        raise ValueError(
            f"Teacher answer not found: "
            f"teacher_id={teacher_id}, "
            f"question_id={question_id}"
        )

    return doc

def fetch_evaluation_result(
        student_id: int,
        teacher_id: int,
        question_id: int,
    ):
    collection = get_evaluations_collection()

    doc = collection.find_one(
        {
            "student_id": student_id,
            "teacher_id": teacher_id,
            "question_id": question_id,
        }
    )

    if doc is None:
        raise ValueError(
            f"No evaluation found for "
            f"student_id={student_id}, "
            f"teacher_id={teacher_id}, "
            f"question_id={question_id}"
        )

    return doc