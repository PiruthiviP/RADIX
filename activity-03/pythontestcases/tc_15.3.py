import re
from datetime import datetime
import pytest
from typing import Dict, Any, List

# Core system baseline date context (Friday, May 22, 2026)
SYSTEM_BASELINE_DATE = datetime(2026, 5, 22)


def extract_dates_from_string(text: str) -> List[datetime]:
    """
    Extracts YYYY-MM-DD or YYYY-MM dates from a text string.
    """
    # Regex to find YYYY-MM-DD
    full_dates = re.findall(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    extracted = []
    for y, m, d in full_dates:
        try:
            extracted.append(datetime(int(y), int(m), int(d)))
        except ValueError:
            pass
            
    # Regex to find YYYY-MM (if full date is missing)
    month_dates = re.findall(r"\b(\d{4})-(\d{2})\b", text)
    for y, m in month_dates:
        # Avoid duplicate counting of matched full dates
        if not any(d.year == int(y) and d.month == int(m) for d in extracted):
            try:
                extracted.append(datetime(int(y), int(m), 1))
            except ValueError:
                pass
                
    return extracted


def calculate_months_difference(date_a: datetime, date_b: datetime) -> int:
    """
    Calculates the absolute difference in months between two datetime objects.
    """
    return abs((date_a.year - date_b.year) * 12 + date_a.month - date_b.month)


def validate_record_recency(record: Dict[str, Any]) -> bool:
    """
    Audits the recency of the company profile [1].
    Ensures that volatile records with stale updates (>12 months) cannot carry
    a 'High' confidence level and must trigger refresh operations [3].
    """
    company_name = record.get("Company Name")
    recent_news = record.get("Recent News")
    overall_confidence = record.get("confidence_level", "Low").strip().title()
    
    # Static data fields (like Year of Incorporation) do not decay, 
    # but volatile fields (like Recent News) do.
    if not recent_news:
        # If there are no news indicators to trace freshness, we drop to Medium/Low
        if overall_confidence == "High":
            raise ValueError(
                f"Recency Exception: Record for '{company_name}' lacks a recent timeline "
                f"to verify operational freshness. 'High' confidence level is disallowed."
            )
        return True

    # 1. Extract dates and find the newest data point
    extracted_dates = extract_dates_from_string(str(recent_news))
    if not extracted_dates:
        # If dates are malformed in the timeline
        if overall_confidence == "High":
            raise ValueError(
                f"Recency Exception: Cannot verify recency for '{company_name}' due to "
                f"malformed dates. 'High' confidence level is disallowed."
            )
        return True

    newest_date = max(extracted_dates)
    months_old = calculate_months_difference(SYSTEM_BASELINE_DATE, newest_date)

    # 2. Categorize Recency Tiers [1]
    if months_old <= 6:
        record["recency_tier"] = "Recent"
    elif months_old <= 12:
        record["recency_tier"] = "Acceptable"
    else:
        record["recency_tier"] = "Outdated"

    # 3. Enforce Freshness Rules
    # Rule A: Outdated records (>12 months) cannot carry a High confidence status
    if record["recency_tier"] == "Outdated":
        record["requires_refresh"] = True
        if overall_confidence == "High":
            raise ValueError(
                f"Recency Mismatch: Record for '{company_name}' is 'Outdated' (latest data is "
                f"{months_old} months old). A 'High' confidence level is disallowed until refreshed."
            )
    else:
        record["requires_refresh"] = False

    return True


# --- Pytest Recency Suite ---

def test_recent_timeline_success():
    """
    Validates a company profile with highly fresh events dated within the last 6 months.
    """
    record = {
        "Company Name": "NeuraLaunch Corp",
        "Recent News": "2026-03-10 - Acquired New Startup, 2025-12-25 - Launched Version 2.0",
        "confidence_level": "High"
    }
    
    assert validate_record_recency(record) is True
    assert record["recency_tier"] == "Recent"
    assert record["requires_refresh"] is False


def test_acceptable_timeline_success():
    """
    Validates a company profile with events dated between 6 and 12 months old.
    """
    record = {
        "Company Name": "Apex SaaS LLC",
        "Recent News": "2025-08-15 - Opened New Office",
        "confidence_level": "Medium"
    }
    
    assert validate_record_recency(record) is True
    assert record["recency_tier"] == "Acceptable"
    assert record["requires_refresh"] is False


def test_outdated_timeline_low_confidence_success():
    """
    Ensures that an outdated record successfully passes validation if its 
    confidence level is correctly restricted to 'Medium' or 'Low' and the refresh flag is set.
    """
    record = {
        "Company Name": "Legacy Tech Corp",
        "Recent News": "2024-02-10 - Series A Funding",  # ~27 months old (Outdated)
        "confidence_level": "Medium"
    }
    
    assert validate_record_recency(record) is True
    assert record["recency_tier"] == "Outdated"
    assert record["requires_refresh"] is True


def test_outdated_timeline_false_high_confidence_fails():
    """
    Asserts that a record with outdated operational details is rejected 
    if it attempts to carry an unverified 'High' confidence status.
    """
    record = {
        "Company Name": "Legacy Tech Corp",
        "Recent News": "2024-02-10 - Series A Funding",  # ~27 months old (Outdated)
        "confidence_level": "High"  # Conflict: Outdated record claiming High confidence
    }
    
    with pytest.raises(ValueError, match="is 'Outdated' .* A 'High' confidence level is disallowed"):
        validate_record_recency(record)


def test_malformed_dates_prevent_high_confidence_fails():
    """
    Asserts that if the recency cannot be programmatically verified due to
    malformed dates, the record is blocked from claiming 'High' confidence.
    """
    record = {
        "Company Name": "Unresolved LLC",
        "Recent News": "Sometime last year - Opened new headquarters",  # Malformed date
        "confidence_level": "High"
    }
    
    with pytest.raises(ValueError, match="Cannot verify recency .* 'High' confidence level is disallowed"):
        validate_record_recency(record)