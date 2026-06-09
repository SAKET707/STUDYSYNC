from rubrics import RUBRIC_REGISTRY


def get_rubric(
        subject_name: str,
        question_type: str,
    ):
    key = (
        subject_name.lower().strip(),
        question_type.lower().strip(),
    )

    rubric = RUBRIC_REGISTRY.get(key)

    if rubric is None:
        raise ValueError(
            f"No rubric found for "
            f"subject='{subject_name}', "
            f"question_type='{question_type}'"
        )

    return rubric