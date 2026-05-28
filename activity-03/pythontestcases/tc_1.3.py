import re
import pytest

# Core Regex Patterns compiled directly from Metadata Parameter Constraints
COMPANY_NAME_RE = re.compile(r"^[\w\s&.,\-\(\)'\u00C0-\u017F]+$")
SHORT_NAME_RE = re.compile(r"^[\w\s&.\-]+$")
URL_RE = re.compile(r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(r"^\+?[1-9]\d{1,14}$")
PERCENT_RE = re.compile(r"^\d{1,3}(\.\d{1,2})?%$")

# Text/Narrative wildcards (supports full UTF-8 space)
def validate_wildcard_text(val: str) -> bool:
    """Narrative text fields (like descriptions) supporting all special characters."""
    return isinstance(val, str) and len(val) > 0


# --- Pytest Tests ---

@pytest.mark.parametrize("valid_company_name", [
    "Café Résumé",
    "M&S Holdings Co.",
    "Bio-Tech (Global) S.A."
])
def test_company_name_valid_special_characters(valid_company_name):
    """Verifies that company name regex allows Latin accents, ampersands, dashes, and parentheses."""
    assert COMPANY_NAME_RE.match(valid_company_name) is not None

@pytest.mark.parametrize("invalid_company_name", [
    "Company™ & Co.®",  # Contains ™ (\u2122) and ® (\u00ae) outside \u00C0-\u017F range
    "Software@Enterprise",  # Contains invalid '@'
    "SaaS #1"  # Contains invalid '#'
])
def test_company_name_invalid_special_characters(invalid_company_name):
    """Verifies that out-of-range symbols fail validation for company name."""
    assert COMPANY_NAME_RE.match(invalid_company_name) is None

@pytest.mark.parametrize("valid_short_name", [
    "M&S",
    "Bio-Tech",
    "S.A."
])
def test_short_name_valid_special_characters(valid_short_name):
    """Verifies standard punctuation in short names passes validation."""
    assert SHORT_NAME_RE.match(valid_short_name) is not None

@pytest.mark.parametrize("invalid_short_name", [
    "Café",  # Non-ASCII accent characters fail strict character class
    "SaaS!",  # Contains invalid '!'
    "Global @ Team"  # Contains invalid '@'
])
def test_short_name_invalid_special_characters(invalid_short_name):
    """Verifies that short name restricts punctuation according to formatting rules."""
    assert SHORT_NAME_RE.match(invalid_short_name) is None

@pytest.mark.parametrize("valid_url", [
    "https://cafe-resume.com",
    "https://example.com/logo.png?v=1.0&size=medium",
    "https://sub.domain.org/path_name/file-name.webp?ref=search"
])
def test_urls_valid_query_parameters(valid_url):
    """Verifies standard URL query strings and directory characters pass format validation."""
    assert URL_RE.match(valid_url) is not None

@pytest.mark.parametrize("invalid_url", [
    "https://example.com/logo@#$.png",  # Contains unencoded invalid symbols
    "http://example.com/logo.png?ref=<script>"  # Injection attempt
])
def test_urls_invalid_characters(invalid_url):
    """Verifies that raw invalid symbols in URLs are rejected."""
    assert URL_RE.match(invalid_url) is None

@pytest.mark.parametrize("valid_text", [
    "Café Résumé: Company™ & Co.® — ($10M+ Revenue!)",
    "• Proprietary AI Engine™ [Patent Approved #12345]",
    "Gender metrics: 45% Female / 55% Male / 5% Non-binary."
])
def test_narrative_text_fields_allow_all_unicode(valid_text):
    """Verifies that unstructured narrative parameters successfully store full UTF-8 character space."""
    assert validate_wildcard_text(valid_text) is True

@pytest.mark.parametrize("valid_email", [
    "contact-info_1@company.com",
    "contact.first+last@sub.domain.org"
])
def test_emails_valid_special_characters(valid_email):
    """Verifies email formatting with dots, dashes, underscores, and plus symbols passes."""
    assert EMAIL_RE.match(valid_email) is not None

@pytest.mark.parametrize("invalid_email", [
    "contact#info@company.com",
    "contact$info@company.com"
])
def test_emails_invalid_special_characters(invalid_email):
    """Verifies invalid email formatting is rejected."""
    assert EMAIL_RE.match(invalid_email) is None

@pytest.mark.parametrize("valid_phone", [
    "+14155552671",
    "4155552671"
])
def test_phone_valid_prefix(valid_phone):
    """Verifies standard phone formatting with leading "+" symbol passes."""
    assert PHONE_RE.match(valid_phone) is not None

@pytest.mark.parametrize("invalid_phone", [
    "+1-415-555-2671",  # Contains forbidden dashes
    "(415) 555-2671"  # Contains forbidden parentheses
])
def test_phone_invalid_characters(invalid_phone):
    """Verifies phone rejects symbols except the optional leading '+' code."""
    assert PHONE_RE.match(invalid_phone) is None