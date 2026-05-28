import re
import datetime
from typing import Any, Tuple, Optional, List, Dict
import pytest

# =====================================================================
# Constants and Regex Patterns Matching Metadata Constraints
# =====================================================================

EMPLOYEE_SIZE_RE = re.compile(r"^(\d+|\d+-\d+|\d+\+?)$")
POSITIVE_INT_RE = re.compile(r"^\d+$")
PERCENTAGE_UNSIGNED_RE = re.compile(r"^\d{1,3}(\.\d{1,2})?%$")
PERCENTAGE_SIGNED_RE = re.compile(r"^([+-]?\d{1,3})(\.\d{1,2})?%$")
YOY_GROWTH_RE = re.compile(r"^[+-]?\d{1,3}(\.\d{1,2})?%$")
NPS_RE = re.compile(r"^-?(100|[1-9]\d?|0)$")
REVENUE_MIX_RE = re.compile(r"^(\d{1,3})%?\s?/\s?(\d{1,3})%?$")
RATIO_CAC_LTV_RE = re.compile(r"^([\d\.]+)(:1)?$")

# Current system time checkpoint: May 22, 2026
CURRENT_SYSTEM_DATE = datetime.date(2026, 5, 22)


# =====================================================================
# Core Parsing and Validation Functions
# =====================================================================

def parse_extreme_currency(val: str) -> Optional[float]:
    """
    Parses and standardizes extreme financial strings (up to trillions) into raw floats.
    Handles 'T' (Trillion), 'B' (Billboard/Billion), 'M' (Million), 'K' (Thousand) multipliers.
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


def parse_currency_string_to_float(val: str) -> Optional[float]:
    """Standardizes and parses financial strings (supporting $0 and commas) into raw floats."""
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
    """Validates that a percentage string matches the strict unsigned percent regex."""
    if not val:
        return False
    return PERCENTAGE_UNSIGNED_RE.match(val) is not None


def validate_positive_integer_string(val: str) -> bool:
    """Validates that an integer count satisfies the positive integer regex."""
    if not val:
        return False
    return POSITIVE_INT_RE.match(val) is not None


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


def parse_percentage_to_float(val: str) -> Optional[float]:
    """Parses a percentage string (e.g. '15.5%', '-5%') into a raw float."""
    if not val:
        return None
    match = PERCENTAGE_SIGNED_RE.match(val.strip())
    if not match:
        return None
    try:
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


def extract_years_from_text(text: str) -> List[int]:
    """Extracts all 4-digit years (from 1800 to 2099) found within a string."""
    if not text:
        return []
    candidates = re.findall(r"\b(18\d{2}|19\d{2}|20\d{2})\b", text)
    return [int(yr) for yr in candidates]


def extract_dates_from_formatted_string(text: str) -> List[datetime.date]:
    """Extracts date objects from YYYY-MM-DD formatted segments."""
    if not text:
        return []
    date_strings = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    parsed_dates = []
    for ds in date_strings:
        try:
            parsed_dates.append(datetime.datetime.strptime(ds, "%Y-%m-%d").date())
        except ValueError:
            pass
    return parsed_dates


def validate_historical_year(year_val: Any) -> bool:
    """Validates that a legal founding year lies strictly between 1800 and 2026."""
    try:
        year = int(year_val)
        return 1800 <= year <= CURRENT_SYSTEM_DATE.year
    except (ValueError, TypeError):
        return False


def validate_historical_timeline(timeline_str: str) -> Tuple[bool, str]:
    """Ensures that no date in a historical event list occurs in the future."""
    dates = extract_dates_from_formatted_string(timeline_str)
    for dt in dates:
        if dt > CURRENT_SYSTEM_DATE:
            return False, f"Factual Error: Event date '{dt}' cannot be in the future (Current: {CURRENT_SYSTEM_DATE})."
    return True, "Historical timeline is valid."


def validate_future_projections(projections_str: str) -> Tuple[bool, str]:
    """Ensures that all years referenced in future projections are strictly > 2026."""
    years = extract_years_from_text(projections_str)
    for year in years:
        if year <= CURRENT_SYSTEM_DATE.year:
            return False, f"Logical Error: Projection year {year} cannot be in the past or present (Threshold: > {CURRENT_SYSTEM_DATE.year})."
    return True, "Future projections timeline is valid."


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
        return "INF"
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


# =====================================================================
# Unit Tests
# =====================================================================

# --- Tests from tc_7.1.py ---

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


# --- Tests from tc_7.2.py ---

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


# --- Tests from tc_7.3.py ---

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


# --- Tests from tc_7.4.py ---

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


# --- Tests from tc_7.5.py ---

@pytest.mark.parametrize("valid_founding_year", [1800, 2000, 2026])
def test_valid_historical_founding_years(valid_founding_year):
    """Verifies that legal incorporation years within bounds (including 1800 and Y2K 2000) pass."""
    assert validate_historical_year(valid_founding_year) is True


@pytest.mark.parametrize("invalid_founding_year", [1799, 2027])
def test_invalid_historical_founding_years_rejected(invalid_founding_year):
    """Verifies that out-of-bounds founding years (too old or future-bound) are rejected."""
    assert validate_historical_year(invalid_founding_year) is False


@pytest.mark.parametrize("valid_news", [
    "2000-01-15 - Y2K System Deployment",
    "2026-05-20 - Global Launch of v2.0"  # Valid historical news right before current checkpoint
])
def test_valid_news_timelines(valid_news):
    """Verifies that historical news events dated in the past pass validation."""
    success, msg = validate_historical_timeline(valid_news)
    assert success is True


@pytest.mark.parametrize("future_news", [
    "2027-10-12 - Series B Closed",  # Future date relative to May 2026
    "2030-01-01 - New Branch Opened"
])
def test_future_news_rejected(future_news):
    """Verifies that historical news parameters strictly reject future dates."""
    success, msg = validate_historical_timeline(future_news)
    assert success is False
    assert "cannot be in the future" in msg


@pytest.mark.parametrize("valid_projection", [
    "2027 - Projected revenue of $50M",
    "Product rollout timeline: Q3 2030 - Launch AI v3.0"
])
def test_valid_future_projections(valid_projection):
    """Verifies that future projections successfully accept forward-looking years (> 2026)."""
    success, msg = validate_future_projections(valid_projection)
    assert success is True


@pytest.mark.parametrize("invalid_projection", [
    "2020 - Completed seed round",  # Past year is invalid for a projection
    "2026 - Current launch trajectory"  # Present year is rejected as future projection
])
def test_invalid_future_projections_rejected(invalid_projection):
    """Verifies that past or present years are rejected in forward-looking projection fields."""
    success, msg = validate_future_projections(invalid_projection)
    assert success is False
    assert "cannot be in the past or present" in msg


# --- Tests from tc_7.6.py ---

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