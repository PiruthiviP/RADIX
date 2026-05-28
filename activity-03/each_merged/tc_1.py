"""
tc_1_all.py — Consolidated Metadata Validation Test Suite
Covers:
  TC 1.1 — Company Name & Short Name field-level validation
  TC 1.2 — Schema-wide nullability & empty/whitespace rejection
  TC 1.3 — Regex pattern validation for all field types
  TC 1.4 — Malformed / misspelled entity detection
  TC 1.5 — Ambiguous entity resolution with context disambiguation
  TC 1.6 — Case normalisation for enums, emails, URLs, and names
"""

import re
import pytest
from typing import Any, Dict, List, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# TC 1.1 — Company Name & Short Name Field Validation
# ─────────────────────────────────────────────────────────────────────────────

COMPANY_NAME_PATTERN = re.compile(r"^[\w\s&.,\-\(\)'\u00C0-\u017F]+$")
SHORT_NAME_PATTERN   = re.compile(r"^[\w\s&.\-]+$")


def validate_company_name(name: str) -> bool:
    """
    Validates 'Company Name':
    - Not None; no leading/trailing whitespace.
    - Length 2–255; matches COMPANY_NAME_PATTERN.
    """
    if name is None:
        return False
    if name != name.strip():
        return False
    if not (2 <= len(name) <= 255):
        return False
    if not COMPANY_NAME_PATTERN.match(name):
        return False
    return True


def validate_short_name(name: str) -> bool:
    """
    Validates 'Short Name' (nullable):
    - None is accepted.
    - If provided: no leading/trailing whitespace, length 2–100, matches SHORT_NAME_PATTERN.
    """
    if name is None:
        return True
    if name != name.strip():
        return False
    if not (2 <= len(name) <= 100):
        return False
    if not SHORT_NAME_PATTERN.match(name):
        return False
    return True


@pytest.mark.parametrize("valid_name", [
    "Microsoft Corporation",
    "Apple Inc.",
    "Tesla, Inc.",
    "L'Oréal S.A.",
    "M&S Group",
    "Bio-Tech (Global) Inc.",
])
def test_company_name_valid_inputs(valid_name):
    """Standard well-formed legal company names must pass."""
    assert validate_company_name(valid_name) is True, \
        f"Failed validation for valid company name: {valid_name}"


@pytest.mark.parametrize("invalid_name", [
    " A",               # Leading space
    "Apple Inc. ",      # Trailing space
    "A",                # Too short
    "Microsoft 🚀 Ltd", # Emoji / illegal character
    "",                 # Empty string
])
def test_company_name_invalid_inputs(invalid_name):
    """Edge-case / badly-formatted legal company names must fail."""
    assert validate_company_name(invalid_name) is False, \
        f"Unexpectedly passed validation for invalid company name: {invalid_name}"


@pytest.mark.parametrize("valid_short_name", [
    "Microsoft", "Apple", "Tesla", "M&S", "Bio-Tech", None,
])
def test_short_name_valid_inputs(valid_short_name):
    """Standard short names (including None) must pass."""
    assert validate_short_name(valid_short_name) is True, \
        f"Failed validation for valid short name: {valid_short_name}"


@pytest.mark.parametrize("invalid_short_name", [
    "A",           # Too short
    "Tesla!",      # Illegal character
    "Microsoft  ", # Trailing space
    "A" * 101,     # Exceeds 100-char limit
])
def test_short_name_invalid_inputs(invalid_short_name):
    """Invalid short names must fail."""
    assert validate_short_name(invalid_short_name) is False, \
        f"Unexpectedly passed validation for invalid short name: {invalid_short_name}"


# ─────────────────────────────────────────────────────────────────────────────
# TC 1.2 — Schema-Wide Nullability & Empty/Whitespace Rejection
# ─────────────────────────────────────────────────────────────────────────────

# False = Not Null (Mandatory) | True = Nullable (Optional)
SCHEMA_REGISTRY: Dict[str, bool] = {
    "Company Name": False, "Short Name": True, "Logo": False, "Category": False,
    "Year of Incorporation": False, "Overview of the Company": False, "Nature of Company": False,
    "Company Headquarters": False, "Countries Operating In": True, "Number of Offices (beyond HQ)": True,
    "Office Locations": True, "Employee Size": False, "Hiring Velocity": True,
    "Employee Turnover": True, "Average Retention Tenure": True, "Pain Points Being Addressed": False,
    "Focus Sectors / Industries": False, "Services / Offerings / Products": False,
    "Top Customers by Client Segments": True, "Core Value Proposition": False, "Vision": True,
    "Mission": True, "Values": True, "Unique Differentiators": True, "Competitive Advantages": True,
    "Weaknesses / Gaps in Offering": True, "Key Challenges and Unmet Needs": True, "Key Competitors": False,
    "Technology Partners": True, "Interesting Facts": True, "Recent News": True, "Website URL": False,
    "Quality of Website": True, "Website Rating": True, "Website Traffic Rank": True,
    "Social Media Followers – Combined": False, "Glassdoor Rating": True, "Indeed Rating": True,
    "Google Reviews Rating": True, "LinkedIn Profile URL": True, "Twitter (X) Handle": True,
    "Facebook Page URL": True, "Instagram Page URL": True, "CEO Name": False, "CEO LinkedIn URL": True,
    "Key Business Leaders": False, "Warm Introduction Pathways": True, "Decision Maker Accessibility": True,
    "Company Contact Email": True, "Company Phone Number": True, "Primary Contact Person's Name": True,
    "Primary Contact Person's Title": True, "Primary Contact Person's Email": True,
    "Primary Contact Person's Phone Number": True, "Awards & Recognitions": True, "Brand Sentiment Score": True,
    "Event Participation": True, "Regulatory & Compliance Status": True, "Legal Issues / Controversies": True,
    "Annual Revenues": True, "Annual Profits": True, "Revenue Mix": True, "Company Valuation": True,
    "Year-over-Year Growth Rate": True, "Profitability Status": False, "Market Share (%)": True,
    "Key Investors / Backers": True, "Recent Funding Rounds": True, "Total Capital Raised": True,
    "ESG Practices or Ratings": True, "Sales Motion": False, "Customer Acquisition Cost (CAC)": True,
    "Customer Lifetime Value (CLV)": True, "CAC:LTV Ratio": True, "Churn Rate": True,
    "Net Promoter Score (NPS)": True, "Customer Concentration Risk": True, "Burn Rate": True,
    "Runway": True, "Burn Multiplier": True, "Intellectual Property": True, "R&D Investment": True,
    "AI/ML Adoption Level": True, "Tech Stack/Tools Used": True, "Cybersecurity Posture": True,
    "Supply Chain Dependencies": True, "Geopolitical Risks": True, "Macro Risks": True,
    "Diversity Metrics": True, "Remote Work Policy": False, "Training/Development Spend": True,
    "Partnership Ecosystem": True, "Exit Strategy/History": True, "Carbon Footprint/Environmental Impact": True,
    "Ethical Sourcing Practices": True, "Benchmark vs. Peers": True, "Future Projections": True,
    "Strategic Priorities": False, "Industry Associations / Memberships": True,
    "Case Studies / Public Success Stories": True, "Go-to-Market Strategy": False, "Innovation Roadmap ": True,
    "Product Pipeline": True, "Board of Directors / Advisors": False,
    "Company Introduction / Marketing videos": True, "Customer testimonial": True,
    "Industry Benchmark Technology Adoption Rating": True, "Total Addressable Market (TAM)": True,
    "Serviceable Addressable Market (SAM)": True, "Serviceable Obtainable Market (SOM)": True,
    "Work culture": True, "Manager quality": True, "Psychological safety": True, "Feedback culture": True,
    "Diversity & inclusion": True, "Ethical standards": True, "Typical working hours": True,
    "Overtime expectations": True, "Weekend work": True, "Remote / hybrid / on-site flexibility": False,
    "Leave policy": True, "Burnout risk": True, "Central vs peripheral location": True,
    "Public transport access": True, "Cab availability and company cab policy": True,
    "Commute time from airport": True, "Office zone type": True, "Area safety": True,
    "Company safety policies": True, "Office infrastructure safety": True, "Emergency response preparedness": True,
    "Health support": True, "Onboarding and training quality": True, "Learning culture": True,
    "Exposure quality": True, "Mentorship availability": True, "Internal mobility": True,
    "Promotion clarity": True, "Tools and technology access": True, "Role clarity": True,
    "Early ownership": True, "Work impact": True, "Execution vs thinking balance": True,
    "Automation level": True, "Cross-functional exposure": True, "Company maturity": False,
    "Brand value": True, "Client quality": True, "Layoff history": True, "Fixed vs variable pay": True,
    "Bonus predictability": True, "ESOPs and long-term incentives": True, "Family health insurance": True,
    "Relocation support": True, "Lifestyle and wellness benefits": True, "Exit opportunities": True,
    "Skill relevance": True, "External recognition": True, "Network strength": True, "Global exposure": True,
    "Mission clarity": True, "Sustainability and CSR": True, "Crisis behavior": True,
}


def validate_field_input(field_name: str, value: Any) -> bool:
    """
    Validates field input rules:
    - Empty strings and whitespace-only strings are always rejected.
    - None: accepted for nullable fields, rejected for mandatory fields.
    """
    is_nullable = SCHEMA_REGISTRY.get(field_name)
    if is_nullable is None:
        raise ValueError(f"Field '{field_name}' is not defined in the SCHEMA_REGISTRY.")

    if value is None:
        return is_nullable

    if isinstance(value, str):
        if value == "" or value.strip() == "":
            return False

    return True


@pytest.mark.parametrize("field_name, is_nullable", SCHEMA_REGISTRY.items())
def test_fields_reject_empty_string(field_name, is_nullable):
    """Empty string must always fail regardless of nullability."""
    assert validate_field_input(field_name, "") is False, \
        f"Empty string validation failed to reject on '{field_name}'."


@pytest.mark.parametrize("field_name, is_nullable", SCHEMA_REGISTRY.items())
def test_fields_reject_whitespace(field_name, is_nullable):
    """Whitespace-only string must always fail across all fields."""
    assert validate_field_input(field_name, "    ") is False, \
        f"Whitespace string validation failed to reject on '{field_name}'."


@pytest.mark.parametrize("field_name, is_nullable", SCHEMA_REGISTRY.items())
def test_null_validation_against_nullability_rules(field_name, is_nullable):
    """None is accepted for nullable fields and rejected for mandatory fields."""
    expected_outcome = is_nullable
    actual_outcome   = validate_field_input(field_name, None)
    assert actual_outcome == expected_outcome, (
        f"Validation mismatch on '{field_name}' with Nullable={is_nullable}. "
        f"Expected {expected_outcome}, but got {actual_outcome}."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TC 1.3 — Regex Pattern Validation
# ─────────────────────────────────────────────────────────────────────────────

COMPANY_NAME_RE = re.compile(r"^[\w\s&.,\-\(\)'\u00C0-\u017F]+$")
SHORT_NAME_RE   = re.compile(r"^[\w\s&.\-]+$")
URL_RE          = re.compile(
    r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}"
    r"\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
)
EMAIL_RE        = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_RE        = re.compile(r"^\+?[1-9]\d{1,14}$")
PERCENT_RE      = re.compile(r"^\d{1,3}(\.\d{1,2})?%$")


def validate_wildcard_text(val: str) -> bool:
    """Narrative text fields supporting full UTF-8."""
    return isinstance(val, str) and len(val) > 0


@pytest.mark.parametrize("valid_company_name", [
    "Café Résumé",
    "M&S Holdings Co.",
    "Bio-Tech (Global) S.A.",
])
def test_company_name_valid_special_characters(valid_company_name):
    """Company name regex must accept Latin accents, ampersands, dashes, parentheses."""
    assert COMPANY_NAME_RE.match(valid_company_name) is not None


@pytest.mark.parametrize("invalid_company_name", [
    "Company™ & Co.®",    # ™ and ® outside \u00C0-\u017F
    "Software@Enterprise", # invalid '@'
    "SaaS #1",             # invalid '#'
])
def test_company_name_invalid_special_characters(invalid_company_name):
    """Out-of-range symbols must fail company name regex."""
    assert COMPANY_NAME_RE.match(invalid_company_name) is None


@pytest.mark.parametrize("valid_short_name", ["M&S", "Bio-Tech", "S.A."])
def test_short_name_valid_special_characters(valid_short_name):
    """Standard punctuation in short names must pass."""
    assert SHORT_NAME_RE.match(valid_short_name) is not None


@pytest.mark.parametrize("invalid_short_name", [
    "Café",          # Non-ASCII accent
    "SaaS!",         # invalid '!'
    "Global @ Team", # invalid '@'
])
def test_short_name_invalid_special_characters(invalid_short_name):
    """Short name must reject disallowed punctuation."""
    assert SHORT_NAME_RE.match(invalid_short_name) is None


@pytest.mark.parametrize("valid_url", [
    "https://cafe-resume.com",
    "https://example.com/logo.png?v=1.0&size=medium",
    "https://sub.domain.org/path_name/file-name.webp?ref=search",
])
def test_urls_valid_query_parameters(valid_url):
    """Standard URL query strings and path characters must pass."""
    assert URL_RE.match(valid_url) is not None


@pytest.mark.parametrize("invalid_url", [
    "https://example.com/logo@#$.png",
    "http://example.com/logo.png?ref=<script>",
])
def test_urls_invalid_characters(invalid_url):
    """Raw invalid symbols in URLs must be rejected."""
    assert URL_RE.match(invalid_url) is None


@pytest.mark.parametrize("valid_text", [
    "Café Résumé: Company™ & Co.® — ($10M+ Revenue!)",
    "• Proprietary AI Engine™ [Patent Approved #12345]",
    "Gender metrics: 45% Female / 55% Male / 5% Non-binary.",
])
def test_narrative_text_fields_allow_all_unicode(valid_text):
    """Unstructured narrative fields must accept full UTF-8."""
    assert validate_wildcard_text(valid_text) is True


@pytest.mark.parametrize("valid_email", [
    "contact-info_1@company.com",
    "contact.first+last@sub.domain.org",
])
def test_emails_valid_special_characters(valid_email):
    """Dots, dashes, underscores, plus signs in emails must pass."""
    assert EMAIL_RE.match(valid_email) is not None


@pytest.mark.parametrize("invalid_email", [
    "contact#info@company.com",
    "contact$info@company.com",
])
def test_emails_invalid_special_characters(invalid_email):
    """Emails with '#' or '$' must be rejected."""
    assert EMAIL_RE.match(invalid_email) is None


@pytest.mark.parametrize("valid_phone", ["+14155552671", "4155552671"])
def test_phone_valid_prefix(valid_phone):
    """Phones with optional leading '+' must pass."""
    assert PHONE_RE.match(valid_phone) is not None


@pytest.mark.parametrize("invalid_phone", [
    "+1-415-555-2671",  # forbidden dashes
    "(415) 555-2671",   # forbidden parentheses
])
def test_phone_invalid_characters(invalid_phone):
    """Phones with dashes or parentheses must be rejected."""
    assert PHONE_RE.match(invalid_phone) is None


# ─────────────────────────────────────────────────────────────────────────────
# TC 1.4 — Malformed / Misspelled Entity Detection
# ─────────────────────────────────────────────────────────────────────────────

VERIFIED_COMPANIES = {"Microsoft Corporation", "Apple Inc.", "Tesla Inc.", "Google LLC", "Amazon.com Inc."}
VERIFIED_BRANDS    = {"Microsoft", "Apple", "Tesla", "Google", "Amazon"}
VERIFIED_INVESTORS = {"Sequoia Capital", "Andreessen Horowitz", "a16z", "Y Combinator"}
VERIFIED_CEOS      = {"Satya Nadella", "Tim Cook", "Elon Musk", "Sundar Pichai", "Andy Jassy"}


def validate_company_name_registry(name: str) -> Tuple[bool, str]:
    """Validates legal Company Name against verified registry."""
    if not name or len(name) < 2:
        return False, "Input is too short to be a valid legal name."
    if name in VERIFIED_COMPANIES:
        return True, "Valid legal name."
    if any(name.lower() in verified.lower() for verified in VERIFIED_COMPANIES):
        return False, "Incomplete or heavily abbreviated legal name."
    return False, "Legal name could not be resolved in the government registry."


def validate_short_name_registry(name: str) -> Tuple[bool, str]:
    """Validates Short Name against verified branding databases."""
    if not name or len(name) < 2:
        return False, "Input too short."
    if name in VERIFIED_BRANDS:
        return True, "Valid short name."
    return False, "Short name does not match verified branding assets."


def validate_competitors_list(competitors_str: str) -> Tuple[bool, List[str]]:
    """Parses comma-separated competitors; flags unresolved entries."""
    if not competitors_str:
        return False, ["Empty Input"]
    competitors = [c.strip() for c in competitors_str.split(",") if c.strip()]
    unresolved = [
        c for c in competitors
        if c not in VERIFIED_COMPANIES and c not in VERIFIED_BRANDS
    ]
    return len(unresolved) == 0, unresolved


def validate_person_name(name: str) -> Tuple[bool, str]:
    """Validates person name completeness (rejects single initials)."""
    if not name:
        return False, "Name cannot be empty."
    parts = [p.replace(".", "").strip() for p in name.split()]
    if any(len(p) <= 1 for p in parts):
        return False, "Name contains truncated single initials or incomplete values."
    return True, "Valid format."


@pytest.mark.parametrize("malformed_company", ["Microsft", "App", "Goog"])
def test_malformed_company_name(malformed_company):
    """Misspelled or heavily truncated legal names must be rejected."""
    success, message = validate_company_name_registry(malformed_company)
    assert success is False
    assert "Incomplete" in message or "could not be resolved" in message


@pytest.mark.parametrize("malformed_short_name", ["Microsft", "Goog"])
def test_malformed_short_name(malformed_short_name):
    """Misspelled or truncated brand names must be caught."""
    success, message = validate_short_name_registry(malformed_short_name)
    assert success is False
    assert "does not match" in message


def test_malformed_competitor_list():
    """Only malformed competitor entries should be flagged."""
    input_list = "Microsft, Apple Inc., Tesl"
    success, unresolved = validate_competitors_list(input_list)
    assert success is False
    assert "Microsft" in unresolved
    assert "Tesl" in unresolved
    assert "Apple Inc." not in unresolved


@pytest.mark.parametrize("malformed_name", ["S", "S. J. S.", "J. René"])
def test_malformed_person_name(malformed_name):
    """Incomplete or initial-only person names must fail."""
    success, message = validate_person_name(malformed_name)
    assert success is False
    assert "truncated" in message


# ─────────────────────────────────────────────────────────────────────────────
# TC 1.5 — Ambiguous Entity Resolution
# ─────────────────────────────────────────────────────────────────────────────

ENTITY_DATABASE = {
    "companies": [
        {"legal_name": "Delta Air Lines, Inc.",    "alias": "Delta",   "domain": "delta.com",            "sector": "Airlines"},
        {"legal_name": "Delta Faucet Company",      "alias": "Delta",   "domain": "deltafaucet.com",      "sector": "Manufacturing"},
        {"legal_name": "Mercury Technologies",      "alias": "Mercury", "domain": "mercury.com",          "sector": "Financials"},
        {"legal_name": "Mercury Insurance Group",   "alias": "Mercury", "domain": "mercuryinsurance.com", "sector": "Insurance"},
    ],
    "ceos": [
        {"name": "John Smith", "company": "Delta Air Lines, Inc.", "linkedin": "linkedin.com/in/john-smith-delta"},
        {"name": "John Smith", "company": "Delta Faucet Company",  "linkedin": "linkedin.com/in/john-smith-faucet"},
    ],
    "investors": [
        {"legal_name": "Founders Fund",           "alias": "Founders"},
        {"legal_name": "Founders Circle Capital", "alias": "Founders"},
    ],
}


def resolve_company_entity(name: str, domain: str = None, sector: str = None) -> Tuple[str, str]:
    """
    Resolves 'Company Name' or 'Short Name' against the entity database.
    Returns ('SUCCESS', legal_name), ('AMBIGUOUS', message), or ('UNRESOLVED', message).
    """
    if not name:
        return "UNRESOLVED", "Empty input name."

    matches = [
        c for c in ENTITY_DATABASE["companies"]
        if c["legal_name"].lower() == name.lower() or c["alias"].lower() == name.lower()
    ]

    if not matches:
        return "UNRESOLVED", f"No database matches found for '{name}'."
    if len(matches) == 1:
        return "SUCCESS", matches[0]["legal_name"]

    if domain:
        domain_matches = [c for c in matches if c["domain"].lower() == domain.lower()]
        if len(domain_matches) == 1:
            return "SUCCESS", domain_matches[0]["legal_name"]

    if sector:
        sector_matches = [c for c in matches if c["sector"].lower() == sector.lower()]
        if len(sector_matches) == 1:
            return "SUCCESS", sector_matches[0]["legal_name"]

    matched_names = ", ".join(c["legal_name"] for c in matches)
    return "AMBIGUOUS", f"Input matches multiple entities: [{matched_names}]. Provide domain or sector to resolve."


def resolve_ceo_entity(ceo_name: str, company_name: str = None, linkedin_url: str = None) -> Tuple[str, str]:
    """
    Resolves 'CEO Name' with optional company / LinkedIn disambiguation.
    Returns ('SUCCESS', name), ('AMBIGUOUS', message), or ('UNRESOLVED', message).
    """
    matches = [c for c in ENTITY_DATABASE["ceos"] if c["name"].lower() == ceo_name.lower()]

    if not matches:
        return "UNRESOLVED", f"No CEO found matching '{ceo_name}'."
    if len(matches) == 1:
        return "SUCCESS", matches[0]["name"]

    if company_name:
        company_matches = [c for c in matches if c["company"].lower() == company_name.lower()]
        if len(company_matches) == 1:
            return "SUCCESS", company_matches[0]["name"]

    if linkedin_url:
        linkedin_matches = [c for c in matches if c["linkedin"].lower() == linkedin_url.lower()]
        if len(linkedin_matches) == 1:
            return "SUCCESS", linkedin_matches[0]["name"]

    return "AMBIGUOUS", f"Multiple executives named '{ceo_name}'. Reconcile with company or LinkedIn URL."


def test_resolve_unique_company():
    """Fully qualified company name must resolve directly."""
    status, result = resolve_company_entity("Delta Air Lines, Inc.")
    assert status == "SUCCESS"
    assert result == "Delta Air Lines, Inc."


def test_resolve_ambiguous_company_without_context():
    """Generic alias without context must be flagged as ambiguous."""
    status, message = resolve_company_entity("Delta")
    assert status == "AMBIGUOUS"
    assert "matches multiple entities" in message


def test_resolve_ambiguous_company_with_domain_context():
    """Generic alias must resolve when domain context is provided."""
    status, result = resolve_company_entity("Delta", domain="deltafaucet.com")
    assert status == "SUCCESS"
    assert result == "Delta Faucet Company"


def test_resolve_ambiguous_company_with_sector_context():
    """Generic alias must resolve when sector context is provided."""
    status, result = resolve_company_entity("Mercury", sector="Insurance")
    assert status == "SUCCESS"
    assert result == "Mercury Insurance Group"


def test_resolve_common_ceo_name_without_context():
    """Common executive name without context must be flagged as ambiguous."""
    status, message = resolve_ceo_entity("John Smith")
    assert status == "AMBIGUOUS"
    assert "Multiple executives" in message


def test_resolve_common_ceo_name_with_company_context():
    """Common executive name must resolve when paired with company context."""
    status, result = resolve_ceo_entity("John Smith", company_name="Delta Air Lines, Inc.")
    assert status == "SUCCESS"
    assert result == "John Smith"


# ─────────────────────────────────────────────────────────────────────────────
# TC 1.6 — Case Normalisation
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_CATEGORIES      = {"Startup", "MSME", "SMB", "Enterprise", "Investor", "VC", "Conglomerate"}
ALLOWED_LEGAL_STRUCTURES = {"Private", "Public", "Subsidiary", "Partnership", "Non-Profit", "Govt"}
ALLOWED_PROFITABILITY    = {"Profitable", "Break-even", "Loss-making"}
ALLOWED_SALES_MOTIONS    = {"PLG", "Product-Led", "Sales-Led", "Field Sales", "Channel", "Hybrid"}
ALLOWED_REMOTE_POLICIES  = {"Remote", "Hybrid", "On-Site", "Flexible Choice"}


def normalize_and_validate_enum(value: str, allowed_set: set) -> Tuple[bool, str]:
    """Case-insensitive enum lookup; maps to standard capitalisation."""
    if not value:
        return False, "Empty value."
    lookup_map = {item.lower(): item for item in allowed_set}
    resolved = lookup_map.get(value.lower())
    if resolved:
        return True, resolved
    return False, f"Value '{value}' not found in allowed enums."


def normalize_email(email: str) -> Tuple[bool, str]:
    """Lowercases the domain part of an email address."""
    if not email or "@" not in email:
        return False, "Invalid email structure."
    local_part, domain_part = email.split("@", 1)
    normalized = f"{local_part.strip()}@{domain_part.strip().lower()}"
    return True, normalized


def normalize_url(url: str) -> Tuple[bool, str]:
    """Lowercases scheme and domain; preserves path case."""
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
    """Normalises names to Title Case."""
    if not name:
        return False, "Empty name."
    return True, name.title()


@pytest.mark.parametrize("category_input", ["startup", "STARTUP", "sTaRtUp"])
def test_category_case_insensitivity(category_input):
    """Category enums must resolve to 'Startup' regardless of input casing."""
    success, resolved = normalize_and_validate_enum(category_input, ALLOWED_CATEGORIES)
    assert success is True
    assert resolved == "Startup"


@pytest.mark.parametrize("structure_input", ["private", "PRIVATE", "pRiVaTe"])
def test_legal_structure_case_insensitivity(structure_input):
    """Legal Structure enums must resolve to 'Private' regardless of casing."""
    success, resolved = normalize_and_validate_enum(structure_input, ALLOWED_LEGAL_STRUCTURES)
    assert success is True
    assert resolved == "Private"


@pytest.mark.parametrize("email_input, expected_normalized", [
    ("INFO@MICROSOFT.COM",          "INFO@microsoft.com"),
    ("user.name@SUB.DOMAIN.ORG",    "user.name@sub.domain.org"),
])
def test_email_domain_normalization(email_input, expected_normalized):
    """Email domains must be lowercased for route consistency."""
    success, normalized = normalize_email(email_input)
    assert success is True
    assert normalized == expected_normalized


@pytest.mark.parametrize("url_input, expected_normalized", [
    ("HTTPS://WWW.MICROSOFT.COM/en-US",          "https://www.microsoft.com/en-US"),
    ("HTTP://SUB.DOMAIN.ORG/Path/To/Resource",   "http://sub.domain.org/Path/To/Resource"),
])
def test_url_domain_normalization(url_input, expected_normalized):
    """URL scheme and domain must be lowercased; path case must be preserved."""
    success, normalized = normalize_url(url_input)
    assert success is True
    assert normalized == expected_normalized


@pytest.mark.parametrize("ceo_input", ["satya nadella", "SATYA NADELLA"])
def test_ceo_name_title_case_normalization(ceo_input):
    """CEO names must normalise cleanly to Title Case."""
    success, normalized = normalize_title_case(ceo_input)
    assert success is True
    assert normalized == "Satya Nadella"
    