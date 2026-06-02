import argparse
import asyncio
import json
import os
import sys
from pipeline import CompanyIntelligencePipeline

def main():
    parser = argparse.ArgumentParser(description="RADIX Company Intelligence Agentic Pipeline")
    parser.add_argument("--company", type=str, required=True, help="Name of the company to research")
    parser.add_argument("--dry-run", action="store_true", help="Performs research, validation, and consolidation without database persistence")
    parser.add_argument("--output", type=str, help="Optional local path to save the final JSON result file")
    
    args = parser.parse_args()
    
    pipeline = CompanyIntelligencePipeline()
    
    # Run pipeline asynchronously
    try:
        final_record, errors, db_status = asyncio.run(
            pipeline.run_pipeline_async(args.company, dry_run=args.dry_run)
        )
        
        # Output summary of errors
        print("\n" + "="*50)
        print("PIPELINE RESULT SUMMARY")
        print("="*50)
        print(f"Target Company: {args.company}")
        print(f"DB Write Status: {db_status}")
        print(f"Validation Errors Remaining: {len(errors)}")
        if errors:
            print("Errors list:")
            for err in errors:
                print(f"  - Field '{err['field']}': {err['error']} (Value: {err['value']})")
        print("="*50 + "\n")
        
        # Save output locally if specified
        if args.output:
            out_dir = os.path.dirname(args.output)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(final_record, f, indent=2, ensure_ascii=False)
            print(f"Successfully saved final verified company profile to: {args.output}")
            
    except KeyboardInterrupt:
        print("\nPipeline execution cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nPipeline failed with exception: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
