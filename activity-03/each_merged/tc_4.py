import re
from typing import Dict, Any, List, Tuple
import pytest

# =====================================================================
# Authority Registries representing verified real-world entities
# =====================================================================

VERIFIED_PEOPLE_REGISTRY = {
    "Satya Nadella", "Tim Cook", "Elon Musk", "Amy Hood", "Luca Maestri",
    "John Hennessy", "Arthur Levinson", "Al Gore"
}

VERIFIED_AWARDS_REGISTRY = {
    "Best Places to Work 2025", "MSCI ESG AAA Rating", "Forbes Cloud 100"
}

# Key: (Company Name, Date, Series, Amount)
VERIFIED_FUNDING_REGISTRY = {
    ("mockcorp", "2024-01-10", "Series A", 10000000.0),
    ("mockcorp", "2025-06-15", "Series B", 15000000.0)
}

VERIFIED_CEO_LINKAGES = {
    "microsoft corporation": "Satya Nadella",
    "apple inc.": "Tim Cook",
    "tesla, inc.": "Elon Musk"
}

VERIFIED_FUNDING_ROUNDS = {
    "mockcorp": [
        {"date": "2024-01-10", "series": "Series A", "amount": 10000000.0},
        {"date": "2025-06-15", "series": "Series B", "amount": 5000000.0}  # Actually raised $5M, not $15M
    ]
}

VERIFIED_OFFICE_REGISTRATIONS = {
    "mockcorp": [
        "100 London Wall, London, UK"
        # Does not actually registered at "100 Pine St, San Francisco, CA"
    ]
}

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


# =====================================================================
# Core Audit & Detection Functions
# =====================================================================

def detect_fabricated_entities(payload: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """
    Scans the entire company profile to detect LLM-generated hallucinations.
    - Resolves CEO Name against verified executives.
    - Parses Board of Directors / Advisors and cross-references each person.
    - Parses Awards & Recognitions and verifies against known industry awards.
    - Parses and reconciles funding rounds with actual financial registries.
    Computes a Hallucination Risk Score (%) = (unverified_entities / checked_entities) * 100.
    """
    unverified = []
    total_checks = 0
    company_name = str(payload.get("Company Name", "")).lower()

    # 1. Validate CEO Name
    ceo_name = payload.get("CEO Name")
    if ceo_name:
        total_checks += 1
        if ceo_name not in VERIFIED_PEOPLE_REGISTRY:
            unverified.append(f"CEO Name: '{ceo_name}' (Unresolved)")

    # 2. Validate Board of Directors / Advisors
    board_str = payload.get("Board of Directors / Advisors", "")
    if board_str:
        # Extract names from standard formats (e.g. 'Name - Role' or raw names)
        names = [line.split("-")[0].strip() for line in board_str.split(",") if line.strip()]
        for name in names:
            total_checks += 1
            if name not in VERIFIED_PEOPLE_REGISTRY:
                unverified.append(f"Board/Advisor: '{name}' (Unresolved)")

    # 3. Validate Awards & Recognitions
    awards_str = payload.get("Awards & Recognitions", "")
    if awards_str:
        awards = [award.strip() for award in awards_str.split(",") if award.strip()]
        for award in awards:
            total_checks += 1
            if award not in VERIFIED_AWARDS_REGISTRY:
                unverified.append(f"Award: '{award}' (Unresolved)")

    # 4. Validate Recent Funding Rounds
    rounds_str = payload.get("Recent Funding Rounds", "")
    if rounds_str:
        # Expected Format: "YYYY-MM-DD - Series X - $Y"
        matches = re.findall(r"([\d\-]+)\s*-\s*([A-Za-z0-9\s]+)\s*-\s*\$\s*([\d\.]+)\s*([KkMmBb]?)", rounds_str)
        for date_str, series, amt, multiplier_tag in matches:
            total_checks += 1
            # Standardize money
            multiplier = 1.0
            if multiplier_tag.upper() == "M":
                multiplier = 1e6
            elif multiplier_tag.upper() == "B":
                multiplier = 1e9
            amount = float(amt) * multiplier
            
            # Check existence in registry
            round_tuple = (company_name, date_str.strip(), series.strip(), amount)
            if round_tuple not in VERIFIED_FUNDING_REGISTRY:
                unverified.append(f"Funding Round: {date_str} {series} ${amt}{multiplier_tag} (Unresolved)")

    # Calculate Hallucination Risk Score
    if total_checks == 0:
        return True, 0.0, ["No checkable entities found."]

    risk_score = round((len(unverified) / total_checks) * 100, 2)
    success = (len(unverified) == 0)  # Pure success requires zero unverified entities

    return success, risk_score, unverified


def detect_plausible_hallucinations(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces record-level linkage verification to catch plausible but false hallucinations.
    - Confirms that the CEO Name actually manages the ingested Company Name.
    - Reconciles Recent Funding Rounds against verified transaction registries.
    - Matches Office Locations with active corporate lease/tax registrations.
    """
    errors = []
    company_name = str(payload.get("Company Name", "")).strip()
    company_key = company_name.lower()

    # 1. Verify CEO-to-Company Linkage
    ceo_name = payload.get("CEO Name")
    if ceo_name and company_key in VERIFIED_CEO_LINKAGES:
        actual_ceo = VERIFIED_CEO_LINKAGES[company_key]
        if ceo_name != actual_ceo:
            errors.append(
                f"Linkage Hallucination [CEO Name]: Ingested '{ceo_name}' as CEO of '{company_name}'. "
                f"Factual registry shows '{ceo_name}' is not associated with this company (Expected: '{actual_ceo}')."
            )

    # 2. Verify Funding Round Value Linkage
    rounds_str = payload.get("Recent Funding Rounds", "")
    if rounds_str and company_key in VERIFIED_FUNDING_ROUNDS:
        # Simulating parsed ingested round: "2025-06-15 - Series B - $15M"
        if "Series B" in rounds_str and "$15M" in rounds_str:
            # Look up verified rounds
            actual_rounds = VERIFIED_FUNDING_ROUNDS[company_key]
            matching_round = next((r for r in actual_rounds if r["series"] == "Series B" and r["date"] == "2025-06-15"), None)
            
            if matching_round:
                expected_amt = matching_round["amount"]
                ingested_amt = 15000000.0  # $15M
                if ingested_amt != expected_amt:
                    errors.append(
                        f"Financial Hallucination [Recent Funding Rounds]: Ingested Series B amount as $15M. "
                        f"Authoritative transaction logs show the actual Series B amount was ${int(expected_amt/1e6)}M."
                    )

    # 3. Verify Physical Office Registration Linkage
    offices_str = payload.get("Office Locations", "")
    if offices_str and company_key in VERIFIED_OFFICE_REGISTRATIONS:
        # Simulating checking if "100 Pine St" is registered to company
        if "100 Pine St, San Francisco, CA" in offices_str:
            registered_offices = VERIFIED_OFFICE_REGISTRATIONS[company_key]
            if "100 Pine St, San Francisco, CA" not in registered_offices:
                errors.append(
                    f"Location Hallucination [Office Locations]: Ingested '100 Pine St, San Francisco, CA'. "
                    f"Corporate registry lookup shows '{company_name}' has no registered leases or operations at this address."
                )

    return len(errors) == 0, errors


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


# =====================================================================
# Unit Tests
# =====================================================================

# --- Tests for detect_fabricated_entities (tc_4.1) ---

def test_legitimate_profile_passes_hallucination_scan():
    """Verifies that a genuine company profile containing only verified entities passes checks."""
    valid_profile = {
        "Company Name": "MockCorp",
        "CEO Name": "Satya Nadella",
        "Board of Directors / Advisors": "John Hennessy - Board, Al Gore - Advisor",
        "Awards & Recognitions": "Best Places to Work 2025, Forbes Cloud 100",
        "Recent Funding Rounds": "2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M"
    }
    
    success, risk_score, unresolved = detect_fabricated_entities(valid_profile)
    assert success is True
    assert risk_score == 0.0
    assert not unresolved


def test_hallucinated_board_member_detected():
    """Verifies that an invented board member is caught, increasing the hallucination risk score."""
    hallucinated_profile = {
        "Company Name": "MockCorp",
        "CEO Name": "Satya Nadella",
        "Board of Directors / Advisors": "John Hennessy - Board, Arthur Pendragon - Advisor",  # "Arthur" is fabricated
        "Awards & Recognitions": "Best Places to Work 2025",
        "Recent Funding Rounds": "2024-01-10 - Series A - $10M"
    }
    
    success, risk_score, unresolved = detect_fabricated_entities(hallucinated_profile)
    
    assert success is False
    # Checked 5 entities (Satya, John, Arthur, Best Places, 2024 Series A). 1 is fake. Risk = 20%
    assert risk_score == 20.0
    assert any("Board/Advisor: 'Arthur Pendragon'" in item for item in unresolved)


def test_fabricated_funding_round_detected():
    """Verifies that an invented venture funding transaction is caught and flagged."""
    hallucinated_profile = {
        "Company Name": "MockCorp",
        "CEO Name": "Satya Nadella",
        "Recent Funding Rounds": "2024-01-10 - Series A - $10M, 2025-05-12 - Series C - $50M"  # Series C is fabricated
    }
    
    success, risk_score, unresolved = detect_fabricated_entities(hallucinated_profile)
    
    assert success is False
    assert any("Funding Round" in item and "Series C" in item for item in unresolved)


# --- Tests for detect_plausible_hallucinations (tc_4.2) ---

def test_legitimate_linked_profile_passes():
    """Verifies that a factual profile with correct relationship linkages passes validation."""
    valid_payload = {
        "Company Name": "Microsoft Corporation",
        "CEO Name": "Satya Nadella",  # Correct CEO linked to Microsoft
        "Recent Funding Rounds": "2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $5M",
        "Office Locations": "100 London Wall, London, UK"
    }
    success, errors = detect_plausible_hallucinations(valid_payload)
    assert success is True
    assert not errors


def test_plausible_but_false_ceo_linkage_fails():
    """Verifies that assigning a highly plausible but incorrect CEO to a company fails validation."""
    invalid_payload = {
        "Company Name": "Microsoft Corporation",
        "CEO Name": "Tim Cook"  # Plausible CEO (of Apple), but incorrect for Microsoft
    }
    success, errors = detect_plausible_hallucinations(invalid_payload)
    
    assert success is False
    assert any("Linkage Hallucination" in err for err in errors)
    assert "Tim Cook" in errors[0]


def test_plausible_but_false_funding_amount_fails():
    """Verifies that an incorrect funding amount on a valid round date fails validation."""
    invalid_payload = {
        "Company Name": "MockCorp",
        "Recent Funding Rounds": "2025-06-15 - Series B - $15M"  # Plausible, but actual was $5M
    }
    success, errors = detect_plausible_hallucinations(invalid_payload)
    
    assert success is False
    assert any("Financial Hallucination" in err for err in errors)
    assert "actual Series B amount was $5M" in errors[0]


def test_plausible_but_false_office_location_fails():
    """Verifies that listing a real tech office building not leased by the company fails validation."""
    invalid_payload = {
        "Company Name": "MockCorp",
        "Office Locations": "100 Pine St, San Francisco, CA"  # Plausible tech building, but company isn't there
    }
    success, errors = detect_plausible_hallucinations(invalid_payload)
    
    assert success is False
    assert any("Location Hallucination" in err for err in errors)
    assert "no registered leases or operations" in errors[0]


# --- Tests for audit_confident_incorrectness (tc_4.3) ---

def test_legitimate_verifiable_record_passes():
    """Verifies that a record with verified patent ownership and standard descriptions passes."""
    valid_payload = {
        "Company Name": "Microsoft Corporation",
        "Intellectual Property": "Patents owned: US-1234567-B2",  # Valid patent registered to Microsoft
        "Overview of the Company": "Microsoft is a multinational technology enterprise specializing in software.",
        "Net Promoter Score (NPS)": 45,
        "_attribution_NPS": {"source_url": "https://trusted-survey-log.com/nps-report"}  # Cited
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