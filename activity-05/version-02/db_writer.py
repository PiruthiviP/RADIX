import logging
from typing import Dict, Any, Tuple
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from schemas import CompanyShort, CompanyFull

logger = logging.getLogger("DBWriter")

class DBWriter:
    def __init__(self):
        self.enabled = bool(SUPABASE_URL and SUPABASE_KEY and 
                            SUPABASE_URL != "your_supabase_url_here" and 
                            SUPABASE_KEY != "your_supabase_anon_key_or_service_role_key_here")
        self.client: Client = None
        
        self.connection_status = "NOT CONFIGURED (URL/Key missing or placeholder)"
        if self.enabled:
            try:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("Successfully initialized Supabase Client.")
                # Perform a lightweight query to test connection
                self.client.table("companies_json").select("company_id").limit(1).execute()
                self.connection_status = "CONNECTED SUCCESSFULLY!"
                print(f"\n>>> Supabase connection check: {self.connection_status} <<<\n")
                logger.info(f"Supabase connection check: {self.connection_status}")
            except Exception as e:
                self.connection_status = f"FAILED! Error: {e}"
                print(f"\n>>> Supabase connection check: {self.connection_status} <<<\n")
                logger.error(f"Supabase connection check failed: {e}")
                self.enabled = False
        else:
            print(f"\n>>> Supabase connection check: {self.connection_status} <<<\n")
            logger.warning("Supabase URL or Key not configured. Database writes will be skipped.")

    def get_next_company_id(self) -> int:
        """
        Queries companies_json to find the maximum company_id and returns max + 1.
        """
        if not self.enabled or not self.client:
            return 9999 # default high ID for dry runs
            
        try:
            # Query all records to scan max company_id
            response = self.client.table("companies_json").select("company_id").execute()
            if response.data:
                existing_ids = [row.get("company_id") for row in response.data if row.get("company_id") is not None]
                if existing_ids:
                    return max(existing_ids) + 1
            return 1
        except Exception as e:
            logger.error(f"Failed to fetch maximum company_id: {e}. Defaulting to 1.")
            return 1

    def build_short_json(self, consolidated: Dict[str, Any], company_id: int) -> Dict[str, Any]:
        """
        Filters consolidated fields to match the CompanyShort schema structure.
        """
        short_keys = list(CompanyShort.model_fields.keys())
        short_data = {}
        for key in short_keys:
            if key == "company_id":
                short_data[key] = company_id
            else:
                short_data[key] = consolidated.get(key, "NA")
        return short_data

    def write_company(self, consolidated: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Writes the consolidated record into the companies_json table in Supabase.
        Uses upsert logic if the company name already exists in the database.
        """
        company_name = consolidated.get("name", "").strip()
        if not company_name:
            return False, "Error: Company name is empty."

        # Assign ID
        company_id = self.get_next_company_id()
        consolidated["company_id"] = company_id
        
        # Build payloads
        short_payload = self.build_short_json(consolidated, company_id)
        
        # Build full payload ensuring all fields are represented
        full_payload = {}
        for key in CompanyFull.model_fields.keys():
            if key == "company_id":
                full_payload[key] = company_id
            else:
                full_payload[key] = consolidated.get(key, "NA")

        if not self.enabled or not self.client:
            logger.warning(f"Dry run write for company: '{company_name}' with ID: {company_id}")
            return True, f"Dry-run: verified write payload for ID {company_id}"

        try:
            # Check if company already exists by name
            # Since 'name' is in full_json, we can filter by querying:
            # Note: filtering jsonb columns in Supabase is done using -> or ->> path syntax
            response = self.client.table("companies_json").select("*").execute()
            
            existing_row = None
            if response.data:
                for row in response.data:
                    full_json = row.get("full_json", {}) or {}
                    row_name = full_json.get("name", "").strip().lower()
                    if row_name == company_name.lower():
                        existing_row = row
                        break
            
            if existing_row:
                # Update existing row
                db_id = existing_row.get("json_id")
                comp_id = existing_row.get("company_id")
                
                # Maintain original company_id
                short_payload["company_id"] = comp_id
                full_payload["company_id"] = comp_id
                
                update_response = self.client.table("companies_json").update({
                    "short_json": short_payload,
                    "full_json": full_payload
                }).eq("json_id", db_id).execute()
                
                logger.info(f"Successfully updated existing company '{company_name}' (ID: {comp_id}) in Supabase.")
                return True, f"Updated company '{company_name}' in Supabase (json_id: {db_id})."
            else:
                # Insert new row
                insert_response = self.client.table("companies_json").insert({
                    "company_id": company_id,
                    "short_json": short_payload,
                    "full_json": full_payload
                }).execute()
                
                logger.info(f"Successfully inserted new company '{company_name}' (ID: {company_id}) in Supabase.")
                return True, f"Inserted new company '{company_name}' in Supabase (company_id: {company_id})."
                
        except Exception as e:
            logger.error(f"Error writing to Supabase: {e}")
            return False, f"Failed to write to database: {e}"
