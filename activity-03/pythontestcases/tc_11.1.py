import pytest
from typing import Dict, Any, Tuple, List

# Mock Enterprise Knowledge Base containing distinct corporations sharing identical names/aliases
KNOWLEDGE_BASE = [
    {
        "id": "target_corp_us",
        "legal_name": "Target Corporation",
        "alias": "Target",
        "domain": "target.com",
        "hq_city": "Minneapolis",
        "hq_state_country": "MN",
        "sector": "Retailing",
        "ceo": "Brian Cornell"
    },
    {
        "id": "target_agency_uk",
        "legal_name": "Target Brand Agency Ltd",
        "alias": "Target",
        "domain": "targetagency.co.uk",
        "hq_city": "London",
        "hq_state_country": "UK",
        "sector": "Advertising",
        "ceo": "John Doe"
    }
]

def resolve_identical_entity_ambiguity(payload: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Holistically disambiguates identical company names using parameter clustering.
    - Compares domain (from Website URL), city/country (from HQ), GICS sector, and CEO.
    - Scores candidates in the Knowledge Base (0 to 4 matches).
    Returns: (resolution_status, resolved_entity_id, log_message)
    """
    company_name = str(payload.get("Company Name", "")).strip().lower()
    website = str(payload.get("Website URL", "")).lower()
    hq = str(payload.get("Company Headquarters", "")).lower()
    sector = str(payload.get("Focus Sectors / Industries", "")).lower()
    ceo = str(payload.get("CEO Name", "")).lower()

    if not company_name:
        return "UNRESOLVED", "None", "Aborted: Empty company name."

    # Filter candidates in knowledge base sharing the same alias/name
    candidates = [c for c in KNOWLEDGE_BASE if c["alias"].lower() == company_name]
    if not candidates:
        return "UNRESOLVED", "None", f"No matching entities found in KB for '{company_name}'."

    scores = {}
    for cand in candidates:
        score = 0
        
        # 1. Match Domain
        if cand["domain"] in website:
            score += 1
            
        # 2. Match Headquarters
        if cand["hq_city"].lower() in hq or cand["hq_state_country"].lower() in hq:
            score += 1
            
        # 3. Match Sector
        if cand["sector"].lower() in sector:
            score += 1
            
        # 4. Match CEO
        if cand["ceo"].lower() == ceo:
            score += 1
            
        scores[cand["id"]] = score

    # Find highest scoring candidate
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_cand_id, best_score = sorted_scores[0]
    
    # Validation logic threshold boundaries:
    # - Must match at least 2 distinct parameters to be confident.
    # - If there's a tie or a close conflict (e.g., both score 2), flag as conflict.
    if best_score < 2:
        return "UNRESOLVED", "None", f"Ambiguous: Insufficient parameter linkage to resolve '{payload.get('Company Name')}' (Best score: {best_score})."
        
    if len(sorted_scores) > 1:
        runner_up_id, runner_up_score = sorted_scores[1]
        if best_score == runner_up_score or (best_score - runner_up_score < 2 and best_score < 4):
            return "CONFLICT", "None", (
                f"Conflicting payload: High correlation with multiple distinct entities. "
                f"[{best_cand_id}] scored {best_score}, while [{runner_up_id}] scored {runner_up_score}. Holds for audit."
            )

    return "SUCCESS", best_cand_id, f"Resolved successfully to '{best_cand_id}' (Score: {best_score}/4)."


# --- Pytest Tests ---

def test_resolve_retail_target_giant_success():
    """Verifies that the retail giant is successfully resolved when its parameters align."""
    retail_payload = {
        "Company Name": "Target",
        "Website URL": "https://www.target.com",
        "Company Headquarters": "Minneapolis, MN",
        "Focus Sectors / Industries": "Consumer Discretionary, Retailing, Supermarkets",
        "CEO Name": "Brian Cornell"
    }
    status, entity_id, msg = resolve_identical_entity_ambiguity(retail_payload)
    
    assert status == "SUCCESS"
    assert entity_id == "target_corp_us"
    assert "Score: 4/4" in msg

def test_resolve_target_branding_agency_success():
    """Verifies that the branding agency is successfully resolved when its parameters align."""
    agency_payload = {
        "Company Name": "Target",
        "Website URL": "https://targetagency.co.uk",
        "Company Headquarters": "London, UK",
        "Focus Sectors / Industries": "Advertising, Marketing Services",
        "CEO Name": "John Doe"
    }
    status, entity_id, msg = resolve_identical_entity_ambiguity(agency_payload)
    
    assert status == "SUCCESS"
    assert entity_id == "target_agency_uk"
    assert "Score: 4/4" in msg

def test_conflicting_parameters_flags_conflict():
    """Verifies that contradictory parameter mappings (e.g. Retailer website + Agency CEO) trigger a conflict lock."""
    conflicting_payload = {
        "Company Name": "Target",
        "Website URL": "https://www.target.com",  # Points to Retailer (US)
        "Company Headquarters": "Minneapolis, MN", # Points to Retailer (US)
        "Focus Sectors / Industries": "Advertising, Marketing Services", # Points to Agency (UK)
        "CEO Name": "John Doe"                     # Points to Agency (UK)
    }
    status, entity_id, msg = resolve_identical_entity_ambiguity(conflicting_payload)
    
    assert status == "CONFLICT"
    assert entity_id == "None"
    assert "Conflicting payload" in msg
    assert "target_corp_us" in msg
    assert "target_agency_uk" in msg

def test_insufficient_parameters_unresolved():
    """Verifies that having insufficient populated metadata values fails resolution, preventing wrong-entity mapping."""
    scant_payload = {
        "Company Name": "Target",
        "Website URL": "https://unrelated-domain.com",
        "Company Headquarters": "Seattle, WA"
    }
    status, entity_id, msg = resolve_identical_entity_ambiguity(scant_payload)
    
    assert status == "UNRESOLVED"
    assert entity_id == "None"
    assert "Insufficient parameter linkage" in msg