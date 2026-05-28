import re
import pytest
from typing import Dict, Any

# Customer Concentration Regex Match: ^(Yes|No|High|Low).*$
CONCENTRATION_REGEX = re.compile(r"^(Yes|No|High|Low)(.*)$", re.IGNORECASE)

# Burnout Risk Regex Match: ^(Low|Medium|High|Severe).*$
BURNOUT_REGEX = re.compile(r"^(Low|Medium|High|Severe)(.*)$", re.IGNORECASE)


def validate_risk_classifications(record: Dict[str, Any]) -> bool:
    """
    Validates structural formatting and logical constraints for Customer Concentration Risk,
    Burnout Risk, and Operational Runway.
    """
    concentration = record.get("Customer Concentration Risk")
    burnout = record.get("Burnout risk")
    runway = record.get("Runway")
    weekend_work = record.get("Weekend work")
    overtime_exp = record.get("Overtime expectations")

    # 1. Validate Customer Concentration Risk
    if concentration is not None:
        con_str = str(concentration).strip()
        match = CONCENTRATION_REGEX.match(con_str)
        if not match:
            raise ValueError(
                f"Format Error: 'Customer Concentration Risk' value '{concentration}' "
                f"must start with 'Yes', 'No', 'High', or 'Low'."
            )
        
        # Cross-field logical check: Extract percentage if specified in string
        percent_match = re.search(r"(\d+)%", con_str)
        if percent_match:
            percent_val = int(percent_match.group(1))
            prefix = match.group(1).title()
            
            # If concentration > 20%, prefix must flag risk (cannot be 'No' or 'Low')
            if percent_val > 20 and prefix in ["No", "Low"]:
                raise ValueError(
                    f"Logical Mismatch: Customer concentration is {percent_val}%, "
                    f"but risk level is marked as '{prefix}'. Expected 'Yes' or 'High'."
                )

    # 2. Validate Burnout Risk Alignment
    if burnout is not None:
        burn_str = str(burnout).strip()
        match = BURNOUT_REGEX.match(burn_str)
        if not match:
            raise ValueError(
                f"Format Error: 'Burnout risk' value '{burnout}' "
                f"must start with 'Low', 'Medium', 'High', or 'Severe'."
            )
            
        prefix = match.group(1).title()
        
        # Relational Check: Extreme work patterns cannot map to Low/Medium burnout risk
        if weekend_work == "Always" and overtime_exp == "Frequent":
            if prefix in ["Low", "Medium"]:
                raise ValueError(
                    f"Logical Mismatch: Workplace has 'Always' weekend work and 'Frequent' "
                    f"overtime, but Burnout Risk is classified as '{prefix}'. Expected 'High' or 'Severe'."
                )

    # 3. Validate Runway Financial Risk Flag
    if runway is not None:
        try:
            runway_val = float(str(runway).strip())
        except ValueError:
            raise ValueError(f"Data Type Error: Runway '{runway}' must be a valid float value.")
            
        if runway_val < 0:
            raise ValueError("Boundary Error: Runway cannot be negative.")
            
        # Log a warning or return state if runway is critical (under 6 months)
        record["is_critical_runway"] = runway_val < 6.0

    return True


# --- Pytest Suite ---

def test_concentration_risk_high_success():
    """
    Validates high concentration risk where percentage exceeds boundary and matches prefix.
    """
    record = {
        "Customer Concentration Risk": "High - 35% from top client",
        "Burnout risk": "Medium",
        "Runway": "18.0"
    }
    assert validate_risk_classifications(record) is True


def test_intense_work_severe_burnout_success():
    """
    Validates extreme work conditions mapped to severe burnout risk.
    """
    record = {
        "Weekend work": "Always",
        "Overtime expectations": "Frequent",
        "Burnout risk": "Severe risk of attrition"
    }
    assert validate_risk_classifications(record) is True


def test_critical_runway_risk_logged():
    """
    Ensures runway under 6 months triggers a critical flag within the metadata dictionary.
    """
    record = {
        "Runway": "4.5"
    }
    assert validate_risk_classifications(record) is True
    assert record["is_critical_runway"] is True


def test_invalid_concentration_prefix_fails():
    """
    Rejects concentration risk strings that use arbitrary non-standard prefixes.
    """
    record = {
        "Customer Concentration Risk": "Maybe - about 15%"  # Non-conforming prefix 'Maybe'
    }
    with pytest.raises(ValueError, match="must start with 'Yes', 'No', 'High', or 'Low'"):
        validate_risk_classifications(record)


def test_contradictory_concentration_and_percentage_fails():
    """
    Rejects records that claim 'Low' or 'No' concentration risk despite >20% revenue from one client.
    """
    record = {
        "Customer Concentration Risk": "Low - 30% from anchor client"  # 30% is too high for a 'Low' risk claim
    }
    with pytest.raises(ValueError, match="Expected 'Yes' or 'High'"):
        validate_risk_classifications(record)


def test_contradictory_work_conditions_and_burnout_fails():
    """
    Rejects records that attempt to greenwash high work-pressure as 'Low' burnout risk.
    """
    record = {
        "Weekend work": "Always",
        "Overtime expectations": "Frequent",
        "Burnout risk": "Low"  # Contradicts extreme work conditions
    }
    with pytest.raises(ValueError, match="Expected 'High' or 'Severe'"):
        validate_risk_classifications(record)