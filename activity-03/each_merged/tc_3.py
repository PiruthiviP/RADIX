"""
Combined Test Suite: tc_3_1 through tc_3_5
Covers:
  - Factual correctness validation (tc_3_1)
  - Temporal accuracy validation (tc_3_2)
  - Format/precision validation (tc_3_3)
  - Cross-field consistency validation (tc_3_4)
  - Source lineage/attribution validation (tc_3_5)
"""

import re
import datetime
import pytest
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# tc_3_1 — Factual Correctness Validation
# =============================================================================

GROUND_TRUTH_REGISTRY = {
    "microsoft corporation": {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": 1975,
        "CEO Name": "Satya Nadella",
        "Website URL": "https://www.microsoft.com",
        "Employee Count": 221000,
        "Annual Revenues": 245000000000.0,
    },
    "apple inc.": {
        "Company Name": "Apple Inc.",
        "Year of Incorporation": 1976,
        "CEO Name": "Tim Cook",
        "Website URL": "https://www.apple.com",
        "Employee Count": 164000,
        "Annual Revenues": 383000000000.0,
    },
}


def parse_employee_range(range_str: str, exact_count: int) -> bool:
    """Validates if an exact numeric headcount falls within an ingested range/bucket."""
    if not range_str:
        return False
    clean_str = range_str.replace(",", "").replace(" ", "")
    if "+" in clean_str:
        min_val = int(clean_str.replace("+", ""))
        return exact_count >= min_val
    if "-" in clean_str:
        parts = clean_str.split("-")
        if len(parts) == 2:
            min_val = int(parts[0])
            max_val = int(parts[1])
            return min_val <= exact_count <= max_val
    return False


def validate_factual_correctness(ingested_record: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """Holistically validates the ingested company record against ground-truth data."""
    company_key = str(ingested_record.get("Company Name", "")).strip().lower()
    if not company_key or company_key not in GROUND_TRUTH_REGISTRY:
        return False, 0.0, [
            f"Validation aborted: Company '{ingested_record.get('Company Name')}' not found in ground-truth registry."
        ]

    truth = GROUND_TRUTH_REGISTRY[company_key]
    errors = []
    checks_passed = 0
    total_checks = 6

    if ingested_record.get("Company Name") == truth["Company Name"]:
        checks_passed += 1
    else:
        errors.append(
            f"Factual Mismatch [Company Name]: Ingested '{ingested_record.get('Company Name')}', "
            f"Ground Truth '{truth['Company Name']}'"
        )

    try:
        ingested_year = int(ingested_record.get("Year of Incorporation", 0))
        if ingested_year == truth["Year of Incorporation"]:
            checks_passed += 1
        else:
            errors.append(
                f"Factual Mismatch [Year of Incorporation]: Ingested {ingested_year}, "
                f"Ground Truth {truth['Year of Incorporation']}"
            )
    except ValueError:
        errors.append(
            f"Type Mismatch [Year of Incorporation]: Value '{ingested_record.get('Year of Incorporation')}' must be integer."
        )

    if ingested_record.get("CEO Name") == truth["CEO Name"]:
        checks_passed += 1
    else:
        errors.append(
            f"Factual Mismatch [CEO Name]: Ingested '{ingested_record.get('CEO Name')}', "
            f"Ground Truth '{truth['CEO Name']}'"
        )

    if ingested_record.get("Website URL") == truth["Website URL"]:
        checks_passed += 1
    else:
        errors.append(
            f"Factual Mismatch [Website URL]: Ingested '{ingested_record.get('Website URL')}', "
            f"Ground Truth '{truth['Website URL']}'"
        )

    ingested_range = ingested_record.get("Employee Size")
    truth_count = truth["Employee Count"]
    if parse_employee_range(ingested_range, truth_count):
        checks_passed += 1
    else:
        errors.append(
            f"Factual Mismatch [Employee Size]: Exact count {truth_count} falls outside ingested range '{ingested_range}'"
        )

    try:
        ingested_rev_raw = str(ingested_record.get("Annual Revenues", "")).replace("$", "").replace(",", "")
        multiplier = 1.0
        if "B" in ingested_rev_raw:
            multiplier = 1_000_000_000.0
            ingested_rev_raw = ingested_rev_raw.replace("B", "")
        elif "M" in ingested_rev_raw:
            multiplier = 1_000_000.0
            ingested_rev_raw = ingested_rev_raw.replace("M", "")
        ingested_rev = float(ingested_rev_raw) * multiplier
        truth_rev = truth["Annual Revenues"]
        variance = abs(ingested_rev - truth_rev) / truth_rev
        if variance <= 0.05:
            checks_passed += 1
        else:
            errors.append(
                f"Factual Mismatch [Annual Revenues]: Ingested {ingested_rev}, "
                f"Ground Truth {truth_rev} (Exceeded 5% variance)"
            )
    except Exception as e:
        errors.append(
            f"Parser Mismatch [Annual Revenues]: Could not reconcile '{ingested_record.get('Annual Revenues')}' due to error: {e}"
        )

    accuracy_score = round((checks_passed / total_checks) * 100, 2)
    success = accuracy_score == 100.0
    return success, accuracy_score, errors


# tc_3_1 Tests

def test_accurate_profile_validation_success():
    """Verifies that an ingested profile that factually matches ground truth passes with a 100% score."""
    accurate_payload = {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": 1975,
        "CEO Name": "Satya Nadella",
        "Website URL": "https://www.microsoft.com",
        "Employee Size": "10,000+",
        "Annual Revenues": "$245B",
    }
    success, score, errors = validate_factual_correctness(accurate_payload)
    assert success is True
    assert score == 100.0
    assert not errors


def test_mismatched_incorporation_year_fails_validation():
    """Verifies that a factual mismatch on incorporation year reduces score and returns errors."""
    inaccurate_payload = {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": 1999,
        "CEO Name": "Satya Nadella",
        "Website URL": "https://www.microsoft.com",
        "Employee Size": "10,000+",
        "Annual Revenues": "$245B",
    }
    success, score, errors = validate_factual_correctness(inaccurate_payload)
    assert success is False
    assert score == 83.33
    assert any("Year of Incorporation" in err for err in errors)


def test_employee_size_range_out_of_bounds_fails():
    """Verifies that if the ground truth headcount does not fall within the range boundary, validation fails."""
    out_of_bounds_payload = {
        "Company Name": "Apple Inc.",
        "Year of Incorporation": 1976,
        "CEO Name": "Tim Cook",
        "Website URL": "https://www.apple.com",
        "Employee Size": "100-500",
        "Annual Revenues": "$383B",
    }
    success, score, errors = validate_factual_correctness(out_of_bounds_payload)
    assert success is False
    assert score == 83.33
    assert any("Employee Size" in err for err in errors)


def test_revenue_estimation_variance_fails_beyond_threshold():
    """Verifies that if estimated revenue exceeds the acceptable 5% variance threshold, validation fails."""
    inaccurate_financials_payload = {
        "Company Name": "Apple Inc.",
        "Year of Incorporation": 1976,
        "CEO Name": "Tim Cook",
        "Website URL": "https://www.apple.com",
        "Employee Size": "10,000+",
        "Annual Revenues": "$200B",
    }
    success, score, errors = validate_factual_correctness(inaccurate_financials_payload)
    assert success is False
    assert score == 83.33
    assert any("Annual Revenues" in err for err in errors)


# =============================================================================
# tc_3_2 — Temporal Accuracy Validation
# =============================================================================

LIVE_GROUND_TRUTH = {
    "microsoft": {
        "current_ceo": "Satya Nadella",
        "former_ceos": {"Bill Gates", "Steve Ballmer"},
        "latest_funding_round_date": "2026-01-15",
        "total_capital_raised": 13000000000.0,
        "employee_count": 221000,
    },
    "mockcorp": {
        "current_ceo": "Jane Doe",
        "former_ceos": {"John Smith"},
        "latest_funding_round_date": "2026-03-10",
        "total_capital_raised": 15000000.0,
        "employee_count": 450,
    },
}


def validate_ceo_temporal_accuracy(company_key: str, ingested_ceo: str) -> Tuple[bool, str]:
    """Ensures that the ingested CEO name represents the active CEO, not a predecessor."""
    truth = LIVE_GROUND_TRUTH.get(company_key.lower())
    if not truth:
        return False, "Company not found in registry."
    if ingested_ceo == truth["current_ceo"]:
        return True, "CEO name is current and accurate."
    elif ingested_ceo in truth["former_ceos"]:
        return False, (
            f"Obsolete Data: '{ingested_ceo}' is a former CEO. "
            f"Current active CEO is '{truth['current_ceo']}'."
        )
    return False, f"Factual error: '{ingested_ceo}' is not registered as an active or former CEO."


def validate_news_temporal_bounds(news_list: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
    """Enforces the trailing 12-24 month window constraint."""
    errors = []
    current_date = datetime.date(2026, 5, 22)
    boundary_date = current_date - datetime.timedelta(days=2 * 365)

    for item in news_list:
        date_str = item.get("date", "")
        try:
            event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if event_date < boundary_date:
                errors.append(
                    f"Stale News: Event '{item.get('headline')}' on {date_str} is older than "
                    f"the 2-year boundary ({boundary_date})."
                )
        except ValueError:
            errors.append(
                f"Format error: Invalid date format '{date_str}' for event '{item.get('headline')}'. Use YYYY-MM-DD."
            )

    return len(errors) == 0, errors


def validate_total_capital_raised_reconciliation(
    company_key: str, ingested_total: float, ingested_rounds: List[Dict[str, Any]]
) -> Tuple[bool, str]:
    """Ensures Total Capital Raised is up-to-date and matches the cumulative sum of all documented rounds."""
    truth = LIVE_GROUND_TRUTH.get(company_key.lower())
    if not truth:
        return False, "Company not found in registry."

    calculated_sum = sum(float(r.get("amount", 0)) for r in ingested_rounds)

    if ingested_total < calculated_sum:
        return False, (
            f"Outdated Financials: Ingested Total Capital ({ingested_total}) is less than "
            f"the cumulative sum of logged rounds ({calculated_sum})."
        )

    if abs(ingested_total - truth["total_capital_raised"]) > 0.01:
        return False, (
            f"Outdated Financials: Ingested Total ({ingested_total}) does not align with "
            f"the current live registry total ({truth['total_capital_raised']})."
        )

    return True, "Financial reconciliation passed."


# tc_3_2 Tests

def test_current_ceo_passes_validation():
    """Verifies that the current CEO successfully passes the temporal check."""
    success, msg = validate_ceo_temporal_accuracy("microsoft", "Satya Nadella")
    assert success is True
    assert "current and accurate" in msg


def test_former_ceo_fails_validation():
    """Verifies that a former CEO is caught and rejected by the temporal database checker."""
    success, msg = validate_ceo_temporal_accuracy("microsoft", "Steve Ballmer")
    assert success is False
    assert "Obsolete Data" in msg
    assert "Steve Ballmer" in msg


def test_news_within_trailing_two_years_passes():
    """Verifies that news events dated within the 2-year boundary pass validation."""
    valid_news = [
        {"date": "2025-10-15", "headline": "Acquired Cloud Platform LLC"},
        {"date": "2024-06-01", "headline": "Launched Generative AI Integration"},
    ]
    success, errors = validate_news_temporal_bounds(valid_news)
    assert success is True
    assert not errors


def test_stale_news_older_than_two_years_fails():
    """Verifies that news events older than the 2-year boundary are rejected as obsolete."""
    stale_news = [
        {"date": "2023-01-10", "headline": "Initial Seed Round Closed"},
        {"date": "2025-05-12", "headline": "Series A Funding Completed"},
    ]
    success, errors = validate_news_temporal_bounds(stale_news)
    assert success is False
    assert any("Stale News" in err for err in errors)


def test_outdated_total_capital_raised_fails():
    """Verifies that out-of-date Total Capital Raised entries that lag behind documented rounds fail."""
    ingested_rounds = [
        {"date": "2018-05-12", "amount": 5000000.0},
        {"date": "2026-03-10", "amount": 10000000.0},
    ]
    stale_total = 5000000.0
    success, msg = validate_total_capital_raised_reconciliation("mockcorp", stale_total, ingested_rounds)
    assert success is False
    assert "Outdated Financials" in msg


# =============================================================================
# tc_3_3 — Format & Precision Validation
# =============================================================================

RATINGS_GD_RE = re.compile(r"^[1-5](\.\d)?$")
RATINGS_WEB_RE = re.compile(r"^(10(\.0)?|[0-9](\.\d)?)$")
EMPLOYEE_SIZE_RE = re.compile(r"^(\d+|\d+-\d+)$")


def parse_currency_string_to_float(val: str) -> Optional[float]:
    """Standardizes and parses financial strings into raw floats."""
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
    """Validates decimal rating string precision."""
    if not val:
        return False, None
    regex = RATINGS_GD_RE if rating_type == "Glassdoor" else RATINGS_WEB_RE
    if not regex.match(val):
        return False, None
    try:
        return True, float(val)
    except ValueError:
        return False, None


# tc_3_3 Tests

@pytest.mark.parametrize(
    "revenue_str, expected_float",
    [
        ("$50.3B", 50300000000.0),
        ("$50,300M", 50300000000.0),
        ("$50B", 50000000000.0),
        ("$500K", 500000.0),
    ],
)
def test_financial_numerical_precision_parsing(revenue_str, expected_float):
    """Verifies that various financial string representations resolve to precise float equivalents."""
    assert parse_currency_string_to_float(revenue_str) == expected_float


@pytest.mark.parametrize("valid_size", ["10000", "1000-5000"])
def test_valid_employee_size_formats(valid_size):
    """Verifies that exact integers or hyphenated ranges pass headcount boundary checks."""
    assert validate_employee_size(valid_size) is True


@pytest.mark.parametrize("invalid_size", ["10K", "~10000", "10,000+"])
def test_invalid_employee_size_formats(invalid_size):
    """Verifies that informal modifiers or alphabetical multipliers in headcounts fail."""
    assert validate_employee_size(invalid_size) is False


@pytest.mark.parametrize(
    "rating_input, expected_float",
    [
        ("4.2", 4.2),
        ("4", 4.0),
    ],
)
def test_valid_ratings_precision(rating_input, expected_float):
    """Verifies that valid single-decimal ratings are successfully validated and parsed."""
    success, parsed_val = validate_and_parse_rating(rating_input, rating_type="Glassdoor")
    assert success is True
    assert parsed_val == expected_float


@pytest.mark.parametrize("invalid_rating", ["4.20", "4.25", "5.1"])
def test_invalid_ratings_rejected(invalid_rating):
    """Verifies that bloated precision ratings or out-of-bounds metrics are strictly rejected."""
    success, parsed_val = validate_and_parse_rating(invalid_rating, rating_type="Glassdoor")
    assert success is False
    assert parsed_val is None


@pytest.mark.parametrize(
    "web_rating_input, expected_float",
    [
        ("8.5", 8.5),
        ("10", 10.0),
        ("10.0", 10.0),
    ],
)
def test_website_ratings_precision(web_rating_input, expected_float):
    """Verifies that website ratings (1.0–10.0 scale) are successfully validated and parsed."""
    success, parsed_val = validate_and_parse_rating(web_rating_input, rating_type="Website")
    assert success is True
    assert parsed_val == expected_float


def test_invalid_website_ratings_rejected():
    """Verifies that out-of-bounds or bloated website ratings are rejected."""
    success, parsed_val = validate_and_parse_rating("11.2", rating_type="Website")
    assert success is False


# =============================================================================
# tc_3_4 — Cross-Field Consistency Validation
# =============================================================================

def parse_money(val: Any) -> float:
    """Parses money strings (e.g. '$10M', '$1.5B') into raw floats."""
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


def validate_cross_field_consistency(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Enforces cross-field mathematical and logical accuracy validations."""
    errors = []

    # 1. Total Capital Raised vs Recent Funding Rounds
    total_raised = parse_money(payload.get("Total Capital Raised"))
    rounds_str = payload.get("Recent Funding Rounds", "")
    if rounds_str and total_raised > 0:
        rounds_amounts = re.findall(r"\$\s*([\d\.]+)\s*([KkMmBb]?)", rounds_str)
        sum_of_rounds = sum(parse_money(f"${amt}{tag}") for amt, tag in rounds_amounts)
        if abs(total_raised - sum_of_rounds) > 0.01:
            errors.append(
                f"Consistency Error: Total Capital Raised ({total_raised}) does not equal "
                f"the sum of Recent Funding Rounds ({sum_of_rounds})."
            )

    # 2. CAC & CLV vs CAC:LTV Ratio
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
                    f"Consistency Error: Ingested CAC:LTV Ratio ({ingested_ratio}) does not match "
                    f"the calculated quotient CLV/CAC ({expected_ratio})."
                )
        else:
            errors.append(f"Format Error: Ingested CAC:LTV Ratio '{ratio_str}' does not match standard ratio formats.")

    # 3. Burn Rate vs Runway vs Total Capital Raised
    burn_monthly = parse_money(payload.get("Burn Rate"))
    total_capital = parse_money(payload.get("Total Capital Raised"))
    runway_str = str(payload.get("Runway", ""))
    if burn_monthly > 0 and total_capital > 0 and runway_str:
        try:
            ingested_runway = float(runway_str)
            expected_runway = round(total_capital / burn_monthly, 2)
            if abs(ingested_runway - expected_runway) > 0.1:
                errors.append(
                    f"Consistency Error: Ingested Runway ({ingested_runway}) does not match "
                    f"calculated Runway Capital/Burn ({expected_runway})."
                )
        except ValueError:
            pass

    # 4. Profitability Status vs Annual Profits
    annual_profits = parse_money(payload.get("Annual Profits"))
    prof_status = payload.get("Profitability Status")
    if prof_status:
        if annual_profits > 0 and prof_status != "Profitable":
            errors.append(
                f"Consistency Error: Profitability Status '{prof_status}' does not match "
                f"positive Annual Profits ({annual_profits})."
            )
        elif annual_profits < 0 and prof_status != "Loss-making":
            errors.append(
                f"Consistency Error: Profitability Status '{prof_status}' does not match "
                f"negative Annual Profits ({annual_profits})."
            )
        elif annual_profits == 0 and prof_status != "Break-even":
            errors.append(
                f"Consistency Error: Profitability Status '{prof_status}' does not match zero Annual Profits."
            )

    # 5. Office Locations vs Countries Operating In
    countries_operating = [
        c.strip().upper()
        for c in str(payload.get("Countries Operating In", "")).split(",")
        if c.strip()
    ]
    offices_str = str(payload.get("Office Locations", ""))
    if countries_operating and offices_str:
        extracted_countries = re.findall(r"\(\s*([A-Za-z]{2,})\s*\)", offices_str)
        for country in extracted_countries:
            if country.upper() not in countries_operating:
                errors.append(
                    f"Consistency Error: Office Location country '({country})' is not registered "
                    f"in Countries Operating In ({countries_operating})."
                )

    return len(errors) == 0, errors


# tc_3_4 Tests

def test_consistent_record_passes_validation():
    """Verifies that a mathematically and structurally consistent profile passes validation."""
    valid_payload = {
        "Total Capital Raised": "$25M",
        "Recent Funding Rounds": "2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M",
        "Customer Acquisition Cost (CAC)": "$100",
        "Customer Lifetime Value (CLV)": "$300",
        "CAC:LTV Ratio": "3:1",
        "Burn Rate": "$50K",
        "Runway": "500",
        "Annual Profits": "-$2M",
        "Profitability Status": "Loss-making",
        "Countries Operating In": "US, UK",
        "Office Locations": "New York (US), London (UK)",
    }
    success, errors = validate_cross_field_consistency(valid_payload)
    assert success is True
    assert not errors


def test_mismatched_funding_rounds_fails():
    """Verifies that if the sum of logged rounds does not match Total Capital Raised, validation fails."""
    inconsistent_payload = {
        "Total Capital Raised": "$30M",
        "Recent Funding Rounds": "2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M",
    }
    success, errors = validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any("Total Capital Raised" in err for err in errors)


def test_mismatched_cac_ltv_ratio_fails():
    """Verifies that an incorrect CAC:LTV quotient fails validation."""
    inconsistent_payload = {
        "Customer Acquisition Cost (CAC)": 100,
        "Customer Lifetime Value (CLV)": 300,
        "CAC:LTV Ratio": "5:1",
    }
    success, errors = validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any("CAC:LTV Ratio" in err for err in errors)


def test_mismatched_profitability_status_fails():
    """Verifies that if profitability status disagrees with annual profit polarity, validation fails."""
    inconsistent_payload = {
        "Annual Profits": 1500000.0,
        "Profitability Status": "Loss-making",
    }
    success, errors = validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any("Profitability Status" in err for err in errors)


def test_mismatched_office_locations_country_fails():
    """Verifies that having an office in a country not listed in Countries Operating In fails."""
    inconsistent_payload = {
        "Countries Operating In": "US",
        "Office Locations": "New York (US), London (UK)",
    }
    success, errors = validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any("Office Location country" in err for err in errors)


# =============================================================================
# tc_3_5 — Source Lineage & Attribution Validation
# =============================================================================

ALLOWED_SOURCES_BY_FIELD = {
    "Company Name": ["Company Registry", "SEC Filings", "Government Database"],
    "Logo": ["Official Website", "LinkedIn"],
    "Employee Size": ["LinkedIn", "HR Tools", "Crunchbase"],
    "Annual Revenues": ["SEC Filings", "Annual Reports", "Company Registry"],
    "Website URL": ["Official Registry", "Company Registry"],
    "Recent News": ["PR Newswire", "Crunchbase", "Official Press Releases"],
}

CREDIBILITY_BLACKLIST = ["random-blog.com", "leakforums.net", "wikipedia.org", "blogspot.com"]


def validate_lineage_attribution(record_payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates the source attribution and lineage of the company record."""
    errors = []
    current_date = datetime.date(2026, 5, 22)
    min_acceptable_date = current_date - datetime.timedelta(days=365)

    for field_name, allowed_origins in ALLOWED_SOURCES_BY_FIELD.items():
        field_value = record_payload.get(field_name)
        if field_value is not None:
            attribution = record_payload.get(f"_attribution_{field_name}")
            if not attribution:
                errors.append(
                    f"Lineage Error: Field '{field_name}' is populated but lacks an "
                    f"'_attribution_{field_name}' block."
                )
                continue

            source_type = attribution.get("source_type")
            source_url = attribution.get("source_url", "")
            timestamp_str = attribution.get("timestamp", "")

            if source_type not in allowed_origins:
                errors.append(
                    f"Credibility Error: Field '{field_name}' cites source '{source_type}'. "
                    f"Allowed sources are: {allowed_origins}."
                )

            if any(bl in source_url.lower() for bl in CREDIBILITY_BLACKLIST):
                errors.append(
                    f"Credibility Error: Field '{field_name}' cites a blacklisted untrusted domain: '{source_url}'."
                )

            try:
                source_date = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d").date()
                if source_date > current_date:
                    errors.append(
                        f"Temporal Lineage Error: Field '{field_name}' has a future source timestamp: '{timestamp_str}'."
                    )
                elif source_date < min_acceptable_date:
                    errors.append(
                        f"Temporal Lineage Error: Field '{field_name}' has an expired source timestamp: "
                        f"'{timestamp_str}' (older than {min_acceptable_date})."
                    )
            except ValueError:
                errors.append(
                    f"Lineage Format Error: Field '{field_name}' has an invalid timestamp format "
                    f"'{timestamp_str}'. Use YYYY-MM-DD."
                )

    return len(errors) == 0, errors


# tc_3_5 Tests

def test_valid_lineage_profile_passes():
    """Verifies that a fully traceable, credible profile record passes validation."""
    valid_record = {
        "Company Name": "Microsoft Corporation",
        "_attribution_Company Name": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov/edgar/searchedgar/companysearch",
            "timestamp": "2026-04-15",
        },
        "Logo": "https://logo.com/ms",
        "_attribution_Logo": {
            "source_type": "LinkedIn",
            "source_url": "https://www.linkedin.com/company/microsoft",
            "timestamp": "2026-05-10",
        },
        "Annual Revenues": "$245B",
        "_attribution_Annual Revenues": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov/edgar/searchedgar/companysearch",
            "timestamp": "2026-04-15",
        },
    }
    success, errors = validate_lineage_attribution(valid_record)
    assert success is True
    assert not errors


def test_missing_attribution_block_fails():
    """Verifies that populating a field without its source attribution fails validation."""
    invalid_record = {"Company Name": "Microsoft Corporation"}
    success, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("lacks an '_attribution_Company Name' block" in err for err in errors)


def test_untrusted_blacklisted_source_fails():
    """Verifies that citing a blacklisted domain for a metric fails validation."""
    invalid_record = {
        "Company Name": "Microsoft Corporation",
        "_attribution_Company Name": {
            "source_type": "SEC Filings",
            "source_url": "https://random-blog.com/leak/microsoft-details",
            "timestamp": "2026-04-15",
        },
    }
    success, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("blacklisted untrusted domain" in err for err in errors)


def test_unpermitted_source_type_fails():
    """Verifies that using an unpermitted source type for a specific parameter fails validation."""
    invalid_record = {
        "Annual Revenues": "$245B",
        "_attribution_Annual Revenues": {
            "source_type": "LinkedIn",
            "source_url": "https://www.linkedin.com/company/microsoft",
            "timestamp": "2026-04-15",
        },
    }
    success, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("Allowed sources are" in err for err in errors)


def test_future_attribution_timestamp_fails():
    """Verifies that an attribution timestamp set in the future is caught and rejected."""
    invalid_record = {
        "Company Name": "Microsoft Corporation",
        "_attribution_Company Name": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov/edgar",
            "timestamp": "2027-10-12",
        },
    }
    success, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("future source timestamp" in err for err in errors)