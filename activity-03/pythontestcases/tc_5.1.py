import re
import pytest
from typing import Dict, Any, List, Tuple

def parse_money(val: Any) -> float:
    """Standardizes money strings (e.g. '$10M', '$1.5B') into raw floats."""
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

def validate_calculated_field_accuracy(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter mathematical accuracy of derived fields.
    Returns: (success_bool, list_of_error_logs)
    """
    errors = []

    # 1. Validate CAC:LTV Ratio
    cac = parse_money(payload.get("Customer Acquisition Cost (CAC)"))
    clv = parse_money(payload.get("Customer Lifetime Value (CLV)"))
    ratio_str = str(payload.get("CAC:LTV Ratio", ""))
    
    if cac > 0 and clv > 0 and ratio_str:
        ratio_match = re.match(r"^([\d\.]+)(:1)?$", ratio_str.strip())
        if ratio_match:
            expected_ratio = round(clv / cac, 2)
            ingested_ratio = round(float(ratio_match.group(1)), 2)
            if abs(expected_ratio - ingested_ratio) > 0.05:
                errors.append(f"Calculation Error: Ingested CAC:LTV Ratio ({ingested_ratio}) is inaccurate. Expected: {expected_ratio}.")
        else:
            errors.append(f"Format Error: Ingested CAC:LTV Ratio '{ratio_str}' is invalid.")

    # 2. Validate Burn Multiplier
    monthly_burn = parse_money(payload.get("Burn Rate"))
    net_new_arr = parse_money(payload.get("Net New ARR"))
    multiplier_str = str(payload.get("Burn Multiplier", ""))
    
    if monthly_burn > 0 and net_new_arr > 0 and multiplier_str:
        try:
            ingested_multiplier = float(multiplier_str)
            annual_burn = monthly_burn * 12.0
            expected_multiplier = round(annual_burn / net_new_arr, 2)
            if abs(ingested_multiplier - expected_multiplier) > 0.05:
                errors.append(f"Calculation Error: Ingested Burn Multiplier ({ingested_multiplier}) is inaccurate. Expected: {expected_multiplier}.")
        except ValueError:
            pass

    # 3. Validate Runway
    monthly_burn_rate = parse_money(payload.get("Burn Rate"))
    total_reserves = parse_money(payload.get("Total Capital Raised"))
    runway_str = str(payload.get("Runway", ""))
    
    if monthly_burn_rate > 0 and total_reserves > 0 and runway_str:
        try:
            ingested_runway = float(runway_str)
            expected_runway = round(total_reserves / monthly_burn_rate, 2)
            if abs(ingested_runway - expected_runway) > 0.05:
                errors.append(f"Calculation Error: Ingested Runway ({ingested_runway}) is inaccurate. Expected: {expected_runway}.")
        except ValueError:
            pass

    # 4. Validate Combined Social Media Followers
    combined = payload.get("Social Media Followers – Combined")
    li = payload.get("LinkedIn Followers", 0) or 0
    tw = payload.get("Twitter Followers", 0) or 0
    fb = payload.get("Facebook Followers", 0) or 0
    ig = payload.get("Instagram Followers", 0) or 0
    
    if combined is not None:
        expected_combined = li + tw + fb + ig
        if int(combined) != expected_combined:
            errors.append(f"Calculation Error: Ingested Combined Followers ({combined}) does not match sum of channels ({expected_combined}).")

    # 5. Validate Market Share (%)
    revenues = parse_money(payload.get("Annual Revenues"))
    tam = parse_money(payload.get("Total Addressable Market (TAM)"))
    market_share_str = str(payload.get("Market Share (%)", ""))
    
    if revenues > 0 and tam > 0 and market_share_str:
        share_match = re.match(r"^([\d\.]+)\s*%$", market_share_str.strip())
        if share_match:
            expected_share = round((revenues / tam) * 100, 2)
            ingested_share = round(float(share_match.group(1)), 2)
            if abs(expected_share - ingested_share) > 0.05:
                errors.append(f"Calculation Error: Ingested Market Share ({ingested_share}%) is inaccurate. Expected: {expected_share}%.")
        else:
            errors.append(f"Format Error: Ingested Market Share '{market_share_str}' is invalid.")

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_accurate_calculations_pass():
    """Verifies that a company profile with mathematically correct calculations passes validation."""
    payload = {
        "Customer Acquisition Cost (CAC)": "$100",
        "Customer Lifetime Value (CLV)": "$300",
        "CAC:LTV Ratio": "3:1",
        "Burn Rate": "$100K",
        "Net New ARR": "$1M",
        "Burn Multiplier": "1.2",  # (100,000 * 12) / 1,000,000 = 1.2
        "Total Capital Raised": "$1.2M",
        "Runway": "12.0",  # 1,200,000 / 100,000 = 12 months
        "LinkedIn Followers": 1000,
        "Twitter Followers": 500,
        "Facebook Followers": 300,
        "Instagram Followers": 200,
        "Social Media Followers – Combined": 2000,
        "Annual Revenues": "$500M",
        "Total Addressable Market (TAM)": "$10B",
        "Market Share (%)": "5%"
    }
    success, errors = validate_calculated_field_accuracy(payload)
    assert success is True
    assert not errors

def test_inaccurate_cac_ltv_ratio_fails():
    """Verifies that an incorrect CAC:LTV Ratio is caught and fails validation."""
    payload = {
        "Customer Acquisition Cost (CAC)": 100.0,
        "Customer Lifetime Value (CLV)": 300.0,
        "CAC:LTV Ratio": "5:1"  # Inaccurate (expected 3:1)
    }
    success, errors = validate_calculated_field_accuracy(payload)
    assert success is False
    assert any("Inaccurate. Expected: 3.0" in err for err in errors)

def test_inaccurate_burn_multiplier_fails():
    """Verifies that an incorrect Burn Multiplier is caught and fails validation."""
    payload = {
        "Burn Rate": 100000.0,
        "Net New ARR": 1000000.0,
        "Burn Multiplier": "2.5"  # Inaccurate (expected 1.2)
    }
    success, errors = validate_calculated_field_accuracy(payload)
    assert success is False
    assert any("Inaccurate. Expected: 1.2" in err for err in errors)

def test_inaccurate_social_media_combined_followers_fails():
    """Verifies that an incorrect Combined followers sum fails validation."""
    payload = {
        "LinkedIn Followers": 1000,
        "Twitter Followers": 500,
        "Social Media Followers – Combined": 2500  # Inaccurate (expected 1500)
    }
    success, errors = validate_calculated_field_accuracy(payload)
    assert success is False
    assert any("Combined Followers" in err for err in errors)

def test_inaccurate_market_share_percentage_fails():
    """Verifies that an incorrect Market Share percentage fails validation."""
    payload = {
        "Annual Revenues": "$100M",
        "Total Addressable Market (TAM)": "$1B",
        "Market Share (%)": "15%"  # Inaccurate (expected 10%)
    }
    success, errors = validate_calculated_field_accuracy(payload)
    assert success is False
    assert any("Inaccurate. Expected: 10.0" in err for err in errors)