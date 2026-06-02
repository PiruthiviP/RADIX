import os
import logging
from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END

# Import components from active directory
from research_agents import run_parallel_research
from validator import PipelineValidator
from consolidation_agent import ConsolidationAgent
from regeneration_loop import RegenerationLoop
from db_writer import DBWriter

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("LangGraphPipeline")

class AgentState(TypedDict):
    company_name: str
    dry_run: bool
    raw_results: Dict[str, Dict[str, Any]]
    consolidated: Dict[str, Any]
    errors: List[Dict[str, Any]]
    attempts: int
    db_status: str
    log: List[str]

# --- Nodes ---

async def research_node(state: AgentState) -> Dict[str, Any]:
    print("\n" + "="*60)
    print(" [Node: research_node]")
    print(f" -> Current Company: {state['company_name']}")
    print(" -> Action: Running parallel researchers (LLM 1, LLM 2, LLM 3)...")
    print("="*60)
    
    results = await run_parallel_research(state["company_name"])
    
    return {
        "raw_results": results,
        "log": state.get("log", []) + ["Executed research_node"]
    }

def consolidation_node(state: AgentState) -> Dict[str, Any]:
    print("\n" + "="*60)
    print(" [Node: consolidation_node]")
    print(" -> Action: Consolidating parallel research datasets...")
    print("="*60)
    
    consolidator = ConsolidationAgent()
    consolidated, conflicts = consolidator.pre_consolidate(state["raw_results"])
    
    print(f"    * Conflicts found: {len(conflicts)}")
    if conflicts:
        resolved = consolidator.resolve_conflicts(state["company_name"], conflicts)
        consolidated.update(resolved)
        
    # Ensure company name is set
    if PipelineValidator.is_empty_or_na(consolidated.get("name")):
        consolidated["name"] = state["company_name"]
        
    return {
        "consolidated": consolidated,
        "log": state.get("log", []) + [f"Executed consolidation_node (resolved {len(conflicts)} conflicts)"]
    }

def validation_check_node(state: AgentState) -> Dict[str, Any]:
    print("\n" + "="*60)
    print(" [Node: validation_check_node]")
    print(" -> Action: Validating consolidated Golden Record against schemas...")
    print("="*60)
    
    errors = PipelineValidator.validate_company(state["consolidated"])
    print(f"    * Validation Status: {'PASSED' if not errors else 'FAILED'}")
    print(f"    * Active Errors: {len(errors)}")
    for err in errors:
        print(f"      - Field '{err['field']}': {err['error']} (Value: {err['value']})")
        
    return {
        "errors": errors,
        "log": state.get("log", []) + [f"Executed validation_check_node (found {len(errors)} errors)"]
    }

def regeneration_node(state: AgentState) -> Dict[str, Any]:
    attempts = state.get("attempts", 0) + 1
    print("\n" + "="*60)
    print(f" [Node: regeneration_node] (Attempt {attempts}/3)")
    print(f" -> Action: Repairing {len(state['errors'])} failed fields via self-healing...")
    print("="*60)
    
    regenerator = RegenerationLoop()
    consolidated = dict(state["consolidated"])
    
    # Run one round of self-healing for each failed field
    for err in state["errors"]:
        field = err["field"]
        curr_val = err["value"]
        err_msg = err["error"]
        
        corrected = regenerator.regenerate_field(state["company_name"], field, curr_val, err_msg)
        consolidated[field] = corrected
        print(f"    * Corrected '{field}': '{curr_val}' -> '{corrected}'")
        
    return {
        "consolidated": consolidated,
        "attempts": attempts,
        "log": state.get("log", []) + [f"Executed regeneration_node attempt {attempts}"]
    }

def supabase_write_node(state: AgentState) -> Dict[str, Any]:
    print("\n" + "="*60)
    print(" [Node: supabase_write_node]")
    print(" -> Action: Writing validated profile to Supabase...")
    print("="*60)
    
    db_status = "Skipped"
    if not state["dry_run"]:
        db_writer = DBWriter()
        success, db_msg = db_writer.write_company(state["consolidated"])
        db_status = db_msg if success else f"DB Write Failed: {db_msg}"
        print(f"    * Supabase Write: {db_status}")
    else:
        db_status = "Skipped (Dry Run Mode)"
        print("    * Supabase Write: Skipped (Dry Run)")
        
    return {
        "db_status": db_status,
        "log": state.get("log", []) + [f"Executed supabase_write_node: {db_status}"]
    }

# --- Router ---

def should_regenerate(state: AgentState) -> str:
    if state["errors"] and state["attempts"] < 3:
        print("\n -> Conditional Edge: State contains validation errors. Routing to 'regeneration_node'...")
        return "regeneration"
    else:
        print("\n -> Conditional Edge: Validation passed or max attempts reached. Routing to 'supabase_write_node'...")
        return "supabase_write"

# --- Graph Assembly ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("research", research_node)
workflow.add_node("consolidation", consolidation_node)
workflow.add_node("validation_check", validation_check_node)
workflow.add_node("regeneration", regeneration_node)
workflow.add_node("supabase_write", supabase_write_node)

# Set Edges
workflow.set_entry_point("research")
workflow.add_edge("research", "consolidation")
workflow.add_edge("consolidation", "validation_check")

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
        "log": []
    }
    
    final_state = await graph.ainvoke(initial_state)
    return final_state
