import pytest
from typing import Dict, Any, Tuple, List

# Allowed legal structures for private companies
ALLOWED_PRIVATE_STRUCTURES = {"Private", "Partnership", "Subsidiary", "Non-Profit"}

def validate_private_company_edge_cases(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter edge case rules for private companies:
    1. Nature of Company MUST be within ALLOWED_PRIVATE_STRUCTURES (cannot be 'Public').
    2. If Nature of Company is private, optional financial metrics (Annual Revenues, Company Valuation,
       Annual Profits) and Exit Strategy/History are allowed to be None (graceful degradation).
    3. Board of Directors / Advisors is mandatory (Not Null) and must be populated with non-empty values,
       rejecting raw None even for private unlisted companies.
    """
    errors = []
    
    # Rule 1: Legal Structure Validation
    nature = payload.get("Nature of Company")
    if not nature:
        errors.append("Validation Error: 'Nature of Company' is mandatory.")
        return False, errors
        
    if nature not in ALLOWED_PRIVATE_STRUCTURES:
        errors.append(
            f"Structure Error: Private company validation run, but company structure is "
            f"marked as '{nature}' (Expected one of: {ALLOWED_PRIVATE_STRUCTURES})."
        )

    # Rule 2: Graceful Degradation check for optional metrics
    # If these are None, we do not append errors (expected behavior for private entities)
    revenues = payload.get("Annual Revenues")
    profits = payload.get("Annual Profits")
    valuation = payload.get("Company Valuation")
    exit_history = payload.get("Exit Strategy/History")

    # Rule 3: Enforce Not Null on Board of Directors
    board = payload.get("Board of Directors / Advisors")
    if board is None:
        errors.append("Mandatory Constraint Error: 'Board of Directors / Advisors' is mandatory and cannot be NULL.")
    elif isinstance(board, str) and board.strip() == "":
        errors.append("Mandatory Constraint Error: 'Board of Directors / Advisors' cannot be empty or whitespace.")

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_valid_private_company_passes():
    """Verifies that a valid private family-owned company successfully passes all edge-case rules."""
    valid_payload = {
        "Nature of Company": "Private",
        "Board of Directors / Advisors": "John Doe - Director, Jane Doe - Director",  # Internal family directors
        "Annual Revenues": None,  # Graceful degradation allowed
        "Annual Profits": None,   # Graceful degradation allowed
        "Company Valuation": None,  # Graceful degradation allowed
        "Exit Strategy/History": None  # Graceful degradation allowed
    }
    success, errors = validate_private_company_edge_cases(valid_payload)
    assert success is True
    assert not errors

def test_private_run_with_public_structure_fails():
    """Verifies that a company marked as 'Public' fails private company validation rules."""
    invalid_payload = {
        "Nature of Company": "Public",  # Invalid for private run
        "Board of Directors / Advisors": "John Doe - Director"
    }
    success, errors = validate_private_company_edge_cases(invalid_payload)
    assert success is False
    assert any("Structure Error" in err for err in errors)

def test_private_company_missing_board_fails():
    """Verifies that even for private companies, the mandatory Board of Directors field cannot be NULL."""
    invalid_payload = {
        "Nature of Company": "Private",
        "Board of Directors / Advisors": None  # Violates Not Null constraint
    }
    success, errors = validate_private_company_edge_cases(invalid_payload)
    assert success is False
    assert any("is mandatory and cannot be NULL" in err for err in errors)

def test_private_company_empty_board_fails():
    """Verifies that even for private companies, the mandatory Board of Directors field cannot be empty whitespace."""
    invalid_payload = {
        "Nature of Company": "Private",
        "Board of Directors / Advisors": "   "  # Violates non-empty data rules
    }
    success, errors = validate_private_company_edge_cases(invalid_payload)
    assert success is False
    assert any("cannot be empty or whitespace" in err for err in errors)