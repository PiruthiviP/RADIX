import time
import uuid
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.config import AppConfig, LangSmithConfig, ModelConfig, SupabaseConfig, validate_provider_config
from app.schemas import (
    CompanyIntelligenceRequest,
    CompanyIntelligenceResponse,
    ProviderDatasetStatus,
    AgentRunStatus,
    AgentStatusResponse
)
from app.intelligence_schema import SchemaManager
from app.metadata_rules import MetadataRulesManager
from app.validation import ValidationEngine
from app.providers import ProviderFactory
from app.supabase_storage import SupabaseStorageManager
from app.graph import build_workflow_graph

logger = logging.getLogger(__name__)

class WorkflowService:
    def __init__(self):
        # 1. Load configuration
        self.app_config = AppConfig()
        self.langsmith_config = LangSmithConfig()
        self.model_config = ModelConfig()
        self.supabase_config = SupabaseConfig()

        # 2. Apply LangSmith settings
        self.langsmith_config.apply()

        # 3. Validate model config
        if not validate_provider_config(self.model_config):
            logger.error("No valid provider keys set. Please set GEMINI_API_KEY, GROQ_API_KEY, or OPENROUTER_API_KEY.")

        # 4. Initialize core components
        self.schema_manager = SchemaManager()
        self.rules_manager = MetadataRulesManager(self.app_config.metadata_path)
        self.validation_engine = ValidationEngine(self.rules_manager, self.schema_manager)
        
        # Initialize providers
        self.active_providers = ProviderFactory.create_providers(self.model_config)
        logger.info(f"Initialized providers: {list(self.active_providers.keys())}")

        # Initialize storage
        self.storage_manager = SupabaseStorageManager(self.supabase_config, self.app_config.db_path)

        # 5. Compile graph
        self.graph = build_workflow_graph(
            self.active_providers,
            self.validation_engine,
            self.schema_manager
        )

        # 6. Initialize stats and registry
        self.startup_time = datetime.utcnow()
        self._lock = threading.Lock()
        self.active_runs: Dict[str, AgentRunStatus] = {}
        self.history_runs: List[AgentRunStatus] = []
        self.total_runs_count = 0
        self.success_runs_count = 0
        self.failed_runs_count = 0
        self.last_run: Optional[AgentRunStatus] = None

    def get_health_status(self) -> Dict[str, Any]:
        """Exposes health status check of active provider LLMs."""
        available = list(self.active_providers.keys())
        status = "OK" if available else "DEGRADED"
        return {
            "status": status,
            "providers_available": available
        }

    def get_global_status(self) -> AgentStatusResponse:
        """Returns aggregated dashboard statistics."""
        with self._lock:
            uptime = (datetime.utcnow() - self.startup_time).total_seconds()
            
            # Refresh elapsed time for currently active runs
            current_active = []
            for run in self.active_runs.values():
                started_dt = datetime.fromisoformat(run.started_at)
                elapsed = (datetime.utcnow() - started_dt).total_seconds()
                run.elapsed_seconds = round(elapsed, 2)
                current_active.append(run)

            return AgentStatusResponse(
                service_status="HEALTHY" if self.active_providers else "UNCONFIGURED",
                service_started_at=self.startup_time.isoformat() + "Z",
                uptime_seconds=round(uptime, 2),
                active_runs=len(self.active_runs),
                total_runs=self.total_runs_count,
                success_runs=self.success_runs_count,
                failed_runs=self.failed_runs_count,
                current_runs=current_active,
                last_run=self.last_run
            )

    def get_run_status(self, run_id: str) -> Optional[AgentRunStatus]:
        with self._lock:
            run = self.active_runs.get(run_id)
            if run:
                started_dt = datetime.fromisoformat(run.started_at)
                run.elapsed_seconds = round((datetime.utcnow() - started_dt).total_seconds(), 2)
                return run
            
            # Check history
            for run in self.history_runs:
                if run.run_id == run_id:
                    return run
            return None

    def _add_active_run(self, run_id: str, company_name: str) -> AgentRunStatus:
        with self._lock:
            self.total_runs_count += 1
            run_status = AgentRunStatus(
                run_id=run_id,
                company_name=company_name,
                stage="initialized",
                progress_percent=0.0,
                started_at=datetime.utcnow().isoformat(),
                elapsed_seconds=0.0,
                generation_status="IN_PROGRESS"
            )
            self.active_runs[run_id] = run_status
            return run_status

    def _update_run_progress(self, run_id: str, stage: str, progress: float) -> None:
        with self._lock:
            run = self.active_runs.get(run_id)
            if run:
                run.stage = stage
                run.progress_percent = progress
                started_dt = datetime.fromisoformat(run.started_at)
                run.elapsed_seconds = round((datetime.utcnow() - started_dt).total_seconds(), 2)

    def _complete_run(self, run_id: str, status: str, error_msg: Optional[str] = None) -> None:
        with self._lock:
            run = self.active_runs.pop(run_id, None)
            if run:
                run.completed_at = datetime.utcnow().isoformat()
                started_dt = datetime.fromisoformat(run.started_at)
                completed_dt = datetime.fromisoformat(run.completed_at)
                duration = (completed_dt - started_dt).total_seconds()
                run.elapsed_seconds = round(duration, 2)
                run.duration_ms = int(duration * 1000)
                run.generation_status = status
                run.stage = "completed"
                run.progress_percent = 100.0
                
                if error_msg:
                    run.error = error_msg
                    self.failed_runs_count += 1
                else:
                    self.success_runs_count += 1

                # Cap history at 200 items
                if len(self.history_runs) >= 200:
                    self.history_runs.pop(0)
                self.history_runs.append(run)
                self.last_run = run

    async def execute_workflow(self, request: CompanyIntelligenceRequest) -> CompanyIntelligenceResponse:
        """Executes the extraction graph, monitors progress, and persists results."""
        run_id = str(uuid.uuid4())
        admin_data = request.admin_payload()
        company_name = admin_data.get("companyName") or "Unknown"
        
        # Start tracking run
        self._add_active_run(run_id, company_name)
        
        # Progress callback linked to state machine updates
        def callback(stage: str, progress: float):
            self._update_run_progress(run_id, stage, progress)

        initial_state = {
            "admin_data": admin_data,
            "temperature": request.temperature,
            "max_retry_rounds": request.maxRetryRounds,
            "strict_grounding_regeneration": request.strictGroundingRegeneration,
            "progress_callback": callback
        }

        try:
            logger.info(f"Triggering intelligence workflow for company: {company_name} (Run ID: {run_id})")
            
            # Execute StateGraph
            result_state = await self.graph.ainvoke(initial_state)
            
            # Extract final metrics
            final_profile = result_state.get("final_profile", {})
            consolidated_sources = result_state.get("consolidated_sources", {})
            provider_datasets = result_state.get("provider_datasets", {})
            provider_stats_raw = result_state.get("provider_stats", {})
            
            # Save results into storage via Plpgsql store transaction
            provider_data_array = []
            for p_name, dataset in provider_datasets.items():
                p_adapter = self.active_providers.get(p_name)
                model_name = p_adapter.model_name if p_adapter else "unknown"
                provider_data_array.append({
                    "llm_name": p_name,
                    "model_name": model_name,
                    "parameters": dataset
                })

            # Save atomic transaction
            self.storage_manager.save_via_transaction(
                company_id=run_id,
                company_name=company_name,
                generation_status="SUCCESS",
                consolidated_profile=final_profile,
                sources=consolidated_sources,
                provider_data_array=provider_data_array
            )

            # Map return stats
            response_provider_stats = {}
            for p_name, p_stat in provider_stats_raw.items():
                response_provider_stats[p_name] = ProviderDatasetStatus(
                    accepted_fields=p_stat["accepted_fields"],
                    failed_fields=p_stat["failed_fields"],
                    retries_used=p_stat["retries_used"],
                    status_message=p_stat["status_message"]
                )

            # Complete active run
            self._complete_run(run_id, "SUCCESS")

            admin_count, gen_count, total_count = self.schema_manager.totals()
            grounded_count = sum(1 for spec in self.schema_manager.fields.values() if spec.is_admin_grounded and final_profile.get(spec.name) != "NA")
            
            return CompanyIntelligenceResponse(
                company_id=run_id,
                company_name=company_name,
                generation_timestamp=datetime.utcnow().isoformat() + "Z",
                generation_status="SUCCESS",
                total_fields=total_count,
                grounded_fields=grounded_count,
                generated_fields=gen_count,
                profile_json=final_profile,
                provider_stats=response_provider_stats
            )

        except Exception as e:
            logger.error(f"Workflow execution failed for {company_name}: {str(e)}", exc_info=True)
            
            # Mark run as failed
            self._complete_run(run_id, "FAILED", error_msg=str(e))
            
            # Save failed profile log in database
            self.storage_manager.save_consolidated_profile(
                company_id=run_id,
                company_name=company_name,
                profile_payload={},
                sources={},
                generation_status="FAILED"
            )
            
            return CompanyIntelligenceResponse(
                company_id=run_id,
                company_name=company_name,
                generation_timestamp=datetime.utcnow().isoformat() + "Z",
                generation_status="FAILED",
                total_fields=165,
                grounded_fields=0,
                generated_fields=152,
                profile_json={},
                provider_stats={}
            )
