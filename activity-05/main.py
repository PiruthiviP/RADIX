import argparse
import asyncio
import json
import os
import sys
from config import validate_config, LANGCHAIN_TRACING_V2, LANGCHAIN_PROJECT
from graph_pipeline import run_graph_pipeline, export_graph_visualization

def main():
    parser = argparse.ArgumentParser(description="RADIX LangGraph Company Intelligence Pipeline")
    parser.add_argument("--company", type=str, required=True, help="Name of the company to research")
    parser.add_argument("--dry-run", action="store_true", help="Performs research, validation, and consolidation without database persistence")
    parser.add_argument("--output", type=str, help="Optional local path to save the final JSON result file")
    
    args = parser.parse_args()
    
    # Check config validity
    is_valid, config_errors = validate_config()
    if not is_valid:
        print(f"Configuration warnings detected: {config_errors}", file=sys.stderr)
        if not args.dry_run:
            print("ERROR: Cannot execute database write with invalid configurations. Exiting.", file=sys.stderr)
            sys.exit(1)

    print("\n" + "="*80)
    print("                RADIX LANGGRAPH PIPELINE RUNNER")
    print("="*80)
    print(f"Target Company: {args.company}")
    print(f"Mode: {'Dry Run' if args.dry_run else 'Production'}")
    print(f"LangSmith Tracing: {'ACTIVE (Project: ' + LANGCHAIN_PROJECT + ')' if LANGCHAIN_TRACING_V2 else 'DISABLED (Set LANGCHAIN_API_KEY to enable)'}")
    print("="*80 + "\n")

    # Run the graph pipeline
    try:
        final_state = asyncio.run(
            run_graph_pipeline(args.company, dry_run=args.dry_run)
        )
        
        # Save output JSON file locally if specified
        if args.output:
            out_dir = os.path.dirname(args.output)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(final_state["consolidated"], f, indent=2, ensure_ascii=False)
            print(f"\nSuccessfully saved final golden record to: {args.output}")

        # Print Execution Report Summary
        print("\n" + "="*80)
        print("                        RUN EXECUTION SUMMARY")
        print("="*80)
        print(f"Target Company: {args.company}")
        print(f"Total Self-Healing Attempts: {final_state['attempts']}")
        print(f"Supabase DB Write Status: {final_state['db_status']}")
        print(f"Remaining Validation Errors: {len(final_state['errors'])}")
        
        if final_state["errors"]:
            print("\nValidation Errors Detail:")
            for err in final_state["errors"]:
                print(f"  - Field '{err['field']}': {err['error']} (Value: {err['value']})")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        print("\nGraph execution cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nGraph execution failed with exception: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Export visual graph chart
        export_graph_visualization("Company_Intelligence_LangGraph.png")

if __name__ == "__main__":
    main()
