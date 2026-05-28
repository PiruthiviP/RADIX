import re
import pytest
from typing import Dict, Any, List, Tuple

def parse_money(val: Any) -> float:
    """Parses money strings (e.g. '$10M', '$1.5B') into raw floats."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
        
    clean_str = str(val).replace("$", "").replace(",", "").strip().upper()
    multiplier = 1.0
    
    if clean_str.endswith("B"):
        multiplier = 1e9
        clean_str = clean_str[:-1]
    elif clean_str.endswith("M"):
        multiplier = 1e6
        clean_str = clean_str[:-1]
    elif clean_str.endswith("K"):
        multiplier = 1e3
        clean_str = clean_str[:-1]
        
    try:
        return float(clean_str) * multiplier
    except ValueError:
        return 0.0

def validate_cross_field_consistency(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces cross-field mathematical and logical accuracy validations.
    Returns: (success_bool, list_of_error_logs)
    """
    errors = []

    # 1. Total Capital Raised vs Recent Funding Rounds
    total_raised = parse_money(payload.get("Total Capital Raised"))
    rounds_str = payload.get("Recent Funding Rounds", "")
    
    if rounds_str and total_raised > 0:
        # Extract all money values (e.g. '$10M') from the rounds string
        rounds_amounts = re.findall(r"\$\s*([\d\.]+)\s*([KkMmBb]?)", rounds_str)
        sum_of_rounds = 0.0
        for amt, multiplier_tag in rounds_amounts:
            full_amt_str = f"${amt}{multiplier_tag}"
            sum_of_rounds += parse_money(full_amt_str)
            
        if abs(total_raised - sum_of_rounds) > 0.01:
            errors.append(f"Consistency Error: Total Capital Raised ({total_raised}) does not equal the sum of Recent Funding Rounds ({sum_of_rounds}).")

    # 2. CAC & CLV vs CAC:LTV Ratio
    cac = parse_money(payload.get("Customer Acquisition Cost (CAC)"))
    clv = parse_money(payload.get("Customer Lifetime Value (CLV)"))
    ratio_str = str(payload.get("CAC:LTV Ratio", ""))
    
    if cac > 0 and clv > 0 and ratio_str:
        # Expecting format 'X:1' or 'X'
        ratio_match = re.match(r"^([\d\.]+)(:1)?$", ratio_str.strip())
        if ratio_match:
            expected_ratio = round(clv / cac, 2)
            ingested_ratio = round(float(ratio_match.group(1)), 2)
            if abs(expected_ratio - ingested_ratio) > 0.05:
                errors.append(f"Consistency Error: Ingested CAC:LTV Ratio ({ingested_ratio}) does not match the calculated quotient CLV/CAC ({expected_ratio}).")
        else:
            errors.append(f"Format Error: Ingested CAC:LTV Ratio '{ratio_str}' does not match standard ratio formats.")

    # 3. Burn Rate vs Runway vs Total Capital Raised
    burn_monthly = parse_money(payload.get("Burn Rate"))
    total_capital = parse_money(payload.get("Total Capital Raised"))
    runway_str = str(payload.get("Runway", ""))
    
    if burn_monthly > 0 and total_capital > 0 and runway_str:
        try:
            ingested_runway = float(runway_str)
            expected_runway = round(total_capital / burn_monthly, 2)
            if abs(ingested_runway - expected_runway) > 0.1:
                errors.append(f"Consistency Error: Ingested Runway ({ingested_runway}) does not match calculated Runway Capital/Burn ({expected_runway}).")
        except ValueError:
            pass

    # 4. Profitability Status vs Annual Profits
    annual_profits = parse_money(payload.get("Annual Profits"))
    prof_status = payload.get("Profitability Status")
    
    if prof_status:
        if annual_profits > 0 and prof_status != "Profitable":
            errors.append(f"Consistency Error: Profitability Status '{prof_status}' does not match positive Annual Profits ({annual_profits}).")
        elif annual_profits < 0 and prof_status != "Loss-making":
            errors.append(f"Consistency Error: Profitability Status '{prof_status}' does not match negative Annual Profits ({annual_profits}).")
        elif annual_profits == 0 and prof_status != "Break-even":
            errors.append(f"Consistency Error: Profitability Status '{prof_status}' does not match zero Annual Profits.")

    # 5. Office Locations vs Countries Operating In
    countries_operating = [c.strip().upper() for c in str(payload.get("Countries Operating In", "")).split(",") if c.strip()]
    offices_str = str(payload.get("Office Locations", ""))
    
    if countries_operating and offices_str:
        # Find country abbreviations in parentheses (e.g., '(US)', '(UK)')
        extracted_countries = re.findall(r"\(\s*([A-Za-z]{2,})\s*\)", offices_str)
        for country in extracted_countries:
            if country.upper() not in countries_operating:
                errors.append(f"Consistency Error: Office Location country '({country})' is not registered in Countries Operating In ({countries_operating}).")

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_consistent_record_passes_validation():
    """Verifies that a mathematically and structurally consistent profile passes validation."""
    valid_payload = {
        "Total Capital Raised": "$25M",
        "Recent Funding Rounds": "2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M",
        "Customer Acquisition Cost (CAC)": "$100",
        "Customer Lifetime Value (CLV)": "$300",
        "CAC:LTV Ratio": "3:1",
        "Burn Rate": "$50K",
        "Runway": "500",  # 25,000,000 / 50,000 = 500 months
        "Annual Profits": "-$2M",
        "Profitability Status": "Loss-making",
        "Countries Operating In": "US, UK",
        "Office Locations": "New York (US), London (UK)"
    }
    success, errors = validate_cross_field_consistency(valid_payload)
    assert success is True
    assert not errors

def test_mismatched_funding_rounds_fails():
    """Verifies that if the sum of logged rounds does not match the Total Capital Raised, validation fails."""
    inconsistent_payload = {
        "Total Capital Raised": "$30M",  # Inconsistent total
        "Recent Funding Rounds": "2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M"
    }
    success, errors = validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any("Total Capital Raised" in err for err in errors)

def test_mismatched_cac_ltv_ratio_fails():
    """Verifies that an incorrect CAC:LTV quotient fails validation."""
    inconsistent_payload = {
        "Customer Acquisition Cost (CAC)": 100,
        "Customer Lifetime Value (CLV)": 300,
        "CAC:LTV Ratio": "5:1"  # Incorrect ratio (300/100 = 3:1)
    }
    success, errors = validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any("CAC:LTV Ratio" in err for err in errors)

def test_mismatched_profitability_status_fails():
    """Verifies that if profitability status disagrees with annual profit polarity, validation fails."""
    inconsistent_payload = {
        "Annual Profits": 1500000.0,  # Positive profit
        "Profitability Status": "Loss-making"  # Contradictory status
    }
    success, errors = validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any("Profitability Status" in err for err in errors)

def test_mismatched_office_locations_country_fails():
    """Verifies that having an office in a country not listed in Countries Operating In fails validation."""
    inconsistent_payload = {
        "Countries Operating In": "US",
        "Office Locations": "New York (US), London (UK)"  # UK is not in operating list
    }
    success, errors = validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any("Office Location country" in err for err in errors)