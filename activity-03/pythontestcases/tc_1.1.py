import re
import pytest

# Compilation of metadata regex patterns
COMPANY_NAME_PATTERN = re.compile(r"^[\w\s&.,\-\(\)'\u00C0-\u017F]+$")
SHORT_NAME_PATTERN = re.compile(r"^[\w\s&.\-]+$")

def validate_company_name(name: str) -> bool:
    """
    Validates the 'Company Name' based on schema rules:
    - Must not be None/Null.
    - Trimmed constraint (no leading or trailing whitespace).
    - Length between 2 and 255 characters.
    - Matches specified regex pattern.
    """
    if name is None:
        return False
    
    # Check leading/trailing spaces
    if name != name.strip():
        return False
        
    # Check length constraints
    if not (2 <= len(name) <= 255):
        return False
        
    # Regex match check
    if not COMPANY_NAME_PATTERN.match(name):
        return False
        
    return True

def validate_short_name(name: str) -> bool:
    """
    Validates the 'Short Name' based on schema rules:
    - Nullable, but if provided, must meet specifications.
    - Length between 2 and 100 characters.
    - Matches specified regex pattern.
    """
    if name is None:
        return True  # Nullable field
        
    if name != name.strip():
        return False

    if not (2 <= len(name) <= 100):
        return False
        
    if not SHORT_NAME_PATTERN.match(name):
        return False
        
    return True

# --- Test Executions ---

@pytest.mark.parametrize("valid_name", [
    "Microsoft Corporation",
    "Apple Inc.",
    "Tesla, Inc.",
    "L'Oréal S.A.",
    "M&S Group",
    "Bio-Tech (Global) Inc."
])
def test_company_name_valid_inputs(valid_name):
    """Verifies that standard, well-formed legal company names pass validation."""
    assert validate_company_name(valid_name) is True, f"Failed validation for valid company name: {valid_name}"

@pytest.mark.parametrize("invalid_name", [
    " A",                 # Leading space
    "Apple Inc. ",        # Trailing space
    "A",                  # Too short (length < 2)
    "Microsoft 🚀 Ltd",   # Contains emojis/illegal character
    "",                   # Empty string
])
def test_company_name_invalid_inputs(invalid_name):
    """Verifies that edge cases and poorly formatted legal company names fail validation."""
    assert validate_company_name(invalid_name) is False, f"Unexpectedly passed validation for invalid company name: {invalid_name}"

@pytest.mark.parametrize("valid_short_name", [
    "Microsoft",
    "Apple",
    "Tesla",
    "M&S",
    "Bio-Tech",
    None                  # Nullable check
])
def test_short_name_valid_inputs(valid_short_name):
    """Verifies that standard, well-formatted short names or brand aliases pass validation."""
    assert validate_short_name(valid_short_name) is True, f"Failed validation for valid short name: {valid_short_name}"

@pytest.mark.parametrize("invalid_short_name", [
    "A",                  # Too short (length < 2)
    "Tesla!",             # Illegal character '!'
    "Microsoft  ",        # Trailing space
    "A" * 101             # Exceeds maximum boundary of 100
])
def test_short_name_invalid_inputs(invalid_short_name):
    """Verifies that invalid short names fail validation."""
    assert validate_short_name(invalid_short_name) is False, f"Unexpectedly passed validation for invalid short name: {invalid_short_name}"