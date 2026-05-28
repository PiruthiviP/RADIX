import re
import pytest
from typing import Optional, List, Dict, Any

# --- Calculation Engines with strict Null Propagation ---

def calculate_yoy_growth(current_rev: Optional[float], prev_rev: Optional[float]) -> Optional[float]:
    """
    Derived metric: YoY Growth.
    Propagates Null if either dependency is missing [1].
    """
    if current_rev is None or prev_rev is None:
        return None
    if prev_rev == 0:
        return None  # Avoid division by zero
    return ((current_rev - prev_rev) / prev_rev) * 100


def calculate_profitability_status(profits: Optional[float]) -> Optional[str]:
    """
    Derived status: Profitability Status.
    Propagates Null if Profits are unknown [1].
    """
    if profits is None:
        return None
    if profits > 0:
        return "Profitable"
    elif profits < 0:
        return "Loss-making"
    else:
        return "Break-even"


def calculate_market_share(revenue: Optional[float], tam: Optional[float]) -> Optional[float]:
    """
    Derived metric: Market Share (%).
    Propagates Null if revenue or TAM is unknown [1].
    """
    if revenue is None or tam is None:
        return None
    if tam == 0:
        return None
    return (revenue / tam) * 100


def sum_total_capital_raised(rounds_text: Optional[str]) -> Optional[float]:
    """
    Derived metric: Total Capital Raised.
    Parses and sums numerical rounds; returns None if all rounds are undisclosed [1].
    """
    if not rounds_text:
        return None
        
    # Extract all currency amounts (e.g., $5,000,000 or $5M)
    amounts = re.findall(r"\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*([KkMmBb]?)", rounds_text)
    if not amounts:
        return None  # All rounds undisclosed or parsing yielded no numbers
        
    total = 0.0
    for val, suffix in amounts:
        num = float(val.replace(",", ""))
        if suffix.lower() == "k":
            num *= 1_000
        elif suffix.lower() == "m":
            num *= 1_000_000
        elif suffix.lower() == "b":
            num *= 1_000_000_000
        total += num
        
    return total


def calculate_cac_ltv_ratio(cac: Optional[float], ltv: Optional[float]) -> Optional[str]:
    """
    Derived metric: CAC:LTV Ratio [1].
    Propagates Null if either dependency is missing [1].
    """
    if cac is None or ltv is None:
        return None
    if ltv == 0:
        return None
    ratio_val = cac / ltv
    return f"{ratio_val:.1f}:1"


def calculate_runway(cash: Optional[float], burn_rate: Optional[float]) -> Optional[float]:
    """
    Derived metric: Runway (Months).
    Propagates Null if cash or burn rate is unknown [1].
    """
    if cash is None or burn_rate is None:
        return None
    if burn_rate <= 0:
        return None  # Infinite runway or division by zero handled as Null
    return cash / burn_rate


def calculate_burn_multiplier(net_burn: Optional[float], net_new_arr: Optional[float]) -> Optional[float]:
    """
    Derived metric: Burn Multiplier.
    Propagates Null if burn or new ARR is unknown [1].
    """
    if net_burn is None or net_new_arr is None:
        return None
    if net_new_arr == 0:
        return None
    return net_burn / net_new_arr


# --- Pytest Null Propagation Test Cases ---

def test_yoy_growth_null_propagation():
    """
    Asserts that if current or previous year revenues are missing,
    the derived YoY growth rate cleanly propagates as None [1].
    """
    # Case A: Current year is missing
    assert calculate_yoy_growth(None, 10_000_000.0) is None
    
    # Case B: Previous year is missing
    assert calculate_yoy_growth(15_000_000.0, None) is None
    
    # Case C: Both are present (Successful path)
    assert calculate_yoy_growth(15_000_000.0, 10_000_000.0) == 50.0


def test_profitability_status_null_propagation():
    """
    Asserts that if annual profits are undisclosed, derived status
    propagates cleanly as None, rather than defaulting to an enum [1].
    """
    # Case A: Profits missing
    assert calculate_profitability_status(None) is None
    
    # Case B: Active profitable state
    assert calculate_profitability_status(2_500_000.0) == "Profitable"


def test_market_share_null_propagation():
    """
    Asserts that if TAM or Revenues are unknown, derived market share is None [1].
    """
    assert calculate_market_share(None, 100_000_000.0) is None
    assert calculate_market_share(5_000_000.0, None) is None
    assert calculate_market_share(5_000_000.0, 100_000_000.0) == 5.0


def test_total_capital_raised_null_propagation():
    """
    Asserts that if all rounds are undisclosed, total capital is None [1].
    """
    # Case A: Undisclosed transaction rounds
    undisclosed_rounds = "2025-01-10 - Undisclosed - Series A, 2024-03-05 - Undisclosed - Seed"
    assert sum_total_capital_raised(undisclosed_rounds) is None
    
    # Case B: Standard transactional evaluation (Successful path)
    valid_rounds = "2025-01-10 - $5M - Series A, 2024-03-05 - $1.5M - Seed"
    assert sum_total_capital_raised(valid_rounds) == 6_500_000.0


def test_cac_ltv_ratio_null_propagation():
    """
    Asserts that if LTV or CAC is missing, ratio propagates cleanly as None [1].
    """
    assert calculate_cac_ltv_ratio(None, 5000.0) is None
    assert calculate_cac_ltv_ratio(1500.0, None) is None
    assert calculate_cac_ltv_ratio(1500.0, 5000.0) == "0.3:1"


def test_runway_null_propagation():
    """
    Asserts that if cash or burn rate is missing, runway propagates as None [1].
    """
    assert calculate_runway(None, 100_000.0) is None
    assert calculate_runway(500_000.0, None) is None
    assert calculate_runway(500_000.0, 0.0) is None  # Division check
    assert calculate_runway(500_000.0, 100_000.0) == 5.0


def test_burn_multiplier_null_propagation():
    """
    Asserts that if net burn or net new ARR is missing, burn multiplier is None [1].
    """
    assert calculate_burn_multiplier(None, 1_000_000.0) is None
    assert calculate_burn_multiplier(500_000.0, None) is None
    assert calculate_burn_multiplier(500_000.0, 1_000_000.0) == 0.5