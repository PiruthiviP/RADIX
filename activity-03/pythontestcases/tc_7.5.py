import re
import datetime
import pytest
from typing import Dict, Any, List, Tuple

# Current system time checkpoint: May 22, 2026
CURRENT_SYSTEM_DATE = datetime.date(2026, 5, 22)

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


# --- Pytest Tests ---

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