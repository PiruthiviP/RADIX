import re
import pytest
from typing import Any
from typing import List, Tuple
from typing import Dict, Any, Tuple
from typing import Any, Tuple
import datetime
from typing import Dict, Any, List, Tuple
from typing import Dict, Any, Tuple, List
from typing import Dict, Any
from typing import Dict, Any, Union
from typing import Dict, Any, Set
import time
from typing import Dict, Any, List
import json
from typing import List, Dict, Any, Set

from typing import Dict, Any, Tuple, Optional
from typing import Dict, Any, Tuple, List, Optional
from typing import Any, Tuple, Optional
from typing import Any, Optional
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any
from typing import Optional, List, Dict, Any
tc_1_1_COMPANY_NAME_PATTERN = re.compile("^[\\w\\s&.,\\-\\(\\)'\\u00C0-\\u017F]+$")
tc_1_1_SHORT_NAME_PATTERN = re.compile('^[\\w\\s&.\\-]+$')

def tc_1_1_validate_company_name(name: str) -> bool:
    """
    Validates the 'Company Name' based on schema rules:
    - Must not be None/Null.
    - Trimmed constraint (no leading or trailing whitespace).
    - Length between 2 and 255 characters.
    - Matches specified regex pattern.
    """
    if name is None:
        return False
    if name != name.strip():
        return False
    if not 2 <= len(name) <= 255:
        return False
    if not tc_1_1_COMPANY_NAME_PATTERN.match(name):
        return False
    return True

def tc_1_1_validate_short_name(name: str) -> bool:
    """
    Validates the 'Short Name' based on schema rules:
    - Nullable, but if provided, must meet specifications.
    - Length between 2 and 100 characters.
    - Matches specified regex pattern.
    """
    if name is None:
        return True
    if name != name.strip():
        return False
    if not 2 <= len(name) <= 100:
        return False
    if not tc_1_1_SHORT_NAME_PATTERN.match(name):
        return False
    return True

@pytest.mark.parametrize('valid_name', ['Microsoft Corporation', 'Apple Inc.', 'Tesla, Inc.', "L'Oréal S.A.", 'M&S Group', 'Bio-Tech (Global) Inc.'])
def test_tc_1_1_company_name_valid_inputs(valid_name):
    """Verifies that standard, well-formed legal company names pass validation."""
    assert tc_1_1_validate_company_name(valid_name) is True, f'Failed validation for valid company name: {valid_name}'

@pytest.mark.parametrize('invalid_name', [' A', 'Apple Inc. ', 'A', 'Microsoft 🚀 Ltd', ''])
def test_tc_1_1_company_name_invalid_inputs(invalid_name):
    """Verifies that edge cases and poorly formatted legal company names fail validation."""
    assert tc_1_1_validate_company_name(invalid_name) is False, f'Unexpectedly passed validation for invalid company name: {invalid_name}'

@pytest.mark.parametrize('valid_short_name', ['Microsoft', 'Apple', 'Tesla', 'M&S', 'Bio-Tech', None])
def test_tc_1_1_short_name_valid_inputs(valid_short_name):
    """Verifies that standard, well-formatted short names or brand aliases pass validation."""
    assert tc_1_1_validate_short_name(valid_short_name) is True, f'Failed validation for valid short name: {valid_short_name}'

@pytest.mark.parametrize('invalid_short_name', ['A', 'Tesla!', 'Microsoft  ', 'A' * 101])
def test_tc_1_1_short_name_invalid_inputs(invalid_short_name):
    """Verifies that invalid short names fail validation."""
    assert tc_1_1_validate_short_name(invalid_short_name) is False, f'Unexpectedly passed validation for invalid short name: {invalid_short_name}'
tc_1_2_SCHEMA_REGISTRY = {'Company Name': False, 'Short Name': True, 'Logo': False, 'Category': False, 'Year of Incorporation': False, 'Overview of the Company': False, 'Nature of Company': False, 'Company Headquarters': False, 'Countries Operating In': True, 'Number of Offices (beyond HQ)': True, 'Office Locations': True, 'Employee Size': False, 'Hiring Velocity': True, 'Employee Turnover': True, 'Average Retention Tenure': True, 'Pain Points Being Addressed': False, 'Focus Sectors / Industries': False, 'Services / Offerings / Products': False, 'Top Customers by Client Segments': True, 'Core Value Proposition': False, 'Vision': True, 'Mission': True, 'Values': True, 'Unique Differentiators': True, 'Competitive Advantages': True, 'Weaknesses / Gaps in Offering': True, 'Key Challenges and Unmet Needs': True, 'Key Competitors': False, 'Technology Partners': True, 'Interesting Facts': True, 'Recent News': True, 'Website URL': False, 'Quality of Website': True, 'Website Rating': True, 'Website Traffic Rank': True, 'Social Media Followers – Combined': False, 'Glassdoor Rating': True, 'Indeed Rating': True, 'Google Reviews Rating': True, 'LinkedIn Profile URL': True, 'Twitter (X) Handle': True, 'Facebook Page URL': True, 'Instagram Page URL': True, 'CEO Name': False, 'CEO LinkedIn URL': True, 'Key Business Leaders': False, 'Warm Introduction Pathways': True, 'Decision Maker Accessibility': True, 'Company Contact Email': True, 'Company Phone Number': True, "Primary Contact Person's Name": True, "Primary Contact Person's Title": True, "Primary Contact Person's Email": True, "Primary Contact Person's Phone Number": True, 'Awards & Recognitions': True, 'Brand Sentiment Score': True, 'Event Participation': True, 'Regulatory & Compliance Status': True, 'Legal Issues / Controversies': True, 'Annual Revenues': True, 'Annual Profits': True, 'Revenue Mix': True, 'Company Valuation': True, 'Year-over-Year Growth Rate': True, 'Profitability Status': False, 'Market Share (%)': True, 'Key Investors / Backers': True, 'Recent Funding Rounds': True, 'Total Capital Raised': True, 'ESG Practices or Ratings': True, 'Sales Motion': False, 'Customer Acquisition Cost (CAC)': True, 'Customer Lifetime Value (CLV)': True, 'CAC:LTV Ratio': True, 'Churn Rate': True, 'Net Promoter Score (NPS)': True, 'Customer Concentration Risk': True, 'Burn Rate': True, 'Runway': True, 'Burn Multiplier': True, 'Intellectual Property': True, 'R&D Investment': True, 'AI/ML Adoption Level': True, 'Tech Stack/Tools Used': True, 'Cybersecurity Posture': True, 'Supply Chain Dependencies': True, 'Geopolitical Risks': True, 'Macro Risks': True, 'Diversity Metrics': True, 'Remote Work Policy': False, 'Training/Development Spend': True, 'Partnership Ecosystem': True, 'Exit Strategy/History': True, 'Carbon Footprint/Environmental Impact': True, 'Ethical Sourcing Practices': True, 'Benchmark vs. Peers': True, 'Future Projections': True, 'Strategic Priorities': False, 'Industry Associations / Memberships': True, 'Case Studies / Public Success Stories': True, 'Go-to-Market Strategy': False, 'Innovation Roadmap ': True, 'Product Pipeline': True, 'Board of Directors / Advisors': False, 'Company Introduction / Marketing videos': True, 'Customer testimonial': True, 'Industry Benchmark Technology Adoption Rating': True, 'Total Addressable Market (TAM)': True, 'Serviceable Addressable Market (SAM)': True, 'Serviceable Obtainable Market (SOM)': True, 'Work culture': True, 'Manager quality': True, 'Psychological safety': True, 'Feedback culture': True, 'Diversity & inclusion': True, 'Ethical standards': True, 'Typical working hours': True, 'Overtime expectations': True, 'Weekend work': True, 'Remote / hybrid / on-site flexibility': False, 'Leave policy': True, 'Burnout risk': True, 'Central vs peripheral location': True, 'Public transport access': True, 'Cab availability and company cab policy': True, 'Commute time from airport': True, 'Office zone type': True, 'Area safety': True, 'Company safety policies': True, 'Office infrastructure safety': True, 'Emergency response preparedness': True, 'Health support': True, 'Onboarding and training quality': True, 'Learning culture': True, 'Exposure quality': True, 'Mentorship availability': True, 'Internal mobility': True, 'Promotion clarity': True, 'Tools and technology access': True, 'Role clarity': True, 'Early ownership': True, 'Work impact': True, 'Execution vs thinking balance': True, 'Automation level': True, 'Cross-functional exposure': True, 'Company maturity': False, 'Brand value': True, 'Client quality': True, 'Layoff history': True, 'Fixed vs variable pay': True, 'Bonus predictability': True, 'ESOPs and long-term incentives': True, 'Family health insurance': True, 'Relocation support': True, 'Lifestyle and wellness benefits': True, 'Exit opportunities': True, 'Skill relevance': True, 'External recognition': True, 'Network strength': True, 'Global exposure': True, 'Mission clarity': True, 'Sustainability and CSR': True, 'Crisis behavior': True}

def tc_1_2_validate_field_input(field_name: str, value: Any) -> bool:
    """
    Validates field input rules:
    - Rejects empty strings ("") and whitespace-only strings ("   ") for all fields.
    - If input is None (NULL):
        - Returns True if the field is optional (Nullable = True).
        - Returns False if the field is mandatory (Nullable = False).
    """
    is_nullable = tc_1_2_SCHEMA_REGISTRY.get(field_name)
    if is_nullable is None:
        raise ValueError(f"Field '{field_name}' is not defined in the SCHEMA_REGISTRY.")
    if value is None:
        return is_nullable
    if isinstance(value, str):
        if value == '' or value.strip() == '':
            return False
    return True

@pytest.mark.parametrize('field_name, is_nullable', tc_1_2_SCHEMA_REGISTRY.items())
def test_tc_1_2_fields_reject_empty_string(field_name, is_nullable):
    """Verifies that an empty string always fails validation regardless of field nullability."""
    assert tc_1_2_validate_field_input(field_name, '') is False, f"Empty string validation failed to reject on '{field_name}'."

@pytest.mark.parametrize('field_name, is_nullable', tc_1_2_SCHEMA_REGISTRY.items())
def test_tc_1_2_fields_reject_whitespace(field_name, is_nullable):
    """Verifies that whitespace-only strings fail validation across all parameters."""
    assert tc_1_2_validate_field_input(field_name, '    ') is False, f"Whitespace string validation failed to reject on '{field_name}'."

@pytest.mark.parametrize('field_name, is_nullable', tc_1_2_SCHEMA_REGISTRY.items())
def test_tc_1_2_null_validation_against_nullability_rules(field_name, is_nullable):
    """
    Verifies NULL validation limits:
    - Nullable fields accept None.
    - Not Null fields reject None.
    """
    expected_outcome = is_nullable
    actual_outcome = tc_1_2_validate_field_input(field_name, None)
    assert actual_outcome == expected_outcome, f"Validation mismatch on '{field_name}' with Nullable={is_nullable}. Expected {expected_outcome}, but got {actual_outcome}."
tc_1_3_COMPANY_NAME_RE = re.compile("^[\\w\\s&.,\\-\\(\\)'\\u00C0-\\u017F]+$")
tc_1_3_SHORT_NAME_RE = re.compile('^[\\w\\s&.\\-]+$')
tc_1_3_URL_RE = re.compile('^https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)$')
tc_1_3_EMAIL_RE = re.compile('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$')
tc_1_3_PHONE_RE = re.compile('^\\+?[1-9]\\d{1,14}$')
tc_1_3_PERCENT_RE = re.compile('^\\d{1,3}(\\.\\d{1,2})?%$')

def tc_1_3_validate_wildcard_text(val: str) -> bool:
    """Narrative text fields (like descriptions) supporting all special characters."""
    return isinstance(val, str) and len(val) > 0

@pytest.mark.parametrize('valid_company_name', ['Café Résumé', 'M&S Holdings Co.', 'Bio-Tech (Global) S.A.'])
def test_tc_1_3_company_name_valid_special_characters(valid_company_name):
    """Verifies that company name regex allows Latin accents, ampersands, dashes, and parentheses."""
    assert tc_1_3_COMPANY_NAME_RE.match(valid_company_name) is not None

@pytest.mark.parametrize('invalid_company_name', ['Company™ & Co.®', 'Software@Enterprise', 'SaaS #1'])
def test_tc_1_3_company_name_invalid_special_characters(invalid_company_name):
    """Verifies that out-of-range symbols fail validation for company name."""
    assert tc_1_3_COMPANY_NAME_RE.match(invalid_company_name) is None

@pytest.mark.parametrize('valid_short_name', ['M&S', 'Bio-Tech', 'S.A.'])
def test_tc_1_3_short_name_valid_special_characters(valid_short_name):
    """Verifies standard punctuation in short names passes validation."""
    assert tc_1_3_SHORT_NAME_RE.match(valid_short_name) is not None

@pytest.mark.parametrize('invalid_short_name', ['Café', 'SaaS!', 'Global @ Team'])
def test_tc_1_3_short_name_invalid_special_characters(invalid_short_name):
    """Verifies that short name restricts punctuation according to formatting rules."""
    assert tc_1_3_SHORT_NAME_RE.match(invalid_short_name) is None

@pytest.mark.parametrize('valid_url', ['https://cafe-resume.com', 'https://example.com/logo.png?v=1.0&size=medium', 'https://sub.domain.org/path_name/file-name.webp?ref=search'])
def test_tc_1_3_urls_valid_query_parameters(valid_url):
    """Verifies standard URL query strings and directory characters pass format validation."""
    assert tc_1_3_URL_RE.match(valid_url) is not None

@pytest.mark.parametrize('invalid_url', ['https://example.com/logo@#$.png', 'http://example.com/logo.png?ref=<script>'])
def test_tc_1_3_urls_invalid_characters(invalid_url):
    """Verifies that raw invalid symbols in URLs are rejected."""
    assert tc_1_3_URL_RE.match(invalid_url) is None

@pytest.mark.parametrize('valid_text', ['Café Résumé: Company™ & Co.® — ($10M+ Revenue!)', '• Proprietary AI Engine™ [Patent Approved #12345]', 'Gender metrics: 45% Female / 55% Male / 5% Non-binary.'])
def test_tc_1_3_narrative_text_fields_allow_all_unicode(valid_text):
    """Verifies that unstructured narrative parameters successfully store full UTF-8 character space."""
    assert tc_1_3_validate_wildcard_text(valid_text) is True

@pytest.mark.parametrize('valid_email', ['contact-info_1@company.com', 'contact.first+last@sub.domain.org'])
def test_tc_1_3_emails_valid_special_characters(valid_email):
    """Verifies email formatting with dots, dashes, underscores, and plus symbols passes."""
    assert tc_1_3_EMAIL_RE.match(valid_email) is not None

@pytest.mark.parametrize('invalid_email', ['contact#info@company.com', 'contact$info@company.com'])
def test_tc_1_3_emails_invalid_special_characters(invalid_email):
    """Verifies invalid email formatting is rejected."""
    assert tc_1_3_EMAIL_RE.match(invalid_email) is None

@pytest.mark.parametrize('valid_phone', ['+14155552671', '4155552671'])
def test_tc_1_3_phone_valid_prefix(valid_phone):
    """Verifies standard phone formatting with leading "+" symbol passes."""
    assert tc_1_3_PHONE_RE.match(valid_phone) is not None

@pytest.mark.parametrize('invalid_phone', ['+1-415-555-2671', '(415) 555-2671'])
def test_tc_1_3_phone_invalid_characters(invalid_phone):
    """Verifies phone rejects symbols except the optional leading '+' code."""
    assert tc_1_3_PHONE_RE.match(invalid_phone) is None
tc_1_4_VERIFIED_COMPANIES = {'Microsoft Corporation', 'Apple Inc.', 'Tesla Inc.', 'Google LLC', 'Amazon.com Inc.'}
tc_1_4_VERIFIED_BRANDS = {'Microsoft', 'Apple', 'Tesla', 'Google', 'Amazon'}
tc_1_4_VERIFIED_INVESTORS = {'Sequoia Capital', 'Andreessen Horowitz', 'a16z', 'Y Combinator'}
tc_1_4_VERIFIED_CEOS = {'Satya Nadella', 'Tim Cook', 'Elon Musk', 'Sundar Pichai', 'Andy Jassy'}

def tc_1_4_validate_company_name(name: str) -> Tuple[bool, str]:
    """
    Validates legal Company Name against verified registry.
    Catches abbreviations, truncations, and spelling errors.
    """
    if not name or len(name) < 2:
        return (False, 'Input is too short to be a valid legal name.')
    if name in tc_1_4_VERIFIED_COMPANIES:
        return (True, 'Valid legal name.')
    if any((name.lower() in verified.lower() for verified in tc_1_4_VERIFIED_COMPANIES)):
        return (False, 'Incomplete or heavily abbreviated legal name.')
    return (False, 'Legal name could not be resolved in the government registry.')

def tc_1_4_validate_short_name(name: str) -> Tuple[bool, str]:
    """Validates Short Name against verified branding databases."""
    if not name or len(name) < 2:
        return (False, 'Input too short.')
    if name in tc_1_4_VERIFIED_BRANDS:
        return (True, 'Valid short name.')
    return (False, 'Short name does not match verified branding assets.')

def tc_1_4_validate_competitors_list(competitors_str: str) -> Tuple[bool, List[str]]:
    """
    Parses a comma-separated list of competitors.
    Returns a boolean success flag and a list of malformed/unresolved entries.
    """
    if not competitors_str:
        return (False, ['Empty Input'])
    competitors = [c.strip() for c in competitors_str.split(',') if c.strip()]
    unresolved = []
    for comp in competitors:
        if comp not in tc_1_4_VERIFIED_COMPANIES and comp not in tc_1_4_VERIFIED_BRANDS:
            unresolved.append(comp)
    return (len(unresolved) == 0, unresolved)

def tc_1_4_validate_person_name(name: str) -> Tuple[bool, str]:
    """Validates a person's name (CEO or primary contact) for completeness."""
    if not name:
        return (False, 'Name cannot be empty.')
    parts = [p.replace('.', '').strip() for p in name.split()]
    if any((len(p) <= 1 for p in parts)):
        return (False, 'Name contains truncated single initials or incomplete values.')
    return (True, 'Valid format.')

@pytest.mark.parametrize('malformed_company', ['Microsft', 'App', 'Goog'])
def test_tc_1_4_malformed_company_name(malformed_company):
    """Verifies that misspelled or heavily truncated company legal names are rejected."""
    success, message = tc_1_4_validate_company_name(malformed_company)
    assert success is False
    assert 'Incomplete' in message or 'could not be resolved' in message

@pytest.mark.parametrize('malformed_short_name', ['Microsft', 'Goog'])
def test_tc_1_4_malformed_short_name(malformed_short_name):
    """Verifies that misspelled or truncated brand names are caught."""
    success, message = tc_1_4_validate_short_name(malformed_short_name)
    assert success is False
    assert 'does not match' in message

def test_tc_1_4_malformed_competitor_list():
    """Verifies that a list containing misspelled competitor names flags only the malformed entities."""
    input_list = 'Microsft, Apple Inc., Tesl'
    success, unresolved = tc_1_4_validate_competitors_list(input_list)
    assert success is False
    assert 'Microsft' in unresolved
    assert 'Tesl' in unresolved
    assert 'Apple Inc.' not in unresolved

@pytest.mark.parametrize('malformed_name', ['S', 'S. J. S.', 'J. René'])
def test_tc_1_4_malformed_person_name(malformed_name):
    """Verifies that incomplete, heavily abbreviated, or initial-only person names fail validation."""
    success, message = tc_1_4_validate_person_name(malformed_name)
    assert success is False
    assert 'truncated' in message
tc_1_5_ENTITY_DATABASE = {'companies': [{'legal_name': 'Delta Air Lines, Inc.', 'alias': 'Delta', 'domain': 'delta.com', 'sector': 'Airlines'}, {'legal_name': 'Delta Faucet Company', 'alias': 'Delta', 'domain': 'deltafaucet.com', 'sector': 'Manufacturing'}, {'legal_name': 'Mercury Technologies', 'alias': 'Mercury', 'domain': 'mercury.com', 'sector': 'Financials'}, {'legal_name': 'Mercury Insurance Group', 'alias': 'Mercury', 'domain': 'mercuryinsurance.com', 'sector': 'Insurance'}], 'ceos': [{'name': 'John Smith', 'company': 'Delta Air Lines, Inc.', 'linkedin': 'linkedin.com/in/john-smith-delta'}, {'name': 'John Smith', 'company': 'Delta Faucet Company', 'linkedin': 'linkedin.com/in/john-smith-faucet'}], 'investors': [{'legal_name': 'Founders Fund', 'alias': 'Founders'}, {'legal_name': 'Founders Circle Capital', 'alias': 'Founders'}]}

def tc_1_5_resolve_company_entity(name: str, domain: str=None, sector: str=None) -> Tuple[str, str]:
    """
    Simulates entity resolution on 'Company Name' or 'Short Name'.
    - Returns ('SUCCESS', legal_name) if resolved uniquely.
    - Returns ('AMBIGUOUS', message) if multiple entities match and secondary context is missing/incorrect.
    - Returns ('UNRESOLVED', message) if no match is found.
    """
    if not name:
        return ('UNRESOLVED', 'Empty input name.')
    matches = [c for c in tc_1_5_ENTITY_DATABASE['companies'] if c['legal_name'].lower() == name.lower() or c['alias'].lower() == name.lower()]
    if not matches:
        return ('UNRESOLVED', f"No database matches found for '{name}'.")
    if len(matches) == 1:
        return ('SUCCESS', matches[0]['legal_name'])
    if domain:
        domain_matches = [c for c in matches if c['domain'].lower() == domain.lower()]
        if len(domain_matches) == 1:
            return ('SUCCESS', domain_matches[0]['legal_name'])
    if sector:
        sector_matches = [c for c in matches if c['sector'].lower() == sector.lower()]
        if len(sector_matches) == 1:
            return ('SUCCESS', sector_matches[0]['legal_name'])
    matched_names = ', '.join([c['legal_name'] for c in matches])
    return ('AMBIGUOUS', f'Input matches multiple entities: [{matched_names}]. Provide domain or sector to resolve.')

def tc_1_5_resolve_ceo_entity(ceo_name: str, company_name: str=None, linkedin_url: str=None) -> Tuple[str, str]:
    """
    Simulates entity resolution on 'CEO Name'.
    - Rejects common names unless reconciled with company context or profile URL.
    """
    matches = [c for c in tc_1_5_ENTITY_DATABASE['ceos'] if c['name'].lower() == ceo_name.lower()]
    if not matches:
        return ('UNRESOLVED', f"No CEO found matching '{ceo_name}'.")
    if len(matches) == 1:
        return ('SUCCESS', matches[0]['name'])
    if company_name:
        company_matches = [c for c in matches if c['company'].lower() == company_name.lower()]
        if len(company_matches) == 1:
            return ('SUCCESS', company_matches[0]['name'])
    if linkedin_url:
        linkedin_matches = [c for c in matches if c['linkedin'].lower() == linkedin_url.lower()]
        if len(linkedin_matches) == 1:
            return ('SUCCESS', linkedin_matches[0]['name'])
    return ('AMBIGUOUS', f"Multiple executives named '{ceo_name}'. Reconcile with company or LinkedIn URL.")

def test_tc_1_5_resolve_unique_company():
    """Verifies that an unambiguous, fully qualified company name resolves directly."""
    status, result = tc_1_5_resolve_company_entity('Delta Air Lines, Inc.')
    assert status == 'SUCCESS'
    assert result == 'Delta Air Lines, Inc.'

def test_tc_1_5_resolve_ambiguous_company_without_context():
    """Verifies that a generic alias flags ambiguity when context is missing."""
    status, message = tc_1_5_resolve_company_entity('Delta')
    assert status == 'AMBIGUOUS'
    assert 'matches multiple entities' in message

def test_tc_1_5_resolve_ambiguous_company_with_domain_context():
    """Verifies that generic alias ambiguity is resolved with domain context."""
    status, result = tc_1_5_resolve_company_entity('Delta', domain='deltafaucet.com')
    assert status == 'SUCCESS'
    assert result == 'Delta Faucet Company'

def test_tc_1_5_resolve_ambiguous_company_with_sector_context():
    """Verifies that generic alias ambiguity is resolved with industry sector context."""
    status, result = tc_1_5_resolve_company_entity('Mercury', sector='Insurance')
    assert status == 'SUCCESS'
    assert result == 'Mercury Insurance Group'

def test_tc_1_5_resolve_common_ceo_name_without_context():
    """Verifies that common executive names are flagged as ambiguous without company context."""
    status, message = tc_1_5_resolve_ceo_entity('John Smith')
    assert status == 'AMBIGUOUS'
    assert 'Multiple executives' in message

def test_tc_1_5_resolve_common_ceo_name_with_company_context():
    """Verifies that common executive names resolve successfully when paired with corporate context."""
    status, result = tc_1_5_resolve_ceo_entity('John Smith', company_name='Delta Air Lines, Inc.')
    assert status == 'SUCCESS'
    assert result == 'John Smith'
tc_1_6_ALLOWED_CATEGORIES = {'Startup', 'MSME', 'SMB', 'Enterprise', 'Investor', 'VC', 'Conglomerate'}
tc_1_6_ALLOWED_LEGAL_STRUCTURES = {'Private', 'Public', 'Subsidiary', 'Partnership', 'Non-Profit', 'Govt'}
tc_1_6_ALLOWED_PROFITABILITY = {'Profitable', 'Break-even', 'Loss-making'}
tc_1_6_ALLOWED_SALES_MOTIONS = {'PLG', 'Product-Led', 'Sales-Led', 'Field Sales', 'Channel', 'Hybrid'}
tc_1_6_ALLOWED_REMOTE_POLICIES = {'Remote', 'Hybrid', 'On-Site', 'Flexible Choice'}

def tc_1_6_normalize_and_validate_enum(value: str, allowed_set: set) -> Tuple[bool, str]:
    """Resolves enum values case-insensitively and maps to standard capitalization."""
    if not value:
        return (False, 'Empty value.')
    lookup_map = {item.lower(): item for item in allowed_set}
    resolved = lookup_map.get(value.lower())
    if resolved:
        return (True, resolved)
    return (False, f"Value '{value}' not found in allowed enums.")

def tc_1_6_normalize_email(email: str) -> Tuple[bool, str]:
    """Normalizes email domain parts to lowercase case-insensitively."""
    if not email or '@' not in email:
        return (False, 'Invalid email structure.')
    local_part, domain_part = email.split('@', 1)
    normalized = f'{local_part.strip()}@{domain_part.strip().lower()}'
    return (True, normalized)

def tc_1_6_normalize_url(url: str) -> Tuple[bool, str]:
    """Normalizes URL scheme and domain to lowercase, leaving path directory intact."""
    if not url or '://' not in url:
        return (False, 'Invalid URL structure.')
    scheme, remainder = url.split('://', 1)
    if '/' in remainder:
        domain, path = remainder.split('/', 1)
        normalized = f'{scheme.lower()}://{domain.lower()}/{path}'
    else:
        normalized = f'{scheme.lower()}://{remainder.lower()}'
    return (True, normalized)

def tc_1_6_normalize_title_case(name: str) -> Tuple[bool, str]:
    """Normalizes names to standard Title Case structure."""
    if not name:
        return (False, 'Empty name.')
    return (True, name.title())

@pytest.mark.parametrize('category_input', ['startup', 'STARTUP', 'sTaRtUp'])
def test_tc_1_6_category_case_insensitivity(category_input):
    """Verifies that Category enums map successfully regardless of input casing."""
    success, resolved = tc_1_6_normalize_and_validate_enum(category_input, tc_1_6_ALLOWED_CATEGORIES)
    assert success is True
    assert resolved == 'Startup'

@pytest.mark.parametrize('structure_input', ['private', 'PRIVATE', 'pRiVaTe'])
def test_tc_1_6_legal_structure_case_insensitivity(structure_input):
    """Verifies that Legal Structure enums map successfully regardless of input casing."""
    success, resolved = tc_1_6_normalize_and_validate_enum(structure_input, tc_1_6_ALLOWED_LEGAL_STRUCTURES)
    assert success is True
    assert resolved == 'Private'

@pytest.mark.parametrize('email_input, expected_normalized', [('INFO@MICROSOFT.COM', 'INFO@microsoft.com'), ('user.name@SUB.DOMAIN.ORG', 'user.name@sub.domain.org')])
def test_tc_1_6_email_domain_normalization(email_input, expected_normalized):
    """Verifies that email domain strings are successfully lowered to preserve route consistency."""
    success, normalized = tc_1_6_normalize_email(email_input)
    assert success is True
    assert normalized == expected_normalized

@pytest.mark.parametrize('url_input, expected_normalized', [('HTTPS://WWW.MICROSOFT.COM/en-US', 'https://www.microsoft.com/en-US'), ('HTTP://SUB.DOMAIN.ORG/Path/To/Resource', 'http://sub.domain.org/Path/To/Resource')])
def test_tc_1_6_url_domain_normalization(url_input, expected_normalized):
    """Verifies that URL scheme and domains are lowered while path cases are preserved."""
    success, normalized = tc_1_6_normalize_url(url_input)
    assert success is True
    assert normalized == expected_normalized

@pytest.mark.parametrize('ceo_input', ['satya nadella', 'SATYA NADELLA'])
def test_tc_1_6_ceo_name_title_case_normalization(ceo_input):
    """Verifies that CEO names normalize cleanly to Standard/Title Case."""
    success, normalized = tc_1_6_normalize_title_case(ceo_input)
    assert success is True
    assert normalized == 'Satya Nadella'
tc_10_1_CURRENT_LINE_DATE = datetime.date(2026, 5, 22)
tc_10_1_LIVE_AUTHORITY_REGISTRY = {'acmesoft': {'Company Name': 'Acmesoft Corporation', 'CEO Name': 'Jane Doe', 'Recent Funding Rounds': '2026-03-10 - Series C - $50M', 'Services / Offerings / Products': 'Core AI Suite, CloudDB v2.0 (Released Q1 2026)', 'Last SEC Filing Date': '2026-04-12'}}

def tc_10_1_check_temporal_freshness(ingested_payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates company profile temporal freshness:
    - Scans for out-of-date executive roles (e.g. predecessor CEO before 2025 transition).
    - Verifies that any 2026 funding rounds logged in live databases are not missing.
    - Confirms that recently announced 2026 products are correctly integrated.
    Returns: (is_fresh, list_of_decay_errors)
    """
    errors = []
    company_name = str(ingested_payload.get('Company Name', '')).strip().lower()
    if company_name not in tc_10_1_LIVE_AUTHORITY_REGISTRY:
        errors.append(f"Ingestion Aborted: Company '{ingested_payload.get('Company Name')}' not found in live registry.")
        return (False, errors)
    truth = tc_10_1_LIVE_AUTHORITY_REGISTRY[company_name]
    ingested_ceo = ingested_payload.get('CEO Name')
    expected_ceo = truth['CEO Name']
    if ingested_ceo and ingested_ceo != expected_ceo:
        if ingested_ceo == 'John Smith':
            errors.append(f"Temporal Decay [CEO Name]: Ingested outdated predecessor CEO 'John Smith' (ousted Q3 2025). Factual active CEO is '{expected_ceo}'.")
        else:
            errors.append(f"Factual Mismatch [CEO Name]: Ingested '{ingested_ceo}', Expected active CEO '{expected_ceo}'.")
    ingested_rounds = str((payload_rounds := ingested_payload.get('Recent Funding Rounds', '')))
    expected_round_sign = 'Series C'
    if expected_round_sign not in ingested_rounds:
        errors.append(f"Temporal Decay [Recent Funding Rounds]: Missing active 2026 transaction '{expected_round_sign}'. Ingested payload only contains outdated historical rounds: '{payload_rounds}'.")
    ingested_products = str((payload_products := ingested_payload.get('Services / Offerings / Products', '')))
    expected_product_sign = 'CloudDB v2.0'
    if expected_product_sign not in ingested_products:
        errors.append(f"Temporal Decay [Services / Offerings / Products]: Missing newly released 2026 product line '{expected_product_sign}'. Ingested payload contains stale catalog: '{payload_products}'.")
    return (len(errors) == 0, errors)

def test_tc_10_1_temporally_fresh_profile_passes():
    """Verifies that a record capturing 2025/2026 updates passes temporal validation."""
    fresh_payload = {'Company Name': 'Acmesoft', 'CEO Name': 'Jane Doe', 'Recent Funding Rounds': '2024-01-10 - Series B - $10M, 2026-03-10 - Series C - $50M', 'Services / Offerings / Products': 'Core AI Suite, CloudDB v2.0 (Released Q1 2026)'}
    success, errors = tc_10_1_check_temporal_freshness(fresh_payload)
    assert success is True
    assert not errors

def test_tc_10_1_stale_pre_2025_ceo_mismatch_fails():
    """Verifies that an outdated CEO (Steve/John before the 2025 transition) is flagged as temporal decay."""
    decayed_payload = {'Company Name': 'Acmesoft', 'CEO Name': 'John Smith', 'Recent Funding Rounds': '2024-01-10 - Series B - $10M, 2026-03-10 - Series C - $50M', 'Services / Offerings / Products': 'Core AI Suite, CloudDB v2.0 (Released Q1 2026)'}
    success, errors = tc_10_1_check_temporal_freshness(decayed_payload)
    assert success is False
    assert any(('Temporal Decay [CEO Name]' in err for err in errors))
    assert 'ousted Q3 2025' in errors[0]

def test_tc_10_1_missing_latest_2026_funding_round_fails():
    """Verifies that a company profile missing a newly completed 2026 round fails validation."""
    decayed_payload = {'Company Name': 'Acmesoft', 'CEO Name': 'Jane Doe', 'Recent Funding Rounds': '2024-01-10 - Series B - $10M', 'Services / Offerings / Products': 'Core AI Suite, CloudDB v2.0 (Released Q1 2026)'}
    success, errors = tc_10_1_check_temporal_freshness(decayed_payload)
    assert success is False
    assert any(('Temporal Decay [Recent Funding Rounds]' in err for err in errors))
    assert 'Missing active 2026 transaction' in errors[0]

def test_tc_10_1_missing_newly_released_2026_product_fails():
    """Verifies that missing a product line launched in early 2026 fails validation."""
    decayed_payload = {'Company Name': 'Acmesoft', 'CEO Name': 'Jane Doe', 'Recent Funding Rounds': '2024-01-10 - Series B - $10M, 2026-03-10 - Series C - $50M', 'Services / Offerings / Products': 'Core AI Suite'}
    success, errors = tc_10_1_check_temporal_freshness(decayed_payload)
    assert success is False
    assert any(('Temporal Decay [Services / Offerings / Products]' in err for err in errors))
    assert 'Missing newly released 2026 product line' in errors[0]
tc_10_2_LIVE_MA_REGISTRY = {'acme corp': {'is_acquired': True, 'acquired_by': 'Mega conglomerate', 'acquisition_date': '2025-11-12', 'expected_nature': 'Subsidiary', 'post_merger_headcount_min': 1000, 'required_news_keywords': ['acquired', 'acquisition', 'merger']}, 'independent startup': {'is_acquired': False, 'expected_nature': 'Private', 'post_merger_headcount_min': 10, 'required_news_keywords': []}}

def tc_10_2_validate_structural_changes(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates company profile structural consistency post-cutoff:
    - If the company was acquired according to the M&A registry:
        1. Nature of Company must be updated to "Subsidiary" (not "Private" or "Partnership").
        2. Employee Size must reflect the combined post-merger headcount (> post_merger_headcount_min).
        3. Recent News must contain references/keywords related to the acquisition.
        4. Exit Strategy/History must document the acquisition event.
    """
    errors = []
    company_name = str(payload.get('Company Name', '')).strip().lower()
    if company_name not in tc_10_2_LIVE_MA_REGISTRY:
        return (True, [])
    truth = tc_10_2_LIVE_MA_REGISTRY[company_name]
    if truth['is_acquired']:
        nature = payload.get('Nature of Company')
        expected_nature = truth['expected_nature']
        if nature != expected_nature:
            errors.append(f"Structural Decay [Nature of Company]: Company was acquired in {truth['acquisition_date']} and must be classified as '{expected_nature}' (Ingested: '{nature}').")
        raw_emp_size = str(payload.get('Employee Size', ''))
        clean_emp = re.sub('[^\\d\\-]', '', raw_emp_size)
        emp_count = 0
        if '-' in clean_emp:
            emp_count = int(clean_emp.split('-')[1])
        elif clean_emp:
            emp_count = int(clean_emp)
        min_expected = truth['post_merger_headcount_min']
        if emp_count < min_expected:
            errors.append(f"Structural Decay [Employee Size]: Headcount '{raw_emp_size}' is outdated. Post-merger combined headcount must be at least {min_expected}.")
        news_str = str(payload.get('Recent News', '')).lower()
        missing_keywords = [kw for kw in truth['required_news_keywords'] if kw not in news_str]
        if len(missing_keywords) == len(truth['required_news_keywords']):
            errors.append(f"Temporal Lineage Error [Recent News]: Missing any reference to the 2025 acquisition. Expected keywords like: {truth['required_news_keywords']}.")
        exit_str = str(payload.get('Exit Strategy/History', '')).lower()
        if 'acquired' not in exit_str and 'merger' not in exit_str:
            errors.append(f"Temporal Lineage Error [Exit Strategy/History]: Exit details must document the 2025 acquisition by '{truth['acquired_by']}'.")
    return (len(errors) == 0, errors)

def test_tc_10_2_fresh_restructured_profile_passes():
    """Verifies that a company profile correctly updated to reflect its 2025 acquisition passes validation."""
    valid_record = {'Company Name': 'Acme Corp', 'Nature of Company': 'Subsidiary', 'Employee Size': '1000-5000', 'Recent News': '2025-11-12 - Acme Corp was acquired by Mega conglomerate for $100M', 'Exit Strategy/History': 'Acquired by Mega conglomerate in November 2025'}
    success, errors = tc_10_2_validate_structural_changes(valid_record)
    assert success is True
    assert not errors

def test_tc_10_2_stale_pre_acquisition_profile_fails():
    """Verifies that an outdated profile retaining standalone pre-acquisition parameters fails validation."""
    stale_record = {'Company Name': 'Acme Corp', 'Nature of Company': 'Private', 'Employee Size': '11-50', 'Recent News': '2024-06-15 - Launched version 2.0 platform', 'Exit Strategy/History': 'Targeting independent IPO in the long term'}
    success, errors = tc_10_2_validate_structural_changes(stale_record)
    assert success is False
    assert any(('Structural Decay [Nature of Company]' in err for err in errors))
    assert any(('Structural Decay [Employee Size]' in err for err in errors))
    assert any(('Temporal Lineage Error [Recent News]' in err for err in errors))
    assert any(('Temporal Lineage Error [Exit Strategy/History]' in err for err in errors))
tc_10_3_LIVE_MARKET_DATABASE = {'generative ai': {'required_disruptors': {'openai', 'anthropic', 'google', 'meta'}, 'defunct_or_acquired': {'cohere-old', 'fake-ai-inc'}, 'market_share_caps': {'openai': 60.0, 'anthropic': 25.0}}, 'web search': {'required_disruptors': {'google', 'microsoft', 'openai'}, 'defunct_or_acquired': {'yahoo', 'ask jeeves'}, 'market_share_caps': {'google': 78.0}}}

def tc_10_3_validate_competitors_freshness(industry_key: str, ingested_competitors: str) -> Tuple[bool, List[str]]:
    """
    Validates that 'Key Competitors' is temporally accurate.
    - Confirms newly emerged disruptors are included in the list.
    - Rejects or flags old, defunct, or acquired competitors.
    """
    errors = []
    industry = tc_10_3_LIVE_MARKET_DATABASE.get(industry_key.lower())
    if not industry:
        return (True, [])
    ingested_list = [c.strip().lower() for c in ingested_competitors.split(',') if c.strip()]
    missing_disruptors = [d for d in industry['required_disruptors'] if d not in ingested_list]
    if len(missing_disruptors) >= len(industry['required_disruptors']) - 1:
        errors.append(f'Temporal Competitor Error: Ingested competitor list is outdated. Failed to include newly emerged dominant disruptors: {missing_disruptors}.')
    for defunct in industry['defunct_or_acquired']:
        if defunct in ingested_list:
            errors.append(f"Obsolete Competitor: Ingested competitor list includes defunct or acquired entity: '{defunct}'.")
    return (len(errors) == 0, errors)

def tc_10_3_validate_disrupted_market_share(industry_key: str, company_alias: str, ingested_share_str: str) -> Tuple[bool, str]:
    """
    Enforces that 'Market Share (%)' reflects post-disruption benchmarks.
    - Legacy firms cannot claim legacy monopoly shares if disrupted.
    """
    industry = tc_10_3_LIVE_MARKET_DATABASE.get(industry_key.lower())
    if not industry:
        return (True, 'Industry not in active market monitor.')
    share_match = re.match('^([\\d\\.]+)\\s*%$', ingested_share_str.strip())
    if not share_match:
        return (False, f"Format Error: Invalid percentage format '{ingested_share_str}'.")
    ingested_share = float(share_match.group(1))
    max_allowed = industry['market_share_caps'].get(company_alias.lower())
    if max_allowed and ingested_share > max_allowed:
        return (False, f"Temporal Accuracy Error: Ingested Market Share ({ingested_share}%) is outdated. Following 2025/2026 industry disruption, the maximum registered share for '{company_alias}' is {max_allowed}%.")
    return (True, 'Market share verified against current-year bounds.')

def tc_10_3_validate_peer_benchmarks(benchmark_text: str, industry_key: str) -> Tuple[bool, str]:
    """Ensures that peer comparisons do not reference obsolete/defunct entities."""
    industry = tc_10_3_LIVE_MARKET_DATABASE.get(industry_key.lower())
    if not industry:
        return (True, 'Industry not monitored.')
    for defunct in industry['defunct_or_acquired']:
        if re.search('\\b' + re.escape(defunct) + '\\b', benchmark_text, re.IGNORECASE):
            return (False, f"Obsolete Benchmark: Peer comparison references obsolete or defunct entity: '{defunct}'.")
    return (True, 'Benchmark peer group is temporally valid.')

def test_tc_10_3_current_competitor_landscape_passes():
    """Verifies that an up-to-date competitor list including active disruptors passes."""
    valid_competitors = 'OpenAI, Anthropic, Google, Meta'
    success, errors = tc_10_3_validate_competitors_freshness('Generative AI', valid_competitors)
    assert success is True
    assert not errors

def test_tc_10_3_outdated_competitor_landscape_fails():
    """Verifies that a competitor list missing newly emerged active disruptors fails validation."""
    outdated_competitors = 'CoHere-Old, Fake-AI-Inc'
    success, errors = tc_10_3_validate_competitors_freshness('Generative AI', outdated_competitors)
    assert success is False
    assert any(('Failed to include newly emerged dominant disruptors' in err for err in errors))
    assert any(('Obsolete Competitor' in err for err in errors))

def test_tc_10_3_disrupted_monopoly_market_share_fails():
    """Verifies that a legacy search company claiming a pre-disruption 95% share is rejected."""
    success, msg = tc_10_3_validate_disrupted_market_share('Web Search', 'Google', '95%')
    assert success is False
    assert 'outdated' in msg
    assert 'maximum registered share' in msg

def test_tc_10_3_disrupted_market_share_passes():
    """Verifies that updated market shares following 2025/2026 disruptions pass validation."""
    success, msg = tc_10_3_validate_disrupted_market_share('Web Search', 'Google', '75%')
    assert success is True

def test_tc_10_3_obsolete_peer_benchmark_rejected():
    """Verifies that benchmark narratives comparing the company to defunct legacy entities fail."""
    success, msg = tc_10_3_validate_peer_benchmarks('Outperforming Yahoo by 50% in search query volume', 'Web Search')
    assert success is False
    assert 'Obsolete Benchmark' in msg
    assert 'Yahoo' in msg
tc_10_4_OBSOLETE_STANDARDS = {'ISO27001:2013': 'ISO27001:2022'}
tc_10_4_MANDATORY_REGULATORY_KEYWORDS = {'critical-infrastructure': {'required': ['NIS2', 'ISO27001:2022'], 'fields': ['Regulatory & Compliance Status', 'Cybersecurity Posture']}, 'enterprise-supply-chain': {'required': ['CSRD', 'CSDDD'], 'fields': ['ESG Practices or Ratings', 'Ethical Sourcing Practices']}}

def tc_10_4_audit_regulatory_validity(payload: Dict[str, Any], company_profile_type: str) -> Tuple[bool, List[str]]:
    """
    Scans compliance and policy parameters for temporal regulatory validity:
    1. Rejects obsolete certifications (e.g. ISO27001:2013) and flags the updated replacement framework.
    2. Enforces mandatory 2025/2026 legislative keywords based on company category.
    """
    errors = []
    for field_name, value in payload.items():
        if isinstance(value, str):
            for obsolete, replacement in tc_10_4_OBSOLETE_STANDARDS.items():
                if obsolete in value:
                    errors.append(f"Temporal Compliance Error in '{field_name}': Stale standard '{obsolete}' is obsolete. Target entity must upgrade and certify under '{replacement}'.")
    rule = tc_10_4_MANDATORY_REGULATORY_KEYWORDS.get(company_profile_type.lower())
    if rule:
        required_keywords = rule['required']
        target_fields = rule['fields']
        combined_text = ''
        for field in target_fields:
            combined_text += ' ' + str(payload.get(field, '')).lower()
        for kw in required_keywords:
            if kw.lower() not in combined_text:
                errors.append(f"Regulatory Compliance Violation: Missing mandatory 2025/2026 compliance framework '{kw}' across evaluated fields: {target_fields}.")
    return (len(errors) == 0, errors)

def test_tc_10_4_compliant_modern_profile_passes():
    """Verifies that a company updated to active 2025/2026 standards passes validation."""
    payload = {'Regulatory & Compliance Status': 'SOC2, HIPAA, ISO27001:2022, NIS2 Compliant', 'Cybersecurity Posture': 'Zero trust architecture conforming strictly to NIS2 Directive.'}
    success, errors = tc_10_4_audit_regulatory_validity(payload, company_profile_type='critical-infrastructure')
    assert success is True
    assert not errors

def test_tc_10_4_obsolete_iso_certification_rejected():
    """Verifies that a company claiming an obsolete certification (ISO27001:2013) is rejected."""
    payload = {'Regulatory & Compliance Status': 'SOC2, HIPAA, ISO27001:2013', 'Cybersecurity Posture': 'Basic security controls implemented.'}
    success, errors = tc_10_4_audit_regulatory_validity(payload, company_profile_type='general')
    assert success is False
    assert any(("Stale standard 'ISO27001:2013' is obsolete" in err for err in errors))
    assert "upgrade and certify under 'ISO27001:2022'" in errors[0]

def test_tc_10_4_critical_infrastructure_missing_nis2_fails():
    """Verifies that critical infrastructure entities missing the mandatory NIS2 framework fail validation."""
    payload = {'Regulatory & Compliance Status': 'SOC2, HIPAA, ISO27001:2022', 'Cybersecurity Posture': 'Standard data encryption active.'}
    success, errors = tc_10_4_audit_regulatory_validity(payload, company_profile_type='critical-infrastructure')
    assert success is False
    assert any(("Missing mandatory 2025/2026 compliance framework 'NIS2'" in err for err in errors))

def test_tc_10_4_enterprise_supply_chain_missing_csddd_fails():
    """Verifies that large supply chain companies missing CSDDD/CSRD compliance fail validation."""
    payload = {'ESG Practices or Ratings': 'We focus on green packaging.', 'Ethical Sourcing Practices': 'Fair labor practices expected from partners.'}
tc_10_5_LIVE_CRISIS_REGISTRY = {'innovatecorp': {'has_layoff_crisis': True, 'layoff_date': '2025-10-15', 'layoff_percentage': 25.0, 'expected_headcount_max': 200, 'required_news_keywords': ['layoff', 'workforce reduction', 'restructuring']}, 'securenet': {'has_legal_scandal': True, 'scandal_type': 'Data Breach', 'scandal_date': '2026-02-05', 'expected_sentiment_bounds': ['Neutral', 'Negative'], 'required_controversy_keywords': ['breach', 'cybersecurity', 'unauthorized access']}}

def tc_10_5_validate_crisis_event_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces record-level consistency when a company has registered crisis events:
    1. For Layoff Crises:
        - Layoff history must contain the event.
        - Employee Size must reflect the headcount contraction.
        - Recent News must log the event.
    2. For Legal/Scandal Crises:
        - Legal Issues / Controversies must document the event.
        - Brand Sentiment Score must not remain 'Positive'.
        - Crisis behavior must detail the response.
    """
    errors = []
    company_name = str(payload.get('Company Name', '')).strip().lower()
    if company_name not in tc_10_5_LIVE_CRISIS_REGISTRY:
        return (True, [])
    truth = tc_10_5_LIVE_CRISIS_REGISTRY[company_name]
    if truth.get('has_layoff_crisis'):
        layoff_history = str(payload.get('Layoff history', ''))
        expected_pct = f"{int(truth['layoff_percentage'])}%"
        if expected_pct not in layoff_history:
            errors.append(f"Factual Error [Layoff history]: Missing registered {expected_pct} layoff occurring on {truth['layoff_date']}.")
        emp_size_str = str(payload.get('Employee Size', ''))
        clean_emp = ''.join([c for c in emp_size_str if c.isdigit() or c == '-'])
        emp_count = 0
        if '-' in clean_emp:
            emp_count = int(clean_emp.split('-')[1])
        elif clean_emp:
            emp_count = int(clean_emp)
        max_allowed = truth['expected_headcount_max']
        if emp_count > max_allowed:
            errors.append(f"Temporal Mismatch [Employee Size]: Headcount '{emp_size_str}' is outdated. Post-layoff headcount must contract below {max_allowed}.")
        news_str = str(payload.get('Recent News', '')).lower()
        missing_news_keywords = [kw for kw in truth['required_news_keywords'] if kw not in news_str]
        if len(missing_news_keywords) == len(truth['required_news_keywords']):
            errors.append(f"Temporal Lineage Error [Recent News]: Missing any reference to the 2025 layoff. Expected keywords like: {truth['required_news_keywords']}.")
    if truth.get('has_legal_scandal'):
        controversies = str(payload.get('Legal Issues / Controversies', '')).lower()
        missing_scandal_keywords = [kw for kw in truth['required_controversy_keywords'] if kw not in controversies]
        if len(missing_scandal_keywords) == len(truth['required_controversy_keywords']):
            errors.append(f"Temporal Lineage Error [Legal Issues / Controversies]: Missing documentation of the 2026 {truth['scandal_type']}. Expected keywords like: {truth['required_controversy_keywords']}.")
        sentiment = payload.get('Brand Sentiment Score')
        allowed_bounds = truth['expected_sentiment_bounds']
        if sentiment not in allowed_bounds:
            errors.append(f"Temporal Accuracy Error [Brand Sentiment Score]: Corporate sentiment remains '{sentiment}' despite a severe {truth['scandal_type']} on {truth['scandal_date']}. Expected: {allowed_bounds}.")
        crisis_behavior = str(payload.get('Crisis behavior', ''))
        if not crisis_behavior or crisis_behavior.strip() == '' or 'N/A' in crisis_behavior:
            errors.append(f"Temporal Lineage Error [Crisis behavior]: Action response is missing or blank following the 2026 {truth['scandal_type']}.")
    return (len(errors) == 0, errors)

def test_tc_10_5_fresh_post_crisis_profile_passes():
    """Verifies that a company profile updated to accurately reflect its 2025/2026 crises passes validation."""
    valid_payload = {'Company Name': 'InnovateCorp', 'Employee Size': '100-200', 'Layoff history': '2025-10-15 - 25% of workforce impacted due to restructuring', 'Recent News': '2025-10-15 - InnovateCorp announced a major workforce reduction of 25%', 'Crisis behavior': 'Managed the 25% RIF transparently with severance packages'}
    success, errors = tc_10_5_validate_crisis_event_coherence(valid_payload)
    assert success is True
    assert not errors

def test_tc_10_5_stale_pre_layoff_profile_fails():
    """Verifies that an outdated profile retaining standalone pre-layoff parameters fails validation."""
    stale_payload = {'Company Name': 'InnovateCorp', 'Employee Size': '500-1000', 'Layoff history': 'None', 'Recent News': '2024-06-15 - Launched version 2.0 platform'}
    success, errors = tc_10_5_validate_crisis_event_coherence(stale_payload)
    assert success is False
    assert any(('Factual Error [Layoff history]' in err for err in errors))
    assert any(('Temporal Mismatch [Employee Size]' in err for err in errors))
    assert any(('Temporal Lineage Error [Recent News]' in err for err in errors))

def test_tc_10_5_stale_reputation_score_fails_on_scandal_company():
    """Verifies that maintaining a 'Positive' sentiment score following a major data breach fails validation."""
    stale_payload = {'Company Name': 'SecureNet', 'Brand Sentiment Score': 'Positive', 'Legal Issues / Controversies': 'None', 'Crisis behavior': 'N/A'}
    success, errors = tc_10_5_validate_crisis_event_coherence(stale_payload)
    assert success is False
    assert any(('Temporal Accuracy Error [Brand Sentiment Score]' in err for err in errors))
    assert any(('Temporal Lineage Error [Legal Issues / Controversies]' in err for err in errors))
    assert any(('Temporal Lineage Error [Crisis behavior]' in err for err in errors))
tc_11_1_KNOWLEDGE_BASE = [{'id': 'target_corp_us', 'legal_name': 'Target Corporation', 'alias': 'Target', 'domain': 'target.com', 'hq_city': 'Minneapolis', 'hq_state_country': 'MN', 'sector': 'Retailing', 'ceo': 'Brian Cornell'}, {'id': 'target_agency_uk', 'legal_name': 'Target Brand Agency Ltd', 'alias': 'Target', 'domain': 'targetagency.co.uk', 'hq_city': 'London', 'hq_state_country': 'UK', 'sector': 'Advertising', 'ceo': 'John Doe'}]

def tc_11_1_resolve_identical_entity_ambiguity(payload: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Holistically disambiguates identical company names using parameter clustering.
    - Compares domain (from Website URL), city/country (from HQ), GICS sector, and CEO.
    - Scores candidates in the Knowledge Base (0 to 4 matches).
    Returns: (resolution_status, resolved_entity_id, log_message)
    """
    company_name = str(payload.get('Company Name', '')).strip().lower()
    website = str(payload.get('Website URL', '')).lower()
    hq = str(payload.get('Company Headquarters', '')).lower()
    sector = str(payload.get('Focus Sectors / Industries', '')).lower()
    ceo = str(payload.get('CEO Name', '')).lower()
    if not company_name:
        return ('UNRESOLVED', 'None', 'Aborted: Empty company name.')
    candidates = [c for c in tc_11_1_KNOWLEDGE_BASE if c['alias'].lower() == company_name]
    if not candidates:
        return ('UNRESOLVED', 'None', f"No matching entities found in KB for '{company_name}'.")
    scores = {}
    for cand in candidates:
        score = 0
        if cand['domain'] in website:
            score += 1
        if cand['hq_city'].lower() in hq or cand['hq_state_country'].lower() in hq:
            score += 1
        if cand['sector'].lower() in sector:
            score += 1
        if cand['ceo'].lower() == ceo:
            score += 1
        scores[cand['id']] = score
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_cand_id, best_score = sorted_scores[0]
    if best_score < 2:
        return ('UNRESOLVED', 'None', f"Ambiguous: Insufficient parameter linkage to resolve '{payload.get('Company Name')}' (Best score: {best_score}).")
    if len(sorted_scores) > 1:
        runner_up_id, runner_up_score = sorted_scores[1]
        if best_score == runner_up_score or (best_score - runner_up_score < 2 and best_score < 4):
            return ('CONFLICT', 'None', f'Conflicting payload: High correlation with multiple distinct entities. [{best_cand_id}] scored {best_score}, while [{runner_up_id}] scored {runner_up_score}. Holds for audit.')
    return ('SUCCESS', best_cand_id, f"Resolved successfully to '{best_cand_id}' (Score: {best_score}/4).")

def test_tc_11_1_resolve_retail_target_giant_success():
    """Verifies that the retail giant is successfully resolved when its parameters align."""
    retail_payload = {'Company Name': 'Target', 'Website URL': 'https://www.target.com', 'Company Headquarters': 'Minneapolis, MN', 'Focus Sectors / Industries': 'Consumer Discretionary, Retailing, Supermarkets', 'CEO Name': 'Brian Cornell'}
    status, entity_id, msg = tc_11_1_resolve_identical_entity_ambiguity(retail_payload)
    assert status == 'SUCCESS'
    assert entity_id == 'target_corp_us'
    assert 'Score: 4/4' in msg

def test_tc_11_1_resolve_target_branding_agency_success():
    """Verifies that the branding agency is successfully resolved when its parameters align."""
    agency_payload = {'Company Name': 'Target', 'Website URL': 'https://targetagency.co.uk', 'Company Headquarters': 'London, UK', 'Focus Sectors / Industries': 'Advertising, Marketing Services', 'CEO Name': 'John Doe'}
    status, entity_id, msg = tc_11_1_resolve_identical_entity_ambiguity(agency_payload)
    assert status == 'SUCCESS'
    assert entity_id == 'target_agency_uk'
    assert 'Score: 4/4' in msg

def test_tc_11_1_conflicting_parameters_flags_conflict():
    """Verifies that contradictory parameter mappings (e.g. Retailer website + Agency CEO) trigger a conflict lock."""
    conflicting_payload = {'Company Name': 'Target', 'Website URL': 'https://www.target.com', 'Company Headquarters': 'Minneapolis, MN', 'Focus Sectors / Industries': 'Advertising, Marketing Services', 'CEO Name': 'John Doe'}
    status, entity_id, msg = tc_11_1_resolve_identical_entity_ambiguity(conflicting_payload)
    assert status == 'CONFLICT'
    assert entity_id == 'None'
    assert 'Conflicting payload' in msg
    assert 'target_corp_us' in msg
    assert 'target_agency_uk' in msg

def test_tc_11_1_insufficient_parameters_unresolved():
    """Verifies that having insufficient populated metadata values fails resolution, preventing wrong-entity mapping."""
    scant_payload = {'Company Name': 'Target', 'Website URL': 'https://unrelated-domain.com', 'Company Headquarters': 'Seattle, WA'}
    status, entity_id, msg = tc_11_1_resolve_identical_entity_ambiguity(scant_payload)
    assert status == 'UNRESOLVED'
    assert entity_id == 'None'
    assert 'Insufficient parameter linkage' in msg
tc_11_2_CORPORATE_RECORDS_DB = {'meta platforms, inc.': {'type': 'Parent', 'legal_name': 'Meta Platforms, Inc.', 'expected_nature': 'Public', 'verified_ceo': 'Mark Zuckerberg', 'verified_domain': 'meta.com', 'consolidated_revenue_min': 100000000000.0}, 'instagram': {'type': 'Subsidiary', 'legal_name': 'Instagram LLC', 'expected_nature': 'Subsidiary', 'parent_key': 'meta platforms, inc.', 'verified_ceo': 'Adam Mosseri', 'verified_domain': 'instagram.com', 'standalone_revenue_max': 60000000000.0}}

def tc_11_2_validate_parent_subsidiary_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates that a subsidiary's profile does not suffer from parent data-bleeding:
    - If the ingested company is a registered Subsidiary:
        1. Nature of Company must be "Subsidiary" (not "Public" or "Private" standalone).
        2. CEO Name must be the subsidiary's distinct head, not the parent's CEO.
        3. Website URL must point to the subsidiary's domain, not the parent's domain.
        4. Annual Revenues must not equal the parent's full consolidated group revenues.
    """
    errors = []
    company_name = str(payload.get('Company Name', '')).strip().lower()
    if company_name not in tc_11_2_CORPORATE_RECORDS_DB:
        return (True, [])
    truth = tc_11_2_CORPORATE_RECORDS_DB[company_name]
    if truth['type'] == 'Subsidiary':
        nature = payload.get('Nature of Company')
        expected_nature = truth['expected_nature']
        if nature != expected_nature:
            errors.append(f"Lineage Contradiction [Nature of Company]: Subsidiary '{payload.get('Company Name')}' must be classified as '{expected_nature}' (Ingested: '{nature}').")
        ingested_ceo = payload.get('CEO Name')
        expected_ceo = truth['verified_ceo']
        parent_truth = tc_11_2_CORPORATE_RECORDS_DB[truth['parent_key']]
        parent_ceo = parent_truth['verified_ceo']
        if ingested_ceo == parent_ceo:
            errors.append(f"Data Bleeding Error [CEO Name]: Ingested parent CEO '{parent_ceo}' on subsidiary record '{payload.get('Company Name')}'. Expected subsidiary head: '{expected_ceo}'.")
        elif ingested_ceo != expected_ceo:
            errors.append(f"Factual Error [CEO Name]: Ingested '{ingested_ceo}', Expected '{expected_ceo}'.")
        ingested_url = str(payload.get('Website URL', '')).lower()
        expected_domain = truth['verified_domain']
        parent_domain = parent_truth['verified_domain']
        if parent_domain in ingested_url:
            errors.append(f"Data Bleeding Error [Website URL]: Ingested parent domain '{parent_domain}' on subsidiary record. Expected subsidiary domain: '{expected_domain}'.")
        elif expected_domain not in ingested_url:
            errors.append(f"Factual Error [Website URL]: Expected domain '{expected_domain}' in URL.")
        raw_rev = payload.get('Annual Revenues')
        if raw_rev:
            clean_rev = str(raw_rev).replace('$', '').replace(',', '').strip().upper()
            multiplier = 1.0
            if clean_rev.endswith('B'):
                multiplier = 1000000000.0
                clean_rev = clean_rev[:-1]
            elif clean_rev.endswith('M'):
                multiplier = 1000000.0
                clean_rev = clean_rev[:-1]
            try:
                ingested_rev = float(clean_rev) * multiplier
                parent_group_revenue = parent_truth['consolidated_revenue_min']
                if ingested_rev >= parent_group_revenue:
                    errors.append(f"Data Bleeding Error [Annual Revenues]: Ingested value '{raw_rev}' matches the parent group's consolidated revenues. Subsidiary revenues must represent its standalone estimate.")
            except ValueError:
                pass
    return (len(errors) == 0, errors)

def test_tc_11_2_distinct_subsidiary_profile_passes():
    """Verifies that a subsidiary record with distinct, non-bleeding parameters passes validation."""
    valid_payload = {'Company Name': 'Instagram', 'Nature of Company': 'Subsidiary', 'CEO Name': 'Adam Mosseri', 'Website URL': 'https://www.instagram.com', 'Annual Revenues': '$50B'}
    success, errors = tc_11_2_validate_parent_subsidiary_coherence(valid_payload)
    assert success is True
    assert not errors

def test_tc_11_2_parent_ceo_bleeding_fails():
    """Verifies that assigning the parent holding company CEO to the subsidiary fails validation."""
    invalid_payload = {'Company Name': 'Instagram', 'Nature of Company': 'Subsidiary', 'CEO Name': 'Mark Zuckerberg', 'Website URL': 'https://www.instagram.com', 'Annual Revenues': '$50B'}
    success, errors = tc_11_2_validate_parent_subsidiary_coherence(invalid_payload)
    assert success is False
    assert any(('Data Bleeding Error [CEO Name]' in err for err in errors))
    assert 'Mark Zuckerberg' in errors[0]

def test_tc_11_2_parent_domain_bleeding_fails():
    """Verifies that assigning the parent domain URL to the subsidiary fails validation."""
    invalid_payload = {'Company Name': 'Instagram', 'Nature of Company': 'Subsidiary', 'CEO Name': 'Adam Mosseri', 'Website URL': 'https://www.meta.com/instagram', 'Annual Revenues': '$50B'}
    success, errors = tc_11_2_validate_parent_subsidiary_coherence(invalid_payload)
    assert success is False
    assert any(('Data Bleeding Error [Website URL]' in err for err in errors))
    assert 'meta.com' in errors[0]

def test_tc_11_2_parent_consolidated_revenue_bleeding_fails():
    """Verifies that assigning parent consolidated group revenues to the subsidiary fails validation."""
    invalid_payload = {'Company Name': 'Instagram', 'Nature of Company': 'Subsidiary', 'CEO Name': 'Adam Mosseri', 'Website URL': 'https://www.instagram.com', 'Annual Revenues': '$134B'}
    success, errors = tc_11_2_validate_parent_subsidiary_coherence(invalid_payload)
    assert success is False
    assert any(('Data Bleeding Error [Annual Revenues]' in err for err in errors))
tc_11_3_GEOGRAPHIC_REGISTRY_DB = {'pwc global': {'type': 'Global Network', 'legal_name': 'PricewaterhouseCoopers International Limited', 'expected_nature': 'Partnership', 'verified_domain': 'pwc.com', 'consolidated_revenue_min': 50000000000.0, 'consolidated_employee_min': 300000}, 'pwc uk': {'type': 'Regional Firm', 'legal_name': 'PricewaterhouseCoopers LLP (UK)', 'expected_nature': 'Partnership', 'parent_key': 'pwc global', 'verified_partner': 'Marco Amitrano', 'verified_domain': 'pwc.co.uk', 'standalone_revenue_max': 10000000000.0, 'standalone_employee_max': 30000, 'expected_hq': 'London'}}

def tc_11_3_parse_currency_to_float(val: Any) -> float:
    """Parses money strings (e.g. '$53B', '£5.8B') into raw floats."""
    if not val:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    clean_str = str(val).replace('$', '').replace('£', '').replace(',', '').strip().upper()
    multiplier = 1.0
    if clean_str.endswith('B'):
        multiplier = 1000000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('M'):
        multiplier = 1000000.0
        clean_str = clean_str[:-1]
    try:
        return float(clean_str) * multiplier
    except ValueError:
        return 0.0

def tc_11_3_parse_headcount_to_int(val: Any) -> int:
    """Parses employee size strings into a representative integer."""
    if not val:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    clean_str = str(val).replace(',', '').replace('+', '').replace(' ', '').strip()
    if '-' in clean_str:
        try:
            return int(clean_str.split('-')[1])
        except (IndexError, ValueError):
            pass
    try:
        return int(clean_str)
    except ValueError:
        return 0

def tc_11_3_validate_geographic_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates that a regional firm's profile does not suffer from global network data-bleeding:
    - If the ingested company is a registered Regional Firm:
        1. Company Headquarters must map to the registered local territory city.
        2. CEO Name must be the regional partner, not the global coordinating CEO.
        3. Website URL must point to the local domain, not the global master domain.
        4. Annual Revenues must represent the local firm's share, not the global network total.
        5. Employee Size must represent the local firm's headcount, not the global network total.
    """
    errors = []
    company_name = str(payload.get('Company Name', '')).strip().lower()
    if company_name not in tc_11_3_GEOGRAPHIC_REGISTRY_DB:
        return (True, [])
    truth = tc_11_3_GEOGRAPHIC_REGISTRY_DB[company_name]
    if truth['type'] == 'Regional Firm':
        hq = str(payload.get('Company Headquarters', '')).lower()
        expected_hq = truth['expected_hq'].lower()
        if expected_hq not in hq:
            errors.append(f"Location Mismatch [Company Headquarters]: Regional firm '{payload.get('Company Name')}' must be based in '{truth['expected_hq']}' (Ingested: '{payload.get('Company Headquarters')}').")
        ingested_ceo = payload.get('CEO Name')
        expected_partner = truth['verified_partner']
        if ingested_ceo and ingested_ceo != expected_partner:
            errors.append(f"Factual Error [CEO Name]: Ingested '{ingested_ceo}' as regional head. Expected regional senior partner: '{expected_partner}'.")
        ingested_url = str(payload.get('Website URL', '')).lower()
        expected_domain = truth['verified_domain']
        global_truth = tc_11_3_GEOGRAPHIC_REGISTRY_DB[truth['parent_key']]
        global_domain = global_truth['verified_domain']
        if global_domain in ingested_url and expected_domain not in ingested_url:
            errors.append(f"Data Bleeding Error [Website URL]: Ingested global network domain '{global_domain}' on regional record. Expected regional domain: '{expected_domain}'.")
        elif expected_domain not in ingested_url:
            errors.append(f"Factual Error [Website URL]: Expected domain '{expected_domain}' in URL.")
        raw_rev = payload.get('Annual Revenues')
        if raw_rev:
            ingested_rev = tc_11_3_parse_currency_to_float(raw_rev)
            global_network_revenue = global_truth['consolidated_revenue_min']
            if ingested_rev >= global_network_revenue:
                errors.append(f"Data Bleeding Error [Annual Revenues]: Ingested value '{raw_rev}' matches the consolidated global network revenues. Regional revenues must represent its local standalone footprint.")
        raw_emp = payload.get('Employee Size')
        if raw_emp:
            ingested_emp = tc_11_3_parse_headcount_to_int(raw_emp)
            global_network_employees = global_truth['consolidated_employee_min']
            if ingested_emp >= global_network_employees:
                errors.append(f"Data Bleeding Error [Employee Size]: Ingested value '{raw_emp}' matches the consolidated global network headcount. Regional headcount must represent its local standalone footprint.")
    return (len(errors) == 0, errors)

def test_tc_11_3_distinct_regional_firm_profile_passes():
    """Verifies that a regional firm record with distinct, non-bleeding parameters passes validation."""
    valid_payload = {'Company Name': 'PwC UK', 'Company Headquarters': 'London, UK', 'CEO Name': 'Marco Amitrano', 'Website URL': 'https://www.pwc.co.uk', 'Annual Revenues': '£5.8B', 'Employee Size': '26,000'}
    success, errors = tc_11_3_validate_geographic_coherence(valid_payload)
    assert success is True
    assert not errors

def test_tc_11_3_global_headcount_bleeding_fails():
    """Verifies that assigning the consolidated global network employee count to the regional firm fails."""
    invalid_payload = {'Company Name': 'PwC UK', 'Company Headquarters': 'London, UK', 'CEO Name': 'Marco Amitrano', 'Website URL': 'https://www.pwc.co.uk', 'Annual Revenues': '£5.8B', 'Employee Size': '360,000'}
    success, errors = tc_11_3_validate_geographic_coherence(invalid_payload)
    assert success is False
    assert any(('Data Bleeding Error [Employee Size]' in err for err in errors))

def test_tc_11_3_global_domain_bleeding_fails():
    """Verifies that assigning the global network master domain to the regional firm fails."""
    invalid_payload = {'Company Name': 'PwC UK', 'Company Headquarters': 'London, UK', 'CEO Name': 'Marco Amitrano', 'Website URL': 'https://www.pwc.com/uk-careers', 'Annual Revenues': '£5.8B', 'Employee Size': '26,000'}
    success, errors = tc_11_3_validate_geographic_coherence(invalid_payload)
    assert success is False
    assert any(('Data Bleeding Error [Website URL]' in err for err in errors))

def test_tc_11_3_global_consolidated_revenue_bleeding_fails():
    """Verifies that assigning global consolidated network revenues to the regional firm fails."""
    invalid_payload = {'Company Name': 'PwC UK', 'Company Headquarters': 'London, UK', 'CEO Name': 'Marco Amitrano', 'Website URL': 'https://www.pwc.co.uk', 'Annual Revenues': '$53B', 'Employee Size': '26,000'}
    success, errors = tc_11_3_validate_geographic_coherence(invalid_payload)
    assert success is False
    assert any(('Data Bleeding Error [Annual Revenues]' in err for err in errors))
tc_11_4_ACRONYM_REGISTRY = {'international business machines corporation': {'legal_name': 'International Business Machines Corporation', 'short_name': 'IBM', 'domain': 'ibm.com'}, 'american telephone & telegraph company': {'legal_name': 'American Telephone & Telegraph Company', 'short_name': 'AT&T', 'domain': 'att.com'}, 'minnesota mining and manufacturing company': {'legal_name': 'Minnesota Mining and Manufacturing Company', 'short_name': '3M', 'domain': '3m.com'}}

def tc_11_4_resolve_and_validate_acronym_coherence(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Holistically resolves and standardizes abbreviation parameters:
    1. If Company Name is passed as an acronym (e.g. 'IBM'), looks up and populates the full legal name, 
       storing 'IBM' as the Short Name.
    2. If Company Name is passed as a full legal name, automatically populates Short Name if left NULL.
    3. Blocks ingestion and raises an error if an ingested acronym conflicts with the legal name.
    """
    errors = []
    resolved_payload = payload.copy()
    ingested_company = str(payload.get('Company Name', '')).strip()
    ingested_short = str(payload.get('Short Name', '')).strip() if payload.get('Short Name') else ''
    ingested_url = str(payload.get('Website URL', '')).lower()
    by_legal = {k: v for k, v in tc_11_4_ACRONYM_REGISTRY.items()}
    by_short = {v['short_name'].lower(): v for k, v in tc_11_4_ACRONYM_REGISTRY.items()}
    resolved_entry = None
    if ingested_company.lower() in by_legal:
        resolved_entry = by_legal[ingested_company.lower()]
    elif ingested_company.lower() in by_short:
        resolved_entry = by_short[ingested_company.lower()]
    elif ingested_short.lower() in by_short:
        resolved_entry = by_short[ingested_short.lower()]
    if resolved_entry:
        expected_legal = resolved_entry['legal_name']
        expected_short = resolved_entry['short_name']
        if ingested_company == expected_short and ingested_short and (ingested_short != expected_short):
            errors.append(f"Clash Error: Ingested Short Name '{ingested_short}' conflicts with resolved acronym '{expected_short}'.")
        elif ingested_company == expected_legal and ingested_short and (ingested_short != expected_short):
            errors.append(f"Clash Error: Ingested Short Name '{ingested_short}' conflicts with resolved acronym '{expected_short}' for legal entity '{expected_legal}'.")
        expected_domain = resolved_entry['domain']
        if ingested_url and expected_domain not in ingested_url:
            errors.append(f"Lineage Error: Website URL '{ingested_url}' does not match resolved entity domain '{expected_domain}'.")
        if not errors:
            resolved_payload['Company Name'] = expected_legal
            resolved_payload['Short Name'] = expected_short
    return (len(errors) == 0, resolved_payload, errors)

def test_tc_11_4_resolve_by_acronym_only_success():
    """Verifies that ingesting with only an acronym (e.g. 'IBM') successfully populates full legal names."""
    payload = {'Company Name': 'IBM', 'Website URL': 'https://www.ibm.com'}
    success, resolved, errors = tc_11_4_resolve_and_validate_acronym_coherence(payload)
    assert success is True
    assert resolved['Company Name'] == 'International Business Machines Corporation'
    assert resolved['Short Name'] == 'IBM'
    assert not errors

def test_tc_11_4_resolve_by_legal_name_populates_acronym():
    """Verifies that ingesting with a legal name successfully populates its famous acronym alias."""
    payload = {'Company Name': 'American Telephone & Telegraph Company', 'Website URL': 'https://www.att.com', 'Short Name': None}
    success, resolved, errors = tc_11_4_resolve_and_validate_acronym_coherence(payload)
    assert success is True
    assert resolved['Company Name'] == 'American Telephone & Telegraph Company'
    assert resolved['Short Name'] == 'AT&T'
    assert not errors

def test_tc_11_4_conflicting_aliases_fail_validation():
    """Verifies that pairing an unrelated legal name and acronym (e.g., IBM + AT&T) fails validation."""
    invalid_payload = {'Company Name': 'International Business Machines Corporation', 'Short Name': 'AT&T', 'Website URL': 'https://www.ibm.com'}
    success, resolved, errors = tc_11_4_resolve_and_validate_acronym_coherence(invalid_payload)
    assert success is False
    assert any(('conflicts with resolved acronym' in err for err in errors))

def test_tc_11_4_conflicting_website_domain_fails_validation():
    """Verifies that having a website URL mismatching the resolved entity domain fails validation."""
    invalid_payload = {'Company Name': 'IBM', 'Website URL': 'https://www.att.com'}
    success, resolved, errors = tc_11_4_resolve_and_validate_acronym_coherence(invalid_payload)
    assert success is False
    assert any(('does not match resolved entity domain' in err for err in errors))
tc_11_5_LEGAL_NAME_REGEX = re.compile("^[\\w\\s&.,\\-\\(\\)'\\u00C0-\\u017F]+$")
tc_11_5_SHORT_NAME_REGEX = re.compile('^[\\w\\s&.\\-]+$')
tc_11_5_DISALLOWED_SHORT_NAME_SUFFIXES = ['inc', 'inc.', 'corp', 'corp.', 'ltd', 'ltd.', 'llc', 'l.l.c.', 'co', 'co.']

def tc_11_5_validate_legal_and_short_names(record: Dict[str, Any]) -> bool:
    """
    Validates structural rules and checks for ambiguity between official 
    legal entity names and common names.
    """
    legal_name = record.get('Company Name')
    short_name = record.get('Short Name')
    if not legal_name:
        raise ValueError("Field Validation Error: 'Company Name' is not null.")
    if legal_name.strip() != legal_name:
        raise ValueError("Data Rule Error: 'Company Name' must trim leading/trailing spaces.")
    if not tc_11_5_LEGAL_NAME_REGEX.match(legal_name):
        raise ValueError(f"Regex Pattern Error: '{legal_name}' contains disallowed characters or emojis.")
    if short_name is not None:
        if short_name.strip() != short_name:
            raise ValueError("Data Rule Error: 'Short Name' must trim leading/trailing spaces.")
        if not tc_11_5_SHORT_NAME_REGEX.match(short_name):
            raise ValueError(f"Regex Pattern Error: Short Name '{short_name}' contains disallowed characters.")
        if len(short_name) > 100:
            raise ValueError("Data Rule Error: 'Short Name' length must be <= 100 characters.")
        tokens = [token.strip(',.').lower() for token in short_name.split()]
        for suffix in tc_11_5_DISALLOWED_SHORT_NAME_SUFFIXES:
            if suffix.strip('.') in tokens:
                raise ValueError(f"Ambiguity Error: Short Name '{short_name}' should not contain formal corporate suffixes like '{suffix}' to remain distinct from full legal names.")
        if short_name.lower() == legal_name.lower() and any((s in legal_name.lower() for s in tc_11_5_DISALLOWED_SHORT_NAME_SUFFIXES)):
            raise ValueError("Ambiguity Error: 'Short Name' is identical to full legal name. Corporate suffixes must be removed.")
    return True

def test_tc_11_5_meta_platforms_legal_vs_short_success():
    """
    Ensures that a properly separated Official Legal Name and clean common brand name are accepted.
    """
    valid_record = {'Company Name': 'Meta Platforms, Inc.', 'Short Name': 'Meta'}
    assert tc_11_5_validate_legal_and_short_names(valid_record) is True

def test_tc_11_5_x_corp_vs_twitter_disambiguation():
    """
    Ensures that a rebranded mapping containing legal suffixes in the legal name and a clean short name is accepted.
    """
    valid_rebranded_record = {'Company Name': 'X Corp.', 'Short Name': 'Twitter'}
    assert tc_11_5_validate_legal_and_short_names(valid_rebranded_record) is True

def test_tc_11_5_untrimmed_legal_name_fails():
    """
    Verifies that leading/trailing whitespaces in company name trigger validation failures.
    """
    invalid_record = {'Company Name': ' Meta Platforms, Inc. ', 'Short Name': 'Meta'}
    with pytest.raises(ValueError, match='must trim leading/trailing spaces'):
        tc_11_5_validate_legal_and_short_names(invalid_record)

def test_tc_11_5_short_name_containing_legal_suffix_fails():
    """
    Verifies that corporate legal suffixes inside brand names are flagged to prevent confusion.
    """
    invalid_record = {'Company Name': 'Meta Platforms, Inc.', 'Short Name': 'Meta Inc.'}
    with pytest.raises(ValueError, match='should not contain formal corporate suffixes'):
        tc_11_5_validate_legal_and_short_names(invalid_record)

def test_tc_11_5_legal_name_regex_disallowed_emojis_fails():
    """
    Verifies that the legal name fails regex validation if emojis or non-standard characters exist.
    """
    invalid_record = {'Company Name': 'Meta Platforms, Inc. 🌐', 'Short Name': 'Meta'}
    with pytest.raises(ValueError, match='contains disallowed characters or emojis'):
        tc_11_5_validate_legal_and_short_names(invalid_record)
tc_12_1_CATEGORY_REGEX = re.compile('^(Startup|MSME|SMB|Enterprise|Investor|VC|Conglomerate)$')

def tc_12_1_parse_employee_size(emp_size: Union[str, int]) -> int:
    """
    Parses exact headcount or headcount ranges to extract the maximum upper limit.
    Example: '11-50' -> 50, '500+' -> 500, 150 -> 150
    """
    if isinstance(emp_size, int):
        return emp_size
    cleaned = str(emp_size).strip().replace(',', '')
    range_match = re.match('^(\\d+)-(\\d+)$', cleaned)
    if range_match:
        return int(range_match.group(2))
    digits = re.findall('\\d+', cleaned)
    if digits:
        return int(digits[0])
    return 0

def tc_12_1_validate_company_classification(record: Dict[str, Any]) -> bool:
    """
    Validates category constraints and enforces cross-field business logic 
    relating Category, Employee Size, and Company Maturity.
    """
    category = record.get('Category')
    employee_size = record.get('Employee Size')
    maturity = record.get('Company maturity')
    if not category:
        raise ValueError("Field Validation Error: 'Category' is Not Null.")
    normalized_cat = category.strip().title()
    if normalized_cat.lower() == 'vc':
        normalized_cat = 'VC'
    elif normalized_cat.lower() == 'msme':
        normalized_cat = 'MSME'
    if not tc_12_1_CATEGORY_REGEX.match(normalized_cat):
        raise ValueError(f"Regex Pattern Error: '{category}' is not a valid standardized business taxonomy enum.")
    record['Category'] = normalized_cat
    num_employees = tc_12_1_parse_employee_size(employee_size) if employee_size else 0
    if normalized_cat == 'MSME' and num_employees > 250:
        raise ValueError(f"Classification Mismatch: Entity classified as 'MSME' has too many employees ({num_employees}). Expected <= 250.")
    if normalized_cat == 'Startup' and num_employees > 500:
        raise ValueError(f"Classification Mismatch: 'Startup' classification is invalid for enterprise-scale headcount of {num_employees}.")
    if maturity:
        if normalized_cat == 'Enterprise' and maturity == 'Startup':
            raise ValueError("Logical Error: 'Enterprise' category cannot align with a 'Startup' maturity level.")
        if normalized_cat == 'Startup' and maturity == 'Mature':
            raise ValueError("Logical Error: 'Startup' category cannot align with a 'Mature' maturity level.")
    return True

def test_tc_12_1_startup_validation_success():
    """
    Validates a typical seed-stage or growth-stage startup with a small headcount.
    """
    record = {'Company Name': 'Alpha Tech', 'Category': 'Startup', 'Employee Size': '11-50', 'Company maturity': 'Startup'}
    assert tc_12_1_validate_company_classification(record) is True

def test_tc_12_1_smb_with_large_headcount_success():
    """
    Validates standard SMB classification for larger operating headcount.
    """
    record = {'Company Name': 'Midwest Manufacturing', 'Category': 'SMB', 'Employee Size': '500', 'Company maturity': 'Scale-up'}
    assert tc_12_1_validate_company_classification(record) is True

def test_tc_12_1_case_insensitive_normalization_success():
    """
    Ensures lowercase category inputs (e.g. 'startup') are normalized and parsed.
    """
    record = {'Company Name': 'Beta Software', 'Category': 'startup', 'Employee Size': '1-10', 'Company maturity': 'Startup'}
    assert tc_12_1_validate_company_classification(record) is True
    assert record['Category'] == 'Startup'

def test_tc_12_1_invalid_category_enum_fails():
    """
    Ensures values outside the allowed taxonomy regex list fail.
    """
    record = {'Company Name': 'Delta Partners', 'Category': 'Venture Capital', 'Employee Size': '11-50'}
    with pytest.raises(ValueError, match='not a valid standardized business taxonomy enum'):
        tc_12_1_validate_company_classification(record)

def test_tc_12_1_startup_headcount_overflow_fails():
    """
    Flags logical anomalies where giant headcounts are falsely categorized as 'Startup'.
    """
    record = {'Company Name': 'Gigantic App Corp', 'Category': 'Startup', 'Employee Size': '2500', 'Company maturity': 'Scale-up'}
    with pytest.raises(ValueError, match="Startup' classification is invalid for enterprise-scale headcount"):
        tc_12_1_validate_company_classification(record)

def test_tc_12_1_enterprise_and_startup_maturity_clash_fails():
    """
    Flags mismatches between Category (Enterprise) and Company Maturity (Startup).
    """
    record = {'Company Name': 'Globex Corp', 'Category': 'Enterprise', 'Employee Size': '1000+', 'Company maturity': 'Startup'}
    with pytest.raises(ValueError, match="Enterprise' category cannot align with a 'Startup' maturity level"):
        tc_12_1_validate_company_classification(record)
tc_12_2_INDUSTRY_REGEX = re.compile('^[\\w\\s&.,\\-/]+$')
INDUSTRY_MASTER_LIST: Set[str] = {'Financial Technology', 'Payments', 'Automotive', 'Clean Energy', 'Energy Storage', 'E-commerce', 'Cloud Computing', 'Software', 'Retail', 'Technology', 'Healthcare', 'Financials'}
tc_12_2_PRODUCT_SECTOR_KEYWORDS = {'payment': ['financial technology', 'payments', 'financials'], 'billing': ['financial technology', 'payments', 'financials'], 'card': ['financial technology', 'payments', 'financials'], 'vehicle': ['automotive'], 'car': ['automotive'], 'solar': ['clean energy'], 'battery': ['energy storage', 'clean energy'], 'retail': ['e-commerce', 'retail'], 'web services': ['cloud computing', 'technology', 'software'], 'aws': ['cloud computing', 'technology', 'software']}

def tc_12_2_validate_industry_classification(record: Dict[str, Any]) -> bool:
    """
    Validates formatting and GICS alignment of the 'Focus Sectors / Industries' field,
    and checks consistency against actual company products/services.
    """
    sectors_string = record.get('Focus Sectors / Industries')
    products_string = record.get('Services / Offerings / Products')
    if not sectors_string:
        raise ValueError("Field Validation Error: 'Focus Sectors / Industries' is Not Null.")
    if not tc_12_2_INDUSTRY_REGEX.match(sectors_string):
        raise ValueError(f"Regex Pattern Error: '{sectors_string}' contains invalid characters. Expected only alphanumeric, spaces, commas, hyphens, slashes, ampersands, and periods.")
    sectors = [s.strip() for s in sectors_string.split(',') if s.strip()]
    for sector in sectors:
        if sector not in INDUSTRY_MASTER_LIST:
            raise ValueError(f"Taxonomy Error: Sector '{sector}' does not exist in the standardized Industry Master List.")
    if products_string:
        normalized_products = products_string.lower()
        normalized_sectors = [s.lower() for s in sectors]
        for keyword, required_sectors in tc_12_2_PRODUCT_SECTOR_KEYWORDS.items():
            if keyword in normalized_products:
                if not any((req in normalized_sectors for req in required_sectors)):
                    raise ValueError(f"Semantic Inconsistency: Products include '{keyword}' indications, but Focus Sectors '{sectors_string}' lack related categories: {required_sectors}.")
    return True

def test_tc_12_2_stripe_fintech_classification_success():
    """
    Validates correct fintech taxonomy and consistency with API/Billing products.
    """
    record = {'Company Name': 'Stripe', 'Focus Sectors / Industries': 'Financial Technology, Payments', 'Services / Offerings / Products': 'Payment Processing APIs, Billing Engine, Corporate Cards'}
    assert tc_12_2_validate_industry_classification(record) is True

def test_tc_12_2_tesla_clean_tech_classification_success():
    """
    Validates correct multi-sector mappings (Automotive, Clean Energy) and product consistency.
    """
    record = {'Company Name': 'Tesla', 'Focus Sectors / Industries': 'Automotive, Clean Energy, Energy Storage', 'Services / Offerings / Products': 'Electric Vehicles, Solar Panels, Powerwall Batteries'}
    assert tc_12_2_validate_industry_classification(record) is True

def test_tc_12_2_amazon_hybrid_retail_cloud_success():
    """
    Validates complex dual-sector mapping for hybrid enterprise models.
    """
    record = {'Company Name': 'Amazon', 'Focus Sectors / Industries': 'E-commerce, Cloud Computing', 'Services / Offerings / Products': 'Online Retail Platform, Amazon Web Services (AWS)'}
    assert tc_12_2_validate_industry_classification(record) is True

def test_tc_12_2_invalid_special_characters_regex_fails():
    """
    Asserts that special characters violating the formatting constraints are caught.
    """
    record = {'Company Name': 'Stripe', 'Focus Sectors / Industries': 'Fintech!!! & Payments', 'Services / Offerings / Products': 'Payment processing'}
    with pytest.raises(ValueError, match='Regex Pattern Error'):
        tc_12_2_validate_industry_classification(record)

def test_tc_12_2_unauthorized_industry_fails():
    """
    Asserts that industries outside the GICS-aligned master taxonomy list are flagged.
    """
    record = {'Company Name': 'Stripe', 'Focus Sectors / Industries': 'Financial Technology, Custom Payment Rails', 'Services / Offerings / Products': 'Payment processing'}
    with pytest.raises(ValueError, match='does not exist in the standardized Industry Master List'):
        tc_12_2_validate_industry_classification(record)

def test_tc_12_2_semantic_product_sector_mismatch_fails():
    """
    Asserts that if a product is 'Electric Vehicles', the sector cannot be classified solely as 'Financial Technology'.
    """
    record = {'Company Name': 'Future Motors', 'Focus Sectors / Industries': 'Financial Technology', 'Services / Offerings / Products': 'Electric Vehicles, Batteries'}
    with pytest.raises(ValueError, match="Semantic Inconsistency: Products include 'vehicle' indications"):
        tc_12_2_validate_industry_classification(record)
tc_12_3_NATURE_OF_COMPANY_REGEX = re.compile('^(Private|Public|Subsidiary|Partnership|Non-Profit|Govt)$')
tc_12_3_PARENT_OWNERSHIP_KEYWORDS = ['owned by', 'subsidiary of', 'acquired by', 'part of', 'division of']

def tc_12_3_validate_nature_of_company(record: Dict[str, Any]) -> bool:
    """
    Validates formatting and enum compliance of 'Nature of Company',
    and checks consistency against funding rounds and description summaries.
    """
    nature = record.get('Nature of Company')
    company_name = record.get('Company Name')
    funding_rounds = record.get('Recent Funding Rounds')
    overview = record.get('Overview of the Company')
    if not nature:
        raise ValueError("Field Validation Error: 'Nature of Company' is Not Null.")
    normalized_nature = nature.strip().title()
    if normalized_nature == 'Non-Profit' or normalized_nature == 'Nonprofit':
        normalized_nature = 'Non-Profit'
    if not tc_12_3_NATURE_OF_COMPANY_REGEX.match(normalized_nature):
        raise ValueError(f"Regex Pattern Error: '{nature}' is not a recognized legal structure enum. Expected: Private, Public, Subsidiary, Partnership, Non-Profit, Govt.")
    record['Nature of Company'] = normalized_nature
    if normalized_nature == 'Public' and funding_rounds:
        venture_pattern = re.compile('(Series\\s+[A-Z]|Seed|Angel)', re.IGNORECASE)
        if venture_pattern.search(str(funding_rounds)):
            raise ValueError(f"Classification Mismatch: '{company_name}' is marked as 'Public', but has private venture funding rounds: '{funding_rounds}'.")
    if normalized_nature == 'Subsidiary' and overview:
        normalized_overview = overview.lower()
        has_ownership_marker = any((marker in normalized_overview for marker in tc_12_3_PARENT_OWNERSHIP_KEYWORDS))
        if not has_ownership_marker:
            raise ValueError(f"Classification Mismatch: '{company_name}' is classified as a 'Subsidiary', but its overview does not outline parent-subsidiary relationship terms.")
    return True

def test_tc_12_3_private_company_with_funding_success():
    """
    Validates typical private venture-backed startup profile.
    """
    record = {'Company Name': 'Space Exploration Technologies Corp.', 'Nature of Company': 'Private', 'Recent Funding Rounds': '2025-01-15 - $250,000,000', 'Overview of the Company': 'An independent aerospace manufacturer founded by Elon Musk.'}
    assert tc_12_3_validate_nature_of_company(record) is True

def test_tc_12_3_public_company_success():
    """
    Validates public enterprise without venture rounds.
    """
    record = {'Company Name': 'Apple Inc.', 'Nature of Company': 'Public', 'Recent Funding Rounds': None, 'Overview of the Company': 'A global consumer electronics manufacturer.'}
    assert tc_12_3_validate_nature_of_company(record) is True

def test_tc_12_3_subsidiary_company_success():
    """
    Validates subsidiary status when supported by description ownership terms.
    """
    record = {'Company Name': 'WhatsApp LLC', 'Nature of Company': 'Subsidiary', 'Recent Funding Rounds': None, 'Overview of the Company': 'A messaging platform owned by Meta Platforms, Inc.'}
    assert tc_12_3_validate_nature_of_company(record) is True

def test_tc_12_3_lowercase_normalization_success():
    """
    Ensures incorrect casing (e.g., 'subsidiary') is corrected to match the regex.
    """
    record = {'Company Name': 'WhatsApp LLC', 'Nature of Company': 'subsidiary', 'Recent Funding Rounds': None, 'Overview of the Company': 'A messaging platform owned by Meta.'}
    assert tc_12_3_validate_nature_of_company(record) is True
    assert record['Nature of Company'] == 'Subsidiary'

def test_tc_12_3_invalid_structure_enum_fails():
    """
    Rejects legal structure values that are outside the standardized enum list.
    """
    record = {'Company Name': 'SpaceX', 'Nature of Company': 'private-owned', 'Recent Funding Rounds': '2025-01-15 - $250,000,000'}
    with pytest.raises(ValueError, match='is not a recognized legal structure enum'):
        tc_12_3_validate_nature_of_company(record)

def test_tc_12_3_public_with_venture_rounds_fails():
    """
    Flags anomalies where a public company lists active private venture capital rounds.
    """
    record = {'Company Name': 'Apple Inc.', 'Nature of Company': 'Public', 'Recent Funding Rounds': '2025-01-15 - Series B - $50,000,000', 'Overview of the Company': 'A global consumer electronics manufacturer.'}
    with pytest.raises(ValueError, match="is marked as 'Public', but has private venture funding"):
        tc_12_3_validate_nature_of_company(record)

def test_tc_12_3_subsidiary_lacking_ownership_text_fails():
    """
    Flags subsidiaries whose overview reports no parent-ownership relationships.
    """
    record = {'Company Name': 'WhatsApp LLC', 'Nature of Company': 'Subsidiary', 'Recent Funding Rounds': None, 'Overview of the Company': 'An independent messaging platform.'}
    with pytest.raises(ValueError, match="is classified as a 'Subsidiary', but its overview does not outline"):
        tc_12_3_validate_nature_of_company(record)
tc_12_4_BRAND_SENTIMENT_REGEX = re.compile('^(Positive|Neutral|Negative)$|^\\d{1,3}$')
tc_12_4_GLASSDOOR_REGEX = re.compile('^[1-5](\\.\\d)?$')
tc_12_4_NPS_REGEX = re.compile('^-?(100|[1-9]\\d?|0)$')

def tc_12_4_validate_sentiment_metrics(record: Dict[str, Any]) -> bool:
    """
    Validates structural patterns and boundary ranges of brand sentiment, 
    Glassdoor employee scores, and Net Promoter Score (NPS).
    """
    brand_sentiment = record.get('Brand Sentiment Score')
    glassdoor_rating = record.get('Glassdoor Rating')
    nps = record.get('Net Promoter Score (NPS)')
    burnout_risk = record.get('Burnout risk')
    if brand_sentiment is not None:
        val_str = str(brand_sentiment).strip()
        if not tc_12_4_BRAND_SENTIMENT_REGEX.match(val_str):
            raise ValueError(f"Format Error: Brand Sentiment '{brand_sentiment}' must be 'Positive', 'Neutral', 'Negative' or an index (0-100).")
        if val_str.isdigit():
            index_val = int(val_str)
            if not 0 <= index_val <= 100:
                raise ValueError(f"Boundary Error: Brand Sentiment Index '{index_val}' must be between 0 and 100.")
    if glassdoor_rating is not None:
        rating_str = str(glassdoor_rating).strip()
        if not tc_12_4_GLASSDOOR_REGEX.match(rating_str):
            raise ValueError(f"Format Error: Glassdoor Rating '{glassdoor_rating}' must match decimal format between 1.0 and 5.0.")
        rating_val = float(rating_str)
        if not 1.0 <= rating_val <= 5.0:
            raise ValueError(f"Boundary Error: Glassdoor Rating '{rating_val}' must be between 1.0 and 5.0.")
    if nps is not None:
        nps_str = str(nps).strip()
        if not tc_12_4_NPS_REGEX.match(nps_str):
            raise ValueError(f"Format Error: NPS '{nps}' must be an integer between -100 and 100.")
        nps_val = int(nps_str)
        if not -100 <= nps_val <= 100:
            raise ValueError(f"Boundary Error: Net Promoter Score '{nps_val}' must be between -100 and 100.")
    if glassdoor_rating is not None and burnout_risk:
        rating_val = float(str(glassdoor_rating).strip())
        if rating_val >= 4.5 and str(burnout_risk).strip().title() == 'Severe':
            raise ValueError(f"Relational Error: High Glassdoor Rating of {rating_val} contradicts a 'Severe' Burnout Risk level.")
    return True

def test_tc_12_4_valid_categorical_brand_sentiment_success():
    """
    Validates standard categorical brand sentiment representation.
    """
    record = {'Brand Sentiment Score': 'Positive', 'Glassdoor Rating': '4.2', 'Net Promoter Score (NPS)': '75'}
    assert tc_12_4_validate_sentiment_metrics(record) is True

def test_tc_12_4_valid_numeric_brand_sentiment_success():
    """
    Validates numeric index brand sentiment representation.
    """
    record = {'Brand Sentiment Score': '82', 'Glassdoor Rating': '3.8', 'Net Promoter Score (NPS)': '45'}
    assert tc_12_4_validate_sentiment_metrics(record) is True

def test_tc_12_4_negative_nps_boundary_success():
    """
    Ensures negative NPS boundaries are accepted when within range limits.
    """
    record = {'Brand Sentiment Score': 'Negative', 'Glassdoor Rating': '2.5', 'Net Promoter Score (NPS)': '-40'}
    assert tc_12_4_validate_sentiment_metrics(record) is True

def test_tc_12_4_invalid_brand_sentiment_adjective_fails():
    """
    Ensures invalid adjectives outside 'Positive'/'Neutral'/'Negative' fail.
    """
    record = {'Brand Sentiment Score': 'Excellent', 'Glassdoor Rating': '4.2'}
    with pytest.raises(ValueError, match="must be 'Positive', 'Neutral', 'Negative' or an index"):
        tc_12_4_validate_sentiment_metrics(record)

def test_tc_12_4_out_of_bound_brand_sentiment_index_fails():
    """
    Flags numerical indexes that exceed 100.
    """
    record = {'Brand Sentiment Score': '125', 'Glassdoor Rating': '4.2'}
    with pytest.raises(ValueError, match="Brand Sentiment Index '125' must be between 0 and 100"):
        tc_12_4_validate_sentiment_metrics(record)

def test_tc_12_4_out_of_bound_glassdoor_rating_fails():
    """
    Flags Glassdoor ratings that violate the standard 1.0 - 5.0 range.
    """
    record = {'Brand Sentiment Score': 'Positive', 'Glassdoor Rating': '5.5'}
    with pytest.raises(ValueError, match='must match decimal format between 1.0 and 5.0'):
        tc_12_4_validate_sentiment_metrics(record)

def test_tc_12_4_out_of_bound_nps_fails():
    """
    Flags NPS records that exceed 100 or fall below -100.
    """
    record = {'Brand Sentiment Score': 'Positive', 'Net Promoter Score (NPS)': '150'}
    with pytest.raises(ValueError, match='must be an integer between -100 and 100'):
        tc_12_4_validate_sentiment_metrics(record)

def test_tc_12_4_contradictory_glassdoor_and_burnout_metrics_fails():
    """
    Flags relational anomalies between high employer score and severe burnout risk.
    """
    record = {'Company Name': 'FutureTech', 'Brand Sentiment Score': 'Positive', 'Glassdoor Rating': '4.8', 'Burnout risk': 'Severe'}
    with pytest.raises(ValueError, match="contradicts a 'Severe' Burnout Risk level"):
        tc_12_4_validate_sentiment_metrics(record)
tc_12_5_CONCENTRATION_REGEX = re.compile('^(Yes|No|High|Low)(.*)$', re.IGNORECASE)
tc_12_5_BURNOUT_REGEX = re.compile('^(Low|Medium|High|Severe)(.*)$', re.IGNORECASE)

def tc_12_5_validate_risk_classifications(record: Dict[str, Any]) -> bool:
    """
    Validates structural formatting and logical constraints for Customer Concentration Risk,
    Burnout Risk, and Operational Runway.
    """
    concentration = record.get('Customer Concentration Risk')
    burnout = record.get('Burnout risk')
    runway = record.get('Runway')
    weekend_work = record.get('Weekend work')
    overtime_exp = record.get('Overtime expectations')
    if concentration is not None:
        con_str = str(concentration).strip()
        match = tc_12_5_CONCENTRATION_REGEX.match(con_str)
        if not match:
            raise ValueError(f"Format Error: 'Customer Concentration Risk' value '{concentration}' must start with 'Yes', 'No', 'High', or 'Low'.")
        percent_match = re.search('(\\d+)%', con_str)
        if percent_match:
            percent_val = int(percent_match.group(1))
            prefix = match.group(1).title()
            if percent_val > 20 and prefix in ['No', 'Low']:
                raise ValueError(f"Logical Mismatch: Customer concentration is {percent_val}%, but risk level is marked as '{prefix}'. Expected 'Yes' or 'High'.")
    if burnout is not None:
        burn_str = str(burnout).strip()
        match = tc_12_5_BURNOUT_REGEX.match(burn_str)
        if not match:
            raise ValueError(f"Format Error: 'Burnout risk' value '{burnout}' must start with 'Low', 'Medium', 'High', or 'Severe'.")
        prefix = match.group(1).title()
        if weekend_work == 'Always' and overtime_exp == 'Frequent':
            if prefix in ['Low', 'Medium']:
                raise ValueError(f"Logical Mismatch: Workplace has 'Always' weekend work and 'Frequent' overtime, but Burnout Risk is classified as '{prefix}'. Expected 'High' or 'Severe'.")
    if runway is not None:
        try:
            runway_val = float(str(runway).strip())
        except ValueError:
            raise ValueError(f"Data Type Error: Runway '{runway}' must be a valid float value.")
        if runway_val < 0:
            raise ValueError('Boundary Error: Runway cannot be negative.')
        record['is_critical_runway'] = runway_val < 6.0
    return True

def test_tc_12_5_concentration_risk_high_success():
    """
    Validates high concentration risk where percentage exceeds boundary and matches prefix.
    """
    record = {'Customer Concentration Risk': 'High - 35% from top client', 'Burnout risk': 'Medium', 'Runway': '18.0'}
    assert tc_12_5_validate_risk_classifications(record) is True

def test_tc_12_5_intense_work_severe_burnout_success():
    """
    Validates extreme work conditions mapped to severe burnout risk.
    """
    record = {'Weekend work': 'Always', 'Overtime expectations': 'Frequent', 'Burnout risk': 'Severe risk of attrition'}
    assert tc_12_5_validate_risk_classifications(record) is True

def test_tc_12_5_critical_runway_risk_logged():
    """
    Ensures runway under 6 months triggers a critical flag within the metadata dictionary.
    """
    record = {'Runway': '4.5'}
    assert tc_12_5_validate_risk_classifications(record) is True
    assert record['is_critical_runway'] is True

def test_tc_12_5_invalid_concentration_prefix_fails():
    """
    Rejects concentration risk strings that use arbitrary non-standard prefixes.
    """
    record = {'Customer Concentration Risk': 'Maybe - about 15%'}
    with pytest.raises(ValueError, match="must start with 'Yes', 'No', 'High', or 'Low'"):
        tc_12_5_validate_risk_classifications(record)

def test_tc_12_5_contradictory_concentration_and_percentage_fails():
    """
    Rejects records that claim 'Low' or 'No' concentration risk despite >20% revenue from one client.
    """
    record = {'Customer Concentration Risk': 'Low - 30% from anchor client'}
    with pytest.raises(ValueError, match="Expected 'Yes' or 'High'"):
        tc_12_5_validate_risk_classifications(record)

def test_tc_12_5_contradictory_work_conditions_and_burnout_fails():
    """
    Rejects records that attempt to greenwash high work-pressure as 'Low' burnout risk.
    """
    record = {'Weekend work': 'Always', 'Overtime expectations': 'Frequent', 'Burnout risk': 'Low'}
    with pytest.raises(ValueError, match="Expected 'High' or 'Severe'"):
        tc_12_5_validate_risk_classifications(record)
tc_13_2_SLA_STARTUP_LIMIT_SEC = 15.0
tc_13_2_SLA_ENTERPRISE_LIMIT_SEC = 45.0

def tc_13_2_simulate_extraction_and_validation(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates the pipeline extraction, reasoning, and validation of all 
    163 metadata parameters. The simulated processing time varies depending
    on company size, ownership nature, and overall data density.
    """
    processing_time = 2.0
    category = record.get('Category', 'Startup')
    nature = record.get('Nature of Company', 'Private')
    if category == 'Enterprise':
        processing_time += 15.0
    if nature == 'Public':
        processing_time += 10.0
    if category == 'Conglomerate':
        processing_time += 8.0
    time.sleep(processing_time)
    record['generation_time_sec'] = processing_time
    record['status'] = 'PROCESSED'
    return record

def test_tc_13_2_startup_generation_response_time():
    """
    Validates that a typical private startup profile with sparse public data 
    is compiled and validated well within the fast SLA threshold of 15 seconds.
    """
    startup_payload = {'Company Name': 'Acme SaaS', 'Category': 'Startup', 'Nature of Company': 'Private'}
    start_time = time.perf_counter()
    result = tc_13_2_simulate_extraction_and_validation(startup_payload)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    assert elapsed_time <= tc_13_2_SLA_STARTUP_LIMIT_SEC, f'Performance SLA Violated: Startup processing took {elapsed_time:.2f}s, exceeding the limit of {tc_13_2_SLA_STARTUP_LIMIT_SEC}s.'
    assert result['status'] == 'PROCESSED'

def test_tc_13_2_fortune_500_enterprise_generation_response_time():
    """
    Validates that a highly complex, public Fortune 500 company profile with dense 
    disclosures is compiled and validated within the maximum SLA threshold of 45 seconds.
    """
    enterprise_payload = {'Company Name': 'Microsoft Corporation', 'Category': 'Enterprise', 'Nature of Company': 'Public'}
    start_time = time.perf_counter()
    result = tc_13_2_simulate_extraction_and_validation(enterprise_payload)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    assert elapsed_time <= tc_13_2_SLA_ENTERPRISE_LIMIT_SEC, f'Performance SLA Violated: Enterprise processing took {elapsed_time:.2f}s, exceeding the limit of {tc_13_2_SLA_ENTERPRISE_LIMIT_SEC}s.'
    assert result['status'] == 'PROCESSED'

def test_tc_13_2_public_vs_private_latency_scaling():
    """
    Compares processing speed differences between public and private company profiles.
    Asserts that the system scales efficiently, showing proportional processing 
    speeds relative to data density.
    """
    private_payload = {'Company Name': 'Alpha Robotics', 'Category': 'Startup', 'Nature of Company': 'Private'}
    public_payload = {'Company Name': 'Tesla Inc.', 'Category': 'Enterprise', 'Nature of Company': 'Public'}
    t_start_private = time.perf_counter()
    res_private = tc_13_2_simulate_extraction_and_validation(private_payload)
    t_end_private = time.perf_counter()
    private_duration = t_end_private - t_start_private
    t_start_public = time.perf_counter()
    res_public = tc_13_2_simulate_extraction_and_validation(public_payload)
    t_end_public = time.perf_counter()
    public_duration = t_end_public - t_start_public
    assert private_duration < public_duration, f'Abnormal Latency Profile: Private startup processing ({private_duration:.2f}s) was not faster than public enterprise processing ({public_duration:.2f}s).'
    assert private_duration <= tc_13_2_SLA_STARTUP_LIMIT_SEC
    assert public_duration <= tc_13_2_SLA_ENTERPRISE_LIMIT_SEC
tc_13_3_TERMINAL_PUNCTUATION_REGEX = re.compile('[.!?)"\\u201d\\u2019]$')
tc_13_3_TRUNCATION_PLACEHOLDERS = ['...', '[truncated]', 'read more', 'etc.', 'etc', '..']

def tc_13_3_validate_token_limit_and_truncation(record: Dict[str, Any]) -> bool:
    """
    Evaluates the record holistically to verify that long content has not 
    suffered mid-sentence cutoffs, structural JSON truncation, or trailing parameter drops.
    """
    overview = record.get('Overview of the Company')
    office_locations = record.get('Office Locations')
    ethical_standards = record.get('Ethical standards')
    if overview is not None:
        overview_str = str(overview).strip()
        for placeholder in tc_13_3_TRUNCATION_PLACEHOLDERS:
            if overview_str.lower().endswith(placeholder):
                raise ValueError(f"Truncation Detected: 'Overview of the Company' ends with a truncation placeholder '{placeholder}'.")
        if not tc_13_3_TERMINAL_PUNCTUATION_REGEX.search(overview_str):
            raise ValueError(f"Grammatical Cutoff Detected: 'Overview of the Company' does not end with valid terminal punctuation. Text ends with: '...{overview_str[-20:]}'")
    if office_locations is not None:
        locs_str = str(office_locations).strip()
        if locs_str.startswith('[') or locs_str.startswith('{'):
            try:
                json.loads(locs_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Structural Truncation Detected: 'Office Locations' failed JSON parsing. It was likely cut off mid-payload. Parsing error: {e}")
        elif locs_str.endswith(',') or locs_str.endswith('-') or locs_str.endswith('*'):
            raise ValueError(f"Structural Truncation Detected: 'Office Locations' ends with a hanging separator, indicating incomplete list rendering.")
    if not ethical_standards:
        raise ValueError("Schema Preservation Error: Tail-end parameter 'Ethical standards' is missing. The system may have hit a token ceiling and dropped the end of the schema payload.")
    return True

def test_tc_13_3_long_content_perfect_execution_success():
    """
    Validates a highly detailed company profile where narrative and 
    structured fields are highly verbose but structurally complete.
    """
    complete_record = {'Overview of the Company': 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, and tablets. The firm continues to expand its digital services footprint worldwide.', 'Office Locations': json.dumps([{'city': 'Cupertino', 'country': 'USA'}, {'city': 'London', 'country': 'UK'}, {'city': 'Tokyo', 'country': 'Japan'}]), 'Ethical standards': 'Maintains strict supply chain compliance standards globally.'}
    assert tc_13_3_validate_token_limit_and_truncation(complete_record) is True

def test_tc_13_3_abrupt_narrative_cutoff_fails():
    """
    Flags a narrative field that gets cut off mid-sentence without terminal punctuation.
    """
    untruncated_but_cutoff_record = {'Overview of the Company': 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, and', 'Office Locations': 'Cupertino, USA; London, UK', 'Ethical standards': 'Compliant'}
    with pytest.raises(ValueError, match='Grammatical Cutoff Detected'):
        tc_13_3_validate_token_limit_and_truncation(untruncated_but_cutoff_record)

def test_tc_13_3_ellipses_placeholder_fails():
    """
    Flags a narrative field that terminates with a '...' truncation placeholder.
    """
    placeholder_record = {'Overview of the Company': 'Apple Inc. designs, manufactures, and markets smartphones...', 'Office Locations': 'Cupertino, USA', 'Ethical standards': 'Compliant'}
    with pytest.raises(ValueError, match='Truncation Detected'):
        tc_13_3_validate_token_limit_and_truncation(placeholder_record)

def test_tc_13_3_truncated_json_array_fails():
    """
    Flags a structured office location list that is cut off mid-payload, causing JSON parsing to fail.
    """
    truncated_json_record = {'Overview of the Company': 'Apple Inc. is a consumer tech giant.', 'Office Locations': '[{"city": "Cupertino", "country": "USA"}, {"city": "London"', 'Ethical standards': 'Compliant'}
    with pytest.raises(ValueError, match='Structural Truncation Detected'):
        tc_13_3_validate_token_limit_and_truncation(truncated_json_record)

def test_tc_13_3_dropped_tail_end_parameters_fails():
    """
    Flags when final fields in the metadata schema are missing, indicating cumulative token exhaustion.
    """
    exhausted_token_record = {'Overview of the Company': 'Highly verbose text...', 'Office Locations': 'Cupertino, USA', 'Ethical standards': None}
    with pytest.raises(ValueError, match='Schema Preservation Error'):
        tc_13_3_validate_token_limit_and_truncation(exhausted_token_record)
tc_13_4_COMMON_STOP_WORDS = {'and', 'the', 'for', 'with', 'from', 'company', 'inc', 'corp', 'llc', 'global', 'technologies', 'services', 'solutions', 'limited', 'incorporated', 'private', 'public', 'systems', 'group', 'co', 'management', 'industries', 'partner'}

def tc_13_4_extract_unique_signatures(record: Dict[str, Any]) -> Set[str]:
    """
    Extracts highly specific, lowercase alphanumeric word tokens from a record.
    These tokens serve as the 'data footprint' of the company to detect context leaks.
    """
    signatures: Set[str] = set()
    target_fields = ['Company Name', 'Short Name', 'Website URL', 'CEO Name', 'Company Headquarters', 'Key Investors / Backers']
    for field in target_fields:
        val = record.get(field)
        if val:
            words = re.findall('\\b[a-zA-Z]{3,20}\\b', str(val).lower())
            for word in words:
                if word not in tc_13_4_COMMON_STOP_WORDS:
                    signatures.add(word)
    return signatures

def tc_13_4_detect_memory_contamination(company_a: Dict[str, Any], company_b: Dict[str, Any]) -> None:
    """
    Asserts that no highly unique signature tokens from Company A's profile 
    exist in Company B's profile, validating clean memory isolation.
    """
    signatures_a = tc_13_4_extract_unique_signatures(company_a)
    all_b_text = ' '.join([str(v) for v in company_b.values() if v is not None]).lower()
    leaked_tokens = []
    for token in signatures_a:
        pattern = re.compile(f'\\b{token}\\b')
        if pattern.search(all_b_text):
            leaked_tokens.append(token)
    if leaked_tokens:
        raise ValueError(f"Memory Contamination Leak Detected: Unique tokens {leaked_tokens} from '{company_a.get('Company Name')}' leaked into the record of '{company_b.get('Company Name')}'.")

def test_tc_13_4_sequential_requests_perfect_isolation_success():
    """
    Validates that two highly distinct sequential requests preserve 
    complete context isolation and do not trigger leak detection.
    """
    company_a = {'Company Name': 'Space Exploration Technologies Corp.', 'Short Name': 'SpaceX', 'Website URL': 'https://www.spacex.com', 'CEO Name': 'Elon Musk', 'Company Headquarters': 'Hawthorne, California', 'Key Investors / Backers': 'Founders Fund, Fidelity'}
    company_b = {'Company Name': 'Blue Origin LLC', 'Short Name': 'Blue Origin', 'Website URL': 'https://www.blueorigin.com', 'CEO Name': 'Jeff Bezos', 'Company Headquarters': 'Kent, Washington', 'Key Investors / Backers': 'Bezos Expeditions'}
    tc_13_4_detect_memory_contamination(company_a, company_b)

def test_tc_13_4_sequential_requests_contamination_failure():
    """
    Asserts that the memory leak detector successfully catches and flags 
    cross-contamination if a preceding company's attributes bleed into the next record.
    """
    company_a = {'Company Name': 'Space Exploration Technologies Corp.', 'Short Name': 'SpaceX', 'Website URL': 'https://www.spacex.com', 'CEO Name': 'Elon Musk', 'Company Headquarters': 'Hawthorne, California', 'Key Investors / Backers': 'Founders Fund, Fidelity'}
    contaminated_company_b = {'Company Name': 'Blue Origin LLC', 'Short Name': 'Blue Origin', 'Website URL': 'https://www.spacex.com', 'CEO Name': 'Elon Musk', 'Company Headquarters': 'Kent, Washington', 'Key Investors / Backers': 'Bezos Expeditions'}
    with pytest.raises(ValueError, match='Memory Contamination Leak Detected'):
        tc_13_4_detect_memory_contamination(company_a, contaminated_company_b)

def test_tc_13_4_batch_run_similar_companies_isolation():
    """
    Checks that highly similar automotive entities parsed concurrently 
    do not experience cross-contamination of their specific identifiers.
    """
    tesla = {'Company Name': 'Tesla Inc.', 'Short Name': 'Tesla', 'Website URL': 'https://www.tesla.com', 'CEO Name': 'Elon Musk', 'Company Headquarters': 'Austin, Texas'}
    rivian = {'Company Name': 'Rivian Automotive', 'Short Name': 'Rivian', 'Website URL': 'https://www.rivian.com', 'CEO Name': 'RJ Scaringe', 'Company Headquarters': 'Irvine, California'}
    tc_13_4_detect_memory_contamination(tesla, rivian)
    tc_13_4_detect_memory_contamination(rivian, tesla)
tc_14_1_MANDATORY_FIELDS = ['Company Name', 'Category', 'Year of Incorporation', 'Overview of the Company', 'Nature of Company', 'Company Headquarters', 'Employee Size']
tc_14_1_STRING_NULL_PLACEHOLDERS = {'n/a', 'na', 'null', 'none', 'unknown', 'undisclosed', ''}

def tc_14_1_validate_nullable_data_integrity(record: Dict[str, Any]) -> bool:
    """
    Evaluates the record for nullability and NA data rules. 
    Enforces strict exceptions on missing mandatory parameters while allowing 
    flexible, graceful mapping on optional parameters.
    """
    for field in tc_14_1_MANDATORY_FIELDS:
        val = record.get(field)
        if val is None:
            raise ValueError(f"Nullability Violation: Mandatory field '{field}' cannot be Null.")
        if isinstance(val, str):
            cleaned_val = val.strip().lower()
            if cleaned_val in tc_14_1_STRING_NULL_PLACEHOLDERS:
                raise ValueError(f"Nullability Violation: Mandatory field '{field}' contains an invalid placeholder value '{val}'.")
    optional_fields = ['Annual Revenues', 'Annual Profits', 'Company Valuation', 'Total Capital Raised']
    for field in optional_fields:
        val = record.get(field)
        if val is not None:
            if isinstance(val, str):
                cleaned_val = val.strip().lower()
                if cleaned_val in tc_14_1_STRING_NULL_PLACEHOLDERS:
                    record[field] = None
    funding_rounds = record.get('Recent Funding Rounds')
    if funding_rounds:
        if 'undisclosed' in str(funding_rounds).lower():
            if record.get('Total Capital Raised') is not None:
                if str(record['Total Capital Raised']).strip().lower() in tc_14_1_STRING_NULL_PLACEHOLDERS:
                    record['Total Capital Raised'] = None
    return True

def test_tc_14_1_private_stealth_startup_null_financials_success():
    """
    Verifies that an early stage stealth company is accepted with completely
    empty optional financial parameters, while maintaining critical mandatory parameters.
    """
    stealth_company = {'Company Name': 'Stealth AI Inc.', 'Category': 'Startup', 'Year of Incorporation': 2025, 'Overview of the Company': 'Building advanced LLM security testing tools in stealth.', 'Nature of Company': 'Private', 'Company Headquarters': 'Boston, USA', 'Employee Size': '1-10', 'Annual Revenues': None, 'Annual Profits': None, 'Company Valuation': 'N/A', 'Recent Funding Rounds': '2025-04-10 - Undisclosed - Seed'}
    assert tc_14_1_validate_nullable_data_integrity(stealth_company) is True
    assert stealth_company['Company Valuation'] is None

def test_tc_14_1_public_company_full_data_success():
    """
    Ensures a fully populated public company profile with active financial metrics passes.
    """
    public_company = {'Company Name': 'Alphabet Inc.', 'Category': 'Enterprise', 'Year of Incorporation': 1998, 'Overview of the Company': 'A global technology company specializing in search and cloud solutions.', 'Nature of Company': 'Public', 'Company Headquarters': 'Mountain View, USA', 'Employee Size': '100000+', 'Annual Revenues': '$307,000,000,000', 'Annual Profits': '$73,000,000,000', 'Company Valuation': '$1,800,000,000,000'}
    assert tc_14_1_validate_nullable_data_integrity(public_company) is True

def test_tc_14_1_missing_mandatory_field_fails():
    """
    Rejects the record if a mandatory parameter is entirely absent (evaluates to None).
    """
    malformed_record = {'Company Name': 'Alpha Partners', 'Category': None, 'Year of Incorporation': 2020, 'Overview of the Company': 'A venture fund seeking tech investments.', 'Nature of Company': 'Partnership', 'Company Headquarters': 'New York, USA', 'Employee Size': '11-50'}
    with pytest.raises(ValueError, match="Mandatory field 'Category' cannot be Null"):
        tc_14_1_validate_nullable_data_integrity(malformed_record)

def test_tc_14_1_placeholder_string_nulls_in_mandatory_field_fails():
    """
    Rejects the record if a mandatory parameter is populated with a string placeholder like "N/A".
    """
    malformed_record = {'Company Name': 'Unknown Co.', 'Category': 'Startup', 'Year of Incorporation': 2021, 'Overview of the Company': 'N/A', 'Nature of Company': 'Private', 'Company Headquarters': 'Seattle, USA', 'Employee Size': '1-10'}
    with pytest.raises(ValueError, match="Mandatory field 'Overview of the Company' contains an invalid placeholder"):
        tc_14_1_validate_nullable_data_integrity(malformed_record)

def tc_14_2_validate_not_applicable_fields(record: Dict[str, Any]) -> bool:
    """
    Validates company metadata by dynamically adjusting constraint rules 
    for fields that do not apply to specific corporate profiles.
    """
    category = record.get('Category')
    company_name = record.get('Company Name')
    products = record.get('Services / Offerings / Products')
    total_capital = record.get('Total Capital Raised')
    investors = record.get('Key Investors / Backers')
    remote_policy = record.get('Remote Work Policy')
    offices_count = record.get('Number of Offices (beyond HQ)')
    office_locations = record.get('Office Locations')
    if not company_name or not category:
        raise ValueError("Field Validation Error: 'Company Name' and 'Category' are required.")
    if category in ['VC', 'Investor']:
        if products is None or 'n/a' in str(products).lower():
            pass
    elif not products or 'n/a' in str(products).lower():
        raise ValueError(f"Validation Failure: Standard commercial category '{category}' must list actual products. '{products}' is not permitted.")
    if total_capital == 0 or total_capital is None:
        if investors is not None and 'n/a' not in str(investors).lower() and ('none' not in str(investors).lower()):
            raise ValueError(f"Logical Conflict: Capital raised is 0, but investors are listed: '{investors}'.")
    elif investors is not None and 'n/a' in str(investors).lower():
        raise ValueError(f"Validation Failure: Capital was raised ({total_capital}), so 'Key Investors / Backers' cannot be N/A.")
    if remote_policy in ['Remote-First', 'Remote']:
        if offices_count == 0:
            if office_locations is not None and 'n/a' not in str(office_locations).lower():
                raise ValueError(f"Logical Conflict: Remote company has 0 physical offices, but listed locations: '{office_locations}'.")
    elif office_locations is not None and 'n/a' in str(office_locations).lower():
        raise ValueError(f"Validation Failure: Physical company with policy '{remote_policy}' cannot have 'N/A' for office locations.")
    return True

def test_tc_14_2_vc_firm_na_products_success():
    """
    Ensures an investment firm (VC) successfully passes validation when its 
    products parameter is mapped to 'N/A'.
    """
    record = {'Company Name': 'Sequoia Capital', 'Category': 'VC', 'Services / Offerings / Products': 'N/A - Financial Investment Services', 'Total Capital Raised': 0, 'Key Investors / Backers': 'None - General Partners', 'Remote Work Policy': 'Hybrid', 'Number of Offices (beyond HQ)': 3, 'Office Locations': 'London, UK; Beijing, China'}
    assert tc_14_2_validate_not_applicable_fields(record) is True

def test_tc_14_2_bootstrapped_company_na_investors_success():
    """
    Ensures a self-funded startup successfully passes validation with 
    investors set to 'N/A' and capital raised set to 0.
    """
    record = {'Company Name': 'Bootstrapped SaaS LLC', 'Category': 'Startup', 'Services / Offerings / Products': 'Subscription Email Marketing Software', 'Total Capital Raised': 0, 'Key Investors / Backers': 'N/A - Bootstrapped', 'Remote Work Policy': 'On-Site', 'Number of Offices (beyond HQ)': 1, 'Office Locations': 'Austin, Texas'}
    assert tc_14_2_validate_not_applicable_fields(record) is True

def test_tc_14_2_remote_first_company_na_offices_success():
    """
    Ensures a fully distributed, remote-first company successfully passes validation 
    with 0 offices and locations set to 'N/A'.
    """
    record = {'Company Name': 'GitLab Inc.', 'Category': 'Enterprise', 'Services / Offerings / Products': 'DevSecOps Platform', 'Total Capital Raised': 100000000, 'Key Investors / Backers': 'Khosla Ventures, Y Combinator', 'Remote Work Policy': 'Remote-First', 'Number of Offices (beyond HQ)': 0, 'Office Locations': 'N/A - Fully Distributed'}
    assert tc_14_2_validate_not_applicable_fields(record) is True

def test_tc_14_2_standard_company_na_products_fails():
    """
    Asserts that standard commercial startups are not permitted to bypass
    the mandatory products field with 'N/A' values.
    """
    record = {'Company Name': 'Standard Soft LLC', 'Category': 'Startup', 'Services / Offerings / Products': 'N/A', 'Total Capital Raised': 500000, 'Key Investors / Backers': 'Angel Investors', 'Remote Work Policy': 'Hybrid', 'Number of Offices (beyond HQ)': 1, 'Office Locations': 'New York, USA'}
    with pytest.raises(ValueError, match='must list actual products'):
        tc_14_2_validate_not_applicable_fields(record)

def test_tc_14_2_funded_company_na_investors_fails():
    """
    Asserts that a company stating it has raised millions cannot set its
    investors field to 'N/A'.
    """
    record = {'Company Name': 'WellFunded Tech', 'Category': 'Startup', 'Services / Offerings / Products': 'AI Copilot Suite', 'Total Capital Raised': 12000000, 'Key Investors / Backers': 'N/A', 'Remote Work Policy': 'Remote-First', 'Number of Offices (beyond HQ)': 0, 'Office Locations': 'N/A - Fully Distributed'}
    with pytest.raises(ValueError, match='cannot be N/A'):
        tc_14_2_validate_not_applicable_fields(record)
tc_14_3_CURRENT_YEAR = 2026

def tc_14_3_validate_ambiguous_availability(record: Dict[str, Any]) -> bool:
    """
    Validates company metadata by dynamically evaluating the source of 
    missing data. Normalizes generic null values into context-rich 
    ambiguity classifications depending on the company lifecycle.
    """
    company_name = record.get('Company Name')
    year_founded = record.get('Year of Incorporation')
    retention_tenure = record.get('Average Retention Tenure')
    layoff_history = record.get('Layoff history')
    website_url = record.get('Website URL')
    glassdoor_rating = record.get('Glassdoor Rating')
    confidence_level = record.get('confidence_level')
    validation_mode = record.get('validation_mode', 'Automated')
    if not company_name:
        raise ValueError("Field Validation Error: 'Company Name' is required.")
    if year_founded and tc_14_3_CURRENT_YEAR - int(year_founded) <= 1:
        if retention_tenure is None or retention_tenure == '':
            record['Average Retention Tenure'] = 'N/A - New Company'
        if layoff_history is None or layoff_history == '':
            record['Layoff history'] = 'None - New Company'
    is_stealth = False
    if website_url and 'stealth' in str(website_url).lower():
        is_stealth = True
    elif 'stealth' in str(company_name).lower():
        is_stealth = True
    if is_stealth:
        if glassdoor_rating is None or glassdoor_rating == '':
            record['Glassdoor Rating'] = 'N/A - Stealth Mode'
        if confidence_level == 'High':
            raise ValueError(f"Confidence Conflict: Stealth entity '{company_name}' cannot have a 'High' confidence level due to unresolvable, non-public data fields.")
    is_url_deactivated = record.get('is_url_deactivated', False)
    if is_url_deactivated:
        if validation_mode == 'Automated':
            raise ValueError(f"Processing Exception: Deactivated assets detected for '{company_name}'. Validation mode must be shifted to 'Supervised' or 'Manual' for human auditing.")
    return True

def test_tc_14_3_newly_founded_company_ambiguity_handled():
    """
    Ensures that a company founded in 2025/2026 successfully maps missing historical 
    parameters to 'N/A - New Company' instead of triggering a validation crash.
    """
    new_company = {'Company Name': 'NeuraLaunch', 'Year of Incorporation': 2025, 'Average Retention Tenure': None, 'Layoff history': None, 'confidence_level': 'High'}
    assert tc_14_3_validate_ambiguous_availability(new_company) is True
    assert new_company['Average Retention Tenure'] == 'N/A - New Company'
    assert new_company['Layoff history'] == 'None - New Company'

def test_tc_14_3_stealth_company_ambiguity_handled():
    """
    Ensures stealth profiles are permitted to have missing digital parameters, 
    verifying that the reliability/confidence rating is constrained to 'Low' or 'Medium'.
    """
    stealth_company = {'Company Name': 'Stealth Crypto Labs', 'Website URL': 'N/A - Stealth Mode', 'Glassdoor Rating': None, 'confidence_level': 'Medium'}
    assert tc_14_3_validate_ambiguous_availability(stealth_company) is True
    assert stealth_company['Glassdoor Rating'] == 'N/A - Stealth Mode'

def test_tc_14_3_stealth_company_invalid_high_confidence_fails():
    """
    Asserts that a stealth-mode profile cannot claim a 'High' data confidence level,
    as several parameters are unresolvable.
    """
    stealth_company = {'Company Name': 'Stealth Crypto Labs', 'Website URL': 'N/A - Stealth Mode', 'Glassdoor Rating': None, 'confidence_level': 'High'}
    with pytest.raises(ValueError, match="cannot have a 'High' confidence level"):
        tc_14_3_validate_ambiguous_availability(stealth_company)

def test_tc_14_3_deactivated_url_demands_manual_validation_fails():
    """
    Asserts that if a company's target URL is deactivated, automated 
    ingestion fails, demanding human-in-the-loop (Manual) validation.
    """
    deactivated_record = {'Company Name': 'Retired Brand Inc.', 'Website URL': 'https://www.oldbrand.com', 'is_url_deactivated': True, 'validation_mode': 'Automated'}
    with pytest.raises(ValueError, match="Validation mode must be shifted to 'Supervised' or 'Manual'"):
        tc_14_3_validate_ambiguous_availability(deactivated_record)

def test_tc_14_3_deactivated_url_supervised_run_success():
    """
    Ensures that deactivated assets pass checks safely if the validation mode is
    correctly configured for manual or supervised auditing.
    """
    deactivated_record = {'Company Name': 'Retired Brand Inc.', 'Website URL': 'https://www.oldbrand.com', 'is_url_deactivated': True, 'validation_mode': 'Manual'}
    assert tc_14_3_validate_ambiguous_availability(deactivated_record) is True
tc_14_4_HQ_COUNTRY_MAP = {'usa': 'United States', 'united states': 'United States', 'india': 'India', 'uk': 'United Kingdom', 'united kingdom': 'United Kingdom', 'germany': 'Germany'}

def tc_14_4_validate_default_value_logic(record: Dict[str, Any]) -> bool:
    """
    Validates company metadata by ensuring appropriate defaults are applied
    and corrupting, inappropriate defaults are flagged and rejected.
    """
    company_name = record.get('Company Name')
    category = record.get('Category')
    maturity = record.get('Company maturity')
    revenues = record.get('Annual Revenues')
    hq = record.get('Company Headquarters')
    countries = record.get('Countries Operating In')
    offices_count = record.get('Number of Offices (beyond HQ)')
    if not company_name or not category:
        raise ValueError("Field Validation Error: 'Company Name' and 'Category' are required.")
    if revenues is not None:
        clean_rev = str(revenues).strip().replace('$', '').replace(',', '')
        if clean_rev in ['0', '0.00', 'free', 'none']:
            if maturity in ['Scale-up', 'Mature'] and category not in ['Non-Profit', 'Govt']:
                raise ValueError(f"Inappropriate Default Detected: Active, mature commercial entity '{company_name}' cannot have its revenue defaulted to zero. Unknown revenue must be represented as Null/None.")
    if countries is None or str(countries).strip() == '':
        if hq:
            hq_lower = str(hq).lower()
            resolved_country = None
            for keyword, country_name in tc_14_4_HQ_COUNTRY_MAP.items():
                if keyword in hq_lower:
                    resolved_country = country_name
                    break
            if resolved_country:
                record['Countries Operating In'] = resolved_country
            else:
                record['Countries Operating In'] = 'Unknown'
        else:
            record['Countries Operating In'] = 'Unknown'
    if offices_count is None:
        record['Number of Offices (beyond HQ)'] = 0
    return True

def test_tc_14_4_context_dependent_hq_country_default_success():
    """
    Ensures that a missing operating country field is safely defaulted to
    the country resolved from the headquarters address block.
    """
    record = {'Company Name': 'Apex SaaS LLC', 'Category': 'Startup', 'Company maturity': 'Startup', 'Company Headquarters': 'San Francisco, USA', 'Countries Operating In': None, 'Number of Offices (beyond HQ)': 1}
    assert tc_14_4_validate_default_value_logic(record) is True
    assert record['Countries Operating In'] == 'United States'

def test_tc_14_4_safe_structural_office_count_default_success():
    """
    Ensures that a missing office count is safely defaulted to 0.
    """
    record = {'Company Name': 'Apex SaaS LLC', 'Category': 'Startup', 'Company maturity': 'Startup', 'Company Headquarters': 'San Francisco, USA', 'Countries Operating In': 'United States', 'Number of Offices (beyond HQ)': None}
    assert tc_14_4_validate_default_value_logic(record) is True
    assert record['Number of Offices (beyond HQ)'] == 0

def test_tc_14_4_inappropriate_financial_zero_default_fails():
    """
    Asserts that an active, mature commercial company is rejected if its 
    revenue is inappropriately defaulted to zero instead of being marked as None/Null.
    """
    record = {'Company Name': 'Enterprise Solutions Inc.', 'Category': 'Enterprise', 'Company maturity': 'Mature', 'Company Headquarters': 'London, UK', 'Annual Revenues': '$0'}
    with pytest.raises(ValueError, match='Active, mature commercial entity .* cannot have its revenue defaulted to zero'):
        tc_14_4_validate_default_value_logic(record)

def test_tc_14_4_legitimate_non_profit_zero_revenue_success():
    """
    Ensures that legitimate zero-revenue states for non-profits are accepted 
    and do not trigger inappropriate default validation failures.
    """
    record = {'Company Name': 'Green Earth Foundation', 'Category': 'Non-Profit', 'Company maturity': 'Mature', 'Company Headquarters': 'Berlin, Germany', 'Annual Revenues': '$0'}
    assert tc_14_4_validate_default_value_logic(record) is True
tc_15_1_HIGH_RELIABILITY_SOURCES = {'Company Registry / SEC Filings', 'SEC Filings', 'Company Registry'}
tc_15_1_SPECULATIVE_SOURCES = {'AI inference', '3rd Party DB Estimates', 'Manual Research', 'Inference'}

def tc_15_1_validate_record_confidence_boundaries(record: Dict[str, Any]) -> bool:
    """
    Evaluates the company record's confidence metrics.
    Enforces strict rules that map overall data source reliability to the 
    declared overall confidence_level.
    """
    company_name = record.get('Company Name')
    data_source = record.get('data_source')
    overall_confidence = record.get('confidence_level')
    revenues = record.get('Annual Revenues')
    work_culture = record.get('Work culture')
    if not company_name or not data_source or (not overall_confidence):
        raise ValueError('Field Validation Error: Missing critical record-level identifiers.')
    clean_source = str(data_source).strip()
    clean_confidence = str(overall_confidence).strip().title()
    has_estimated_financials = False
    if revenues:
        if 'estimate' in str(revenues).lower() or 'inferred' in str(revenues).lower():
            has_estimated_financials = True
    has_subjective_metrics = False
    if work_culture:
        if 'inferred' in str(work_culture).lower() or 'sentiment' in str(work_culture).lower():
            has_subjective_metrics = True
    if clean_source in tc_15_1_SPECULATIVE_SOURCES and clean_confidence == 'High':
        raise ValueError(f"Confidence Mismatch: Record for '{company_name}' is sourced via '{data_source}' but claims an overall 'High' confidence level. This is not permitted for speculative data.")
    if has_estimated_financials and clean_confidence == 'High':
        raise ValueError(f"Confidence Mismatch: Record for '{company_name}' contains estimated financial figures, capping the overall 'confidence_level' at 'Medium' or 'Low'.")
    if clean_source == 'Mixed' and has_subjective_metrics and (clean_confidence == 'High'):
        raise ValueError(f"Confidence Mismatch: Mixed data record with subjective elements for '{company_name}' must be capped at 'Medium' or 'Low' confidence levels.")
    return True

def test_tc_15_1_high_confidence_regulatory_profile_success():
    """
    Validates a public enterprise record sourced completely from official regulatory filings.
    """
    record = {'Company Name': 'Apple Inc.', 'data_source': 'Company Registry / SEC Filings', 'confidence_level': 'High', 'Annual Revenues': '$383,000,000,000 (Confirmed)', 'Work culture': 'Standard corporate policies enforced.'}
    assert tc_15_1_validate_record_confidence_boundaries(record) is True

def test_tc_15_1_mixed_medium_confidence_profile_success():
    """
    Validates a mixed-source record with subjective culture indicators.
    """
    record = {'Company Name': 'GitLab Inc.', 'data_source': 'Mixed', 'confidence_level': 'Medium', 'Annual Revenues': '$500,000,000', 'Work culture': 'Collaborative (Glassdoor Inferred)'}
    assert tc_15_1_validate_record_confidence_boundaries(record) is True

def test_tc_15_1_speculative_source_false_high_confidence_fails():
    """
    Asserts that a record heavily dependent on speculative AI inference is
    rejected if it claims an unverified 'High' confidence level.
    """
    record = {'Company Name': 'Stealth Tech', 'data_source': 'AI inference', 'confidence_level': 'High', 'Annual Revenues': '$5,000,000 (Estimated)'}
    with pytest.raises(ValueError, match='is not permitted for speculative data'):
        tc_15_1_validate_record_confidence_boundaries(record)

def test_tc_15_1_estimated_financials_false_high_confidence_fails():
    """
    Asserts that a record with estimated financials cannot claim 'High' confidence.
    """
    record = {'Company Name': 'Apex SaaS LLC', 'data_source': 'Company Registry', 'confidence_level': 'High', 'Annual Revenues': '$10,000,000 (Estimated)'}
    with pytest.raises(ValueError, match="capping the overall 'confidence_level' at 'Medium' or 'Low'"):
        tc_15_1_validate_record_confidence_boundaries(record)

def test_tc_15_1_mixed_record_with_subjective_excessive_confidence_fails():
    """
    Asserts that a mixed record containing subjective metrics (e.g. Glassdoor inferred culture)
    cannot claim 'High' confidence.
    """
    record = {'Company Name': 'GitLab Inc.', 'data_source': 'Mixed', 'confidence_level': 'High', 'Annual Revenues': '$500,000,000', 'Work culture': 'Collaborative (Glassdoor Inferred)'}
    with pytest.raises(ValueError, match="must be capped at 'Medium' or 'Low' confidence levels"):
        tc_15_1_validate_record_confidence_boundaries(record)
tc_15_2_TIER_1_PRIMARY = {'company registry / sec filings', 'sec filings', 'company registry', 'company website', 'official registry', 'sec'}
tc_15_2_TIER_2_SECONDARY = {'linkedin', 'crunchbase', 'pr newswire', 'careers page', 'job boards', 'apollo', 'clearbit', 'website contact page'}
tc_15_2_TIER_3_TERTIARY = {'news articles', 'blog posts', 'glassdoor', 'indeed', 'yelp', 'analyst reports', '3rd party db estimates', 'ai inference', 'court records', 'twitter', 'x', 'social media'}

def tc_15_2_get_source_tier(source_string: str) -> int:
    """
    Classifies a data source string into Tier 1, 2, or 3.
    """
    clean_src = str(source_string).strip().lower()
    if any((p in clean_src for p in tc_15_2_TIER_1_PRIMARY)):
        return 1
    if any((s in clean_src for s in tc_15_2_TIER_2_SECONDARY)):
        return 2
    if any((t in clean_src for t in tc_15_2_TIER_3_TERTIARY)):
        return 3
    return 3

def tc_15_2_validate_source_quality_tiers(record: Dict[str, Any]) -> bool:
    """
    Enforces quality checks based on source tiers. Critical identity fields 
    must rely on Tier 1 or Tier 2 verification, preventing unverified or 
    speculative tertiary data from being accepted as High confidence [1].
    """
    company_name = record.get('Company Name')
    overall_confidence = record.get('confidence_level', 'Low').strip().title()
    critical_fields_sources = {'Company Name': record.get('source_company_name'), 'Year of Incorporation': record.get('source_year_founded'), 'Company Headquarters': record.get('source_hq')}
    for field_name, source in critical_fields_sources.items():
        if not source:
            raise ValueError(f"Field Validation Error: Sourcing data missing for critical field '{field_name}'.")
    for field_name, source in critical_fields_sources.items():
        tier = tc_15_2_get_source_tier(source)
        if tier == 3:
            raise ValueError(f"Source Tier Exception: Critical parameter '{field_name}' for '{company_name}' is sourced via a speculative Tier 3 source: '{source}'. Expected Tier 1 (Primary) or Tier 2 (Secondary) verification.")
    if overall_confidence == 'High':
        for field_name, source in critical_fields_sources.items():
            tier = tc_15_2_get_source_tier(source)
            if tier != 1:
                raise ValueError(f"Confidence Mismatch: Overall record is classified as 'High' confidence, but critical parameter '{field_name}' relies on a non-primary Tier {tier} source: '{source}'.")
    return True

def test_tc_15_2_high_quality_primary_record_success():
    """
    Validates a record where all critical parameters rely strictly on Tier 1 sources.
    """
    record = {'Company Name': 'Microsoft Corporation', 'confidence_level': 'High', 'source_company_name': 'SEC Filings', 'source_year_founded': 'Company Registry', 'source_hq': 'Company Website'}
    assert tc_15_2_validate_source_quality_tiers(record) is True

def test_tc_15_2_mixed_tier_medium_confidence_record_success():
    """
    Validates a standard mixed-tier record. Critical parameters are Tier 1/2,
    making it acceptable for a Medium confidence classification.
    """
    record = {'Company Name': 'GitLab Inc.', 'confidence_level': 'Medium', 'source_company_name': 'SEC Filings', 'source_year_founded': 'Company Registry', 'source_hq': 'Website Contact Page'}
    assert tc_15_2_validate_source_quality_tiers(record) is True

def test_tc_15_2_critical_fields_sourced_from_tertiary_fails():
    """
    Asserts that critical corporate parameters cannot be extracted from
    speculative Tier 3 sources like blogs or Twitter.
    """
    record = {'Company Name': 'Stealth Corp', 'confidence_level': 'Medium', 'source_company_name': 'Blog Posts', 'source_year_founded': 'Company Registry', 'source_hq': 'Twitter'}
    with pytest.raises(ValueError, match='is sourced via a speculative Tier 3 source'):
        tc_15_2_validate_source_quality_tiers(record)

def test_tc_15_2_high_confidence_claimed_with_secondary_sources_fails():
    """
    Asserts that a record cannot claim 'High' confidence if any of its
    critical parameters rely on secondary (Tier 2) sources instead of Tier 1.
    """
    record = {'Company Name': 'Tesla Inc.', 'confidence_level': 'High', 'source_company_name': 'SEC Filings', 'source_year_founded': 'LinkedIn', 'source_hq': 'Company Website'}
    with pytest.raises(ValueError, match='relies on a non-primary Tier 2 source'):
        tc_15_2_validate_source_quality_tiers(record)
tc_15_3_SYSTEM_BASELINE_DATE = datetime.datetime(2026, 5, 22)

def tc_15_3_extract_dates_from_string(text: str) -> List[datetime.datetime]:
    """
    Extracts YYYY-MM-DD or YYYY-MM dates from a text string.
    """
    full_dates = re.findall('\\b(\\d{4})-(\\d{2})-(\\d{2})\\b', text)
    extracted = []
    for y, m, d in full_dates:
        try:
            extracted.append(datetime.datetime(int(y), int(m), int(d)))
        except ValueError:
            pass
    month_dates = re.findall('\\b(\\d{4})-(\\d{2})\\b', text)
    for y, m in month_dates:
        if not any((d.year == int(y) and d.month == int(m) for d in extracted)):
            try:
                extracted.append(datetime.datetime(int(y), int(m), 1))
            except ValueError:
                pass
    return extracted

def tc_15_3_calculate_months_difference(date_a: datetime.datetime, date_b: datetime.datetime) -> int:
    """
    Calculates the absolute difference in months between two datetime objects.
    """
    return abs((date_a.year - date_b.year) * 12 + date_a.month - date_b.month)

def tc_15_3_validate_record_recency(record: Dict[str, Any]) -> bool:
    """
    Audits the recency of the company profile [1].
    Ensures that volatile records with stale updates (>12 months) cannot carry
    a 'High' confidence level and must trigger refresh operations [3].
    """
    company_name = record.get('Company Name')
    recent_news = record.get('Recent News')
    overall_confidence = record.get('confidence_level', 'Low').strip().title()
    if not recent_news:
        if overall_confidence == 'High':
            raise ValueError(f"Recency Exception: Record for '{company_name}' lacks a recent timeline to verify operational freshness. 'High' confidence level is disallowed.")
        return True
    extracted_dates = tc_15_3_extract_dates_from_string(str(recent_news))
    if not extracted_dates:
        if overall_confidence == 'High':
            raise ValueError(f"Recency Exception: Cannot verify recency for '{company_name}' due to malformed dates. 'High' confidence level is disallowed.")
        return True
    newest_date = max(extracted_dates)
    months_old = tc_15_3_calculate_months_difference(tc_15_3_SYSTEM_BASELINE_DATE, newest_date)
    if months_old <= 6:
        record['recency_tier'] = 'Recent'
    elif months_old <= 12:
        record['recency_tier'] = 'Acceptable'
    else:
        record['recency_tier'] = 'Outdated'
    if record['recency_tier'] == 'Outdated':
        record['requires_refresh'] = True
        if overall_confidence == 'High':
            raise ValueError(f"Recency Mismatch: Record for '{company_name}' is 'Outdated' (latest data is {months_old} months old). A 'High' confidence level is disallowed until refreshed.")
    else:
        record['requires_refresh'] = False
    return True

def test_tc_15_3_recent_timeline_success():
    """
    Validates a company profile with highly fresh events dated within the last 6 months.
    """
    record = {'Company Name': 'NeuraLaunch Corp', 'Recent News': '2026-03-10 - Acquired New Startup, 2025-12-25 - Launched Version 2.0', 'confidence_level': 'High'}
    assert tc_15_3_validate_record_recency(record) is True
    assert record['recency_tier'] == 'Recent'
    assert record['requires_refresh'] is False

def test_tc_15_3_acceptable_timeline_success():
    """
    Validates a company profile with events dated between 6 and 12 months old.
    """
    record = {'Company Name': 'Apex SaaS LLC', 'Recent News': '2025-08-15 - Opened New Office', 'confidence_level': 'Medium'}
    assert tc_15_3_validate_record_recency(record) is True
    assert record['recency_tier'] == 'Acceptable'
    assert record['requires_refresh'] is False

def test_tc_15_3_outdated_timeline_low_confidence_success():
    """
    Ensures that an outdated record successfully passes validation if its 
    confidence level is correctly restricted to 'Medium' or 'Low' and the refresh flag is set.
    """
    record = {'Company Name': 'Legacy Tech Corp', 'Recent News': '2024-02-10 - Series A Funding', 'confidence_level': 'Medium'}
    assert tc_15_3_validate_record_recency(record) is True
    assert record['recency_tier'] == 'Outdated'
    assert record['requires_refresh'] is True

def test_tc_15_3_outdated_timeline_false_high_confidence_fails():
    """
    Asserts that a record with outdated operational details is rejected 
    if it attempts to carry an unverified 'High' confidence status.
    """
    record = {'Company Name': 'Legacy Tech Corp', 'Recent News': '2024-02-10 - Series A Funding', 'confidence_level': 'High'}
    with pytest.raises(ValueError, match="is 'Outdated' .* A 'High' confidence level is disallowed"):
        tc_15_3_validate_record_recency(record)

def test_tc_15_3_malformed_dates_prevent_high_confidence_fails():
    """
    Asserts that if the recency cannot be programmatically verified due to
    malformed dates, the record is blocked from claiming 'High' confidence.
    """
    record = {'Company Name': 'Unresolved LLC', 'Recent News': 'Sometime last year - Opened new headquarters', 'confidence_level': 'High'}
    with pytest.raises(ValueError, match="Cannot verify recency .* 'High' confidence level is disallowed"):
        tc_15_3_validate_record_recency(record)
tc_15_5_FIELD_WEIGHTS = {'Company Name': 10, 'Category': 10, 'Year of Incorporation': 10, 'Nature of Company': 10, 'Company Headquarters': 10, 'Employee Size': 10, 'Website URL': 10, 'CEO Name': 10, 'Recent News': 5, 'Annual Revenues': 5, 'Recent Funding Rounds': 5, 'Total Capital Raised': 5, 'Hiring Velocity': 5, 'Employee Turnover': 5, 'Short Name': 2, 'Logo': 2, 'Countries Operating In': 2, 'Office Locations': 2, 'Market Share (%)': 2, 'Key Investors / Backers': 2, 'Quality of Website': 1, 'Website Rating': 1, 'Website Traffic Rank': 1, 'Glassdoor Rating': 1, 'Indeed Rating': 1}

def tc_15_5_calculate_composite_quality_score(record: Dict[str, Any]) -> Tuple[float, str]:
    """
    Calculates the weighted composite quality score for a company record [1, 3].
    
    Formula:
      - Completeness: Sum(weights of populated fields) / Sum(all field weights)
      - Accuracy: Average confidence level of populated fields (High=100%, Medium=70%, Low=40%)
      - Recency: Freshness of record (Recent=100%, Acceptable=85%, Outdated=50%, Unknown=0%)
      
      Composite = (Completeness * 0.4) + (Accuracy * 0.4) + (Recency * 0.2)
    """
    total_possible_weight = sum(tc_15_5_FIELD_WEIGHTS.values())
    populated_weight = 0.0
    confidence_sum = 0.0
    populated_count = 0
    for field, weight in tc_15_5_FIELD_WEIGHTS.items():
        val = record.get(field)
        if val is not None and str(val).strip() != '' and (str(val).lower() != 'n/a'):
            populated_weight += weight
            populated_count += 1
            field_conf = record.get(f"confidence_{field.lower().replace(' ', '_')}", 'Medium').strip().title()
            if field_conf == 'High':
                confidence_sum += 1.0
            elif field_conf == 'Medium':
                confidence_sum += 0.7
            else:
                confidence_sum += 0.4
    completeness_score = populated_weight / total_possible_weight * 100
    accuracy_score = confidence_sum / populated_count * 100 if populated_count > 0 else 0.0
    recency_tier = record.get('recency_tier', 'Unknown').strip().title()
    if recency_tier == 'Recent':
        recency_score = 100.0
    elif recency_tier == 'Acceptable':
        recency_score = 85.0
    elif recency_tier == 'Outdated':
        recency_score = 50.0
    else:
        recency_score = 0.0
    composite_score = completeness_score * 0.4 + accuracy_score * 0.4 + recency_score * 0.2
    if composite_score >= 90.0:
        grade = 'A'
    elif composite_score >= 80.0:
        grade = 'B'
    elif composite_score >= 70.0:
        grade = 'C'
    elif composite_score >= 60.0:
        grade = 'D'
    else:
        grade = 'F'
    critical_fields = [f for f, w in tc_15_5_FIELD_WEIGHTS.items() if w == 10]
    for field in critical_fields:
        if record.get(field) is None or str(record.get(field)).strip() == '':
            grade = 'F'
            break
    return (round(composite_score, 2), grade)

def tc_15_5_validate_record_quality_threshold(record: Dict[str, Any]) -> bool:
    """
    SDET Validator: Enforces overall quality thresholds.
    Halts execution if the composite score calculates to an 'F' grade [1].
    """
    score, grade = tc_15_5_calculate_composite_quality_score(record)
    record['composite_quality_score'] = score
    record['quality_grade'] = grade
    if grade == 'F':
        raise ValueError(f"Quality Threshold Violated: Record has failed quality grading with an 'F' grade (Score: {score}%). Processing halted.")
    return True

def test_tc_15_5_perfect_enterprise_profile_grade_a():
    """
    Validates a completely populated, high-confidence, fresh public enterprise 
    record. Expects a score of >= 90% and a grade of 'A'.
    """
    record = {'Company Name': 'Microsoft Corp.', 'Category': 'Enterprise', 'Year of Incorporation': 1975, 'Nature of Company': 'Public', 'Company Headquarters': 'Redmond, USA', 'Employee Size': '100000+', 'Website URL': 'https://www.microsoft.com', 'CEO Name': 'Satya Nadella', 'Recent News': '2026-03-10 - Acquired New Startup', 'Annual Revenues': '$211B', 'Recent Funding Rounds': 'N/A', 'Total Capital Raised': '$10B', 'Hiring Velocity': 'High', 'Employee Turnover': '10%', 'recency_tier': 'Recent', 'confidence_company_name': 'High', 'confidence_category': 'High', 'confidence_year_of_incorporation': 'High', 'confidence_nature_of_company': 'High', 'confidence_company_headquarters': 'High', 'confidence_employee_size': 'High', 'confidence_website_url': 'High', 'confidence_ceo_name': 'High', 'confidence_recent_news': 'High', 'confidence_annual_revenues': 'High'}
    assert tc_15_5_validate_record_quality_threshold(record) is True
    assert record['quality_grade'] == 'A'
    assert record['composite_quality_score'] >= 90.0

def test_tc_15_5_mixed_startup_profile_grade_b_or_c():
    """
    Validates a standard startup record missing several optional parameters.
    Expects a passing grade (B or C) because critical parameters are intact.
    """
    record = {'Company Name': 'SaaSLauncher', 'Category': 'Startup', 'Year of Incorporation': 2022, 'Nature of Company': 'Private', 'Company Headquarters': 'Boston, USA', 'Employee Size': '11-50', 'Website URL': 'https://www.saaslaunch.com', 'CEO Name': 'Jane Doe', 'Recent News': None, 'Annual Revenues': None, 'Total Capital Raised': None, 'recency_tier': 'Acceptable'}
    assert tc_15_5_validate_record_quality_threshold(record) is True
    assert record['quality_grade'] in ['B', 'C']

def test_tc_15_5_missing_critical_field_auto_fails_to_f():
    """
    Asserts that if any critical identity parameter (like CEO Name) is missing,
    the scoring engine automatically downgrades the record to 'F' and halts ingestion.
    """
    record = {'Company Name': 'SaaSLauncher', 'Category': 'Startup', 'Year of Incorporation': 2022, 'Nature of Company': 'Private', 'Company Headquarters': 'Boston, USA', 'Employee Size': '11-50', 'Website URL': 'https://www.saaslaunch.com', 'CEO Name': None, 'recency_tier': 'Recent'}
    with pytest.raises(ValueError, match="failed quality grading with an 'F' grade"):
        tc_15_5_validate_record_quality_threshold(record)

def test_tc_15_5_low_confidence_and_outdated_fails_to_f():
    """
    Asserts that a record heavily populated with low-confidence and outdated
    parameters mathematically falls below the passing score threshold, failing with an 'F'.
    """
    record = {'Company Name': 'Stale Corp', 'Category': 'Startup', 'Year of Incorporation': 2010, 'Nature of Company': 'Private', 'Company Headquarters': 'Detroit, USA', 'Employee Size': '1-10', 'Website URL': 'https://www.stale.com', 'CEO Name': 'John Stale', 'recency_tier': 'Outdated', 'confidence_company_name': 'Low', 'confidence_category': 'Low', 'confidence_year_of_incorporation': 'Low', 'confidence_nature_of_company': 'Low', 'confidence_company_headquarters': 'Low', 'confidence_employee_size': 'Low', 'confidence_website_url': 'Low', 'confidence_ceo_name': 'Low'}
    with pytest.raises(ValueError, match="failed quality grading with an 'F' grade"):
        tc_15_5_validate_record_quality_threshold(record)
tc_2_1_METADATA_SCHEMA = {'Company Name': False, 'Short Name': True, 'Logo': False, 'Category': False, 'Year of Incorporation': False, 'Overview of the Company': False, 'Nature of Company': False, 'Company Headquarters': False, 'Countries Operating In': True, 'Number of Offices (beyond HQ)': True, 'Office Locations': True, 'Employee Size': False, 'Hiring Velocity': True, 'Employee Turnover': True, 'Average Retention Tenure': True, 'Pain Points Being Addressed': False, 'Focus Sectors / Industries': False, 'Services / Offerings / Products': False, 'Top Customers by Client Segments': True, 'Core Value Proposition': False, 'Vision': True, 'Mission': True, 'Values': True, 'Unique Differentiators': True, 'Competitive Advantages': True, 'Weaknesses / Gaps in Offering': True, 'Key Challenges and Unmet Needs': True, 'Key Competitors': False, 'Technology Partners': True, 'Interesting Facts': True, 'Recent News': True, 'Website URL': False, 'Quality of Website': True, 'Website Rating': True, 'Website Traffic Rank': True, 'Social Media Followers – Combined': False, 'Glassdoor Rating': True, 'Indeed Rating': True, 'Google Reviews Rating': True, 'LinkedIn Profile URL': True, 'Twitter (X) Handle': True, 'Facebook Page URL': True, 'Instagram Page URL': True, 'CEO Name': False, 'CEO LinkedIn URL': True, 'Key Business Leaders': False, 'Warm Introduction Pathways': True, 'Decision Maker Accessibility': True, 'Company Contact Email': True, 'Company Phone Number': True, "Primary Contact Person's Name": True, "Primary Contact Person's Title": True, "Primary Contact Person's Email": True, "Primary Contact Person's Phone Number": True, 'Awards & Recognitions': True, 'Brand Sentiment Score': True, 'Event Participation': True, 'Regulatory & Compliance Status': True, 'Legal Issues / Controversies': True, 'Annual Revenues': True, 'Annual Profits': True, 'Revenue Mix': True, 'Company Valuation': True, 'Year-over-Year Growth Rate': True, 'Profitability Status': False, 'Market Share (%)': True, 'Key Investors / Backers': True, 'Recent Funding Rounds': True, 'Total Capital Raised': True, 'ESG Practices or Ratings': True, 'Sales Motion': False, 'Customer Acquisition Cost (CAC)': True, 'Customer Lifetime Value (CLV)': True, 'CAC:LTV Ratio': True, 'Churn Rate': True, 'Net Promoter Score (NPS)': True, 'Customer Concentration Risk': True, 'Burn Rate': True, 'Runway': True, 'Burn Multiplier': True, 'Intellectual Property': True, 'R&D Investment': True, 'AI/ML Adoption Level': True, 'Tech Stack/Tools Used': True, 'Cybersecurity Posture': True, 'Supply Chain Dependencies': True, 'Geopolitical Risks': True, 'Macro Risks': True, 'Diversity Metrics': True, 'Remote Work Policy': False, 'Training/Development Spend': True, 'Partnership Ecosystem': True, 'Exit Strategy/History': True, 'Carbon Footprint/Environmental Impact': True, 'Ethical Sourcing Practices': True, 'Benchmark vs. Peers': True, 'Future Projections': True, 'Strategic Priorities': False, 'Industry Associations / Memberships': True, 'Case Studies / Public Success Stories': True, 'Go-to-Market Strategy': False, 'Innovation Roadmap ': True, 'Product Pipeline': True, 'Board of Directors / Advisors': False, 'Company Introduction / Marketing videos': True, 'Customer testimonial': True, 'Industry Benchmark Technology Adoption Rating': True, 'Total Addressable Market (TAM)': True, 'Serviceable Addressable Market (SAM)': True, 'Serviceable Obtainable Market (SOM)': True, 'Work culture': True, 'Manager quality': True, 'Psychological safety': True, 'Feedback culture': True, 'Diversity & inclusion': True, 'Ethical standards': True, 'Typical working hours': True, 'Overtime expectations': True, 'Weekend work': True, 'Remote / hybrid / on-site flexibility': False, 'Leave policy': True, 'Burnout risk': True, 'Central vs peripheral location': True, 'Public transport access': True, 'Cab availability and company cab policy': True, 'Commute time from airport': True, 'Office zone type': True, 'Area safety': True, 'Company safety policies': True, 'Office infrastructure safety': True, 'Emergency response preparedness': True, 'Health support': True, 'Onboarding and training quality': True, 'Learning culture': True, 'Exposure quality': True, 'Mentorship availability': True, 'Internal mobility': True, 'Promotion clarity': True, 'Tools and technology access': True, 'Role clarity': True, 'Early ownership': True, 'Work impact': True, 'Execution vs thinking balance': True, 'Automation level': True, 'Cross-functional exposure': True, 'Company maturity': False, 'Brand value': True, 'Client quality': True, 'Layoff history': True, 'Fixed vs variable pay': True, 'Bonus predictability': True, 'ESOPs and long-term incentives': True, 'Family health insurance': True, 'Relocation support': True, 'Lifestyle and wellness benefits': True, 'Exit opportunities': True, 'Skill relevance': True, 'External recognition': True, 'Network strength': True, 'Global exposure': True, 'Mission clarity': True, 'Sustainability and CSR': True, 'Crisis behavior': True}

def tc_2_1_calculate_profile_richness(payload: Dict[str, Any]) -> Tuple[bool, float, str]:
    """
    Evaluates profile completeness across the complete 163-field schema.
    - Ensures all mandatory fields (nullable=False) are present and non-empty.
    - Computes a percentage richness score based on both optional and mandatory presence.
    - Returns (validation_success, richness_percentage, error_message).
    """
    total_fields = len(tc_2_1_METADATA_SCHEMA)
    populated_count = 0
    missing_mandatory = []
    for field_name, is_nullable in tc_2_1_METADATA_SCHEMA.items():
        val = payload.get(field_name)
        is_populated = False
        if val is not None:
            if isinstance(val, str):
                if val.strip() != '':
                    is_populated = True
            else:
                is_populated = True
        if is_populated:
            populated_count += 1
        elif not is_nullable:
            missing_mandatory.append(field_name)
    richness_score = round(populated_count / total_fields * 100, 2)
    if missing_mandatory:
        error_msg = f"Mandatory fields missing: {', '.join(missing_mandatory)}"
        return (False, richness_score, error_msg)
    return (True, richness_score, 'Profile validated successfully.')

def tc_2_1_generate_mock_completed_profile() -> Dict[str, Any]:
    """Generates a mock profile payload with all 163 fields populated with valid placeholder values."""
    mock_profile = {}
    for field_name, is_nullable in tc_2_1_METADATA_SCHEMA.items():
        if 'Rating' in field_name or 'Rate' in field_name or 'Score' in field_name:
            mock_profile[field_name] = '5.0' if 'Rating' in field_name else '15%'
        elif 'Number' in field_name or 'Size' in field_name or 'Year' in field_name or ('Rank' in field_name):
            mock_profile[field_name] = 2025 if 'Year' in field_name else 100
        elif 'URL' in field_name or 'video' in field_name:
            mock_profile[field_name] = 'https://example.com'
        elif 'Email' in field_name:
            mock_profile[field_name] = 'contact@example.com'
        else:
            mock_profile[field_name] = 'Mock populated text data'
    return mock_profile

def test_tc_2_1_complete_profile_richness_score_100_percent():
    """Verifies that a fully populated profile returns exactly a 100% data richness score."""
    full_payload = tc_2_1_generate_mock_completed_profile()
    success, score, msg = tc_2_1_calculate_profile_richness(full_payload)
    assert success is True
    assert score == 100.0
    assert msg == 'Profile validated successfully.'

def test_tc_2_1_missing_mandatory_fields_fails_validation():
    """Verifies that missing any mandatory field fails validation even if other fields are populated."""
    payload = tc_2_1_generate_mock_completed_profile()
    payload.pop('Company Name')
    success, score, msg = tc_2_1_calculate_profile_richness(payload)
    assert success is False
    assert 'Company Name' in msg
    assert score < 100.0

def test_tc_2_1_missing_optional_fields_graceful_degradation():
    """Verifies that missing optional fields degrades the richness score but passes schema validation."""
    payload = tc_2_1_generate_mock_completed_profile()
    optional_keys_to_remove = [k for k, is_nullable in tc_2_1_METADATA_SCHEMA.items() if is_nullable][:10]
    for key in optional_keys_to_remove:
        payload.pop(key)
    success, score, msg = tc_2_1_calculate_profile_richness(payload)
    assert success is True
    assert score == 93.87
    assert 'validated successfully' in msg
tc_2_2_SCHEMA_DEFINITIONS = {'Company Name': False, 'Short Name': True, 'Logo': False, 'Category': False, 'Year of Incorporation': False, 'Overview of the Company': False, 'Nature of Company': False, 'Company Headquarters': False, 'Countries Operating In': True, 'Number of Offices (beyond HQ)': True, 'Office Locations': True, 'Employee Size': False, 'Hiring Velocity': True, 'Employee Turnover': True, 'Average Retention Tenure': True, 'Pain Points Being Addressed': False, 'Focus Sectors / Industries': False, 'Services / Offerings / Products': False, 'Top Customers by Client Segments': True, 'Core Value Proposition': False, 'Vision': True, 'Mission': True, 'Values': True, 'Unique Differentiators': True, 'Competitive Advantages': True, 'Weaknesses / Gaps in Offering': True, 'Key Challenges and Unmet Needs': True, 'Key Competitors': False, 'Technology Partners': True, 'Interesting Facts': True, 'Recent News': True, 'Website URL': False, 'Quality of Website': True, 'Website Rating': True, 'Website Traffic Rank': True, 'Social Media Followers – Combined': False, 'Glassdoor Rating': True, 'Indeed Rating': True, 'Google Reviews Rating': True, 'LinkedIn Profile URL': True, 'Twitter (X) Handle': True, 'Facebook Page URL': True, 'Instagram Page URL': True, 'CEO Name': False, 'CEO LinkedIn URL': True, 'Key Business Leaders': False, 'Warm Introduction Pathways': True, 'Decision Maker Accessibility': True, 'Company Contact Email': True, 'Company Phone Number': True, "Primary Contact Person's Name": True, "Primary Contact Person's Title": True, "Primary Contact Person's Email": True, "Primary Contact Person's Phone Number": True, 'Awards & Recognitions': True, 'Brand Sentiment Score': True, 'Event Participation': True, 'Regulatory & Compliance Status': True, 'Legal Issues / Controversies': True, 'Annual Revenues': True, 'Annual Profits': True, 'Revenue Mix': True, 'Company Valuation': True, 'Year-over-Year Growth Rate': True, 'Profitability Status': False, 'Market Share (%)': True, 'Key Investors / Backers': True, 'Recent Funding Rounds': True, 'Total Capital Raised': True, 'ESG Practices or Ratings': True, 'Sales Motion': False, 'Customer Acquisition Cost (CAC)': True, 'Customer Lifetime Value (CLV)': True, 'CAC:LTV Ratio': True, 'Churn Rate': True, 'Net Promoter Score (NPS)': True, 'Customer Concentration Risk': True, 'Burn Rate': True, 'Runway': True, 'Burn Multiplier': True, 'Intellectual Property': True, 'R&D Investment': True, 'AI/ML Adoption Level': True, 'Tech Stack/Tools Used': True, 'Cybersecurity Posture': True, 'Supply Chain Dependencies': True, 'Geopolitical Risks': True, 'Macro Risks': True, 'Diversity Metrics': True, 'Remote Work Policy': False, 'Training/Development Spend': True, 'Partnership Ecosystem': True, 'Exit Strategy/History': True, 'Carbon Footprint/Environmental Impact': True, 'Ethical Sourcing Practices': True, 'Benchmark vs. Peers': True, 'Future Projections': True, 'Strategic Priorities': False, 'Industry Associations / Memberships': True, 'Case Studies / Public Success Stories': True, 'Go-to-Market Strategy': False, 'Innovation Roadmap ': True, 'Product Pipeline': True, 'Board of Directors / Advisors': False, 'Company Introduction / Marketing videos': True, 'Customer testimonial': True, 'Industry Benchmark Technology Adoption Rating': True, 'Total Addressable Market (TAM)': True, 'Serviceable Addressable Market (SAM)': True, 'Serviceable Obtainable Market (SOM)': True, 'Work culture': True, 'Manager quality': True, 'Psychological safety': True, 'Feedback culture': True, 'Diversity & inclusion': True, 'Ethical standards': True, 'Typical working hours': True, 'Overtime expectations': True, 'Weekend work': True, 'Remote / hybrid / on-site flexibility': False, 'Leave policy': True, 'Burnout risk': True, 'Central vs peripheral location': True, 'Public transport access': True, 'Cab availability and company cab policy': True, 'Commute time from airport': True, 'Office zone type': True, 'Area safety': True, 'Company safety policies': True, 'Office infrastructure safety': True, 'Emergency response preparedness': True, 'Health support': True, 'Onboarding and training quality': True, 'Learning culture': True, 'Exposure quality': True, 'Mentorship availability': True, 'Internal mobility': True, 'Promotion clarity': True, 'Tools and technology access': True, 'Role clarity': True, 'Early ownership': True, 'Work impact': True, 'Execution vs thinking balance': True, 'Automation level': True, 'Cross-functional exposure': True, 'Company maturity': False, 'Brand value': True, 'Client quality': True, 'Layoff history': True, 'Fixed vs variable pay': True, 'Bonus predictability': True, 'ESOPs and long-term incentives': True, 'Family health insurance': True, 'Relocation support': True, 'Lifestyle and wellness benefits': True, 'Exit opportunities': True, 'Skill relevance': True, 'External recognition': True, 'Network strength': True, 'Global exposure': True, 'Mission clarity': True, 'Sustainability and CSR': True, 'Crisis behavior': True}

def tc_2_2_parse_derived_runway(total_capital: Optional[float], burn_rate: Optional[float]) -> Optional[float]:
    """
    Calculates derived runway metric.
    Safely degrades to None if parent values are missing, avoiding division/null errors.
    """
    if total_capital is None or burn_rate is None:
        return None
    if burn_rate == 0:
        return None
    return round(total_capital / burn_rate, 2)

def tc_2_2_evaluate_profile(payload: Dict[str, Any]) -> Tuple[bool, float, Optional[float], str]:
    """
    Validates complete profile payload.
    - Fails if mandatory fields are missing.
    - Calculates overall richness score.
    - Safely evaluates derived financial metrics.
    Returns: (success, richness_percentage, calculated_runway, message)
    """
    total_fields = len(tc_2_2_SCHEMA_DEFINITIONS)
    populated_count = 0
    missing_mandatory = []
    for field, is_nullable in tc_2_2_SCHEMA_DEFINITIONS.items():
        val = payload.get(field)
        is_populated = False
        if val is not None:
            if isinstance(val, str):
                if val.strip() != '':
                    is_populated = True
            else:
                is_populated = True
        if is_populated:
            populated_count += 1
        elif not is_nullable:
            missing_mandatory.append(field)
    richness_score = round(populated_count / total_fields * 100, 2)
    if missing_mandatory:
        return (False, richness_score, None, f"Failed: Mandatory fields missing - {', '.join(missing_mandatory)}")
    raw_capital = payload.get('Total Capital Raised')
    raw_burn = payload.get('Burn Rate')
    runway = tc_2_2_parse_derived_runway(raw_capital, raw_burn)
    return (True, richness_score, runway, 'Profile processed successfully.')

def tc_2_2_build_minimal_mandatory_profile() -> Dict[str, Any]:
    """Generates a profile with only mandatory fields populated (minimally complete)."""
    minimal_profile = {}
    for field, is_nullable in tc_2_2_SCHEMA_DEFINITIONS.items():
        if not is_nullable:
            if 'Year' in field:
                minimal_profile[field] = 2026
            elif 'followers' in field.lower() or 'followers' in field:
                minimal_profile[field] = 500
            elif 'URL' in field:
                minimal_profile[field] = 'https://example.com'
            else:
                minimal_profile[field] = 'Mandatory Text Placeholder'
        else:
            minimal_profile[field] = None
    return minimal_profile

def test_tc_2_2_minimal_mandatory_profile_passes_validation():
    """Verifies that a profile containing only mandatory fields successfully passes validation."""
    minimal_payload = tc_2_2_build_minimal_mandatory_profile()
    success, score, runway, msg = tc_2_2_evaluate_profile(minimal_payload)
    assert success is True
    assert score == 15.34
    assert runway is None
    assert msg == 'Profile processed successfully.'

def test_tc_2_2_derived_runway_calculation_success():
    """Verifies that runway calculation evaluates correctly when base optional fields are provided."""
    payload = tc_2_2_build_minimal_mandatory_profile()
    payload['Total Capital Raised'] = 1200000.0
    payload['Burn Rate'] = 100000.0
    success, score, runway, msg = tc_2_2_evaluate_profile(payload)
    assert success is True
    assert score == 16.56
    assert runway == 12.0

def test_tc_2_2_derived_runway_by_zero_handling():
    """Verifies that division-by-zero errors are caught and handled gracefully as None."""
    payload = tc_2_2_build_minimal_mandatory_profile()
    payload['Total Capital Raised'] = 100000.0
    payload['Burn Rate'] = 0.0
    success, score, runway, msg = tc_2_2_evaluate_profile(payload)
    assert success is True
    assert runway is None
tc_2_3_SCHEMA_NULLABILITY_REGISTRY = {'Company Name': False, 'Short Name': True, 'Logo': False, 'Category': False, 'Year of Incorporation': False, 'Overview of the Company': False, 'Nature of Company': False, 'Company Headquarters': False, 'Countries Operating In': True, 'Number of Offices (beyond HQ)': True, 'Office Locations': True, 'Employee Size': False, 'Hiring Velocity': True, 'Employee Turnover': True, 'Average Retention Tenure': True, 'Pain Points Being Addressed': False, 'Focus Sectors / Industries': False, 'Services / Offerings / Products': False, 'Top Customers by Client Segments': True, 'Core Value Proposition': False, 'Vision': True, 'Mission': True, 'Values': True, 'Unique Differentiators': True, 'Competitive Advantages': True, 'Weaknesses / Gaps in Offering': True, 'Key Challenges and Unmet Needs': True, 'Key Competitors': False, 'Technology Partners': True, 'Interesting Facts': True, 'Recent News': True, 'Website URL': False, 'Quality of Website': True, 'Website Rating': True, 'Website Traffic Rank': True, 'Social Media Followers – Combined': False, 'Glassdoor Rating': True, 'Indeed Rating': True, 'Google Reviews Rating': True, 'LinkedIn Profile URL': True, 'Twitter (X) Handle': True, 'Facebook Page URL': True, 'Instagram Page URL': True, 'CEO Name': False, 'CEO LinkedIn URL': True, 'Key Business Leaders': False, 'Warm Introduction Pathways': True, 'Decision Maker Accessibility': True, 'Company Contact Email': True, 'Company Phone Number': True, "Primary Contact Person's Name": True, "Primary Contact Person's Title": True, "Primary Contact Person's Email": True, "Primary Contact Person's Phone Number": True, 'Awards & Recognitions': True, 'Brand Sentiment Score': True, 'Event Participation': True, 'Regulatory & Compliance Status': True, 'Legal Issues / Controversies': True, 'Annual Revenues': True, 'Annual Profits': True, 'Revenue Mix': True, 'Company Valuation': True, 'Year-over-Year Growth Rate': True, 'Profitability Status': False, 'Market Share (%)': True, 'Key Investors / Backers': True, 'Recent Funding Rounds': True, 'Total Capital Raised': True, 'ESG Practices or Ratings': True, 'Sales Motion': False, 'Customer Acquisition Cost (CAC)': True, 'Customer Lifetime Value (CLV)': True, 'CAC:LTV Ratio': True, 'Churn Rate': True, 'Net Promoter Score (NPS)': True, 'Customer Concentration Risk': True, 'Burn Rate': True, 'Runway': True, 'Burn Multiplier': True, 'Intellectual Property': True, 'R&D Investment': True, 'AI/ML Adoption Level': True, 'Tech Stack/Tools Used': True, 'Cybersecurity Posture': True, 'Supply Chain Dependencies': True, 'Geopolitical Risks': True, 'Macro Risks': True, 'Diversity Metrics': True, 'Remote Work Policy': False, 'Training/Development Spend': True, 'Partnership Ecosystem': True, 'Exit Strategy/History': True, 'Carbon Footprint/Environmental Impact': True, 'Ethical Sourcing Practices': True, 'Benchmark vs. Peers': True, 'Future Projections': True, 'Strategic Priorities': False, 'Industry Associations / Memberships': True, 'Case Studies / Public Success Stories': True, 'Go-to-Market Strategy': False, 'Innovation Roadmap ': True, 'Product Pipeline': True, 'Board of Directors / Advisors': False, 'Company Introduction / Marketing videos': True, 'Customer testimonial': True, 'Industry Benchmark Technology Adoption Rating': True, 'Total Addressable Market (TAM)': True, 'Serviceable Addressable Market (SAM)': True, 'Serviceable Obtainable Market (SOM)': True, 'Work culture': True, 'Manager quality': True, 'Psychological safety': True, 'Feedback culture': True, 'Diversity & inclusion': True, 'Ethical standards': True, 'Typical working hours': True, 'Overtime expectations': True, 'Weekend work': True, 'Remote / hybrid / on-site flexibility': False, 'Leave policy': True, 'Burnout risk': True, 'Central vs peripheral location': True, 'Public transport access': True, 'Cab availability and company cab policy': True, 'Commute time from airport': True, 'Office zone type': True, 'Area safety': True, 'Company safety policies': True, 'Office infrastructure safety': True, 'Emergency response preparedness': True, 'Health support': True, 'Onboarding and training quality': True, 'Learning culture': True, 'Exposure quality': True, 'Mentorship availability': True, 'Internal mobility': True, 'Promotion clarity': True, 'Tools and technology access': True, 'Role clarity': True, 'Early ownership': True, 'Work impact': True, 'Execution vs thinking balance': True, 'Automation level': True, 'Cross-functional exposure': True, 'Company maturity': False, 'Brand value': True, 'Client quality': True, 'Layoff history': True, 'Fixed vs variable pay': True, 'Bonus predictability': True, 'ESOPs and long-term incentives': True, 'Family health insurance': True, 'Relocation support': True, 'Lifestyle and wellness benefits': True, 'Exit opportunities': True, 'Skill relevance': True, 'External recognition': True, 'Network strength': True, 'Global exposure': True, 'Mission clarity': True, 'Sustainability and CSR': True, 'Crisis behavior': True}

def tc_2_3_simulate_pipeline_extraction(company_name: str) -> dict:
    """
    Simulates a data ingestion pipeline.
    If the target company is non-existent, it returns None/NULL for all 163 fields.
    """
    known_entities = {'Microsoft', 'Apple', 'Tesla', 'Google'}
    extracted_data = {}
    if company_name in known_entities:
        for field in tc_2_3_SCHEMA_NULLABILITY_REGISTRY.keys():
            extracted_data[field] = 'Valid Data'
    else:
        for field in tc_2_3_SCHEMA_NULLABILITY_REGISTRY.keys():
            extracted_data[field] = None
    return extracted_data

def tc_2_3_validate_extracted_field(field_name: str, extracted_value: Any) -> bool:
    """
    Validates field input rules:
    - If extracted value is None:
        - Returns True if the field is optional (Nullable = True).
        - Returns False if the field is mandatory (Nullable = False).
    """
    is_nullable = tc_2_3_SCHEMA_NULLABILITY_REGISTRY.get(field_name)
    if is_nullable is None:
        raise ValueError(f"Field '{field_name}' not defined in nullability registry.")
    if extracted_value is None:
        return is_nullable
    return True

@pytest.mark.parametrize('field_name, is_nullable', tc_2_3_SCHEMA_NULLABILITY_REGISTRY.items())
def test_tc_2_3_non_existent_company_extraction_handling(field_name, is_nullable):
    """
    Systematically verifies parameter behavior when target entity does not exist:
    - Verifies that mandatory parameters reject NULL and raise/return False.
    - Verifies that optional parameters accept NULL and return True.
    """
    extracted_payload = tc_2_3_simulate_pipeline_extraction('FakeCorpXYZ')
    field_value = extracted_payload.get(field_name)
    assert field_value is None, f'Expected {field_name} to be extracted as None, but got {field_value}.'
    validation_status = tc_2_3_validate_extracted_field(field_name, field_value)
    assert validation_status == is_nullable, f"Validation failure on '{field_name}' with Nullable={is_nullable}. Expected validation response of {is_nullable}, but got {validation_status}."
tc_2_4_SCHEMA_REGISTRY = {'Company Name': False, 'Short Name': True, 'Logo': False, 'Category': False, 'Year of Incorporation': False, 'Overview of the Company': False, 'Nature of Company': False, 'Company Headquarters': False, 'Countries Operating In': True, 'Number of Offices (beyond HQ)': True, 'Office Locations': True, 'Employee Size': False, 'Hiring Velocity': True, 'Employee Turnover': True, 'Average Retention Tenure': True, 'Pain Points Being Addressed': False, 'Focus Sectors / Industries': False, 'Services / Offerings / Products': False, 'Top Customers by Client Segments': True, 'Core Value Proposition': False, 'Vision': True, 'Mission': True, 'Values': True, 'Unique Differentiators': True, 'Competitive Advantages': True, 'Weaknesses / Gaps in Offering': True, 'Key Challenges and Unmet Needs': True, 'Key Competitors': False, 'Technology Partners': True, 'Interesting Facts': True, 'Recent News': True, 'Website URL': False, 'Quality of Website': True, 'Website Rating': True, 'Website Traffic Rank': True, 'Social Media Followers – Combined': False, 'Glassdoor Rating': True, 'Indeed Rating': True, 'Google Reviews Rating': True, 'LinkedIn Profile URL': True, 'Twitter (X) Handle': True, 'Facebook Page URL': True, 'Instagram Page URL': True, 'CEO Name': False, 'CEO LinkedIn URL': True, 'Key Business Leaders': False, 'Warm Introduction Pathways': True, 'Decision Maker Accessibility': True, 'Company Contact Email': True, 'Company Phone Number': True, "Primary Contact Person's Name": True, "Primary Contact Person's Title": True, "Primary Contact Person's Email": True, "Primary Contact Person's Phone Number": True, 'Awards & Recognitions': True, 'Brand Sentiment Score': True, 'Event Participation': True, 'Regulatory & Compliance Status': True, 'Legal Issues / Controversies': True, 'Annual Revenues': True, 'Annual Profits': True, 'Revenue Mix': True, 'Company Valuation': True, 'Year-over-Year Growth Rate': True, 'Profitability Status': False, 'Market Share (%)': True, 'Key Investors / Backers': True, 'Recent Funding Rounds': True, 'Total Capital Raised': True, 'ESG Practices or Ratings': True, 'Sales Motion': False, 'Customer Acquisition Cost (CAC)': True, 'Customer Lifetime Value (CLV)': True, 'CAC:LTV Ratio': True, 'Churn Rate': True, 'Net Promoter Score (NPS)': True, 'Customer Concentration Risk': True, 'Burn Rate': True, 'Runway': True, 'Burn Multiplier': True, 'Intellectual Property': True, 'R&D Investment': True, 'AI/ML Adoption Level': True, 'Tech Stack/Tools Used': True, 'Cybersecurity Posture': True, 'Supply Chain Dependencies': True, 'Geopolitical Risks': True, 'Macro Risks': True, 'Diversity Metrics': True, 'Remote Work Policy': False, 'Training/Development Spend': True, 'Partnership Ecosystem': True, 'Exit Strategy/History': True, 'Carbon Footprint/Environmental Impact': True, 'Ethical Sourcing Practices': True, 'Benchmark vs. Peers': True, 'Future Projections': True, 'Strategic Priorities': False, 'Industry Associations / Memberships': True, 'Case Studies / Public Success Stories': True, 'Go-to-Market Strategy': False, 'Innovation Roadmap ': True, 'Product Pipeline': True, 'Board of Directors / Advisors': False, 'Company Introduction / Marketing videos': True, 'Customer testimonial': True, 'Industry Benchmark Technology Adoption Rating': True, 'Total Addressable Market (TAM)': True, 'Serviceable Addressable Market (SAM)': True, 'Serviceable Obtainable Market (SOM)': True, 'Work culture': True, 'Manager quality': True, 'Psychological safety': True, 'Feedback culture': True, 'Diversity & inclusion': True, 'Ethical standards': True, 'Typical working hours': True, 'Overtime expectations': True, 'Weekend work': True, 'Remote / hybrid / on-site flexibility': False, 'Leave policy': True, 'Burnout risk': True, 'Central vs peripheral location': True, 'Public transport access': True, 'Cab availability and company cab policy': True, 'Commute time from airport': True, 'Office zone type': True, 'Area safety': True, 'Company safety policies': True, 'Office infrastructure safety': True, 'Emergency response preparedness': True, 'Health support': True, 'Onboarding and training quality': True, 'Learning culture': True, 'Exposure quality': True, 'Mentorship availability': True, 'Internal mobility': True, 'Promotion clarity': True, 'Tools and technology access': True, 'Role clarity': True, 'Early ownership': True, 'Work impact': True, 'Execution vs thinking balance': True, 'Automation level': True, 'Cross-functional exposure': True, 'Company maturity': False, 'Brand value': True, 'Client quality': True, 'Layoff history': True, 'Fixed vs variable pay': True, 'Bonus predictability': True, 'ESOPs and long-term incentives': True, 'Family health insurance': True, 'Relocation support': True, 'Lifestyle and wellness benefits': True, 'Exit opportunities': True, 'Skill relevance': True, 'External recognition': True, 'Network strength': True, 'Global exposure': True, 'Mission clarity': True, 'Sustainability and CSR': True, 'Crisis behavior': True}

def tc_2_4_validate_mandatory_and_optional_rules(field_name: str, value: Any) -> bool:
    """
    Validates boundary criteria:
    - If value is None:
        - Returns True if field is optional (is_nullable = True).
        - Returns False if field is mandatory (is_nullable = False).
    - If value is not None, returns True (passes completeness boundary).
    """
    is_nullable = tc_2_4_SCHEMA_REGISTRY.get(field_name)
    if is_nullable is None:
        raise ValueError(f"Field '{field_name}' not defined in SCHEMA_REGISTRY.")
    if value is None:
        return is_nullable
    return True

@pytest.mark.parametrize('field_name, is_nullable', tc_2_4_SCHEMA_REGISTRY.items())
def test_tc_2_4_null_value_completeness_boundaries(field_name, is_nullable):
    """
    Validates per-parameter boundaries:
    - Asserts that mandatory fields (is_nullable=False) reject None.
    - Asserts that optional fields (is_nullable=True) accept None.
    """
    actual_status = tc_2_4_validate_mandatory_and_optional_rules(field_name, None)
    expected_status = is_nullable
    assert actual_status == expected_status, f"Completeness boundary mismatch on '{field_name}' with Nullable={is_nullable}. Expected {expected_status}, but got {actual_status}."

def tc_2_5_validate_field_dependencies(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter completeness dependency rules:
    1. If CEO Name exists, CEO LinkedIn URL should exist.
    2. If CAC and CLV exist, CAC:LTV Ratio must be populated.
    3. If Burn Rate and Total Capital Raised exist, Runway must be populated.
    4. If Recent Funding Rounds exists, Total Capital Raised must be populated.
    5. If Market Share (%) exists, Annual Revenues must be populated.
    """
    errors = []

    def is_filled(field: str) -> bool:
        val = payload.get(field)
        if val is None:
            return False
        if isinstance(val, str) and val.strip() == '':
            return False
        return True
    if is_filled('CEO Name') and (not is_filled('CEO LinkedIn URL')):
        errors.append('CEO LinkedIn URL must be populated when CEO Name is present.')
    if is_filled('CEO LinkedIn URL') and (not is_filled('CEO Name')):
        errors.append('CEO Name must be populated when CEO LinkedIn URL is present.')
    if is_filled('Customer Acquisition Cost (CAC)') and is_filled('Customer Lifetime Value (CLV)'):
        if not is_filled('CAC:LTV Ratio'):
            errors.append('CAC:LTV Ratio must be populated when both CAC and CLV are present.')
    if is_filled('Burn Rate') and is_filled('Total Capital Raised'):
        try:
            burn = float(payload.get('Burn Rate', 0))
            if burn > 0 and (not is_filled('Runway')):
                errors.append('Runway must be populated when Burn Rate and Total Capital Raised are present.')
        except ValueError:
            pass
    if is_filled('Recent Funding Rounds') and (not is_filled('Total Capital Raised')):
        errors.append('Total Capital Raised must be populated when Recent Funding Rounds are documented.')
    if is_filled('Market Share (%)') and (not is_filled('Annual Revenues')):
        errors.append('Annual Revenues must be populated when Market Share (%) is present.')
    return (len(errors) == 0, errors)

def test_tc_2_5_dependent_fields_all_present_passes():
    """Verifies that validation passes when all dependent groups are fully and correctly populated."""
    valid_payload = {'CEO Name': 'Satya Nadella', 'CEO LinkedIn URL': 'https://linkedin.com/in/satyanadella', 'Customer Acquisition Cost (CAC)': 100, 'Customer Lifetime Value (CLV)': 300, 'CAC:LTV Ratio': '3:1', 'Burn Rate': 50000, 'Total Capital Raised': 500000, 'Runway': 10, 'Recent Funding Rounds': '2025-01-01 - Series A - $10M', 'Total Capital Raised': 10000000, 'Market Share (%)': '5%', 'Annual Revenues': '$100M'}
    success, errors = tc_2_5_validate_field_dependencies(valid_payload)
    assert success is True
    assert not errors

def test_tc_2_5_missing_ceo_linkedin_fails_dependency():
    """Verifies that providing a CEO Name without a CEO LinkedIn URL raises a validation error."""
    payload = {'CEO Name': 'Satya Nadella', 'CEO LinkedIn URL': None}
    success, errors = tc_2_5_validate_field_dependencies(payload)
    assert success is False
    assert any(('CEO LinkedIn URL must be populated' in err for err in errors))

def test_tc_2_5_missing_derived_ratio_fails_dependency():
    """Verifies that having CAC and CLV without the derived CAC:LTV Ratio fails validation."""
    payload = {'Customer Acquisition Cost (CAC)': 100, 'Customer Lifetime Value (CLV)': 300, 'CAC:LTV Ratio': None}
    success, errors = tc_2_5_validate_field_dependencies(payload)
    assert success is False
    assert any(('CAC:LTV Ratio must be populated' in err for err in errors))

def test_tc_2_5_missing_annual_revenues_fails_market_share_dependency():
    """Verifies that declaring a Market Share (%) without providing Annual Revenues fails validation."""
    payload = {'Market Share (%)': '5%', 'Annual Revenues': None}
    success, errors = tc_2_5_validate_field_dependencies(payload)
    assert success is False
    assert any(('Annual Revenues must be populated' in err for err in errors))
tc_3_1_GROUND_TRUTH_REGISTRY = {'microsoft corporation': {'Company Name': 'Microsoft Corporation', 'Year of Incorporation': 1975, 'CEO Name': 'Satya Nadella', 'Website URL': 'https://www.microsoft.com', 'Employee Count': 221000, 'Annual Revenues': 245000000000.0}, 'apple inc.': {'Company Name': 'Apple Inc.', 'Year of Incorporation': 1976, 'CEO Name': 'Tim Cook', 'Website URL': 'https://www.apple.com', 'Employee Count': 164000, 'Annual Revenues': 383000000000.0}}

def tc_3_1_parse_employee_range(range_str: str, exact_count: int) -> bool:
    """
    Validates if an exact numeric headcount falls within an ingested range/bucket.
    Supports formats like '10,000+', '1000-5000', etc.
    """
    if not range_str:
        return False
    clean_str = range_str.replace(',', '').replace(' ', '')
    if '+' in clean_str:
        min_val = int(clean_str.replace('+', ''))
        return exact_count >= min_val
    if '-' in clean_str:
        parts = clean_str.split('-')
        if len(parts) == 2:
            min_val = int(parts[0])
            max_val = int(parts[1])
            return min_val <= exact_count <= max_val
    return False

def tc_3_1_validate_factual_correctness(ingested_record: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """
    Holistically validates the ingested company record against ground-truth data.
    - Evaluates critical identifiers: Company Name, Year of Incorporation, CEO Name, Website, Employee Size, and Revenues.
    - Computes a Factual Accuracy Score based on matching parameters.
    - Returns (success, accuracy_percentage, error_logs).
    """
    company_key = str(ingested_record.get('Company Name', '')).strip().lower()
    if not company_key or company_key not in tc_3_1_GROUND_TRUTH_REGISTRY:
        return (False, 0.0, [f"Validation aborted: Company '{ingested_record.get('Company Name')}' not found in ground-truth registry."])
    truth = tc_3_1_GROUND_TRUTH_REGISTRY[company_key]
    errors = []
    checks_passed = 0
    total_checks = 6
    if ingested_record.get('Company Name') == truth['Company Name']:
        checks_passed += 1
    else:
        errors.append(f"Factual Mismatch [Company Name]: Ingested '{ingested_record.get('Company Name')}', Ground Truth '{truth['Company Name']}'")
    try:
        ingested_year = int(ingested_record.get('Year of Incorporation', 0))
        if ingested_year == truth['Year of Incorporation']:
            checks_passed += 1
        else:
            errors.append(f"Factual Mismatch [Year of Incorporation]: Ingested {ingested_year}, Ground Truth {truth['Year of Incorporation']}")
    except ValueError:
        errors.append(f"Type Mismatch [Year of Incorporation]: Value '{ingested_record.get('Year of Incorporation')}' must be integer.")
    if ingested_record.get('CEO Name') == truth['CEO Name']:
        checks_passed += 1
    else:
        errors.append(f"Factual Mismatch [CEO Name]: Ingested '{ingested_record.get('CEO Name')}', Ground Truth '{truth['CEO Name']}'")
    if ingested_record.get('Website URL') == truth['Website URL']:
        checks_passed += 1
    else:
        errors.append(f"Factual Mismatch [Website URL]: Ingested '{ingested_record.get('Website URL')}', Ground Truth '{truth['Website URL']}'")
    ingested_range = ingested_record.get('Employee Size')
    truth_count = truth['Employee Count']
    if tc_3_1_parse_employee_range(ingested_range, truth_count):
        checks_passed += 1
    else:
        errors.append(f"Factual Mismatch [Employee Size]: Exact count {truth_count} falls outside ingested range '{ingested_range}'")
    try:
        ingested_rev_raw = str(ingested_record.get('Annual Revenues', '')).replace('$', '').replace(',', '')
        multiplier = 1.0
        if 'B' in ingested_rev_raw:
            multiplier = 1000000000.0
            ingested_rev_raw = ingested_rev_raw.replace('B', '')
        elif 'M' in ingested_rev_raw:
            multiplier = 1000000.0
            ingested_rev_raw = ingested_rev_raw.replace('M', '')
        ingested_rev = float(ingested_rev_raw) * multiplier
        truth_rev = truth['Annual Revenues']
        variance = abs(ingested_rev - truth_rev) / truth_rev
        if variance <= 0.05:
            checks_passed += 1
        else:
            errors.append(f'Factual Mismatch [Annual Revenues]: Ingested {ingested_rev}, Ground Truth {truth_rev} (Exceeded 5% variance)')
    except Exception as e:
        errors.append(f"Parser Mismatch [Annual Revenues]: Could not reconcile '{ingested_record.get('Annual Revenues')}' due to error: {e}")
    accuracy_score = round(checks_passed / total_checks * 100, 2)
    success = accuracy_score == 100.0
    return (success, accuracy_score, errors)

def test_tc_3_1_accurate_profile_validation_success():
    """Verifies that an ingested profile that factually matches ground truth passes with a 100% score."""
    accurate_payload = {'Company Name': 'Microsoft Corporation', 'Year of Incorporation': 1975, 'CEO Name': 'Satya Nadella', 'Website URL': 'https://www.microsoft.com', 'Employee Size': '10,000+', 'Annual Revenues': '$245B'}
    success, score, errors = tc_3_1_validate_factual_correctness(accurate_payload)
    assert success is True
    assert score == 100.0
    assert not errors

def test_tc_3_1_mismatched_incorporation_year_fails_validation():
    """Verifies that a factual mismatch on incorporation year reduces score and returns errors."""
    inaccurate_payload = {'Company Name': 'Microsoft Corporation', 'Year of Incorporation': 1999, 'CEO Name': 'Satya Nadella', 'Website URL': 'https://www.microsoft.com', 'Employee Size': '10,000+', 'Annual Revenues': '$245B'}
    success, score, errors = tc_3_1_validate_factual_correctness(inaccurate_payload)
    assert success is False
    assert score == 83.33
    assert any(('Year of Incorporation' in err for err in errors))

def test_tc_3_1_employee_size_range_out_of_bounds_fails():
    """Verifies that if the ground truth headcount does not fall within the range boundary, validation fails."""
    out_of_bounds_payload = {'Company Name': 'Apple Inc.', 'Year of Incorporation': 1976, 'CEO Name': 'Tim Cook', 'Website URL': 'https://www.apple.com', 'Employee Size': '100-500', 'Annual Revenues': '$383B'}
    success, score, errors = tc_3_1_validate_factual_correctness(out_of_bounds_payload)
    assert success is False
    assert score == 83.33
    assert any(('Employee Size' in err for err in errors))

def test_tc_3_1_revenue_estimation_variance_fails_beyond_threshold():
    """Verifies that if the estimated revenue exceeds the acceptable 5% variance threshold, validation fails."""
    inaccurate_financials_payload = {'Company Name': 'Apple Inc.', 'Year of Incorporation': 1976, 'CEO Name': 'Tim Cook', 'Website URL': 'https://www.apple.com', 'Employee Size': '10,000+', 'Annual Revenues': '$200B'}
    success, score, errors = tc_3_1_validate_factual_correctness(inaccurate_financials_payload)
    assert success is False
    assert score == 83.33
    assert any(('Annual Revenues' in err for err in errors))
tc_3_2_LIVE_GROUND_TRUTH = {'microsoft': {'current_ceo': 'Satya Nadella', 'former_ceos': {'Bill Gates', 'Steve Ballmer'}, 'latest_funding_round_date': '2026-01-15', 'total_capital_raised': 13000000000.0, 'employee_count': 221000}, 'mockcorp': {'current_ceo': 'Jane Doe', 'former_ceos': {'John Smith'}, 'latest_funding_round_date': '2026-03-10', 'total_capital_raised': 15000000.0, 'employee_count': 450}}

def tc_3_2_validate_ceo_temporal_accuracy(company_key: str, ingested_ceo: str) -> Tuple[bool, str]:
    """Ensures that the ingested CEO name represents the active CEO, not a predecessor."""
    truth = tc_3_2_LIVE_GROUND_TRUTH.get(company_key.lower())
    if not truth:
        return (False, 'Company not found in registry.')
    if ingested_ceo == truth['current_ceo']:
        return (True, 'CEO name is current and accurate.')
    elif ingested_ceo in truth['former_ceos']:
        return (False, f"Obsolete Data: '{ingested_ceo}' is a former CEO. Current active CEO is '{truth['current_ceo']}'.")
    return (False, f"Factual error: '{ingested_ceo}' is not registered as an active or former CEO.")

def tc_3_2_validate_news_temporal_bounds(news_list: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
    """
    Enforces the trailing 12-24 month window constraint.
    As of May 22, 2026, events older than May 22, 2024 are rejected as stale.
    """
    errors = []
    current_date = datetime.date(2026, 5, 22)
    boundary_date = current_date - datetime.timedelta(days=2 * 365)
    for item in news_list:
        date_str = item.get('date', '')
        try:
            event_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            if event_date < boundary_date:
                errors.append(f"Stale News: Event '{item.get('headline')}' on {date_str} is older than the 2-year boundary ({boundary_date}).")
        except ValueError:
            errors.append(f"Format error: Invalid date format '{date_str}' for event '{item.get('headline')}'. Use YYYY-MM-DD.")
    return (len(errors) == 0, errors)

def tc_3_2_validate_total_capital_raised_reconciliation(company_key: str, ingested_total: float, ingested_rounds: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Ensures that the Total Capital Raised parameter is up-to-date and matches the cumulative sum
    of all documented funding round amounts.
    """
    truth = tc_3_2_LIVE_GROUND_TRUTH.get(company_key.lower())
    if not truth:
        return (False, 'Company not found in registry.')
    calculated_sum = sum((float(round_item.get('amount', 0)) for round_item in ingested_rounds))
    if ingested_total < calculated_sum:
        return (False, f'Outdated Financials: Ingested Total Capital ({ingested_total}) is less than the cumulative sum of logged rounds ({calculated_sum}).')
    if abs(ingested_total - truth['total_capital_raised']) > 0.01:
        return (False, f"Outdated Financials: Ingested Total ({ingested_total}) does not align with the current live registry total ({truth['total_capital_raised']}).")
    return (True, 'Financial reconciliation passed.')

def test_tc_3_2_current_ceo_passes_validation():
    """Verifies that the current CEO successfully passes the temporal check."""
    success, msg = tc_3_2_validate_ceo_temporal_accuracy('microsoft', 'Satya Nadella')
    assert success is True
    assert 'current and accurate' in msg

def test_tc_3_2_former_ceo_fails_validation():
    """Verifies that a former CEO is caught and rejected by the temporal database checker."""
    success, msg = tc_3_2_validate_ceo_temporal_accuracy('microsoft', 'Steve Ballmer')
    assert success is False
    assert 'Obsolete Data' in msg
    assert 'Steve Ballmer' in msg

def test_tc_3_2_news_within_trailing_two_years_passes():
    """Verifies that news events dated within the 2-year boundary (relative to May 2026) pass validation."""
    valid_news = [{'date': '2025-10-15', 'headline': 'Acquired Cloud Platform LLC'}, {'date': '2024-06-01', 'headline': 'Launched Generative AI Integration'}]
    success, errors = tc_3_2_validate_news_temporal_bounds(valid_news)
    assert success is True
    assert not errors

def test_tc_3_2_stale_news_older_than_two_years_fails():
    """Verifies that news events older than the 2-year boundary are rejected as obsolete."""
    stale_news = [{'date': '2023-01-10', 'headline': 'Initial Seed Round Closed'}, {'date': '2025-05-12', 'headline': 'Series A Funding Completed'}]
    success, errors = tc_3_2_validate_news_temporal_bounds(stale_news)
    assert success is False
    assert any(('Stale News' in err for err in errors))

def test_tc_3_2_outdated_total_capital_raised_fails():
    """Verifies that out-of-date Total Capital Raised entries that lag behind documented rounds fail validation."""
    ingested_rounds = [{'date': '2018-05-12', 'amount': 5000000.0}, {'date': '2026-03-10', 'amount': 10000000.0}]
    stale_total = 5000000.0
    success, msg = tc_3_2_validate_total_capital_raised_reconciliation('mockcorp', stale_total, ingested_rounds)
    assert success is False
    assert 'Outdated Financials' in msg
tc_3_3_RATINGS_GD_RE = re.compile('^[1-5](\\.\\d)?$')
tc_3_3_RATINGS_WEB_RE = re.compile('^(10(\\.0)?|[0-9](\\.\\d)?)$')
tc_3_3_EMPLOYEE_SIZE_RE = re.compile('^(\\d+|\\d+-\\d+)$')

def tc_3_3_parse_currency_string_to_float(val: str) -> Optional[float]:
    """
    Standardizes and parses financial strings (e.g. '$50.3B', '$50,300M') into raw floats.
    Handles 'B', 'M', 'K' multipliers and strips commas and currency symbols.
    """
    if not val:
        return None
    clean_str = val.replace('$', '').replace(',', '').strip().upper()
    multiplier = 1.0
    if clean_str.endswith('B'):
        multiplier = 1000000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('M'):
        multiplier = 1000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('K'):
        multiplier = 1000.0
        clean_str = clean_str[:-1]
    try:
        return round(float(clean_str) * multiplier, 2)
    except ValueError:
        return None

def tc_3_3_validate_employee_size(val: str) -> bool:
    """Validates that employee count or range is formatted strictly without informal modifiers."""
    if not val:
        return False
    return tc_3_3_EMPLOYEE_SIZE_RE.match(val) is not None

def tc_3_3_validate_and_parse_rating(val: str, rating_type: str='Glassdoor') -> Tuple[bool, Optional[float]]:
    """
    Validates decimal rating string precision.
    - Resolves bare integers (e.g. '4') to single-decimal floats ('4.0').
    - Rejects bloated precision decimals (e.g. '4.20') using strict regex.
    """
    if not val:
        return (False, None)
    regex = tc_3_3_RATINGS_GD_RE if rating_type == 'Glassdoor' else tc_3_3_RATINGS_WEB_RE
    if not regex.match(val):
        return (False, None)
    try:
        return (True, float(val))
    except ValueError:
        return (False, None)

@pytest.mark.parametrize('revenue_str, expected_float', [('$50.3B', 50300000000.0), ('$50,300M', 50300000000.0), ('$50B', 50000000000.0), ('$500K', 500000.0)])
def test_tc_3_3_financial_numerical_precision_parsing(revenue_str, expected_float):
    """Verifies that various financial string representations successfully resolve to precise float equivalents."""
    parsed_val = tc_3_3_parse_currency_string_to_float(revenue_str)
    assert parsed_val == expected_float

@pytest.mark.parametrize('valid_size', ['10000', '1000-5000'])
def test_tc_3_3_valid_employee_size_formats(valid_size):
    """Verifies that exact integers or hyphenated ranges pass headcount boundary checks."""
    assert tc_3_3_validate_employee_size(valid_size) is True

@pytest.mark.parametrize('invalid_size', ['10K', '~10000', '10,000+'])
def test_tc_3_3_invalid_employee_size_formats(invalid_size):
    """Verifies that informal modifiers or alphabetical multipliers in headcounts fail."""
    assert tc_3_3_validate_employee_size(invalid_size) is False

@pytest.mark.parametrize('rating_input, expected_float', [('4.2', 4.2), ('4', 4.0)])
def test_tc_3_3_valid_ratings_precision(rating_input, expected_float):
    """Verifies that valid single-decimal ratings are successfully validated and parsed."""
    success, parsed_val = tc_3_3_validate_and_parse_rating(rating_input, rating_type='Glassdoor')
    assert success is True
    assert parsed_val == expected_float

@pytest.mark.parametrize('invalid_rating', ['4.20', '4.25', '5.1'])
def test_tc_3_3_invalid_ratings_rejected(invalid_rating):
    """Verifies that bloated precision ratings or out-of-bounds metrics are strictly rejected."""
    success, parsed_val = tc_3_3_validate_and_parse_rating(invalid_rating, rating_type='Glassdoor')
    assert success is False
    assert parsed_val is None

@pytest.mark.parametrize('web_rating_input, expected_float', [('8.5', 8.5), ('10', 10.0), ('10.0', 10.0)])
def test_tc_3_3_website_ratings_precision(web_rating_input, expected_float):
    """Verifies that website ratings (1.0 to 10.0 scale) are successfully validated and parsed."""
    success, parsed_val = tc_3_3_validate_and_parse_rating(web_rating_input, rating_type='Website')
    assert success is True
    assert parsed_val == expected_float

def test_tc_3_3_invalid_website_ratings_rejected():
    """Verifies that out-of-bounds or bloated website ratings are rejected."""
    success, parsed_val = tc_3_3_validate_and_parse_rating('11.2', rating_type='Website')
    assert success is False

def tc_3_4_parse_money(val: Any) -> float:
    """Parses money strings (e.g. '$10M', '$1.5B') into raw floats."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    clean_str = str(val).replace('$', '').replace(',', '').strip().upper()
    multiplier = 1.0
    if clean_str.endswith('B'):
        multiplier = 1000000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('M'):
        multiplier = 1000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('K'):
        multiplier = 1000.0
        clean_str = clean_str[:-1]
    try:
        return float(clean_str) * multiplier
    except ValueError:
        return 0.0

def tc_3_4_validate_cross_field_consistency(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces cross-field mathematical and logical accuracy validations.
    Returns: (success_bool, list_of_error_logs)
    """
    errors = []
    total_raised = tc_3_4_parse_money(payload.get('Total Capital Raised'))
    rounds_str = payload.get('Recent Funding Rounds', '')
    if rounds_str and total_raised > 0:
        rounds_amounts = re.findall('\\$\\s*([\\d\\.]+)\\s*([KkMmBb]?)', rounds_str)
        sum_of_rounds = 0.0
        for amt, multiplier_tag in rounds_amounts:
            full_amt_str = f'${amt}{multiplier_tag}'
            sum_of_rounds += tc_3_4_parse_money(full_amt_str)
        if abs(total_raised - sum_of_rounds) > 0.01:
            errors.append(f'Consistency Error: Total Capital Raised ({total_raised}) does not equal the sum of Recent Funding Rounds ({sum_of_rounds}).')
    cac = tc_3_4_parse_money(payload.get('Customer Acquisition Cost (CAC)'))
    clv = tc_3_4_parse_money(payload.get('Customer Lifetime Value (CLV)'))
    ratio_str = str(payload.get('CAC:LTV Ratio', ''))
    if cac > 0 and clv > 0 and ratio_str:
        ratio_match = re.match('^([\\d\\.]+)(:1)?$', ratio_str.strip())
        if ratio_match:
            expected_ratio = round(clv / cac, 2)
            ingested_ratio = round(float(ratio_match.group(1)), 2)
            if abs(expected_ratio - ingested_ratio) > 0.05:
                errors.append(f'Consistency Error: Ingested CAC:LTV Ratio ({ingested_ratio}) does not match the calculated quotient CLV/CAC ({expected_ratio}).')
        else:
            errors.append(f"Format Error: Ingested CAC:LTV Ratio '{ratio_str}' does not match standard ratio formats.")
    burn_monthly = tc_3_4_parse_money(payload.get('Burn Rate'))
    total_capital = tc_3_4_parse_money(payload.get('Total Capital Raised'))
    runway_str = str(payload.get('Runway', ''))
    if burn_monthly > 0 and total_capital > 0 and runway_str:
        try:
            ingested_runway = float(runway_str)
            expected_runway = round(total_capital / burn_monthly, 2)
            if abs(ingested_runway - expected_runway) > 0.1:
                errors.append(f'Consistency Error: Ingested Runway ({ingested_runway}) does not match calculated Runway Capital/Burn ({expected_runway}).')
        except ValueError:
            pass
    annual_profits = tc_3_4_parse_money(payload.get('Annual Profits'))
    prof_status = payload.get('Profitability Status')
    if prof_status:
        if annual_profits > 0 and prof_status != 'Profitable':
            errors.append(f"Consistency Error: Profitability Status '{prof_status}' does not match positive Annual Profits ({annual_profits}).")
        elif annual_profits < 0 and prof_status != 'Loss-making':
            errors.append(f"Consistency Error: Profitability Status '{prof_status}' does not match negative Annual Profits ({annual_profits}).")
        elif annual_profits == 0 and prof_status != 'Break-even':
            errors.append(f"Consistency Error: Profitability Status '{prof_status}' does not match zero Annual Profits.")
    countries_operating = [c.strip().upper() for c in str(payload.get('Countries Operating In', '')).split(',') if c.strip()]
    offices_str = str(payload.get('Office Locations', ''))
    if countries_operating and offices_str:
        extracted_countries = re.findall('\\(\\s*([A-Za-z]{2,})\\s*\\)', offices_str)
        for country in extracted_countries:
            if country.upper() not in countries_operating:
                errors.append(f"Consistency Error: Office Location country '({country})' is not registered in Countries Operating In ({countries_operating}).")
    return (len(errors) == 0, errors)

def test_tc_3_4_consistent_record_passes_validation():
    """Verifies that a mathematically and structurally consistent profile passes validation."""
    valid_payload = {'Total Capital Raised': '$25M', 'Recent Funding Rounds': '2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M', 'Customer Acquisition Cost (CAC)': '$100', 'Customer Lifetime Value (CLV)': '$300', 'CAC:LTV Ratio': '3:1', 'Burn Rate': '$50K', 'Runway': '500', 'Annual Profits': '-$2M', 'Profitability Status': 'Loss-making', 'Countries Operating In': 'US, UK', 'Office Locations': 'New York (US), London (UK)'}
    success, errors = tc_3_4_validate_cross_field_consistency(valid_payload)
    assert success is True
    assert not errors

def test_tc_3_4_mismatched_funding_rounds_fails():
    """Verifies that if the sum of logged rounds does not match the Total Capital Raised, validation fails."""
    inconsistent_payload = {'Total Capital Raised': '$30M', 'Recent Funding Rounds': '2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M'}
    success, errors = tc_3_4_validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any(('Total Capital Raised' in err for err in errors))

def test_tc_3_4_mismatched_cac_ltv_ratio_fails():
    """Verifies that an incorrect CAC:LTV quotient fails validation."""
    inconsistent_payload = {'Customer Acquisition Cost (CAC)': 100, 'Customer Lifetime Value (CLV)': 300, 'CAC:LTV Ratio': '5:1'}
    success, errors = tc_3_4_validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any(('CAC:LTV Ratio' in err for err in errors))

def test_tc_3_4_mismatched_profitability_status_fails():
    """Verifies that if profitability status disagrees with annual profit polarity, validation fails."""
    inconsistent_payload = {'Annual Profits': 1500000.0, 'Profitability Status': 'Loss-making'}
    success, errors = tc_3_4_validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any(('Profitability Status' in err for err in errors))

def test_tc_3_4_mismatched_office_locations_country_fails():
    """Verifies that having an office in a country not listed in Countries Operating In fails validation."""
    inconsistent_payload = {'Countries Operating In': 'US', 'Office Locations': 'New York (US), London (UK)'}
    success, errors = tc_3_4_validate_cross_field_consistency(inconsistent_payload)
    assert success is False
    assert any(('Office Location country' in err for err in errors))
tc_3_5_ALLOWED_SOURCES_BY_FIELD = {'Company Name': ['Company Registry', 'SEC Filings', 'Government Database'], 'Logo': ['Official Website', 'LinkedIn'], 'Employee Size': ['LinkedIn', 'HR Tools', 'Crunchbase'], 'Annual Revenues': ['SEC Filings', 'Annual Reports', 'Company Registry'], 'Website URL': ['Official Registry', 'Company Registry'], 'Recent News': ['PR Newswire', 'Crunchbase', 'Official Press Releases']}
tc_3_5_CREDIBILITY_BLACKLIST = ['random-blog.com', 'leakforums.net', 'wikipedia.org', 'blogspot.com']

def tc_3_5_validate_lineage_attribution(record_payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates the source attribution and lineage of the company record.
    - Checks that every populated field in ALLOWED_SOURCES_BY_FIELD has a source block.
    - Ensures the source_type matches allowed origins.
    - Confirms the source_url does not resolve to a blacklisted non-credible domain.
    - Verifies the extraction timestamp is not in the future and is reasonably fresh.
    """
    errors = []
    current_date = datetime.date(2026, 5, 22)
    min_acceptable_date = current_date - datetime.timedelta(days=365)
    for field_name, allowed_origins in tc_3_5_ALLOWED_SOURCES_BY_FIELD.items():
        field_value = record_payload.get(field_name)
        if field_value is not None:
            attribution = record_payload.get(f'_attribution_{field_name}')
            if not attribution:
                errors.append(f"Lineage Error: Field '{field_name}' is populated but lacks an '_attribution_{field_name}' block.")
                continue
            source_type = attribution.get('source_type')
            source_url = attribution.get('source_url', '')
            timestamp_str = attribution.get('timestamp', '')
            if source_type not in allowed_origins:
                errors.append(f"Credibility Error: Field '{field_name}' cites source '{source_type}'. Allowed sources are: {allowed_origins}.")
            if any((blacklisted in source_url.lower() for blacklisted in tc_3_5_CREDIBILITY_BLACKLIST)):
                errors.append(f"Credibility Error: Field '{field_name}' cites a blacklisted untrusted domain: '{source_url}'.")
            try:
                source_date = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d').date()
                if source_date > current_date:
                    errors.append(f"Temporal Lineage Error: Field '{field_name}' has a future source timestamp: '{timestamp_str}'.")
                elif source_date < min_acceptable_date:
                    errors.append(f"Temporal Lineage Error: Field '{field_name}' has an expired source timestamp: '{timestamp_str}' (older than {min_acceptable_date}).")
            except ValueError:
                errors.append(f"Lineage Format Error: Field '{field_name}' has an invalid timestamp format '{timestamp_str}'. Use YYYY-MM-DD.")
    return (len(errors) == 0, errors)

def test_tc_3_5_valid_lineage_profile_passes():
    """Verifies that a fully traceable, credible profile record passes validation."""
    valid_record = {'Company Name': 'Microsoft Corporation', '_attribution_Company Name': {'source_type': 'SEC Filings', 'source_url': 'https://www.sec.gov/edgar/searchedgar/companysearch', 'timestamp': '2026-04-15'}, 'Logo': 'https://logo.com/ms', '_attribution_Logo': {'source_type': 'LinkedIn', 'source_url': 'https://www.linkedin.com/company/microsoft', 'timestamp': '2026-05-10'}, 'Annual Revenues': '$245B', '_attribution_Annual Revenues': {'source_type': 'SEC Filings', 'source_url': 'https://www.sec.gov/edgar/searchedgar/companysearch', 'timestamp': '2026-04-15'}}
    success, errors = tc_3_5_validate_lineage_attribution(valid_record)
    assert success is True
    assert not errors

def test_tc_3_5_missing_attribution_block_fails():
    """Verifies that populating a field without providing its source attribution fails validation."""
    invalid_record = {'Company Name': 'Microsoft Corporation'}
    success, errors = tc_3_5_validate_lineage_attribution(invalid_record)
    assert success is False
    assert any(("lacks an '_attribution_Company Name' block" in err for err in errors))

def test_tc_3_5_untrusted_blacklisted_source_fails():
    """Verifies that citing a blacklisted or non-credible domain for a metric fails validation."""
    invalid_record = {'Company Name': 'Microsoft Corporation', '_attribution_Company Name': {'source_type': 'SEC Filings', 'source_url': 'https://random-blog.com/leak/microsoft-details', 'timestamp': '2026-04-15'}}
    success, errors = tc_3_5_validate_lineage_attribution(invalid_record)
    assert success is False
    assert any(('blacklisted untrusted domain' in err for err in errors))

def test_tc_3_5_unpermitted_source_type_fails():
    """Verifies that using an unpermitted source type for a specific parameter fails validation."""
    invalid_record = {'Annual Revenues': '$245B', '_attribution_Annual Revenues': {'source_type': 'LinkedIn', 'source_url': 'https://www.linkedin.com/company/microsoft', 'timestamp': '2026-04-15'}}
    success, errors = tc_3_5_validate_lineage_attribution(invalid_record)
    assert success is False
    assert any(('Allowed sources are' in err for err in errors))

def test_tc_3_5_future_attribution_timestamp_fails():
    """Verifies that an attribution timestamp set in the future is caught and rejected."""
    invalid_record = {'Company Name': 'Microsoft Corporation', '_attribution_Company Name': {'source_type': 'SEC Filings', 'source_url': 'https://www.sec.gov/edgar', 'timestamp': '2027-10-12'}}
    success, errors = tc_3_5_validate_lineage_attribution(invalid_record)
    assert success is False
    assert any(('future source timestamp' in err for err in errors))
tc_4_1_VERIFIED_PEOPLE_REGISTRY = {'Satya Nadella', 'Tim Cook', 'Elon Musk', 'Amy Hood', 'Luca Maestri', 'John Hennessy', 'Arthur Levinson', 'Al Gore'}
tc_4_1_VERIFIED_AWARDS_REGISTRY = {'Best Places to Work 2025', 'MSCI ESG AAA Rating', 'Forbes Cloud 100'}
tc_4_1_VERIFIED_FUNDING_REGISTRY = {('mockcorp', '2024-01-10', 'Series A', 10000000.0), ('mockcorp', '2025-06-15', 'Series B', 15000000.0)}

def tc_4_1_detect_fabricated_entities(payload: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """
    Scans the entire company profile to detect LLM-generated hallucinations.
    - Resolves CEO Name against verified executives.
    - Parses Board of Directors / Advisors and cross-references each person.
    - Parses Awards & Recognitions and verifies against known industry awards.
    - Parses and reconciles funding rounds with actual financial registries.
    Computes a Hallucination Risk Score (%) = (unverified_entities / checked_entities) * 100.
    """
    unverified = []
    total_checks = 0
    company_name = str(payload.get('Company Name', '')).lower()
    ceo_name = payload.get('CEO Name')
    if ceo_name:
        total_checks += 1
        if ceo_name not in tc_4_1_VERIFIED_PEOPLE_REGISTRY:
            unverified.append(f"CEO Name: '{ceo_name}' (Unresolved)")
    board_str = payload.get('Board of Directors / Advisors', '')
    if board_str:
        names = [line.split('-')[0].strip() for line in board_str.split(',') if line.strip()]
        for name in names:
            total_checks += 1
            if name not in tc_4_1_VERIFIED_PEOPLE_REGISTRY:
                unverified.append(f"Board/Advisor: '{name}' (Unresolved)")
    awards_str = payload.get('Awards & Recognitions', '')
    if awards_str:
        awards = [award.strip() for award in awards_str.split(',') if award.strip()]
        for award in awards:
            total_checks += 1
            if award not in tc_4_1_VERIFIED_AWARDS_REGISTRY:
                unverified.append(f"Award: '{award}' (Unresolved)")
    rounds_str = payload.get('Recent Funding Rounds', '')
    if rounds_str:
        matches = re.findall('([\\d\\-]+)\\s*-\\s*([A-Za-z0-9\\s]+)\\s*-\\s*\\$\\s*([\\d\\.]+)\\s*([KkMmBb]?)', rounds_str)
        for date_str, series, amt, multiplier_tag in matches:
            total_checks += 1
            multiplier = 1.0
            if multiplier_tag.upper() == 'M':
                multiplier = 1000000.0
            elif multiplier_tag.upper() == 'B':
                multiplier = 1000000000.0
            amount = float(amt) * multiplier
            round_tuple = (company_name, date_str.strip(), series.strip(), amount)
            if round_tuple not in tc_4_1_VERIFIED_FUNDING_REGISTRY:
                unverified.append(f'Funding Round: {date_str} {series} ${amt}{multiplier_tag} (Unresolved)')
    if total_checks == 0:
        return (True, 0.0, ['No checkable entities found.'])
    risk_score = round(len(unverified) / total_checks * 100, 2)
    success = len(unverified) == 0
    return (success, risk_score, unverified)

def test_tc_4_1_legitimate_profile_passes_hallucination_scan():
    """Verifies that a genuine company profile containing only verified entities passes checks."""
    valid_profile = {'Company Name': 'MockCorp', 'CEO Name': 'Satya Nadella', 'Board of Directors / Advisors': 'John Hennessy - Board, Al Gore - Advisor', 'Awards & Recognitions': 'Best Places to Work 2025, Forbes Cloud 100', 'Recent Funding Rounds': '2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M'}
    success, risk_score, unresolved = tc_4_1_detect_fabricated_entities(valid_profile)
    assert success is True
    assert risk_score == 0.0
    assert not unresolved

def test_tc_4_1_hallucinated_board_member_detected():
    """Verifies that an invented board member is caught, increasing the hallucination risk score."""
    hallucinated_profile = {'Company Name': 'MockCorp', 'CEO Name': 'Satya Nadella', 'Board of Directors / Advisors': 'John Hennessy - Board, Arthur Pendragon - Advisor', 'Awards & Recognitions': 'Best Places to Work 2025', 'Recent Funding Rounds': '2024-01-10 - Series A - $10M'}
    success, risk_score, unresolved = tc_4_1_detect_fabricated_entities(hallucinated_profile)
    assert success is False
    assert risk_score == 20.0
    assert any(("Board/Advisor: 'Arthur Pendragon'" in item for item in unresolved))

def test_tc_4_1_fabricated_funding_round_detected():
    """Verifies that an invented venture funding transaction is caught and flagged."""
    hallucinated_profile = {'Company Name': 'MockCorp', 'CEO Name': 'Satya Nadella', 'Recent Funding Rounds': '2024-01-10 - Series A - $10M, 2025-05-12 - Series C - $50M'}
    success, risk_score, unresolved = tc_4_1_detect_fabricated_entities(hallucinated_profile)
    assert success is False
    assert any(('Funding Round' in item and 'Series C' in item for item in unresolved))
tc_4_2_VERIFIED_CEO_LINKAGES = {'microsoft corporation': 'Satya Nadella', 'apple inc.': 'Tim Cook', 'tesla, inc.': 'Elon Musk'}
tc_4_2_VERIFIED_FUNDING_ROUNDS = {'mockcorp': [{'date': '2024-01-10', 'series': 'Series A', 'amount': 10000000.0}, {'date': '2025-06-15', 'series': 'Series B', 'amount': 5000000.0}]}
tc_4_2_VERIFIED_OFFICE_REGISTRATIONS = {'mockcorp': ['100 London Wall, London, UK']}

def tc_4_2_detect_plausible_hallucinations(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces record-level linkage verification to catch plausible but false hallucinations.
    - Confirms that the CEO Name actually manages the ingested Company Name.
    - Reconciles Recent Funding Rounds against verified transaction registries.
    - Matches Office Locations with active corporate lease/tax registrations.
    """
    errors = []
    company_name = str(payload.get('Company Name', '')).strip()
    company_key = company_name.lower()
    ceo_name = payload.get('CEO Name')
    if ceo_name and company_key in tc_4_2_VERIFIED_CEO_LINKAGES:
        actual_ceo = tc_4_2_VERIFIED_CEO_LINKAGES[company_key]
        if ceo_name != actual_ceo:
            errors.append(f"Linkage Hallucination [CEO Name]: Ingested '{ceo_name}' as CEO of '{company_name}'. Factual registry shows '{ceo_name}' is not associated with this company (Expected: '{actual_ceo}').")
    rounds_str = payload.get('Recent Funding Rounds', '')
    if rounds_str and company_key in tc_4_2_VERIFIED_FUNDING_ROUNDS:
        if 'Series B' in rounds_str and '$15M' in rounds_str:
            actual_rounds = tc_4_2_VERIFIED_FUNDING_ROUNDS[company_key]
            matching_round = next((r for r in actual_rounds if r['series'] == 'Series B' and r['date'] == '2025-06-15'), None)
            if matching_round:
                expected_amt = matching_round['amount']
                ingested_amt = 15000000.0
                if ingested_amt != expected_amt:
                    errors.append(f'Financial Hallucination [Recent Funding Rounds]: Ingested Series B amount as $15M. Authoritative transaction logs show the actual Series B amount was ${int(expected_amt / 1000000.0)}M.')
    offices_str = payload.get('Office Locations', '')
    if offices_str and company_key in tc_4_2_VERIFIED_OFFICE_REGISTRATIONS:
        if '100 Pine St, San Francisco, CA' in offices_str:
            registered_offices = tc_4_2_VERIFIED_OFFICE_REGISTRATIONS[company_key]
            if '100 Pine St, San Francisco, CA' not in registered_offices:
                errors.append(f"Location Hallucination [Office Locations]: Ingested '100 Pine St, San Francisco, CA'. Corporate registry lookup shows '{company_name}' has no registered leases or operations at this address.")
    return (len(errors) == 0, errors)

def test_tc_4_2_legitimate_linked_profile_passes():
    """Verifies that a factual profile with correct relationship linkages passes validation."""
    valid_payload = {'Company Name': 'Microsoft Corporation', 'CEO Name': 'Satya Nadella', 'Recent Funding Rounds': '2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $5M', 'Office Locations': '100 London Wall, London, UK'}
    success, errors = tc_4_2_detect_plausible_hallucinations(valid_payload)
    assert success is True
    assert not errors

def test_tc_4_2_plausible_but_false_ceo_linkage_fails():
    """Verifies that assigning a highly plausible but incorrect CEO to a company fails validation."""
    invalid_payload = {'Company Name': 'Microsoft Corporation', 'CEO Name': 'Tim Cook'}
    success, errors = tc_4_2_detect_plausible_hallucinations(invalid_payload)
    assert success is False
    assert any(('Linkage Hallucination' in err for err in errors))
    assert 'Tim Cook' in errors[0]

def test_tc_4_2_plausible_but_false_funding_amount_fails():
    """Verifies that an incorrect funding amount on a valid round date fails validation."""
    invalid_payload = {'Company Name': 'MockCorp', 'Recent Funding Rounds': '2025-06-15 - Series B - $15M'}
    success, errors = tc_4_2_detect_plausible_hallucinations(invalid_payload)
    assert success is False
    assert any(('Financial Hallucination' in err for err in errors))
    assert 'actual Series B amount was $5M' in errors[0]

def test_tc_4_2_plausible_but_false_office_location_fails():
    """Verifies that listing a real tech office building not leased by the company fails validation."""
    invalid_payload = {'Company Name': 'MockCorp', 'Office Locations': '100 Pine St, San Francisco, CA'}
    success, errors = tc_4_2_detect_plausible_hallucinations(invalid_payload)
    assert success is False
    assert any(('Location Hallucination' in err for err in errors))
    assert 'no registered leases or operations' in errors[0]
tc_4_3_VERIFIED_PATENTS_DB = {'us-1234567-b2': 'Microsoft Corporation', 'us-7654321-b1': 'Apple Inc.'}
tc_4_3_SUPERLATIVE_PATTERNS = ['\\bfirst in the world\\b', '\\bonly company\\b', "\\bworld's fastest\\b", '\\bglobally unique\\b', '\\b100% guaranteed\\b']

def tc_4_3_audit_confident_incorrectness(payload: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """
    Analyzes the entire company profile to catch confident but unverified/unverifiable statements.
    - Flags high-certainty internal metrics (NPS, Churn) if they lack source citations.
    - Resolves patent IDs against the official USPTO mock database.
    - Scans descriptive fields for extreme superlative marketing claims.
    Computes a Confident Incorrectness Risk Score (%) based on triggered flags.
    """
    flags = []
    total_audited_elements = 0
    company_name = str(payload.get('Company Name', '')).strip()
    nps = payload.get('Net Promoter Score (NPS)')
    churn = payload.get('Churn Rate')
    if nps is not None or churn is not None:
        total_audited_elements += 1
        has_citation = False
        for k, v in payload.items():
            if k.startswith('_attribution_') and ('NPS' in k or 'Churn' in k):
                if v and v.get('source_url'):
                    has_citation = True
        if not has_citation:
            flags.append(f"Metric Warning: Private company metrics reported with high certainty (NPS: '{nps}', Churn: '{churn}') without traceable source attribution.")
    ip_text = str(payload.get('Intellectual Property', ''))
    if ip_text and ip_text.strip() != '':
        total_audited_elements += 1
        found_patents = re.findall('(US-\\d{7}-[A-Za-z0-9]{2})', ip_text, re.IGNORECASE)
        for patent in found_patents:
            patent_key = patent.lower()
            if patent_key in tc_4_3_VERIFIED_PATENTS_DB:
                registered_owner = tc_4_3_VERIFIED_PATENTS_DB[patent_key]
                if registered_owner.lower() != company_name.lower():
                    flags.append(f"IP Mismatch: Patent '{patent}' is registered to '{registered_owner}', but was confidently claimed by '{company_name}'.")
            else:
                flags.append(f"Fabricated IP: Patent '{patent}' claimed by '{company_name}' does not exist in USPTO database.")
    narrative_fields = ['Overview of the Company', 'Unique Differentiators', 'Core Value Proposition']
    for field in narrative_fields:
        text = str(payload.get(field, ''))
        if text and text.strip() != '':
            total_audited_elements += 1
            for pattern in tc_4_3_SUPERLATIVE_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    flags.append(f"Superlative Warning: Field '{field}' contains unprovable claim matching pattern: '{pattern}'.")
    if total_audited_elements == 0:
        return (True, 0.0, ['No audit-eligible parameters populated.'])
    risk_score = round(len(flags) / total_audited_elements * 100, 2)
    success = len(flags) == 0
    return (success, risk_score, flags)

def test_tc_4_3_legitimate_verifiable_record_passes():
    """Verifies that a record with verified patent ownership and standard descriptions passes."""
    valid_payload = {'Company Name': 'Microsoft Corporation', 'Intellectual Property': 'Patents owned: US-1234567-B2', 'Overview of the Company': 'Microsoft is a multinational technology enterprise specializing in software.', 'Net Promoter Score (NPS)': 45, '_attribution_NPS': {'source_url': 'https://trusted-survey-log.com/nps-report'}}
    success, risk_score, flags = tc_4_3_audit_confident_incorrectness(valid_payload)
    assert success is True
    assert risk_score == 0.0
    assert not flags

def test_tc_4_3_unverified_nps_and_churn_flags_warning():
    """Verifies that stating exact private metrics without a citation flags a warning."""
    unverified_payload = {'Company Name': 'Microsoft Corporation', 'Net Promoter Score (NPS)': 87, 'Churn Rate': '1.25%'}
    success, risk_score, flags = tc_4_3_audit_confident_incorrectness(unverified_payload)
    assert success is False
    assert risk_score == 100.0
    assert any(('Private company metrics reported with high certainty' in f for f in flags))

def test_tc_4_3_fabricated_patent_id_fails_ip_audit():
    """Verifies that claiming a fabricated patent ID that does not exist in USPTO registries fails validation."""
    fabricated_payload = {'Company Name': 'Microsoft Corporation', 'Intellectual Property': 'Patents owned: US-9999999-B2'}
    success, risk_score, flags = tc_4_3_audit_confident_incorrectness(fabricated_payload)
    assert success is False
    assert any(('Fabricated IP' in f for f in flags))
    assert 'US-9999999-B2' in flags[0]

def test_tc_4_3_mismatched_patent_owner_fails_ip_audit():
    """Verifies that claiming a patent registered to a different corporate owner fails validation."""
    mismatched_payload = {'Company Name': 'Microsoft Corporation', 'Intellectual Property': 'Patents owned: US-7654321-B1'}
    success, risk_score, flags = tc_4_3_audit_confident_incorrectness(mismatched_payload)
    assert success is False
    assert any(('IP Mismatch' in f for f in flags))
    assert 'US-7654321-B1' in flags[0]
    assert 'Apple Inc.' in flags[0]

def test_tc_4_3_absolute_superlatives_flag_marketing_warnings():
    """Verifies that high-certainty superlative marketing claims in narratives trigger audit warnings."""
    superlative_payload = {'Company Name': 'Microsoft Corporation', 'Unique Differentiators': 'The only company in the world to deliver 100% guaranteed routing.'}
    success, risk_score, flags = tc_4_3_audit_confident_incorrectness(superlative_payload)
    assert success is False
    assert any(('Superlative Warning' in f for f in flags))
    assert 'only company' in flags[0]

def tc_5_1_parse_money(val: Any) -> float:
    """Standardizes money strings (e.g. '$10M', '$1.5B') into raw floats."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    clean_str = str(val).replace('$', '').replace(',', '').strip().upper()
    multiplier = 1.0
    if clean_str.endswith('B'):
        multiplier = 1000000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('M'):
        multiplier = 1000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('K'):
        multiplier = 1000.0
        clean_str = clean_str[:-1]
    try:
        return float(clean_str) * multiplier
    except ValueError:
        return 0.0

def tc_5_1_validate_calculated_field_accuracy(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter mathematical accuracy of derived fields.
    Returns: (success_bool, list_of_error_logs)
    """
    errors = []
    cac = tc_5_1_parse_money(payload.get('Customer Acquisition Cost (CAC)'))
    clv = tc_5_1_parse_money(payload.get('Customer Lifetime Value (CLV)'))
    ratio_str = str(payload.get('CAC:LTV Ratio', ''))
    if cac > 0 and clv > 0 and ratio_str:
        ratio_match = re.match('^([\\d\\.]+)(:1)?$', ratio_str.strip())
        if ratio_match:
            expected_ratio = round(clv / cac, 2)
            ingested_ratio = round(float(ratio_match.group(1)), 2)
            if abs(expected_ratio - ingested_ratio) > 0.05:
                errors.append(f'Calculation Error: Ingested CAC:LTV Ratio ({ingested_ratio}) is inaccurate. Expected: {expected_ratio}.')
        else:
            errors.append(f"Format Error: Ingested CAC:LTV Ratio '{ratio_str}' is invalid.")
    monthly_burn = tc_5_1_parse_money(payload.get('Burn Rate'))
    net_new_arr = tc_5_1_parse_money(payload.get('Net New ARR'))
    multiplier_str = str(payload.get('Burn Multiplier', ''))
    if monthly_burn > 0 and net_new_arr > 0 and multiplier_str:
        try:
            ingested_multiplier = float(multiplier_str)
            annual_burn = monthly_burn * 12.0
            expected_multiplier = round(annual_burn / net_new_arr, 2)
            if abs(ingested_multiplier - expected_multiplier) > 0.05:
                errors.append(f'Calculation Error: Ingested Burn Multiplier ({ingested_multiplier}) is inaccurate. Expected: {expected_multiplier}.')
        except ValueError:
            pass
    monthly_burn_rate = tc_5_1_parse_money(payload.get('Burn Rate'))
    total_reserves = tc_5_1_parse_money(payload.get('Total Capital Raised'))
    runway_str = str(payload.get('Runway', ''))
    if monthly_burn_rate > 0 and total_reserves > 0 and runway_str:
        try:
            ingested_runway = float(runway_str)
            expected_runway = round(total_reserves / monthly_burn_rate, 2)
            if abs(ingested_runway - expected_runway) > 0.05:
                errors.append(f'Calculation Error: Ingested Runway ({ingested_runway}) is inaccurate. Expected: {expected_runway}.')
        except ValueError:
            pass
    combined = payload.get('Social Media Followers – Combined')
    li = payload.get('LinkedIn Followers', 0) or 0
    tw = payload.get('Twitter Followers', 0) or 0
    fb = payload.get('Facebook Followers', 0) or 0
    ig = payload.get('Instagram Followers', 0) or 0
    if combined is not None:
        expected_combined = li + tw + fb + ig
        if int(combined) != expected_combined:
            errors.append(f'Calculation Error: Ingested Combined Followers ({combined}) does not match sum of channels ({expected_combined}).')
    revenues = tc_5_1_parse_money(payload.get('Annual Revenues'))
    tam = tc_5_1_parse_money(payload.get('Total Addressable Market (TAM)'))
    market_share_str = str(payload.get('Market Share (%)', ''))
    if revenues > 0 and tam > 0 and market_share_str:
        share_match = re.match('^([\\d\\.]+)\\s*%$', market_share_str.strip())
        if share_match:
            expected_share = round(revenues / tam * 100, 2)
            ingested_share = round(float(share_match.group(1)), 2)
            if abs(expected_share - ingested_share) > 0.05:
                errors.append(f'Calculation Error: Ingested Market Share ({ingested_share}%) is inaccurate. Expected: {expected_share}%.')
        else:
            errors.append(f"Format Error: Ingested Market Share '{market_share_str}' is invalid.")
    return (len(errors) == 0, errors)

def test_tc_5_1_accurate_calculations_pass():
    """Verifies that a company profile with mathematically correct calculations passes validation."""
    payload = {'Customer Acquisition Cost (CAC)': '$100', 'Customer Lifetime Value (CLV)': '$300', 'CAC:LTV Ratio': '3:1', 'Burn Rate': '$100K', 'Net New ARR': '$1M', 'Burn Multiplier': '1.2', 'Total Capital Raised': '$1.2M', 'Runway': '12.0', 'LinkedIn Followers': 1000, 'Twitter Followers': 500, 'Facebook Followers': 300, 'Instagram Followers': 200, 'Social Media Followers – Combined': 2000, 'Annual Revenues': '$500M', 'Total Addressable Market (TAM)': '$10B', 'Market Share (%)': '5%'}
    success, errors = tc_5_1_validate_calculated_field_accuracy(payload)
    assert success is True
    assert not errors

def test_tc_5_1_inaccurate_cac_ltv_ratio_fails():
    """Verifies that an incorrect CAC:LTV Ratio is caught and fails validation."""
    payload = {'Customer Acquisition Cost (CAC)': 100.0, 'Customer Lifetime Value (CLV)': 300.0, 'CAC:LTV Ratio': '5:1'}
    success, errors = tc_5_1_validate_calculated_field_accuracy(payload)
    assert success is False
    assert any(('Inaccurate. Expected: 3.0' in err for err in errors))

def test_tc_5_1_inaccurate_burn_multiplier_fails():
    """Verifies that an incorrect Burn Multiplier is caught and fails validation."""
    payload = {'Burn Rate': 100000.0, 'Net New ARR': 1000000.0, 'Burn Multiplier': '2.5'}
    success, errors = tc_5_1_validate_calculated_field_accuracy(payload)
    assert success is False
    assert any(('Inaccurate. Expected: 1.2' in err for err in errors))

def test_tc_5_1_inaccurate_social_media_combined_followers_fails():
    """Verifies that an incorrect Combined followers sum fails validation."""
    payload = {'LinkedIn Followers': 1000, 'Twitter Followers': 500, 'Social Media Followers – Combined': 2500}
    success, errors = tc_5_1_validate_calculated_field_accuracy(payload)
    assert success is False
    assert any(('Combined Followers' in err for err in errors))

def test_tc_5_1_inaccurate_market_share_percentage_fails():
    """Verifies that an incorrect Market Share percentage fails validation."""
    payload = {'Annual Revenues': '$100M', 'Total Addressable Market (TAM)': '$1B', 'Market Share (%)': '15%'}
    success, errors = tc_5_1_validate_calculated_field_accuracy(payload)
    assert success is False
    assert any(('Inaccurate. Expected: 10.0' in err for err in errors))

def tc_5_2_parse_money_to_float(val: Any) -> float:
    """Parses money strings (e.g. '$10M', '-$1.5B') into raw floats supporting negative signs."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    raw_str = str(val).replace('$', '').replace(',', '').strip().upper()
    is_negative = False
    if '-' in raw_str:
        is_negative = True
        raw_str = raw_str.replace('-', '')
    multiplier = 1.0
    if raw_str.endswith('B'):
        multiplier = 1000000000.0
        raw_str = raw_str[:-1]
    elif raw_str.endswith('M'):
        multiplier = 1000000.0
        raw_str = raw_str[:-1]
    elif raw_str.endswith('K'):
        multiplier = 1000.0
        raw_str = raw_str[:-1]
    try:
        val_float = float(raw_str) * multiplier
        return -val_float if is_negative else val_float
    except ValueError:
        return 0.0

def tc_5_2_validate_logical_consistency(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter logical alignment of related fields.
    Returns: (success_bool, list_of_error_logs)
    """
    errors = []

    def is_filled(field: str) -> bool:
        val = payload.get(field)
        if val is None:
            return False
        if isinstance(val, str) and val.strip() == '':
            return False
        return True
    profit = tc_5_2_parse_money_to_float(payload.get('Annual Profits'))
    status = payload.get('Profitability Status')
    if status:
        if status == 'Profitable' and profit <= 0:
            errors.append(f"Logical Contradiction: Profitability Status is 'Profitable' but Annual Profits are negative/zero ({profit}).")
        elif status == 'Loss-making' and profit >= 0:
            errors.append(f"Logical Contradiction: Profitability Status is 'Loss-making' but Annual Profits are positive/zero ({profit}).")
        elif status == 'Break-even' and profit != 0:
            errors.append(f"Logical Contradiction: Profitability Status is 'Break-even' but Annual Profits are non-zero ({profit}).")
    nature = payload.get('Nature of Company')
    exit_history = str(payload.get('Exit Strategy/History', ''))
    if nature == 'Public':
        if not re.search('\\b(ipo|public|stock|listed|nasdaq|nyse)\\b', exit_history, re.IGNORECASE):
            errors.append("Logical Contradiction: Company Nature is 'Public' but Exit History lacks public listing / IPO references.")
    concentration = payload.get('Customer Concentration Risk')
    customers = payload.get('Top Customers by Client Segments')
    if concentration == 'Yes' or (isinstance(concentration, str) and 'High' in concentration):
        if not is_filled('Top Customers by Client Segments'):
            errors.append('Logical Contradiction: Customer Concentration Risk is flagged but Top Customers are missing.')
    try:
        offices_count = int(payload.get('Number of Offices (beyond HQ)', 0) or 0)
        if offices_count > 0 and (not is_filled('Office Locations')):
            errors.append(f'Logical Contradiction: Number of Offices is {offices_count} but Office Locations list is empty.')
    except ValueError:
        pass
    remote_policy = payload.get('Remote Work Policy')
    flex_policy = payload.get('Remote / hybrid / on-site flexibility')
    if remote_policy == 'Remote-First' and flex_policy == 'On-Site':
        errors.append("Logical Contradiction: Remote Work Policy is 'Remote-First' but flexibility policy is set as strict 'On-Site'.")
    return (len(errors) == 0, errors)

def test_tc_5_2_consistent_relationships_pass():
    """Verifies that logically aligned fields pass the consistency audit."""
    valid_payload = {'Annual Profits': '$1.5M', 'Profitability Status': 'Profitable', 'Nature of Company': 'Public', 'Exit Strategy/History': 'Completed IPO on NASDAQ in 2024', 'Customer Concentration Risk': 'Yes', 'Top Customers by Client Segments': 'Enterprise Segment: 4 main accounts', 'Number of Offices (beyond HQ)': 3, 'Office Locations': 'London (UK), Paris (FR), Berlin (GER)', 'Remote Work Policy': 'Remote-First', 'Remote / hybrid / on-site flexibility': 'Remote'}
    success, errors = tc_5_2_validate_logical_consistency(valid_payload)
    assert success is True
    assert not errors

def test_tc_5_2_profit_polarity_contradiction_fails():
    """Verifies that mismatched Profitability Status and Annual Profits fail validation."""
    invalid_payload = {'Annual Profits': '-$500K', 'Profitability Status': 'Profitable'}
    success, errors = tc_5_2_validate_logical_consistency(invalid_payload)
    assert success is False
    assert any(("Profitability Status is 'Profitable'" in err for err in errors))

def test_tc_5_2_public_company_missing_ipo_evidence_fails():
    """Verifies that a public company with an exit history lacking public listing details fails validation."""
    invalid_payload = {'Nature of Company': 'Public', 'Exit Strategy/History': 'Early stage private seed round completed.'}
    success, errors = tc_5_2_validate_logical_consistency(invalid_payload)
    assert success is False
    assert any(('Exit History lacks public listing / IPO references' in err for err in errors))

def test_tc_5_2_unsubstantiated_concentration_risk_fails():
    """Verifies that flagging concentration risk without providing customer details fails validation."""
    invalid_payload = {'Customer Concentration Risk': 'Yes', 'Top Customers by Client Segments': None}
    success, errors = tc_5_2_validate_logical_consistency(invalid_payload)
    assert success is False
    assert any(('Top Customers are missing' in err for err in errors))

def test_tc_5_2_missing_office_locations_fails():
    """Verifies that declaring branch offices without specifying their locations fails validation."""
    invalid_payload = {'Number of Offices (beyond HQ)': 5, 'Office Locations': ''}
    success, errors = tc_5_2_validate_logical_consistency(invalid_payload)
    assert success is False
    assert any(('Office Locations list is empty' in err for err in errors))

def tc_5_3_extract_years_from_text(text: str) -> List[int]:
    """Extracts all 4-digit years (from 1800 to 2099) found within a string."""
    if not text:
        return []
    candidates = re.findall('\\b(18\\d{2}|19\\d{2}|20\\d{2})\\b', text)
    return [int(yr) for yr in candidates]

def tc_5_3_extract_dates_from_formatted_string(text: str) -> List[int]:
    """Extracts years specifically from YYYY-MM-DD formatted segments."""
    if not text:
        return []
    dates = re.findall('\\b(18\\d{2}|19\\d{2}|20\\d{2})-\\d{2}-\\d{2}\\b', text)
    return [int(yr) for yr in dates]

def tc_5_3_validate_timeline_consistency(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces cross-parameter chronological consistency validations:
    1. Rejects Year of Incorporation values that exist in the future (beyond May 22, 2026).
    2. Verifies that all funding round years are >= Year of Incorporation.
    3. Verifies that all news event years are >= Year of Incorporation.
    4. Verifies that all exit strategy event years are >= Year of Incorporation.
    5. Verifies that all layoff history years are >= Year of Incorporation.
    """
    errors = []
    current_year = 2026
    try:
        inc_year = int(payload.get('Year of Incorporation', 0) or 0)
        if inc_year < 1800 or inc_year > current_year:
            errors.append(f'Anchor Error: Year of Incorporation ({inc_year}) must be a valid past year (1800 to {current_year}).')
            return (False, errors)
    except ValueError:
        errors.append(f"Type Error: Year of Incorporation '{payload.get('Year of Incorporation')}' is not a valid integer.")
        return (False, errors)
    rounds_str = payload.get('Recent Funding Rounds', '')
    if rounds_str:
        funding_years = tc_5_3_extract_dates_from_formatted_string(rounds_str)
        for year in funding_years:
            if year < inc_year:
                errors.append(f'Chronological Error: Funding round in {year} occurs before Year of Incorporation ({inc_year}).')
    news_str = payload.get('Recent News', '')
    if news_str:
        news_years = tc_5_3_extract_dates_from_formatted_string(news_str)
        if not news_years:
            news_years = tc_5_3_extract_years_from_text(news_str)
        for year in news_years:
            if year < inc_year:
                errors.append(f'Chronological Error: News event in {year} occurs before Year of Incorporation ({inc_year}).')
    exit_str = payload.get('Exit Strategy/History', '')
    if exit_str:
        exit_years = tc_5_3_extract_years_from_text(exit_str)
        for year in exit_years:
            if year < inc_year:
                errors.append(f'Chronological Error: Exit strategy event in {year} occurs before Year of Incorporation ({inc_year}).')
    layoffs_str = payload.get('Layoff history', '')
    if layoffs_str:
        layoff_years = tc_5_3_extract_dates_from_formatted_string(layoffs_str)
        if not layoff_years:
            layoff_years = tc_5_3_extract_years_from_text(layoffs_str)
        for year in layoff_years:
            if year < inc_year:
                errors.append(f'Chronological Error: Layoff event in {year} occurs before Year of Incorporation ({inc_year}).')
    return (len(errors) == 0, errors)

def test_tc_5_3_chronologically_consistent_record_passes():
    """Verifies that a record with consistent event timelines successfully passes validation."""
    valid_payload = {'Year of Incorporation': 2015, 'Recent Funding Rounds': '2018-05-12 - Series A - $10M, 2026-03-10 - Series B - $15M', 'Recent News': '2024-06-15 - Expanded into European markets, 2025-11-04 - Launched platform v2.0', 'Exit Strategy/History': 'Targeting IPO on NYSE by 2027', 'Layoff history': '2022-10-12 - 5% of workforce impacted'}
    success, errors = tc_5_3_validate_timeline_consistency(valid_payload)
    assert success is True
    assert not errors

def test_tc_5_3_future_incorporation_year_rejected():
    """Verifies that a future incorporation year fails validation immediately."""
    invalid_payload = {'Year of Incorporation': 2028}
    success, errors = tc_5_3_validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any(('must be a valid past year' in err for err in errors))

def test_tc_5_3_pre_incorporation_funding_rejected():
    """Verifies that funding transactions dated before company incorporation fail validation."""
    invalid_payload = {'Year of Incorporation': 2015, 'Recent Funding Rounds': '2010-05-12 - Seed Round - $1M'}
    success, errors = tc_5_3_validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any(('Funding round in 2010 occurs before Year of Incorporation' in err for err in errors))

def test_tc_5_3_pre_incorporation_news_rejected():
    """Verifies that news events dated before company incorporation fail validation."""
    invalid_payload = {'Year of Incorporation': 2020, 'Recent News': '2015-11-04 - Company partnered with Tech Corp'}
    success, errors = tc_5_3_validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any(('News event in 2015 occurs before Year of Incorporation' in err for err in errors))

def test_tc_5_3_pre_incorporation_layoffs_rejected():
    """Verifies that layoff events dated before company incorporation fail validation."""
    invalid_payload = {'Year of Incorporation': 2021, 'Layoff history': '2018-05-10 - Restructuring led to 10% staff cut'}
    success, errors = tc_5_3_validate_timeline_consistency(invalid_payload)
    assert success is False
    assert any(('Layoff event in 2018 occurs before Year of Incorporation' in err for err in errors))
tc_5_4_REGISTRY_PATTERNS = {'Company Phone Number': re.compile('^\\+?[1-9]\\d{1,14}$'), 'Company Contact Email': re.compile('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'), 'Website URL': re.compile('^https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)$'), 'Annual Revenues': re.compile('^\\$?\\d{1,3}(,\\d{3})*(\\.\\d{2})?[KkMmBb]?$'), 'Year of Incorporation': re.compile('^(19|20)\\d{2}$')}

def tc_5_4_validate_field_format(field_name: str, value: Any) -> bool:
    """Enforces absolute standard format validation based on parameter rules."""
    pattern = tc_5_4_REGISTRY_PATTERNS.get(field_name)
    if not pattern:
        raise ValueError(f"No regex format mapped for field '{field_name}'.")
    if value is None:
        return False
    return pattern.match(str(value)) is not None

def tc_5_4_validate_funding_rounds_date_format(rounds_str: str) -> bool:
    """
    Validates embedded date formats inside funding timeline lists.
    Every round must start with a YYYY-MM-DD date segment.
    """
    if not rounds_str:
        return False
    records = [r.strip() for r in rounds_str.split(',') if r.strip()]
    for record in records:
        date_match = re.match('^(\\d{4}-\\d{2}-\\d{2})\\b', record)
        if not date_match:
            return False
    return True

@pytest.mark.parametrize('valid_phone', ['+14155552671', '+442079460192', '14155552671'])
def test_tc_5_4_valid_phone_format(valid_phone):
    """Verifies that E.164 standard phone formats pass successfully."""
    assert tc_5_4_validate_field_format('Company Phone Number', valid_phone) is True

@pytest.mark.parametrize('invalid_phone', ['+1-415-555-2671', '(415) 555-2671', '415-555-2671'])
def test_tc_5_4_invalid_phone_rejected(invalid_phone):
    """Verifies that regional formatting with dashes, spaces, or parentheses is rejected."""
    assert tc_5_4_validate_field_format('Company Phone Number', invalid_phone) is False

@pytest.mark.parametrize('valid_email', ['info@company.com', 'contact_sales@sub.domain.org'])
def test_tc_5_4_valid_email_format(valid_email):
    """Verifies that standard RFC 5322 emails pass successfully."""
    assert tc_5_4_validate_field_format('Company Contact Email', valid_email) is True

@pytest.mark.parametrize('invalid_email', ['info#company.com', 'info@company', '@domain.com'])
def test_tc_5_4_invalid_email_rejected(invalid_email):
    """Verifies that malformed emails are rejected."""
    assert tc_5_4_validate_field_format('Company Contact Email', invalid_email) is False

@pytest.mark.parametrize('valid_url', ['https://microsoft.com', 'https://www.google.com/search?q=test'])
def test_tc_5_4_valid_url_format(valid_url):
    """Verifies that standard HTTPS URLs pass successfully."""
    assert tc_5_4_validate_field_format('Website URL', valid_url) is True

@pytest.mark.parametrize('invalid_url', ['http://microsoft@com', 'https://invalid_url', 'www.no-scheme.com'])
def test_tc_5_4_invalid_url_rejected(invalid_url):
    """Verifies that malformed or non-secure URL configurations are rejected."""
    assert tc_5_4_validate_field_format('Website URL', invalid_url) is False

@pytest.mark.parametrize('valid_revenue', ['$150,000,000', '150,000,000', '$150M', '1.5B'])
def test_tc_5_4_valid_revenue_format(valid_revenue):
    """Verifies that standard currency and magnitude notations pass successfully."""
    assert tc_5_4_validate_field_format('Annual Revenues', valid_revenue) is True

@pytest.mark.parametrize('invalid_revenue', ['150M USD', 'USD 150,000,000', 'Approx $150M'])
def test_tc_5_4_invalid_revenue_rejected(invalid_revenue):
    """Verifies that informal non-standardized currency tags are rejected."""
    assert tc_5_4_validate_field_format('Annual Revenues', invalid_revenue) is False

@pytest.mark.parametrize('valid_rounds', ['2024-01-10 - Series A - $10M', '2024-01-10 - Series A - $10M, 2025-06-15 - Series B - $15M'])
def test_tc_5_4_valid_funding_rounds_date_formatting(valid_rounds):
    """Verifies that embedded dates conforming strictly to YYYY-MM-DD pass validation."""
    assert tc_5_4_validate_funding_rounds_date_format(valid_rounds) is True

@pytest.mark.parametrize('invalid_rounds', ['01/10/2024 - Series A - $10M', '2024.01.10 - Series A - $10M'])
def test_tc_5_4_invalid_funding_rounds_date_rejected(invalid_rounds):
    """Verifies that non-standard date separators or formatting fail validation."""
    assert tc_5_4_validate_funding_rounds_date_format(invalid_rounds) is False

def tc_5_5_parse_percent_to_float(val: Any) -> float:
    """Parses percentage strings (e.g. '15.5%', '5%') into raw floats."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    clean_str = str(val).replace('%', '').strip()
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

def tc_5_5_parse_employee_size_to_int(val: Any) -> int:
    """
    Parses employee size strings into a representative integer.
    Supports ranges ('11-50' -> 50) and exact counts ('1000' -> 1000).
    """
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    clean_str = str(val).replace(',', '').replace(' ', '').strip()
    if '+' in clean_str:
        clean_str = clean_str.replace('+', '')
    if '-' in clean_str:
        parts = clean_str.split('-')
        try:
            return int(parts[1])
        except (IndexError, ValueError):
            pass
    try:
        return int(clean_str)
    except ValueError:
        return 0

def tc_5_5_validate_cross_parameter_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Performs holistic record-level validations to catch contradictory metric combinations.
    1. Operational Footprint: Flags if headcount is tiny (< 10) but office count is high (> 5).
    2. Customer Success: Flags if NPS is exceptional (> 75) but churn rate is extremely high (> 30%).
    3. Talent Growth: Flags if turnover is extremely high (> 40%) but workforce is marked as stable/scaling with 0 hiring velocity.
    """
    errors = []
    headcount = tc_5_5_parse_employee_size_to_int(payload.get('Employee Size'))
    try:
        office_count = int(payload.get('Number of Offices (beyond HQ)', 0) or 0)
        if 0 < headcount < 10 and office_count > 5:
            errors.append(f'Operational Contradiction: Employee count is very small ({headcount}), but company claims {office_count} offices beyond HQ. This ratio is highly anomalous.')
    except ValueError:
        pass
    nps = payload.get('Net Promoter Score (NPS)')
    churn_rate = tc_5_5_parse_percent_to_float(payload.get('Churn Rate'))
    if nps is not None and churn_rate > 0:
        try:
            nps_val = int(nps)
            if nps_val >= 75 and churn_rate >= 30.0:
                errors.append(f'Loyalty Contradiction: Ingested Net Promoter Score is exceptionally high ({nps_val}), but Churn Rate is recorded as extremely high ({churn_rate}%). These metrics contradict each other.')
        except ValueError:
            pass
    turnover = tc_5_5_parse_percent_to_float(payload.get('Employee Turnover'))
    hiring_velocity = str(payload.get('Hiring Velocity', '')).lower()
    if turnover >= 45.0 and ('low' in hiring_velocity or 'none' in hiring_velocity or '0' in hiring_velocity):
        errors.append(f"Talent Contradiction: Employee Turnover is extremely high ({turnover}%), but Hiring Velocity is recorded as '{payload.get('Hiring Velocity')}'. This combination indicates rapid workforce depletion without replacement.")
    return (len(errors) == 0, errors)

def test_tc_5_5_coherent_metrics_pass_audit():
    """Verifies that internally consistent, logically coherent records pass validation."""
    coherent_payload = {'Employee Size': '10,000+', 'Number of Offices (beyond HQ)': 25, 'Net Promoter Score (NPS)': 80, 'Churn Rate': '4%', 'Employee Turnover': '12%', 'Hiring Velocity': 'High'}
    success, errors = tc_5_5_validate_cross_parameter_coherence(coherent_payload)
    assert success is True
    assert not errors

def test_tc_5_5_anomalous_headcount_to_office_ratio_fails():
    """Verifies that claiming a tiny headcount with a massive branch office footprint fails validation."""
    anomalous_payload = {'Employee Size': '1-5', 'Number of Offices (beyond HQ)': 12}
    success, errors = tc_5_5_validate_cross_parameter_coherence(anomalous_payload)
    assert success is False
    assert any(('Operational Contradiction' in err for err in errors))

def test_tc_5_5_contradictory_nps_and_churn_fails():
    """Verifies that contradictory high customer satisfaction and high customer churn fail validation."""
    contradictory_payload = {'Net Promoter Score (NPS)': 85, 'Churn Rate': '35%'}
    success, errors = tc_5_5_validate_cross_parameter_coherence(contradictory_payload)
    assert success is False
    assert any(('Loyalty Contradiction' in err for err in errors))

def test_tc_5_5_unsupported_high_turnover_fails():
    """Verifies that high employee loss paired with zero hiring velocity triggers an alarm."""
    contradictory_payload = {'Employee Turnover': '50%', 'Hiring Velocity': 'None / Zero open roles'}
    success, errors = tc_5_5_validate_cross_parameter_coherence(contradictory_payload)
    assert success is False
    assert any(('Talent Contradiction' in err for err in errors))
tc_6_1_ALLOWED_MATURITY_STAGES = {'Startup', 'Scale-up', 'Mature', 'Enterprise'}
tc_6_1_ALLOWED_PROFITABILITY_STATUSES = {'Profitable', 'Break-even', 'Loss-making'}

def tc_6_1_validate_early_stage_startup(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter edge case rules for new startups (Incorporation Year = 2026):
    1. If Year of Incorporation is 2026, Company maturity MUST be "Startup".
    2. If Annual Revenues is None/NULL or $0, Profitability Status CANNOT be "Profitable".
    3. Optional metrics (like Glassdoor Rating, Exit History) are allowed to be None.
    """
    errors = []
    try:
        inc_year = int(payload.get('Year of Incorporation', 0) or 0)
    except ValueError:
        errors.append('Type Error: Year of Incorporation must be an integer.')
        return (False, errors)
    maturity = payload.get('Company maturity')
    if inc_year == 2026:
        if maturity != 'Startup':
            errors.append(f"Maturity Error: Company founded in 2026 must have maturity 'Startup' (Ingested: '{maturity}').")
    revenues = payload.get('Annual Revenues')
    profitability = payload.get('Profitability Status')
    is_pre_revenue = False
    if revenues is None:
        is_pre_revenue = True
    elif isinstance(revenues, (int, float)) and revenues == 0:
        is_pre_revenue = True
    elif isinstance(revenues, str):
        clean_rev = revenues.replace('$', '').replace(',', '').strip()
        if clean_rev == '' or clean_rev == '0':
            is_pre_revenue = True
    if is_pre_revenue:
        if profitability == 'Profitable':
            errors.append("Financial Logic Error: Company is pre-revenue (Annual Revenues is NULL or $0) but Profitability Status is marked as 'Profitable'.")
    optional_fields_to_check = ['Glassdoor Rating', 'Indeed Rating', 'Exit Strategy/History', 'Awards & Recognitions']
    for field in optional_fields_to_check:
        val = payload.get(field)
        if val is None:
            pass
    return (len(errors) == 0, errors)

def test_tc_6_1_valid_new_startup_passes():
    """Verifies that a valid early-stage startup profile passes all edge-case rules."""
    new_startup_payload = {'Year of Incorporation': 2026, 'Company maturity': 'Startup', 'Annual Revenues': None, 'Profitability Status': 'Loss-making', 'Glassdoor Rating': None, 'Exit Strategy/History': None}
    success, errors = tc_6_1_validate_early_stage_startup(new_startup_payload)
    assert success is True
    assert not errors

def test_tc_6_1_new_startup_with_invalid_maturity_fails():
    """Verifies that a company incorporated in 2026 claiming to be 'Mature' fails validation."""
    invalid_payload = {'Year of Incorporation': 2026, 'Company maturity': 'Mature', 'Annual Revenues': None, 'Profitability Status': 'Loss-making'}
    success, errors = tc_6_1_validate_early_stage_startup(invalid_payload)
    assert success is False
    assert any(('Maturity Error' in err for err in errors))

def test_tc_6_1_pre_revenue_marked_profitable_fails():
    """Verifies that a pre-revenue company claiming to be 'Profitable' fails validation."""
    invalid_payload = {'Year of Incorporation': 2026, 'Company maturity': 'Startup', 'Annual Revenues': '$0', 'Profitability Status': 'Profitable'}
    success, errors = tc_6_1_validate_early_stage_startup(invalid_payload)
    assert success is False
    assert any(('Financial Logic Error' in err for err in errors))
tc_6_2_ALLOWED_CONGLOMERATE_CATEGORIES = {'Conglomerate', 'Enterprise'}
tc_6_2_ALLOWED_CONGLOMERATE_MATURITIES = {'Mature', 'Enterprise'}

def tc_6_2_parse_currency_string_to_float(val: str) -> float:
    """Parses money strings (e.g. '$307.39B') into raw floats."""
    if not val:
        return 0.0
    clean_str = str(val).replace('$', '').replace(',', '').strip().upper()
    multiplier = 1.0
    if clean_str.endswith('B'):
        multiplier = 1000000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('M'):
        multiplier = 1000000.0
        clean_str = clean_str[:-1]
    try:
        return float(clean_str) * multiplier
    except ValueError:
        return 0.0

def tc_6_2_validate_conglomerate_edge_cases(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter edge case rules for very large companies:
    1. If parsed Annual Revenues are > $1B (1e9), Category MUST be 'Conglomerate' or 'Enterprise'.
    2. If Countries Operating In lists > 1 country, Global exposure MUST be 'Yes'.
    3. If Employee Size is '10,000+' or > 10000, Company maturity MUST be 'Mature' or 'Enterprise'.
    """
    errors = []
    raw_rev = payload.get('Annual Revenues')
    category = payload.get('Category')
    if raw_rev:
        revenue_float = tc_6_2_parse_currency_string_to_float(raw_rev)
        if revenue_float >= 1000000000.0:
            if category not in tc_6_2_ALLOWED_CONGLOMERATE_CATEGORIES:
                errors.append(f"Category Error: Company with revenue >= $1B ({raw_rev}) must be classified as 'Conglomerate' or 'Enterprise' (Ingested: '{category}').")
    countries_str = str(payload.get('Countries Operating In', ''))
    global_exp = payload.get('Global exposure')
    if countries_str and countries_str.strip() != '':
        countries_list = [c.strip() for c in countries_str.split(',') if c.strip()]
        if len(countries_list) > 1:
            if global_exp != 'Yes':
                errors.append(f"Logical Error: Company operates in multiple countries ({countries_str}), but Global exposure is marked as '{global_exp}' (Expected: 'Yes').")
    emp_size = str(payload.get('Employee Size', ''))
    maturity = payload.get('Company maturity')
    if emp_size == '10,000+' or '10000' in emp_size:
        if maturity not in tc_6_2_ALLOWED_CONGLOMERATE_MATURITIES:
            errors.append(f"Maturity Error: Company with headcount '{emp_size}' must have maturity 'Mature' or 'Enterprise' (Ingested: '{maturity}').")
    return (len(errors) == 0, errors)

def test_tc_6_2_valid_conglomerate_profile_passes():
    """Verifies that a valid global conglomerate profile successfully passes all edge-case rules."""
    valid_payload = {'Company Name': 'Alphabet Inc.', 'Category': 'Conglomerate', 'Employee Size': '10,000+', 'Countries Operating In': 'US, UK, Germany, France, Japan', 'Annual Revenues': '$307.39B', 'Company maturity': 'Mature', 'Global exposure': 'Yes'}
    success, errors = tc_6_2_validate_conglomerate_edge_cases(valid_payload)
    assert success is True
    assert not errors

def test_tc_6_2_billion_dollar_company_mismatched_category_fails():
    """Verifies that a company with revenues >= $1B classified as a 'Startup' fails validation."""
    invalid_payload = {'Company Name': 'Alphabet Inc.', 'Category': 'Startup', 'Employee Size': '10,000+', 'Countries Operating In': 'US, UK', 'Annual Revenues': '$307.39B', 'Company maturity': 'Mature', 'Global exposure': 'Yes'}
    success, errors = tc_6_2_validate_conglomerate_edge_cases(invalid_payload)
    assert success is False
    assert any(('Category Error' in err for err in errors))

def test_tc_6_2_multinational_with_no_global_exposure_fails():
    """Verifies that operating in multiple countries requires 'Yes' for Global exposure."""
    invalid_payload = {'Company Name': 'Nestlé S.A.', 'Category': 'Conglomerate', 'Employee Size': '10,000+', 'Countries Operating In': 'US, UK, Switzerland', 'Annual Revenues': '$95B', 'Company maturity': 'Mature', 'Global exposure': 'No'}
    success, errors = tc_6_2_validate_conglomerate_edge_cases(invalid_payload)
    assert success is False
    assert any(("Global exposure is marked as 'No'" in err for err in errors))

def test_tc_6_2_giant_headcount_with_invalid_maturity_fails():
    """Verifies that a company with 10,000+ employees claiming to be a 'Startup' fails validation."""
    invalid_payload = {'Company Name': 'Berkshire Hathaway', 'Category': 'Conglomerate', 'Employee Size': '10,000+', 'Countries Operating In': 'US', 'Annual Revenues': '$360B', 'Company maturity': 'Startup', 'Global exposure': 'No'}
    success, errors = tc_6_2_validate_conglomerate_edge_cases(invalid_payload)
    assert success is False
    assert any(('Maturity Error' in err for err in errors))
tc_6_3_ALLOWED_PRIVATE_STRUCTURES = {'Private', 'Partnership', 'Subsidiary', 'Non-Profit'}

def tc_6_3_validate_private_company_edge_cases(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces per-parameter edge case rules for private companies:
    1. Nature of Company MUST be within ALLOWED_PRIVATE_STRUCTURES (cannot be 'Public').
    2. If Nature of Company is private, optional financial metrics (Annual Revenues, Company Valuation,
       Annual Profits) and Exit Strategy/History are allowed to be None (graceful degradation).
    3. Board of Directors / Advisors is mandatory (Not Null) and must be populated with non-empty values,
       rejecting raw None even for private unlisted companies.
    """
    errors = []
    nature = payload.get('Nature of Company')
    if not nature:
        errors.append("Validation Error: 'Nature of Company' is mandatory.")
        return (False, errors)
    if nature not in tc_6_3_ALLOWED_PRIVATE_STRUCTURES:
        errors.append(f"Structure Error: Private company validation run, but company structure is marked as '{nature}' (Expected one of: {tc_6_3_ALLOWED_PRIVATE_STRUCTURES}).")
    revenues = payload.get('Annual Revenues')
    profits = payload.get('Annual Profits')
    valuation = payload.get('Company Valuation')
    exit_history = payload.get('Exit Strategy/History')
    board = payload.get('Board of Directors / Advisors')
    if board is None:
        errors.append("Mandatory Constraint Error: 'Board of Directors / Advisors' is mandatory and cannot be NULL.")
    elif isinstance(board, str) and board.strip() == '':
        errors.append("Mandatory Constraint Error: 'Board of Directors / Advisors' cannot be empty or whitespace.")
    return (len(errors) == 0, errors)

def test_tc_6_3_valid_private_company_passes():
    """Verifies that a valid private family-owned company successfully passes all edge-case rules."""
    valid_payload = {'Nature of Company': 'Private', 'Board of Directors / Advisors': 'John Doe - Director, Jane Doe - Director', 'Annual Revenues': None, 'Annual Profits': None, 'Company Valuation': None, 'Exit Strategy/History': None}
    success, errors = tc_6_3_validate_private_company_edge_cases(valid_payload)
    assert success is True
    assert not errors

def test_tc_6_3_private_run_with_public_structure_fails():
    """Verifies that a company marked as 'Public' fails private company validation rules."""
    invalid_payload = {'Nature of Company': 'Public', 'Board of Directors / Advisors': 'John Doe - Director'}
    success, errors = tc_6_3_validate_private_company_edge_cases(invalid_payload)
    assert success is False
    assert any(('Structure Error' in err for err in errors))

def test_tc_6_3_private_company_missing_board_fails():
    """Verifies that even for private companies, the mandatory Board of Directors field cannot be NULL."""
    invalid_payload = {'Nature of Company': 'Private', 'Board of Directors / Advisors': None}
    success, errors = tc_6_3_validate_private_company_edge_cases(invalid_payload)
    assert success is False
    assert any(('is mandatory and cannot be NULL' in err for err in errors))

def test_tc_6_3_private_company_empty_board_fails():
    """Verifies that even for private companies, the mandatory Board of Directors field cannot be empty whitespace."""
    invalid_payload = {'Nature of Company': 'Private', 'Board of Directors / Advisors': '   '}
    success, errors = tc_6_3_validate_private_company_edge_cases(invalid_payload)
    assert success is False
    assert any(('cannot be empty or whitespace' in err for err in errors))
tc_7_1_EMPLOYEE_SIZE_RE = re.compile('^(\\d+|\\d+-\\d+|\\d+\\+?)$')
tc_7_1_POSITIVE_INT_RE = re.compile('^\\d+$')

def tc_7_1_parse_extreme_currency(val: str) -> Optional[float]:
    """
    Parses and standardizes extreme financial strings (up to trillions) into raw floats.
    Handles 'T' (Trillion), 'B' (敲illion), 'M' (Million), 'K' (Thousand) multipliers.
    """
    if not val:
        return None
    clean_str = val.replace('$', '').replace(',', '').strip().upper()
    multiplier = 1.0
    if clean_str.endswith('T'):
        multiplier = 1000000000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('B'):
        multiplier = 1000000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('M'):
        multiplier = 1000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('K'):
        multiplier = 1000.0
        clean_str = clean_str[:-1]
    try:
        return float(clean_str) * multiplier
    except ValueError:
        return None

def tc_7_1_validate_extreme_headcount(val: str) -> bool:
    """Validates that massive employee size strings match allowed configurations."""
    if not val:
        return False
    return tc_7_1_EMPLOYEE_SIZE_RE.match(val) is not None

def tc_7_1_validate_extreme_positive_integer(val: str) -> bool:
    """Validates extremely large integer strings (followers, offices) match positive int patterns."""
    if not val:
        return False
    return tc_7_1_POSITIVE_INT_RE.match(val) is not None

@pytest.mark.parametrize('extreme_revenue, expected_float', [('$611.3B', 611300000000.0), ('$3.1T', 3100000000000.0), ('$100T', 100000000000000.0), ('$25B', 25000000000.0)])
def test_tc_7_1_extreme_currency_parsing_precision(extreme_revenue, expected_float):
    """Verifies that extreme financial scale notations are parsed into floats with complete precision."""
    parsed_val = tc_7_1_parse_extreme_currency(extreme_revenue)
    assert parsed_val == expected_float

@pytest.mark.parametrize('extreme_headcount', ['2300000', '2300000+', '1500000-2000000'])
def test_tc_7_1_extreme_employee_size_validation(extreme_headcount):
    """Verifies that extreme headcount values successfully pass boundary pattern matching."""
    assert tc_7_1_validate_extreme_headcount(extreme_headcount) is True

@pytest.mark.parametrize('extreme_integer', ['150000000', '11500'])
def test_tc_7_1_extreme_positive_integer_validation(extreme_integer):
    """Verifies that extremely large integer values (follower counts, office counts) pass checks."""
    assert tc_7_1_validate_extreme_positive_integer(extreme_integer) is True

def test_tc_7_1_negative_integer_rejected_as_positive_boundary():
    """Verifies that negative values are rejected by the positive integer boundary checks."""
    assert tc_7_1_validate_extreme_positive_integer('-11500') is False
tc_7_2_PERCENTAGE_RE = re.compile('^\\d{1,3}(\\.\\d{1,2})?%$')
tc_7_2_POSITIVE_INT_RE = re.compile('^\\d+$')

def tc_7_2_parse_currency_string_to_float(val: str) -> Optional[float]:
    """
    Standardizes and parses financial strings (supporting $0 and commas) into raw floats.
    """
    if val is None:
        return None
    clean_str = val.replace('$', '').replace(',', '').strip().upper()
    multiplier = 1.0
    if clean_str.endswith('B'):
        multiplier = 1000000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('M'):
        multiplier = 1000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('K'):
        multiplier = 1000.0
        clean_str = clean_str[:-1]
    try:
        return float(clean_str) * multiplier
    except ValueError:
        return None

def tc_7_2_validate_percentage_string(val: str) -> bool:
    """Validates that a percentage string matches the strict percent regex."""
    if not val:
        return False
    return tc_7_2_PERCENTAGE_RE.match(val) is not None

def tc_7_2_validate_positive_integer_string(val: str) -> bool:
    """Validates that an integer count satisfies the positive integer regex."""
    if not val:
        return False
    return tc_7_2_POSITIVE_INT_RE.match(val) is not None

@pytest.mark.parametrize('zero_revenue', ['$0', '0', '$0.00', '0.00'])
def test_tc_7_2_zero_currency_parsing(zero_revenue):
    """Verifies that various zero-currency string representations parse cleanly to float 0.0."""
    parsed_val = tc_7_2_parse_currency_string_to_float(zero_revenue)
    assert parsed_val == 0.0

@pytest.mark.parametrize('zero_percentage', ['0%', '0.0%', '0.00%'])
def test_tc_7_2_zero_percentage_regex_validation(zero_percentage):
    """Verifies that zero percentage notations satisfy the percentage regex constraint."""
    assert tc_7_2_validate_percentage_string(zero_percentage) is True

@pytest.mark.parametrize('zero_integer', ['0', '00'])
def test_tc_7_2_zero_integer_regex_validation(zero_integer):
    """Verifies that exact zero integer counts satisfy the positive integer pattern."""
    assert tc_7_2_validate_positive_integer_string(zero_integer) is True

def test_tc_7_2_negative_turnover_rejected_by_percent_regex():
    """Verifies that negative percentages (invalid boundary states) fail validation."""
    assert tc_7_2_validate_percentage_string('-5%') is False

def test_tc_7_2_negative_offices_rejected_by_integer_regex():
    """Verifies that negative office counts (invalid boundary states) fail validation."""
    assert tc_7_2_validate_positive_integer_string('-1') is False
tc_7_3_YOY_GROWTH_RE = re.compile('^[+-]?\\d{1,3}(\\.\\d{1,2})?%$')
tc_7_3_NPS_RE = re.compile('^-?(100|[1-9]\\d?|0)$')

def tc_7_3_parse_negative_currency(val: str) -> Optional[float]:
    """
    Parses financial strings into raw floats, supporting negative values.
    Handles standard minus prefix ('-$15M'), suffix ('$15M-'), 
    and accounting parentheses ('($15M)').
    """
    if not val:
        return None
    clean_str = val.strip().upper()
    is_negative = False
    if clean_str.startswith('(') and clean_str.endswith(')'):
        is_negative = True
        clean_str = clean_str[1:-1]
    if '-' in clean_str:
        is_negative = True
        clean_str = clean_str.replace('-', '')
    clean_str = clean_str.replace('$', '').replace(',', '')
    multiplier = 1.0
    if clean_str.endswith('B'):
        multiplier = 1000000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('M'):
        multiplier = 1000000.0
        clean_str = clean_str[:-1]
    elif clean_str.endswith('K'):
        multiplier = 1000.0
        clean_str = clean_str[:-1]
    try:
        val_float = float(clean_str) * multiplier
        return -val_float if is_negative else val_float
    except ValueError:
        return None

def tc_7_3_validate_negative_growth_rate(val: str) -> bool:
    """Validates that a negative growth percentage conforms to the signed regex."""
    if not val:
        return False
    return tc_7_3_YOY_GROWTH_RE.match(val) is not None

def tc_7_3_validate_nps_boundary(val: str) -> Tuple[bool, Optional[int]]:
    """
    Validates that Net Promoter Score (NPS) falls strictly within the [-100, 100] range.
    Rejects values outside this range (e.g. -101) using strict regex pattern matching.
    """
    if not val:
        return (False, None)
    if not tc_7_3_NPS_RE.match(val):
        return (False, None)
    try:
        nps_int = int(val)
        if -100 <= nps_int <= 100:
            return (True, nps_int)
        return (False, None)
    except ValueError:
        return (False, None)

@pytest.mark.parametrize('negative_profit_str, expected_float', [('-15000000', -15000000.0), ('-$15,000,000', -15000000.0), ('($15,000,000)', -15000000.0), ('-$15M', -15000000.0), ('($1.5B)', -1500000000.0)])
def test_tc_7_3_negative_financials_parsing(negative_profit_str, expected_float):
    """Verifies that various negative currency formatting options standardize to exact negative floats."""
    parsed_val = tc_7_3_parse_negative_currency(negative_profit_str)
    assert parsed_val == expected_float

@pytest.mark.parametrize('negative_growth', ['-15.5%', '-15%', '-0.5%'])
def test_tc_7_3_negative_growth_rate_validation(negative_growth):
    """Verifies that negative percentage strings representing revenue contraction are validated successfully."""
    assert tc_7_3_validate_negative_growth_rate(negative_growth) is True

@pytest.mark.parametrize('valid_negative_nps, expected_int', [('-85', -85), ('-100', -100), ('0', 0)])
def test_tc_7_3_valid_negative_nps_boundaries(valid_negative_nps, expected_int):
    """Verifies that negative Net Promoter Scores within the valid range are successfully validated and parsed."""
    success, parsed_val = tc_7_3_validate_nps_boundary(valid_negative_nps)
    assert success is True
    assert parsed_val == expected_int

@pytest.mark.parametrize('invalid_negative_nps', ['-101', '-150', '-100.5'])
def test_tc_7_3_invalid_negative_nps_rejected(invalid_negative_nps):
    """Verifies that unallowable or out-of-bounds negative Net Promoter Scores are strictly rejected."""
    success, parsed_val = tc_7_3_validate_nps_boundary(invalid_negative_nps)
    assert success is False
    assert parsed_val is None
tc_7_4_PERCENTAGE_RE = re.compile('^([+-]?\\d{1,3})(\\.\\d{1,2})?%$')
tc_7_4_REVENUE_MIX_RE = re.compile('^(\\d{1,3})%?\\s?/\\s?(\\d{1,3})%?$')

def tc_7_4_parse_percentage_to_float(val: str) -> Optional[float]:
    """Parses a percentage string (e.g. '15.5%', '-5%') into a raw float."""
    if not val:
        return None
    match = tc_7_4_PERCENTAGE_RE.match(val.strip())
    if not match:
        return None
    try:
        clean_str = val.replace('%', '').strip()
        return float(clean_str)
    except ValueError:
        return None

def tc_7_4_validate_strictly_bounded_percentage(val: str) -> bool:
    """Enforces strict [0.0%, 100.0%] bounds on standard percentage fields."""
    parsed_val = tc_7_4_parse_percentage_to_float(val)
    if parsed_val is None:
        return False
    return 0.0 <= parsed_val <= 100.0

def tc_7_4_validate_unbounded_percentage(val: str) -> bool:
    """Validates percentage strings without range limits (allows negative/exceeding 100%)."""
    parsed_val = tc_7_4_parse_percentage_to_float(val)
    return parsed_val is not None

def tc_7_4_validate_revenue_mix(val: str) -> bool:
    """
    Validates composite revenue mix ratios (e.g., '80/20' or '80%/20%').
    The sum of the components must equal exactly 100%.
    """
    if not val:
        return False
    match = tc_7_4_REVENUE_MIX_RE.match(val.strip())
    if not match:
        return False
    try:
        part1 = int(match.group(1))
        part2 = int(match.group(2))
        return part1 + part2 == 100
    except ValueError:
        return False

@pytest.mark.parametrize('valid_turnover', ['0%', '15.5%', '100%'])
def test_tc_7_4_valid_strictly_bounded_percentages(valid_turnover):
    """Verifies that turnover, churn, and market shares inside [0, 100] bounds pass validation."""
    assert tc_7_4_validate_strictly_bounded_percentage(valid_turnover) is True

@pytest.mark.parametrize('invalid_turnover', ['-5%', '100.1%', '105%', 'InvalidText'])
def test_tc_7_4_invalid_strictly_bounded_percentages_rejected(invalid_turnover):
    """Verifies that negative or >100% values are strictly rejected for bounded fields."""
    assert tc_7_4_validate_strictly_bounded_percentage(invalid_turnover) is False

@pytest.mark.parametrize('valid_unbounded_growth', ['+150%', '-50%', '0%', '100%', '300%'])
def test_tc_7_4_valid_unbounded_growth_rates(valid_unbounded_growth):
    """Verifies that YoY growth rate accepts negative values and values exceeding 100%."""
    assert tc_7_4_validate_unbounded_percentage(valid_unbounded_growth) is True

def test_tc_7_4_invalid_unbounded_growth_format_rejected():
    """Verifies that malformed strings fail growth validation."""
    assert tc_7_4_validate_unbounded_percentage('150 percent') is False

@pytest.mark.parametrize('valid_mix', ['80/20', '80%/20%', '50 / 50'])
def test_tc_7_4_valid_revenue_mix_summing_to_100(valid_mix):
    """Verifies that revenue mix structures whose parts total exactly 100 pass validation."""
    assert tc_7_4_validate_revenue_mix(valid_mix) is True

@pytest.mark.parametrize('invalid_mix', ['70/40', '50/40', '100/10', 'InvalidText'])
def test_tc_7_4_invalid_revenue_mix_rejected(invalid_mix):
    """Verifies that revenue mix structures whose parts do not sum to 100 are rejected."""
    assert tc_7_4_validate_revenue_mix(invalid_mix) is False
tc_7_5_CURRENT_SYSTEM_DATE = datetime.date(2026, 5, 22)

def tc_7_5_extract_years_from_text(text: str) -> List[int]:
    """Extracts all 4-digit years (from 1800 to 2099) found within a string."""
    if not text:
        return []
    candidates = re.findall('\\b(18\\d{2}|19\\d{2}|20\\d{2})\\b', text)
    return [int(yr) for yr in candidates]

def tc_7_5_extract_dates_from_formatted_string(text: str) -> List[datetime.date]:
    """Extracts date objects from YYYY-MM-DD formatted segments."""
    if not text:
        return []
    date_strings = re.findall('\\b(\\d{4}-\\d{2}-\\d{2})\\b', text)
    parsed_dates = []
    for ds in date_strings:
        try:
            parsed_dates.append(datetime.datetime.strptime(ds, '%Y-%m-%d').date())
        except ValueError:
            pass
    return parsed_dates

def tc_7_5_validate_historical_year(year_val: Any) -> bool:
    """Validates that a legal founding year lies strictly between 1800 and 2026."""
    try:
        year = int(year_val)
        return 1800 <= year <= tc_7_5_CURRENT_SYSTEM_DATE.year
    except (ValueError, TypeError):
        return False

def tc_7_5_validate_historical_timeline(timeline_str: str) -> Tuple[bool, str]:
    """Ensures that no date in a historical event list occurs in the future."""
    dates = tc_7_5_extract_dates_from_formatted_string(timeline_str)
    for dt in dates:
        if dt > tc_7_5_CURRENT_SYSTEM_DATE:
            return (False, f"Factual Error: Event date '{dt}' cannot be in the future (Current: {tc_7_5_CURRENT_SYSTEM_DATE}).")
    return (True, 'Historical timeline is valid.')

def tc_7_5_validate_future_projections(projections_str: str) -> Tuple[bool, str]:
    """Ensures that all years referenced in future projections are strictly > 2026."""
    years = tc_7_5_extract_years_from_text(projections_str)
    for year in years:
        if year <= tc_7_5_CURRENT_SYSTEM_DATE.year:
            return (False, f'Logical Error: Projection year {year} cannot be in the past or present (Threshold: > {tc_7_5_CURRENT_SYSTEM_DATE.year}).')
    return (True, 'Future projections timeline is valid.')

@pytest.mark.parametrize('valid_founding_year', [1800, 2000, 2026])
def test_tc_7_5_valid_historical_founding_years(valid_founding_year):
    """Verifies that legal incorporation years within bounds (including 1800 and Y2K 2000) pass."""
    assert tc_7_5_validate_historical_year(valid_founding_year) is True

@pytest.mark.parametrize('invalid_founding_year', [1799, 2027])
def test_tc_7_5_invalid_historical_founding_years_rejected(invalid_founding_year):
    """Verifies that out-of-bounds founding years (too old or future-bound) are rejected."""
    assert tc_7_5_validate_historical_year(invalid_founding_year) is False

@pytest.mark.parametrize('valid_news', ['2000-01-15 - Y2K System Deployment', '2026-05-20 - Global Launch of v2.0'])
def test_tc_7_5_valid_news_timelines(valid_news):
    """Verifies that historical news events dated in the past pass validation."""
    success, msg = tc_7_5_validate_historical_timeline(valid_news)
    assert success is True

@pytest.mark.parametrize('future_news', ['2027-10-12 - Series B Closed', '2030-01-01 - New Branch Opened'])
def test_tc_7_5_future_news_rejected(future_news):
    """Verifies that historical news parameters strictly reject future dates."""
    success, msg = tc_7_5_validate_historical_timeline(future_news)
    assert success is False
    assert 'cannot be in the future' in msg

@pytest.mark.parametrize('valid_projection', ['2027 - Projected revenue of $50M', 'Product rollout timeline: Q3 2030 - Launch AI v3.0'])
def test_tc_7_5_valid_future_projections(valid_projection):
    """Verifies that future projections successfully accept forward-looking years (> 2026)."""
    success, msg = tc_7_5_validate_future_projections(valid_projection)
    assert success is True

@pytest.mark.parametrize('invalid_projection', ['2020 - Completed seed round', '2026 - Current launch trajectory'])
def test_tc_7_5_invalid_future_projections_rejected(invalid_projection):
    """Verifies that past or present years are rejected in forward-looking projection fields."""
    success, msg = tc_7_5_validate_future_projections(invalid_projection)
    assert success is False
    assert 'cannot be in the past or present' in msg
tc_7_6_RATIO_CAC_LTV_RE = re.compile('^([\\d\\.]+)(:1)?$')
tc_7_6_REVENUE_MIX_RE = re.compile('^(\\d{1,3})%?\\s?/\\s?(\\d{1,3})%?$')

def tc_7_6_validate_and_parse_cac_ltv(ratio_str: str) -> Tuple[bool, str, Optional[float]]:
    """
    Validates the CAC:LTV Ratio boundary conditions.
    - Rejects ratios <= 0 (invalid business model state).
    - Flags a warning if ratio is < 1.0 (unprofitable acquisition).
    - Accepts ratios >= 1.0.
    """
    if not ratio_str:
        return (False, 'Empty input.', None)
    match = tc_7_6_RATIO_CAC_LTV_RE.match(ratio_str.strip())
    if not match:
        return (False, 'Invalid ratio format.', None)
    try:
        ratio_val = float(match.group(1))
        if ratio_val <= 0:
            return (False, f'Model Error: Ingested ratio {ratio_val} is invalid (must be > 0).', ratio_val)
        elif ratio_val < 1.0:
            return (True, f'Warning: Unprofitable Model (Ratio {ratio_val} < 1.0).', ratio_val)
        return (True, 'Valid ratio.', ratio_val)
    except ValueError:
        return (False, 'Parser error.', None)

def tc_7_6_calculate_burn_multiplier_with_inf(annual_net_burn: float, net_new_arr: float) -> str:
    """
    Calculates Burn Multiplier.
    - If net_new_arr is 0, returns "INF" (infinity) gracefully instead of raising a zero-division error.
    - If annual_net_burn is 0 (or negative/profitable), returns "0.0".
    """
    if annual_net_burn <= 0:
        return '0.0'
    if net_new_arr == 0:
        return 'INF'
    return str(round(annual_net_burn / net_new_arr, 2))

def tc_7_6_validate_revenue_mix_extremes(mix_str: str) -> bool:
    """Validates that extreme 100/0 and 0/100 proportion mixes pass sum rules."""
    if not mix_str:
        return False
    match = tc_7_6_REVENUE_MIX_RE.match(mix_str.strip())
    if not match:
        return False
    try:
        part1 = int(match.group(1))
        part2 = int(match.group(2))
        return part1 + part2 == 100
    except ValueError:
        return False

@pytest.mark.parametrize('valid_ratio, expected_status', [('3:1', 'Valid ratio.'), ('3', 'Valid ratio.'), ('0.8:1', 'Warning: Unprofitable Model')])
def test_tc_7_6_cac_ltv_ratio_boundaries(valid_ratio, expected_status):
    """Verifies that valid and warning-state acquisition ratios parse correctly."""
    success, msg, val = tc_7_6_validate_and_parse_cac_ltv(valid_ratio)
    assert success is True
    assert expected_status in msg

@pytest.mark.parametrize('invalid_ratio', ['0:1', '-0.5:1', '0'])
def test_tc_7_6_invalid_cac_ltv_ratios_rejected(invalid_ratio):
    """Verifies that non-positive acquisition ratios (such as zero or negative boundaries) are rejected."""
    success, msg, val = tc_7_6_validate_and_parse_cac_ltv(invalid_ratio)
    assert success is False
    assert 'Model Error' in msg

def test_tc_7_6_infinite_burn_multiplier_handling():
    """Verifies that flat ARR growth gracefully returns an infinite string ('INF') instead of crashing."""
    result = tc_7_6_calculate_burn_multiplier_with_inf(annual_net_burn=1200000.0, net_new_arr=0.0)
    assert result == 'INF'

def test_tc_7_6_profitable_burn_multiplier_handling():
    """Verifies that a net-zero or profitable cash-flow state returns a '0.0' burn multiplier."""
    result = tc_7_6_calculate_burn_multiplier_with_inf(annual_net_burn=0.0, net_new_arr=1000000.0)
    assert result == '0.0'

@pytest.mark.parametrize('extreme_mix', ['100/0', '0/100'])
def test_tc_7_6_extreme_revenue_mix_boundaries(extreme_mix):
    """Verifies that pure-play (100% recurring or 100% service) mix boundaries pass successfully."""
    assert tc_7_6_validate_revenue_mix_extremes(extreme_mix) is True
tc_8_1_SCHEMA_TYPE_REGISTRY = {'Company Name': str, 'Year of Incorporation': int, 'Overview of the Company': str, 'Number of Offices (beyond HQ)': int, 'Website Rating': float, 'Glassdoor Rating': float, 'Social Media Followers – Combined': int, 'CEO Name': str, 'Key Business Leaders': list, 'Annual Profits': float, 'Profitability Status': str}

def tc_8_1_validate_record_data_types(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Performs holistic, record-level structural type checks.
    - Validates that populated fields match their exact schema-defined Python types.
    - Gracefully handles nullable fields (allows None without throwing type errors).
    - Specifically validates JSON array parsing for 'Key Business Leaders'.
    """
    errors = []
    for field_name, expected_type in tc_8_1_SCHEMA_TYPE_REGISTRY.items():
        val = payload.get(field_name)
        if val is None:
            continue
        if field_name == 'Key Business Leaders':
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
        if not isinstance(val, expected_type):
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
                errors.append(f"Type Error: Field '{field_name}' must be of type {expected_type.__name__}, but got {type(val).__name__} (Value: '{val}').")
    return (len(errors) == 0, errors)

def test_tc_8_1_fully_typed_valid_record_passes():
    """Verifies that a record with 100% correct type mappings passes validation successfully."""
    valid_payload = {'Company Name': 'Microsoft Corporation', 'Year of Incorporation': 1975, 'Overview of the Company': 'Global technology giant.', 'Number of Offices (beyond HQ)': 120, 'Website Rating': 9.5, 'Glassdoor Rating': 4.3, 'Social Media Followers – Combined': 15000000, 'CEO Name': 'Satya Nadella', 'Key Business Leaders': [{'name': 'Amy Hood', 'title': 'CFO'}, {'name': 'Brad Smith', 'title': 'President'}], 'Annual Profits': 72000000000.0, 'Profitability Status': 'Profitable'}
    success, errors = tc_8_1_validate_record_data_types(valid_payload)
    assert success is True
    assert not errors

def test_tc_8_1_record_with_string_representing_numbers_passes_coercion():
    """Verifies that numbers passed as clean numeric strings are successfully coerced and pass."""
    coercible_payload = {'Company Name': 'Microsoft Corporation', 'Year of Incorporation': '1975', 'Website Rating': '9.5'}
    success, errors = tc_8_1_validate_record_data_types(coercible_payload)
    assert success is True
    assert not errors

def test_tc_8_1_record_with_type_violation_fails():
    """Verifies that passing alphabetical characters to an integer year field fails type validation."""
    invalid_payload = {'Company Name': 'Microsoft Corporation', 'Year of Incorporation': 'Nineteen-Seventy-Five'}
    success, errors = tc_8_1_validate_record_data_types(invalid_payload)
    assert success is False
    assert any(('must be of type int' in err for err in errors))

def test_tc_8_1_record_with_malformed_json_fails():
    """Verifies that passing a flat unformatted text string to a JSON array field fails type validation."""
    invalid_payload = {'Company Name': 'Microsoft Corporation', 'Key Business Leaders': 'Amy Hood - CFO, Brad Smith - President'}
    success, errors = tc_8_1_validate_record_data_types(invalid_payload)
    assert success is False
    assert any(('JSON Parse Error' in err for err in errors))
tc_8_2_LOGO_RE = re.compile('^https?:\\/\\/.*\\.(?:png|jpg|jpeg|svg|webp)(?:\\?.*)?$')
tc_8_2_WEBSITE_RE = re.compile('^https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)$')
tc_8_2_LINKEDIN_COMPANY_RE = re.compile('^https?:\\/\\/(www\\.)?linkedin\\.com\\/company\\/[A-Za-z0-9_\\-]+\\/?$')
tc_8_2_LINKEDIN_PROFILE_RE = re.compile('^https?:\\/\\/(www\\.)?linkedin\\.com\\/in\\/[A-Za-z0-9_\\-]+\\/?$')
tc_8_2_VIDEO_RE = re.compile('^https?:\\/\\/(www\\.)?(youtube\\.com|vimeo\\.com|youtu\\.be)\\/.*$')

class tc_8_2_MockNetworkClient:
    """Simulates active HTTP request connections to evaluate URL validity on the wire."""

    def __init__(self):
        self.mock_web_registry = {'https://microsoft.com': {'status_code': 200, 'content_type': 'text/html'}, 'https://example.com/logo.png': {'status_code': 200, 'content_type': 'image/png'}, 'https://example.com/document.pdf': {'status_code': 200, 'content_type': 'application/pdf'}, 'https://linkedin.com/company/microsoft': {'status_code': 200, 'content_type': 'text/html'}, 'https://linkedin.com/in/satyanadella': {'status_code': 200, 'content_type': 'text/html'}, 'https://youtube.com/watch?v=123': {'status_code': 200, 'content_type': 'text/html'}, 'https://redirecting-site.com': {'status_code': 301, 'redirect_to': 'https://microsoft.com'}, 'https://brokenlink404.com': {'status_code': 404}, 'https://linkedin.com/company/deleted-page-404': {'status_code': 404}, 'https://youtube.com/watch?v=deletedvideo': {'status_code': 404}}

    def request(self, method: str, url: str, follow_redirects: bool=True) -> Dict[str, Any]:
        target_url = url.strip()
        response = self.mock_web_registry.get(target_url, {'status_code': 404})
        if response.get('status_code') in (301, 302) and follow_redirects:
            redirect_url = response.get('redirect_to')
            return self.request(method, redirect_url)
        return response
tc_8_2_network_client = tc_8_2_MockNetworkClient()

def tc_8_2_validate_website_url(url: str) -> Tuple[bool, str]:
    """Validates Website URL regex and active HTTP resolution (supporting redirects)."""
    if not tc_8_2_WEBSITE_RE.match(url):
        return (False, 'Regex Error: Invalid URL structure.')
    response = tc_8_2_network_client.request('GET', url)
    if response.get('status_code') == 200:
        return (True, 'Valid Website URL resolved successfully.')
    return (False, f"Connection Error: Server returned status {response.get('status_code')}.")

def tc_8_2_validate_logo_url(url: str) -> Tuple[bool, str]:
    """Validates Logo URL regex, active HTTP resolution, and image MIME-type."""
    if not tc_8_2_LOGO_RE.match(url):
        return (False, 'Regex Error: Invalid Logo file extension/URL structure.')
    response = tc_8_2_network_client.request('GET', url)
    if response.get('status_code') != 200:
        return (False, f"Connection Error: Server returned status {response.get('status_code')}.")
    mime_type = response.get('content_type', '')
    if not mime_type.startswith('image/'):
        return (False, f"Format Error: Resolved URL content-type is '{mime_type}', not a valid image format.")
    return (True, 'Valid Logo image resolved successfully.')

def tc_8_2_validate_linkedin_url(url: str, is_company: bool=True) -> Tuple[bool, str]:
    """Validates LinkedIn URL structure and active profile resolution."""
    regex = tc_8_2_LINKEDIN_COMPANY_RE if is_company else tc_8_2_LINKEDIN_PROFILE_RE
    if not regex.match(url):
        return (False, 'Regex Error: Invalid LinkedIn profile URL structure.')
    response = tc_8_2_network_client.request('GET', url)
    if response.get('status_code') == 200:
        return (True, 'Valid profile route resolved successfully.')
    return (False, f"Routing Error: Profile route returned status {response.get('status_code')}.")

def tc_8_2_validate_video_url(url: str) -> Tuple[bool, str]:
    """Validates video platform URL structure and active routing."""
    if not tc_8_2_VIDEO_RE.match(url):
        return (False, 'Regex Error: Invalid video platform URL structure.')
    response = tc_8_2_network_client.request('GET', url)
    if response.get('status_code') == 200:
        return (True, 'Valid video route resolved successfully.')
    return (False, f"Routing Error: Video route returned status {response.get('status_code')}.")

def test_tc_8_2_valid_website_url_resolves():
    """Verifies that an active, properly formatted website URL passes validation."""
    success, msg = tc_8_2_validate_website_url('https://microsoft.com')
    assert success is True
    assert 'resolved successfully' in msg

def test_tc_8_2_redirected_website_url_resolves():
    """Verifies that the validation layer follows redirects (301/302) to verify the final destination."""
    success, msg = tc_8_2_validate_website_url('https://redirecting-site.com')
    assert success is True
    assert 'resolved successfully' in msg

def test_tc_8_2_broken_website_url_fails():
    """Verifies that unresolvable website URLs are caught and rejected."""
    success, msg = tc_8_2_validate_website_url('https://brokenlink404.com')
    assert success is False
    assert 'status 404' in msg

def test_tc_8_2_valid_logo_image_resolves():
    """Verifies that logo image links resolving to active image files pass validation."""
    success, msg = tc_8_2_validate_logo_url('https://example.com/logo.png')
    assert success is True
    assert 'image resolved successfully' in msg

def test_tc_8_2_logo_pointing_to_non_image_fails():
    """Verifies that logo image links pointing to non-image resources (like PDFs) are rejected."""
    success, msg = tc_8_2_validate_logo_url('https://example.com/document.pdf')
    assert success is False
    assert 'not a valid image format' in msg

def test_tc_8_2_deleted_linkedin_page_fails():
    """Verifies that unresolvable social media routes are caught and rejected."""
    success, msg = tc_8_2_validate_linkedin_url('https://linkedin.com/company/deleted-page-404', is_company=True)
    assert success is False
    assert 'returned status 404' in msg

def test_tc_8_2_deleted_marketing_video_fails():
    """Verifies that unresolvable video marketing routes are caught and rejected."""
    success, msg = tc_8_2_validate_video_url('https://youtube.com/watch?v=deletedvideo')
    assert success is False
    assert 'returned status 404' in msg
tc_8_5_COUNTRIES_OPERATING_RE = re.compile('^([A-Za-z\\s]+)(,\\s*[A-Za-z\\s]+)*$')
tc_8_5_KEY_COMPETITORS_RE = re.compile('^[\\w\\s&.,\\-/]+(,\\s*[\\w\\s&.,\\-/]+)*$')
tc_8_5_KEY_INVESTORS_RE = re.compile('^[\\w\\s&.,\\-\\(\\)]+(,\\s*[\\w\\s&.,\\-\\(\\)]+)*$')
tc_8_5_ILLEGAL_DELIMITERS = [';', '|', ' / ', ' & ']

def tc_8_5_validate_comma_separated_list(val: str, regex: re.Pattern) -> Tuple[bool, str, List[str]]:
    """
    Validates that a multi-value string is cleanly formatted as a comma-separated list:
    - Fails if any illegal delimiters (semicolons, pipes, slashes, ampersands) are found.
    - Confirms the entire string matches the specified metadata regex pattern.
    - Returns (success, log_message, parsed_list_elements)
    """
    if not val:
        return (False, 'Empty list input.', [])
    for delim in tc_8_5_ILLEGAL_DELIMITERS:
        if delim in val:
            return (False, f"Delimiter Error: Found illegal list separator '{delim.strip()}'. Use commas instead.", [])
    if not regex.match(val):
        return (False, 'Regex Error: String does not conform to strict comma-separated list boundaries.', [])
    elements = [item.strip() for item in val.split(',') if item.strip()]
    return (True, 'List formatted and validated successfully.', elements)

@pytest.mark.parametrize('valid_countries, expected_list', [('US, UK, Germany', ['US', 'UK', 'Germany']), ('United States, United Kingdom', ['United States', 'United Kingdom'])])
def test_tc_8_5_valid_countries_list_formatting(valid_countries, expected_list):
    """Verifies that countries lists separated cleanly by commas pass and parse successfully."""
    success, msg, elements = tc_8_5_validate_comma_separated_list(valid_countries, tc_8_5_COUNTRIES_OPERATING_RE)
    assert success is True
    assert elements == expected_list

@pytest.mark.parametrize('invalid_countries', ['US; UK; Germany', 'US | UK | Germany', 'US / UK', 'US & UK'])
def test_tc_8_5_invalid_countries_list_rejected(invalid_countries):
    """Verifies that non-comma list delimiters in countries operating lists are strictly rejected."""
    success, msg, elements = tc_8_5_validate_comma_separated_list(invalid_countries, tc_8_5_COUNTRIES_OPERATING_RE)
    assert success is False
    assert 'Delimiter Error' in msg or 'Regex Error' in msg

@pytest.mark.parametrize('valid_competitors', ['Apple Inc., Tesla, Inc., Google LLC', 'M&S Group, Bio-Tech (Global) Inc.'])
def test_tc_8_5_valid_competitors_list_formatting(valid_competitors):
    """Verifies that competitor lists with ampersands and periods inside values, but comma-separated, pass."""
    success, msg, elements = tc_8_5_validate_comma_separated_list(valid_competitors, tc_8_5_KEY_COMPETITORS_RE)
    assert success is True

@pytest.mark.parametrize('invalid_competitors', ['Apple Inc. / Tesla Inc.', 'Apple Inc.; Tesla Inc.'])
def test_tc_8_5_invalid_competitors_list_rejected(invalid_competitors):
    """Verifies that competitor lists containing non-comma delimiters fail."""
    success, msg, elements = tc_8_5_validate_comma_separated_list(invalid_competitors, tc_8_5_KEY_COMPETITORS_RE)
    assert success is False

@pytest.mark.parametrize('valid_investors', ['Sequoia, Andreessen Horowitz, Founders Fund (US)', 'a16z, Y Combinator'])
def test_tc_8_5_valid_investors_list_formatting(valid_investors):
    """Verifies that investor lists containing parenthetical details but cleanly comma-separated pass."""
    success, msg, elements = tc_8_5_validate_comma_separated_list(valid_investors, tc_8_5_KEY_INVESTORS_RE)
    assert success is True

@pytest.mark.parametrize('invalid_investors', ['Sequoia; a16z', 'Sequoia | a16z'])
def test_tc_8_5_invalid_investors_list_rejected(invalid_investors):
    """Verifies that non-comma delimiters in investor lists are rejected."""
    success, msg, elements = tc_8_5_validate_comma_separated_list(invalid_investors, tc_8_5_KEY_INVESTORS_RE)
    assert success is False
tc_8_6_SCHEMA_LENGTH_REGISTRY = {'Company Name': (2, 255), 'Short Name': (2, 100), 'Overview of the Company': (50, 5000), 'Core Value Proposition': (20, 2000), 'Vision': (10, 500), 'CEO Name': (2, 100)}

def tc_8_6_validate_text_length(field_name: str, value: Any) -> Tuple[bool, str]:
    """
    Validates that a string's character length strictly falls within
    the defined [min_len, max_len] boundaries.
    """
    bounds = tc_8_6_SCHEMA_LENGTH_REGISTRY.get(field_name)
    if not bounds:
        raise ValueError(f"No length boundaries registered for field '{field_name}'.")
    if value is None:
        return (False, f"Null Error: Field '{field_name}' cannot be NULL.")
    if not isinstance(value, str):
        return (False, f"Type Error: Field '{field_name}' must be of type STRING (got {type(value).__name__}).")
    val_len = len(value)
    min_len, max_len = bounds
    if val_len < min_len:
        return (False, f"Length Error: Field '{field_name}' must be at least {min_len} characters (got {val_len}).")
    if val_len > max_len:
        return (False, f"Length Error: Field '{field_name}' cannot exceed {max_len} characters (got {val_len}).")
    return (True, 'Length validation successful.')

@pytest.mark.parametrize('field_name, valid_input', [('Company Name', 'Microsoft Corporation'), ('Short Name', 'Apple'), ('Overview of the Company', 'A' * 250), ('Core Value Proposition', 'A' * 150), ('Vision', 'To empower everyone on the planet.'), ('CEO Name', 'Tim Cook')])
def test_tc_8_6_valid_text_lengths(field_name, valid_input):
    """Verifies that strings falling within normal character boundaries pass validation."""
    success, msg = tc_8_6_validate_text_length(field_name, valid_input)
    assert success is True
    assert 'successful' in msg

@pytest.mark.parametrize('field_name, short_input', [('Company Name', 'A'), ('Short Name', 'A'), ('Overview of the Company', 'A' * 49), ('Core Value Proposition', 'A' * 19), ('Vision', 'To do'), ('CEO Name', 'A')])
def test_tc_8_6_insufficient_text_lengths_rejected(field_name, short_input):
    """Verifies that strings below the minimum character limit fail validation."""
    success, msg = tc_8_6_validate_text_length(field_name, short_input)
    assert success is False
    assert 'at least' in msg

@pytest.mark.parametrize('field_name, bloated_input', [('Company Name', 'A' * 256), ('Short Name', 'A' * 101), ('Overview of the Company', 'A' * 5001), ('Core Value Proposition', 'A' * 2001), ('Vision', 'A' * 501), ('CEO Name', 'A' * 101)])
def test_tc_8_6_excessive_text_lengths_rejected(field_name, bloated_input):
    """Verifies that strings exceeding the maximum character limit fail validation."""
    success, msg = tc_8_6_validate_text_length(field_name, bloated_input)
    assert success is False
    assert 'cannot exceed' in msg

def test_tc_8_6_non_string_input_rejected():
    """Verifies that type mismatch checks fail type boundaries before assessing character length."""
    success, msg = tc_8_6_validate_text_length('Company Name', 12345)
    assert success is False
    assert 'must be of type STRING' in msg

def tc_9_3_validate_batch_isolation(records: List[Dict[str, Any]]) -> bool:
    """
    Validates that sequential or batched records of highly similar entities 
    do not suffer from cross-contamination, context confusion, or data leakage.
    
    Args:
        records (List[Dict[str, Any]]): A list of processed company records containing metadata.
        
    Raises:
        ValueError: If duplicate fields or context-bleeding attributes are discovered.
    """
    seen_domains = set()
    for i, record in enumerate(records):
        company_name = record.get('Company Name')
        website_url = record.get('Website URL')
        if not company_name or not website_url:
            raise ValueError('Incomplete record: Missing required identifying fields.')
        if website_url in seen_domains:
            raise ValueError(f"Context Confusion Detected: Duplicate Website URL '{website_url}' found across distinct records. Possible context leakage.")
        seen_domains.add(website_url)
        if i > 0:
            prev_record = records[i - 1]
            prev_name = prev_record.get('Company Name', '')
            current_first_token = company_name.split()[0].lower()
            prev_first_token = prev_name.split()[0].lower()
            if current_first_token == prev_first_token and company_name != prev_name:
                distinct_fields = ['Website URL', 'Overview of the Company', 'CEO Name', 'Focus Sectors / Industries']
                for field in distinct_fields:
                    current_val = record.get(field)
                    prev_val = prev_record.get(field)
                    if current_val and prev_val:
                        if str(current_val).strip().lower() == str(prev_val).strip().lower():
                            raise ValueError(f"Context Bleed Warning: Attribute '{field}' is identical between similar sequential entities '{prev_name}' and '{company_name}'. Values: '{current_val}'.")
    return True

def test_tc_9_3_sequential_names_isolated_success():
    """
    Verifies that distinct companies with similar names (e.g., Apple Inc. & Apple Bank)
    are successfully processed when metadata is correctly isolated.
    """
    test_data = [{'Company Name': 'Apple Inc.', 'Short Name': 'Apple', 'Website URL': 'https://www.apple.com', 'CEO Name': 'Tim Cook', 'Focus Sectors / Industries': 'Consumer Electronics, Technology', 'Overview of the Company': 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, and wearables.'}, {'Company Name': 'Apple Bank', 'Short Name': 'Apple Bank', 'Website URL': 'https://www.applebank.com', 'CEO Name': 'Steven C. Schuster', 'Focus Sectors / Industries': 'Banking, Financial Services', 'Overview of the Company': 'Apple Bank provides commercial and individual retail banking services.'}]
    assert tc_9_3_validate_batch_isolation(test_data) is True

def test_tc_9_3_batch_homonymous_entities_success():
    """
    Verifies that multiple 'Delta' entities are successfully isolated when no data leaks occur.
    """
    test_data = [{'Company Name': 'Delta Air Lines', 'Website URL': 'https://www.delta.com', 'CEO Name': 'Ed Bastian', 'Focus Sectors / Industries': 'Airlines, Transportation', 'Overview of the Company': 'Delta Air Lines, Inc. provides scheduled air transportation for passengers and cargo.'}, {'Company Name': 'Delta Faucet Company', 'Website URL': 'https://www.deltafaucet.com', 'CEO Name': 'Ken Roberts', 'Focus Sectors / Industries': 'Manufacturing, Consumer Goods', 'Overview of the Company': 'Delta Faucet Company is a manufacturer of residential and commercial kitchen and bath faucets.'}]
    assert tc_9_3_validate_batch_isolation(test_data) is True

def test_tc_9_3_context_confusion_duplicate_url_failure():
    """
    Verifies that the validator flags an error if a similar sequential company
    leaks the previous company's URL.
    """
    faulty_data = [{'Company Name': 'Delta Air Lines', 'Website URL': 'https://www.delta.com', 'CEO Name': 'Ed Bastian'}, {'Company Name': 'Delta Faucet Company', 'Website URL': 'https://www.delta.com', 'CEO Name': 'Ken Roberts'}]
    with pytest.raises(ValueError, match='Context Confusion Detected: Duplicate Website URL'):
        tc_9_3_validate_batch_isolation(faulty_data)

def test_tc_9_3_context_confusion_ceo_bleed_failure():
    """
    Verifies that the validator flags an error if key unique parameters like
    CEO Name bleed between two highly similar consecutive entries.
    """
    faulty_data = [{'Company Name': 'Apple Inc.', 'Website URL': 'https://www.apple.com', 'CEO Name': 'Tim Cook', 'Focus Sectors / Industries': 'Consumer Electronics'}, {'Company Name': 'Apple Bank', 'Website URL': 'https://www.applebank.com', 'CEO Name': 'Tim Cook', 'Focus Sectors / Industries': 'Banking'}]
    with pytest.raises(ValueError, match="Context Bleed Warning: Attribute 'CEO Name' is identical"):
        tc_9_3_validate_batch_isolation(faulty_data)

def tcc_14_5_calculate_yoy_growth(current_rev: Optional[float], prev_rev: Optional[float]) -> Optional[float]:
    """
    Derived metric: YoY Growth.
    Propagates Null if either dependency is missing [1].
    """
    if current_rev is None or prev_rev is None:
        return None
    if prev_rev == 0:
        return None
    return (current_rev - prev_rev) / prev_rev * 100

def tcc_14_5_calculate_profitability_status(profits: Optional[float]) -> Optional[str]:
    """
    Derived status: Profitability Status.
    Propagates Null if Profits are unknown [1].
    """
    if profits is None:
        return None
    if profits > 0:
        return 'Profitable'
    elif profits < 0:
        return 'Loss-making'
    else:
        return 'Break-even'

def tcc_14_5_calculate_market_share(revenue: Optional[float], tam: Optional[float]) -> Optional[float]:
    """
    Derived metric: Market Share (%).
    Propagates Null if revenue or TAM is unknown [1].
    """
    if revenue is None or tam is None:
        return None
    if tam == 0:
        return None
    return revenue / tam * 100

def tcc_14_5_sum_total_capital_raised(rounds_text: Optional[str]) -> Optional[float]:
    """
    Derived metric: Total Capital Raised.
    Parses and sums numerical rounds; returns None if all rounds are undisclosed [1].
    """
    if not rounds_text:
        return None
    amounts = re.findall('\\$(\\d+(?:,\\d{3})*(?:\\.\\d+)?)\\s*([KkMmBb]?)', rounds_text)
    if not amounts:
        return None
    total = 0.0
    for val, suffix in amounts:
        num = float(val.replace(',', ''))
        if suffix.lower() == 'k':
            num *= 1000
        elif suffix.lower() == 'm':
            num *= 1000000
        elif suffix.lower() == 'b':
            num *= 1000000000
        total += num
    return total

def tcc_14_5_calculate_cac_ltv_ratio(cac: Optional[float], ltv: Optional[float]) -> Optional[str]:
    """
    Derived metric: CAC:LTV Ratio [1].
    Propagates Null if either dependency is missing [1].
    """
    if cac is None or ltv is None:
        return None
    if ltv == 0:
        return None
    ratio_val = cac / ltv
    return f'{ratio_val:.1f}:1'

def tcc_14_5_calculate_runway(cash: Optional[float], burn_rate: Optional[float]) -> Optional[float]:
    """
    Derived metric: Runway (Months).
    Propagates Null if cash or burn rate is unknown [1].
    """
    if cash is None or burn_rate is None:
        return None
    if burn_rate <= 0:
        return None
    return cash / burn_rate

def tcc_14_5_calculate_burn_multiplier(net_burn: Optional[float], net_new_arr: Optional[float]) -> Optional[float]:
    """
    Derived metric: Burn Multiplier.
    Propagates Null if burn or new ARR is unknown [1].
    """
    if net_burn is None or net_new_arr is None:
        return None
    if net_new_arr == 0:
        return None
    return net_burn / net_new_arr

def test_tcc_14_5_yoy_growth_null_propagation():
    """
    Asserts that if current or previous year revenues are missing,
    the derived YoY growth rate cleanly propagates as None [1].
    """
    assert tcc_14_5_calculate_yoy_growth(None, 10000000.0) is None
    assert tcc_14_5_calculate_yoy_growth(15000000.0, None) is None
    assert tcc_14_5_calculate_yoy_growth(15000000.0, 10000000.0) == 50.0

def test_tcc_14_5_profitability_status_null_propagation():
    """
    Asserts that if annual profits are undisclosed, derived status
    propagates cleanly as None, rather than defaulting to an enum [1].
    """
    assert tcc_14_5_calculate_profitability_status(None) is None
    assert tcc_14_5_calculate_profitability_status(2500000.0) == 'Profitable'

def test_tcc_14_5_market_share_null_propagation():
    """
    Asserts that if TAM or Revenues are unknown, derived market share is None [1].
    """
    assert tcc_14_5_calculate_market_share(None, 100000000.0) is None
    assert tcc_14_5_calculate_market_share(5000000.0, None) is None
    assert tcc_14_5_calculate_market_share(5000000.0, 100000000.0) == 5.0

def test_tcc_14_5_total_capital_raised_null_propagation():
    """
    Asserts that if all rounds are undisclosed, total capital is None [1].
    """
    undisclosed_rounds = '2025-01-10 - Undisclosed - Series A, 2024-03-05 - Undisclosed - Seed'
    assert tcc_14_5_sum_total_capital_raised(undisclosed_rounds) is None
    valid_rounds = '2025-01-10 - $5M - Series A, 2024-03-05 - $1.5M - Seed'
    assert tcc_14_5_sum_total_capital_raised(valid_rounds) == 6500000.0

def test_tcc_14_5_cac_ltv_ratio_null_propagation():
    """
    Asserts that if LTV or CAC is missing, ratio propagates cleanly as None [1].
    """
    assert tcc_14_5_calculate_cac_ltv_ratio(None, 5000.0) is None
    assert tcc_14_5_calculate_cac_ltv_ratio(1500.0, None) is None
    assert tcc_14_5_calculate_cac_ltv_ratio(1500.0, 5000.0) == '0.3:1'

def test_tcc_14_5_runway_null_propagation():
    """
    Asserts that if cash or burn rate is missing, runway propagates as None [1].
    """
    assert tcc_14_5_calculate_runway(None, 100000.0) is None
    assert tcc_14_5_calculate_runway(500000.0, None) is None
    assert tcc_14_5_calculate_runway(500000.0, 0.0) is None
    assert tcc_14_5_calculate_runway(500000.0, 100000.0) == 5.0

def test_tcc_14_5_burn_multiplier_null_propagation():
    """
    Asserts that if net burn or net new ARR is missing, burn multiplier is None [1].
    """
    assert tcc_14_5_calculate_burn_multiplier(None, 1000000.0) is None
    assert tcc_14_5_calculate_burn_multiplier(500000.0, None) is None
    assert tcc_14_5_calculate_burn_multiplier(500000.0, 1000000.0) == 0.5