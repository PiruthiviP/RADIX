import pytest
from typing import Dict, Any, Tuple

# Mock Database showing multiple entities sharing the same generic name/alias
ENTITY_DATABASE = {
    "companies": [
        {"legal_name": "Delta Air Lines, Inc.", "alias": "Delta", "domain": "delta.com", "sector": "Airlines"},
        {"legal_name": "Delta Faucet Company", "alias": "Delta", "domain": "deltafaucet.com", "sector": "Manufacturing"},
        {"legal_name": "Mercury Technologies", "alias": "Mercury", "domain": "mercury.com", "sector": "Financials"},
        {"legal_name": "Mercury Insurance Group", "alias": "Mercury", "domain": "mercuryinsurance.com", "sector": "Insurance"}
    ],
    "ceos": [
        {"name": "John Smith", "company": "Delta Air Lines, Inc.", "linkedin": "linkedin.com/in/john-smith-delta"},
        {"name": "John Smith", "company": "Delta Faucet Company", "linkedin": "linkedin.com/in/john-smith-faucet"}
    ],
    "investors": [
        {"legal_name": "Founders Fund", "alias": "Founders"},
        {"legal_name": "Founders Circle Capital", "alias": "Founders"}
    ]
}

def resolve_company_entity(name: str, domain: str = None, sector: str = None) -> Tuple[str, str]:
    """
    Simulates entity resolution on 'Company Name' or 'Short Name'.
    - Returns ('SUCCESS', legal_name) if resolved uniquely.
    - Returns ('AMBIGUOUS', message) if multiple entities match and secondary context is missing/incorrect.
    - Returns ('UNRESOLVED', message) if no match is found.
    """
    if not name:
        return "UNRESOLVED", "Empty input name."

    # Find matching companies by legal name or alias
    matches = [
        c for c in ENTITY_DATABASE["companies"]
        if c["legal_name"].lower() == name.lower() or c["alias"].lower() == name.lower()
    ]

    if not matches:
        return "UNRESOLVED", f"No database matches found for '{name}'."

    if len(matches) == 1:
        return "SUCCESS", matches[0]["legal_name"]

    # Ambiguity detected: attempt to resolve with secondary context (domain or sector)
    if domain:
        domain_matches = [c for c in matches if c["domain"].lower() == domain.lower()]
        if len(domain_matches) == 1:
            return "SUCCESS", domain_matches[0]["legal_name"]

    if sector:
        sector_matches = [c for c in matches if c["sector"].lower() == sector.lower()]
        if len(sector_matches) == 1:
            return "SUCCESS", sector_matches[0]["legal_name"]

    matched_names = ", ".join([c["legal_name"] for c in matches])
    return "AMBIGUOUS", f"Input matches multiple entities: [{matched_names}]. Provide domain or sector to resolve."

def resolve_ceo_entity(ceo_name: str, company_name: str = None, linkedin_url: str = None) -> Tuple[str, str]:
    """
    Simulates entity resolution on 'CEO Name'.
    - Rejects common names unless reconciled with company context or profile URL.
    """
    matches = [c for c in ENTITY_DATABASE["ceos"] if c["name"].lower() == ceo_name.lower()]
    
    if not matches:
        return "UNRESOLVED", f"No CEO found matching '{ceo_name}'."
        
    if len(matches) == 1:
        return "SUCCESS", matches[0]["name"]
        
    # Ambiguity: try company correlation
    if company_name:
        company_matches = [c for c in matches if c["company"].lower() == company_name.lower()]
        if len(company_matches) == 1:
            return "SUCCESS", company_matches[0]["name"]
            
    # Ambiguity: try linkedin correlation
    if linkedin_url:
        linkedin_matches = [c for c in matches if c["linkedin"].lower() == linkedin_url.lower()]
        if len(linkedin_matches) == 1:
            return "SUCCESS", linkedin_matches[0]["name"]
            
    return "AMBIGUOUS", f"Multiple executives named '{ceo_name}'. Reconcile with company or LinkedIn URL."


# --- Pytest Tests ---

def test_resolve_unique_company():
    """Verifies that an unambiguous, fully qualified company name resolves directly."""
    status, result = resolve_company_entity("Delta Air Lines, Inc.")
    assert status == "SUCCESS"
    assert result == "Delta Air Lines, Inc."

def test_resolve_ambiguous_company_without_context():
    """Verifies that a generic alias flags ambiguity when context is missing."""
    status, message = resolve_company_entity("Delta")
    assert status == "AMBIGUOUS"
    assert "matches multiple entities" in message

def test_resolve_ambiguous_company_with_domain_context():
    """Verifies that generic alias ambiguity is resolved with domain context."""
    status, result = resolve_company_entity("Delta", domain="deltafaucet.com")
    assert status == "SUCCESS"
    assert result == "Delta Faucet Company"

def test_resolve_ambiguous_company_with_sector_context():
    """Verifies that generic alias ambiguity is resolved with industry sector context."""
    status, result = resolve_company_entity("Mercury", sector="Insurance")
    assert status == "SUCCESS"
    assert result == "Mercury Insurance Group"

def test_resolve_common_ceo_name_without_context():
    """Verifies that common executive names are flagged as ambiguous without company context."""
    status, message = resolve_ceo_entity("John Smith")
    assert status == "AMBIGUOUS"
    assert "Multiple executives" in message

def test_resolve_common_ceo_name_with_company_context():
    """Verifies that common executive names resolve successfully when paired with corporate context."""
    status, result = resolve_ceo_entity("John Smith", company_name="Delta Air Lines, Inc.")
    assert status == "SUCCESS"
    assert result == "John Smith"