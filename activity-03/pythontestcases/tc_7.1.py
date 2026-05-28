import re
import pytest
from typing import Any, Optional

# Regex patterns matching metadata constraints exactly
EMPLOYEE_SIZE_RE = re.compile(r"^(\d+|\d+-\d+|\d+\+?)$")
POSITIVE_INT_RE = re.compile(r"^\d+$")

def parse_extreme_currency(val: str) -> Optional[float]:
    """
    Parses and standardizes extreme financial strings (up to trillions) into raw floats.
    Handles 'T' (Trillion), 'B' (敲illion), 'M' (Million), 'K' (Thousand) multipliers.
    """
    if not val:
        return None
        
    clean_str = val.replace("$", "").replace(",", "").strip().upper()
    multiplier = 1.0
    
    if clean_str.endswith("T"):
        multiplier = 1e12
        clean_str = clean_str[:-1]
    elif clean_str.endswith("B"):
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
        return None

def validate_extreme_headcount(val: str) -> bool:
    """Validates that massive employee size strings match allowed configurations."""
    if not val:
        return False
    return EMPLOYEE_SIZE_RE.match(val) is not None

def validate_extreme_positive_integer(val: str) -> bool:
    """Validates extremely large integer strings (followers, offices) match positive int patterns."""
    if not val:
        return False
    return POSITIVE_INT_RE.match(val) is not None


# --- Pytest Tests ---

@pytest.mark.parametrize("extreme_revenue, expected_float", [
    ("$611.3B", 611300000000.0),    # Massive retail revenue (Walmart scale)
    ("$3.1T", 3100000000000.0),      # Trillion-dollar market cap (Apple scale)
    ("$100T", 100000000000000.0),    # Global TAM scale
    ("$25B", 25000000000.0)          # Extreme private funding raised
])
def test_extreme_currency_parsing_precision(extreme_revenue, expected_float):
    """Verifies that extreme financial scale notations are parsed into floats with complete precision."""
    parsed_val = parse_extreme_currency(extreme_revenue)
    assert parsed_val == expected_float

@pytest.mark.parametrize("extreme_headcount", ["2300000", "2300000+", "1500000-2000000"])
def test_extreme_employee_size_validation(extreme_headcount):
    """Verifies that extreme headcount values successfully pass boundary pattern matching."""
    assert validate_extreme_headcount(extreme_headcount) is True

@pytest.mark.parametrize("extreme_integer", ["150000000", "11500"])
def test_extreme_positive_integer_validation(extreme_integer):
    """Verifies that extremely large integer values (follower counts, office counts) pass checks."""
    assert validate_extreme_positive_integer(extreme_integer) is True

def test_negative_integer_rejected_as_positive_boundary():
    """Verifies that negative values are rejected by the positive integer boundary checks."""
    assert validate_extreme_positive_integer("-11500") is False