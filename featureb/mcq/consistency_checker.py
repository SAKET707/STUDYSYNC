import json
import logging
import concurrent.futures
from typing import Any, List
from pydantic import BaseModel, Field, ValidationError

from langchain_core.messages import SystemMessage, HumanMessage

from mcq.schemas import GeneratedMCQ

logger = logging.getLogger(__name__)

class ConsistencyResult(BaseModel):
    """
    Data contract representing the semantic and logical integrity of an MCQ.
    """
    is_consistent: bool
    reason: str
    errors: List[str] = Field(default_factory=list)

class LLMConsistencyResponse(BaseModel):
    """Internal contract to force the LLM reviewer to output strict JSON."""
    is_consistent: bool
    reason: str


class MCQConsistencyChecker:
    """
    Component 6 of the MCQ Pipeline (Quality Gate 2).
    Responsibility: Acts as an adversarial LLM reviewer to ensure the generated 
    Explanation logically supports the designated Correct Option. 
    Catches "pointer mismatch" hallucinations.
    """

    def __init__(self, llm: Any):
        self.llm = llm

    def _build_evaluation_prompt(self, mcq: GeneratedMCQ) -> str:
        """
        Constructs the strict analysis prompt. Feeds the isolated MCQ parts
        to the reviewer model to spot internal contradictions.
        """
        options = {
            1: mcq.option_1,
            2: mcq.option_2,
            3: mcq.option_3,
            4: mcq.option_4
        }
        designated_correct_text = options.get(mcq.correct_option, "UNKNOWN OPTION")

        return f"""You are an expert Quality Assurance reviewer for NEET Biology examinations.
Your task is to analyze the following Multiple Choice Question to ensure logical consistency.

--- QUESTION PAYLOAD ---
Question: {mcq.question}
Option 1: {mcq.option_1}
Option 2: {mcq.option_2}
Option 3: {mcq.option_3}
Option 4: {mcq.option_4}

Designated Correct Option: Option {mcq.correct_option} ({designated_correct_text})
Provided Explanation: {mcq.explanation}
------------------------

TASK:
Determine if the Provided Explanation definitively supports the Designated Correct Option. 
Look out for contradictions (e.g., the explanation justifies Option 1, but the designated correct option is 2).

IMPORTANT:
Ignore whether the biology fact itself is correct.
Only determine whether the explanation supports the designated correct option.

CRITICAL RULE:
Respond ONLY with a raw, valid JSON object matching this schema. No markdown, no prose.
{{
  "is_consistent": true/false,
  "reason": "Brief justification of your ruling."
}}
"""

    def _clean_json_response(self, raw_text: str) -> str:
        """Strips markdown code fences that LLMs frequently append."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
            
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        return cleaned.strip()

    def check(self, mcq: GeneratedMCQ) -> ConsistencyResult:
        """
        Invokes the LLM to perform a semantic consistency review on a single MCQ.
        """
        prompt = self._build_evaluation_prompt(mcq)
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a strict, JSON-only logical reviewer. Output nothing but valid JSON."),
                HumanMessage(content=prompt)
            ])
            
            raw_content = response.content if isinstance(response.content, str) else str(response.content)
            cleaned_json_string = self._clean_json_response(raw_content)
            
            if not cleaned_json_string:
                 return ConsistencyResult(
                     is_consistent=False, 
                     reason="Reviewer LLM returned empty content.", 
                     errors=["LLM Evaluation Failed"]
                 )

            parsed_json = json.loads(cleaned_json_string)
            evaluation = LLMConsistencyResponse(**parsed_json)
            
            errors = []
            if not evaluation.is_consistent:
                errors.append(f"Logical Contradiction Detected: {evaluation.reason}")
                
            return ConsistencyResult(
                is_consistent=evaluation.is_consistent,
                reason=evaluation.reason,
                errors=errors
            )

        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Failed to parse consistency review output. Marking MCQ as inconsistent to be safe. Error: {e}")
            return ConsistencyResult(
                is_consistent=False, 
                reason="Reviewer evaluation output was malformed.", 
                errors=[f"Schema parsing error: {e}"]
            )
        except Exception as e:
             logger.error(f"Fatal error during consistency check LLM invocation: {e}")
             return ConsistencyResult(
                 is_consistent=False,
                 reason="API Failure during review.",
                 errors=[str(e)]
             )

    def check_batch(self, mcqs: List[GeneratedMCQ], max_workers: int = 5) -> List[GeneratedMCQ]:
        """
        Executes parallel consistency evaluation on a collection of structurally valid MCQs.
        Filters out semantic failures while processing survivors.
        """
        if not mcqs:
            return []

        initial_count = len(mcqs)
        consistent_mcqs: List[GeneratedMCQ] = []

        logger.info(f"Initiating parallel logical consistency review for {initial_count} MCQs (Max Workers: {max_workers}).")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_mcq = {executor.submit(self.check, mcq): mcq for mcq in mcqs}

            for future in concurrent.futures.as_completed(future_to_mcq):
                mcq = future_to_mcq[future]
                try:
                    result = future.result()
                    
                    if result.is_consistent:
                        consistent_mcqs.append(mcq)
                    else:
                        # Logged as a warning because filtering bad generations is expected behavior, not a system failure.
                        logger.warning(
                            f"MCQ Consistency Check Failed.\n"
                            f"Question Preview: '{mcq.question[:40]}...'\n"
                            f"Reason: {result.reason}"
                        )
                except Exception as exc:
                    logger.error(f"Parallel evaluation thread failed for a GeneratedMCQ: {exc}")

        logger.info(f"Consistency review complete. {len(consistent_mcqs)}/{initial_count} MCQs cleared this gate.")
        return consistent_mcqs