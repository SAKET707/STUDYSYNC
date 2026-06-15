import json
import logging
from typing import Any
from pydantic import ValidationError


from langchain_core.messages import SystemMessage, HumanMessage


from retrieval.schema import RetrievalResult
from mcq.schemas import MCQGenerationRequest, MCQGenerationResult, GeneratedMCQ
from mcq.prompts import MCQ_SYSTEM_PROMPT, build_mcq_user_prompt

logger = logging.getLogger(__name__)

class MCQGenerator:
    """
    Phase 4 Orchestrator: The LLM Generation Layer.
    Responsibility: Translate chapter-based retrieval contexts into strict MCQ schemas via LLM invocation.
    Handles prompt compilation, robust API communication, JSON deserialization, schema validation, 
    and precise lineage mapping (source_block -> parent_id).
    """

    def __init__(self, llm: Any):
        self.llm = llm

    def _clean_json_response(self, raw_text: str) -> str:
        """
        Defensive utility. Strips markdown code fences that LLMs frequently 
        append despite strict system prompt instructions.
        """
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
            
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        return cleaned.strip()

    def generate(
        self, 
        retrieval_result: RetrievalResult, 
        request: MCQGenerationRequest
    ) -> MCQGenerationResult:
        """
        Executes the generation pipeline: Context mapping -> LLM generation -> Schema validation.
        """
        logger.info(f"Generating MCQs for chapter '{request.chapter}' ({request.num_questions} questions requested).")

        if not retrieval_result.parent_contexts:
            logger.warning("Generation aborted: No parent contexts were provided by the retrieval pipeline.")
            return MCQGenerationResult(mcqs=[])

        
        context_blocks = []
        context_map = {}
        for idx, context in enumerate(retrieval_result.parent_contexts):
            context_blocks.append(context.text)
          
            context_map[idx + 1] = context.parent_id 


        user_prompt = build_mcq_user_prompt(
            context_blocks=context_blocks,
            chapter=request.chapter,
            num_questions=request.num_questions
        )

        try:
            logger.debug("Invoking LLM with system instructions and contextual payload...")
            response = self.llm.invoke([
                SystemMessage(content=MCQ_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ])
            
            raw_content = (
                response.content 
                if isinstance(response.content, str) 
                else str(response.content)
            )
            
        except Exception as e:
            logger.error(f"Fatal error during LLM invocation: {e}")
            raise

        cleaned_json_string = self._clean_json_response(raw_content)
        
        if not cleaned_json_string:
            logger.error("LLM returned empty content after JSON cleaning.")
            return MCQGenerationResult(mcqs=[])
        
        try:
            raw_mcqs = json.loads(cleaned_json_string)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode LLM JSON output. Raw output:\n{raw_content}\nError: {e}")
            return MCQGenerationResult(mcqs=[])

        if not isinstance(raw_mcqs, list):
            logger.error("LLM returned valid JSON, but it is not a List/Array as requested.")
            return MCQGenerationResult(mcqs=[])

        generated_mcqs = []
        for index, item in enumerate(raw_mcqs):
            try:
                
                source_block_index = item.get("source_block")
                
               
                actual_parent_id = context_map.get(source_block_index) if source_block_index else None

                mcq = GeneratedMCQ(
                    question=item["question"],
                    option_1=item["option_1"],
                    option_2=item["option_2"],
                    option_3=item["option_3"],
                    option_4=item["option_4"],
                    correct_option=item["correct_option"],
                    explanation=item["explanation"],
                    source_parent_id=actual_parent_id  
                )
                generated_mcqs.append(mcq)
                
            except ValidationError as e:
                logger.warning(f"Schema validation failed for generated question at index {index}. Skipping.\nErrors: {e}")
                continue
            except KeyError as e:
                logger.warning(f"Missing required key in generated question at index {index}: {e}. Skipping.")
                continue

        if not generated_mcqs:
            logger.warning("No valid MCQs survived Pydantic schema validation. Returning empty result.")
            return MCQGenerationResult(mcqs=[])

        logger.info(f"Successfully generated and validated {len(generated_mcqs)} MCQs.")
        return MCQGenerationResult(mcqs=generated_mcqs)