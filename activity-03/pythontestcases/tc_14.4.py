import pytest
from typing import Dict, Any

# Map headquarters country keywords to standardized country names
HQ_COUNTRY_MAP = {
    "usa": "United States",
    "united states": "United States",
    "india": "India",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "germany": "Germany"
}


def validate_default_value_logic(record: Dict[str, Any]) -> bool:
    """
    Validates company metadata by ensuring appropriate defaults are applied
    and corrupting, inappropriate defaults are flagged and rejected.
    """
    company_name = record.get("Company Name")
    category = record.get("Category")
    maturity = record.get("Company maturity")
    revenues = record.get("Annual Revenues")
    hq = record.get("Company Headquarters")
    countries = record.get("Countries Operating In")
    offices_count = record.get("Number of Offices (beyond HQ)")

    if not company_name or not category:
        raise ValueError("Field Validation Error: 'Company Name' and 'Category' are required.")

    # 1. Reject Inappropriate Financial Defaults
    # Active commercial scale-ups or mature enterprises cannot have defaulted zero revenues ($0)
    if revenues is not None:
        clean_rev = str(revenues).strip().replace("$", "").replace(",", "")
        
        # Check if revenue is explicitly defaulted to zero
        if clean_rev in ["0", "0.00", "free", "none"]:
            if maturity in ["Scale-up", "Mature"] and category not in ["Non-Profit", "Govt"]:
                raise ValueError(
                    f"Inappropriate Default Detected: Active, mature commercial entity '{company_name}' "
                    f"cannot have its revenue defaulted to zero. Unknown revenue must be represented as Null/None."
                )

    # 2. Execute Context-Dependent Defaults
    # If 'Countries Operating In' is missing, default it to the HQ's country
    if countries is None or str(countries).strip() == "":
        if hq:
            hq_lower = str(hq).lower()
            resolved_country = None
            
            # Extract country from the HQ address string
            for keyword, country_name in HQ_COUNTRY_MAP.items():
                if keyword in hq_lower:
                    resolved_country = country_name
                    break
                    
            if resolved_country:
                record["Countries Operating In"] = resolved_country
            else:
                # Fallback to general classification if country cannot be parsed
                record["Countries Operating In"] = "Unknown"
        else:
            record["Countries Operating In"] = "Unknown"

    # 3. Execute Safe Structural Defaults
    # If additional office counts are missing, default to 0 safely
    if offices_count is None:
        record["Number of Offices (beyond HQ)"] = 0

    return True


# --- Pytest Default Ingestion Suite ---

def test_context_dependent_hq_country_default_success():
    """
    Ensures that a missing operating country field is safely defaulted to
    the country resolved from the headquarters address block.
    """
    record = {
        "Company Name": "Apex SaaS LLC",
        "Category": "Startup",
        "Company maturity": "Startup",
        "Company Headquarters": "San Francisco, USA",
        "Countries Operating In": None,  # Should be defaulted to United States
        "Number of Offices (beyond HQ)": 1
    }
    
    assert validate_default_value_logic(record) is True
    assert record["Countries Operating In"] == "United States"


def test_safe_structural_office_count_default_success():
    """
    Ensures that a missing office count is safely defaulted to 0.
    """
    record = {
        "Company Name": "Apex SaaS LLC",
        "Category": "Startup",
        "Company maturity": "Startup",
        "Company Headquarters": "San Francisco, USA",
        "Countries Operating In": "United States",
        "Number of Offices (beyond HQ)": None  # Should be defaulted to 0
    }
    
    assert validate_default_value_logic(record) is True
    assert record["Number of Offices (beyond HQ)"] == 0


def test_inappropriate_financial_zero_default_fails():
    """
    Asserts that an active, mature commercial company is rejected if its 
    revenue is inappropriately defaulted to zero instead of being marked as None/Null.
    """
    record = {
        "Company Name": "Enterprise Solutions Inc.",
        "Category": "Enterprise",
        "Company maturity": "Mature",
        "Company Headquarters": "London, UK",
        "Annual Revenues": "$0"  # Inappropriate default
    }
    
    with pytest.raises(ValueError, match="Active, mature commercial entity .* cannot have its revenue defaulted to zero"):
        validate_default_value_logic(record)


def test_legitimate_non_profit_zero_revenue_success():
    """
    Ensures that legitimate zero-revenue states for non-profits are accepted 
    and do not trigger inappropriate default validation failures.
    """
    record = {
        "Company Name": "Green Earth Foundation",
        "Category": "Non-Profit",
        "Company maturity": "Mature",
        "Company Headquarters": "Berlin, Germany",
        "Annual Revenues": "$0"  # Allowed for Non-Profits
    }
    assert validate_default_value_logic(record) is True