import re
import pytest
from typing import Any, Tuple, Optional

# Regex patterns matching metadata constraints exactly
PERCENTAGE_RE = re.compile(r"^([+-]?\d{1,3})(\.\d{1,2})?%$")
REVENUE_MIX_RE = re.compile(r"^(\d{1,3})%?\s?/\s?(\d{1,3})%?$")

def parse_percentage_to_float(val: str) -> Optional[float]:
    """Parses a percentage string (e.g. '15.5%', '-5%') into a raw float."""
    if not val:
        return None
    match = PERCENTAGE_RE.match(val.strip())
    if not match:
        return None
    try:
        # Re-attach digits and convert to float
        clean_str = val.replace("%", "").strip()
        return float(clean_str)
    except ValueError:
        return None

def validate_strictly_bounded_percentage(val: str) -> bool:
    """Enforces strict [0.0%, 100.0%] bounds on standard percentage fields."""
    parsed_val = parse_percentage_to_float(val)
    if parsed_val is None:
        return False
    return 0.0 <= parsed_val <= 100.0

def validate_unbounded_percentage(val: str) -> bool:
    """Validates percentage strings without range limits (allows negative/exceeding 100%)."""
    parsed_val = parse_percentage_to_float(val)
    return parsed_val is not None

def validate_revenue_mix(val: str) -> bool:
    """
    Validates composite revenue mix ratios (e.g., '80/20' or '80%/20%').
    The sum of the components must equal exactly 100%.
    """
    if not val:
        return False
    match = REVENUE_MIX_RE.match(val.strip())
    if not match:
        return False
    try:
        part1 = int(match.group(1))
        part2 = int(match.group(2))
        return (part1 + part2) == 100
    except ValueError:
        return False


# --- Pytest Tests ---

@pytest.mark.parametrize("valid_turnover", ["0%", "15.5%", "100%"])
def test_valid_strictly_bounded_percentages(valid_turnover):
    """Verifies that turnover, churn, and market shares inside [0, 100] bounds pass validation."""
    assert validate_strictly_bounded_percentage(valid_turnover) is True

@pytest.mark.parametrize("invalid_turnover", ["-5%", "100.1%", "105%", "InvalidText"])
def test_invalid_strictly_bounded_percentages_rejected(invalid_turnover):
    """Verifies that negative or >100% values are strictly rejected for bounded fields."""
    assert validate_strictly_bounded_percentage(invalid_turnover) is False

@pytest.mark.parametrize("valid_unbounded_growth", ["+150%", "-50%", "0%", "100%", "300%"])
def test_valid_unbounded_growth_rates(valid_unbounded_growth):
    """Verifies that YoY growth rate accepts negative values and values exceeding 100%."""
    assert validate_unbounded_percentage(valid_unbounded_growth) is True

def test_invalid_unbounded_growth_format_rejected():
    """Verifies that malformed strings fail growth validation."""
    assert validate_unbounded_percentage("150 percent") is False

@pytest.mark.parametrize("valid_mix", ["80/20", "80%/20%", "50 / 50"])
def test_valid_revenue_mix_summing_to_100(valid_mix):
    """Verifies that revenue mix structures whose parts total exactly 100 pass validation."""
    assert validate_revenue_mix(valid_mix) is True

@pytest.mark.parametrize("invalid_mix", ["70/40", "50/40", "100/10", "InvalidText"])
def test_invalid_revenue_mix_rejected(invalid_mix):
    """Verifies that revenue mix structures whose parts do not sum to 100 are rejected."""
    assert validate_revenue_mix(invalid_mix) is False