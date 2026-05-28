import pytest
from typing import Dict, Any, List, Tuple

# Mock Live Crisis Registry as of May 22, 2026
LIVE_CRISIS_REGISTRY = {
    "innovatecorp": {
        "has_layoff_crisis": True,
        "layoff_date": "2025-10-15",
        "layoff_percentage": 25.0,
        "expected_headcount_max": 200,      # Headcount must contract below this limit
        "required_news_keywords": ["layoff", "workforce reduction", "restructuring"]
    },
    "securenet": {
        "has_legal_scandal": True,
        "scandal_type": "Data Breach",
        "scandal_date": "2026-02-05",
        "expected_sentiment_bounds": ["Neutral", "Negative"],
        "required_controversy_keywords": ["breach", "cybersecurity", "unauthorized access"]
    }
}

def validate_crisis_event_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces record-level consistency when a company has registered crisis events:
    1. For Layoff Crises:
        - Layoff history must contain the event.
        - Employee Size must reflect the headcount contraction.
        - Recent News must log the event.
    2. For Legal/Scandal Crises:
        - Legal Issues / Controversies must document the event.
        - Brand Sentiment Score must not remain 'Positive'.
        - Crisis behavior must detail the response.
    """
    errors = []
    company_name = str(payload.get("Company Name", "")).strip().lower()

    if company_name not in LIVE_CRISIS_REGISTRY:
        return True, [] # Bypasses checks if no active crisis is recorded

    truth = LIVE_CRISIS_REGISTRY[company_name]

    # --- Case 1: Layoff Crisis Verification ---
    if truth.get("has_layoff_crisis"):
        # Check 1.1: Layoff history must contain the RIF percentage
        layoff_history = str(payload.get("Layoff history", ""))
        expected_pct = f"{int(truth['layoff_percentage'])}%"
        if expected_pct not in layoff_history:
            errors.append(
                f"Factual Error [Layoff history]: Missing registered {expected_pct} layoff "
                f"occurring on {truth['layoff_date']}."
            )

        # Check 1.2: Headcount must reflect contraction
        emp_size_str = str(payload.get("Employee Size", ""))
        # Simple extraction of numeric values from string (e.g. "100-200")
        clean_emp = "".join([c for c in emp_size_str if c.isdigit() or c == "-"])
        emp_count = 0
        if "-" in clean_emp:
            emp_count = int(clean_emp.split("-")[1])
        elif clean_emp:
            emp_count = int(clean_emp)
            
        max_allowed = truth["expected_headcount_max"]
        if emp_count > max_allowed:
            errors.append(
                f"Temporal Mismatch [Employee Size]: Headcount '{emp_size_str}' is outdated. "
                f"Post-layoff headcount must contract below {max_allowed}."
            )

        # Check 1.3: Recent News must record the event
        news_str = str(payload.get("Recent News", "")).lower()
        missing_news_keywords = [kw for kw in truth["required_news_keywords"] if kw not in news_str]
        if len(missing_news_keywords) == len(truth["required_news_keywords"]):
            errors.append(
                f"Temporal Lineage Error [Recent News]: Missing any reference to the 2025 layoff. "
                f"Expected keywords like: {truth['required_news_keywords']}."
            )

    # --- Case 2: Legal / Scandal Crisis Verification ---
    if truth.get("has_legal_scandal"):
        # Check 2.1: Legal Issues / Controversies must document the scandal
        controversies = str(payload.get("Legal Issues / Controversies", "")).lower()
        missing_scandal_keywords = [kw for kw in truth["required_controversy_keywords"] if kw not in controversies]
        if len(missing_scandal_keywords) == len(truth["required_controversy_keywords"]):
            errors.append(
                f"Temporal Lineage Error [Legal Issues / Controversies]: Missing documentation of the 2026 {truth['scandal_type']}. "
                f"Expected keywords like: {truth['required_controversy_keywords']}."
            )

        # Check 2.2: Brand Sentiment Score must degrade
        sentiment = payload.get("Brand Sentiment Score")
        allowed_bounds = truth["expected_sentiment_bounds"]
        if sentiment not in allowed_bounds:
            errors.append(
                f"Temporal Accuracy Error [Brand Sentiment Score]: Corporate sentiment remains '{sentiment}' "
                f"despite a severe {truth['scandal_type']} on {truth['scandal_date']}. Expected: {allowed_bounds}."
            )

        # Check 2.3: Crisis behavior must document response
        crisis_behavior = str(payload.get("Crisis behavior", ""))
        if not crisis_behavior or crisis_behavior.strip() == "" or "N/A" in crisis_behavior:
            errors.append(
                f"Temporal Lineage Error [Crisis behavior]: Action response is missing or blank "
                f"following the 2026 {truth['scandal_type']}."
            )

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_fresh_post_crisis_profile_passes():
    """Verifies that a company profile updated to accurately reflect its 2025/2026 crises passes validation."""
    valid_payload = {
        "Company Name": "InnovateCorp",
        "Employee Size": "100-200",  # Correctly contracted headcount
        "Layoff history": "2025-10-15 - 25% of workforce impacted due to restructuring",  # Correctly logged
        "Recent News": "2025-10-15 - InnovateCorp announced a major workforce reduction of 25%",  # News updated
        "Crisis behavior": "Managed the 25% RIF transparently with severance packages"
    }
    
    success, errors = validate_crisis_event_coherence(valid_payload)
    assert success is True
    assert not errors

def test_stale_pre_layoff_profile_fails():
    """Verifies that an outdated profile retaining standalone pre-layoff parameters fails validation."""
    stale_payload = {
        "Company Name": "InnovateCorp",
        "Employee Size": "500-1000",  # Outdated headcount
        "Layoff history": "None",      # Missing layoff log
        "Recent News": "2024-06-15 - Launched version 2.0 platform"  # Missing 2025 layoff news
    }
    
    success, errors = validate_crisis_event_coherence(stale_payload)
    assert success is False
    assert any("Factual Error [Layoff history]" in err for err in errors)
    assert any("Temporal Mismatch [Employee Size]" in err for err in errors)
    assert any("Temporal Lineage Error [Recent News]" in err for err in errors)

def test_stale_reputation_score_fails_on_scandal_company():
    """Verifies that maintaining a 'Positive' sentiment score following a major data breach fails validation."""
    stale_payload = {
        "Company Name": "SecureNet",
        "Brand Sentiment Score": "Positive",  # Obsolete/stale reputation score
        "Legal Issues / Controversies": "None",  # Missing breach logs
        "Crisis behavior": "N/A"  # Missing response
    }
    
    success, errors = validate_crisis_event_coherence(stale_payload)
    assert success is False
    assert any("Temporal Accuracy Error [Brand Sentiment Score]" in err for err in errors)
    assert any("Temporal Lineage Error [Legal Issues / Controversies]" in err for err in errors)
    assert any("Temporal Lineage Error [Crisis behavior]" in err for err in errors)