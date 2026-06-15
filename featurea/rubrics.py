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

HINDI_LONG_ANSWER = {
    "rubric_id": "hindi_long_answer",
    "subject": "hindi",
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
            "description": "उत्तर में शिक्षक उत्तर-कुंजी के मुख्य बिंदुओं का समुचित समावेश होना चाहिए।",
            "weight": 0.45,
            "match_type": "key_points_coverage",
            "min_points_required": 3,
            "case_insensitive": True,
            "allow_synonyms": True
        },

        "structure_and_flow": {
            "description": "उत्तर में तार्किक क्रम होना चाहिए: भूमिका → व्याख्या → निष्कर्ष अथवा क्रमबद्ध बिंदु।",
            "weight": 0.20,
            "match_type": "structure_quality",
            "required_elements": ["intro", "body"],
            "optional_elements": ["conclusion", "examples"]
        },

        "grammar": {
            "description": "व्याकरण, वाक्य-विन्यास, वर्तनी तथा विराम-चिह्नों की शुद्धता।",
            "weight": 0.20,
            "match_type": "grammar_quality",
            "allow_minor_errors": True
        },

        "examples_or_support": {
            "description": "जहाँ आवश्यक हो वहाँ उदाहरण, तथ्य या सहायक विवरण दिए गए हों।",
            "weight": 0.15,
            "match_type": "supporting_details",
            "optional": True
        }
    },

    "penalties": {
        "major_wrong_fact": {
            "description": "ऐसा गलत तथ्य जो उत्तर के अर्थ को बदल दे।",
            "deduction_percentage": 0.20,
            "allowed": True
        },

        "irrelevant_answer": {
            "description": "उत्तर प्रश्न के विषय से संबंधित नहीं है।",
            "deduction_percentage": 1.00
        },

        "too_short": {
            "description": "दीर्घ उत्तरीय प्रश्न के लिए उत्तर बहुत छोटा है।",
            "deduction_percentage": 0.20,
            "threshold_words": 25
        },

        "poor_structure": {
            "description": "उत्तर में विचारों का क्रम एवं प्रवाह स्पष्ट नहीं है।",
            "deduction_percentage": 0.10
        },

        "copying_or_exact_key_match": {
            "description": "उत्तर शिक्षक की उत्तर-कुंजी से लगभग शब्दशः मेल खाता है।",
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
        "दीर्घ उत्तर में केवल परिभाषा नहीं, बल्कि विषय का विस्तारपूर्वक वर्णन होना चाहिए।",
        "अंक मुख्य बिंदुओं के समावेश और उत्तर की तार्किक संरचना के आधार पर दिए जाएँ।",
        "छोटी व्याकरणिक त्रुटियाँ स्वीकार्य हैं जब तक अर्थ प्रभावित न हो।",
        "यदि उत्तर पूर्णतः अप्रासंगिक है तो अंक 0 दिए जाएँ।",
        "समानार्थी शब्दों एवं भावार्थ आधारित उत्तरों को स्वीकार करने हेतु semantic similarity का उपयोग किया जा सकता है।"
    ]
}

HINDI_SHORT_ANSWER = {
    "rubric_id": "hindi_short_answer",
    "subject": "hindi",
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
            "description": "उत्तर में अपेक्षित मुख्य शब्दों या प्रमुख अवधारणाओं का समावेश होना चाहिए।",
            "weight": 0.50,
            "match_type": "keyword_overlap",
            "min_keywords_required": 2,
            "case_insensitive": True
        },

        "grammar": {
            "description": "मूलभूत व्याकरण, वाक्य-विन्यास तथा भाषा का प्रयोग सही होना चाहिए।",
            "weight": 0.30,
            "match_type": "grammar_quality",
            "allow_minor_errors": True
        },

        "spelling": {
            "description": "वर्तनी सामान्यतः सही होनी चाहिए। छोटी-मोटी त्रुटियाँ स्वीकार्य हैं।",
            "weight": 0.20,
            "match_type": "spelling_quality",
            "allow_minor_errors": True
        }
    },

    "penalties": {
        "major_grammar_error": {
            "description": "व्याकरण संबंधी त्रुटि के कारण उत्तर का अर्थ स्पष्ट नहीं हो रहा है।",
            "deduction_percentage": 0.15,
            "allowed": True
        },

        "major_spelling_error": {
            "description": "वर्तनी की त्रुटि उत्तर के अर्थ को बदल देती है।",
            "deduction_percentage": 0.15,
            "allowed": True
        },

        "irrelevant_answer": {
            "description": "उत्तर प्रश्न से संबंधित नहीं है।",
            "deduction_percentage": 1.00
        },

        "extra_unnecessary_content": {
            "description": "उत्तर अपेक्षित लंबाई से अधिक है और उसमें अनावश्यक विवरण शामिल हैं।",
            "deduction_percentage": 0.05
        }
    },

    "constraints": {
        "allow_partial_credit": True,
        "max_sentences": 2,
        "max_words": 30,
        "use_semantic_similarity": True,
        "min_relevance_score": 0.40
    },

    "evaluation_notes": [
        "लघु उत्तरीय प्रश्नों के उत्तर सामान्यतः 1-2 पंक्तियों में होने चाहिए।",
        "अंक मुख्यतः सही विषयवस्तु, प्रमुख शब्दों और अवधारणाओं के आधार पर दिए जाएँ।",
        "व्याकरण और वर्तनी सहायक मूल्यांकन कारक हैं।",
        "यदि उत्तर प्रश्न से असंबंधित है, तो अंक 0 दिए जाएँ।"
    ]
}

GEOGRAPHY_LONG_ANSWER = {
    "rubric_id": "geography_long_answer",
    "subject": "geography",
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
        "geographical_accuracy": {
            "description": "Geographical facts, concepts, locations, resources, climate features, and processes should be accurate.",
            "weight": 0.45,
            "match_type": "geographical_accuracy"
        },

        "key_geographical_points": {
            "description": "Student should cover the important geographical features, characteristics, factors, and concepts expected in the answer.",
            "weight": 0.30,
            "expected_points": 6,
            "minimum_correct_points": 5,
            "use_semantic_similarity": True
        },

        "cause_effect_and_relationships": {
            "description": "The answer should clearly explain relationships such as cause-effect, human-environment interaction, distribution patterns, or impacts where applicable.",
            "weight": 0.15,
            "match_type": "cause_effect_analysis"
        },

        "geographical_terminology": {
            "description": "Appropriate geographical terms and subject vocabulary should be used correctly.",
            "weight": 0.10,
            "match_type": "terminology_usage"
        }
    },

    "penalties": {
        "wrong_fact": {
            "description": "Geographically incorrect statement or concept.",
            "deduction_percentage": 0.20
        },

        "multiple_wrong_facts": {
            "description": "More than one major geographical error.",
            "deduction_percentage": 0.40
        },

        "missing_core_points": {
            "description": "Important geographical aspects are missing.",
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
        "check_cause_effect_relationships": True,
        "use_semantic_similarity": True,
        "return_json_only": True
    },

    "evaluation_notes": [
        "Geographical accuracy carries the highest weight.",
        "Important features, factors, and concepts should be covered.",
        "Cause-effect relationships and geographical reasoning should be rewarded.",
        "Use of proper geographical terminology improves answer quality.",
        "One factual mistake may be tolerated, but multiple mistakes should reduce marks significantly."
    ]
}

GEOGRAPHY_SHORT_ANSWER = {
    "rubric_id": "geography_short_answer",
    "subject": "geography",
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
        "geographical_facts": {
            "description": "Answer must contain clear and correct geographical facts, features, concepts, or characteristics.",
            "weight": 0.70,
            "minimum_correct_facts": 3,
            "expected_facts": 4,
            "allowed_incorrect_facts": 1,
            "scoring_mode": "threshold_partial"
        },

        "accuracy": {
            "description": "Locations, resources, climatic features, geographical processes, and terminology should be accurate.",
            "weight": 0.30,
            "match_type": "geographical_accuracy"
        }
    },

    "penalties": {
        "wrong_fact": {
            "description": "Geographically incorrect statement or concept.",
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
        "Geographical facts and concepts must be accurate.",
        "Important features, characteristics, or causes should be included where relevant.",
        "Minor wording differences should not reduce marks if the meaning is correct.",
        "Partial credit should be awarded when most geographical facts are correct.",
        "The answer should remain focused on the asked geographical concept, feature, process, or location."
    ]
}

CIVICS_LONG_ANSWER = {
    "rubric_id": "civics_long_answer",
    "subject": "civics",
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
        "conceptual_accuracy": {
            "description": "Civics concepts, institutions, rights, duties, laws, and governance-related statements should be accurate.",
            "weight": 0.45,
            "match_type": "conceptual_accuracy"
        },

        "key_civics_points": {
            "description": "Student should cover the important points, features, functions, responsibilities, or principles expected in the answer.",
            "weight": 0.30,
            "expected_points": 6,
            "minimum_correct_points": 5,
            "use_semantic_similarity": True
        },

        "explanation_and_reasoning": {
            "description": "The answer should explain why, how, importance, significance, or impact where applicable.",
            "weight": 0.15,
            "match_type": "reasoning_quality"
        },

        "use_of_civics_terminology": {
            "description": "Appropriate civics terminology should be used correctly.",
            "weight": 0.10,
            "match_type": "terminology_usage"
        }
    },

    "penalties": {
        "wrong_concept": {
            "description": "Incorrect civics concept, institution, right, duty, or governance-related statement.",
            "deduction_percentage": 0.20
        },

        "multiple_wrong_concepts": {
            "description": "More than one major conceptual error.",
            "deduction_percentage": 0.40
        },

        "missing_core_points": {
            "description": "Important civics aspects are missing.",
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
        "check_reasoning_quality": True,
        "use_semantic_similarity": True,
        "return_json_only": True
    },

    "evaluation_notes": [
        "Conceptual accuracy carries the highest weight.",
        "Important features, functions, rights, duties, or principles should be covered.",
        "Reasoning and explanation should be rewarded where relevant.",
        "Correct use of civics terminology improves answer quality.",
        "Multiple conceptual mistakes should significantly reduce marks."
    ]
}

CIVICS_SHORT_ANSWER = {
    "rubric_id": "civics_short_answer",
    "subject": "civics",
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
        "civics_concepts": {
            "description": "Answer must contain correct civics concepts, principles, rights, duties, institutions, or governance-related facts.",
            "weight": 0.70,
            "minimum_correct_facts": 3,
            "expected_facts": 4,
            "allowed_incorrect_facts": 1,
            "scoring_mode": "threshold_partial"
        },

        "accuracy": {
            "description": "Civics terminology, concepts, institutions, and governance-related statements should be accurate.",
            "weight": 0.30,
            "match_type": "conceptual_accuracy"
        }
    },

    "penalties": {
        "wrong_concept": {
            "description": "Incorrect civics concept or statement.",
            "deduction_percentage": 0.25
        },

        "irrelevant_fact": {
            "description": "Point is not related to the question.",
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
        "Civics concepts and terminology must be accurate.",
        "Definitions and explanations should remain concise and relevant.",
        "Minor wording differences should not reduce marks if the meaning is correct.",
        "Partial credit should be awarded when most concepts are correct.",
        "The answer should remain focused on the asked civics concept, institution, right, duty, or principle."
    ]
}

ECONOMICS_LONG_ANSWER = {
    "rubric_id": "economics_long_answer",
    "subject": "economics",
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
        "economic_concept_accuracy": {
            "description": "Economic concepts, terms, sectors, resources, production activities, and economic statements should be accurate.",
            "weight": 0.45,
            "match_type": "conceptual_accuracy"
        },

        "key_economic_points": {
            "description": "Student should cover the important economic concepts, factors, features, causes, effects, or examples expected in the answer.",
            "weight": 0.30,
            "expected_points": 6,
            "minimum_correct_points": 5,
            "use_semantic_similarity": True
        },

        "economic_reasoning": {
            "description": "The answer should clearly explain economic relationships, causes, effects, significance, or impacts where applicable.",
            "weight": 0.15,
            "match_type": "economic_reasoning"
        },

        "use_of_economic_terminology": {
            "description": "Appropriate economic terminology should be used correctly.",
            "weight": 0.10,
            "match_type": "terminology_usage"
        }
    },

    "penalties": {
        "wrong_concept": {
            "description": "Incorrect economic concept, relationship, or statement.",
            "deduction_percentage": 0.20
        },

        "multiple_wrong_concepts": {
            "description": "More than one major conceptual error.",
            "deduction_percentage": 0.40
        },

        "missing_core_points": {
            "description": "Important economic aspects are missing.",
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
        "check_reasoning_quality": True,
        "use_semantic_similarity": True,
        "return_json_only": True
    },

    "evaluation_notes": [
        "Conceptual accuracy carries the highest weight.",
        "Important economic factors, causes, effects, and concepts should be covered.",
        "Economic reasoning should be rewarded.",
        "Correct use of economic terminology improves answer quality.",
        "Multiple conceptual mistakes should significantly reduce marks."
    ]
}

ECONOMICS_SHORT_ANSWER = {
    "rubric_id": "economics_short_answer",
    "subject": "economics",
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
        "economic_facts_and_concepts": {
            "description": "Answer must contain correct economic concepts, definitions, characteristics, factors, or examples relevant to the question.",
            "weight": 0.70,
            "minimum_correct_facts": 3,
            "expected_facts": 4,
            "allowed_incorrect_facts": 1,
            "scoring_mode": "threshold_partial"
        },

        "accuracy": {
            "description": "Economic terminology, concepts, and relationships should be accurate.",
            "weight": 0.30,
            "match_type": "conceptual_accuracy"
        }
    },

    "penalties": {
        "wrong_concept": {
            "description": "Incorrect economic concept or statement.",
            "deduction_percentage": 0.25
        },

        "irrelevant_fact": {
            "description": "Point is not related to the question.",
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
        "Economic concepts and terminology must be accurate.",
        "Definitions and explanations should remain concise and relevant.",
        "Minor wording differences should not reduce marks if the meaning is correct.",
        "Partial credit should be awarded when most concepts are correct.",
        "The answer should remain focused on the asked economic concept, factor, sector, activity, or relationship."
    ]
}

RUBRIC_REGISTRY = {
    ("english", "long_answer"): ENGLISH_LONG_ANSWER,
    ("english", "short_answer"): ENGLISH_SHORT_ANSWER,

    ("history", "long_answer"): HISTORY_LONG_ANSWER,
    ("history", "short_answer"): HISTORY_SHORT_ANSWER,

    ("hindi","long_answer"): HINDI_LONG_ANSWER,
    ("hindi","short_answer"): HINDI_SHORT_ANSWER,

    ("geography","long_answer"):GEOGRAPHY_LONG_ANSWER,
    ("geography","short_answer"):GEOGRAPHY_SHORT_ANSWER,

    ("civics","long_answer"):CIVICS_LONG_ANSWER,
    ("civics","short_answer"):CIVICS_SHORT_ANSWER,

    ("economics","long_answer"):ECONOMICS_LONG_ANSWER,
    ("economics","short_answer"):ECONOMICS_SHORT_ANSWER
}