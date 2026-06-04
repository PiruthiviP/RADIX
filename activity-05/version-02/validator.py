import re
import datetime
from typing import List, Dict, Any, Tuple
from schemas import CompanyFull

class PipelineValidator:
    @staticmethod
    def is_empty_or_na(val: Any) -> bool:
        if val is None:
            return True
        val_str = str(val).strip().upper()
        return val_str in ("", "NA", "N/A", "NONE", "NOT AVAILABLE", "NULL")

    @classmethod
    def validate_company(cls, company_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        errors = []
        current_year = datetime.datetime.now().year
        
        # Helper to report error
        def add_error(field: str, value: Any, msg: str):
            errors.append({
                "field": field,
                "value": value,
                "error": msg
            })

        for key, val in company_data.items():
            # Skip fields not in schema
            if key not in CompanyFull.model_fields:
                continue

            field_info = CompanyFull.model_fields[key]
            
            # Check nullability rules
            # We can check specific critical fields that should not be empty:
            critical_non_nullable = ["name", "logo_url", "category", "nature_of_company", "headquarters_address", 
                                     "employee_size", "website_url", "ceo_name", "primary_contact_email"]
            
            if key in critical_non_nullable and cls.is_empty_or_na(val):
                add_error(key, val, f"Field '{key}' is required but is empty or 'NA'.")
                continue

            # If the value is empty/NA and allowed to be null, we skip further format validations
            if cls.is_empty_or_na(val):
                continue

            # Check Specific Field Rules based on metadata:
            
            # 1. Year of Incorporation
            if key == "incorporation_year":
                try:
                    year = int(float(val))
                    if not (1800 <= year <= current_year):
                        add_error(key, val, f"Year must be between 1800 and {current_year}.")
                except (ValueError, TypeError):
                    add_error(key, val, "Year of incorporation must be a valid integer.")

            # 2. URLs (logo_url, website_url, linkedin_url, facebook_url, twitter_handle, instagram_url, ceo_linkedin_url, marketing_video_url)
            elif key in ["logo_url", "website_url", "linkedin_url", "facebook_url", "instagram_url", "ceo_linkedin_url"]:
                url_pattern = re.compile(
                    r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
                )
                if not url_pattern.match(str(val)):
                    add_error(key, val, f"Invalid URL format.")

            # 3. Emails (primary_contact_email, contact_person_email)
            elif key in ["primary_contact_email", "contact_person_email"]:
                email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                if not email_pattern.match(str(val)):
                    add_error(key, val, "Invalid email address format.")

            # 4. Phone Numbers (primary_phone_number, contact_person_phone)
            elif key in ["primary_phone_number", "contact_person_phone"]:
                # Relaxed regex for phone numbers to allow spaces, hyphens, parentheses, and leading plus
                phone_pattern = re.compile(r'^\+?[\d\s\-\(\).]{7,25}$')
                if not phone_pattern.match(str(val)):
                    add_error(key, val, "Invalid phone number format.")

            # 5. Ratings (glassdoor_rating, indeed_rating, google_rating)
            elif key in ["glassdoor_rating", "indeed_rating", "google_rating"]:
                try:
                    rating = float(val)
                    # Note: in company_full sample, ratings were represented as datetime-like large numbers due to formatting bugs
                    # If rating is extremely large, we treat it as an error to trigger correction.
                    if not (1.0 <= rating <= 5.0):
                        add_error(key, val, "Rating must be a float between 1.0 and 5.0.")
                except (ValueError, TypeError):
                    add_error(key, val, "Rating must be a valid numeric value.")

            # 6. Website Rating
            elif key == "website_rating":
                try:
                    # Allow 'NA' as a string, but if populated, must be between 1.0 and 10.0
                    rating = float(val)
                    if not (0.0 <= rating <= 10.0):
                        add_error(key, val, "Website rating must be between 0.0 and 10.0.")
                except (ValueError, TypeError):
                    # If it's a string like '7/10' or '8.5/10', try parsing the numerator
                    match = re.match(r'^([\d\.]+)/10$', str(val))
                    if match:
                        try:
                            rating = float(match.group(1))
                            if not (0.0 <= rating <= 10.0):
                                add_error(key, val, "Website rating numerator must be between 0.0 and 10.0.")
                        except ValueError:
                            add_error(key, val, "Invalid format for website rating.")
                    else:
                        add_error(key, val, "Website rating must be a numeric value.")

            # 7. Net Promoter Score (NPS)
            elif key == "net_promoter_score":
                try:
                    nps = int(float(val))
                    if not (-100 <= nps <= 100):
                        add_error(key, val, "NPS must be an integer between -100 and 100.")
                except (ValueError, TypeError):
                    add_error(key, val, "NPS must be a valid integer.")

            # 8. YoY Growth Rate
            elif key == "yoy_growth_rate":
                # Growth rate can be float (0.03) or string ('3%')
                try:
                    rate = float(val)
                    if not (-1.0 <= rate <= 10.0): # between -100% and +1000%
                        add_error(key, val, "YoY Growth rate float must be between -1.0 and 10.0.")
                except (ValueError, TypeError):
                    # Check if it has a % sign
                    match = re.match(r'^([+-]?\d+(?:\.\d+)?)\s*%$', str(val).strip())
                    if not match:
                        add_error(key, val, "YoY growth rate must be a float or a percentage (e.g. 15%).")

            # 9. Numeric counts (employee_size, office_count, valuation, annual_revenue, annual_profit, etc. can be text or number)
            # We don't strictly enforce int for valuation since they can have suffixes like "$220B", which are valid strings.

        return errors
