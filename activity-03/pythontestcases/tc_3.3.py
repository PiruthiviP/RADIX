import re
import pytest
from typing import Any, Tuple, Optional

# Regex patterns matching metadata constraints exactly
RATINGS_GD_RE = re.compile(r"^[1-5](\.\d)?$")
RATINGS_WEB_RE = re.compile(r"^(10(\.0)?|[0-9](\.\d)?)$")
EMPLOYEE_SIZE_RE = re.compile(r"^(\d+|\d+-\d+)$")

def parse_currency_string_to_float(val: str) -> Optional[float]:
    """
    Standardizes and parses financial strings (e.g. '$50.3B', '$50,300M') into raw floats.
    Handles 'B', 'M', 'K' multipliers and strips commas and currency symbols.
    """
    if not val:
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
        return round(float(clean_str) * multiplier, 2)
    except ValueError:
        return None

def validate_employee_size(val: str) -> bool:
    """Validates that employee count or range is formatted strictly without informal modifiers."""
    if not val:
        return False
    return EMPLOYEE_SIZE_RE.match(val) is not None

def validate_and_parse_rating(val: str, rating_type: str = "Glassdoor") -> Tuple[bool, Optional[float]]:
    """
    Validates decimal rating string precision.
    - Resolves bare integers (e.g. '4') to single-decimal floats ('4.0').
    - Rejects bloated precision decimals (e.g. '4.20') using strict regex.
    """
    if not val:
        return False, None
        
    regex = RATINGS_GD_RE if rating_type == "Glassdoor" else RATINGS_WEB_RE
    
    if not regex.match(val):
        return False, None
        
    try:
        return True, float(val)
    except ValueError:
        return False, None


# --- Pytest Tests ---

@pytest.mark.parametrize("revenue_str, expected_float", [
    ("$50.3B", 50300000000.0),
    ("$50,300M", 50300000000.0),
    ("$50B", 50000000000.0),
    ("$500K", 500000.0)
])
def test_financial_numerical_precision_parsing(revenue_str, expected_float):
    """Verifies that various financial string representations successfully resolve to precise float equivalents."""
    parsed_val = parse_currency_string_to_float(revenue_str)
    assert parsed_val == expected_float

@pytest.mark.parametrize("valid_size", ["10000", "1000-5000"])
def test_valid_employee_size_formats(valid_size):
    """Verifies that exact integers or hyphenated ranges pass headcount boundary checks."""
    assert validate_employee_size(valid_size) is True

@pytest.mark.parametrize("invalid_size", ["10K", "~10000", "10,000+"])
def test_invalid_employee_size_formats(invalid_size):
    """Verifies that informal modifiers or alphabetical multipliers in headcounts fail."""
    assert validate_employee_size(invalid_size) is False

@pytest.mark.parametrize("rating_input, expected_float", [
    ("4.2", 4.2),
    ("4", 4.0)  # Integers must parse cleanly to standard decimal float representation
])
def test_valid_ratings_precision(rating_input, expected_float):
    """Verifies that valid single-decimal ratings are successfully validated and parsed."""
    success, parsed_val = validate_and_parse_rating(rating_input, rating_type="Glassdoor")
    assert success is True
    assert parsed_val == expected_float

@pytest.mark.parametrize("invalid_rating", [
    "4.20",  # Fails strict single-decimal constraint
    "4.25",  # Fails strict single-decimal constraint
    "5.1"    # Out of bounds (1.0 to 5.0)
])
def test_invalid_ratings_rejected(invalid_rating):
    """Verifies that bloated precision ratings or out-of-bounds metrics are strictly rejected."""
    success, parsed_val = validate_and_parse_rating(invalid_rating, rating_type="Glassdoor")
    assert success is False
    assert parsed_val is None

@pytest.mark.parametrize("web_rating_input, expected_float", [
    ("8.5", 8.5),
    ("10", 10.0),
    ("10.0", 10.0)
])
def test_website_ratings_precision(web_rating_input, expected_float):
    """Verifies that website ratings (1.0 to 10.0 scale) are successfully validated and parsed."""
    success, parsed_val = validate_and_parse_rating(web_rating_input, rating_type="Website")
    assert success is True
    assert parsed_val == expected_float

def test_invalid_website_ratings_rejected():
    """Verifies that out-of-bounds or bloated website ratings are rejected."""
    success, parsed_val = validate_and_parse_rating("11.2", rating_type="Website")
    assert success is False