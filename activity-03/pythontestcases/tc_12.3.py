import re
import pytest
from typing import Dict, Any

# Nature of Company Enum Match: ^(Private|Public|Subsidiary|Partnership|Non-Profit|Govt)$
NATURE_OF_COMPANY_REGEX = re.compile(r"^(Private|Public|Subsidiary|Partnership|Non-Profit|Govt)$")

# Keywords in company description that indicate subsidiary ownership
PARENT_OWNERSHIP_KEYWORDS = ["owned by", "subsidiary of", "acquired by", "part of", "division of"]


def validate_nature_of_company(record: Dict[str, Any]) -> bool:
    """
    Validates formatting and enum compliance of 'Nature of Company',
    and checks consistency against funding rounds and description summaries.
    """
    nature = record.get("Nature of Company")
    company_name = record.get("Company Name")
    funding_rounds = record.get("Recent Funding Rounds")
    overview = record.get("Overview of the Company")
    
    # 1. Nullability Check
    if not nature:
        raise ValueError("Field Validation Error: 'Nature of Company' is Not Null.")
        
    # 2. Case Normalization to Match Regex
    normalized_nature = nature.strip().title()
    if normalized_nature == "Non-Profit" or normalized_nature == "Nonprofit":
        normalized_nature = "Non-Profit"
        
    if not NATURE_OF_COMPANY_REGEX.match(normalized_nature):
        raise ValueError(
            f"Regex Pattern Error: '{nature}' is not a recognized legal structure enum. "
            f"Expected: Private, Public, Subsidiary, Partnership, Non-Profit, Govt."
        )
        
    # Write back normalized value
    record["Nature of Company"] = normalized_nature
    
    # 3. Cross-Field Business Logic Validation
    # Rule A: Publicly traded companies do not raise typical startup venture series rounds
    if normalized_nature == "Public" and funding_rounds:
        # Check if the funding rounds text contains venture indicators (Series A/B/C/D, Seed)
        venture_pattern = re.compile(r"(Series\s+[A-Z]|Seed|Angel)", re.IGNORECASE)
        if venture_pattern.search(str(funding_rounds)):
            raise ValueError(
                f"Classification Mismatch: '{company_name}' is marked as 'Public', "
                f"but has private venture funding rounds: '{funding_rounds}'."
            )
            
    # Rule B: Subsidiary structures should exhibit parent relationship markers in their overview
    if normalized_nature == "Subsidiary" and overview:
        normalized_overview = overview.lower()
        has_ownership_marker = any(marker in normalized_overview for marker in PARENT_OWNERSHIP_KEYWORDS)
        if not has_ownership_marker:
            raise ValueError(
                f"Classification Mismatch: '{company_name}' is classified as a 'Subsidiary', "
                f"but its overview does not outline parent-subsidiary relationship terms."
            )
            
    return True


# --- Pytest Suite ---

def test_private_company_with_funding_success():
    """
    Validates typical private venture-backed startup profile.
    """
    record = {
        "Company Name": "Space Exploration Technologies Corp.",
        "Nature of Company": "Private",
        "Recent Funding Rounds": "2025-01-15 - $250,000,000",
        "Overview of the Company": "An independent aerospace manufacturer founded by Elon Musk."
    }
    assert validate_nature_of_company(record) is True


def test_public_company_success():
    """
    Validates public enterprise without venture rounds.
    """
    record = {
        "Company Name": "Apple Inc.",
        "Nature of Company": "Public",
        "Recent Funding Rounds": None,
        "Overview of the Company": "A global consumer electronics manufacturer."
    }
    assert validate_nature_of_company(record) is True


def test_subsidiary_company_success():
    """
    Validates subsidiary status when supported by description ownership terms.
    """
    record = {
        "Company Name": "WhatsApp LLC",
        "Nature of Company": "Subsidiary",
        "Recent Funding Rounds": None,
        "Overview of the Company": "A messaging platform owned by Meta Platforms, Inc."
    }
    assert validate_nature_of_company(record) is True


def test_lowercase_normalization_success():
    """
    Ensures incorrect casing (e.g., 'subsidiary') is corrected to match the regex.
    """
    record = {
        "Company Name": "WhatsApp LLC",
        "Nature of Company": "subsidiary",
        "Recent Funding Rounds": None,
        "Overview of the Company": "A messaging platform owned by Meta."
    }
    assert validate_nature_of_company(record) is True
    assert record["Nature of Company"] == "Subsidiary"


def test_invalid_structure_enum_fails():
    """
    Rejects legal structure values that are outside the standardized enum list.
    """
    record = {
        "Company Name": "SpaceX",
        "Nature of Company": "private-owned",  # Disallowed structure term
        "Recent Funding Rounds": "2025-01-15 - $250,000,000"
    }
    with pytest.raises(ValueError, match="is not a recognized legal structure enum"):
        validate_nature_of_company(record)


def test_public_with_venture_rounds_fails():
    """
    Flags anomalies where a public company lists active private venture capital rounds.
    """
    record = {
        "Company Name": "Apple Inc.",
        "Nature of Company": "Public",
        "Recent Funding Rounds": "2025-01-15 - Series B - $50,000,000",  # Venture round on public corp
        "Overview of the Company": "A global consumer electronics manufacturer."
    }
    with pytest.raises(ValueError, match="is marked as 'Public', but has private venture funding"):
        validate_nature_of_company(record)


def test_subsidiary_lacking_ownership_text_fails():
    """
    Flags subsidiaries whose overview reports no parent-ownership relationships.
    """
    record = {
        "Company Name": "WhatsApp LLC",
        "Nature of Company": "Subsidiary",
        "Recent Funding Rounds": None,
        "Overview of the Company": "An independent messaging platform."  # Mismatch: claims to be independent
    }
    with pytest.raises(ValueError, match="is classified as a 'Subsidiary', but its overview does not outline"):
        validate_nature_of_company(record)