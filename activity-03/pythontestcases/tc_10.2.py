import pytest
from typing import Dict, Any, List, Tuple

# Mock M&A and Restructuring Registry as of May 22, 2026
LIVE_MA_REGISTRY = {
    "acme corp": {
        "is_acquired": True,
        "acquired_by": "Mega conglomerate",
        "acquisition_date": "2025-11-12",
        "expected_nature": "Subsidiary",
        "post_merger_headcount_min": 1000,
        "required_news_keywords": ["acquired", "acquisition", "merger"]
    },
    "independent startup": {
        "is_acquired": False,
        "expected_nature": "Private",
        "post_merger_headcount_min": 10,
        "required_news_keywords": []
    }
}

def validate_structural_changes(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates company profile structural consistency post-cutoff:
    - If the company was acquired according to the M&A registry:
        1. Nature of Company must be updated to "Subsidiary" (not "Private" or "Partnership").
        2. Employee Size must reflect the combined post-merger headcount (> post_merger_headcount_min).
        3. Recent News must contain references/keywords related to the acquisition.
        4. Exit Strategy/History must document the acquisition event.
    """
    errors = []
    company_name = str(payload.get("Company Name", "")).strip().lower()
    
    if company_name not in LIVE_MA_REGISTRY:
        # Non-registered companies bypass M&A checks
        return True, []
        
    truth = LIVE_MA_REGISTRY[company_name]
    
    if truth["is_acquired"]:
        # 1. Validate Legal Nature transition
        nature = payload.get("Nature of Company")
        expected_nature = truth["expected_nature"]
        if nature != expected_nature:
            errors.append(
                f"Structural Decay [Nature of Company]: Company was acquired in {truth['acquisition_date']} "
                f"and must be classified as '{expected_nature}' (Ingested: '{nature}')."
            )
            
        # 2. Validate Employee Headcount scaling post-merger
        raw_emp_size = str(payload.get("Employee Size", ""))
        # Simple parser to extract maximum number from range (e.g. "501-1000" -> 1000 or "10,000+" -> 10000)
        clean_emp = re.sub(r"[^\d\-]", "", raw_emp_size)
        emp_count = 0
        if "-" in clean_emp:
            emp_count = int(clean_emp.split("-")[1])
        elif clean_emp:
            emp_count = int(clean_emp)
            
        min_expected = truth["post_merger_headcount_min"]
        if emp_count < min_expected:
            errors.append(
                f"Structural Decay [Employee Size]: Headcount '{raw_emp_size}' is outdated. "
                f"Post-merger combined headcount must be at least {min_expected}."
            )

        # 3. Validate Recent News update
        news_str = str(payload.get("Recent News", "")).lower()
        missing_keywords = [kw for kw in truth["required_news_keywords"] if kw not in news_str]
        if len(missing_keywords) == len(truth["required_news_keywords"]):
            errors.append(
                f"Temporal Lineage Error [Recent News]: Missing any reference to the 2025 acquisition. "
                f"Expected keywords like: {truth['required_news_keywords']}."
            )

        # 4. Validate Exit History documentation
        exit_str = str(payload.get("Exit Strategy/History", "")).lower()
        if "acquired" not in exit_str and "merger" not in exit_str:
            errors.append(
                f"Temporal Lineage Error [Exit Strategy/History]: Exit details must document "
                f"the 2025 acquisition by '{truth['acquired_by']}'."
            )

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_fresh_restructured_profile_passes():
    """Verifies that a company profile correctly updated to reflect its 2025 acquisition passes validation."""
    valid_record = {
        "Company Name": "Acme Corp",
        "Nature of Company": "Subsidiary",  # Successfully updated legal structure
        "Employee Size": "1000-5000",        # Successfully updated combined headcount
        "Recent News": "2025-11-12 - Acme Corp was acquired by Mega conglomerate for $100M",  # Logs transaction
        "Exit Strategy/History": "Acquired by Mega conglomerate in November 2025"             # Logs exit
    }
    
    success, errors = validate_structural_changes(valid_record)
    assert success is True
    assert not errors

def test_stale_pre_acquisition_profile_fails():
    """Verifies that an outdated profile retaining standalone pre-acquisition parameters fails validation."""
    stale_record = {
        "Company Name": "Acme Corp",
        "Nature of Company": "Private",      # Obsolete (pre-acquisition status)
        "Employee Size": "11-50",            # Obsolete (pre-acquisition headcount)
        "Recent News": "2024-06-15 - Launched version 2.0 platform",  # Missing 2025 acquisition news
        "Exit Strategy/History": "Targeting independent IPO in the long term"  # Obsolete exit plans
    }
    
    success, errors = validate_structural_changes(stale_record)
    assert success is False
    assert any("Structural Decay [Nature of Company]" in err for err in errors)
    assert any("Structural Decay [Employee Size]" in err for err in errors)
    assert any("Temporal Lineage Error [Recent News]" in err for err in errors)
    assert any("Temporal Lineage Error [Exit Strategy/History]" in err for err in errors)