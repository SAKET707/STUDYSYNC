import logging
from typing import List
from pydantic import BaseModel, Field

from mcq.schemas import GeneratedMCQ

logger = logging.getLogger(__name__)



class ValidationResult(BaseModel):
    """
    Data contract representing the structural and linguistic health of an MCQ.
    """
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)



class MCQValidator:
    """
    Component 5 of the MCQ Pipeline (Quality Gate 1).
    Responsibility: Evaluates whether a GeneratedMCQ object meets the baseline 
    structural, mechanical, and length-sanity thresholds required for a NEET test.
    """

  
    MIN_QUESTION_CHAR_LEN = 15
    MIN_OPTION_CHAR_LEN = 2
    MIN_EXPLANATION_CHAR_LEN = 15

    def validate(self, mcq: GeneratedMCQ) -> ValidationResult:
        """
        Runs comprehensive structural and deterministic rules against a single MCQ.
        Returns a ValidationResult object detailing rules broken.
        """
        errors: List[str] = []
        warnings: List[str] = []

       
        question_cleaned = mcq.question.strip()
        if not question_cleaned:
            errors.append("Question text is empty or contains only whitespace.")
        elif len(question_cleaned) < self.MIN_QUESTION_CHAR_LEN:
            errors.append(
                f"Question text fails length sanity check ({len(question_cleaned)} chars). "
                f"Minimum required is {self.MIN_QUESTION_CHAR_LEN} chars."
            )

     
        explanation_cleaned = mcq.explanation.strip()
        if not explanation_cleaned:
            errors.append("Pedagogical explanation text is empty or contains only whitespace.")
        elif len(explanation_cleaned) < self.MIN_EXPLANATION_CHAR_LEN:
            warnings.append(
                f"Explanation is unusually brief ({len(explanation_cleaned)} chars). "
                f"May lack optimal academic depth for NEET review."
            )

      
        options = [
            mcq.option_1.strip(),
            mcq.option_2.strip(),
            mcq.option_3.strip(),
            mcq.option_4.strip()
        ]

        for idx, option in enumerate(options, start=1):
            if not option:
                errors.append(f"Option {idx} is empty or contains only whitespace.")
            elif len(option) < self.MIN_OPTION_CHAR_LEN:
                errors.append(
                    f"Option {idx} text ('{option}') fails length sanity check. "
                    f"Too brief to represent a realistic biological option."
                )

       
        normalized_options = [opt.strip().lower() for opt in options if opt]
        if len(set(normalized_options)) < len(normalized_options):
            errors.append("Duplicate options detected. All four options must be entirely unique.")

       
        if mcq.correct_option < 1 or mcq.correct_option > 4:
            errors.append(f"Correct option pointer ({mcq.correct_option}) out of bounds. Must be an integer between 1 and 4.")
        else:
            
            correct_answer_text = options[mcq.correct_option - 1]
            if not correct_answer_text.strip():
                errors.append("Correct option pointer points to an empty option.")

        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def validate_batch(self, mcqs: List[GeneratedMCQ]) -> List[GeneratedMCQ]:
        """
        Executes batch evaluation on a collection of MCQs. 
        Maintains the partial success pattern by filtering out structural failures while processing survivors.
        """
        initial_count = len(mcqs)
        valid_mcqs: List[GeneratedMCQ] = []

        logger.info(f"Initiating batch structural validation for {initial_count} MCQs.")

        for index, mcq in enumerate(mcqs):
            result = self.validate(mcq)
            
            if result.is_valid:
                valid_mcqs.append(mcq)
                if result.warnings:
                    logger.warning(f"MCQ at index {index} passed validation with warnings: {result.warnings}")
            else:
                logger.error(
                    f"MCQ structural gate rejection at index {index}.\n"
                    f"Question Preview: '{mcq.question[:40]}...'\n"
                    f"Validation Errors Raised: {result.errors}"
                )

        logger.info(f"Batch validation complete. {len(valid_mcqs)}/{initial_count} MCQs cleared this gate.")
        return valid_mcqs