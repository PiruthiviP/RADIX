import pytest
from typing import List, Tuple

# Mock Master Registries representing official verified databases
VERIFIED_COMPANIES = {"Microsoft Corporation", "Apple Inc.", "Tesla Inc.", "Google LLC", "Amazon.com Inc."}
VERIFIED_BRANDS = {"Microsoft", "Apple", "Tesla", "Google", "Amazon"}
VERIFIED_INVESTORS = {"Sequoia Capital", "Andreessen Horowitz", "a16z", "Y Combinator"}
VERIFIED_CEOS = {"Satya Nadella", "Tim Cook", "Elon Musk", "Sundar Pichai", "Andy Jassy"}

def validate_company_name(name: str) -> Tuple[bool, str]:
    """
    Validates legal Company Name against verified registry.
    Catches abbreviations, truncations, and spelling errors.
    """
    if not name or len(name) < 2:
        return False, "Input is too short to be a valid legal name."
    
    if name in VERIFIED_COMPANIES:
        return True, "Valid legal name."
    
    # Check for common truncated entries
    if any(name.lower() in verified.lower() for verified in VERIFIED_COMPANIES):
        return False, "Incomplete or heavily abbreviated legal name."
        
    return False, "Legal name could not be resolved in the government registry."

def validate_short_name(name: str) -> Tuple[bool, str]:
    """Validates Short Name against verified branding databases."""
    if not name or len(name) < 2:
        return False, "Input too short."
        
    if name in VERIFIED_BRANDS:
        return True, "Valid short name."
        
    return False, "Short name does not match verified branding assets."

def validate_competitors_list(competitors_str: str) -> Tuple[bool, List[str]]:
    """
    Parses a comma-separated list of competitors.
    Returns a boolean success flag and a list of malformed/unresolved entries.
    """
    if not competitors_str:
        return False, ["Empty Input"]
        
    competitors = [c.strip() for c in competitors_str.split(",") if c.strip()]
    unresolved = []
    
    for comp in competitors:
        # Check against both full legal names and short brand names
        if comp not in VERIFIED_COMPANIES and comp not in VERIFIED_BRANDS:
            unresolved.append(comp)
            
    return len(unresolved) == 0, unresolved

def validate_person_name(name: str) -> Tuple[bool, str]:
    """Validates a person's name (CEO or primary contact) for completeness."""
    if not name:
        return False, "Name cannot be empty."
        
    # Check for single initial inputs (e.g., "S", "J.")
    parts = [p.replace(".", "").strip() for p in name.split()]
    if any(len(p) <= 1 for p in parts):
        return False, "Name contains truncated single initials or incomplete values."
        
    return True, "Valid format."


# --- Pytest Tests ---

@pytest.mark.parametrize("malformed_company", ["Microsft", "App", "Goog"])
def test_malformed_company_name(malformed_company):
    """Verifies that misspelled or heavily truncated company legal names are rejected."""
    success, message = validate_company_name(malformed_company)
    assert success is False
    assert "Incomplete" in message or "could not be resolved" in message

@pytest.mark.parametrize("malformed_short_name", ["Microsft", "Goog"])
def test_malformed_short_name(malformed_short_name):
    """Verifies that misspelled or truncated brand names are caught."""
    success, message = validate_short_name(malformed_short_name)
    assert success is False
    assert "does not match" in message

def test_malformed_competitor_list():
    """Verifies that a list containing misspelled competitor names flags only the malformed entities."""
    input_list = "Microsft, Apple Inc., Tesl"
    success, unresolved = validate_competitors_list(input_list)
    
    assert success is False
    assert "Microsft" in unresolved
    assert "Tesl" in unresolved
    assert "Apple Inc." not in unresolved

@pytest.mark.parametrize("malformed_name", ["S", "S. J. S.", "J. René"])
def test_malformed_person_name(malformed_name):
    """Verifies that incomplete, heavily abbreviated, or initial-only person names fail validation."""
    success, message = validate_person_name(malformed_name)
    assert success is False
    assert "truncated" in message