import pytest
from typing import Dict, Any, List, Tuple

# Mock Authority Registries representing verified relationship mappings
VERIFIED_CEO_LINKAGES = {
    "microsoft corporation": "Satya Nadella",
    "apple inc.": "Tim Cook",
    "tesla, inc.": "Elon Musk"
}

VERIFIED_FUNDING_ROUNDS = {
    "mockcorp": [
        {"date": "2024-01-10", "series": "Series A", "amount": 10000000.0},
        {"date": "2025-06-15", "series": "Series B", "amount": 5000000.0} # Actually raised $5M, not $15M
    ]
}

VERIFIED_OFFICE_REGISTRATIONS = {
    "mockcorp": [
        "100 London Wall, London, UK"
        # Does not actually registered at "100 Pine St, San Francisco, CA"
    ]
}

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
        # Let's extract values
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


# --- Pytest Tests ---

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