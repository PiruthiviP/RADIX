import re
import pytest
from typing import Dict, Any, List, Tuple

def parse_money_to_float(val: Any) -> float:
    """Parses money strings (e.g. '$10M', '-$1.5B') into raw floats supporting negative signs."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
        
    raw_str = str(val).replace("$", "").replace(",", "").strip().upper()
    
    # Handle negative signs inside or outside currency symbols (e.g. -$2M, $-2M)
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

def validate_logical_consistency(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter logical alignment of related fields.
    Returns: (success_bool, list_of_error_logs)
    """
    errors = []

    # Helper to check if a field is populated
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
            errors.append(f"Logical Contradiction: Profitability Status is 'Profitable' but Annual Profits are negative/zero ({profit}).")
        elif status == "Loss-making" and profit >= 0:
            errors.append(f"Logical Contradiction: Profitability Status is 'Loss-making' but Annual Profits are positive/zero ({profit}).")
        elif status == "Break-even" and profit != 0:
            errors.append(f"Logical Contradiction: Profitability Status is 'Break-even' but Annual Profits are non-zero ({profit}).")

    # Rule 2: Nature of Company vs Exit Strategy
    nature = payload.get("Nature of Company")
    exit_history = str(payload.get("Exit Strategy/History", ""))
    
    if nature == "Public":
        # Public companies must show public listing/IPO traces in their exit/strategy history
        if not re.search(r"\b(ipo|public|stock|listed|nasdaq|nyse)\b", exit_history, re.IGNORECASE):
            errors.append("Logical Contradiction: Company Nature is 'Public' but Exit History lacks public listing / IPO references.")

    # Rule 3: Customer Concentration Risk vs Top Customers
    concentration = payload.get("Customer Concentration Risk")
    customers = payload.get("Top Customers by Client Segments")
    
    if concentration == "Yes" or (isinstance(concentration, str) and "High" in concentration):
        if not is_filled("Top Customers by Client Segments"):
            errors.append("Logical Contradiction: Customer Concentration Risk is flagged but Top Customers are missing.")

    # Rule 4: Number of Offices vs Office Locations
    try:
        offices_count = int(payload.get("Number of Offices (beyond HQ)", 0) or 0)
        if offices_count > 0 and not is_filled("Office Locations"):
            errors.append(f"Logical Contradiction: Number of Offices is {offices_count} but Office Locations list is empty.")
    except ValueError:
        pass

    # Rule 5: Remote Work Policy vs Flexibility Policy
    remote_policy = payload.get("Remote Work Policy")
    flex_policy = payload.get("Remote / hybrid / on-site flexibility")
    
    if remote_policy == "Remote-First" and flex_policy == "On-Site":
        errors.append("Logical Contradiction: Remote Work Policy is 'Remote-First' but flexibility policy is set as strict 'On-Site'.")

    return len(errors) == 0, errors


# --- Pytest Tests ---

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
        "Remote / hybrid / on-site flexibility": "Remote"
    }
    success, errors = validate_logical_consistency(valid_payload)
    assert success is True
    assert not errors

def test_profit_polarity_contradiction_fails():
    """Verifies that mismatched Profitability Status and Annual Profits fail validation."""
    invalid_payload = {
        "Annual Profits": "-$500K",  # Negative profit
        "Profitability Status": "Profitable"  # Contradicts negative profits
    }
    success, errors = validate_logical_consistency(invalid_payload)
    assert success is False
    assert any("Profitability Status is 'Profitable'" in err for err in errors)

def test_public_company_missing_ipo_evidence_fails():
    """Verifies that a public company with an exit history lacking public listing details fails validation."""
    invalid_payload = {
        "Nature of Company": "Public",
        "Exit Strategy/History": "Early stage private seed round completed."  # Contradicts public nature
    }
    success, errors = validate_logical_consistency(invalid_payload)
    assert success is False
    assert any("Exit History lacks public listing / IPO references" in err for err in errors)

def test_unsubstantiated_concentration_risk_fails():
    """Verifies that flagging concentration risk without providing customer details fails validation."""
    invalid_payload = {
        "Customer Concentration Risk": "Yes",
        "Top Customers by Client Segments": None  # Missing customer listing
    }
    success, errors = validate_logical_consistency(invalid_payload)
    assert success is False
    assert any("Top Customers are missing" in err for err in errors)

def test_missing_office_locations_fails():
    """Verifies that declaring branch offices without specifying their locations fails validation."""
    invalid_payload = {
        "Number of Offices (beyond HQ)": 5,
        "Office Locations": ""  # Missing locations list
    }
    success, errors = validate_logical_consistency(invalid_payload)
    assert success is False
    assert any("Office Locations list is empty" in err for err in errors)