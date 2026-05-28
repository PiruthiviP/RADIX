import pytest
from typing import Dict, Any, List, Tuple

# Mock Corporate Knowledge Base containing strict Global/Regional schemas
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
        return True, [] # Skip if company is not modeled in the registry
        
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


# --- Pytest Tests ---

def test_distinct_regional_firm_profile_passes():
    """Verifies that a regional firm record with distinct, non-bleeding parameters passes validation."""
    valid_payload = {
        "Company Name": "PwC UK",
        "Company Headquarters": "London, UK",
        "CEO Name": "Marco Amitrano",  # Correct UK senior partner
        "Website URL": "https://www.pwc.co.uk",  # Correct regional domain
        "Annual Revenues": "£5.8B",  # Correct regional standalone revenue
        "Employee Size": "26,000"  # Correct regional headcount
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
        "Employee Size": "360,000"  # Global network headcount (Data bleeding)
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
        "Website URL": "https://www.pwc.com/uk-careers",  # Global domain (Data bleeding)
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
        "Annual Revenues": "$53B",  # Global network revenue (Data bleeding)
        "Employee Size": "26,000"
    }
    success, errors = validate_geographic_coherence(invalid_payload)
    assert success is False
    assert any("Data Bleeding Error [Annual Revenues]" in err for err in errors)