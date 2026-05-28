import pytest
from typing import Dict, Any, List

# List of critical mandatory parameters based on schema nullability rules
MANDATORY_FIELDS = [
    "Company Name", 
    "Category", 
    "Year of Incorporation", 
    "Overview of the Company", 
    "Nature of Company", 
    "Company Headquarters", 
    "Employee Size"
]

# Standard string representations of null/empty values to catch and normalize
STRING_NULL_PLACEHOLDERS = {"n/a", "na", "null", "none", "unknown", "undisclosed", ""}


def validate_nullable_data_integrity(record: Dict[str, Any]) -> bool:
    """
    Evaluates the record for nullability and NA data rules. 
    Enforces strict exceptions on missing mandatory parameters while allowing 
    flexible, graceful mapping on optional parameters.
    """
    # 1. Check all mandatory parameters
    for field in MANDATORY_FIELDS:
        val = record.get(field)
        
        # Check for python None
        if val is None:
            raise ValueError(f"Nullability Violation: Mandatory field '{field}' cannot be Null.")
            
        # Check for string placeholders representing nulls (e.g. "N/A" or "Unknown")
        if isinstance(val, str):
            cleaned_val = val.strip().lower()
            if cleaned_val in STRING_NULL_PLACEHOLDERS:
                raise ValueError(
                    f"Nullability Violation: Mandatory field '{field}' contains "
                    f"an invalid placeholder value '{val}'."
                )

    # 2. Parse and normalize optional parameters (e.g., Private Financials)
    optional_fields = ["Annual Revenues", "Annual Profits", "Company Valuation", "Total Capital Raised"]
    for field in optional_fields:
        val = record.get(field)
        if val is not None:
            if isinstance(val, str):
                cleaned_val = val.strip().lower()
                if cleaned_val in STRING_NULL_PLACEHOLDERS:
                    # Gracefully normalize the placeholder to Python None
                    record[field] = None

    # 3. Graceful parsing check of text fields containing undisclosed values
    funding_rounds = record.get("Recent Funding Rounds")
    if funding_rounds:
        # Verify that containing the word "Undisclosed" doesn't crash any financial logic,
        # but is treated as a valid textual history.
        if "undisclosed" in str(funding_rounds).lower():
            # Ensure total capital is safely handled as null/None if undisclosed
            if record.get("Total Capital Raised") is not None:
                # If capital was populated as a string like "Undisclosed", normalize to None
                if str(record["Total Capital Raised"]).strip().lower() in STRING_NULL_PLACEHOLDERS:
                    record["Total Capital Raised"] = None

    return True


# --- Pytest Nullability Suite ---

def test_private_stealth_startup_null_financials_success():
    """
    Verifies that an early stage stealth company is accepted with completely
    empty optional financial parameters, while maintaining critical mandatory parameters.
    """
    stealth_company = {
        "Company Name": "Stealth AI Inc.",
        "Category": "Startup",
        "Year of Incorporation": 2025,
        "Overview of the Company": "Building advanced LLM security testing tools in stealth.",
        "Nature of Company": "Private",
        "Company Headquarters": "Boston, USA",
        "Employee Size": "1-10",
        # Nullable optional metrics
        "Annual Revenues": None,
        "Annual Profits": None,
        "Company Valuation": "N/A",  # String placeholder to be normalized
        "Recent Funding Rounds": "2025-04-10 - Undisclosed - Seed"
    }
    
    assert validate_nullable_data_integrity(stealth_company) is True
    # Verify optional "N/A" was normalized to None successfully
    assert stealth_company["Company Valuation"] is None


def test_public_company_full_data_success():
    """
    Ensures a fully populated public company profile with active financial metrics passes.
    """
    public_company = {
        "Company Name": "Alphabet Inc.",
        "Category": "Enterprise",
        "Year of Incorporation": 1998,
        "Overview of the Company": "A global technology company specializing in search and cloud solutions.",
        "Nature of Company": "Public",
        "Company Headquarters": "Mountain View, USA",
        "Employee Size": "100000+",
        "Annual Revenues": "$307,000,000,000",
        "Annual Profits": "$73,000,000,000",
        "Company Valuation": "$1,800,000,000,000"
    }
    assert validate_nullable_data_integrity(public_company) is True


def test_missing_mandatory_field_fails():
    """
    Rejects the record if a mandatory parameter is entirely absent (evaluates to None).
    """
    malformed_record = {
        "Company Name": "Alpha Partners",
        "Category": None,  # Mandatory field is missing
        "Year of Incorporation": 2020,
        "Overview of the Company": "A venture fund seeking tech investments.",
        "Nature of Company": "Partnership",
        "Company Headquarters": "New York, USA",
        "Employee Size": "11-50"
    }
    with pytest.raises(ValueError, match="Mandatory field 'Category' cannot be Null"):
        validate_nullable_data_integrity(malformed_record)


def test_placeholder_string_nulls_in_mandatory_field_fails():
    """
    Rejects the record if a mandatory parameter is populated with a string placeholder like "N/A".
    """
    malformed_record = {
        "Company Name": "Unknown Co.",
        "Category": "Startup",
        "Year of Incorporation": 2021,
        "Overview of the Company": "N/A",  # Mandatory field populated with invalid placeholder
        "Nature of Company": "Private",
        "Company Headquarters": "Seattle, USA",
        "Employee Size": "1-10"
    }
    with pytest.raises(ValueError, match="Mandatory field 'Overview of the Company' contains an invalid placeholder"):
        validate_nullable_data_integrity(malformed_record)