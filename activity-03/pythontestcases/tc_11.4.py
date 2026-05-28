import pytest
from typing import Dict, Any, List, Tuple

# Mock Registry mapping verified legal names to their corresponding famous acronyms and domains
ACRONYM_REGISTRY = {
    "international business machines corporation": {
        "legal_name": "International Business Machines Corporation",
        "short_name": "IBM",
        "domain": "ibm.com"
    },
    "american telephone & telegraph company": {
        "legal_name": "American Telephone & Telegraph Company",
        "short_name": "AT&T",
        "domain": "att.com"
    },
    "minnesota mining and manufacturing company": {
        "legal_name": "Minnesota Mining and Manufacturing Company",
        "short_name": "3M",
        "domain": "3m.com"
    }
}

def resolve_and_validate_acronym_coherence(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Holistically resolves and standardizes abbreviation parameters:
    1. If Company Name is passed as an acronym (e.g. 'IBM'), looks up and populates the full legal name, 
       storing 'IBM' as the Short Name.
    2. If Company Name is passed as a full legal name, automatically populates Short Name if left NULL.
    3. Blocks ingestion and raises an error if an ingested acronym conflicts with the legal name.
    """
    errors = []
    resolved_payload = payload.copy()
    
    ingested_company = str(payload.get("Company Name", "")).strip()
    ingested_short = str(payload.get("Short Name", "")).strip() if payload.get("Short Name") else ""
    ingested_url = str(payload.get("Website URL", "")).lower()

    # Create lookups
    by_legal = {k: v for k, v in ACRONYM_REGISTRY.items()}
    by_short = {v["short_name"].lower(): v for k, v in ACRONYM_REGISTRY.items()}

    resolved_entry = None

    # Step 1: Detect if Company Name is a registered legal name
    if ingested_company.lower() in by_legal:
        resolved_entry = by_legal[ingested_company.lower()]
    # Step 2: Detect if Company Name is a registered acronym
    elif ingested_company.lower() in by_short:
        resolved_entry = by_short[ingested_company.lower()]
    # Step 3: Detect if Short Name is a registered acronym
    elif ingested_short.lower() in by_short:
        resolved_entry = by_short[ingested_short.lower()]

    if resolved_entry:
        # Check for conflicts between ingested fields
        expected_legal = resolved_entry["legal_name"]
        expected_short = resolved_entry["short_name"]
        
        # Verify no clashing if both were populated
        if ingested_company == expected_short and ingested_short and ingested_short != expected_short:
            errors.append(f"Clash Error: Ingested Short Name '{ingested_short}' conflicts with resolved acronym '{expected_short}'.")
        elif ingested_company == expected_legal and ingested_short and ingested_short != expected_short:
            errors.append(f"Clash Error: Ingested Short Name '{ingested_short}' conflicts with resolved acronym '{expected_short}' for legal entity '{expected_legal}'.")

        # Verify Website URL doesn't clash with resolved domain
        expected_domain = resolved_entry["domain"]
        if ingested_url and expected_domain not in ingested_url:
            errors.append(f"Lineage Error: Website URL '{ingested_url}' does not match resolved entity domain '{expected_domain}'.")

        # If clean, normalize the payload
        if not errors:
            resolved_payload["Company Name"] = expected_legal
            resolved_payload["Short Name"] = expected_short

    return len(errors) == 0, resolved_payload, errors


# --- Pytest Tests ---

def test_resolve_by_acronym_only_success():
    """Verifies that ingesting with only an acronym (e.g. 'IBM') successfully populates full legal names."""
    payload = {
        "Company Name": "IBM",
        "Website URL": "https://www.ibm.com"
    }
    success, resolved, errors = resolve_and_validate_acronym_coherence(payload)
    
    assert success is True
    assert resolved["Company Name"] == "International Business Machines Corporation"
    assert resolved["Short Name"] == "IBM"
    assert not errors

def test_resolve_by_legal_name_populates_acronym():
    """Verifies that ingesting with a legal name successfully populates its famous acronym alias."""
    payload = {
        "Company Name": "American Telephone & Telegraph Company",
        "Website URL": "https://www.att.com",
        "Short Name": None
    }
    success, resolved, errors = resolve_and_validate_acronym_coherence(payload)
    
    assert success is True
    assert resolved["Company Name"] == "American Telephone & Telegraph Company"
    assert resolved["Short Name"] == "AT&T"
    assert not errors

def test_conflicting_aliases_fail_validation():
    """Verifies that pairing an unrelated legal name and acronym (e.g., IBM + AT&T) fails validation."""
    invalid_payload = {
        "Company Name": "International Business Machines Corporation",
        "Short Name": "AT&T",  # Conflicting acronym
        "Website URL": "https://www.ibm.com"
    }
    success, resolved, errors = resolve_and_validate_acronym_coherence(invalid_payload)
    
    assert success is False
    assert any("conflicts with resolved acronym" in err for err in errors)

def test_conflicting_website_domain_fails_validation():
    """Verifies that having a website URL mismatching the resolved entity domain fails validation."""
    invalid_payload = {
        "Company Name": "IBM",
        "Website URL": "https://www.att.com"  # Incorrect domain
    }
    success, resolved, errors = resolve_and_validate_acronym_coherence(invalid_payload)
    
    assert success is False
    assert any("does not match resolved entity domain" in err for err in errors)