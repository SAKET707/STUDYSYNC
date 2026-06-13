import json
import logging
import concurrent.futures
from typing import Any, List, Dict
from pydantic import BaseModel, Field, ValidationError

from langchain_core.messages import SystemMessage, HumanMessage

# Strict Data Contracts (Standardized plural schemas)
from mcq.schemas import GeneratedMCQ
from retrieval.schema import ParentContext

logger = logging.getLogger(__name__)

MAX_CONTEXT_CHARS = 4000 

class FaithfulnessResult(BaseModel):
    """
    Data contract representing whether an MCQ is strictly grounded in the source text.
    """
    is_faithful: bool
    reason: str
    errors: List[str] = Field(default_factory=list)

class LLMFaithfulnessResponse(BaseModel):
    """Internal contract to force the LLM reviewer to output strict JSON."""
    is_faithful: bool
    reason: str

class MCQFaithfulnessChecker:
    """
    Component 7 of the MCQ Pipeline (Quality Gate 3).
    Responsibility: Acts as a strict Anti-Hallucination auditor.
    Verifies that the generated question, options, and explanation are 100% 
    derivable from the specific NCERT parent context, preventing cross-contamination.
    """

    def __init__(self, llm: Any):
        self.llm = llm

    def _build_evaluation_prompt(self, mcq: GeneratedMCQ, context_text: str) -> str:
        """
        Constructs the strict grounding analysis prompt. 
        """
        
        if len(context_text) > MAX_CONTEXT_CHARS:
            context_text = context_text[:MAX_CONTEXT_CHARS] + "\n...[TRUNCATED]"

        return f"""You are a strict Anti-Hallucination Auditor for a medical entrance exam platform.
Your task is to determine if the following Multiple Choice Question is 100% FAITHFUL to the provided textbook context.

--- TEXTBOOK CONTEXT (GROUND TRUTH) ---
{context_text}
---------------------------------------

--- GENERATED MCQ ---
Question: {mcq.question}
Option 1: {mcq.option_1}
Option 2: {mcq.option_2}
Option 3: {mcq.option_3}
Option 4: {mcq.option_4}
Explanation: {mcq.explanation}
---------------------

TASK:
Determine if the Generated MCQ relies on ANY outside information not explicitly stated or strongly implied by the Textbook Context. 
If the question, ANY of the options, or the explanation contains facts, terms, or relationships missing from the Context, it is NOT faithful.

IMPORTANT:
Do not use external biology knowledge.
Judge only using the supplied textbook context.
If information is missing from the context, mark the MCQ as unfaithful.

CRITICAL RULE:
Respond ONLY with a raw, valid JSON object matching this schema. No markdown, no prose.
{{
  "is_faithful": true/false,
  "reason": "Briefly point out the exact sentence that supports the MCQ, or specify the exact term that was hallucinated."
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

    def check(self, mcq: GeneratedMCQ, context_text: str) -> FaithfulnessResult:
        """
        Invokes the LLM to perform a grounding review on a single MCQ against the source text.
        """
        if not context_text.strip():
            return FaithfulnessResult(
                is_faithful=False, 
                reason="No source context was provided for validation.", 
                errors=["Empty Context Error"]
            )

        prompt = self._build_evaluation_prompt(mcq, context_text)
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an uncompromising fact-checker. Output nothing but valid JSON."),
                HumanMessage(content=prompt)
            ])
            
            raw_content = response.content if isinstance(response.content, str) else str(response.content)
            cleaned_json_string = self._clean_json_response(raw_content)
            
            if not cleaned_json_string:
                 return FaithfulnessResult(
                     is_faithful=False, 
                     reason="Reviewer LLM returned empty content.", 
                     errors=["LLM Evaluation Failed"]
                 )

            parsed_json = json.loads(cleaned_json_string)
            evaluation = LLMFaithfulnessResponse(**parsed_json)
            
            errors = []
            if not evaluation.is_faithful:
                errors.append(f"Hallucination Detected: {evaluation.reason}")
                
            return FaithfulnessResult(
                is_faithful=evaluation.is_faithful,
                reason=evaluation.reason,
                errors=errors
            )

        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Failed to parse faithfulness review output. Error: {e}")
            return FaithfulnessResult(is_faithful=False, reason="Reviewer evaluation output was malformed.", errors=[str(e)])
        except Exception as e:
             logger.error(f"Fatal error during faithfulness check LLM invocation: {e}")
             return FaithfulnessResult(is_faithful=False, reason="API Failure during review.", errors=[str(e)])

    def check_batch(self, mcqs: List[GeneratedMCQ], parent_contexts: List[ParentContext], max_workers: int = 5) -> List[GeneratedMCQ]:
        """
        Executes precision parallel faithfulness evaluation. 
        Maps each MCQ back to its specific originating parent block to prevent cross-contamination hallucinations.
        """
        if not mcqs:
            return []

        initial_count = len(mcqs)
        faithful_mcqs: List[GeneratedMCQ] = []
        failed_count = 0

        logger.info(f"Initiating parallel anti-hallucination review for {initial_count} MCQs (Max Workers: {max_workers}).")

        context_map: Dict[str, str] = {str(p.parent_id): str(p.text) for p in parent_contexts}
        
        # Memory/Token Optimization: Limit fallback to the first 5 contexts
        # Prevents building a massive string just to have it arbitrarily truncated later
        combined_fallback = "\n\n".join(list(context_map.values())[:5])

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_mcq = {}
            for mcq in mcqs:
                if mcq.source_parent_id and mcq.source_parent_id in context_map:
                    specific_context = context_map[mcq.source_parent_id]
                else:
                    specific_context = combined_fallback

                future_to_mcq[executor.submit(self.check, mcq, specific_context)] = mcq

            for future in concurrent.futures.as_completed(future_to_mcq):
                mcq = future_to_mcq[future]
                try:
                    result = future.result()
                    
                    if result.is_faithful:
                        faithful_mcqs.append(mcq)
                    else:
                        logger.warning(
                            f"Hallucination / Ungrounded Fact Caught!\n"
                            f"Question Preview: '{mcq.question[:40]}...'\n"
                            f"Reason: {result.reason}"
                        )
                        failed_count += 1
                except Exception as exc:
                    logger.error(f"Parallel evaluation thread failed for a GeneratedMCQ: {exc}")
                    failed_count += 1 

        logger.info(
            f"Faithfulness review complete. "
            f"{len(faithful_mcqs)}/{initial_count} MCQs cleared this final gate. "
            f"Total failures (Hallucinations + Errors): {failed_count}"
        )
        return faithful_mcqs