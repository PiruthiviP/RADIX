import re
import pytest
from typing import Any, Optional

# Regex patterns matching metadata constraints exactly
PERCENTAGE_RE = re.compile(r"^\d{1,3}(\.\d{1,2})?%$")
POSITIVE_INT_RE = re.compile(r"^\d+$")

def parse_currency_string_to_float(val: str) -> Optional[float]:
    """
    Standardizes and parses financial strings (supporting $0 and commas) into raw floats.
    """
    if val is None:
        return None
        
    clean_str = val.replace("$", "").replace(",", "").strip().upper()
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
        return None

def validate_percentage_string(val: str) -> bool:
    """Validates that a percentage string matches the strict percent regex."""
    if not val:
        return False
    return PERCENTAGE_RE.match(val) is not None

def validate_positive_integer_string(val: str) -> bool:
    """Validates that an integer count satisfies the positive integer regex."""
    if not val:
        return False
    return POSITIVE_INT_RE.match(val) is not None


# --- Pytest Tests ---

@pytest.mark.parametrize("zero_revenue", ["$0", "0", "$0.00", "0.00"])
def test_zero_currency_parsing(zero_revenue):
    """Verifies that various zero-currency string representations parse cleanly to float 0.0."""
    parsed_val = parse_currency_string_to_float(zero_revenue)
    assert parsed_val == 0.0

@pytest.mark.parametrize("zero_percentage", ["0%", "0.0%", "0.00%"])
def test_zero_percentage_regex_validation(zero_percentage):
    """Verifies that zero percentage notations satisfy the percentage regex constraint."""
    assert validate_percentage_string(zero_percentage) is True

@pytest.mark.parametrize("zero_integer", ["0", "00"])
def test_zero_integer_regex_validation(zero_integer):
    """Verifies that exact zero integer counts satisfy the positive integer pattern."""
    assert validate_positive_integer_string(zero_integer) is True

def test_negative_turnover_rejected_by_percent_regex():
    """Verifies that negative percentages (invalid boundary states) fail validation."""
    assert validate_percentage_string("-5%") is False

def test_negative_offices_rejected_by_integer_regex():
    """Verifies that negative office counts (invalid boundary states) fail validation."""
    assert validate_positive_integer_string("-1") is False