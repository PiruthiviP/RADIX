import asyncio
import logging
import json
from typing import Dict, Any, Tuple, List
from config import validate_config
from research_agents import run_parallel_research
from validator import PipelineValidator
from consolidation_agent import ConsolidationAgent
from regeneration_loop import RegenerationLoop
from db_writer import DBWriter

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("CompanyIntelligencePipeline")

class CompanyIntelligencePipeline:
    def __init__(self):
        self.consolidator = ConsolidationAgent()
        self.regenerator = RegenerationLoop()
        self.db_writer = DBWriter()

    async def run_pipeline_async(self, company_name: str, dry_run: bool = False) -> Tuple[Dict[str, Any], List[Dict[str, Any]], str]:
        """
        Executes the entire company research, validation, consolidation, and persistence flow.
        """
        import os
        import re
        import json
        from config import (
            MODEL_CLAUDE,
            MODEL_GEMINI,
            MODEL_LLAMA,
            MODEL_CONSOLIDATOR
        )
        from schemas import CompanyFull

        report_lines = []
        report_lines.append("================================================================================")
        report_lines.append("                       RADIX AGENTIC PIPELINE EXECUTION")
        report_lines.append("================================================================================")
        report_lines.append(f"Target Company: {company_name}")
        report_lines.append("")

        # Step 1: Check Database Connectivity
        supabase_status = self.db_writer.connection_status if hasattr(self.db_writer, 'connection_status') else "NOT CHECKED"
        report_lines.append("[1] DATABASE CONNECTIVITY STATUS")
        report_lines.append("--------------------------------------------------------------------------------")
        report_lines.append(f"Supabase Status: {supabase_status}")
        report_lines.append("")

        is_valid, config_errors = validate_config()
        if not is_valid:
            logger.warning(f"Configuration warnings detected: {config_errors}")
            if not dry_run:
                err_msg = f"Configuration error: {config_errors}"
                report_lines.append(f"ERROR: {err_msg}")
                self._save_and_print_report(company_name, report_lines)
                return {}, [], err_msg

        # Step 2: Parallel research by Claude, Gemini, and Llama
        report_lines.append("[2] PARALLEL RESEARCH INPUTS (RAW LLM OUTPUTS)")
        report_lines.append("--------------------------------------------------------------------------------")
        
        raw_results = await run_parallel_research(company_name)
        
        # Map researcher names to model IDs for display
        model_mapping = {
            "claude": MODEL_CLAUDE,
            "gemini": MODEL_GEMINI,
            "llama": MODEL_LLAMA
        }

        for researcher_name, researcher_data in raw_results.items():
            errors = PipelineValidator.validate_company(researcher_data)
            field_count = len(researcher_data)
            na_count = sum(1 for v in researcher_data.values() if PipelineValidator.is_empty_or_na(v))
            completeness = ((field_count - na_count) / field_count * 100) if field_count > 0 else 0
            
            model_id = model_mapping.get(researcher_name, "Unknown Model")
            report_lines.append(f">>> Researcher: {researcher_name.upper()} (Model: {model_id})")
            report_lines.append(f"Completeness: {completeness:.1f}% | Validation Errors: {len(errors)}")
            report_lines.append("Raw JSON Output:")
            report_lines.append(json.dumps(researcher_data, indent=2))
            report_lines.append("")

        # Step 3: Consolidation (Field-by-field merge and conflict resolution)
        report_lines.append("[3] CONSOLIDATION STAGE (GOLDEN RECORD MERGE)")
        report_lines.append("--------------------------------------------------------------------------------")
        
        consolidated, conflicts = self.consolidator.pre_consolidate(raw_results)
        
        report_lines.append(f"Conflicts/Disagreements Found: {len(conflicts)}")
        if conflicts:
            for field, options in conflicts.items():
                report_lines.append(f"- Field '{field}':")
                for model, val in options.items():
                    report_lines.append(f"    * {model.capitalize()}: {val}")
            
            report_lines.append("")
            report_lines.append(f"Reconciliation LLM (Model: {MODEL_CONSOLIDATOR}) Output:")
            resolved = self.consolidator.resolve_conflicts(company_name, conflicts)
            report_lines.append(json.dumps(resolved, indent=2))
            consolidated.update(resolved)
        else:
            report_lines.append("No conflicts found. All researchers agreed or fields were empty.")
            
        # Ensure company name is set correctly
        if PipelineValidator.is_empty_or_na(consolidated.get("name")):
            consolidated["name"] = company_name

        report_lines.append("")
        report_lines.append("Consolidated Golden Record (Pre-Validation):")
        report_lines.append(json.dumps(consolidated, indent=2))
        report_lines.append("")

        # Step 4: Validation
        pre_val_errors = PipelineValidator.validate_company(consolidated)
        report_lines.append("[4] VALIDATION SUITE RESULTS (CONSOLIDATED RECORD)")
        report_lines.append("--------------------------------------------------------------------------------")
        if pre_val_errors:
            report_lines.append(f"Validation Status: FAILED ({len(pre_val_errors)} errors detected)")
            for err in pre_val_errors:
                report_lines.append(f"  - Field '{err['field']}': {err['error']} (Value: {err['value']})")
        else:
            report_lines.append("Validation Status: PASSED (0 errors detected)")
        report_lines.append("")

        # Step 5: Self-healing regeneration loop for fields failing validation
        report_lines.append("[5] SELF-HEALING REGENERATION LOOP")
        report_lines.append("--------------------------------------------------------------------------------")
        
        regeneration_log = []
        final_record, validation_errors = self.regenerator.run_loop(company_name, consolidated, max_attempts=3, steps_log=regeneration_log)
        
        if regeneration_log:
            report_lines.extend(regeneration_log)
        else:
            report_lines.append("No self-healing required. All consolidated fields passed validation.")
        report_lines.append("")

        # Step 6: Database Write / Payload Splits
        db_status = "Skipped"
        if not dry_run:
            success, db_msg = self.db_writer.write_company(final_record)
            db_status = db_msg if success else f"DB Write Failed: {db_msg}"
        else:
            db_status = "Skipped (Dry Run Mode)"

        report_lines.append("[6] DATABASE WRITE STATUS")
        report_lines.append("--------------------------------------------------------------------------------")
        report_lines.append(f"DB Write Status: {db_status}")
        report_lines.append("")

        # Generate payloads for display
        company_id = final_record.get("company_id") or (self.db_writer.get_next_company_id() if self.db_writer.enabled else 9999)
        short_json = self.db_writer.build_short_json(final_record, company_id)
        
        # Build full payload
        full_json = {}
        for key in CompanyFull.model_fields.keys():
            if key == "company_id":
                full_json[key] = company_id
            else:
                full_json[key] = final_record.get(key, "NA")

        report_lines.append("[7] FINAL GOLDEN RECORD SCHEMAS")
        report_lines.append("--------------------------------------------------------------------------------")
        report_lines.append(">>> SHORT JSON (9 Fields - CompanyShort Schema)")
        report_lines.append(json.dumps(short_json, indent=2))
        report_lines.append("")
        report_lines.append(">>> LONG JSON (163 Fields - CompanyFull Schema)")
        report_lines.append(json.dumps(full_json, indent=2))
        report_lines.append("================================================================================")

        # Save to log file and print
        self._save_and_print_report(company_name, report_lines)

        return final_record, validation_errors, db_status

    def _save_and_print_report(self, company_name: str, report_lines: List[str]):
        import os
        import re
        
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
