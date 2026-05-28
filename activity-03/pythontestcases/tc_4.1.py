import re
import pytest
from typing import Dict, Any, List, Tuple

# Mock Authority Registries representing verified real-world entities
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


# --- Pytest Tests ---

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