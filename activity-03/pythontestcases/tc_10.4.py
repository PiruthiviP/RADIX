import re
import pytest
from typing import Dict, Any, List, Tuple

# List of obsolete compliance standards as of May 22, 2026
OBSOLETE_STANDARDS = {
    "ISO27001:2013": "ISO27001:2022"  # Outdated ISO security standard
}

# Mandatory framework keywords required for specific industry categories in 2025/2026
MANDATORY_REGULATORY_KEYWORDS = {
    "critical-infrastructure": {
        "required": ["NIS2", "ISO27001:2022"],
        "fields": ["Regulatory & Compliance Status", "Cybersecurity Posture"]
    },
    "enterprise-supply-chain": {
        "required": ["CSRD", "CSDDD"],
        "fields": ["ESG Practices or Ratings", "Ethical Sourcing Practices"]
    }
}

def audit_regulatory_validity(payload: Dict[str, Any], company_profile_type: str) -> Tuple[bool, List[str]]:
    """
    Scans compliance and policy parameters for temporal regulatory validity:
    1. Rejects obsolete certifications (e.g. ISO27001:2013) and flags the updated replacement framework.
    2. Enforces mandatory 2025/2026 legislative keywords based on company category.
    """
    errors = []
    
    # 1. Scan for Obsolete Standards across all text parameters
    for field_name, value in payload.items():
        if isinstance(value, str):
            for obsolete, replacement in OBSOLETE_STANDARDS.items():
                if obsolete in value:
                    errors.append(
                        f"Temporal Compliance Error in '{field_name}': Stale standard '{obsolete}' is obsolete. "
                        f"Target entity must upgrade and certify under '{replacement}'."
                    )

    # 2. Scan for newly active 2025/2026 mandatory regulations
    rule = MANDATORY_REGULATORY_KEYWORDS.get(company_profile_type.lower())
    if rule:
        required_keywords = rule["required"]
        target_fields = rule["fields"]
        
        # Concatenate text from target fields
        combined_text = ""
        for field in target_fields:
            combined_text += " " + str(payload.get(field, "")).lower()
            
        for kw in required_keywords:
            if kw.lower() not in combined_text:
                errors.append(
                    f"Regulatory Compliance Violation: Missing mandatory 2025/2026 compliance framework '{kw}' "
                    f"across evaluated fields: {target_fields}."
                )

    return len(errors) == 0, errors


# --- Pytest Tests ---

def test_compliant_modern_profile_passes():
    """Verifies that a company updated to active 2025/2026 standards passes validation."""
    payload = {
        "Regulatory & Compliance Status": "SOC2, HIPAA, ISO27001:2022, NIS2 Compliant",
        "Cybersecurity Posture": "Zero trust architecture conforming strictly to NIS2 Directive."
    }
    success, errors = audit_regulatory_validity(payload, company_profile_type="critical-infrastructure")
    assert success is True
    assert not errors

def test_obsolete_iso_certification_rejected():
    """Verifies that a company claiming an obsolete certification (ISO27001:2013) is rejected."""
    payload = {
        "Regulatory & Compliance Status": "SOC2, HIPAA, ISO27001:2013",  # Obsolete standard
        "Cybersecurity Posture": "Basic security controls implemented."
    }
    success, errors = audit_regulatory_validity(payload, company_profile_type="general")
    
    assert success is False
    assert any("Stale standard 'ISO27001:2013' is obsolete" in err for err in errors)
    assert "upgrade and certify under 'ISO27001:2022'" in errors[0]

def test_critical_infrastructure_missing_nis2_fails():
    """Verifies that critical infrastructure entities missing the mandatory NIS2 framework fail validation."""
    payload = {
        "Regulatory & Compliance Status": "SOC2, HIPAA, ISO27001:2022",  # Missing mandatory NIS2
        "Cybersecurity Posture": "Standard data encryption active."
    }
    success, errors = audit_regulatory_validity(payload, company_profile_type="critical-infrastructure")
    
    assert success is False
    assert any("Missing mandatory 2025/2026 compliance framework 'NIS2'" in err for err in errors)

def test_enterprise_supply_chain_missing_csddd_fails():
    """Verifies that large supply chain companies missing CSDDD/CSRD compliance fail validation."""
    payload = {
        "ESG Practices or Ratings": "We focus on green packaging.",
        "Ethical Sourcing Practices": "Fair labor practices expected from partners."  # Missing CSDDD / CSRD
    }