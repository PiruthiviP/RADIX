import datetime
import pytest
from typing import Dict, Any, List, Tuple

# Mock Live Database reflecting the exact corporate reality as of May 22, 2026
LIVE_GROUND_TRUTH = {
    "microsoft": {
        "current_ceo": "Satya Nadella",
        "former_ceos": {"Bill Gates", "Steve Ballmer"},
        "latest_funding_round_date": "2026-01-15",
        "total_capital_raised": 13000000000.0,
        "employee_count": 221000
    },
    "mockcorp": {
        "current_ceo": "Jane Doe",
        "former_ceos": {"John Smith"},
        "latest_funding_round_date": "2026-03-10",
        "total_capital_raised": 15000000.0,
        "employee_count": 450
    }
}

def validate_ceo_temporal_accuracy(company_key: str, ingested_ceo: str) -> Tuple[bool, str]:
    """Ensures that the ingested CEO name represents the active CEO, not a predecessor."""
    truth = LIVE_GROUND_TRUTH.get(company_key.lower())
    if not truth:
        return False, "Company not found in registry."
        
    if ingested_ceo == truth["current_ceo"]:
        return True, "CEO name is current and accurate."
    elif ingested_ceo in truth["former_ceos"]:
        return False, f"Obsolete Data: '{ingested_ceo}' is a former CEO. Current active CEO is '{truth['current_ceo']}'."
    return False, f"Factual error: '{ingested_ceo}' is not registered as an active or former CEO."

def validate_news_temporal_bounds(news_list: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
    """
    Enforces the trailing 12-24 month window constraint.
    As of May 22, 2026, events older than May 22, 2024 are rejected as stale.
    """
    errors = []
    current_date = datetime.date(2026, 5, 22)
    boundary_date = current_date - datetime.timedelta(days=2*365)  # 2 years boundary
    
    for item in news_list:
        date_str = item.get("date", "")
        try:
            event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if event_date < boundary_date:
                errors.append(f"Stale News: Event '{item.get('headline')}' on {date_str} is older than the 2-year boundary ({boundary_date}).")
        except ValueError:
            errors.append(f"Format error: Invalid date format '{date_str}' for event '{item.get('headline')}'. Use YYYY-MM-DD.")
            
    return len(errors) == 0, errors

def validate_total_capital_raised_reconciliation(company_key: str, ingested_total: float, ingested_rounds: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Ensures that the Total Capital Raised parameter is up-to-date and matches the cumulative sum
    of all documented funding round amounts.
    """
    truth = LIVE_GROUND_TRUTH.get(company_key.lower())
    if not truth:
        return False, "Company not found in registry."
        
    # Calculate cumulative sum of ingested rounds to check alignment
    calculated_sum = sum(float(round_item.get("amount", 0)) for round_item in ingested_rounds)
    
    if ingested_total < calculated_sum:
        return False, f"Outdated Financials: Ingested Total Capital ({ingested_total}) is less than the cumulative sum of logged rounds ({calculated_sum})."
        
    if abs(ingested_total - truth["total_capital_raised"]) > 0.01:
        return False, f"Outdated Financials: Ingested Total ({ingested_total}) does not align with the current live registry total ({truth['total_capital_raised']})."
        
    return True, "Financial reconciliation passed."


# --- Pytest Tests ---

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
    """Verifies that news events dated within the 2-year boundary (relative to May 2026) pass validation."""
    valid_news = [
        {"date": "2025-10-15", "headline": "Acquired Cloud Platform LLC"},
        {"date": "2024-06-01", "headline": "Launched Generative AI Integration"}
    ]
    success, errors = validate_news_temporal_bounds(valid_news)
    assert success is True
    assert not errors

def test_stale_news_older_than_two_years_fails():
    """Verifies that news events older than the 2-year boundary are rejected as obsolete."""
    stale_news = [
        {"date": "2023-01-10", "headline": "Initial Seed Round Closed"},  # Obsolete (older than May 22, 2024)
        {"date": "2025-05-12", "headline": "Series A Funding Completed"}
    ]
    success, errors = validate_news_temporal_bounds(stale_news)
    assert success is False
    assert any("Stale News" in err for err in errors)

def test_outdated_total_capital_raised_fails():
    """Verifies that out-of-date Total Capital Raised entries that lag behind documented rounds fail validation."""
    ingested_rounds = [
        {"date": "2018-05-12", "amount": 5000000.0},
        {"date": "2026-03-10", "amount": 10000000.0}
    ]
    # Ingested total lacks the 2026 round addition (stuck on old $5M total)
    stale_total = 5000000.0
    
    success, msg = validate_total_capital_raised_reconciliation("mockcorp", stale_total, ingested_rounds)
    assert success is False
    assert "Outdated Financials" in msg