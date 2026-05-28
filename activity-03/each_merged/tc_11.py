import re
from typing import Dict, Any, List, Tuple
import pytest

# =====================================================================
# Constants, Databases, and Regex Patterns
# =====================================================================

# Mock Enterprise Knowledge Base containing distinct corporations sharing identical names/aliases
KNOWLEDGE_BASE = [
    {
        "id": "target_corp_us",
        "legal_name": "Target Corporation",
        "alias": "Target",
        "domain": "target.com",
        "hq_city": "Minneapolis",
        "hq_state_country": "MN",
        "sector": "Retailing",
        "ceo": "Brian Cornell"
    },
    {
        "id": "target_agency_uk",
        "legal_name": "Target Brand Agency Ltd",
        "alias": "Target",
        "domain": "targetagency.co.uk",
        "hq_city": "London",
        "hq_state_country": "UK",
        "sector": "Advertising",
        "ceo": "John Doe"
    }
]

# Mock Corporate Knowledge Base containing Parent/Subsidiary schemas
CORPORATE_RECORDS_DB = {
    "meta platforms, inc.": {
        "type": "Parent",
        "legal_name": "Meta Platforms, Inc.",
        "expected_nature": "Public",
        "verified_ceo": "Mark Zuckerberg",
        "verified_domain": "meta.com",
        "consolidated_revenue_min": 1e11 # $100B+
    },
    "instagram": {
        "type": "Subsidiary",
        "legal_name": "Instagram LLC",
        "expected_nature": "Subsidiary",
        "parent_key": "meta platforms, inc.",
        "verified_ceo": "Adam Mosseri",
        "verified_domain": "instagram.com",
        "standalone_revenue_max": 6e10 # Max $60B estimated
    }
}

# Mock Corporate Knowledge Base containing Global/Regional schemas
GEOGRAPHIC_REGISTRY_DB = {
    "pwc global": {
        "type": "Global Network",
        "legal_name": "PricewaterhouseCoopers International Limited",
        "expected_nature": "Partnership",
        "verified_domain": "pwc.com",
        "consolidated_revenue_min": 5e10, # $50B+
        "consolidated_employee_min": 300000 # 300,000+ employees
    },
    "pwc uk": {
        "type": "Regional Firm",
        "legal_name": "PricewaterhouseCoopers LLP (UK)",
        "expected_nature": "Partnership",
        "parent_key": "pwc global",
        "verified_partner": "Marco Amitrano",       # UK Senior Partner / Regional Head
        "verified_domain": "pwc.co.uk",
        "standalone_revenue_max": 1e10,             # Max £10B estimated standalone
        "standalone_employee_max": 30000,           # Max 30k employees
        "expected_hq": "London"
    }
}

# Mock Registry mapping verified legal names to their corresponding famous acronyms and domains
ACRONYM_REGISTRY = {
    "international business machines corporation": {
        "legal_name": "International Business Machines Corporation",
        "short_name": "IBM",
        "domain": "ibm.com"
    },
    "american telephone & telegraph company": {
        "legal_name": "American Telephone & Telegraph Company",
        "short_name": "AT&T",
        "domain": "att.com"
    },
    "minnesota mining and manufacturing company": {
        "legal_name": "Minnesota Mining and Manufacturing Company",
        "short_name": "3M",
        "domain": "3m.com"
    }
}

# Valid legal name character regex based on schema: ^[\w\s&.,\-\(\)'\u00C0-\u017F]+$
LEGAL_NAME_REGEX = re.compile(r"^[\w\s&.,\-\(\)'\u00C0-\u017F]+$")

# Valid short name character regex based on schema: ^[\w\s&.\-]+$
SHORT_NAME_REGEX = re.compile(r"^[\w\s&.\-]+$")

# Prohibited corporate suffixes inside brand/short names
DISALLOWED_SHORT_NAME_SUFFIXES = ["inc", "inc.", "corp", "corp.", "ltd", "ltd.", "llc", "l.l.c.", "co", "co."]


# =====================================================================
# Disambiguation and Boundary Resolution Functions
# =====================================================================

def resolve_identical_entity_ambiguity(payload: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Holistically disambiguates identical company names using parameter clustering.
    - Compares domain (from Website URL), city/country (from HQ), GICS sector, and CEO.
    - Scores candidates in the Knowledge Base (0 to 4 matches).
    Returns: (resolution_status, resolved_entity_id, log_message)
    """
    company_name = str(payload.get("Company Name", "")).strip().lower()
    website = str(payload.get("Website URL", "")).lower()
    hq = str(payload.get("Company Headquarters", "")).lower()
    sector = str(payload.get("Focus Sectors / Industries", "")).lower()
    ceo = str(payload.get("CEO Name", "")).lower()

    if not company_name:
        return "UNRESOLVED", "None", "Aborted: Empty company name."

    # Filter candidates in knowledge base sharing the same alias/name
    candidates = [c for c in KNOWLEDGE_BASE if c["alias"].lower() == company_name]
    if not candidates:
        return "UNRESOLVED", "None", f"No matching entities found in KB for '{company_name}'."

    scores = {}
    for cand in candidates:
        score = 0
        
        # 1. Match Domain
        if cand["domain"] in website:
            score += 1
            
        # 2. Match Headquarters
        if cand["hq_city"].lower() in hq or cand["hq_state_country"].lower() in hq:
            score += 1
            
        # 3. Match Sector
        if cand["sector"].lower() in sector:
            score += 1
            
        # 4. Match CEO
        if cand["ceo"].lower() == ceo:
            score += 1
            
        scores[cand["id"]] = score

    # Find highest scoring candidate
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_cand_id, best_score = sorted_scores[0]
    
    # Validation logic threshold boundaries:
    if best_score < 2:
        return "UNRESOLVED", "None", f"Ambiguous: Insufficient parameter linkage to resolve '{payload.get('Company Name')}' (Best score: {best_score})."
        
    if len(sorted_scores) > 1:
        runner_up_id, runner_up_score = sorted_scores[1]
        if best_score == runner_up_score or (best_score - runner_up_score < 2 and best_score < 4):
            return "CONFLICT", "None", (
                f"Conflicting payload: High correlation with multiple distinct entities. "
                f"[{best_cand_id}] scored {best_score}, while [{runner_up_id}] scored {runner_up_score}. Holds for audit."
            )

    return "SUCCESS", best_cand_id, f"Resolved successfully to '{best_cand_id}' (Score: {best_score}/4)."


def validate_parent_subsidiary_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates that a subsidiary's profile does not suffer from parent data-bleeding:
    - If the ingested company is a registered Subsidiary:
        1. Nature of Company must be "Subsidiary" (not "Public" or "Private" standalone).
        2. CEO Name must be the subsidiary's distinct head, not the parent's CEO.
        3. Website URL must point to the subsidiary's domain, not the parent's domain.
        4. Annual Revenues must not equal the parent's full consolidated group revenues.
    """
    errors = []
    company_name = str(payload.get("Company Name", "")).strip().lower()

    if company_name not in CORPORATE_RECORDS_DB:
        return True, []
        
    truth = CORPORATE_RECORDS_DB[company_name]

    if truth["type"] == "Subsidiary":
        # 1. Validate Legal Nature
        nature = payload.get("Nature of Company")
        expected_nature = truth["expected_nature"]
        if nature != expected_nature:
            errors.append(
                f"Lineage Contradiction [Nature of Company]: Subsidiary '{payload.get('Company Name')}' "
                f"must be classified as '{expected_nature}' (Ingested: '{nature}')."
            )

        # 2. Prevent CEO Bleeding
        ingested_ceo = payload.get("CEO Name")
        expected_ceo = truth["verified_ceo"]
        parent_truth = CORPORATE_RECORDS_DB[truth["parent_key"]]
        parent_ceo = parent_truth["verified_ceo"]
        
        if ingested_ceo == parent_ceo:
            errors.append(
                f"Data Bleeding Error [CEO Name]: Ingested parent CEO '{parent_ceo}' "
                f"on subsidiary record '{payload.get('Company Name')}'. Expected subsidiary head: '{expected_ceo}'."
            )
        elif ingested_ceo != expected_ceo:
            errors.append(f"Factual Error [CEO Name]: Ingested '{ingested_ceo}', Expected '{expected_ceo}'.")

        # 3. Prevent Domain Bleeding
        ingested_url = str(payload.get("Website URL", "")).lower()
        expected_domain = truth["verified_domain"]
        parent_domain = parent_truth["verified_domain"]
        
        if parent_domain in ingested_url:
            errors.append(
                f"Data Bleeding Error [Website URL]: Ingested parent domain '{parent_domain}' "
                f"on subsidiary record. Expected subsidiary domain: '{expected_domain}'."
            )
        elif expected_domain not in ingested_url:
            errors.append(f"Factual Error [Website URL]: Expected domain '{expected_domain}' in URL.")

        # 4. Prevent Consolidated Revenue Bleeding
        raw_rev = payload.get("Annual Revenues")
        if raw_rev:
            clean_rev = str(raw_rev).replace("$", "").replace(",", "").strip().upper()
            multiplier = 1.0
            if clean_rev.endswith("B"):
                multiplier = 1e9
                clean_rev = clean_rev[:-1]
            elif clean_rev.endswith("M"):
                multiplier = 1e6
                clean_rev = clean_rev[:-1]
                
            try:
                ingested_rev = float(clean_rev) * multiplier
                parent_group_revenue = parent_truth["consolidated_revenue_min"]
                if ingested_rev >= parent_group_revenue:
                    errors.append(
                        f"Data Bleeding Error [Annual Revenues]: Ingested value '{raw_rev}' matches the "
                        f"parent group's consolidated revenues. Subsidiary revenues must represent its standalone estimate."
                    )
            except ValueError:
                pass

    return len(errors) == 0, errors


def parse_currency_to_float(val: Any) -> float:
    """Parses money strings (e.g. '$53B', '£5.8B') into raw floats."""
    if not val:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    clean_str = str(val).replace("$", "").replace("£", "").replace(",", "").strip().upper()
    multiplier = 1.0
    if clean_str.endswith("B"):
        multiplier = 1e9
        clean_str = clean_str[:-1]
    elif clean_str.endswith("M"):
        multiplier = 1e6
        clean_str = clean_str[:-1]
    try:
        return float(clean_str) * multiplier
    except ValueError:
        return 0.0


def parse_headcount_to_int(val: Any) -> int:
    """Parses employee size strings into a representative integer."""
    if not val:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    clean_str = str(val).replace(",", "").replace("+", "").replace(" ", "").strip()
    if "-" in clean_str:
        try:
            return int(clean_str.split("-")[1])
        except (IndexError, ValueError):
            pass
    try:
        return int(clean_str)
    except ValueError:
        return 0


def validate_geographic_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
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
    company_name = str(payload.get("Company Name", "")).strip().lower()

    if company_name not in GEOGRAPHIC_REGISTRY_DB:
        return True, []
        
    truth = GEOGRAPHIC_REGISTRY_DB[company_name]

    if truth["type"] == "Regional Firm":
        # 1. Validate Headquarters Location
        hq = str(payload.get("Company Headquarters", "")).lower()
        expected_hq = truth["expected_hq"].lower()
        if expected_hq not in hq:
            errors.append(
                f"Location Mismatch [Company Headquarters]: Regional firm '{payload.get('Company Name')}' "
                f"must be based in '{truth['expected_hq']}' (Ingested: '{payload.get('Company Headquarters')}')."
            )

        # 2. Prevent Leadership Bleeding
        ingested_ceo = payload.get("CEO Name")
        expected_partner = truth["verified_partner"]
        if ingested_ceo and ingested_ceo != expected_partner:
            errors.append(
                f"Factual Error [CEO Name]: Ingested '{ingested_ceo}' as regional head. "
                f"Expected regional senior partner: '{expected_partner}'."
            )

        # 3. Prevent Domain Bleeding
        ingested_url = str(payload.get("Website URL", "")).lower()
        expected_domain = truth["verified_domain"]
        global_truth = GEOGRAPHIC_REGISTRY_DB[truth["parent_key"]]
        global_domain = global_truth["verified_domain"]
        
        if global_domain in ingested_url and expected_domain not in ingested_url:
            errors.append(
                f"Data Bleeding Error [Website URL]: Ingested global network domain '{global_domain}' "
                f"on regional record. Expected regional domain: '{expected_domain}'."
            )
        elif expected_domain not in ingested_url:
            errors.append(f"Factual Error [Website URL]: Expected domain '{expected_domain}' in URL.")

        # 4. Prevent Consolidated Revenue Bleeding
        raw_rev = payload.get("Annual Revenues")
        if raw_rev:
            ingested_rev = parse_currency_to_float(raw_rev)
            global_network_revenue = global_truth["consolidated_revenue_min"]
            if ingested_rev >= global_network_revenue:
                errors.append(
                    f"Data Bleeding Error [Annual Revenues]: Ingested value '{raw_rev}' matches the "
                    f"consolidated global network revenues. Regional revenues must represent its local standalone footprint."
                )

        # 5. Prevent Consolidated Headcount Bleeding
        raw_emp = payload.get("Employee Size")
        if raw_emp:
            ingested_emp = parse_headcount_to_int(raw_emp)
            global_network_employees = global_truth["consolidated_employee_min"]
            if ingested_emp >= global_network_employees:
                errors.append(
                    f"Data Bleeding Error [Employee Size]: Ingested value '{raw_emp}' matches the "
                    f"consolidated global network headcount. Regional headcount must represent its local standalone footprint."
                )

    return len(errors) == 0, errors


def resolve_and_validate_acronym_coherence(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Resolves and standardizes abbreviation parameters:
    1. If Company Name is passed as an acronym, populates full legal name and stores acronym as Short Name.
    2. If Company Name is passed as a full legal name, automatically populates Short Name if left NULL.
    3. Blocks ingestion if an acronym conflicts with the legal name.
    """
    errors = []
    resolved_payload = payload.copy()
    
    ingested_company = str(payload.get("Company Name", "")).strip()
    ingested_short = str(payload.get("Short Name", "")).strip() if payload.get("Short Name") else ""
    ingested_url = str(payload.get("Website URL", "")).lower()

    by_legal = {k: v for k, v in ACRONYM_REGISTRY.items()}
    by_short = {v["short_name"].lower(): v for k, v in ACRONYM_REGISTRY.items()}

    resolved_entry = None

    # Step 1: Detect by legal name
    if ingested_company.lower() in by_legal:
        resolved_entry = by_legal[ingested_company.lower()]
    # Step 2: Detect by short acronym
    elif ingested_company.lower() in by_short:
        resolved_entry = by_short[ingested_company.lower()]
    # Step 3: Detect by short name parameter
    elif ingested_short.lower() in by_short:
        resolved_entry = by_short[ingested_short.lower()]

    if resolved_entry:
        expected_legal = resolved_entry["legal_name"]
        expected_short = resolved_entry["short_name"]
        
        if ingested_company == expected_short and ingested_short and ingested_short != expected_short:
            errors.append(f"Clash Error: Ingested Short Name '{ingested_short}' conflicts with resolved acronym '{expected_short}'.")
        elif ingested_company == expected_legal and ingested_short and ingested_short != expected_short:
            errors.append(f"Clash Error: Ingested Short Name '{ingested_short}' conflicts with resolved acronym '{expected_short}' for legal entity '{expected_legal}'.")

        expected_domain = resolved_entry["domain"]
        if ingested_url and expected_domain not in ingested_url:
            errors.append(f"Lineage Error: Website URL '{ingested_url}' does not match resolved entity domain '{expected_domain}'.")

        if not errors:
            resolved_payload["Company Name"] = expected_legal
            resolved_payload["Short Name"] = expected_short

    return len(errors) == 0, resolved_payload, errors


def validate_legal_and_short_names(record: Dict[str, Any]) -> bool:
    """
    Validates structural rules and checks for ambiguity between official 
    legal entity names and common brand names.
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
            
        # 3. Disambiguation Check: Suffixes inside Short Name
        tokens = [token.strip(",.").lower() for token in short_name.split()]
        for suffix in DISALLOWED_SHORT_NAME_SUFFIXES:
            if suffix.strip(".") in tokens:
                raise ValueError(
                    f"Ambiguity Error: Short Name '{short_name}' should not contain formal corporate suffixes "
                    f"like '{suffix}' to remain distinct from full legal names."
                )
                
        # 4. Logical Check: Short Name Identity to Legal Name with Suffix
        if short_name.lower() == legal_name.lower() and any(s in legal_name.lower() for s in DISALLOWED_SHORT_NAME_SUFFIXES):
            raise ValueError("Ambiguity Error: 'Short Name' is identical to full legal name. Corporate suffixes must be removed.")

    return True


# =====================================================================
# Unit Tests
# =====================================================================

# --- Tests from tc_11.1.py ---

def test_resolve_retail_target_giant_success():
    """Verifies that the retail giant is successfully resolved when its parameters align."""
    retail_payload = {
        "Company Name": "Target",
        "Website URL": "https://www.target.com",
        "Company Headquarters": "Minneapolis, MN",
        "Focus Sectors / Industries": "Consumer Discretionary, Retailing, Supermarkets",
        "CEO Name": "Brian Cornell"
    }
    status, entity_id, msg = resolve_identical_entity_ambiguity(retail_payload)
    
    assert status == "SUCCESS"
    assert entity_id == "target_corp_us"
    assert "Score: 4/4" in msg


def test_resolve_target_branding_agency_success():
    """Verifies that the branding agency is successfully resolved when its parameters align."""
    agency_payload = {
        "Company Name": "Target",
        "Website URL": "https://targetagency.co.uk",
        "Company Headquarters": "London, UK",
        "Focus Sectors / Industries": "Advertising, Marketing Services",
        "CEO Name": "John Doe"
    }
    status, entity_id, msg = resolve_identical_entity_ambiguity(agency_payload)
    
    assert status == "SUCCESS"
    assert entity_id == "target_agency_uk"
    assert "Score: 4/4" in msg


def test_conflicting_parameters_flags_conflict():
    """Verifies that contradictory parameter mappings trigger a conflict lock."""
    conflicting_payload = {
        "Company Name": "Target",
        "Website URL": "https://www.target.com",
        "Company Headquarters": "Minneapolis, MN",
        "Focus Sectors / Industries": "Advertising, Marketing Services",
        "CEO Name": "John Doe"
    }
    status, entity_id, msg = resolve_identical_entity_ambiguity(conflicting_payload)
    
    assert status == "CONFLICT"
    assert entity_id == "None"
    assert "Conflicting payload" in msg
    assert "target_corp_us" in msg
    assert "target_agency_uk" in msg


def test_insufficient_parameters_unresolved():
    """Verifies that having insufficient populated metadata values fails resolution."""
    scant_payload = {
        "Company Name": "Target",
        "Website URL": "https://unrelated-domain.com",
        "Company Headquarters": "Seattle, WA"
    }
    status, entity_id, msg = resolve_identical_entity_ambiguity(scant_payload)
    
    assert status == "UNRESOLVED"
    assert entity_id == "None"
    assert "Insufficient parameter linkage" in msg


# --- Tests from tc_11.2.py ---

def test_distinct_subsidiary_profile_passes():
    """Verifies that a subsidiary record with distinct, non-bleeding parameters passes validation."""
    valid_payload = {
        "Company Name": "Instagram",
        "Nature of Company": "Subsidiary",
        "CEO Name": "Adam Mosseri",
        "Website URL": "https://www.instagram.com",
        "Annual Revenues": "$50B"
    }
    success, errors = validate_parent_subsidiary_coherence(valid_payload)
    assert success is True
    assert not errors


def test_parent_ceo_bleeding_fails():
    """Verifies that assigning the parent holding company CEO to the subsidiary fails validation."""
    invalid_payload = {
        "Company Name": "Instagram",
        "Nature of Company": "Subsidiary",
        "CEO Name": "Mark Zuckerberg",
        "Website URL": "https://www.instagram.com",
        "Annual Revenues": "$50B"
    }
    success, errors = validate_parent_subsidiary_coherence(invalid_payload)
    assert success is False
    assert any("Data Bleeding Error [CEO Name]" in err for err in errors)
    assert "Mark Zuckerberg" in errors[0]


def test_parent_domain_bleeding_fails():
    """Verifies that assigning the parent domain URL to the subsidiary fails validation."""
    invalid_payload = {
        "Company Name": "Instagram",
        "Nature of Company": "Subsidiary",
        "CEO Name": "Adam Mosseri",
        "Website URL": "https://www.meta.com/instagram",
        "Annual Revenues": "$50B"
    }
    success, errors = validate_parent_subsidiary_coherence(invalid_payload)
    assert success is False
    assert any("Data Bleeding Error [Website URL]" in err for err in errors)
    assert "meta.com" in errors[0]


def test_parent_consolidated_revenue_bleeding_fails():
    """Verifies that assigning parent consolidated group revenues to the subsidiary fails validation."""
    invalid_payload = {
        "Company Name": "Instagram",
        "Nature of Company": "Subsidiary",
        "CEO Name": "Adam Mosseri",
        "Website URL": "https://www.instagram.com",
        "Annual Revenues": "$134B"
    }
    success, errors = validate_parent_subsidiary_coherence(invalid_payload)
    assert success is False
    assert any("Data Bleeding Error [Annual Revenues]" in err for err in errors)


# --- Tests from tc_11.3.py ---

def test_distinct_regional_firm_profile_passes():
    """Verifies that a regional firm record with distinct, non-bleeding parameters passes validation."""
    valid_payload = {
        "Company Name": "PwC UK",
        "Company Headquarters": "London, UK",
        "CEO Name": "Marco Amitrano",
        "Website URL": "https://www.pwc.co.uk",
        "Annual Revenues": "£5.8B",
        "Employee Size": "26,000"
    }
    success, errors = validate_geographic_coherence(valid_payload)
    assert success is True
    assert not errors


def test_global_headcount_bleeding_fails():
    """Verifies that assigning the consolidated global network employee count to the regional firm fails."""
    invalid_payload = {
        "Company Name": "PwC UK",
        "Company Headquarters": "London, UK",
        "CEO Name": "Marco Amitrano",
        "Website URL": "https://www.pwc.co.uk",
        "Annual Revenues": "£5.8B",
        "Employee Size": "360,000"
    }
    success, errors = validate_geographic_coherence(invalid_payload)
    assert success is False
    assert any("Data Bleeding Error [Employee Size]" in err for err in errors)


def test_global_domain_bleeding_fails():
    """Verifies that assigning the global network master domain to the regional firm fails."""
    invalid_payload = {
        "Company Name": "PwC UK",
        "Company Headquarters": "London, UK",
        "CEO Name": "Marco Amitrano",
        "Website URL": "https://www.pwc.com/uk-careers",
        "Annual Revenues": "£5.8B",
        "Employee Size": "26,000"
    }
    success, errors = validate_geographic_coherence(invalid_payload)
    assert success is False
    assert any("Data Bleeding Error [Website URL]" in err for err in errors)


def test_global_consolidated_revenue_bleeding_fails():
    """Verifies that assigning global consolidated network revenues to the regional firm fails."""
    invalid_payload = {
        "Company Name": "PwC UK",
        "Company Headquarters": "London, UK",
        "CEO Name": "Marco Amitrano",
        "Website URL": "https://www.pwc.co.uk",
        "Annual Revenues": "$53B",
        "Employee Size": "26,000"
    }
    success, errors = validate_geographic_coherence(invalid_payload)
    assert success is False
    assert any("Data Bleeding Error [Annual Revenues]" in err for err in errors)


# --- Tests from tc_11.4.py ---

def test_resolve_by_acronym_only_success():
    """Verifies that ingesting with only an acronym successfully populates full legal names."""
    payload = {
        "Company Name": "IBM",
        "Website URL": "https://www.ibm.com"
    }
    success, resolved, errors = resolve_and_validate_acronym_coherence(payload)
    
    assert success is True
    assert resolved["Company Name"] == "International Business Machines Corporation"
    assert resolved["Short Name"] == "IBM"
    assert not errors


def test_resolve_by_legal_name_populates_acronym():
    """Verifies that ingesting with a legal name successfully populates its acronym alias."""
    payload = {
        "Company Name": "American Telephone & Telegraph Company",
        "Website URL": "https://www.att.com",
        "Short Name": None
    }
    success, resolved, errors = resolve_and_validate_acronym_coherence(payload)
    
    assert success is True
    assert resolved["Company Name"] == "American Telephone & Telegraph Company"
    assert resolved["Short Name"] == "AT&T"
    assert not errors


def test_conflicting_aliases_fail_validation():
    """Verifies that pairing an unrelated legal name and acronym fails validation."""
    invalid_payload = {
        "Company Name": "International Business Machines Corporation",
        "Short Name": "AT&T",
        "Website URL": "https://www.ibm.com"
    }
    success, resolved, errors = resolve_and_validate_acronym_coherence(invalid_payload)
    
    assert success is False
    assert any("conflicts with resolved acronym" in err for err in errors)


def test_conflicting_website_domain_fails_validation():
    """Verifies that having a website URL mismatching the resolved entity domain fails validation."""
    invalid_payload = {
        "Company Name": "IBM",
        "Website URL": "https://www.att.com"
    }
    success, resolved, errors = resolve_and_validate_acronym_coherence(invalid_payload)
    
    assert success is False
    assert any("does not match resolved entity domain" in err for err in errors)


# --- Tests from tc_11.5.py ---

def test_meta_platforms_legal_vs_short_success():
    """Ensures that a properly separated Official Legal Name and clean common brand name are accepted."""
    valid_record = {
        "Company Name": "Meta Platforms, Inc.",
        "Short Name": "Meta"
    }
    assert validate_legal_and_short_names(valid_record) is True


def test_x_corp_vs_twitter_disambiguation():
    """Ensures that a rebranded mapping containing legal suffixes in the legal name and a clean short name is accepted."""
    valid_rebranded_record = {
        "Company Name": "X Corp.",
        "Short Name": "Twitter"
    }
    assert validate_legal_and_short_names(valid_rebranded_record) is True


def test_untrimmed_legal_name_fails():
    """Verifies that leading/trailing whitespaces in company name trigger validation failures."""
    invalid_record = {
        "Company Name": " Meta Platforms, Inc. ",
        "Short Name": "Meta"
    }
    with pytest.raises(ValueError, match="must trim leading/trailing spaces"):
        validate_legal_and_short_names(invalid_record)


def test_short_name_containing_legal_suffix_fails():
    """Verifies that corporate legal suffixes inside brand names are flagged to prevent confusion."""
    invalid_record = {
        "Company Name": "Meta Platforms, Inc.",
        "Short Name": "Meta Inc."
    }
    with pytest.raises(ValueError, match="should not contain formal corporate suffixes"):
        validate_legal_and_short_names(invalid_record)


def test_legal_name_regex_disallowed_emojis_fails():
    """Verifies that the legal name fails regex validation if emojis exist."""
    invalid_record = {
        "Company Name": "Meta Platforms, Inc. 🌐",
        "Short Name": "Meta"
    }
    with pytest.raises(ValueError, match="contains disallowed characters or emojis"):
        validate_legal_and_short_names(invalid_record)