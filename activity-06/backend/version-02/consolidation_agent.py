import json
import logging
from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import (
    MODEL_CONSOLIDATOR,
    MODEL_CONSOLIDATOR_FALLBACK,
    get_client_credentials
)
from schemas import CompanyFull
from validator import PipelineValidator

logger = logging.getLogger("ConsolidationAgent")

class ConsolidationAgent:
    def __init__(self):
        api_key, api_base, model_slug = get_client_credentials(MODEL_CONSOLIDATOR)
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=api_base,
            model_name=model_slug,
            temperature=0.0, # low temperature for deterministic reconciliation
            max_tokens=4096
        )

    def _normalize_val(self, val: Any) -> str:
        if val is None:
            return ""
        return str(val).strip().lower().replace(",", "").replace(" plc", "").replace(" inc", "")

    def pre_consolidate(self, datasets: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """
        Performs rule-based pre-consolidation across all available datasets dynamically:
        - If all agree (after normalization), choose that value.
        - If some are NA/empty, choose the non-empty value.
        - If there is disagreement, mark it as a conflict for the LLM to resolve.
        """
        consolidated = {}
        conflicts = {}
        
        all_fields = list(CompanyFull.model_fields.keys())
        if "company_id" in all_fields:
            all_fields.remove("company_id")
            
        for field in all_fields:
            # Gather all non-empty values for this field across all datasets
            field_vals = {}
            for model_name, data in datasets.items():
                val = data.get(field, "NA")
                if not PipelineValidator.is_empty_or_na(val):
                    field_vals[model_name] = val
            
            # Case 1: All empty
            if not field_vals:
                consolidated[field] = "NA"
                continue
                
            # Case 2: Only one is populated
            if len(field_vals) == 1:
                consolidated[field] = list(field_vals.values())[0]
                continue
                
            # Case 3: Multiple are populated. Check if they agree.
            norm_vals = {self._normalize_val(v): v for v in field_vals.values()}
            
            # If all normalized values are identical, choose the first raw value
            if len(norm_vals) == 1:
                consolidated[field] = list(field_vals.values())[0]
            else:
                # There is a conflict; store all values for this field from all models
                conflicts[field] = {
                    model_name: datasets.get(model_name, {}).get(field, "NA")
                    for model_name in datasets
                }
                
        return consolidated, conflicts

    def resolve_conflicts(self, company_name: str, conflicts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calls the LLM to resolve fields with conflicting values.
        """
        if not conflicts:
            return {}
            
        logger.info(f"Resolving {len(conflicts)} conflicting fields via LLM...")
        
        # Build prompt listing the conflicts
        conflict_list = []
        for field, options in conflicts.items():
            field_info = CompanyFull.model_fields[field]
            desc = field_info.description or ""
            options_lines = "\n".join([f"  - {model.capitalize()}: {val}" for model, val in options.items()])
            conflict_list.append(
                f"- **{field}** ({desc}):\n{options_lines}"
            )
            
        conflicts_str = "\n\n".join(conflict_list)
        
        prompt_text = (
            "You are a Data Reconciliation and Validation Engine.\n"
            "We have collected company intelligence for '{company_name}' using different search models, "
            "but they disagree on the following fields:\n\n"
            "{conflicts_str}\n\n"
            "INSTRUCTIONS:\n"
            "1. Resolve the conflict for each field. Choose the most accurate, complete, or standard value.\n"
            "2. If one of the values is more detailed, choose it. If one contains a citation or specific metric that looks correct, prefer it.\n"
            "3. If they are different formats of the same fact, standardize it (e.g. choose '$64.1B' over '64.1 billion USD' if standard, or vice versa depending on common patterns).\n"
            "4. Your output MUST be a single JSON object where the keys are the field names and the values are your resolved values. Example:\n"
            "   {{\n"
            "     \"field_name_1\": \"resolved_value_1\",\n"
            "     \"field_name_2\": \"resolved_value_2\"\n"
            "   }}\n"
            "5. Output ONLY the JSON object. Do not write any other text or markdown backticks."
        )
        
        prompt = PromptTemplate(
            template=prompt_text,
            input_variables=["company_name", "conflicts_str"]
        )
        
        formatted_prompt = prompt.format(
            company_name=company_name,
            conflicts_str=conflicts_str
        )
        
        try:
            response = self.llm.invoke(formatted_prompt)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            resolved_data = json.loads(content)
            logger.info("Successfully resolved conflicts via LLM.")
            return resolved_data
        except Exception as primary_error:
            logger.warning(f"Primary consolidation model failed: {primary_error}. Attempting fallback model ({MODEL_CONSOLIDATOR_FALLBACK})...")
            try:
                api_key, api_base, model_slug = get_client_credentials(MODEL_CONSOLIDATOR_FALLBACK)
                fallback_llm = ChatOpenAI(
                    openai_api_key=api_key,
                    openai_api_base=api_base,
                    model_name=model_slug,
                    temperature=0.0,
                    max_tokens=4096
                )
                response = fallback_llm.invoke(formatted_prompt)
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                resolved_data = json.loads(content)
                logger.info(f"Successfully resolved conflicts via fallback LLM ({MODEL_CONSOLIDATOR_FALLBACK}).")
                return resolved_data
            except Exception as secondary_error:
                logger.error(f"Fallback consolidation model failed: {secondary_error}. Falling back to default selection.")
                # Fallback: choose the first non-empty value
                fallback = {}
                for field, options in conflicts.items():
                    chosen_val = "NA"
                    for model_name, val in options.items():
                        if not PipelineValidator.is_empty_or_na(val):
                            chosen_val = val
                            break
                    fallback[field] = chosen_val
                return fallback

    def consolidate(self, company_name: str, datasets: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Orchestrates the entire consolidation flow.
        """
        # Step 1: Pre-consolidate based on rules
        consolidated, conflicts = self.pre_consolidate(datasets)
        
        # Step 2: Resolve conflicts via LLM if any exist
        if conflicts:
            resolved = self.resolve_conflicts(company_name, conflicts)
            consolidated.update(resolved)
            
        return consolidated
