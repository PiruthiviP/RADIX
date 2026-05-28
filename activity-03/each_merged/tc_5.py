"""
Combined Test Suite: tc_5_1 through tc_5_5
Covers:
  - Calculated field accuracy validation (tc_5_1)
  - Logical consistency validation (tc_5_2)
  - Timeline/chronological consistency validation (tc_5_3)
  - Field format validation (tc_5_4)
  - Cross-parameter coherence validation (tc_5_5)
"""

import re
import pytest
from typing import Any, Dict, List, Tuple


# =============================================================================
# Shared Utilities
# =============================================================================

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


def parse_money_to_float(val: Any) -> float:
    """Parses money strings (e.g. '$10M', '-$1.5B') into raw floats supporting negative signs."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    raw_str = str(val).replace("$", "").replace(",", "").strip().upper()
    is_negative = False
    if "-" in raw_str:
        is_negative = True
        raw_str = raw_str.replace("-", "")
    multiplier = 1.0
    if raw_str.endswith("B"):
        multiplier = 1e9
        raw_str = raw_str[:-1]
    elif raw_str.endswith("M"):
        multiplier = 1e6
        raw_str = raw_str[:-1]
    elif raw_str.endswith("K"):
        multiplier = 1e3
        raw_str = raw_str[:-1]
    try:
        val_float = float(raw_str) * multiplier
        return -val_float if is_negative else val_float
    except ValueError:
        return 0.0


# =============================================================================
# tc_5_1 — Calculated Field Accuracy Validation
# =============================================================================

def validate_calculated_field_accuracy(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Enforces per-parameter mathematical accuracy of derived fields."""
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
                errors.append(
                    f"Calculation Error: Ingested CAC:LTV Ratio ({ingested_ratio}) is inaccurate. "
                    f"Expected: {expected_ratio}."
                )
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
                errors.append(
                    f"Calculation Error: Ingested Burn Multiplier ({ingested_multiplier}) is inaccurate. "
                    f"Expected: {expected_multiplier}."
                )
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
                errors.append(
                    f"Calculation Error: Ingested Runway ({ingested_runway}) is inaccurate. "
                    f"Expected: {expected_runway}."
                )
        except ValueError:
            pass

    # 4. Validate Combined Social Media Followers
    combined = payload.get("Social Media Followers \u2013 Combined")
    li = payload.get("LinkedIn Followers", 0) or 0
    tw = payload.get("Twitter Followers", 0) or 0
    fb = payload.get("Facebook Followers", 0) or 0
    ig = payload.get("Instagram Followers", 0) or 0
    if combined is not None:
        expected_combined = li + tw + fb + ig
        if int(combined) != expected_combined:
            errors.append(
                f"Calculation Error: Ingested Combined Followers ({combined}) does not match "
                f"sum of channels ({expected_combined})."
            )

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
                errors.append(
                    f"Calculation Error: Ingested Market Share ({ingested_share}%) is inaccurate. "
                    f"Expected: {expected_share}%."
                )
        else:
            errors.append(f"Format Error: Ingested Market Share '{market_share_str}' is invalid.")

    return len(errors) == 0, errors


# tc_5_1 Tests

def test_accurate_calculations_pass():
    """Verifies that a company profile with mathematically correct calculations passes validation."""
    payload = {
        "Customer Acquisition Cost (CAC)": "$100",
        "Customer Lifetime Value (CLV)": "$300",
        "CAC:LTV Ratio": "3:1",
        "Burn Rate": "$100K",
        "Net New ARR": "$1M",
        "Burn Multiplier": "1.2",
        "Total Capital Raised": "$1.2M",
        "Runway": "12.0",
        "LinkedIn Followers": 1000,
        "Twitter Followers": 500,
        "Facebook Followers": 300,
        "Instagram Followers": 200,
        "Social Media Followers \u2013 Combined": 2000,
        "Annual Revenues": "$500M",
        "Total Addressable Market (TAM)": "$10B",
        "Market Share (%)": "5%",
    }
    success, errors = validate_calculated_field_accuracy(payload)
    assert success is True
    assert not errors


def test_inaccurate_cac_ltv_ratio_fails():
    """Verifies that an incorrect CAC:LTV Ratio is caught and fails validation."""
    payload = {
        "Customer Acquisition Cost (CAC)": 100.0,
        "Customer Lifetime Value (CLV)": 300.0,
        "CAC:LTV Ratio": "5:1",
    }
    success, errors = validate_calculated_field_accuracy(payload)
    assert success is False
    assert any("Inaccurate. Expected: 3.0" in err for err in errors)


def test_inaccurate_burn_multiplier_fails():
    """Verifies that an incorrect Burn Multiplier is caught and fails validation."""
    payload = {
        "Burn Rate": 100000.0,
        "Net New ARR": 1000000.0,
        "Burn Multiplier": "2.5",
    }
    success, errors = validate_calculated_field_accuracy(payload)
    assert success is False
    assert any("Inaccurate. Expected: 1.2" in err for err in errors)


def test_inaccurate_social_media_combined_followers_fails():
    """Verifies that an incorrect Combined followers sum fails validation."""
    payload = {
        "LinkedIn Followers": 1000,
        "Twitter Followers": 500,
        "Social Media Followers \u2013 Combined": 2500,
    }
    success, errors = validate_calculated_field_accuracy(payload)
    assert success is False
    assert any("Combined Followers" in err for err in errors)


def test_inaccurate_market_share_percentage_fails():
    """Verifies that an incorrect Market Share percentage fails validation."""
    payload = {
        "Annual Revenues": "$100M",
        "Total Addressable Market (TAM)": "$1B",
        "Market Share (%)": "15%",
    }
    success, errors = validate_calculated_field_accuracy(payload)
    assert success is False
    assert any("Inaccurate. Expected: 10.0" in err for err in errors)


# =============================================================================
# tc_5_2 — Logical Consistency Validation
# =============================================================================

def validate_logical_consistency(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Enforces per-parameter logical alignment of related fields."""
    errors = []

    def is_filled(field: str) -> bool:
        val = payload.get(field)
        if val is None:
            return False
        if isinstance(val, str) and val.strip() == "":
            return False
        return True

    # Rule 1: Profitability Status vs Annual Profits
    profit = parse_money_to_float(payload.get("Annual Profits"))
    status = payload.get("Profitability Status")
    if status:
        if status == "Profitable" and profit <= 0:
            errors.append(
                f"Logical Contradiction: Profitability Status is 'Profitable' but Annual Profits are "
                f"negative/zero ({profit})."
            )
        elif status == "Loss-making" and profit >= 0:
            errors.append(
                f"Logical Contradiction: Profitability Status is 'Loss-making' but Annual Profits are "
                f"positive/zero ({profit})."
            )
        elif status == "Break-even" and profit != 0:
            errors.append(
                f"Logical Contradiction: Profitability Status is 'Break-even' but Annual Profits are "
                f"non-zero ({profit})."
            )

    # Rule 2: Nature of Company vs Exit Strategy
    nature = payload.get("Nature of Company")
    exit_history = str(payload.get("Exit Strategy/History", ""))
    if nature == "Public":
        if not re.search(r"\b(ipo|public|stock|listed|nasdaq|nyse)\b", exit_history, re.IGNORECASE):
            errors.append(
                "Logical Contradiction: Company Nature is 'Public' but Exit History lacks "
                "public listing / IPO references."
            )

    # Rule 3: Customer Concentration Risk vs Top Customers
    concentration = payload.get("Customer Concentration Risk")
    if concentration == "Yes" or (isinstance(concentration, str) and "High" in concentration):
        if not is_filled("Top Customers by Client Segments"):
            errors.append(
                "Logical Contradiction: Customer Concentration Risk is flagged but Top Customers are missing."
            )

    # Rule 4: Number of Offices vs Office Locations
    try:
        offices_count = int(payload.get("Number of Offices (beyond HQ)", 0) or 0)
        if offices_count > 0 and not is_filled("Office Locations"):
            errors.append(
                f"Logical Contradiction: Number of Offices is {offices_count} but Office Locations list is empty."
            )
    except ValueError:
        pass

    # Rule 5: Remote Work Policy vs Flexibility Policy
    remote_policy = payload.get("Remote Work Policy")
    flex_policy = payload.get("Remote / hybrid / on-site flexibility")
    if remote_policy == "Remote-First" and flex_policy == "On-Site":
        errors.append(
            "Logical Contradiction: Remote Work Policy is 'Remote-First' but flexibility policy is "
            "set as strict 'On-Site'."
        )

    return len(errors) == 0, errors


# tc_5_2 Tests

def test_consistent_relationships_pass():
    """Verifies that logically aligned fields pass the consistency audit."""
    valid_payload = {
        "Annual Profits": "$1.5M",
        "Profitability Status": "Profitable",
        "Nature of Company": "Public",
        "Exit Strategy/History": "Completed IPO on NASDAQ in 2024",
        "Customer Concentration Risk": "Yes",
        "Top Customers by Client Segments": "Enterprise Segment: 4 main accounts",
        "Number of Offices (beyond HQ)": 3,
        "Office Locations": "London (UK), Paris (FR), Berlin (GER)",
        "Remote Work Policy": "Remote-First",
        "Remote / hybrid / on-site flexibility": "Remote",
    }
    success, errors = validate_logical_consistency(valid_payload)
    assert success is True
    assert not errors


def test_profit_polarity_contradiction_fails():
    """Verifies that mismatched Profitability Status and Annual Profits fail validation."""
    invalid_payload = {
        "Annual Profits": "-$500K",
        "Profitability Status": "Profitable",
    }
    success, errors = validate_logical_consistency(invalid_payload)
    assert success is False
    assert any("Profitability Status is 'Profitable'" in err for err in errors)


def test_public_company_missing_ipo_evidence_fails():
    """Verifies that a public company with an exit history lacking public listing details fails."""
    invalid_payload = {
        "Nature of Company": "Public",
        "Exit Strategy/History": "Early stage private seed round completed.",
    }
    success, errors = validate_logical_consistency(invalid_payload)
    assert success is False
    assert any("Exit History lacks public listing / IPO references" in err for err in errors)


def test_unsubstantiated_concentration_risk_fails():
    """Verifies that flagging concentration risk without providing customer details fails."""
    invalid_payload = {
        "Customer Concentration Risk": "Yes",
        "Top Customers by Client Segments": None,
    }
    success, errors = validate_logical_consistency(invalid_payload)
    assert success is False
    assert any("Top Customers are missing" in err for err in errors)


def test_missing_office_locations_fails():
    """Verifies that declaring branch offices without specifying their locations fails."""
    invalid_payload = {
        "Number of Offices (beyond HQ)": 5,
        "Office Locations": "",
    }
    success, errors = validate_logical_consistency(invalid_payload)
    assert success is False
    assert any("Office Locations list is empty" in err for err in errors)


# =============================================================================
# tc_5_3 — Timeline / Chronological Consistency Validation
# =============================================================================

def extract_years_from_text(text: str) -> List[int]:
    """Extracts all 4-digit years (1800–2099) found within a string."""
    if not text:
        return []
    candidates = re.findall(r"\b(18\d{2}|19\d{2}|20\d{2})\b", text)
    return [int(yr) for yr in candidates]


def extract_dates_from_formatted_string(text: str) -> List[int]:
    """Extracts years specifically from YYYY-MM-DD formatted segments."""
    if not text:
        return []
    dates = re.findall(r"\b(18\d{2}|19\d{2}|20\d{2})-\d{2}-\d{2}\b", text)
    return [int(yr) for yr in dates]


def validate_timeline_consistency(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Enforces cross-parameter chronological consistency validations."""
    errors = []
    current_year = 2026

    try:
        inc_year = int(payload.get("Year of Incorporation", 0) or 0)
        if inc_year < 1800 or inc_year > current_year:
            errors.append(
                f"Anchor Error: Year of Incorporation ({inc_year}) must be a valid past year "
                f"(1800 to {current_year})."
            )
            return False, errors
    except ValueError:
        errors.append(
            f"Type Error: Year of Incorporation '{payload.get('Year of Incorporation')}' is not a valid integer."
        )
        return False, errors

    # 1. Recent Funding Rounds
    rounds_str = payload.get("Recent Funding Rounds", "")
    if rounds_str:
        for year in extract_dates_from_formatted_string(rounds_str):
            if year < inc_year:
                errors.append(
                    f"Chronological Error: Funding round in {year} occurs before Year of Incorporation ({inc_year})."
                )

    # 2. Recent News
    news_str = payload.get("Recent News", "")
    if news_str:
        news_years = extract_dates_from_formatted_string(news_str) or extract_years_from_text(news_str)
        for year in news_years:
            if year < inc_year:
                errors.append(
                    f"Chronological Error: News event in {year} occurs before Year of Incorporation ({inc_year})."
                )

    # 3. Exit Strategy/History
    exit_str = payload.get("Exit Strategy/History", "")
    if exit_str:
        for year in extract_years_from_text(exit_str):
            if year < inc_year:
                errors.append(
                    f"Chronological Error: Exit strategy event in {year} occurs before Year of Incorporation ({inc_year})."
                )

    # 4. Layoff History
    layoffs_str = payload.get("Layoff history", "")
    if layoffs_str:
        layoff_years = extract_dates_from_formatted_string(layoffs_str) or extract_years_from_text(layoffs_str)
        for year in layoff_years:
            if year < inc_year:
                errors.append(
                    f"Chronological Error: Layoff event in {year} occurs before Year of Incorporation ({inc_year})."
                )

    return len(errors) == 0, errors


# tc_5_3 Tests

def test_chronologically_consistent_record_passes():
    """Verifies that a record with consistent event timelines successfully passes validation."""
    valid_payload = {
        "Year of Incorporation": 2015,
        "Recent Funding Rounds": "2018-05-12 - Series A - $10M, 2026-03-10 - Series B - $15M",
        "Recent News": "2024-06-15 - Expanded into European markets, 2025-11-04 - Launched platform v2.0",
        "Exit Strategy/History": "Targeting IPO on NYSE by 2027",
        "Layoff history": "2022-10-12 - 5% of workforce impacted",
    }
    success, errors = validate_timeline_consistency(valid_payload)
    assert success is True
    assert not errors


def test_future_incorporation_year_rejected():
    """Verifies that a future incorporation year fails validation immediately."""
    invalid_payload = {"Year of Incorporation": 2028}
    success, errors = validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any("must be a valid past year" in err for err in errors)


def test_pre_incorporation_funding_rejected():
    """Verifies that funding transactions dated before company incorporation fail validation."""
    invalid_payload = {
        "Year of Incorporation": 2015,
        "Recent Funding Rounds": "2010-05-12 - Seed Round - $1M",
    }
    success, errors = validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any("Funding round in 2010 occurs before Year of Incorporation" in err for err in errors)


def test_pre_incorporation_news_rejected():
    """Verifies that news events dated before company incorporation fail validation."""
    invalid_payload = {
        "Year of Incorporation": 2020,
        "Recent News": "2015-11-04 - Company partnered with Tech Corp",
    }
    success, errors = validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any("News event in 2015 occurs before Year of Incorporation" in err for err in errors)


def test_pre_incorporation_layoffs_rejected():
    """Verifies that layoff events dated before company incorporation fail validation."""
    invalid_payload = {
        "Year of Incorporation": 2021,
        "Layoff history": "2018-05-10 - Restructuring led to 10% staff cut",
    }
    success, errors = validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any("Layoff event in 2018 occurs before Year of Incorporation" in err for err in errors)


# =============================================================================
# tc_5_4 — Field Format Validation
# =============================================================================

REGISTRY_PATTERNS = {
    "Company Phone Number": re.compile(r"^\+?[1-9]\d{1,14}$"),
    "Company Contact Email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
    "Website URL": re.compile(
        r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}"
        r"\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
    ),
    "Annual Revenues": re.compile(r"^\$?\d{1,3}(,\d{3})*(\.\d{2})?[KkMmBb]?$"),
    "Year of Incorporation": re.compile(r"^(19|20)\d{2}$"),
}


def validate_field_format(field_name: str, value: Any) -> bool:
    """Enforces absolute standard format validation based on parameter rules."""
    pattern = REGISTRY_PATTERNS.get(field_name)
    if not pattern:
        raise ValueError(f"No regex format mapped for field '{field_name}'.")
    if value is None:
        return False
    return pattern.match(str(value)) is not None


def validate_funding_rounds_date_format(rounds_str: str) -> bool:
    """Validates embedded date formats inside funding timeline lists (must be YYYY-MM-DD)."""
    if not rounds_str:
        return False
    records = [r.strip() for r in rounds_str.split(",") if r.strip()]
    for record in records:
        if not re.match(r"^(\d{4}-\d{2}-\d{2})\b", record):
            return False
    return True


# tc_5_4 Tests

@pytest.mark.parametrize("valid_phone", ["+14155552671", "+442079460192", "14155552671"])
def test_valid_phone_format(valid_phone):
    """Verifies that E.164 standard phone formats pass successfully."""
    assert validate_field_format("Company Phone Number", valid_phone) is True


@pytest.mark.parametrize("invalid_phone", ["+1-415-555-2671", "(415) 555-2671", "415-555-2671"])
def test_invalid_phone_rejected(invalid_phone):
    """Verifies that regional formatting with dashes, spaces, or parentheses is rejected."""
    assert validate_field_format("Company Phone Number", invalid_phone) is False


@pytest.mark.parametrize("valid_email", ["info@company.com", "contact_sales@sub.domain.org"])
def test_valid_email_format(valid_email):
    """Verifies that standard RFC 5322 emails pass successfully."""
    assert validate_field_format("Company Contact Email", valid_email) is True


@pytest.mark.parametrize("invalid_email", ["info#company.com", "info@company", "@domain.com"])
def test_invalid_email_rejected(invalid_email):
    """Verifies that malformed emails are rejected."""
    assert validate_field_format("Company Contact Email", invalid_email) is False


@pytest.mark.parametrize("valid_url", ["https://microsoft.com", "https://www.google.com/search?q=test"])
def test_valid_url_format(valid_url):
    """Verifies that standard HTTPS URLs pass successfully."""
    assert validate_field_format("Website URL", valid_url) is True


@pytest.mark.parametrize("invalid_url", ["http://microsoft@com", "https://invalid_url", "www.no-scheme.com"])
def test_invalid_url_rejected(invalid_url):
    """Verifies that malformed or non-secure URL configurations are rejected."""
    assert validate_field_format("Website URL", invalid_url) is False


@pytest.mark.parametrize("valid_revenue", ["$150,000,000", "150,000,000", "$150M", "1.5B"])
def test_valid_revenue_format(valid_revenue):
    """Verifies that standard currency and magnitude notations pass successfully."""
    assert validate_field_format("Annual Revenues", valid_revenue) is True


@pytest.mark.parametrize("invalid_revenue", ["150M USD", "USD 150,000,000", "Approx $150M"])
def test_invalid_revenue_rejected(invalid_revenue):
    """Verifies that informal non-standardized currency tags are rejected."""
    assert validate_field_format("Annual Revenues", invalid_revenue) is False


@pytest.mark.parametrize(
    "valid_rounds",
    [
        "2024-01-10 - Series A - $10M",
        "2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M",
    ],
)
def test_valid_funding_rounds_date_formatting(valid_rounds):
    """Verifies that embedded dates conforming strictly to YYYY-MM-DD pass validation."""
    assert validate_funding_rounds_date_format(valid_rounds) is True


@pytest.mark.parametrize(
    "invalid_rounds",
    [
        "01/10/2024 - Series A - $10M",
        "2024.01.10 - Series A - $10M",
    ],
)
def test_invalid_funding_rounds_date_rejected(invalid_rounds):
    """Verifies that non-standard date separators or formatting fail validation."""
    assert validate_funding_rounds_date_format(invalid_rounds) is False


# =============================================================================
# tc_5_5 — Cross-Parameter Coherence Validation
# =============================================================================

def parse_percent_to_float(val: Any) -> float:
    """Parses percentage strings (e.g. '15.5%', '5%') into raw floats."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    clean_str = str(val).replace("%", "").strip()
    try:
        return float(clean_str)
    except ValueError:
        return 0.0


def parse_employee_size_to_int(val: Any) -> int:
    """Parses employee size strings into a representative integer (uses max bound of ranges)."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    clean_str = str(val).replace(",", "").replace(" ", "").strip()
    if "+" in clean_str:
        clean_str = clean_str.replace("+", "")
    if "-" in clean_str:
        parts = clean_str.split("-")
        try:
            return int(parts[1])
        except (IndexError, ValueError):
            pass
    try:
        return int(clean_str)
    except ValueError:
        return 0


def validate_cross_parameter_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Performs holistic record-level validations to catch contradictory metric combinations."""
    errors = []

    # 1. Footprint Audit: Employee Size vs Number of Offices
    headcount = parse_employee_size_to_int(payload.get("Employee Size"))
    try:
        office_count = int(payload.get("Number of Offices (beyond HQ)", 0) or 0)
        if 0 < headcount < 10 and office_count > 5:
            errors.append(
                f"Operational Contradiction: Employee count is very small ({headcount}), "
                f"but company claims {office_count} offices beyond HQ. This ratio is highly anomalous."
            )
    except ValueError:
        pass

    # 2. Customer Success Audit: NPS vs Churn Rate
    nps = payload.get("Net Promoter Score (NPS)")
    churn_rate = parse_percent_to_float(payload.get("Churn Rate"))
    if nps is not None and churn_rate > 0:
        try:
            nps_val = int(nps)
            if nps_val >= 75 and churn_rate >= 30.0:
                errors.append(
                    f"Loyalty Contradiction: Ingested Net Promoter Score is exceptionally high ({nps_val}), "
                    f"but Churn Rate is recorded as extremely high ({churn_rate}%). "
                    f"These metrics contradict each other."
                )
        except ValueError:
            pass

    # 3. Talent Audit: Turnover vs Hiring Velocity
    turnover = parse_percent_to_float(payload.get("Employee Turnover"))
    hiring_velocity = str(payload.get("Hiring Velocity", "")).lower()
    if turnover >= 45.0 and ("low" in hiring_velocity or "none" in hiring_velocity or "0" in hiring_velocity):
        errors.append(
            f"Talent Contradiction: Employee Turnover is extremely high ({turnover}%), "
            f"but Hiring Velocity is recorded as '{payload.get('Hiring Velocity')}'. "
            f"This combination indicates rapid workforce depletion without replacement."
        )

    return len(errors) == 0, errors


# tc_5_5 Tests

def test_coherent_metrics_pass_audit():
    """Verifies that internally consistent, logically coherent records pass validation."""
    coherent_payload = {
        "Employee Size": "10,000+",
        "Number of Offices (beyond HQ)": 25,
        "Net Promoter Score (NPS)": 80,
        "Churn Rate": "4%",
        "Employee Turnover": "12%",
        "Hiring Velocity": "High",
    }
    success, errors = validate_cross_parameter_coherence(coherent_payload)
    assert success is True
    assert not errors


def test_anomalous_headcount_to_office_ratio_fails():
    """Verifies that claiming a tiny headcount with a massive branch office footprint fails."""
    anomalous_payload = {
        "Employee Size": "1-5",
        "Number of Offices (beyond HQ)": 12,
    }
    success, errors = validate_cross_parameter_coherence(anomalous_payload)
    assert success is False
    assert any("Operational Contradiction" in err for err in errors)


def test_contradictory_nps_and_churn_fails():
    """Verifies that contradictory high customer satisfaction and high churn fail validation."""
    contradictory_payload = {
        "Net Promoter Score (NPS)": 85,
        "Churn Rate": "35%",
    }
    success, errors = validate_cross_parameter_coherence(contradictory_payload)
    assert success is False
    assert any("Loyalty Contradiction" in err for err in errors)


def test_unsupported_high_turnover_fails():
    """Verifies that high employee loss paired with zero hiring velocity triggers an alarm."""
    contradictory_payload = {
        "Employee Turnover": "50%",
        "Hiring Velocity": "None / Zero open roles",
    }
    success, errors = validate_cross_parameter_coherence(contradictory_payload)
    assert success is False
    assert any("Talent Contradiction" in err for err in errors)