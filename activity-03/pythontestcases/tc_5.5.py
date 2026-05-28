import pytest
from typing import Dict, Any, List, Tuple

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
    """
    Parses employee size strings into a representative integer.
    Supports ranges ('11-50' -> 50) and exact counts ('1000' -> 1000).
    """
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
            return int(parts[1])  # Use max bound of range
        except (IndexError, ValueError):
            pass
            
    try:
        return int(clean_str)
    except ValueError:
        return 0

def validate_cross_parameter_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Performs holistic record-level validations to catch contradictory metric combinations.
    1. Operational Footprint: Flags if headcount is tiny (< 10) but office count is high (> 5).
    2. Customer Success: Flags if NPS is exceptional (> 75) but churn rate is extremely high (> 30%).
    3. Talent Growth: Flags if turnover is extremely high (> 40%) but workforce is marked as stable/scaling with 0 hiring velocity.
    """
    errors = []

    # 1. Footprint Audit: Employee Size vs Number of Offices
    headcount = parse_employee_size_to_int(payload.get("Employee Size"))
    try:
        office_count = int(payload.get("Number of Offices (beyond HQ)", 0) or 0)
        # It is highly anomalous for < 10 employees to maintain more than 5 distinct offices
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
            # High NPS (75+) should correlate with healthy retention (churn < 30%)
            if nps_val >= 75 and churn_rate >= 30.0:
                errors.append(
                    f"Loyalty Contradiction: Ingested Net Promoter Score is exceptionally high ({nps_val}), "
                    f"but Churn Rate is recorded as extremely high ({churn_rate}%). These metrics contradict each other."
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


# --- Pytest Tests ---

def test_coherent_metrics_pass_audit():
    """Verifies that internally consistent, logically coherent records pass validation."""
    coherent_payload = {
        "Employee Size": "10,000+",
        "Number of Offices (beyond HQ)": 25,  # Large footprint matches large headcount
        "Net Promoter Score (NPS)": 80,
        "Churn Rate": "4%",                   # High NPS aligns with low churn
        "Employee Turnover": "12%",
        "Hiring Velocity": "High"
    }
    success, errors = validate_cross_parameter_coherence(coherent_payload)
    assert success is True
    assert not errors

def test_anomalous_headcount_to_office_ratio_fails():
    """Verifies that claiming a tiny headcount with a massive branch office footprint fails validation."""
    anomalous_payload = {
        "Employee Size": "1-5",
        "Number of Offices (beyond HQ)": 12  # Anomalous (max 5 employees cannot run 12 offices)
    }
    success, errors = validate_cross_parameter_coherence(anomalous_payload)
    assert success is False
    assert any("Operational Contradiction" in err for err in errors)

def test_contradictory_nps_and_churn_fails():
    """Verifies that contradictory high customer satisfaction and high customer churn fail validation."""
    contradictory_payload = {
        "Net Promoter Score (NPS)": 85,
        "Churn Rate": "35%"  # Mismatch: extreme loyalty score paired with rapid customer loss
    }
    success, errors = validate_cross_parameter_coherence(contradictory_payload)
    assert success is False
    assert any("Loyalty Contradiction" in err for err in errors)

def test_unsupported_high_turnover_fails():
    """Verifies that high employee loss paired with zero hiring velocity triggers an alarm."""
    contradictory_payload = {
        "Employee Turnover": "50%",
        "Hiring Velocity": "None / Zero open roles"  # Mismatch: massive attrition with zero replacement scaling
    }
    success, errors = validate_cross_parameter_coherence(contradictory_payload)
    assert success is False
    assert any("Talent Contradiction" in err for err in errors)