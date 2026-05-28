import pytest
from typing import Any, Tuple

# Allowed Enums (Standard Capitalization)
ALLOWED_CATEGORIES = {"Startup", "MSME", "SMB", "Enterprise", "Investor", "VC", "Conglomerate"}
ALLOWED_LEGAL_STRUCTURES = {"Private", "Public", "Subsidiary", "Partnership", "Non-Profit", "Govt"}
ALLOWED_PROFITABILITY = {"Profitable", "Break-even", "Loss-making"}
ALLOWED_SALES_MOTIONS = {"PLG", "Product-Led", "Sales-Led", "Field Sales", "Channel", "Hybrid"}
ALLOWED_REMOTE_POLICIES = {"Remote", "Hybrid", "On-Site", "Flexible Choice"}

def normalize_and_validate_enum(value: str, allowed_set: set) -> Tuple[bool, str]:
    """Resolves enum values case-insensitively and maps to standard capitalization."""
    if not value:
        return False, "Empty value."
    
    # Map lowercase to standard capitalized key
    lookup_map = {item.lower(): item for item in allowed_set}
    resolved = lookup_map.get(value.lower())
    
    if resolved:
        return True, resolved
    return False, f"Value '{value}' not found in allowed enums."

def normalize_email(email: str) -> Tuple[bool, str]:
    """Normalizes email domain parts to lowercase case-insensitively."""
    if not email or "@" not in email:
        return False, "Invalid email structure."
        
    local_part, domain_part = email.split("@", 1)
    # Standard practice is to lowercase the domain, keeping local case-sensitive (practically treated case-insensitively)
    normalized = f"{local_part.strip()}@{domain_part.strip().lower()}"
    return True, normalized

def normalize_url(url: str) -> Tuple[bool, str]:
    """Normalizes URL scheme and domain to lowercase, leaving path directory intact."""
    if not url or "://" not in url:
        return False, "Invalid URL structure."
        
    scheme, remainder = url.split("://", 1)
    if "/" in remainder:
        domain, path = remainder.split("/", 1)
        normalized = f"{scheme.lower()}://{domain.lower()}/{path}"
    else:
        normalized = f"{scheme.lower()}://{remainder.lower()}"
        
    return True, normalized

def normalize_title_case(name: str) -> Tuple[bool, str]:
    """Normalizes names to standard Title Case structure."""
    if not name:
        return False, "Empty name."
    return True, name.title()


# --- Pytest Tests ---

@pytest.mark.parametrize("category_input", ["startup", "STARTUP", "sTaRtUp"])
def test_category_case_insensitivity(category_input):
    """Verifies that Category enums map successfully regardless of input casing."""
    success, resolved = normalize_and_validate_enum(category_input, ALLOWED_CATEGORIES)
    assert success is True
    assert resolved == "Startup"

@pytest.mark.parametrize("structure_input", ["private", "PRIVATE", "pRiVaTe"])
def test_legal_structure_case_insensitivity(structure_input):
    """Verifies that Legal Structure enums map successfully regardless of input casing."""
    success, resolved = normalize_and_validate_enum(structure_input, ALLOWED_LEGAL_STRUCTURES)
    assert success is True
    assert resolved == "Private"

@pytest.mark.parametrize("email_input, expected_normalized", [
    ("INFO@MICROSOFT.COM", "INFO@microsoft.com"),
    ("user.name@SUB.DOMAIN.ORG", "user.name@sub.domain.org")
])
def test_email_domain_normalization(email_input, expected_normalized):
    """Verifies that email domain strings are successfully lowered to preserve route consistency."""
    success, normalized = normalize_email(email_input)
    assert success is True
    assert normalized == expected_normalized

@pytest.mark.parametrize("url_input, expected_normalized", [
    ("HTTPS://WWW.MICROSOFT.COM/en-US", "https://www.microsoft.com/en-US"),
    ("HTTP://SUB.DOMAIN.ORG/Path/To/Resource", "http://sub.domain.org/Path/To/Resource")
])
def test_url_domain_normalization(url_input, expected_normalized):
    """Verifies that URL scheme and domains are lowered while path cases are preserved."""
    success, normalized = normalize_url(url_input)
    assert success is True
    assert normalized == expected_normalized

@pytest.mark.parametrize("ceo_input", ["satya nadella", "SATYA NADELLA"])
def test_ceo_name_title_case_normalization(ceo_input):
    """Verifies that CEO names normalize cleanly to Standard/Title Case."""
    success, normalized = normalize_title_case(ceo_input)
    assert success is True
    assert normalized == "Satya Nadella"