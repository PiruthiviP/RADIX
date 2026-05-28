import pytest
from typing import Dict, Any

# Current Year context for temporal comparisons
CURRENT_YEAR = 2026


def validate_ambiguous_availability(record: Dict[str, Any]) -> bool:
    """
    Validates company metadata by dynamically evaluating the source of 
    missing data. Normalizes generic null values into context-rich 
    ambiguity classifications depending on the company lifecycle.
    """
    company_name = record.get("Company Name")
    year_founded = record.get("Year of Incorporation")
    retention_tenure = record.get("Average Retention Tenure")
    layoff_history = record.get("Layoff history")
    website_url = record.get("Website URL")
    glassdoor_rating = record.get("Glassdoor Rating")
    confidence_level = record.get("confidence_level")
    validation_mode = record.get("validation_mode", "Automated")

    if not company_name:
         raise ValueError("Field Validation Error: 'Company Name' is required.")

    # 1. Temporal Ambiguity Rule (Data Not Yet Generated)
    # If the company was founded very recently (current or previous year),
    # historical parameters like Employee Retention or Layoff histories are physically non-existent.
    if year_founded and (CURRENT_YEAR - int(year_founded)) <= 1:
        if retention_tenure is None or retention_tenure == "":
            record["Average Retention Tenure"] = "N/A - New Company"
        if layoff_history is None or layoff_history == "":
            record["Layoff history"] = "None - New Company"

    # 2. Stealth/Confidential Ambiguity Rule (Exists but Not Public)
    # If a company is in stealth, digital footprints (Glassdoor, Website traffic, etc.) 
    # are hidden. We normalize empty values to 'N/A - Stealth' and enforce a Low confidence level.
    is_stealth = False
    if website_url and "stealth" in str(website_url).lower():
        is_stealth = True
    elif "stealth" in str(company_name).lower():
        is_stealth = True

    if is_stealth:
        if glassdoor_rating is None or glassdoor_rating == "":
            record["Glassdoor Rating"] = "N/A - Stealth Mode"
        
        # Enforce that a stealth profile must have its reliability/confidence level restricted
        if confidence_level == "High":
            raise ValueError(
                f"Confidence Conflict: Stealth entity '{company_name}' cannot have "
                f"a 'High' confidence level due to unresolvable, non-public data fields."
            )

    # 3. Decommissioned/Deactivated Assets Rule (Previously Existed)
    # If a URL is flagged as offline/deactivated (simulated here via a mock status flag),
    # we enforce that the validation_mode shifts to Supervised or Manual to avoid silent ingestion failure.
    is_url_deactivated = record.get("is_url_deactivated", False)
    if is_url_deactivated:
        if validation_mode == "Automated":
            raise ValueError(
                f"Processing Exception: Deactivated assets detected for '{company_name}'. "
                f"Validation mode must be shifted to 'Supervised' or 'Manual' for human auditing."
            )

    return True


# --- Pytest Suite ---

def test_newly_founded_company_ambiguity_handled():
    """
    Ensures that a company founded in 2025/2026 successfully maps missing historical 
    parameters to 'N/A - New Company' instead of triggering a validation crash.
    """
    new_company = {
        "Company Name": "NeuraLaunch",
        "Year of Incorporation": 2025,
        "Average Retention Tenure": None,  # Ambiguous: Does not exist yet
        "Layoff history": None,            # Ambiguous: Does not exist yet
        "confidence_level": "High"
    }
    
    assert validate_ambiguous_availability(new_company) is True
    assert new_company["Average Retention Tenure"] == "N/A - New Company"
    assert new_company["Layoff history"] == "None - New Company"


def test_stealth_company_ambiguity_handled():
    """
    Ensures stealth profiles are permitted to have missing digital parameters, 
    verifying that the reliability/confidence rating is constrained to 'Low' or 'Medium'.
    """
    stealth_company = {
        "Company Name": "Stealth Crypto Labs",
        "Website URL": "N/A - Stealth Mode",
        "Glassdoor Rating": None,          # Exists privately but not public
        "confidence_level": "Medium"
    }
    
    assert validate_ambiguous_availability(stealth_company) is True
    assert stealth_company["Glassdoor Rating"] == "N/A - Stealth Mode"


def test_stealth_company_invalid_high_confidence_fails():
    """
    Asserts that a stealth-mode profile cannot claim a 'High' data confidence level,
    as several parameters are unresolvable.
    """
    stealth_company = {
        "Company Name": "Stealth Crypto Labs",
        "Website URL": "N/A - Stealth Mode",
        "Glassdoor Rating": None,
        "confidence_level": "High"  # Conflict: High confidence is incompatible with stealth
    }
    with pytest.raises(ValueError, match="cannot have a 'High' confidence level"):
        validate_ambiguous_availability(stealth_company)


def test_deactivated_url_demands_manual_validation_fails():
    """
    Asserts that if a company's target URL is deactivated, automated 
    ingestion fails, demanding human-in-the-loop (Manual) validation.
    """
    deactivated_record = {
        "Company Name": "Retired Brand Inc.",
        "Website URL": "https://www.oldbrand.com",
        "is_url_deactivated": True,  # Simulated deactivated asset
        "validation_mode": "Automated"  # Attempting unsafe automated run
    }
    with pytest.raises(ValueError, match="Validation mode must be shifted to 'Supervised' or 'Manual'"):
        validate_ambiguous_availability(deactivated_record)


def test_deactivated_url_supervised_run_success():
    """
    Ensures that deactivated assets pass checks safely if the validation mode is
    correctly configured for manual or supervised auditing.
    """
    deactivated_record = {
        "Company Name": "Retired Brand Inc.",
        "Website URL": "https://www.oldbrand.com",
        "is_url_deactivated": True,
        "validation_mode": "Manual"  # Correctly configured
    }
    assert validate_ambiguous_availability(deactivated_record) is True