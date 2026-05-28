import re
import pytest
from typing import Dict, Any, Tuple, Optional

# Regex patterns matching metadata constraints exactly
RATIO_CAC_LTV_RE = re.compile(r"^([\d\.]+)(:1)?$")
REVENUE_MIX_RE = re.compile(r"^(\d{1,3})%?\s?/\s?(\d{1,3})%?$")

def validate_and_parse_cac_ltv(ratio_str: str) -> Tuple[bool, str, Optional[float]]:
    """
    Validates the CAC:LTV Ratio boundary conditions.
    - Rejects ratios <= 0 (invalid business model state).
    - Flags a warning if ratio is < 1.0 (unprofitable acquisition).
    - Accepts ratios >= 1.0.
    """
    if not ratio_str:
        return False, "Empty input.", None
        
    match = RATIO_CAC_LTV_RE.match(ratio_str.strip())
    if not match:
        return False, "Invalid ratio format.", None
        
    try:
        ratio_val = float(match.group(1))
        if ratio_val <= 0:
            return False, f"Model Error: Ingested ratio {ratio_val} is invalid (must be > 0).", ratio_val
        elif ratio_val < 1.0:
            return True, f"Warning: Unprofitable Model (Ratio {ratio_val} < 1.0).", ratio_val
        return True, "Valid ratio.", ratio_val
    except ValueError:
        return False, "Parser error.", None

def calculate_burn_multiplier_with_inf(annual_net_burn: float, net_new_arr: float) -> str:
    """
    Calculates Burn Multiplier.
    - If net_new_arr is 0, returns "INF" (infinity) gracefully instead of raising a zero-division error.
    - If annual_net_burn is 0 (or negative/profitable), returns "0.0".
    """
    if annual_net_burn <= 0:
        return "0.0"
    if net_new_arr == 0:
        return "INF"  # Map infinite burn to standard string representation
    return str(round(annual_net_burn / net_new_arr, 2))

def validate_revenue_mix_extremes(mix_str: str) -> bool:
    """Validates that extreme 100/0 and 0/100 proportion mixes pass sum rules."""
    if not mix_str:
        return False
    match = REVENUE_MIX_RE.match(mix_str.strip())
    if not match:
        return False
    try:
        part1 = int(match.group(1))
        part2 = int(match.group(2))
        return (part1 + part2) == 100
    except ValueError:
        return False


# --- Pytest Tests ---

@pytest.mark.parametrize("valid_ratio, expected_status", [
    ("3:1", "Valid ratio."),
    ("3", "Valid ratio."),
    ("0.8:1", "Warning: Unprofitable Model")  # Bounded warning for unprofitable acquisition
])
def test_cac_ltv_ratio_boundaries(valid_ratio, expected_status):
    """Verifies that valid and warning-state acquisition ratios parse correctly."""
    success, msg, val = validate_and_parse_cac_ltv(valid_ratio)
    assert success is True
    assert expected_status in msg

@pytest.mark.parametrize("invalid_ratio", ["0:1", "-0.5:1", "0"])
def test_invalid_cac_ltv_ratios_rejected(invalid_ratio):
    """Verifies that non-positive acquisition ratios (such as zero or negative boundaries) are rejected."""
    success, msg, val = validate_and_parse_cac_ltv(invalid_ratio)
    assert success is False
    assert "Model Error" in msg

def test_infinite_burn_multiplier_handling():
    """Verifies that flat ARR growth gracefully returns an infinite string ('INF') instead of crashing."""
    result = calculate_burn_multiplier_with_inf(annual_net_burn=1200000.0, net_new_arr=0.0)
    assert result == "INF"

def test_profitable_burn_multiplier_handling():
    """Verifies that a net-zero or profitable cash-flow state returns a '0.0' burn multiplier."""
    result = calculate_burn_multiplier_with_inf(annual_net_burn=0.0, net_new_arr=1000000.0)
    assert result == "0.0"

@pytest.mark.parametrize("extreme_mix", ["100/0", "0/100"])
def test_extreme_revenue_mix_boundaries(extreme_mix):
    """Verifies that pure-play (100% recurring or 100% service) mix boundaries pass successfully."""
    assert validate_revenue_mix_extremes(extreme_mix) is True