import logging
from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import (
    MODEL_REGENERATOR,
    MODEL_REGENERATOR_FALLBACK,
    USE_SEARCH_TOOL,
    get_client_credentials
)
from schemas import CompanyFull
from validator import PipelineValidator

logger = logging.getLogger("RegenerationLoop")

class RegenerationLoop:
    def __init__(self):
        extra_body = None
        api_key, api_base, model_slug = get_client_credentials(MODEL_REGENERATOR)
        
        # openrouter:web_search is only valid for OpenRouter endpoints
        if USE_SEARCH_TOOL and "openrouter.ai" in api_base:
            extra_body = {
                "tools": [{"type": "openrouter:web_search"}]
            }
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=api_base,
            model_name=model_slug,
            temperature=0.1,
            max_tokens=500,
            extra_body=extra_body
        )

    def regenerate_field(self, company_name: str, field: str, current_value: Any, error_msg: str) -> Any:
        logger.info(f"Regenerating field '{field}' for {company_name}. Error was: {error_msg}")
        
        field_info = CompanyFull.model_fields[field]
        desc = field_info.description or ""
        
        prompt_text = (
            "You are a Data Correction Agent.\n"
            "We are compiling research for the company '{company_name}'.\n"
            "The parameter '{field}' ({desc}) currently has the value: '{current_value}'.\n"
            "This value failed validation with the following error: '{error_msg}'.\n\n"
            "INSTRUCTIONS:\n"
            "1. Search the web specifically to find the correct, updated, or standard value for this parameter.\n"
            "2. Ensure it satisfies the validation rule (e.g. if it requires a valid email, find the correct email; if it requires a year, find the 4-digit year; if it requires a rating, find the float between 1.0 and 5.0).\n"
            "3. Return ONLY the corrected value. Do not output any JSON structure, explanation, markdown backticks, or extra words. Output only the value string or number."
        )
        
        prompt = PromptTemplate(
            template=prompt_text,
            input_variables=["company_name", "field", "desc", "current_value", "error_msg"]
        )
        
        formatted_prompt = prompt.format(
            company_name=company_name,
            field=field,
            desc=desc,
            current_value=current_value,
            error_msg=error_msg
        )
        
        try:
            response = self.llm.invoke(formatted_prompt)
            corrected_value = response.content.strip()
            logger.info(f"Regeneration result for '{field}': '{corrected_value}'")
            
            # Simple type conversions
            # If the schema expects int or float, try to cast it
            type_str = str(field_info.annotation).lower()
            if "int" in type_str:
                try:
                    return int(float(corrected_value))
                except ValueError:
                    pass
            elif "float" in type_str:
                try:
                    return float(corrected_value)
                except ValueError:
                    pass
            
            return corrected_value
        except Exception as primary_error:
            logger.warning(f"Primary regeneration model failed for '{field}': {primary_error}. Attempting fallback model ({MODEL_REGENERATOR_FALLBACK})...")
            try:
                extra_body = None
                api_key, api_base, model_slug = get_client_credentials(MODEL_REGENERATOR_FALLBACK)
                
                # openrouter:web_search is only valid for OpenRouter endpoints
                if USE_SEARCH_TOOL and "openrouter.ai" in api_base:
                    extra_body = {
                        "tools": [{"type": "openrouter:web_search"}]
                    }
                fallback_llm = ChatOpenAI(
                    openai_api_key=api_key,
                    openai_api_base=api_base,
                    model_name=model_slug,
                    temperature=0.1,
                    max_tokens=500,
                    extra_body=extra_body
                )
                response = fallback_llm.invoke(formatted_prompt)
                corrected_value = response.content.strip()
                logger.info(f"Regeneration result via fallback LLM ({MODEL_REGENERATOR_FALLBACK}) for '{field}': '{corrected_value}'")
                
                # Simple type conversions
                type_str = str(field_info.annotation).lower()
                if "int" in type_str:
                    try:
                        return int(float(corrected_value))
                    except ValueError:
                        pass
                elif "float" in type_str:
                    try:
                        return float(corrected_value)
                    except ValueError:
                        pass
                return corrected_value
            except Exception as secondary_error:
                logger.error(f"Fallback regeneration model failed for '{field}': {secondary_error}. Keeping original value.")
                return current_value

    def run_loop(self, company_name: str, consolidated: Dict[str, Any], max_attempts: int = 3, steps_log: list = None) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Runs the self-healing loop until validation succeeds or max attempts are reached.
        """
        attempt = 1
        errors = PipelineValidator.validate_company(consolidated)
        
        while errors and attempt <= max_attempts:
            msg = f"[Attempt {attempt}/{max_attempts}] Consolidated record has {len(errors)} validation errors."
            logger.warning(msg)
            if steps_log is not None:
                steps_log.append(msg)
            
            # Regenerate each failed field
            for err in errors:
                field = err["field"]
                curr_val = err["value"]
                err_msg = err["error"]
                
                corrected = self.regenerate_field(company_name, field, curr_val, err_msg)
                consolidated[field] = corrected
                if steps_log is not None:
                    steps_log.append(f"  - Regenerated field '{field}': '{curr_val}' -> '{corrected}' (Reason: {err_msg})")
                
            # Re-validate
            errors = PipelineValidator.validate_company(consolidated)
            attempt += 1
            
        if not errors:
            msg = "Validation succeeded! The record is clean and verified."
            logger.info(msg)
            if steps_log is not None:
                steps_log.append(msg)
        else:
            msg = f"Validation failed after {max_attempts} attempts. Remaining errors: {errors}"
            logger.error(msg)
            if steps_log is not None:
                steps_log.append(msg)
            
        return consolidated, errors
