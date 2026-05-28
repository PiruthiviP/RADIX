import pytest
from typing import Dict, Any, Tuple, List, Optional

# Mock Ground-Truth Registries (representing verified state, SEC, and LinkedIn databases)
GROUND_TRUTH_REGISTRY = {
    "microsoft corporation": {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": 1975,
        "CEO Name": "Satya Nadella",
        "Website URL": "https://www.microsoft.com",
        "Employee Count": 221000,
        "Annual Revenues": 245000000000.0  # $245B
    },
    "apple inc.": {
        "Company Name": "Apple Inc.",
        "Year of Incorporation": 1976,
        "CEO Name": "Tim Cook",
        "Website URL": "https://www.apple.com",
        "Employee Count": 164000,
        "Annual Revenues": 383000000000.0  # $383B
    }
}

def parse_employee_range(range_str: str, exact_count: int) -> bool:
    """
    Validates if an exact numeric headcount falls within an ingested range/bucket.
    Supports formats like '10,000+', '1000-5000', etc.
    """
    if not range_str:
        return False
    
    clean_str = range_str.replace(",", "").replace(" ", "")
    
    if "+" in clean_str:
        min_val = int(clean_str.replace("+", ""))
        return exact_count >= min_val
        
    if "-" in clean_str:
        parts = clean_str.split("-")
        if len(parts) == 2:
            min_val = int(parts[0])
            max_val = int(parts[1])
            return min_val <= exact_count <= max_val
            
    return False

def validate_factual_correctness(ingested_record: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """
    Holistically validates the ingested company record against ground-truth data.
    - Evaluates critical identifiers: Company Name, Year of Incorporation, CEO Name, Website, Employee Size, and Revenues.
    - Computes a Factual Accuracy Score based on matching parameters.
    - Returns (success, accuracy_percentage, error_logs).
    """
    company_key = str(ingested_record.get("Company Name", "")).strip().lower()
    
    if not company_key or company_key not in GROUND_TRUTH_REGISTRY:
        return False, 0.0, [f"Validation aborted: Company '{ingested_record.get('Company Name')}' not found in ground-truth registry."]
        
    truth = GROUND_TRUTH_REGISTRY[company_key]
    errors = []
    checks_passed = 0
    total_checks = 6

    # Check 1: Legal Name Matching
    if ingested_record.get("Company Name") == truth["Company Name"]:
        checks_passed += 1
    else:
        errors.append(f"Factual Mismatch [Company Name]: Ingested '{ingested_record.get('Company Name')}', Ground Truth '{truth['Company Name']}'")

    # Check 2: Year of Incorporation Matching
    try:
        ingested_year = int(ingested_record.get("Year of Incorporation", 0))
        if ingested_year == truth["Year of Incorporation"]:
            checks_passed += 1
        else:
            errors.append(f"Factual Mismatch [Year of Incorporation]: Ingested {ingested_year}, Ground Truth {truth['Year of Incorporation']}")
    except ValueError:
        errors.append(f"Type Mismatch [Year of Incorporation]: Value '{ingested_record.get('Year of Incorporation')}' must be integer.")

    # Check 3: CEO Name Matching
    if ingested_record.get("CEO Name") == truth["CEO Name"]:
        checks_passed += 1
    else:
        errors.append(f"Factual Mismatch [CEO Name]: Ingested '{ingested_record.get('CEO Name')}', Ground Truth '{truth['CEO Name']}'")

    # Check 4: Website URL Matching
    if ingested_record.get("Website URL") == truth["Website URL"]:
        checks_passed += 1
    else:
        errors.append(f"Factual Mismatch [Website URL]: Ingested '{ingested_record.get('Website URL')}', Ground Truth '{truth['Website URL']}'")

    # Check 5: Employee Size Range Containment
    ingested_range = ingested_record.get("Employee Size")
    truth_count = truth["Employee Count"]
    if parse_employee_range(ingested_range, truth_count):
        checks_passed += 1
    else:
        errors.append(f"Factual Mismatch [Employee Size]: Exact count {truth_count} falls outside ingested range '{ingested_range}'")

    # Check 6: Financial Revenue Reconciliation (Allow up to 5% variance due to estimation methods)
    try:
        ingested_rev_raw = str(ingested_record.get("Annual Revenues", "")).replace("$", "").replace(",", "")
        # Parsing basic multiplier representations like "B" or "M"
        multiplier = 1.0
        if "B" in ingested_rev_raw:
            multiplier = 1000000000.0
            ingested_rev_raw = ingested_rev_raw.replace("B", "")
        elif "M" in ingested_rev_raw:
            multiplier = 1000000.0
            ingested_rev_raw = ingested_rev_raw.replace("M", "")
            
        ingested_rev = float(ingested_rev_raw) * multiplier
        truth_rev = truth["Annual Revenues"]
        
        variance = abs(ingested_rev - truth_rev) / truth_rev
        if variance <= 0.05:  # 5% acceptable variance
            checks_passed += 1
        else:
            errors.append(f"Factual Mismatch [Annual Revenues]: Ingested {ingested_rev}, Ground Truth {truth_rev} (Exceeded 5% variance)")
    except Exception as e:
        errors.append(f"Parser Mismatch [Annual Revenues]: Could not reconcile '{ingested_record.get('Annual Revenues')}' due to error: {e}")

    accuracy_score = round((checks_passed / total_checks) * 100, 2)
    success = (accuracy_score == 100.0)

    return success, accuracy_score, errors


# --- Pytest Tests ---

def test_accurate_profile_validation_success():
    """Verifies that an ingested profile that factually matches ground truth passes with a 100% score."""
    accurate_payload = {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": 1975,
        "CEO Name": "Satya Nadella",
        "Website URL": "https://www.microsoft.com",
        "Employee Size": "10,000+",
        "Annual Revenues": "$245B"
    }
    success, score, errors = validate_factual_correctness(accurate_payload)
    
    assert success is True
    assert score == 100.0
    assert not errors

def test_mismatched_incorporation_year_fails_validation():
    """Verifies that a factual mismatch on incorporation year reduces score and returns errors."""
    inaccurate_payload = {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": 1999,  # Mismatched year
        "CEO Name": "Satya Nadella",
        "Website URL": "https://www.microsoft.com",
        "Employee Size": "10,000+",
        "Annual Revenues": "$245B"
    }
    success, score, errors = validate_factual_correctness(inaccurate_payload)
    
    assert success is False
    assert score == 83.33  # 5 out of 6 checks passed
    assert any("Year of Incorporation" in err for err in errors)

def test_employee_size_range_out_of_bounds_fails():
    """Verifies that if the ground truth headcount does not fall within the range boundary, validation fails."""
    out_of_bounds_payload = {
        "Company Name": "Apple Inc.",
        "Year of Incorporation": 1976,
        "CEO Name": "Tim Cook",
        "Website URL": "https://www.apple.com",
        "Employee Size": "100-500",  # Incorrect range for 164,000 employees
        "Annual Revenues": "$383B"
    }
    success, score, errors = validate_factual_correctness(out_of_bounds_payload)
    
    assert success is False
    assert score == 83.33
    assert any("Employee Size" in err for err in errors)

def test_revenue_estimation_variance_fails_beyond_threshold():
    """Verifies that if the estimated revenue exceeds the acceptable 5% variance threshold, validation fails."""
    inaccurate_financials_payload = {
        "Company Name": "Apple Inc.",
        "Year of Incorporation": 1976,
        "CEO Name": "Tim Cook",
        "Website URL": "https://www.apple.com",
        "Employee Size": "10,000+",
        "Annual Revenues": "$200B"  # Mismatch (exceeds 5% variance on $383B)
    }
    success, score, errors = validate_factual_correctness(inaccurate_financials_payload)
    
    assert success is False
    assert score == 83.33
    assert any("Annual Revenues" in err for err in errors)