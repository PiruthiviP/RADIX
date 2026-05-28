import pytest
from typing import Dict, Any, Tuple, Optional

# Expected standard values according to metadata constraints
ALLOWED_MATURITY_STAGES = {"Startup", "Scale-up", "Mature", "Enterprise"}
ALLOWED_PROFITABILITY_STATUSES = {"Profitable", "Break-even", "Loss-making"}

def validate_early_stage_startup(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter edge case rules for new startups (Incorporation Year = 2026):
    1. If Year of Incorporation is 2026, Company maturity MUST be "Startup".
    2. If Annual Revenues is None/NULL or $0, Profitability Status CANNOT be "Profitable".
    3. Optional metrics (like Glassdoor Rating, Exit History) are allowed to be None.
    """
    errors = []
    
    # Parse Incorporation Year
    try:
        inc_year = int(payload.get("Year of Incorporation", 0) or 0)
    except ValueError:
        errors.append("Type Error: Year of Incorporation must be an integer.")
        return False, errors

    # Rule 1: Maturity constraint for 2026 startups
    maturity = payload.get("Company maturity")
    if inc_year == 2026:
        if maturity != "Startup":
            errors.append(f"Maturity Error: Company founded in 2026 must have maturity 'Startup' (Ingested: '{maturity}').")

    # Rule 2: Profitability constraint for pre-revenue companies
    revenues = payload.get("Annual Revenues")
    profitability = payload.get("Profitability Status")
    
    is_pre_revenue = False
    if revenues is None:
        is_pre_revenue = True
    elif isinstance(revenues, (int, float)) and revenues == 0:
        is_pre_revenue = True
    elif isinstance(revenues, str):
        # Check if string represents zero
        clean_rev = revenues.replace("$", "").replace(",", "").strip()
        if clean_rev == "" or clean_rev == "0":
            is_pre_revenue = True

    if is_pre_revenue:
        if profitability == "Profitable":
            errors.append("Financial Logic Error: Company is pre-revenue (Annual Revenues is NULL or $0) but Profitability Status is marked as 'Profitable'.")

    # Rule 3: Verify optional fields are allowed to be None (no errors raised)
    optional_fields_to_check = ["Glassdoor Rating", "Indeed Rating", "Exit Strategy/History", "Awards & Recognitions"]
    for field in optional_fields_to_check:
        val = payload.get(field)
        # Simply verifying that having None values does not generate validation errors
        if val is None:
            pass 

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_valid_new_startup_passes():
    """Verifies that a valid early-stage startup profile passes all edge-case rules."""
    new_startup_payload = {
        "Year of Incorporation": 2026,
        "Company maturity": "Startup",
        "Annual Revenues": None,  # Pre-revenue
        "Profitability Status": "Loss-making",  # Valid status for pre-revenue
        "Glassdoor Rating": None,  # Graceful degradation
        "Exit Strategy/History": None  # Graceful degradation
    }
    
    success, errors = validate_early_stage_startup(new_startup_payload)
    assert success is True
    assert not errors

def test_new_startup_with_invalid_maturity_fails():
    """Verifies that a company incorporated in 2026 claiming to be 'Mature' fails validation."""
    invalid_payload = {
        "Year of Incorporation": 2026,
        "Company maturity": "Mature",  # Contradicts 2026 founding year
        "Annual Revenues": None,
        "Profitability Status": "Loss-making"
    }
    
    success, errors = validate_early_stage_startup(invalid_payload)
    assert success is False
    assert any("Maturity Error" in err for err in errors)

def test_pre_revenue_marked_profitable_fails():
    """Verifies that a pre-revenue company claiming to be 'Profitable' fails validation."""
    invalid_payload = {
        "Year of Incorporation": 2026,
        "Company maturity": "Startup",
        "Annual Revenues": "$0",  # Pre-revenue
        "Profitability Status": "Profitable"  # Contradicts $0 revenue
    }
    
    success, errors = validate_early_stage_startup(invalid_payload)
    assert success is False
    assert any("Financial Logic Error" in err for err in errors)