import re
import pytest
from typing import Dict, Any, List, Tuple

def extract_years_from_text(text: str) -> List[int]:
    """Extracts all 4-digit years (from 1800 to 2099) found within a string."""
    if not text:
        return []
    # Find all 4-digit numbers
    candidates = re.findall(r"\b(18\d{2}|19\d{2}|20\d{2})\b", text)
    return [int(yr) for yr in candidates]

def extract_dates_from_formatted_string(text: str) -> List[int]:
    """Extracts years specifically from YYYY-MM-DD formatted segments."""
    if not text:
        return []
    dates = re.findall(r"\b(18\d{2}|19\d{2}|20\d{2})-\d{2}-\d{2}\b", text)
    return [int(yr) for yr in dates]

def validate_timeline_consistency(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces cross-parameter chronological consistency validations:
    1. Rejects Year of Incorporation values that exist in the future (beyond May 22, 2026).
    2. Verifies that all funding round years are >= Year of Incorporation.
    3. Verifies that all news event years are >= Year of Incorporation.
    4. Verifies that all exit strategy event years are >= Year of Incorporation.
    5. Verifies that all layoff history years are >= Year of Incorporation.
    """
    errors = []
    current_year = 2026

    # Parse and validate baseline Year of Incorporation
    try:
        inc_year = int(payload.get("Year of Incorporation", 0) or 0)
        if inc_year < 1800 or inc_year > current_year:
            errors.append(f"Anchor Error: Year of Incorporation ({inc_year}) must be a valid past year (1800 to {current_year}).")
            return False, errors
    except ValueError:
        errors.append(f"Type Error: Year of Incorporation '{payload.get('Year of Incorporation')}' is not a valid integer.")
        return False, errors

    # 1. Validate Recent Funding Rounds Timeline
    rounds_str = payload.get("Recent Funding Rounds", "")
    if rounds_str:
        funding_years = extract_dates_from_formatted_string(rounds_str)
        for year in funding_years:
            if year < inc_year:
                errors.append(f"Chronological Error: Funding round in {year} occurs before Year of Incorporation ({inc_year}).")

    # 2. Validate Recent News Timeline
    news_str = payload.get("Recent News", "")
    if news_str:
        # Check standard date formats first
        news_years = extract_dates_from_formatted_string(news_str)
        # If no YYYY-MM-DD pattern, fall back to general 4-digit years in news text
        if not news_years:
            news_years = extract_years_from_text(news_str)
            
        for year in news_years:
            if year < inc_year:
                errors.append(f"Chronological Error: News event in {year} occurs before Year of Incorporation ({inc_year}).")

    # 3. Validate Exit Strategy/History Timeline
    exit_str = payload.get("Exit Strategy/History", "")
    if exit_str:
        exit_years = extract_years_from_text(exit_str)
        for year in exit_years:
            if year < inc_year:
                errors.append(f"Chronological Error: Exit strategy event in {year} occurs before Year of Incorporation ({inc_year}).")

    # 4. Validate Layoff History Timeline
    layoffs_str = payload.get("Layoff history", "")
    if layoffs_str:
        layoff_years = extract_dates_from_formatted_string(layoffs_str)
        if not layoff_years:
            layoff_years = extract_years_from_text(layoffs_str)
            
        for year in layoff_years:
            if year < inc_year:
                errors.append(f"Chronological Error: Layoff event in {year} occurs before Year of Incorporation ({inc_year}).")

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_chronologically_consistent_record_passes():
    """Verifies that a record with consistent event timelines successfully passes validation."""
    valid_payload = {
        "Year of Incorporation": 2015,
        "Recent Funding Rounds": "2018-05-12 - Series A - $10M, 2026-03-10 - Series B - $15M",
        "Recent News": "2024-06-15 - Expanded into European markets, 2025-11-04 - Launched platform v2.0",
        "Exit Strategy/History": "Targeting IPO on NYSE by 2027",
        "Layoff history": "2022-10-12 - 5% of workforce impacted"
    }
    success, errors = validate_timeline_consistency(valid_payload)
    assert success is True
    assert not errors

def test_future_incorporation_year_rejected():
    """Verifies that a future incorporation year fails validation immediately."""
    invalid_payload = {
        "Year of Incorporation": 2028  # Future year (relative to May 2026)
    }
    success, errors = validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any("must be a valid past year" in err for err in errors)

def test_pre_incorporation_funding_rejected():
    """Verifies that funding transactions dated before company incorporation fail validation."""
    invalid_payload = {
        "Year of Incorporation": 2015,
        "Recent Funding Rounds": "2010-05-12 - Seed Round - $1M"  # 2010 < 2015
    }
    success, errors = validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any("Funding round in 2010 occurs before Year of Incorporation" in err for err in errors)

def test_pre_incorporation_news_rejected():
    """Verifies that news events dated before company incorporation fail validation."""
    invalid_payload = {
        "Year of Incorporation": 2020,
        "Recent News": "2015-11-04 - Company partnered with Tech Corp"  # 2015 < 2020
    }
    success, errors = validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any("News event in 2015 occurs before Year of Incorporation" in err for err in errors)

def test_pre_incorporation_layoffs_rejected():
    """Verifies that layoff events dated before company incorporation fail validation."""
    invalid_payload = {
        "Year of Incorporation": 2021,
        "Layoff history": "2018-05-10 - Restructuring led to 10% staff cut"  # 2018 < 2021
    }
    success, errors = validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any("Layoff event in 2018 occurs before Year of Incorporation" in err for err in errors)