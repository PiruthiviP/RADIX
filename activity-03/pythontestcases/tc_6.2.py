import pytest
from typing import Dict, Any, Tuple, List

# Allowed categories and stages as defined by metadata constraints
ALLOWED_CONGLOMERATE_CATEGORIES = {"Conglomerate", "Enterprise"}
ALLOWED_CONGLOMERATE_MATURITIES = {"Mature", "Enterprise"}

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


# --- Pytest Tests ---

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