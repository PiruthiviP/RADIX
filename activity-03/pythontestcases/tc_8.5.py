import re
import pytest
from typing import List, Tuple

# Strict regex patterns matching metadata constraints exactly
COUNTRIES_OPERATING_RE = re.compile(r"^([A-Za-z\s]+)(,\s*[A-Za-z\s]+)*$")
KEY_COMPETITORS_RE = re.compile(r"^[\w\s&.,\-/]+(,\s*[\w\s&.,\-/]+)*$")
KEY_INVESTORS_RE = re.compile(r"^[\w\s&.,\-\(\)]+(,\s*[\w\s&.,\-\(\)]+)*$")

# List of illegal delimiters that commonly cause list formatting corruption
ILLEGAL_DELIMITERS = [";", "|", " / ", " & "]

def validate_comma_separated_list(val: str, regex: re.Pattern) -> Tuple[bool, str, List[str]]:
    """
    Validates that a multi-value string is cleanly formatted as a comma-separated list:
    - Fails if any illegal delimiters (semicolons, pipes, slashes, ampersands) are found.
    - Confirms the entire string matches the specified metadata regex pattern.
    - Returns (success, log_message, parsed_list_elements)
    """
    if not val:
        return False, "Empty list input.", []

    # Check for forbidden delimiters on the wire
    for delim in ILLEGAL_DELIMITERS:
        if delim in val:
            return False, f"Delimiter Error: Found illegal list separator '{delim.strip()}'. Use commas instead.", []

    if not regex.match(val):
        return False, "Regex Error: String does not conform to strict comma-separated list boundaries.", []

    # Split and clean individual list elements
    elements = [item.strip() for item in val.split(",") if item.strip()]
    return True, "List formatted and validated successfully.", elements


# --- Pytest Tests ---

@pytest.mark.parametrize("valid_countries, expected_list", [
    ("US, UK, Germany", ["US", "UK", "Germany"]),
    ("United States, United Kingdom", ["United States", "United Kingdom"])
])
def test_valid_countries_list_formatting(valid_countries, expected_list):
    """Verifies that countries lists separated cleanly by commas pass and parse successfully."""
    success, msg, elements = validate_comma_separated_list(valid_countries, COUNTRIES_OPERATING_RE)
    assert success is True
    assert elements == expected_list

@pytest.mark.parametrize("invalid_countries", [
    "US; UK; Germany",      # Semi-colon delimiter
    "US | UK | Germany",    # Pipe delimiter
    "US / UK",              # Slash delimiter
    "US & UK"               # Ampersand delimiter
])
def test_invalid_countries_list_rejected(invalid_countries):
    """Verifies that non-comma list delimiters in countries operating lists are strictly rejected."""
    success, msg, elements = validate_comma_separated_list(invalid_countries, COUNTRIES_OPERATING_RE)
    assert success is False
    assert "Delimiter Error" in msg or "Regex Error" in msg

@pytest.mark.parametrize("valid_competitors", [
    "Apple Inc., Tesla, Inc., Google LLC",
    "M&S Group, Bio-Tech (Global) Inc."
])
def test_valid_competitors_list_formatting(valid_competitors):
    """Verifies that competitor lists with ampersands and periods inside values, but comma-separated, pass."""
    success, msg, elements = validate_comma_separated_list(valid_competitors, KEY_COMPETITORS_RE)
    assert success is True

@pytest.mark.parametrize("invalid_competitors", [
    "Apple Inc. / Tesla Inc.",
    "Apple Inc.; Tesla Inc."
])
def test_invalid_competitors_list_rejected(invalid_competitors):
    """Verifies that competitor lists containing non-comma delimiters fail."""
    success, msg, elements = validate_comma_separated_list(invalid_competitors, KEY_COMPETITORS_RE)
    assert success is False

@pytest.mark.parametrize("valid_investors", [
    "Sequoia, Andreessen Horowitz, Founders Fund (US)",
    "a16z, Y Combinator"
])
def test_valid_investors_list_formatting(valid_investors):
    """Verifies that investor lists containing parenthetical details but cleanly comma-separated pass."""
    success, msg, elements = validate_comma_separated_list(valid_investors, KEY_INVESTORS_RE)
    assert success is True

@pytest.mark.parametrize("invalid_investors", [
    "Sequoia; a16z",
    "Sequoia | a16z"
])
def test_invalid_investors_list_rejected(invalid_investors):
    """Verifies that non-comma delimiters in investor lists are rejected."""
    success, msg, elements = validate_comma_separated_list(invalid_investors, KEY_INVESTORS_RE)
    assert success is False