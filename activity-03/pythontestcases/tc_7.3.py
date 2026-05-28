import re
import pytest
from typing import Any, Tuple, Optional

# Regex patterns matching metadata constraints exactly
YOY_GROWTH_RE = re.compile(r"^[+-]?\d{1,3}(\.\d{1,2})?%$")
NPS_RE = re.compile(r"^-?(100|[1-9]\d?|0)$")

def parse_negative_currency(val: str) -> Optional[float]:
    """
    Parses financial strings into raw floats, supporting negative values.
    Handles standard minus prefix ('-$15M'), suffix ('$15M-'), 
    and accounting parentheses ('($15M)').
    """
    if not val:
        return None
        
    clean_str = val.strip().upper()
    is_negative = False
    
    # Check for accounting parentheses: e.g. ($15M) -> -15M
    if clean_str.startswith("(") and clean_str.endswith(")"):
        is_negative = True
        clean_str = clean_str[1:-1]
        
    # Check for standard minus signs
    if "-" in clean_str:
        is_negative = True
        clean_str = clean_str.replace("-", "")
        
    # Remove standard formatting characters
    clean_str = clean_str.replace("$", "").replace(",", "")
    
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
        val_float = float(clean_str) * multiplier
        return -val_float if is_negative else val_float
    except ValueError:
        return None

def validate_negative_growth_rate(val: str) -> bool:
    """Validates that a negative growth percentage conforms to the signed regex."""
    if not val:
        return False
    return YOY_GROWTH_RE.match(val) is not None

def validate_nps_boundary(val: str) -> Tuple[bool, Optional[int]]:
    """
    Validates that Net Promoter Score (NPS) falls strictly within the [-100, 100] range.
    Rejects values outside this range (e.g. -101) using strict regex pattern matching.
    """
    if not val:
        return False, None
        
    if not NPS_RE.match(val):
        return False, None
        
    try:
        nps_int = int(val)
        if -100 <= nps_int <= 100:
            return True, nps_int
        return False, None
    except ValueError:
        return False, None


# --- Pytest Tests ---

@pytest.mark.parametrize("negative_profit_str, expected_float", [
    ("-15000000", -15000000.0),
    ("-$15,000,000", -15000000.0),
    ("($15,000,000)", -15000000.0),  # Accounting style parenthesis
    ("-$15M", -15000000.0),
    ("($1.5B)", -1500000000.0)
])
def test_negative_financials_parsing(negative_profit_str, expected_float):
    """Verifies that various negative currency formatting options standardize to exact negative floats."""
    parsed_val = parse_negative_currency(negative_profit_str)
    assert parsed_val == expected_float

@pytest.mark.parametrize("negative_growth", ["-15.5%", "-15%", "-0.5%"])
def test_negative_growth_rate_validation(negative_growth):
    """Verifies that negative percentage strings representing revenue contraction are validated successfully."""
    assert validate_negative_growth_rate(negative_growth) is True

@pytest.mark.parametrize("valid_negative_nps, expected_int", [
    ("-85", -85),
    ("-100", -100),  # Exact lower boundary limit
    ("0", 0)
])
def test_valid_negative_nps_boundaries(valid_negative_nps, expected_int):
    """Verifies that negative Net Promoter Scores within the valid range are successfully validated and parsed."""
    success, parsed_val = validate_nps_boundary(valid_negative_nps)
    assert success is True
    assert parsed_val == expected_int

@pytest.mark.parametrize("invalid_negative_nps", [
    "-101",  # Strictly out-of-bounds
    "-150",  # Strictly out-of-bounds
    "-100.5" # Rejects non-integer values
])
def test_invalid_negative_nps_rejected(invalid_negative_nps):
    """Verifies that unallowable or out-of-bounds negative Net Promoter Scores are strictly rejected."""
    success, parsed_val = validate_nps_boundary(invalid_negative_nps)
    assert success is False
    assert parsed_val is None