import json
import re
from typing import Dict, Any, List, Tuple, Optional
import pytest

# =====================================================================
# Constants, Registries, and Regex Patterns
# =====================================================================

# Schema Type Map representing key representative fields
SCHEMA_TYPE_REGISTRY = {
    "Company Name": str,
    "Year of Incorporation": int,
    "Overview of the Company": str,
    "Number of Offices (beyond HQ)": int,
    "Website Rating": float,
    "Glassdoor Rating": float,
    "Social Media Followers – Combined": int,
    "CEO Name": str,
    "Key Business Leaders": list,  # Expected parsed JSON array
    "Annual Profits": float,
    "Profitability Status": str
}

# Regex patterns matching URL boundaries
LOGO_RE = re.compile(r"^https?:\/\/.*\.(?:png|jpg|jpeg|svg|webp)(?:\?.*)?$")
WEBSITE_RE = re.compile(r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$")
LINKEDIN_COMPANY_RE = re.compile(r"^https?:\/\/(www\.)?linkedin\.com\/company\/[A-Za-z0-9_\-]+\/?$")
LINKEDIN_PROFILE_RE = re.compile(r"^https?:\/\/(www\.)?linkedin\.com\/in\/[A-Za-z0-9_\-]+\/?$")
VIDEO_RE = re.compile(r"^https?:\/\/(www\.)?(youtube\.com|vimeo\.com|youtu\.be)\/.*$")

# List-formatting regex constraints
COUNTRIES_OPERATING_RE = re.compile(r"^([A-Za-z\s]+)(,\s*[A-Za-z\s]+)*$")
KEY_COMPETITORS_RE = re.compile(r"^[\w\s&.,\-/]+(,\s*[\w\s&.,\-/]+)*$")
KEY_INVESTORS_RE = re.compile(r"^[\w\s&.,\-\(\)]+(,\s*[\w\s&.,\-\(\)]+)*$")

ILLEGAL_DELIMITERS = [";", "|", " / ", " & "]

# Schema Length limits representing boundary limits
# Key: (min_characters, max_characters)
SCHEMA_LENGTH_REGISTRY = {
    "Company Name": (2, 255),
    "Short Name": (2, 100),
    "Overview of the Company": (50, 5000),
    "Core Value Proposition": (20, 2000),
    "Vision": (10, 500),
    "CEO Name": (2, 100)
}


# =====================================================================
# Mock Network Client Simulation
# =====================================================================

class MockNetworkClient:
    """Simulates active HTTP request connections to evaluate URL validity."""
    def __init__(self):
        self.mock_web_registry = {
            "https://microsoft.com": {"status_code": 200, "content_type": "text/html"},
            "https://example.com/logo.png": {"status_code": 200, "content_type": "image/png"},
            "https://example.com/document.pdf": {"status_code": 200, "content_type": "application/pdf"},
            "https://linkedin.com/company/microsoft": {"status_code": 200, "content_type": "text/html"},
            "https://linkedin.com/in/satyanadella": {"status_code": 200, "content_type": "text/html"},
            "https://youtube.com/watch?v=123": {"status_code": 200, "content_type": "text/html"},
            "https://redirecting-site.com": {"status_code": 301, "redirect_to": "https://microsoft.com"},
            "https://brokenlink404.com": {"status_code": 404},
            "https://linkedin.com/company/deleted-page-404": {"status_code": 404},
            "https://youtube.com/watch?v=deletedvideo": {"status_code": 404}
        }

    def request(self, method: str, url: str, follow_redirects: bool = True) -> Dict[str, Any]:
        target_url = url.strip()
        response = self.mock_web_registry.get(target_url, {"status_code": 404})
        
        if response.get("status_code") in (301, 302) and follow_redirects:
            redirect_url = response.get("redirect_to")
            return self.request(method, redirect_url)
            
        return response


network_client = MockNetworkClient()


# =====================================================================
# Structural, URL, Content, and Length Validation Functions
# =====================================================================

def validate_record_data_types(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Performs holistic, record-level structural type checks.
    - Validates that populated fields match their exact schema-defined Python types.
    - Gracefully handles nullable fields (allows None without throwing type errors).
    - Specifically validates JSON array parsing for 'Key Business Leaders'.
    """
    errors = []

    for field_name, expected_type in SCHEMA_TYPE_REGISTRY.items():
        val = payload.get(field_name)
        
        # Safe skip for optional Nullable parameters set to None
        if val is None:
            continue
            
        # Special case: Key Business Leaders (expects list or valid JSON string parsing to list)
        if field_name == "Key Business Leaders":
            if isinstance(val, str):
                try:
                    parsed_json = json.loads(val)
                    if not isinstance(parsed_json, list):
                        errors.append(f"Type Error: '{field_name}' parsed from JSON string but is not a LIST structure.")
                except json.JSONDecodeError:
                    errors.append(f"JSON Parse Error: '{field_name}' contains invalid JSON formatting.")
            elif not isinstance(val, list):
                errors.append(f"Type Error: Field '{field_name}' must be of type LIST (JSON Array), got {type(val).__name__}.")
            continue

        # General type checking for atomic fields
        if not isinstance(val, expected_type):
            # Attempt safe float/int coercion for numeric types if passed as strings (standard DB practice)
            coerced = False
            if expected_type in (int, float) and isinstance(val, str):
                try:
                    if expected_type == int:
                        int(val)
                    else:
                        float(val)
                    coerced = True
                except ValueError:
                    pass
            
            if not coerced:
                errors.append(
                    f"Type Error: Field '{field_name}' must be of type {expected_type.__name__}, "
                    f"but got {type(val).__name__} (Value: '{val}')."
                )

    return len(errors) == 0, errors


def validate_website_url(url: str) -> Tuple[bool, str]:
    """Validates Website URL regex and active HTTP resolution (supporting redirects)."""
    if not WEBSITE_RE.match(url):
        return False, "Regex Error: Invalid URL structure."
        
    response = network_client.request("GET", url)
    if response.get("status_code") == 200:
        return True, "Valid Website URL resolved successfully."
    return False, f"Connection Error: Server returned status {response.get('status_code')}."


def validate_logo_url(url: str) -> Tuple[bool, str]:
    """Validates Logo URL regex, active HTTP resolution, and image MIME-type."""
    if not LOGO_RE.match(url):
        return False, "Regex Error: Invalid Logo file extension/URL structure."
        
    response = network_client.request("GET", url)
    if response.get("status_code") != 200:
        return False, f"Connection Error: Server returned status {response.get('status_code')}."
        
    mime_type = response.get("content_type", "")
    if not mime_type.startswith("image/"):
        return False, f"Format Error: Resolved URL content-type is '{mime_type}', not a valid image format."
        
    return True, "Valid Logo image resolved successfully."


def validate_linkedin_url(url: str, is_company: bool = True) -> Tuple[bool, str]:
    """Validates LinkedIn URL structure and active profile resolution."""
    regex = LINKEDIN_COMPANY_RE if is_company else LINKEDIN_PROFILE_RE
    if not regex.match(url):
        return False, "Regex Error: Invalid LinkedIn profile URL structure."
        
    response = network_client.request("GET", url)
    if response.get("status_code") == 200:
        return True, "Valid profile route resolved successfully."
    return False, f"Routing Error: Profile route returned status {response.get('status_code')}."


def validate_video_url(url: str) -> Tuple[bool, str]:
    """Validates video platform URL structure and active routing."""
    if not VIDEO_RE.match(url):
        return False, "Regex Error: Invalid video platform URL structure."
        
    response = network_client.request("GET", url)
    if response.get("status_code") == 200:
        return True, "Valid video route resolved successfully."
    return False, f"Routing Error: Video route returned status {response.get('status_code')}."


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


def validate_text_length(field_name: str, value: Any) -> Tuple[bool, str]:
    """
    Validates that a string's character length strictly falls within
    the defined [min_len, max_len] boundaries.
    """
    bounds = SCHEMA_LENGTH_REGISTRY.get(field_name)
    if not bounds:
        raise ValueError(f"No length boundaries registered for field '{field_name}'.")

    if value is None:
        return False, f"Null Error: Field '{field_name}' cannot be NULL."
        
    if not isinstance(value, str):
        return False, f"Type Error: Field '{field_name}' must be of type STRING (got {type(value).__name__})."

    val_len = len(value)
    min_len, max_len = bounds

    if val_len < min_len:
        return False, f"Length Error: Field '{field_name}' must be at least {min_len} characters (got {val_len})."
        
    if val_len > max_len:
        return False, f"Length Error: Field '{field_name}' cannot exceed {max_len} characters (got {val_len})."

    return True, "Length validation successful."


# =====================================================================
# Unit Tests
# =====================================================================

# --- Tests from tc_8.1.py ---

def test_fully_typed_valid_record_passes():
    """Verifies that a record with 100% correct type mappings passes validation successfully."""
    valid_payload = {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": 1975,
        "Overview of the Company": "Global technology giant.",
        "Number of Offices (beyond HQ)": 120,
        "Website Rating": 9.5,
        "Glassdoor Rating": 4.3,
        "Social Media Followers – Combined": 15000000,
        "CEO Name": "Satya Nadella",
        "Key Business Leaders": [
            {"name": "Amy Hood", "title": "CFO"},
            {"name": "Brad Smith", "title": "President"}
        ],
        "Annual Profits": 72000000000.0,
        "Profitability Status": "Profitable"
    }
    success, errors = validate_record_data_types(valid_payload)
    assert success is True
    assert not errors


def test_record_with_string_representing_numbers_passes_coercion():
    """Verifies that numbers passed as clean numeric strings are successfully coerced and pass."""
    coercible_payload = {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": "1975",  # String representing integer
        "Website Rating": "9.5"          # String representing float
    }
    success, errors = validate_record_data_types(coercible_payload)
    assert success is True
    assert not errors


def test_record_with_type_violation_fails():
    """Verifies that passing alphabetical characters to an integer year field fails type validation."""
    invalid_payload = {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": "Nineteen-Seventy-Five"  # Explicit type violation (cannot coerce to int)
    }
    success, errors = validate_record_data_types(invalid_payload)
    
    assert success is False
    assert any("must be of type int" in err for err in errors)


def test_record_with_malformed_json_fails():
    """Verifies that passing a flat unformatted text string to a JSON array field fails type validation."""
    invalid_payload = {
        "Company Name": "Microsoft Corporation",
        "Key Business Leaders": "Amy Hood - CFO, Brad Smith - President"  # Flat text instead of valid JSON array
    }
    success, errors = validate_record_data_types(invalid_payload)
    
    assert success is False
    assert any("JSON Parse Error" in err for err in errors)


# --- Tests from tc_8.2.py ---

def test_valid_website_url_resolves():
    """Verifies that an active, properly formatted website URL passes validation."""
    success, msg = validate_website_url("https://microsoft.com")
    assert success is True
    assert "resolved successfully" in msg


def test_redirected_website_url_resolves():
    """Verifies that the validation layer follows redirects (301/302) to verify the final destination."""
    success, msg = validate_website_url("https://redirecting-site.com")
    assert success is True
    assert "resolved successfully" in msg


def test_broken_website_url_fails():
    """Verifies that unresolvable website URLs are caught and rejected."""
    success, msg = validate_website_url("https://brokenlink404.com")
    assert success is False
    assert "status 404" in msg


def test_valid_logo_image_resolves():
    """Verifies that logo image links resolving to active image files pass validation."""
    success, msg = validate_logo_url("https://example.com/logo.png")
    assert success is True
    assert "image resolved successfully" in msg


def test_logo_pointing_to_non_image_fails():
    """Verifies that logo image links pointing to non-image resources (like PDFs) are rejected."""
    success, msg = validate_logo_url("https://example.com/document.pdf")
    assert success is False
    assert "not a valid image format" in msg


def test_deleted_linkedin_page_fails():
    """Verifies that unresolvable social media routes are caught and rejected."""
    success, msg = validate_linkedin_url("https://linkedin.com/company/deleted-page-404", is_company=True)
    assert success is False
    assert "returned status 404" in msg


def test_deleted_marketing_video_fails():
    """Verifies that unresolvable video marketing routes are caught and rejected."""
    success, msg = validate_video_url("https://youtube.com/watch?v=deletedvideo")
    assert success is False
    assert "returned status 404" in msg


# --- Tests from tc_8.5.py ---

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


# --- Tests from tc_8.6.py ---

@pytest.mark.parametrize("field_name, valid_input", [
    ("Company Name", "Microsoft Corporation"),
    ("Short Name", "Apple"),
    ("Overview of the Company", "A" * 250),
    ("Core Value Proposition", "A" * 150),
    ("Vision", "To empower everyone on the planet."),
    ("CEO Name", "Tim Cook")
])
def test_valid_text_lengths(field_name, valid_input):
    """Verifies that strings falling within normal character boundaries pass validation."""
    success, msg = validate_text_length(field_name, valid_input)
    assert success is True
    assert "successful" in msg


@pytest.mark.parametrize("field_name, short_input", [
    ("Company Name", "A"),                    # Below 2 min limit
    ("Short Name", "A"),                      # Below 2 min limit
    ("Overview of the Company", "A" * 49),    # Below 50 min limit
    ("Core Value Proposition", "A" * 19),     # Below 20 min limit
    ("Vision", "To do"),                      # Below 10 min limit
    ("CEO Name", "A")                         # Below 2 min limit
])
def test_insufficient_text_lengths_rejected(field_name, short_input):
    """Verifies that strings below the minimum character limit fail validation."""
    success, msg = validate_text_length(field_name, short_input)
    assert success is False
    assert "at least" in msg


@pytest.mark.parametrize("field_name, bloated_input", [
    ("Company Name", "A" * 256),             # Exceeds 255 max
    ("Short Name", "A" * 101),               # Exceeds 100 max
    ("Overview of the Company", "A" * 5001), # Exceeds 5000 max
    ("Core Value Proposition", "A" * 2001),  # Exceeds 2000 max
    ("Vision", "A" * 501),                   # Exceeds 500 max
    ("CEO Name", "A" * 101)                  # Exceeds 100 max
])
def test_excessive_text_lengths_rejected(field_name, bloated_input):
    """Verifies that strings exceeding the maximum character limit fail validation."""
    success, msg = validate_text_length(field_name, bloated_input)
    assert success is False
    assert "cannot exceed" in msg


def test_non_string_input_rejected():
    """Verifies that type mismatch checks fail type boundaries before assessing character length."""
    success, msg = validate_text_length("Company Name", 12345)
    assert success is False
    assert "must be of type STRING" in msg