import pytest
from typing import Dict, Any, Tuple, List, Optional

# =====================================================================
# Allowed standard values and metadata constraints
# =====================================================================

ALLOWED_MATURITY_STAGES = {"Startup", "Scale-up", "Mature", "Enterprise"}
ALLOWED_PROFITABILITY_STATUSES = {"Profitable", "Break-even", "Loss-making"}
ALLOWED_CONGLOMERATE_CATEGORIES = {"Conglomerate", "Enterprise"}
ALLOWED_CONGLOMERATE_MATURITIES = {"Mature", "Enterprise"}
ALLOWED_PRIVATE_STRUCTURES = {"Private", "Partnership", "Subsidiary", "Non-Profit"}


# =====================================================================
# Utility Functions & Core Validation Functions
# =====================================================================

def parse_currency_string_to_float(val: str) -> float:
    """Parses money strings (e.g. '$307.39B') into raw floats."""
    if not val:
        return 0.0
    clean_str = str(val).replace("$", "").replace(",", "").strip().upper()
    multiplier = 1.0
    if clean_str.endswith("B"):
        multiplier = 1e9
        clean_str = clean_str[:-1]
    elif clean_str.endswith("M"):
        multiplier = 1e6
        clean_str = clean_str[:-1]
    try:
        return float(clean_str) * multiplier
    except ValueError:
        return 0.0


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
        if val is None:
            pass 

    return len(errors) == 0, errors


def validate_conglomerate_edge_cases(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter edge case rules for very large companies:
    1. If parsed Annual Revenues are > $1B (1e9), Category MUST be 'Conglomerate' or 'Enterprise'.
    2. If Countries Operating In lists > 1 country, Global exposure MUST be 'Yes'.
    3. If Employee Size is '10,000+' or > 10000, Company maturity MUST be 'Mature' or 'Enterprise'.
    """
    errors = []
    
    # Rule 1: Category enforcement for billion-dollar entities
    raw_rev = payload.get("Annual Revenues")
    category = payload.get("Category")
    if raw_rev:
        revenue_float = parse_currency_string_to_float(raw_rev)
        if revenue_float >= 1e9: # Greater than or equal to $1B
            if category not in ALLOWED_CONGLOMERATE_CATEGORIES:
                errors.append(
                    f"Category Error: Company with revenue >= $1B ({raw_rev}) must be classified as "
                    f"'Conglomerate' or 'Enterprise' (Ingested: '{category}')."
                )

    # Rule 2: Global exposure constraint for multinational lists
    countries_str = str(payload.get("Countries Operating In", ""))
    global_exp = payload.get("Global exposure")
    if countries_str and countries_str.strip() != "":
        countries_list = [c.strip() for c in countries_str.split(",") if c.strip()]
        if len(countries_list) > 1:
            if global_exp != "Yes":
                errors.append(
                    f"Logical Error: Company operates in multiple countries ({countries_str}), "
                    f"but Global exposure is marked as '{global_exp}' (Expected: 'Yes')."
                )

    # Rule 3: Maturity level for massive headcounts
    emp_size = str(payload.get("Employee Size", ""))
    maturity = payload.get("Company maturity")
    if emp_size == "10,000+" or "10000" in emp_size:
        if maturity not in ALLOWED_CONGLOMERATE_MATURITIES:
            errors.append(
                f"Maturity Error: Company with headcount '{emp_size}' must have maturity "
                f"'Mature' or 'Enterprise' (Ingested: '{maturity}')."
            )

    return len(errors) == 0, errors


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


# =====================================================================
# Unit Tests
# =====================================================================

# --- Tests for validate_early_stage_startup (tc_6.1) ---

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


# --- Tests for validate_conglomerate_edge_cases (tc_6.2) ---

def test_valid_conglomerate_profile_passes():
    """Verifies that a valid global conglomerate profile successfully passes all edge-case rules."""
    valid_payload = {
        "Company Name": "Alphabet Inc.",
        "Category": "Conglomerate",
        "Employee Size": "10,000+",
        "Countries Operating In": "US, UK, Germany, France, Japan",
        "Annual Revenues": "$307.39B",
        "Company maturity": "Mature",
        "Global exposure": "Yes"
    }
    success, errors = validate_conglomerate_edge_cases(valid_payload)
    assert success is True
    assert not errors


def test_billion_dollar_company_mismatched_category_fails():
    """Verifies that a company with revenues >= $1B classified as a 'Startup' fails validation."""
    invalid_payload = {
        "Company Name": "Alphabet Inc.",
        "Category": "Startup",  # Invalid classification for a giant conglomerate
        "Employee Size": "10,000+",
        "Countries Operating In": "US, UK",
        "Annual Revenues": "$307.39B",
        "Company maturity": "Mature",
        "Global exposure": "Yes"
    }
    success, errors = validate_conglomerate_edge_cases(invalid_payload)
    assert success is False
    assert any("Category Error" in err for err in errors)


def test_multinational_with_no_global_exposure_fails():
    """Verifies that operating in multiple countries requires 'Yes' for Global exposure."""
    invalid_payload = {
        "Company Name": "Nestlé S.A.",
        "Category": "Conglomerate",
        "Employee Size": "10,000+",
        "Countries Operating In": "US, UK, Switzerland",
        "Annual Revenues": "$95B",
        "Company maturity": "Mature",
        "Global exposure": "No"  # Contradicts multi-country list
    }
    success, errors = validate_conglomerate_edge_cases(invalid_payload)
    assert success is False
    assert any("Global exposure is marked as 'No'" in err for err in errors)


def test_giant_headcount_with_invalid_maturity_fails():
    """Verifies that a company with 10,000+ employees claiming to be a 'Startup' fails validation."""
    invalid_payload = {
        "Company Name": "Berkshire Hathaway",
        "Category": "Conglomerate",
        "Employee Size": "10,000+",
        "Countries Operating In": "US",
        "Annual Revenues": "$360B",
        "Company maturity": "Startup",  # Contradicts 10,000+ headcount
        "Global exposure": "No"
    }
    success, errors = validate_conglomerate_edge_cases(invalid_payload)
    assert success is False
    assert any("Maturity Error" in err for err in errors)


# --- Tests for validate_private_company_edge_cases (tc_6.3) ---

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
    success, errors = validate_pr