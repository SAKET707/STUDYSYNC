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
  "max_marks": 5,

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
      "weight": 0.2,
      "match_type": "structure_quality",
      "required_elements": ["intro", "body"],
      "optional_elements": ["conclusion", "examples"]
    },
    "grammar": {
      "description": "Grammar quality: sentence formation, tense consistency, punctuation.",
      "weight": 0.2,
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
      "deduction": 1.0,
      "allowed": True
    },
    "irrelevant_answer": {
      "description": "Answer does not address the question topic.",
      "deduction": 5.0
    },
    "too_short": {
      "description": "Answer is too short for a long answer question.",
      "deduction": 1.0,
      "threshold_words": 25
    },
    "poor_structure": {
      "description": "Answer lacks flow: random sentences, no clear explanation.",
      "deduction": 0.5
    },
    "copying_or_exact_key_match": {
      "description": "Answer seems copied exactly from teacher key (optional rule for originality).",
      "deduction": 0.25,
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
  "max_marks": 3,

  "rules": {
    "content_keywords": {
      "description": "Answer must contain key expected keywords / concepts.",
      "weight": 0.5,
      "match_type": "keyword_overlap",
      "min_keywords_required": 2,
      "case_insensitive": True
    },
    "grammar": {
      "description": "Basic grammar should be correct (sentence structure, tense).",
      "weight": 0.3,
      "match_type": "grammar_quality",
      "allow_minor_errors": True
    },
    "spelling": {
      "description": "Spelling should be correct. Minor mistakes allowed.",
      "weight": 0.2,
      "match_type": "spelling_quality",
      "allow_minor_errors": True
    }
  },

  "penalties": {
    "major_grammar_error": {
      "description": "Sentence is not understandable due to grammar.",
      "deduction": 0.5,
      "allowed": True
    },
    "major_spelling_error": {
      "description": "Spelling mistake changes the meaning of the answer.",
      "deduction": 0.5,
      "allowed": True
    },
    "irrelevant_answer": {
      "description": "Answer does not address the question.",
      "deduction": 3
    },
    "extra_unnecessary_content": {
      "description": "Answer includes unnecessary explanation beyond 1-2 lines.",
      "deduction": 0.25
    }
  },

  "constraints": {
    "allow_partial_credit": True,
    "max_sentences": 2,
    "max_words": 30,
    "use_semantic_similarity": False,
    "min_relevance_score": 0.4
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
  "supported_formats": ["long_answer"],
  "max_marks": 5,

  "rules": {
    "key_historical_points": {
      "description": "Student must present 6–7 historically accurate key points covering causes, events, and consequences.",
      "expected_points": 6,
      "minimum_correct_points": 5,
      "allowed_incorrect_points": 1,
      "scoring_mode": "threshold_full_marks",
      "weight": 1.0
    }
  },

  "penalties": {
    "excess_wrong_facts": {
      "description": "More than one incorrect historical fact.",
      "deduction_per_extra_wrong": 1.0
    },
    "missing_core_points": {
      "description": "Important historical aspects not mentioned.",
      "deduction": 0.75
    },
    "off_topic": {
      "description": "Answer significantly deviates from the historical question.",
      "deduction": 2.0
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
    "One factual mistake is tolerated.",
    "Understanding of causes and consequences is rewarded."
  ]
}

HISTORY_SHORT_ANSWER = {
  "rubric_id": "history_short_answer",
  "subject": "history",
  "question_type": "short_answer",
  "supported_formats": ["short_answer"],
  "max_marks": 3,

  "rules": {
    "historical_facts": {
      "description": "Answer must contain clear and correct historical facts.",
      "minimum_correct_facts": 3,
      "expected_facts": 4,
      "allowed_incorrect_facts": 1,
      "scoring_mode": "threshold_partial",
      "weight": 1.0
    }
  },

  "penalties": {
    "wrong_fact": {
      "description": "Historically incorrect statement.",
      "deduction": 1.0
    },
    "irrelevant_fact": {
      "description": "Fact not related to the question.",
      "deduction": 0.75
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
    "Minor phrasing issues are ignored.",
    "Partial credit allowed if most facts are correct."
  ]
}

RUBRIC_REGISTRY = {
    ("english", "long_answer"): ENGLISH_LONG_ANSWER,
    ("english", "short_answer"): ENGLISH_SHORT_ANSWER,

    ("history", "long_answer"): HISTORY_LONG_ANSWER,
    ("history", "short_answer"): HISTORY_SHORT_ANSWER,
}