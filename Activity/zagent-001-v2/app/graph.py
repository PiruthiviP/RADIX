import re
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Tuple, TypedDict
from langgraph.graph import StateGraph, START, END

from app.intelligence_schema import SchemaManager, FieldSpec
from app.validation import ValidationEngine, normalize_value
from app.providers import ProviderAdapter, ProviderFactory
from app.research import ResearchEngine

logger = logging.getLogger(__name__)

# State shape definition
class WorkflowState(TypedDict, total=False):
    admin_data: Dict[str, Any]
    temperature: float
    max_retry_rounds: int
    strict_grounding_regeneration: bool
    schema_totals: Dict[str, int]
    missing_fields: List[str]
    research_docs: List[Dict[str, str]]
    research_context: str
    batch_plan: List[str]
    provider_datasets: Dict[str, Dict[str, Any]]
    provider_stats: Dict[str, Dict[str, Any]] # Map of provider -> stats dict
    consolidated_sources: Dict[str, str]       # Map of field_name -> provider_name
    final_profile: Dict[str, Any]
    generation_status: str
    progress_callback: Optional[Callable[[str, float], None]]


def build_batch_prompt(fields_to_query: List[FieldSpec], admin_data: Dict[str, Any], research_context: str) -> str:
    """Builds a structured prompt asking the LLM to output a JSON payload for the requested fields."""
    fields_desc = ""
    for spec in fields_to_query:
        enum_info = f" Allowed values: {spec.enum_values}." if spec.enum_values else ""
        fields_desc += f"- {spec.name} ({spec.field_type}): {spec.description}.{enum_info}\n"

    prompt = f"""You are a professional company intelligence analyst.
Your task is to extract structural facts and metrics for the company '{admin_data.get("companyName")}' using the provided Research Context.

Administrative Grounding Inputs:
{json.dumps(admin_data, indent=2)}

Research Context:
{research_context}

Please extract the values for the following fields. If a field's value cannot be confidently verified in the context, set it to "NA":
{fields_desc}

Provide your output ONLY as a valid JSON object matching the requested field names. Do not include markdown code block formatting (like ```json), explanation text, or extra fields. If a value cannot be found in the context or guidelines, output "NA" for that field.

JSON Output:
"""
    return prompt


def clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """Cleans markdown blocks and returns parsed JSON dictionary."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        
    first_bracket = cleaned.find("{")
    last_bracket = cleaned.rfind("}")
    if first_bracket != -1 and last_bracket != -1:
        cleaned = cleaned[first_bracket:last_bracket+1]

    try:
        return json.loads(cleaned)
    except Exception as e:
        logger.warning(f"JSON parsing failed. Extracting key-value patterns via regex. Error: {str(e)}")
        # Simple regex extraction fallback if JSON parsing failed completely
        extracted = {}
        pattern = r'"(\w+)":\s*(?:"([^"]*)"|(\[.*?\])|(\d+)|(true|false|null))'
        matches = re.findall(pattern, cleaned)
        for m in matches:
            key = m[0]
            val = m[1] or m[2] or m[3] or m[4]
            if val == "null":
                extracted[key] = "NA"
            elif val.startswith("["):
                try:
                    extracted[key] = json.loads(val)
                except Exception:
                    extracted[key] = []
            else:
                extracted[key] = val
        return extracted


def calculate_overlap(value: str, context: str) -> float:
    """Calculates word overlap percentage for words length >= 3 in research context."""
    if not value or value == "NA":
        return 0.0
        
    # Clean and split into words
    val_words = [w.strip(".,!?;:()[]\"'").lower() for w in value.split()]
    val_words = [w for w in val_words if len(w) >= 3]
    if not val_words:
        return 0.0
        
    context_words = set(w.strip(".,!?;:()[]\"'").lower() for w in context.split())
    context_words = {w for w in context_words if len(w) >= 3}
    
    overlap_count = sum(1 for w in val_words if w in context_words)
    return overlap_count / len(val_words)


# Node Definitions
def validate_input_node(state: WorkflowState) -> Dict[str, Any]:
    if state.get("progress_callback"):
        state["progress_callback"]("validate_input", 5.0)
    
    admin_data = state.get("admin_data", {})
    normalized_admin = {}
    for k, v in admin_data.items():
        if v is not None:
            normalized_admin[k] = v
        else:
            normalized_admin[k] = "NA"
            
    return {"admin_data": normalized_admin, "generation_status": "IN_PROGRESS"}


def load_schema_node(state: WorkflowState) -> Dict[str, Any]:
    if state.get("progress_callback"):
        state["progress_callback"]("load_schema", 10.0)
        
    schema_manager = SchemaManager()
    admin_count, gen_count, total = schema_manager.totals()
    
    return {
        "schema_totals": {
            "admin": admin_count,
            "generated": gen_count,
            "total": total
        }
    }


def detect_missing_node(state: WorkflowState) -> Dict[str, Any]:
    if state.get("progress_callback"):
        state["progress_callback"]("detect_missing", 15.0)
        
    admin_data = state.get("admin_data", {})
    schema_manager = SchemaManager()
    
    missing = []
    for k, spec in schema_manager.fields.items():
        if spec.is_admin_grounded:
            val = admin_data.get(k)
            if val is None or val == "NA" or val == "":
                missing.append(k)
                
    return {"missing_fields": missing}


async def collect_research_node(state: WorkflowState) -> Dict[str, Any]:
    if state.get("progress_callback"):
        state["progress_callback"]("collect_research", 25.0)
        
    admin_data = state.get("admin_data", {})
    company_name = admin_data.get("companyName", "")
    website_url = admin_data.get("websiteUrl", "")
    
    research_engine = ResearchEngine(timeout_seconds=8)
    docs = await research_engine.collect(company_name, website_url)
    
    return {"research_docs": [docs]}


def build_context_node(state: WorkflowState) -> Dict[str, Any]:
    if state.get("progress_callback"):
        state["progress_callback"]("build_context", 30.0)
        
    docs_list = state.get("research_docs", [])
    if not docs_list:
        return {"research_context": ""}
        
    docs = docs_list[0]
    research_engine = ResearchEngine()
    context = research_engine.build_context(
        docs.get("wikipedia", ""),
        docs.get("homepage", ""),
        docs.get("guidelines", "")
    )
    
    return {"research_context": context}


def plan_batches_node(state: WorkflowState) -> Dict[str, Any]:
    if state.get("progress_callback"):
        state["progress_callback"]("plan_batches", 35.0)
        
    # The 6 generated batches
    batches = [
        "core_identity",
        "digital_presence",
        "financial_intelligence",
        "strategy_ecosystem",
        "work_culture",
        "career_growth"
    ]
    return {"batch_plan": batches}


# Custom generate node that takes providers list
def create_generate_node(active_providers: Dict[str, ProviderAdapter], validation_engine: ValidationEngine, schema_manager: SchemaManager) -> Callable[[WorkflowState], Dict[str, Any]]:
    
    async def generate_with_retry_node(state: WorkflowState) -> Dict[str, Any]:
        admin_data = state.get("admin_data", {})
        research_context = state.get("research_context", "")
        max_retry_rounds = state.get("max_retry_rounds", 2)
        strict_grounding = state.get("strict_grounding_regeneration", False)
        batch_plan = state.get("batch_plan", [])
        
        # Initialize datasets with grounded admin data
        all_fields = list(schema_manager.fields.keys())
        provider_datasets = {}
        provider_stats = {}
        
        for prov_name in active_providers.keys():
            dataset = {f: "NA" for f in all_fields}
            for k, v in admin_data.items():
                if v is not None and v != "NA":
                    dataset[k] = v
            provider_datasets[prov_name] = dataset
            provider_stats[prov_name] = {
                "accepted_fields": 13, # 13 admin fields initialized
                "failed_fields": 0,
                "retries_used": 0,
                "status_message": "Initialized"
            }

        # Create execution plan
        execution_plan = []
        if strict_grounding:
            execution_plan.append("admin")
        execution_plan.extend(batch_plan)

        total_steps = len(execution_plan)
        
        # Loop through each batch in the plan
        for step_idx, batch_name in enumerate(execution_plan):
            progress_val = 40.0 + (step_idx / total_steps) * 50.0
            if state.get("progress_callback"):
                state["progress_callback"](f"generating_batch_{batch_name}", progress_val)

            # Retrieve fields belonging to this batch
            if batch_name == "admin":
                fields_in_batch = [f for f in schema_manager.fields.values() if f.is_admin_grounded]
            else:
                fields_in_batch = schema_manager.get_fields_by_batch(batch_name)

            if not fields_in_batch:
                continue

            # Parallel query loop for each provider
            async def process_provider_batch(prov_name: str, adapter: ProviderAdapter) -> Tuple[str, Dict[str, Any], int]:
                # Start retry loop
                provider_dataset = provider_datasets[prov_name]
                fields_to_query = list(fields_in_batch)
                retries_used = 0
                
                for round_idx in range(1, max_retry_rounds + 1):
                    if not fields_to_query:
                        break
                    
                    retries_used = round_idx - 1
                    prompt = build_batch_prompt(fields_to_query, admin_data, research_context)
                    
                    # Async invoke the LLM provider
                    response_payload = await adapter.ainvoke(
                        prompt, 
                        company_name=admin_data.get("companyName", ""), 
                        batch_name=batch_name,
                        temperature=state.get("temperature", 0.2)
                    )
                    
                    if response_payload.get("error"):
                        logger.error(f"Provider {prov_name} batch {batch_name} error: {response_payload.get('error')}")
                        # Keep current fields to retry next round
                        continue

                    # Parse output JSON
                    raw_content = response_payload.get("content", "")
                    parsed_json = clean_and_parse_json(raw_content)

                    # Update local dataset values
                    for spec in fields_to_query:
                        if spec.name in parsed_json:
                            provider_dataset[spec.name] = parsed_json[spec.name]

                    # Validate dataset
                    valid_dataset, failed_fields_dict = validation_engine.validate_dataset(provider_dataset)
                    
                    # Filter failed fields belonging to the current batch
                    fields_to_query = [
                        spec for spec in fields_in_batch 
                        if spec.name in failed_fields_dict
                    ]

                # After retries exhausted, lock remaining invalid fields of this batch to "NA"
                for spec in fields_in_batch:
                    # Run a final validation check for this field
                    val = provider_dataset.get(spec.name)
                    norm_val, err = validation_engine.validate_value(val, spec)
                    if err:
                        provider_dataset[spec.name] = "NA"
                    else:
                        provider_dataset[spec.name] = norm_val

                return prov_name, provider_dataset, retries_used

            # Invoke active providers in parallel
            tasks = [
                process_provider_batch(prov_name, adapter)
                for prov_name, adapter in active_providers.items()
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Save results into state
            for prov_name, dataset, retries in results:
                provider_datasets[prov_name] = dataset
                provider_stats[prov_name]["retries_used"] += retries

        # Update final stats counts
        for prov_name in active_providers.keys():
            dataset = provider_datasets[prov_name]
            valid_ds, failed_ds = validation_engine.validate_dataset(dataset)
            
            provider_stats[prov_name]["accepted_fields"] = len(valid_ds)
            provider_stats[prov_name]["failed_fields"] = len(failed_ds)
            provider_stats[prov_name]["status_message"] = (
                f"Completed. Accepted: {len(valid_ds)}, Failed: {len(failed_ds)}"
            )

        return {
            "provider_datasets": provider_datasets,
            "provider_stats": provider_stats
        }

    return generate_with_retry_node


def create_consolidate_node(schema_manager: SchemaManager) -> Callable[[WorkflowState], Dict[str, Any]]:
    
    def consolidate_node(state: WorkflowState) -> Dict[str, Any]:
        if state.get("progress_callback"):
            state["progress_callback"]("consolidate", 95.0)
            
        provider_datasets = state.get("provider_datasets", {})
        research_context = state.get("research_context", "")
        admin_data = state.get("admin_data", {})
        
        final_profile = {}
        consolidated_sources = {}
        
        # Copy over admin fields directly
        for k, spec in schema_manager.fields.items():
            if spec.is_admin_grounded:
                val = admin_data.get(k, "NA")
                final_profile[k] = val
                consolidated_sources[k] = "admin"

        # Resolve generated fields (152 fields total)
        for k, spec in schema_manager.fields.items():
            if spec.is_admin_grounded:
                continue
                
            # Collect values from all active providers
            provider_values = {}
            for prov, dataset in provider_datasets.items():
                val = dataset.get(k, "NA")
                if val != "NA":
                    provider_values[prov] = val
                    
            if not provider_values:
                # All providers returned "NA"
                final_profile[k] = "NA"
                consolidated_sources[k] = "NA"
                continue

            # 1. Majority Vote
            # Standardize casing/whitespace for matching
            normalized_to_prov = {}
            for prov, val in provider_values.items():
                norm = "".join(str(val).lower().split())
                if norm not in normalized_to_prov:
                    normalized_to_prov[norm] = []
                normalized_to_prov[norm].append((prov, val))
                
            # Check if any group has frequency >= 2
            majority_val = None
            majority_prov = None
            max_freq = 0
            
            for norm, prov_list in normalized_to_prov.items():
                if len(prov_list) > max_freq:
                    max_freq = len(prov_list)
                    # Pick the raw value from the first provider in that group
                    majority_prov, majority_val = prov_list[0]
                    
            if max_freq >= 2:
                final_profile[k] = majority_val
                consolidated_sources[k] = "consensus"
                continue

            # 2. Single Non-NA Fallback
            if len(provider_values) == 1:
                prov, val = list(provider_values.items())[0]
                final_profile[k] = val
                consolidated_sources[k] = prov
                continue

            # 3. Research Consistency Overlap
            # All providers differ, calculate overlap percentage against context
            highest_overlap = -1.0
            winning_val = "NA"
            winning_prov = "NA"
            
            for prov, val in provider_values.items():
                overlap = calculate_overlap(str(val), research_context)
                if overlap > highest_overlap:
                    highest_overlap = overlap
                    winning_val = val
                    winning_prov = prov
                    
            if highest_overlap > 0.0:
                final_profile[k] = winning_val
                consolidated_sources[k] = winning_prov
            else:
                # No overlap, fallback to first provider's value
                prov, val = list(provider_values.items())[0]
                final_profile[k] = val
                consolidated_sources[k] = prov

        if state.get("progress_callback"):
            state["progress_callback"]("completed", 100.0)
            
        return {
            "final_profile": final_profile,
            "consolidated_sources": consolidated_sources,
            "generation_status": "SUCCESS"
        }

    return consolidate_node


# Graph compilation builder
def build_workflow_graph(active_providers: Dict[str, ProviderAdapter], validation_engine: ValidationEngine, schema_manager: SchemaManager) -> StateGraph:
    # 1. Create StateGraph
    builder = StateGraph(WorkflowState)
    
    # 2. Register Nodes
    builder.add_node("validate_input", validate_input_node)
    builder.add_node("load_schema", load_schema_node)
    builder.add_node("detect_missing", detect_missing_node)
    builder.add_node("collect_research", collect_research_node)
    builder.add_node("build_context", build_context_node)
    builder.add_node("plan_batches", plan_batches_node)
    
    # Create nodes with injection dependencies
    generate_node = create_generate_node(active_providers, validation_engine, schema_manager)
    consolidate_node = create_consolidate_node(schema_manager)
    
    builder.add_node("generate_with_retry", generate_node)
    builder.add_node("consolidate", consolidate_node)
    
    # 3. Register Edges
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "load_schema")
    builder.add_edge("load_schema", "detect_missing")
    builder.add_edge("detect_missing", "collect_research")
    builder.add_edge("collect_research", "build_context")
    builder.add_edge("build_context", "plan_batches")
    builder.add_edge("plan_batches", "generate_with_retry")
    builder.add_edge("generate_with_retry", "consolidate")
    builder.add_edge("consolidate", END)
    
    # 4. Compile
    return builder.compile()
