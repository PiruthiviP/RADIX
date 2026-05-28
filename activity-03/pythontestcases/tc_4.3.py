import re
import pytest
from typing import Dict, Any, List, Tuple

# Mock USPTO Patent Office Database representing verified registrations
VERIFIED_PATENTS_DB = {
    "us-1234567-b2": "Microsoft Corporation",
    "us-7654321-b1": "Apple Inc."
}

# Strict superlative keywords indicating potential marketing hallucinations
SUPERLATIVE_PATTERNS = [
    r"\bfirst in the world\b",
    r"\bonly company\b",
    r"\bworld's fastest\b",
    r"\bglobally unique\b",
    r"\b100% guaranteed\b"
]

def audit_confident_incorrectness(payload: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """
    Analyzes the entire company profile to catch confident but unverified/unverifiable statements.
    - Flags high-certainty internal metrics (NPS, Churn) if they lack source citations.
    - Resolves patent IDs against the official USPTO mock database.
    - Scans descriptive fields for extreme superlative marketing claims.
    Computes a Confident Incorrectness Risk Score (%) based on triggered flags.
    """
    flags = []
    total_audited_elements = 0
    company_name = str(payload.get("Company Name", "")).strip()

    # 1. Audit Internal Private Metrics (NPS, Churn)
    nps = payload.get("Net Promoter Score (NPS)")
    churn = payload.get("Churn Rate")
    
    if nps is not None or churn is not None:
        total_audited_elements += 1
        # Private companies rarely publish exact NPS/Churn; check if source is cited
        has_citation = False
        for k, v in payload.items():
            if k.startswith("_attribution_") and ("NPS" in k or "Churn" in k):
                if v and v.get("source_url"):
                    has_citation = True
        if not has_citation:
            flags.append(
                f"Metric Warning: Private company metrics reported with high certainty (NPS: '{nps}', Churn: '{churn}') "
                f"without traceable source attribution."
            )

    # 2. Audit Intellectual Property (Patent verification)
    ip_text = str(payload.get("Intellectual Property", ""))
    if ip_text and ip_text.strip() != "":
        total_audited_elements += 1
        # Extract US patent patterns, e.g. "US-1234567-B2"
        found_patents = re.findall(r"(US-\d{7}-[A-Za-z0-9]{2})", ip_text, re.IGNORECASE)
        for patent in found_patents:
            patent_key = patent.lower()
            if patent_key in VERIFIED_PATENTS_DB:
                registered_owner = VERIFIED_PATENTS_DB[patent_key]
                if registered_owner.lower() != company_name.lower():
                    flags.append(
                        f"IP Mismatch: Patent '{patent}' is registered to '{registered_owner}', "
                        f"but was confidently claimed by '{company_name}'."
                    )
            else:
                flags.append(f"Fabricated IP: Patent '{patent}' claimed by '{company_name}' does not exist in USPTO database.")

    # 3. Audit Superlative Marketing Claims in Narratives
    narrative_fields = ["Overview of the Company", "Unique Differentiators", "Core Value Proposition"]
    for field in narrative_fields:
        text = str(payload.get(field, ""))
        if text and text.strip() != "":
            total_audited_elements += 1
            for pattern in SUPERLATIVE_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    flags.append(f"Superlative Warning: Field '{field}' contains unprovable claim matching pattern: '{pattern}'.")

    if total_audited_elements == 0:
        return True, 0.0, ["No audit-eligible parameters populated."]

    # Risk rating based on triggered alerts
    risk_score = round((len(flags) / total_audited_elements) * 100, 2)
    success = (len(flags) == 0)

    return success, risk_score, flags


# --- Pytest Tests ---

def test_legitimate_verifiable_record_passes():
    """Verifies that a record with verified patent ownership and standard descriptions passes."""
    valid_payload = {
        "Company Name": "Microsoft Corporation",
        "Intellectual Property": "Patents owned: US-1234567-B2",  # Valid patent registered to Microsoft
        "Overview of the Company": "Microsoft is a multinational technology enterprise specializing in software.",
        "Net Promoter Score (NPS)": 45,
        "_attribution_NPS": {"source_url": "https://trusted-survey-log.com/nps-report"} # Cited
    }
    success, risk_score, flags = audit_confident_incorrectness(valid_payload)
    assert success is True
    assert risk_score == 0.0
    assert not flags

def test_unverified_nps_and_churn_flags_warning():
    """Verifies that stating exact private metrics without a citation flags a warning."""
    unverified_payload = {
        "Company Name": "Microsoft Corporation",
        "Net Promoter Score (NPS)": 87,
        "Churn Rate": "1.25%"
        # Missing '_attribution_NPS' or '_attribution_Churn Rate'
    }
    success, risk_score, flags = audit_confident_incorrectness(unverified_payload)
    
    assert success is False
    assert risk_score == 100.0
    assert any("Private company metrics reported with high certainty" in f for f in flags)

def test_fabricated_patent_id_fails_ip_audit():
    """Verifies that claiming a fabricated patent ID that does not exist in USPTO registries fails validation."""
    fabricated_payload = {
        "Company Name": "Microsoft Corporation",
        "Intellectual Property": "Patents owned: US-9999999-B2"  # Plausible but non-existent
    }
    success, risk_score, flags = audit_confident_incorrectness(fabricated_payload)
    
    assert success is False
    assert any("Fabricated IP" in f for f in flags)
    assert "US-9999999-B2" in flags[0]

def test_mismatched_patent_owner_fails_ip_audit():
    """Verifies that claiming a patent registered to a different corporate owner fails validation."""
    mismatched_payload = {
        "Company Name": "Microsoft Corporation",
        "Intellectual Property": "Patents owned: US-7654321-B1"  # Valid patent, but registered to Apple
    }
    success, risk_score, flags = audit_confident_incorrectness(mismatched_payload)
    
    assert success is False
    assert any("IP Mismatch" in f for f in flags)
    assert "US-7654321-B1" in flags[0]
    assert "Apple Inc." in flags[0]

def test_absolute_superlatives_flag_marketing_warnings():
    """Verifies that high-certainty superlative marketing claims in narratives trigger audit warnings."""
    superlative_payload = {
        "Company Name": "Microsoft Corporation",
        "Unique Differentiators": "The only company in the world to deliver 100% guaranteed routing."
    }
    success, risk_score, flags = audit_confident_incorrectness(superlative_payload)
    
    assert success is False
    assert any("Superlative Warning" in f for f in flags)
    assert "only company" in flags[0]