import logging
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger("DBClient")

class DBClient:
    def __init__(self):
        self.enabled = bool(SUPABASE_URL and SUPABASE_KEY and 
                            SUPABASE_URL != "your_supabase_url_here" and 
                            SUPABASE_KEY != "your_supabase_anon_key_or_service_role_key_here")
        self.client: Client = None
        if self.enabled:
            try:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize Supabase: {e}")
                self.enabled = False

    def fetch_all_companies(self) -> list[dict]:
        """
        Retrieves all companies from the Supabase database. Returns a list of full_json dictionaries.
        """
        if not self.enabled or not self.client:
            logger.warning("Supabase client is not enabled. Returning empty list.")
            return []
            
        try:
            response = self.client.table("companies_json").select("*").execute()
            companies = []
            if response.data:
                for row in response.data:
                    full_json = row.get("full_json", {})
                    # Ensure company_id is present
                    if full_json and "company_id" not in full_json:
                        full_json["company_id"] = row.get("company_id")
                    if full_json:
                        companies.append(full_json)
            logger.info(f"Fetched {len(companies)} companies from Supabase.")
            return companies
        except Exception as e:
            logger.error(f"Failed to fetch companies from Supabase: {e}")
            return []
