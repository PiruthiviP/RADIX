import uuid
import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional

try:
    from supabase import create_client, Client
except ImportError:
    Client = None

from app.config import SupabaseConfig

logger = logging.getLogger(__name__)

class SQLiteStorage:
    """Fallback local database storage when Supabase is disabled."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS provider_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    company_name TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    llm_name TEXT,
                    model_name TEXT,
                    parameters TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consolidated_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT UNIQUE,
                    company_name TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    parameters TEXT,
                    sources TEXT,
                    generation_status TEXT
                )
            """)
            conn.commit()
            conn.close()
            logger.info(f"Initialized local SQLite fallback database at: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite database: {str(e)}")

    def save_provider_output(self, company_id: str, company_name: str, llm_name: str, model_name: str, parameters: Dict[str, Any]) -> None:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO provider_outputs (company_id, company_name, llm_name, model_name, parameters)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, company_name, llm_name, model_name, json.dumps(parameters)))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"SQLite save_provider_output failed: {str(e)}")

    def save_consolidated_profile(self, company_id: str, company_name: str, parameters: Dict[str, Any], sources: Dict[str, Any], status: str) -> None:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO consolidated_profiles (company_id, company_name, parameters, sources, generation_status)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(company_id) DO UPDATE SET
                    company_name = excluded.company_name,
                    parameters = excluded.parameters,
                    sources = excluded.sources,
                    generation_status = excluded.generation_status,
                    timestamp = CURRENT_TIMESTAMP
            """, (company_id, company_name, json.dumps(parameters), json.dumps(sources), status))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"SQLite save_consolidated_profile failed: {str(e)}")


class SupabaseStorageManager:
    def __init__(self, supabase_config: SupabaseConfig, db_path: str):
        self.config = supabase_config
        self.supabase_client: Optional[Client] = None
        self.sqlite_fallback = SQLiteStorage(db_path)
        self._init_supabase()

    def _init_supabase(self) -> None:
        if self.config.enabled:
            try:
                from supabase import create_client
                self.supabase_client = create_client(self.config.url, self.config.key)
                logger.info("Successfully connected to Supabase storage layer.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}. Running with local SQLite fallback.")
                self.supabase_client = None
        else:
            logger.info("Supabase disabled. Running with local SQLite storage.")

    def save_provider_outputs(self, company_name: str, llm_name: str, model_name: str, profile_payload: Dict[str, Any], company_id: Optional[str] = None) -> str:
        """Inserts a row for each LLM provider into database. Returns run UUID (company_id)."""
        run_uuid = company_id or str(uuid.uuid4())
        
        # Save to SQLite fallback
        self.sqlite_fallback.save_provider_output(run_uuid, company_name, llm_name, model_name, profile_payload)

        # Save to Supabase if active
        if self.supabase_client:
            try:
                self.supabase_client.table("provider_outputs").insert({
                    "company_id": run_uuid,
                    "company_name": company_name,
                    "llm_name": llm_name,
                    "model_name": model_name,
                    "parameters": profile_payload
                }).execute()
                logger.info(f"Saved {llm_name} provider outputs to Supabase for {company_name}")
            except Exception as e:
                logger.error(f"Failed to save {llm_name} outputs to Supabase: {str(e)}")
                
        return run_uuid

    def save_consolidated_profile(self, company_id: str, company_name: str, profile_payload: Dict[str, Any], sources: Dict[str, Any], generation_status: str) -> None:
        """Inserts/Updates the consolidated profile."""
        # Save to SQLite fallback
        self.sqlite_fallback.save_consolidated_profile(company_id, company_name, profile_payload, sources, generation_status)

        # Save to Supabase if active
        if self.supabase_client:
            try:
                self.supabase_client.table("consolidated_profiles").insert({
                    "company_id": company_id,
                    "company_name": company_name,
                    "parameters": profile_payload,
                    "sources": sources,
                    "generation_status": generation_status
                }).execute()
                logger.info(f"Saved consolidated profile to Supabase for {company_name} (Status: {generation_status})")
            except Exception as e:
                logger.error(f"Failed to save consolidated profile to Supabase: {str(e)}")
                
    def save_via_transaction(self, company_id: str, company_name: str, generation_status: str, consolidated_profile: Dict[str, Any], sources: Dict[str, Any], provider_data_array: List[Dict[str, Any]]) -> None:
        """Attempts atomic write via stored PL/pgSQL function."""
        # 1. Always save to SQLite individually
        self.sqlite_fallback.save_consolidated_profile(company_id, company_name, consolidated_profile, sources, generation_status)
        for prov in provider_data_array:
            self.sqlite_fallback.save_provider_output(company_id, company_name, prov["llm_name"], prov["model_name"], prov["parameters"])

        # 2. Save via RPC in Supabase
        if self.supabase_client:
            try:
                # Supabase expects json arrays for procedure inputs
                self.supabase_client.rpc("store_company_profile", {
                    "p_company_id": company_id,
                    "p_company_name": company_name,
                    "p_generation_status": generation_status,
                    "p_consolidated_profile": consolidated_profile,
                    "p_sources": sources,
                    "p_provider_data": provider_data_array
                }).execute()
                logger.info(f"Successfully ran store_company_profile transaction in Supabase for {company_name}")
            except Exception as e:
                logger.warning(f"Supabase store_company_profile transaction call failed: {str(e)}. Falling back to individual tables insert.")
                # Fallback to manual inserts
                self.save_consolidated_profile(company_id, company_name, consolidated_profile, sources, generation_status)
                for prov in provider_data_array:
                    self.save_provider_outputs(company_name, prov["llm_name"], prov["model_name"], prov["parameters"], company_id=company_id)
