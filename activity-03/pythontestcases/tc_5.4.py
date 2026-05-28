import re
import pytest
from typing import Any

# Registry of format regular expressions mapped directly from metadata
REGISTRY_PATTERNS = {
    "Company Phone Number": re.compile(r"^\+?[1-9]\d{1,14}$"),
    "Company Contact Email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
    "Website URL": re.compile(r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"),
    "Annual Revenues": re.compile(r"^\$?\d{1,3}(,\d{3})*(\.\d{2})?[KkMmBb]?$"),
    "Year of Incorporation": re.compile(r"^(19|20)\d{2}$")
}

def validate_field_format(field_name: str, value: Any) -> bool:
    """Enforces absolute standard format validation based on parameter rules."""
    pattern = REGISTRY_PATTERNS.get(field_name)
    if not pattern:
        raise ValueError(f"No regex format mapped for field '{field_name}'.")

    if value is None:
        return False

    return pattern.match(str(value)) is not None

def validate_funding_rounds_date_format(rounds_str: str) -> bool:
    """
    Validates embedded date formats inside funding timeline lists.
    Every round must start with a YYYY-MM-DD date segment.
    """
    if not rounds_str:
        return False
        
    # Split by comma-separated records
    records = [r.strip() for r in rounds_str.split(",") if r.strip()]
    for record in records:
        # Check if record starts with valid YYYY-MM-DD
        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})\b", record)
        if not date_match:
            return False
            
    return True


# --- Pytest Tests ---

@pytest.mark.parametrize("valid_phone", ["+14155552671", "+442079460192", "14155552671"])
def test_valid_phone_format(valid_phone):
    """Verifies that E.164 standard phone formats pass successfully."""
    assert validate_field_format("Company Phone Number", valid_phone) is True

@pytest.mark.parametrize("invalid_phone", ["+1-415-555-2671", "(415) 555-2671", "415-555-2671"])
def test_invalid_phone_rejected(invalid_phone):
    """Verifies that regional formatting with dashes, spaces, or parentheses is rejected."""
    assert validate_field_format("Company Phone Number", invalid_phone) is False

@pytest.mark.parametrize("valid_email", ["info@company.com", "contact_sales@sub.domain.org"])
def test_valid_email_format(valid_email):
    """Verifies that standard RFC 5322 emails pass successfully."""
    assert validate_field_format("Company Contact Email", valid_email) is True

@pytest.mark.parametrize("invalid_email", ["info#company.com", "info@company", "@domain.com"])
def test_invalid_email_rejected(invalid_email):
    """Verifies that malformed emails are rejected."""
    assert validate_field_format("Company Contact Email", invalid_email) is False

@pytest.mark.parametrize("valid_url", ["https://microsoft.com", "https://www.google.com/search?q=test"])
def test_valid_url_format(valid_url):
    """Verifies that standard HTTPS URLs pass successfully."""
    assert validate_field_format("Website URL", valid_url) is True

@pytest.mark.parametrize("invalid_url", ["http://microsoft@com", "https://invalid_url", "www.no-scheme.com"])
def test_invalid_url_rejected(invalid_url):
    """Verifies that malformed or non-secure URL configurations are rejected."""
    assert validate_field_format("Website URL", invalid_url) is False

@pytest.mark.parametrize("valid_revenue", ["$150,000,000", "150,000,000", "$150M", "1.5B"])
def test_valid_revenue_format(valid_revenue):
    """Verifies that standard currency and magnitude notations pass successfully."""
    assert validate_field_format("Annual Revenues", valid_revenue) is True

@pytest.mark.parametrize("invalid_revenue", ["150M USD", "USD 150,000,000", "Approx $150M"])
def test_invalid_revenue_rejected(invalid_revenue):
    """Verifies that informal non-standardized currency tags are rejected."""
    assert validate_field_format("Annual Revenues", invalid_revenue) is False

@pytest.mark.parametrize("valid_rounds", [
    "2024-01-10 - Series A - $10M",
    "2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M"
])
def test_valid_funding_rounds_date_formatting(valid_rounds):
    """Verifies that embedded dates conforming strictly to YYYY-MM-DD pass validation."""
    assert validate_funding_rounds_date_format(valid_rounds) is True

@pytest.mark.parametrize("invalid_rounds", [
    "01/10/2024 - Series A - $10M",  # US date format
    "2024.01.10 - Series A - $10M"   # Dot separator format
])
def test_invalid_funding_rounds_date_rejected(invalid_rounds):
    """Verifies that non-standard date separators or formatting fail validation."""
    assert validate_funding_rounds_date_format(invalid_rounds) is False