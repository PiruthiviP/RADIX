import pytest
from typing import Dict, Any, List, Tuple

def validate_field_dependencies(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter completeness dependency rules:
    1. If CEO Name exists, CEO LinkedIn URL should exist.
    2. If CAC and CLV exist, CAC:LTV Ratio must be populated.
    3. If Burn Rate and Total Capital Raised exist, Runway must be populated.
    4. If Recent Funding Rounds exists, Total Capital Raised must be populated.
    5. If Market Share (%) exists, Annual Revenues must be populated.
    """
    errors = []

    # Helper to check if a field is populated (non-null and non-empty string)
    def is_filled(field: str) -> bool:
        val = payload.get(field)
        if val is None:
            return False
        if isinstance(val, str) and val.strip() == "":
            return False
        return True

    # Rule 1: CEO Name <-> CEO LinkedIn URL
    if is_filled("CEO Name") and not is_filled("CEO LinkedIn URL"):
        errors.append("CEO LinkedIn URL must be populated when CEO Name is present.")
    if is_filled("CEO LinkedIn URL") and not is_filled("CEO Name"):
        errors.append("CEO Name must be populated when CEO LinkedIn URL is present.")

    # Rule 2: CAC & CLV -> CAC:LTV Ratio
    if is_filled("Customer Acquisition Cost (CAC)") and is_filled("Customer Lifetime Value (CLV)"):
        if not is_filled("CAC:LTV Ratio"):
            errors.append("CAC:LTV Ratio must be populated when both CAC and CLV are present.")

    # Rule 3: Burn Rate & Total Capital Raised -> Runway
    if is_filled("Burn Rate") and is_filled("Total Capital Raised"):
        # Ensure burn rate isn't 0 before requiring runway
        try:
            burn = float(payload.get("Burn Rate", 0))
            if burn > 0 and not is_filled("Runway"):
                errors.append("Runway must be populated when Burn Rate and Total Capital Raised are present.")
        except ValueError:
            pass # Handle non-numeric formats gracefully if applicable

    # Rule 4: Recent Funding Rounds -> Total Capital Raised
    if is_filled("Recent Funding Rounds") and not is_filled("Total Capital Raised"):
        errors.append("Total Capital Raised must be populated when Recent Funding Rounds are documented.")

    # Rule 5: Market Share (%) -> Annual Revenues
    if is_filled("Market Share (%)") and not is_filled("Annual Revenues"):
        errors.append("Annual Revenues must be populated when Market Share (%) is present.")

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_dependent_fields_all_present_passes():
    """Verifies that validation passes when all dependent groups are fully and correctly populated."""
    valid_payload = {
        "CEO Name": "Satya Nadella",
        "CEO LinkedIn URL": "https://linkedin.com/in/satyanadella",
        "Customer Acquisition Cost (CAC)": 100,
        "Customer Lifetime Value (CLV)": 300,
        "CAC:LTV Ratio": "3:1",
        "Burn Rate": 50000,
        "Total Capital Raised": 500000,
        "Runway": 10,
        "Recent Funding Rounds": "2025-01-01 - Series A - $10M",
        "Total Capital Raised": 10000000,
        "Market Share (%)": "5%",
        "Annual Revenues": "$100M"
    }
    success, errors = validate_field_dependencies(valid_payload)
    assert success is True
    assert not errors

def test_missing_ceo_linkedin_fails_dependency():
    """Verifies that providing a CEO Name without a CEO LinkedIn URL raises a validation error."""
    payload = {
        "CEO Name": "Satya Nadella",
        "CEO LinkedIn URL": None
    }
    success, errors = validate_field_dependencies(payload)
    assert success is False
    assert any("CEO LinkedIn URL must be populated" in err for err in errors)

def test_missing_derived_ratio_fails_dependency():
    """Verifies that having CAC and CLV without the derived CAC:LTV Ratio fails validation."""
    payload = {
        "Customer Acquisition Cost (CAC)": 100,
        "Customer Lifetime Value (CLV)": 300,
        "CAC:LTV Ratio": None
    }
    success, errors = validate_field_dependencies(payload)
    assert success is False
    assert any("CAC:LTV Ratio must be populated" in err for err in errors)

def test_missing_annual_revenues_fails_market_share_dependency():
    """Verifies that declaring a Market Share (%) without providing Annual Revenues fails validation."""
    payload = {
        "Market Share (%)": "5%",
        "Annual Revenues": None
    }
    success, errors = validate_field_dependencies(payload)
    assert success is False
    assert any("Annual Revenues must be populated" in err for err in errors)