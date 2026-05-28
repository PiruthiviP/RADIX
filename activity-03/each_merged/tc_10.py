import datetime
import re
from typing import Dict, Any, List, Tuple, Optional
import pytest

# =====================================================================
# Constants and Live Databases (Temporal Baselines as of May 22, 2026)
# =====================================================================

CURRENT_LINE_DATE = datetime.date(2026, 5, 22)

# Mock Live Authority Registry reflecting absolute corporate changes as of May 22, 2026
LIVE_AUTHORITY_REGISTRY = {
    "acmesoft": {
        "Company Name": "Acmesoft Corporation",
        "CEO Name": "Jane Doe",                   # Appointed Q3 2025 (Former CEO was "John Smith")
        "Recent Funding Rounds": "2026-03-10 - Series C - $50M", # Closed in 2026
        "Services / Offerings / Products": "Core AI Suite, CloudDB v2.0 (Released Q1 2026)",
        "Last SEC Filing Date": "2026-04-12"
    }
}

# Mock M&A and Restructuring Registry as of May 22, 2026
LIVE_MA_REGISTRY = {
    "acme corp": {
        "is_acquired": True,
        "acquired_by": "Mega conglomerate",
        "acquisition_date": "2025-11-12",
        "expected_nature": "Subsidiary",
        "post_merger_headcount_min": 1000,
        "required_news_keywords": ["acquired", "acquisition", "merger"]
    },
    "independent startup": {
        "is_acquired": False,
        "expected_nature": "Private",
        "post_merger_headcount_min": 10,
        "required_news_keywords": []
    }
}

# Mock Live Market Database representing the competitive landscape as of May 22, 2026
LIVE_MARKET_DATABASE = {
    "generative ai": {
        "required_disruptors": {"openai", "anthropic", "google", "meta"},
        "defunct_or_acquired": {"cohere-old", "fake-ai-inc"},
        "market_share_caps": {
            "openai": 60.0,
            "anthropic": 25.0
        }
    },
    "web search": {
        "required_disruptors": {"google", "microsoft", "openai"},
        "defunct_or_acquired": {"yahoo", "ask jeeves"},
        "market_share_caps": {
            "google": 78.0  # Disrupted down from 95% by AI search entrants
        }
    }
}

# List of obsolete compliance standards as of May 22, 2026
OBSOLETE_STANDARDS = {
    "ISO27001:2013": "ISO27001:2022"  # Outdated ISO security standard
}

# Mandatory framework keywords required for specific industry categories in 2025/2026
MANDATORY_REGULATORY_KEYWORDS = {
    "critical-infrastructure": {
        "required": ["NIS2", "ISO27001:2022"],
        "fields": ["Regulatory & Compliance Status", "Cybersecurity Posture"]
    },
    "enterprise-supply-chain": {
        "required": ["CSRD", "CSDDD"],
        "fields": ["ESG Practices or Ratings", "Ethical Sourcing Practices"]
    }
}

# Mock Live Crisis Registry as of May 22, 2026
LIVE_CRISIS_REGISTRY = {
    "innovatecorp": {
        "has_layoff_crisis": True,
        "layoff_date": "2025-10-15",
        "layoff_percentage": 25.0,
        "expected_headcount_max": 200,      # Headcount must contract below this limit
        "required_news_keywords": ["layoff", "workforce reduction", "restructuring"]
    },
    "securenet": {
        "has_legal_scandal": True,
        "scandal_type": "Data Breach",
        "scandal_date": "2026-02-05",
        "expected_sentiment_bounds": ["Neutral", "Negative"],
        "required_controversy_keywords": ["breach", "cybersecurity", "unauthorized access"]
    }
}


# =====================================================================
# Temporal Validation & Regulatory Coherence Functions
# =====================================================================

def check_temporal_freshness(ingested_payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates company profile temporal freshness:
    - Scans for out-of-date executive roles (e.g. predecessor CEO before 2025 transition).
    - Verifies that any 2026 funding rounds logged in live databases are not missing.
    - Confirms that recently announced 2026 products are correctly integrated.
    """
    errors = []
    company_name = str(ingested_payload.get("Company Name", "")).strip().lower()
    
    # Resolve company registry
    if company_name not in LIVE_AUTHORITY_REGISTRY:
        errors.append(f"Ingestion Aborted: Company '{ingested_payload.get('Company Name')}' not found in live registry.")
        return False, errors
        
    truth = LIVE_AUTHORITY_REGISTRY[company_name]
    
    # 1. Audit CEO Temporal Freshness (CEO succession occurred in 2025)
    ingested_ceo = ingested_payload.get("CEO Name")
    expected_ceo = truth["CEO Name"]
    if ingested_ceo and ingested_ceo != expected_ceo:
        if ingested_ceo == "John Smith": # Known former CEO (Pre-2025)
            errors.append(
                f"Temporal Decay [CEO Name]: Ingested outdated predecessor CEO 'John Smith' (ousted Q3 2025). "
                f"Factual active CEO is '{expected_ceo}'."
            )
        else:
            errors.append(f"Factual Mismatch [CEO Name]: Ingested '{ingested_ceo}', Expected active CEO '{expected_ceo}'.")

    # 2. Audit Funding Round Freshness (Series C closed in Q1 2026)
    ingested_rounds = str(payload_rounds := ingested_payload.get("Recent Funding Rounds", ""))
    expected_round_sign = "Series C"
    if expected_round_sign not in ingested_rounds:
        errors.append(
            f"Temporal Decay [Recent Funding Rounds]: Missing active 2026 transaction '{expected_round_sign}'. "
            f"Ingested payload only contains outdated historical rounds: '{payload_rounds}'."
        )

    # 3. Audit Product Offerings Freshness (CloudDB v2.0 released in Q1 2026)
    ingested_products = str(payload_products := ingested_payload.get("Services / Offerings / Products", ""))
    expected_product_sign = "CloudDB v2.0"
    if expected_product_sign not in ingested_products:
        errors.append(
            f"Temporal Decay [Services / Offerings / Products]: Missing newly released 2026 product line '{expected_product_sign}'. "
            f"Ingested payload contains stale catalog: '{payload_products}'."
        )

    return len(errors) == 0, errors


def validate_structural_changes(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates company profile structural consistency post-cutoff:
    - If the company was acquired according to the M&A registry:
        1. Nature of Company must be updated to "Subsidiary" (not "Private" or "Partnership").
        2. Employee Size must reflect the combined post-merger headcount (> post_merger_headcount_min).
        3. Recent News must contain references/keywords related to the acquisition.
        4. Exit Strategy/History must document the acquisition event.
    """
    errors = []
    company_name = str(payload.get("Company Name", "")).strip().lower()
    
    if company_name not in LIVE_MA_REGISTRY:
        return True, []
        
    truth = LIVE_MA_REGISTRY[company_name]
    
    if truth["is_acquired"]:
        # 1. Validate Legal Nature transition
        nature = payload.get("Nature of Company")
        expected_nature = truth["expected_nature"]
        if nature != expected_nature:
            errors.append(
                f"Structural Decay [Nature of Company]: Company was acquired in {truth['acquisition_date']} "
                f"and must be classified as '{expected_nature}' (Ingested: '{nature}')."
            )
            
        # 2. Validate Employee Headcount scaling post-merger
        raw_emp_size = str(payload.get("Employee Size", ""))
        clean_emp = re.sub(r"[^\d\-]", "", raw_emp_size)
        emp_count = 0
        if "-" in clean_emp:
            emp_count = int(clean_emp.split("-")[1])
        elif clean_emp:
            emp_count = int(clean_emp)
            
        min_expected = truth["post_merger_headcount_min"]
        if emp_count < min_expected:
            errors.append(
                f"Structural Decay [Employee Size]: Headcount '{raw_emp_size}' is outdated. "
                f"Post-merger combined headcount must be at least {min_expected}."
            )

        # 3. Validate Recent News update
        news_str = str(payload.get("Recent News", "")).lower()
        missing_keywords = [kw for kw in truth["required_news_keywords"] if kw not in news_str]
        if len(missing_keywords) == len(truth["required_news_keywords"]):
            errors.append(
                f"Temporal Lineage Error [Recent News]: Missing any reference to the 2025 acquisition. "
                f"Expected keywords like: {truth['required_news_keywords']}."
            )

        # 4. Validate Exit History documentation
        exit_str = str(payload.get("Exit Strategy/History", "")).lower()
        if "acquired" not in exit_str and "merger" not in exit_str:
            errors.append(
                f"Temporal Lineage Error [Exit Strategy/History]: Exit details must document "
                f"the 2025 acquisition by '{truth['acquired_by']}'."
            )

    return len(errors) == 0, errors


def validate_competitors_freshness(industry_key: str, ingested_competitors: str) -> Tuple[bool, List[str]]:
    """
    Validates that 'Key Competitors' is temporally accurate.
    - Confirms newly emerged disruptors are included in the list.
    - Rejects or flags old, defunct, or acquired competitors.
    """
    errors = []
    industry = LIVE_MARKET_DATABASE.get(industry_key.lower())
    if not industry:
        return True, []
        
    ingested_list = [c.strip().lower() for c in ingested_competitors.split(",") if c.strip()]
    
    # Check 1: Ensure new critical disruptors are mentioned
    missing_disruptors = [d for d in industry["required_disruptors"] if d not in ingested_list]
    if len(missing_disruptors) >= len(industry["required_disruptors"]) - 1:
        errors.append(
            f"Temporal Competitor Error: Ingested competitor list is outdated. "
            f"Failed to include newly emerged dominant disruptors: {missing_disruptors}."
        )
        
    # Check 2: Reject defunct/obsolete competitors
    for defunct in industry["defunct_or_acquired"]:
        if defunct in ingested_list:
            errors.append(f"Obsolete Competitor: Ingested competitor list includes defunct or acquired entity: '{defunct}'.")
            
    return len(errors) == 0, errors


def validate_disrupted_market_share(industry_key: str, company_alias: str, ingested_share_str: str) -> Tuple[bool, str]:
    """
    Enforces that 'Market Share (%)' reflects post-disruption benchmarks.
    - Legacy firms cannot claim legacy monopoly shares if disrupted.
    """
    industry = LIVE_MARKET_DATABASE.get(industry_key.lower())
    if not industry:
        return True, "Industry not in active market monitor."
        
    share_match = re.match(r"^([\d\.]+)\s*%$", ingested_share_str.strip())
    if not share_match:
        return False, f"Format Error: Invalid percentage format '{ingested_share_str}'."
        
    ingested_share = float(share_match.group(1))
    
    max_allowed = industry["market_share_caps"].get(company_alias.lower())
    if max_allowed and ingested_share > max_allowed:
        return False, (
            f"Temporal Accuracy Error: Ingested Market Share ({ingested_share}%) is outdated. "
            f"Following 2025/2026 industry disruption, the maximum registered share for '{company_alias}' is {max_allowed}%."
        )
        
    return True, "Market share verified against current-year bounds."


def validate_peer_benchmarks(benchmark_text: str, industry_key: str) -> Tuple[bool, str]:
    """Ensures that peer comparisons do not reference obsolete/defunct entities."""
    industry = LIVE_MARKET_DATABASE.get(industry_key.lower())
    if not industry:
        return True, "Industry not monitored."
        
    for defunct in industry["defunct_or_acquired"]:
        if re.search(r"\b" + re.escape(defunct) + r"\b", benchmark_text, re.IGNORECASE):
            return False, f"Obsolete Benchmark: Peer comparison references obsolete or defunct entity: '{defunct}'."
            
    return True, "Benchmark peer group is temporally valid."


def audit_regulatory_validity(payload: Dict[str, Any], company_profile_type: str) -> Tuple[bool, List[str]]:
    """
    Scans compliance and policy parameters for temporal regulatory validity:
    1. Rejects obsolete certifications (e.g. ISO27001:2013) and flags the updated replacement framework.
    2. Enforces mandatory 2025/2026 legislative keywords based on company category.
    """
    errors = []
    
    # 1. Scan for Obsolete Standards across all text parameters
    for field_name, value in payload.items():
        if isinstance(value, str):
            for obsolete, replacement in OBSOLETE_STANDARDS.items():
                if obsolete in value:
                    errors.append(
                        f"Temporal Compliance Error in '{field_name}': Stale standard '{obsolete}' is obsolete. "
                        f"Target entity must upgrade and certify under '{replacement}'."
                    )

    # 2. Scan for newly active 2025/2026 mandatory regulations
    rule = MANDATORY_REGULATORY_KEYWORDS.get(company_profile_type.lower())
    if rule:
        required_keywords = rule["required"]
        target_fields = rule["fields"]
        
        combined_text = ""
        for field in target_fields:
            combined_text += " " + str(payload.get(field, "")).lower()
            
        for kw in required_keywords:
            if kw.lower() not in combined_text:
                errors.append(
                    f"Regulatory Compliance Violation: Missing mandatory 2025/2026 compliance framework '{kw}' "
                    f"across evaluated fields: {target_fields}."
                )

    return len(errors) == 0, errors


def validate_crisis_event_coherence(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
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
    company_name = str(payload.get("Company Name", "")).strip().lower()

    if company_name not in LIVE_CRISIS_REGISTRY:
        return True, []

    truth = LIVE_CRISIS_REGISTRY[company_name]

    # --- Case 1: Layoff Crisis Verification ---
    if truth.get("has_layoff_crisis"):
        layoff_history = str(payload.get("Layoff history", ""))
        expected_pct = f"{int(truth['layoff_percentage'])}%"
        if expected_pct not in layoff_history:
            errors.append(
                f"Factual Error [Layoff history]: Missing registered {expected_pct} layoff "
                f"occurring on {truth['layoff_date']}."
            )

        emp_size_str = str(payload.get("Employee Size", ""))
        clean_emp = "".join([c for c in emp_size_str if c.isdigit() or c == "-"])
        emp_count = 0
        if "-" in clean_emp:
            emp_count = int(clean_emp.split("-")[1])
        elif clean_emp:
            emp_count = int(clean_emp)
            
        max_allowed = truth["expected_headcount_max"]
        if emp_count > max_allowed:
            errors.append(
                f"Temporal Mismatch [Employee Size]: Headcount '{emp_size_str}' is outdated. "
                f"Post-layoff headcount must contract below {max_allowed}."
            )

        news_str = str(payload.get("Recent News", "")).lower()
        missing_news_keywords = [kw for kw in truth["required_news_keywords"] if kw not in news_str]
        if len(missing_news_keywords) == len(truth["required_news_keywords"]):
            errors.append(
                f"Temporal Lineage Error [Recent News]: Missing any reference to the 2025 layoff. "
                f"Expected keywords like: {truth['required_news_keywords']}."
            )

    # --- Case 2: Legal / Scandal Crisis Verification ---
    if truth.get("has_legal_scandal"):
        controversies = str(payload.get("Legal Issues / Controversies", "")).lower()
        missing_scandal_keywords = [kw for kw in truth["required_controversy_keywords"] if kw not in controversies]
        if len(missing_scandal_keywords) == len(truth["required_controversy_keywords"]):
            errors.append(
                f"Temporal Lineage Error [Legal Issues / Controversies]: Missing documentation of the 2026 {truth['scandal_type']}. "
                f"Expected keywords like: {truth['required_controversy_keywords']}."
            )

        sentiment = payload.get("Brand Sentiment Score")
        allowed_bounds = truth["expected_sentiment_bounds"]
        if sentiment not in allowed_bounds:
            errors.append(
                f"Temporal Accuracy Error [Brand Sentiment Score]: Corporate sentiment remains '{sentiment}' "
                f"despite a severe {truth['scandal_type']} on {truth['scandal_date']}. Expected: {allowed_bounds}."
            )

        crisis_behavior = str(payload.get("Crisis behavior", ""))
        if not crisis_behavior or crisis_behavior.strip() == "" or "N/A" in crisis_behavior:
            errors.append(
                f"Temporal Lineage Error [Crisis behavior]: Action response is missing or blank "
                f"following the 2026 {truth['scandal_type']}."
            )

    return len(errors) == 0, errors


# =====================================================================
# Unit Tests
# =====================================================================

# --- Tests from tc_10.1.py ---

def test_temporally_fresh_profile_passes():
    """Verifies that a record capturing 2025/2026 updates passes temporal validation."""
    fresh_payload = {
        "Company Name": "Acmesoft",
        "CEO Name": "Jane Doe",
        "Recent Funding Rounds": "2024-01-10 - Series B - $10M, 2026-03-10 - Series C - $50M",
        "Services / Offerings / Products": "Core AI Suite, CloudDB v2.0 (Released Q1 2026)"
    }
    success, errors = check_temporal_freshness(fresh_payload)
    assert success is True
    assert not errors


def test_stale_pre_2025_ceo_mismatch_fails():
    """Verifies that an outdated CEO (pre-2025 transition) is flagged as temporal decay."""
    decayed_payload = {
        "Company Name": "Acmesoft",
        "CEO Name": "John Smith",
        "Recent Funding Rounds": "2024-01-10 - Series B - $10M, 2026-03-10 - Series C - $50M",
        "Services / Offerings / Products": "Core AI Suite, CloudDB v2.0 (Released Q1 2026)"
    }
    success, errors = check_temporal_freshness(decayed_payload)
    assert success is False
    assert any("Temporal Decay [CEO Name]" in err for err in errors)
    assert "ousted Q3 2025" in errors[0]


def test_missing_latest_2026_funding_round_fails():
    """Verifies that a company profile missing a newly completed 2026 round fails validation."""
    decayed_payload = {
        "Company Name": "Acmesoft",
        "CEO Name": "Jane Doe",
        "Recent Funding Rounds": "2024-01-10 - Series B - $10M",
        "Services / Offerings / Products": "Core AI Suite, CloudDB v2.0 (Released Q1 2026)"
    }
    success, errors = check_temporal_freshness(decayed_payload)
    assert success is False
    assert any("Temporal Decay [Recent Funding Rounds]" in err for err in errors)
    assert "Missing active 2026 transaction" in errors[0]


def test_missing_newly_released_2026_product_fails():
    """Verifies that missing a product line launched in early 2026 fails validation."""
    decayed_payload = {
        "Company Name": "Acmesoft",
        "CEO Name": "Jane Doe",
        "Recent Funding Rounds": "2024-01-10 - Series B - $10M, 2026-03-10 - Series C - $50M",
        "Services / Offerings / Products": "Core AI Suite"
    }
    success, errors = check_temporal_freshness(decayed_payload)
    assert success is False
    assert any("Temporal Decay [Services / Offerings / Products]" in err for err in errors)
    assert "Missing newly released 2026 product line" in errors[0]


# --- Tests from tc_10.2.py ---

def test_fresh_restructured_profile_passes():
    """Verifies that a company profile correctly updated to reflect its 2025 acquisition passes validation."""
    valid_record = {
        "Company Name": "Acme Corp",
        "Nature of Company": "Subsidiary",
        "Employee Size": "1000-5000",
        "Recent News": "2025-11-12 - Acme Corp was acquired by Mega conglomerate for $100M",
        "Exit Strategy/History": "Acquired by Mega conglomerate in November 2025"
    }
    success, errors = validate_structural_changes(valid_record)
    assert success is True
    assert not errors


def test_stale_pre_acquisition_profile_fails():
    """Verifies that an outdated profile retaining standalone pre-acquisition parameters fails validation."""
    stale_record = {
        "Company Name": "Acme Corp",
        "Nature of Company": "Private",
        "Employee Size": "11-50",
        "Recent News": "2024-06-15 - Launched version 2.0 platform",
        "Exit Strategy/History": "Targeting independent IPO in the long term"
    }
    success, errors = validate_structural_changes(stale_record)
    assert success is False
    assert any("Structural Decay [Nature of Company]" in err for err in errors)
    assert any("Structural Decay [Employee Size]" in err for err in errors)
    assert any("Temporal Lineage Error [Recent News]" in err for err in errors)
    assert any("Temporal Lineage Error [Exit Strategy/History]" in err for err in errors)


# --- Tests from tc_10.3.py ---

def test_current_competitor_landscape_passes():
    """Verifies that an up-to-date competitor list including active disruptors passes."""
    valid_competitors = "OpenAI, Anthropic, Google, Meta"
    success, errors = validate_competitors_freshness("Generative AI", valid_competitors)
    assert success is True
    assert not errors


def test_outdated_competitor_landscape_fails():
    """Verifies that a competitor list missing newly emerged active disruptors fails validation."""
    outdated_competitors = "CoHere-Old, Fake-AI-Inc"
    success, errors = validate_competitors_freshness("Generative AI", outdated_competitors)
    assert success is False
    assert any("Failed to include newly emerged dominant disruptors" in err for err in errors)
    assert any("Obsolete Competitor" in err for err in errors)


def test_disrupted_monopoly_market_share_fails():
    """Verifies that a legacy search company claiming a pre-disruption 95% share is rejected."""
    success, msg = validate_disrupted_market_share("Web Search", "Google", "95%")
    assert success is False
    assert "outdated" in msg
    assert "maximum registered share" in msg


def test_disrupted_market_share_passes():
    """Verifies that updated market shares following 2025/2026 disruptions pass validation."""
    success, msg = validate_disrupted_market_share("Web Search", "Google", "75%")
    assert success is True


def test_obsolete_peer_benchmark_rejected():
    """Verifies that benchmark narratives comparing the company to defunct legacy entities fail."""
    success, msg = validate_peer_benchmarks("Outperforming Yahoo by 50% in search query volume", "Web Search")
    assert success is False
    assert "Obsolete Benchmark" in msg
    assert "Yahoo" in msg


# --- Tests from tc_10.4.py ---

def test_compliant_modern_profile_passes():
    """Verifies that a company updated to active 2025/2026 standards passes validation."""
    payload = {
        "Regulatory & Compliance Status": "SOC2, HIPAA, ISO27001:2022, NIS2 Compliant",
        "Cybersecurity Posture": "Zero trust architecture conforming strictly to NIS2 Directive."
    }
    success, errors = audit_regulatory_validity(payload, company_profile_type="critical-infrastructure")
    assert success is True
    assert not errors


def test_obsolete_iso_certification_rejected():
    """Verifies that a company claiming an obsolete certification (ISO27001:2013) is rejected."""
    payload = {
        "Regulatory & Compliance Status": "SOC2, HIPAA, ISO27001:2013",
        "Cybersecurity Posture": "Basic security controls implemented."
    }
    success, errors = audit_regulatory_validity(payload, company_profile_type="general")
    assert success is False
    assert any("Stale standard 'ISO27001:2013' is obsolete" in err for err in errors)
    assert "upgrade and certify under 'ISO27001:2022'" in errors[0]


def test_critical_infrastructure_missing_nis2_fails():
    """Verifies that critical infrastructure entities missing the mandatory NIS2 framework fail validation."""
    payload = {
        "Regulatory & Compliance Status": "SOC2, HIPAA, ISO27002:2022",  # Missing mandatory NIS2
        "Cybersecurity Posture": "Standard data encryption active."
    }
    success, errors = audit_regulatory_validity(payload, company_profile_type="critical-infrastructure")
    assert success is False
    assert any("Missing mandatory 2025/2026 compliance framework 'NIS2'" in err for err in errors)


def test_enterprise_supply_chain_missing_csddd_fails():
    """Verifies that large supply chain companies missing CSDDD/CSRD compliance fail validation."""
    payload = {
        "ESG Practices or Ratings": "We focus on green packaging.",
        "Ethical Sourcing Practices": "Fair labor practices expected from partners."
    }
    success, errors = audit_regulatory_validity(payload, company_profile_type="enterprise-supply-chain")
    assert success is False
    assert any("Missing mandatory 2025/2026 compliance framework" in err for err in errors)


# --- Tests from tc_10.5.py ---

def test_fresh_post_crisis_profile_passes():
    """Verifies that a company profile updated to accurately reflect its 2025/2026 crises passes validation."""
    valid_payload = {
        "Company Name": "InnovateCorp",
        "Employee Size": "100-200",
        "Layoff history": "2025-10-15 - 25% of workforce impacted due to restructuring",
        "Recent News": "2025-10-15 - InnovateCorp announced a major workforce reduction of 25%",
        "Crisis behavior": "Managed the 25% RIF transparently with severance packages"
    }
    success, errors = validate_crisis_event_coherence(valid_payload)
    assert success is True
    assert not errors


def test_stale_pre_layoff_profile_fails():
    """Verifies that an outdated profile retaining standalone pre-layoff parameters fails validation."""
    stale_payload = {
        "Company Name": "InnovateCorp",
        "Employee Size": "500-1000",
        "Layoff history": "None",
        "Recent News": "2024-06-15 - Launched version 2.0 platform"
    }
    success, errors = validate_crisis_event_coherence(stale_payload)
    assert success is False
    assert any("Factual Error [Layoff history]" in err for err in errors)
    assert any("Temporal Mismatch [Employee Size]" in err for err in errors)
    assert any("Temporal Lineage Error [Recent News]" in err for err in errors)


def test_stale_reputation_score_fails_on_scandal_company():
    """Verifies that maintaining a 'Positive' sentiment score following a major data breach fails validation."""
    stale_payload = {
        "Company Name": "SecureNet",
        "Brand Sentiment Score": "Positive",
        "Legal Issues / Controversies": "None",
        "Crisis behavior": "N/A"
    }
    success, errors = validate_crisis_event_coherence(stale_payload)
    assert success is False
    assert any("Temporal Accuracy Error [Brand Sentiment Score]" in err for err in errors)
    assert any("Temporal Lineage Error [Legal Issues / Controversies]" in err for err in errors)
    assert any("Temporal Lineage Error [Crisis behavior]" in err for err in errors)