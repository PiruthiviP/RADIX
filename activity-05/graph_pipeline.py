import os
import re
import logging
from typing import TypedDict, Dict, Any, List, Annotated
from langgraph.graph import StateGraph, END, START

# Import components from active directory
from validator import PipelineValidator
from consolidation_agent import ConsolidationAgent
from regeneration_loop import RegenerationLoop
from db_writer import DBWriter
from config import MODEL_CLAUDE, MODEL_GEMINI, MODEL_LLAMA, MODEL_CONSOLIDATOR

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("LangGraphPipeline")

# Reducer for raw_results dictionary to allow parallel merge
def merge_raw_results(existing: Dict[str, Any], new_value: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(existing or {})
    merged.update(new_value)
    return merged

# Clean model name for node labeling in the graph visualization
def clean_node_name(model_path: str) -> str:
    parts = model_path.split("/")
    name = parts[-1] if len(parts) > 1 else parts[0]
    name = name.split(":")[0]  # Remove version/tag if any
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()
    return clean

claude_node_name = f"research_{clean_node_name(MODEL_CLAUDE)}"
gemini_node_name = f"research_{clean_node_name(MODEL_GEMINI)}"
llama_node_name = f"research_{clean_node_name(MODEL_LLAMA)}"
consolidation_node_name = f"consolidation_{clean_node_name(MODEL_CONSOLIDATOR)}"

class AgentState(TypedDict):
    company_name: str
    dry_run: bool
    raw_results: Annotated[Dict[str, Dict[str, Any]], merge_raw_results]
    consolidated: Dict[str, Any]
    errors: List[Dict[str, Any]]
    attempts: int
    db_status: str
    log: List[str]
    conflicts: Dict[str, Any]
    resolved: Dict[str, Any]
    pre_val_errors: List[Dict[str, Any]]
    pre_healing_consolidated: Dict[str, Any]
    regeneration_log: List[str]

# --- Nodes ---

async def claude_researcher_node(state: AgentState) -> Dict[str, Any]:
    from research_agents import ClaudeResearcher
    print("\n" + "="*60)
    print(f" [Node: {claude_node_name}]")
    print(f" -> Current Company: {state['company_name']}")
    print(f" -> Action: Claude Researcher querying chunked parameters ({MODEL_CLAUDE})...")
    print("="*60)
    
    agent = ClaudeResearcher()
    results = await agent.research_company_async(state["company_name"])
    return {
        "raw_results": {"claude": results},
        "log": state.get("log", []) + [f"Executed {claude_node_name}"]
    }

async def gemini_researcher_node(state: AgentState) -> Dict[str, Any]:
    from research_agents import GeminiResearcher
    print("\n" + "="*60)
    print(f" [Node: {gemini_node_name}]")
    print(f" -> Current Company: {state['company_name']}")
    print(f" -> Action: Gemini Researcher querying chunked parameters ({MODEL_GEMINI})...")
    print("="*60)
    
    agent = GeminiResearcher()
    results = await agent.research_company_async(state["company_name"])
    return {
        "raw_results": {"gemini": results},
        "log": state.get("log", []) + [f"Executed {gemini_node_name}"]
    }

async def llama_researcher_node(state: AgentState) -> Dict[str, Any]:
    from research_agents import LlamaResearcher
    print("\n" + "="*60)
    print(f" [Node: {llama_node_name}]")
    print(f" -> Current Company: {state['company_name']}")
    print(f" -> Action: Llama Researcher querying chunked parameters ({MODEL_LLAMA})...")
    print("="*60)
    
    agent = LlamaResearcher()
    results = await agent.research_company_async(state["company_name"])
    return {
        "raw_results": {"llama": results},
        "log": state.get("log", []) + [f"Executed {llama_node_name}"]
    }

def consolidation_node(state: AgentState) -> Dict[str, Any]:
    import copy
    print("\n" + "="*60)
    print(f" [Node: {consolidation_node_name}]")
    print(" -> Action: Consolidating parallel research datasets...")
    print("="*60)
    
    consolidator = ConsolidationAgent()
    consolidated, conflicts = consolidator.pre_consolidate(state.get("raw_results", {}))
    
    resolved = {}
    print(f"    * Conflicts found: {len(conflicts)}")
    if conflicts:
        resolved = consolidator.resolve_conflicts(state["company_name"], conflicts)
        consolidated.update(resolved)
        
    # Ensure company name is set
    if PipelineValidator.is_empty_or_na(consolidated.get("name")):
        consolidated["name"] = state["company_name"]
        
    pre_healing = copy.deepcopy(consolidated)
        
    return {
        "consolidated": consolidated,
        "conflicts": conflicts,
        "resolved": resolved,
        "pre_healing_consolidated": pre_healing,
        "log": state.get("log", []) + [f"Executed {consolidation_node_name} (resolved {len(conflicts)} conflicts)"]
    }

def validation_check_node(state: AgentState) -> Dict[str, Any]:
    print("\n" + "="*60)
    print(" [Node: validation_check]")
    print(" -> Action: Validating consolidated Golden Record against schemas...")
    print("="*60)
    
    errors = PipelineValidator.validate_company(state.get("consolidated", {}))
    print(f"    * Validation Status: {'PASSED' if not errors else 'FAILED'}")
    print(f"    * Active Errors: {len(errors)}")
    for err in errors:
        print(f"      - Field '{err['field']}': {err['error']} (Value: {err['value']})")
        
    update_dict = {
        "errors": errors,
        "log": state.get("log", []) + [f"Executed validation_check (found {len(errors)} errors)"]
    }
    if state.get("attempts", 0) == 0:
        update_dict["pre_val_errors"] = errors
        
    return update_dict

def regeneration_node(state: AgentState) -> Dict[str, Any]:
    attempts = state.get("attempts", 0) + 1
    print("\n" + "="*60)
    print(f" [Node: regeneration] (Attempt {attempts}/3)")
    print(f" -> Action: Repairing {len(state.get('errors', []))} failed fields via self-healing...")
    print("="*60)
    
    regenerator = RegenerationLoop()
    consolidated = dict(state.get("consolidated", {}))
    
    regen_log = list(state.get("regeneration_log", []))
    msg = f"[Attempt {attempts}/3] Consolidated record has {len(state.get('errors', []))} validation errors."
    regen_log.append(msg)
    
    # Run one round of self-healing for each failed field
    for err in state.get("errors", []):
        field = err["field"]
        curr_val = err["value"]
        err_msg = err["error"]
        
        corrected = regenerator.regenerate_field(state["company_name"], field, curr_val, err_msg)
        consolidated[field] = corrected
        print(f"    * Corrected '{field}': '{curr_val}' -> '{corrected}'")
        regen_log.append(f"  - Regenerated field '{field}': '{curr_val}' -> '{corrected}' (Reason: {err_msg})")
        
    return {
        "consolidated": consolidated,
        "attempts": attempts,
        "regeneration_log": regen_log,
        "log": state.get("log", []) + [f"Executed regeneration attempt {attempts}"]
    }

def supabase_write_node(state: AgentState) -> Dict[str, Any]:
    print("\n" + "="*60)
    print(" [Node: supabase_write]")
    print(" -> Action: Writing validated profile to Supabase...")
    print("="*60)
    
    db_status = "Skipped"
    if not state.get("dry_run", True):
        db_writer = DBWriter()
        success, db_msg = db_writer.write_company(state.get("consolidated", {}))
        db_status = db_msg if success else f"DB Write Failed: {db_msg}"
        print(f"    * Supabase Write: {db_status}")
    else:
        db_status = "Skipped (Dry Run Mode)"
        print("    * Supabase Write: Skipped (Dry Run)")
        
    return {
        "db_status": db_status,
        "log": state.get("log", []) + [f"Executed supabase_write: {db_status}"]
    }

# --- Router ---

def should_regenerate(state: AgentState) -> str:
    if state.get("errors", []) and state.get("attempts", 0) < 3:
        print("\n -> Conditional Edge: State contains validation errors. Routing to 'regeneration'...")
        return "regeneration"
    else:
        print("\n -> Conditional Edge: Validation passed or max attempts reached. Routing to 'supabase_write'...")
        return "supabase_write"

# --- Graph Assembly ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node(claude_node_name, claude_researcher_node)
workflow.add_node(gemini_node_name, gemini_researcher_node)
workflow.add_node(llama_node_name, llama_researcher_node)
workflow.add_node(consolidation_node_name, consolidation_node)
workflow.add_node("validation_check", validation_check_node)
workflow.add_node("regeneration", regeneration_node)
workflow.add_node("supabase_write", supabase_write_node)

# Set Parallel Edges
workflow.add_edge(START, claude_node_name)
workflow.add_edge(START, gemini_node_name)
workflow.add_edge(START, llama_node_name)

# Fork-Join at Consolidation
workflow.add_edge(claude_node_name, consolidation_node_name)
workflow.add_edge(gemini_node_name, consolidation_node_name)
workflow.add_edge(llama_node_name, consolidation_node_name)

# Consolidation to validation
workflow.add_edge(consolidation_node_name, "validation_check")

# Add Conditional Transition
workflow.add_conditional_edges(
    "validation_check",
    should_regenerate,
    {
        "regeneration": "regeneration",
        "supabase_write": "supabase_write"
    }
)

# Complete Loop Back
workflow.add_edge("regeneration", "validation_check")
workflow.add_edge("supabase_write", END)

# Compile Graph
graph = workflow.compile()

# --- Export Visual Graph ---

def export_graph_visualization(output_path: str = "Company_Intelligence_LangGraph.png"):
    print(f"\nExporting graph visualization to: {output_path}...")
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        with open(output_path, "wb") as f:
            f.write(png_data)
        print("Graph visualization successfully exported as PNG!")
    except Exception as e:
        print(f"Could not export PNG visualization: {e}")
        try:
            mermaid_text = graph.get_graph().draw_mermaid()
            text_path = output_path.replace(".png", ".md")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(f"```mermaid\n{mermaid_text}\n```")
            print(f"Saved fallback Mermaid chart syntax to: {text_path}")
        except Exception as ex:
            print(f"Failed to generate text fallback: {ex}")

# --- Save and Print Report ---

def save_and_print_report(state: Dict[str, Any]):
    import json
    import re
    import os
    from schemas import CompanyFull
    
    company_name = state["company_name"]
    dry_run = state.get("dry_run", True)
    raw_results = state.get("raw_results", {})
    consolidated = state.get("consolidated", {})
    errors = state.get("errors", [])
    attempts = state.get("attempts", 0)
    db_status = state.get("db_status", "Skipped")
    conflicts = state.get("conflicts", {})
    resolved = state.get("resolved", {})
    pre_val_errors = state.get("pre_val_errors", [])
    pre_healing_consolidated = state.get("pre_healing_consolidated", {})
    regeneration_log = state.get("regeneration_log", [])

    report_lines = []
    report_lines.append("================================================================================")
    report_lines.append("                       RADIX AGENTIC PIPELINE EXECUTION")
    report_lines.append("================================================================================")
    report_lines.append(f"Target Company: {company_name}")
    report_lines.append("")

    # Step 1: Check Database Connectivity
    db_writer = DBWriter()
    supabase_status = db_writer.connection_status
    report_lines.append("[1] DATABASE CONNECTIVITY STATUS")
    report_lines.append("--------------------------------------------------------------------------------")
    report_lines.append(f"Supabase Status: {supabase_status}")
    report_lines.append("")

    # Step 2: Parallel research by Claude, Gemini, and Llama
    report_lines.append("[2] PARALLEL RESEARCH INPUTS (RAW LLM OUTPUTS)")
    report_lines.append("--------------------------------------------------------------------------------")
    
    # Map researcher names to model IDs for display
    model_mapping = {
        "claude": MODEL_CLAUDE,
        "gemini": MODEL_GEMINI,
        "llama": MODEL_LLAMA
    }

    for researcher_name in ["claude", "gemini", "llama"]:
        researcher_data = raw_results.get(researcher_name, {})
        errors_list = PipelineValidator.validate_company(researcher_data)
        field_count = len(researcher_data)
        na_count = sum(1 for v in researcher_data.values() if PipelineValidator.is_empty_or_na(v))
        completeness = ((field_count - na_count) / field_count * 100) if field_count > 0 else 0
        
        model_id = model_mapping.get(researcher_name, "Unknown Model")
        report_lines.append(f">>> Researcher: {researcher_name.upper()} (Model: {model_id})")
        report_lines.append(f"Completeness: {completeness:.1f}% | Validation Errors: {len(errors_list)}")
        report_lines.append("Raw JSON Output:")
        report_lines.append(json.dumps(researcher_data, indent=2))
        report_lines.append("")

    # Step 3: Consolidation
    report_lines.append("[3] CONSOLIDATION STAGE (GOLDEN RECORD MERGE)")
    report_lines.append("--------------------------------------------------------------------------------")
    report_lines.append(f"Conflicts/Disagreements Found: {len(conflicts)}")
    if conflicts:
        for field, options in conflicts.items():
            report_lines.append(f"- Field '{field}':")
            for model, val in options.items():
                report_lines.append(f"    * {model.capitalize()}: {val}")
        
        report_lines.append("")
        report_lines.append(f"Reconciliation LLM (Model: {MODEL_CONSOLIDATOR}) Output:")
        report_lines.append(json.dumps(resolved, indent=2))
    else:
        report_lines.append("No conflicts found. All researchers agreed or fields were empty.")
        
    report_lines.append("")
    report_lines.append("Consolidated Golden Record (Pre-Validation):")
    report_lines.append(json.dumps(pre_healing_consolidated, indent=2))
    report_lines.append("")

    # Step 4: Validation
    report_lines.append("[4] VALIDATION SUITE RESULTS (CONSOLIDATED RECORD)")
    report_lines.append("--------------------------------------------------------------------------------")
    if pre_val_errors:
        report_lines.append(f"Validation Status: FAILED ({len(pre_val_errors)} errors detected)")
        for err in pre_val_errors:
            report_lines.append(f"  - Field '{err['field']}': {err['error']} (Value: {err['value']})")
    else:
        report_lines.append("Validation Status: PASSED (0 errors detected)")
    report_lines.append("")

    # Step 5: Self-healing regeneration loop
    report_lines.append("[5] SELF-HEALING REGENERATION LOOP")
    report_lines.append("--------------------------------------------------------------------------------")
    if regeneration_log:
        report_lines.extend(regeneration_log)
        if not errors:
            report_lines.append("Validation succeeded! The record is clean and verified.")
        else:
            report_lines.append(f"Validation failed after {attempts} attempts. Remaining errors: {errors}")
    else:
        report_lines.append("No self-healing required. All consolidated fields passed validation.")
    report_lines.append("")

    # Step 6: Database Write / Payload Splits
    report_lines.append("[6] DATABASE WRITE STATUS")
    report_lines.append("--------------------------------------------------------------------------------")
    report_lines.append(f"DB Write Status: {db_status}")
    report_lines.append("")

    # Generate payloads for display
    company_id = consolidated.get("company_id") or (db_writer.get_next_company_id() if db_writer.enabled else 9999)
    short_json = db_writer.build_short_json(consolidated, company_id)
    
    # Build full payload
    full_json = {}
    for key in CompanyFull.model_fields.keys():
        if key == "company_id":
            full_json[key] = company_id
        else:
            full_json[key] = consolidated.get(key, "NA")

    report_lines.append("[7] FINAL GOLDEN RECORD SCHEMAS")
    report_lines.append("--------------------------------------------------------------------------------")
    report_lines.append(">>> SHORT JSON (9 Fields - CompanyShort Schema)")
    report_lines.append(json.dumps(short_json, indent=2))
    report_lines.append("")
    report_lines.append(">>> LONG JSON (163 Fields - CompanyFull Schema)")
    report_lines.append(json.dumps(full_json, indent=2))
    report_lines.append("================================================================================")

    report_text = "\n".join(report_lines)
    
    # Create safe filename from company name
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', company_name).lower()
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, f"{safe_name}_pipeline.log")
    
    # Write to log file
    with open(log_file_path, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    # Print entire report to stdout
    print("\n" + report_text + "\n")
    logger.info(f"Structured pipeline report saved to: {log_file_path}")

# --- Entrypoint wrapper ---

async def run_graph_pipeline(company_name: str, dry_run: bool = False) -> Dict[str, Any]:
    initial_state = {
        "company_name": company_name,
        "dry_run": dry_run,
        "raw_results": {},
        "consolidated": {},
        "errors": [],
        "attempts": 0,
        "db_status": "",
        "log": [],
        "conflicts": {},
        "resolved": {},
        "pre_val_errors": [],
        "pre_healing_consolidated": {},
        "regeneration_log": []
    }
    
    final_state = await graph.ainvoke(initial_state)
    
    # Generate and print/save report
    save_and_print_report(final_state)
    
    return final_state
