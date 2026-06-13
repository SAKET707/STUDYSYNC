ENGLISH_LONG_ANSWER = {
    "rubric_id": "english_long_answer",
    "subject": "english",
    "question_type": "long_answer",

    "supported_formats": [
        "paragraph",
        "multi_point",
        "explanation",
        "qa_long"
    ],

    "scoring": {
        "base_score_formula": "weighted_sum",
        "score_scale": [0, 1],
        "final_marks_formula": "weighted_score * max_marks - penalties",
        "clamp_between": [0, "max_marks"]
    },

    "rules": {
        "content_coverage": {
            "description": "Answer must cover the key expected points from the teacher answer key.",
            "weight": 0.45,
            "match_type": "key_points_coverage",
            "min_points_required": 3,
            "case_insensitive": True,
            "allow_synonyms": True
        },

        "structure_and_flow": {
            "description": "Answer must have logical flow: intro -> explanation -> conclusion OR ordered points.",
            "weight": 0.20,
            "match_type": "structure_quality",
            "required_elements": ["intro", "body"],
            "optional_elements": ["conclusion", "examples"]
        },

        "grammar": {
            "description": "Grammar quality: sentence formation, tense consistency, punctuation.",
            "weight": 0.20,
            "match_type": "grammar_quality",
            "allow_minor_errors": True
        },

        "examples_or_support": {
            "description": "Student provides examples, facts, or supporting explanation where applicable.",
            "weight": 0.15,
            "match_type": "supporting_details",
            "optional": True
        }
    },

    "penalties": {
        "major_wrong_fact": {
            "description": "A wrong fact or misleading statement that changes the meaning.",
            "deduction_percentage": 0.20,
            "allowed": True
        },

        "irrelevant_answer": {
            "description": "Answer does not address the question topic.",
            "deduction_percentage": 1.00
        },

        "too_short": {
            "description": "Answer is too short for a long answer question.",
            "deduction_percentage": 0.20,
            "threshold_words": 25
        },

        "poor_structure": {
            "description": "Answer lacks flow: random sentences, no clear explanation.",
            "deduction_percentage": 0.10
        },

        "copying_or_exact_key_match": {
            "description": "Answer seems copied exactly from teacher key.",
            "deduction_percentage": 0.05,
            "allowed": False
        }
    },

    "constraints": {
        "allow_partial_credit": True,
        "min_words": 25,
        "max_words": 180,
        "max_paragraphs": 3,
        "expected_points_range": [3, 7],
        "use_semantic_similarity": True,
        "semantic_similarity_threshold": 0.55
    },

    "evaluation_notes": [
        "Long answers should explain the concept in detail, not just define it.",
        "Marks depend on coverage of key points and logical structure.",
        "Grammar mistakes reduce marks but do not make answer wrong unless meaning changes.",
        "If answer is irrelevant -> score becomes 0.",
        "Semantic similarity can be used to accept synonyms/paraphrased content."
    ]
}


ENGLISH_SHORT_ANSWER = {
    "rubric_id": "english_short_answer",
    "subject": "english",
    "question_type": "short_answer",

    "supported_formats": [
        "one_line",
        "two_lines",
        "definition",
        "short_explanation"
    ],

    "scoring": {
        "base_score_formula": "weighted_sum",
        "score_scale": [0, 1],
        "final_marks_formula": "weighted_score * max_marks - penalties",
        "clamp_between": [0, "max_marks"]
    },

    "rules": {
        "content_keywords": {
            "description": "Answer must contain key expected keywords / concepts.",
            "weight": 0.50,
            "match_type": "keyword_overlap",
            "min_keywords_required": 2,
            "case_insensitive": True
        },

        "grammar": {
            "description": "Basic grammar should be correct.",
            "weight": 0.30,
            "match_type": "grammar_quality",
            "allow_minor_errors": True
        },

        "spelling": {
            "description": "Spelling should be correct. Minor mistakes allowed.",
            "weight": 0.20,
            "match_type": "spelling_quality",
            "allow_minor_errors": True
        }
    },

    "penalties": {
        "major_grammar_error": {
            "description": "Sentence is not understandable due to grammar.",
            "deduction_percentage": 0.15,
            "allowed": True
        },

        "major_spelling_error": {
            "description": "Spelling mistake changes the meaning of the answer.",
            "deduction_percentage": 0.15,
            "allowed": True
        },

        "irrelevant_answer": {
            "description": "Answer does not address the question.",
            "deduction_percentage": 1.00
        },

        "extra_unnecessary_content": {
            "description": "Answer includes unnecessary explanation beyond expected length.",
            "deduction_percentage": 0.05
        }
    },

    "constraints": {
        "allow_partial_credit": True,
        "max_sentences": 2,
        "max_words": 30,
        "use_semantic_similarity": False,
        "min_relevance_score": 0.40
    },

    "evaluation_notes": [
        "Short answers should be 1-2 lines only.",
        "Marks are mainly based on correct content keywords.",
        "Grammar and spelling are supporting factors.",
        "If answer is irrelevant -> score becomes 0."
    ]
}


HISTORY_LONG_ANSWER = {
    "rubric_id": "history_long_answer",
    "subject": "history",
    "question_type": "long_answer",

    "supported_formats": [
        "long_answer",
        "paragraph",
        "multi_point"
    ],

    "scoring": {
        "base_score_formula": "weighted_sum",
        "score_scale": [0, 1],
        "final_marks_formula": "weighted_score * max_marks - penalties",
        "clamp_between": [0, "max_marks"]
    },

    "rules": {
        "historical_accuracy": {
            "description": "Facts, events, dates, names, and historical statements should be accurate.",
            "weight": 0.50,
            "match_type": "historical_accuracy"
        },

        "key_historical_points": {
            "description": "Student should cover causes, events, developments, and consequences expected in the answer.",
            "weight": 0.30,
            "expected_points": 6,
            "minimum_correct_points": 5,
            "use_semantic_similarity": True
        },

        "chronology_and_causality": {
            "description": "Events should be presented in logical historical sequence and cause-effect relationships should be clear.",
            "weight": 0.20,
            "match_type": "chronology_and_causality"
        }
    },

    "penalties": {
        "wrong_fact": {
            "description": "Historically incorrect statement.",
            "deduction_percentage": 0.20
        },

        "multiple_wrong_facts": {
            "description": "More than one major incorrect historical fact.",
            "deduction_percentage": 0.40
        },

        "missing_core_points": {
            "description": "Important historical aspects are missing.",
            "deduction_percentage": 0.15
        },

        "off_topic": {
            "description": "Answer significantly deviates from the question.",
            "deduction_percentage": 1.00
        }
    },

    "constraints": {
        "content_length": {
            "min_words": 95,
            "max_words": 170,
            "recommended_lines": "6-7"
        },

        "extract_points_as_list": True,
        "classify_points_as_correct_or_incorrect": True,
        "check_chronology_and_causality": True,
        "use_semantic_similarity": True,
        "return_json_only": True
    },

    "evaluation_notes": [
        "Chronological correctness is important.",
        "Historical accuracy carries the highest weight.",
        "One factual mistake may be tolerated, but multiple mistakes should reduce marks significantly.",
        "Understanding of causes and consequences is rewarded."
    ]
}


HISTORY_SHORT_ANSWER = {
    "rubric_id": "history_short_answer",
    "subject": "history",
    "question_type": "short_answer",

    "supported_formats": [
        "short_answer",
        "definition",
        "fact_based"
    ],

    "scoring": {
        "base_score_formula": "weighted_sum",
        "score_scale": [0, 1],
        "final_marks_formula": "weighted_score * max_marks - penalties",
        "clamp_between": [0, "max_marks"]
    },

    "rules": {
        "historical_facts": {
            "description": "Answer must contain clear and correct historical facts.",
            "weight": 0.70,
            "minimum_correct_facts": 3,
            "expected_facts": 4,
            "allowed_incorrect_facts": 1,
            "scoring_mode": "threshold_partial"
        },

        "accuracy": {
            "description": "Dates, names, events, and terminology should be historically accurate.",
            "weight": 0.30,
            "match_type": "historical_accuracy"
        }
    },

    "penalties": {
        "wrong_fact": {
            "description": "Historically incorrect statement.",
            "deduction_percentage": 0.25
        },

        "irrelevant_fact": {
            "description": "Fact not related to the question.",
            "deduction_percentage": 0.15
        },

        "irrelevant_answer": {
            "description": "Answer does not address the question.",
            "deduction_percentage": 1.00
        }
    },

    "constraints": {
        "content_length": {
            "min_words": 40,
            "max_words": 70,
            "recommended_lines": "3-4"
        },

        "extract_facts_as_points": True,
        "evaluate_each_fact_individually": True,
        "use_semantic_similarity": True,
        "return_json_only": True
    },

    "evaluation_notes": [
        "Dates, names, and events must be accurate.",
        "Minor phrasing issues should not reduce marks.",
        "Partial credit should be awarded when most facts are correct.",
        "The answer should remain focused on the asked historical event or concept."
    ]
}


RUBRIC_REGISTRY = {
    ("english", "long_answer"): ENGLISH_LONG_ANSWER,
    ("english", "short_answer"): ENGLISH_SHORT_ANSWER,

    ("history", "long_answer"): HISTORY_LONG_ANSWER,
    ("history", "short_answer"): HISTORY_SHORT_ANSWER,
}