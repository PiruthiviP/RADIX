import re
import pytest
from typing import Dict, Any

# Valid legal name character regex based on schema: ^[\w\s&.,\-\(\)'\u00C0-\u017F]+$
LEGAL_NAME_REGEX = re.compile(r"^[\w\s&.,\-\(\)'\u00C0-\u017F]+$")

# Valid short name character regex based on schema: ^[\w\s&.\-]+$
SHORT_NAME_REGEX = re.compile(r"^[\w\s&.\-]+$")

# Prohibited corporate suffixes inside brand/short names
DISALLOWED_SHORT_NAME_SUFFIXES = ["inc", "inc.", "corp", "corp.", "ltd", "ltd.", "llc", "l.l.c.", "co", "co."]


def validate_legal_and_short_names(record: Dict[str, Any]) -> bool:
    """
    Validates structural rules and checks for ambiguity between official 
    legal entity names and common names.
    """
    legal_name = record.get("Company Name")
    short_name = record.get("Short Name")
    
    # 1. Company Name Nullability & Validation Rules
    if not legal_name:
        raise ValueError("Field Validation Error: 'Company Name' is not null.")
    
    if legal_name.strip() != legal_name:
        raise ValueError("Data Rule Error: 'Company Name' must trim leading/trailing spaces.")
        
    if not LEGAL_NAME_REGEX.match(legal_name):
        raise ValueError(f"Regex Pattern Error: '{legal_name}' contains disallowed characters or emojis.")
        
    # 2. Short Name Nullability & Validation Rules
    if short_name is not None:
        if short_name.strip() != short_name:
            raise ValueError("Data Rule Error: 'Short Name' must trim leading/trailing spaces.")
            
        if not SHORT_NAME_REGEX.match(short_name):
            raise ValueError(f"Regex Pattern Error: Short Name '{short_name}' contains disallowed characters.")
            
        if len(short_name) > 100:
            raise ValueError("Data Rule Error: 'Short Name' length must be <= 100 characters.")
            
        # 3. Disambiguation Check: Short Name should not contain formal corporate suffixes
        tokens = [token.strip(",.").lower() for token in short_name.split()]
        for suffix in DISALLOWED_SHORT_NAME_SUFFIXES:
            if suffix.strip(".") in tokens:
                raise ValueError(
                    f"Ambiguity Error: Short Name '{short_name}' should not contain formal corporate suffixes "
                    f"like '{suffix}' to remain distinct from full legal names."
                )
                
        # 4. Logical check: Short Name should generally not equal Legal Name if a suffix is dropped
        if short_name.lower() == legal_name.lower() and any(s in legal_name.lower() for s in DISALLOWED_SHORT_NAME_SUFFIXES):
            raise ValueError("Ambiguity Error: 'Short Name' is identical to full legal name. Corporate suffixes must be removed.")

    return True


# --- Pytest Suite ---

def test_meta_platforms_legal_vs_short_success():
    """
    Ensures that a properly separated Official Legal Name and clean common brand name are accepted.
    """
    valid_record = {
        "Company Name": "Meta Platforms, Inc.",
        "Short Name": "Meta"
    }
    assert validate_legal_and_short_names(valid_record) is True


def test_x_corp_vs_twitter_disambiguation():
    """
    Ensures that a rebranded mapping containing legal suffixes in the legal name and a clean short name is accepted.
    """
    valid_rebranded_record = {
        "Company Name": "X Corp.",
        "Short Name": "Twitter"
    }
    assert validate_legal_and_short_names(valid_rebranded_record) is True


def test_untrimmed_legal_name_fails():
    """
    Verifies that leading/trailing whitespaces in company name trigger validation failures.
    """
    invalid_record = {
        "Company Name": " Meta Platforms, Inc. ",
        "Short Name": "Meta"
    }
    with pytest.raises(ValueError, match="must trim leading/trailing spaces"):
        validate_legal_and_short_names(invalid_record)


def test_short_name_containing_legal_suffix_fails():
    """
    Verifies that corporate legal suffixes inside brand names are flagged to prevent confusion.
    """
    invalid_record = {
        "Company Name": "Meta Platforms, Inc.",
        "Short Name": "Meta Inc."
    }
    with pytest.raises(ValueError, match="should not contain formal corporate suffixes"):
        validate_legal_and_short_names(invalid_record)


def test_legal_name_regex_disallowed_emojis_fails():
    """
    Verifies that the legal name fails regex validation if emojis or non-standard characters exist.
    """
    invalid_record = {
        "Company Name": "Meta Platforms, Inc. 🌐",
        "Short Name": "Meta"
    }
    with pytest.raises(ValueError, match="contains disallowed characters or emojis"):
        validate_legal_and_short_names(invalid_record)