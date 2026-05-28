"""
tc_2_all.py — Consolidated Profile Completeness & Dependency Validation Test Suite
Covers:
  TC 2.1 — Profile richness score & mandatory field completeness
  TC 2.2 — Minimal mandatory profile + derived runway metric calculation
  TC 2.3 — Non-existent entity extraction pipeline NULL handling
  TC 2.4 — Per-parameter NULL boundary validation across all 163 fields
  TC 2.5 — Cross-field dependency rule enforcement
"""

import pytest
from typing import Any, Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Shared Schema — 163 fields (False = Mandatory, True = Optional/Nullable)
# Used across TC 2.1, 2.2, 2.3, and 2.4
# ─────────────────────────────────────────────────────────────────────────────

METADATA_SCHEMA: Dict[str, bool] = {
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


# ─────────────────────────────────────────────────────────────────────────────
# TC 2.1 — Profile Richness Score & Mandatory Field Completeness
# ─────────────────────────────────────────────────────────────────────────────

def calculate_profile_richness(payload: Dict[str, Any]) -> Tuple[bool, float, str]:
    """
    Evaluates profile completeness across the full 163-field schema.
    - Fails if any mandatory field is missing/empty.
    - Returns (success, richness_percentage, message).
    """
    total_fields = len(METADATA_SCHEMA)
    populated_count = 0
    missing_mandatory = []

    for field_name, is_nullable in METADATA_SCHEMA.items():
        val = payload.get(field_name)
        is_populated = (
            val is not None and
            (val.strip() != "" if isinstance(val, str) else True)
        )

        if is_populated:
            populated_count += 1
        elif not is_nullable:
            missing_mandatory.append(field_name)

    richness_score = round((populated_count / total_fields) * 100, 2)

    if missing_mandatory:
        return False, richness_score, f"Mandatory fields missing: {', '.join(missing_mandatory)}"

    return True, richness_score, "Profile validated successfully."


def generate_mock_completed_profile() -> Dict[str, Any]:
    """Generates a fully populated mock profile for all 163 fields."""
    mock_profile = {}
    for field_name in METADATA_SCHEMA:
        if "Rating" in field_name or "Score" in field_name:
            mock_profile[field_name] = "5.0"
        elif "Rate" in field_name:
            mock_profile[field_name] = "15%"
        elif "Number" in field_name or "Size" in field_name or "Rank" in field_name:
            mock_profile[field_name] = 100
        elif "Year" in field_name:
            mock_profile[field_name] = 2025
        elif "URL" in field_name or "video" in field_name:
            mock_profile[field_name] = "https://example.com"
        elif "Email" in field_name:
            mock_profile[field_name] = "contact@example.com"
        else:
            mock_profile[field_name] = "Mock populated text data"
    return mock_profile


def test_complete_profile_richness_score_100_percent():
    """A fully populated profile must return a 100% richness score."""
    success, score, msg = calculate_profile_richness(generate_mock_completed_profile())
    assert success is True
    assert score == 100.0
    assert msg == "Profile validated successfully."


def test_missing_mandatory_fields_fails_validation():
    """Removing a mandatory field must fail validation and report it."""
    payload = generate_mock_completed_profile()
    payload.pop("Company Name")
    success, score, msg = calculate_profile_richness(payload)
    assert success is False
    assert "Company Name" in msg
    assert score < 100.0


def test_missing_optional_fields_graceful_degradation():
    """Removing 10 optional fields must degrade richness to ~93.87% but still pass."""
    payload = generate_mock_completed_profile()
    optional_keys = [k for k, nullable in METADATA_SCHEMA.items() if nullable][:10]
    for key in optional_keys:
        payload.pop(key)
    success, score, msg = calculate_profile_richness(payload)
    assert success is True
    assert score == 93.87
    assert "validated successfully" in msg


# ─────────────────────────────────────────────────────────────────────────────
# TC 2.2 — Minimal Mandatory Profile + Derived Runway Calculation
# ─────────────────────────────────────────────────────────────────────────────

def parse_derived_runway(
    total_capital: Optional[float],
    burn_rate: Optional[float],
) -> Optional[float]:
    """
    Calculates derived runway (months).
    Returns None if either input is missing or burn_rate is zero.
    """
    if total_capital is None or burn_rate is None:
        return None
    if burn_rate == 0:
        return None
    return round(total_capital / burn_rate, 2)


def evaluate_profile(
    payload: Dict[str, Any],
) -> Tuple[bool, float, Optional[float], str]:
    """
    Full profile evaluation:
    - Validates mandatory field presence.
    - Computes richness score.
    - Computes derived runway from optional financial fields.
    Returns: (success, richness_percentage, calculated_runway, message).
    """
    total_fields = len(METADATA_SCHEMA)
    populated_count = 0
    missing_mandatory = []

    for field, is_nullable in METADATA_SCHEMA.items():
        val = payload.get(field)
        is_populated = (
            val is not None and
            (val.strip() != "" if isinstance(val, str) else True)
        )
        if is_populated:
            populated_count += 1
        elif not is_nullable:
            missing_mandatory.append(field)

    richness_score = round((populated_count / total_fields) * 100, 2)

    if missing_mandatory:
        return False, richness_score, None, \
            f"Failed: Mandatory fields missing - {', '.join(missing_mandatory)}"

    runway = parse_derived_runway(
        payload.get("Total Capital Raised"),
        payload.get("Burn Rate"),
    )
    return True, richness_score, runway, "Profile processed successfully."


def build_minimal_mandatory_profile() -> Dict[str, Any]:
    """Builds a profile with only mandatory fields populated; optional fields set to None."""
    profile = {}
    for field, is_nullable in METADATA_SCHEMA.items():
        if not is_nullable:
            if "Year" in field:
                profile[field] = 2026
            elif "URL" in field:
                profile[field] = "https://example.com"
            else:
                profile[field] = "Mandatory Text Placeholder"
        else:
            profile[field] = None
    return profile


def test_minimal_mandatory_profile_passes_validation():
    """A profile with only mandatory fields must pass with ~15.34% richness and no runway."""
    success, score, runway, msg = evaluate_profile(build_minimal_mandatory_profile())
    assert success is True
    assert score == 15.34
    assert runway is None
    assert msg == "Profile processed successfully."


def test_derived_runway_calculation_success():
    """Runway must calculate correctly when Total Capital Raised and Burn Rate are provided."""
    payload = build_minimal_mandatory_profile()
    payload["Total Capital Raised"] = 1_200_000.0
    payload["Burn Rate"] = 100_000.0
    success, score, runway, msg = evaluate_profile(payload)
    assert success is True
    assert score == 16.56
    assert runway == 12.0


def test_derived_runway_by_zero_handling():
    """Runway must return None gracefully when Burn Rate is zero."""
    payload = build_minimal_mandatory_profile()
    payload["Total Capital Raised"] = 100_000.0
    payload["Burn Rate"] = 0.0
    success, score, runway, msg = evaluate_profile(payload)
    assert success is True
    assert runway is None


# ─────────────────────────────────────────────────────────────────────────────
# TC 2.3 — Non-Existent Entity Extraction Pipeline NULL Handling
# ─────────────────────────────────────────────────────────────────────────────

KNOWN_ENTITIES = {"Microsoft", "Apple", "Tesla", "Google"}


def simulate_pipeline_extraction(company_name: str) -> Dict[str, Any]:
    """
    Simulates a data ingestion pipeline.
    Known companies return populated data; unknown companies return None for all fields.
    """
    if company_name in KNOWN_ENTITIES:
        return {field: "Valid Data" for field in METADATA_SCHEMA}
    return {field: None for field in METADATA_SCHEMA}


def validate_extracted_field(field_name: str, extracted_value: Any) -> bool:
    """
    Validates a single extracted field against the schema nullability rules.
    None is accepted for optional fields; rejected for mandatory fields.
    """
    is_nullable = METADATA_SCHEMA.get(field_name)
    if is_nullable is None:
        raise ValueError(f"Field '{field_name}' not defined in schema.")
    if extracted_value is None:
        return is_nullable
    return True


@pytest.mark.parametrize("field_name, is_nullable", METADATA_SCHEMA.items())
def test_non_existent_company_extraction_handling(field_name, is_nullable):
    """
    For a non-existent company all extracted values are None.
    Mandatory fields must return False; optional fields must return True.
    """
    extracted_payload = simulate_pipeline_extraction("FakeCorpXYZ")
    field_value = extracted_payload.get(field_name)
    assert field_value is None, \
        f"Expected '{field_name}' to be None, got {field_value!r}."
    validation_status = validate_extracted_field(field_name, field_value)
    assert validation_status == is_nullable, (
        f"Validation failure on '{field_name}' (Nullable={is_nullable}). "
        f"Expected {is_nullable}, got {validation_status}."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TC 2.4 — Per-Parameter NULL Boundary Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_mandatory_and_optional_rules(field_name: str, value: Any) -> bool:
    """
    Returns True if the value satisfies the field's nullability rule:
    - None allowed only for nullable/optional fields.
    - Any non-None value always passes.
    """
    is_nullable = METADATA_SCHEMA.get(field_name)
    if is_nullable is None:
        raise ValueError(f"Field '{field_name}' not defined in METADATA_SCHEMA.")
    if value is None:
        return is_nullable
    return True


@pytest.mark.parametrize("field_name, is_nullable", METADATA_SCHEMA.items())
def test_null_value_completeness_boundaries(field_name, is_nullable):
    """
    Mandatory fields (is_nullable=False) must reject None.
    Optional fields (is_nullable=True) must accept None.
    """
    actual   = validate_mandatory_and_optional_rules(field_name, None)
    expected = is_nullable
    assert actual == expected, (
        f"Boundary mismatch on '{field_name}' (Nullable={is_nullable}). "
        f"Expected {expected}, got {actual}."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TC 2.5 — Cross-Field Dependency Rule Enforcement
# ─────────────────────────────────────────────────────────────────────────────

def validate_field_dependencies(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Enforces cross-field dependency rules:
    1. CEO Name <-> CEO LinkedIn URL (bidirectional).
    2. CAC + CLV present -> CAC:LTV Ratio must be populated.
    3. Burn Rate + Total Capital Raised (>0) -> Runway must be populated.
    4. Recent Funding Rounds -> Total Capital Raised must be populated.
    5. Market Share (%) -> Annual Revenues must be populated.
    """
    errors = []

    def is_filled(field: str) -> bool:
        val = payload.get(field)
        if val is None:
            return False
        if isinstance(val, str) and val.strip() == "":
            return False
        return True

    # Rule 1: CEO Name <-> CEO LinkedIn URL
    if is_filled("CEO Name") and not is_filled("CEO LinkedIn URL"):
        errors.append("CEO LinkedIn URL must be populated when CEO Name is present.")
    if is_filled("CEO LinkedIn URL") and not is_filled("CEO Name"):
        errors.append("CEO Name must be populated when CEO LinkedIn URL is present.")

    # Rule 2: CAC & CLV -> CAC:LTV Ratio
    if is_filled("Customer Acquisition Cost (CAC)") and is_filled("Customer Lifetime Value (CLV)"):
        if not is_filled("CAC:LTV Ratio"):
            errors.append("CAC:LTV Ratio must be populated when both CAC and CLV are present.")

    # Rule 3: Burn Rate & Total Capital Raised -> Runway
    if is_filled("Burn Rate") and is_filled("Total Capital Raised"):
        try:
            if float(payload.get("Burn Rate", 0)) > 0 and not is_filled("Runway"):
                errors.append("Runway must be populated when Burn Rate and Total Capital Raised are present.")
        except (ValueError, TypeError):
            pass  # Non-numeric burn rate; skip rule

    # Rule 4: Recent Funding Rounds -> Total Capital Raised
    if is_filled("Recent Funding Rounds") and not is_filled("Total Capital Raised"):
        errors.append("Total Capital Raised must be populated when Recent Funding Rounds are documented.")

    # Rule 5: Market Share (%) -> Annual Revenues
    if is_filled("Market Share (%)") and not is_filled("Annual Revenues"):
        errors.append("Annual Revenues must be populated when Market Share (%) is present.")

    return len(errors) == 0, errors


def test_dependent_fields_all_present_passes():
    """Validation must pass when all dependent field groups are fully populated."""
    valid_payload = {
        "CEO Name": "Satya Nadella",
        "CEO LinkedIn URL": "https://linkedin.com/in/satyanadella",
        "Customer Acquisition Cost (CAC)": 100,
        "Customer Lifetime Value (CLV)": 300,
        "CAC:LTV Ratio": "3:1",
        "Burn Rate": 50_000,
        "Total Capital Raised": 10_000_000,
        "Runway": 10,
        "Recent Funding Rounds": "2025-01-01 - Series A - $10M",
        "Market Share (%)": "5%",
        "Annual Revenues": "$100M",
    }
    success, errors = validate_field_dependencies(valid_payload)
    assert success is True
    assert not errors


def test_missing_ceo_linkedin_fails_dependency():
    """CEO Name without CEO LinkedIn URL must raise a dependency error."""
    payload = {"CEO Name": "Satya Nadella", "CEO LinkedIn URL": None}
    success, errors = validate_field_dependencies(payload)
    assert success is False
    assert any("CEO LinkedIn URL must be populated" in e for e in errors)


def test_missing_derived_ratio_fails_dependency():
    """CAC and CLV without CAC:LTV Ratio must raise a dependency error."""
    payload = {
        "Customer Acquisition Cost (CAC)": 100,
        "Customer Lifetime Value (CLV)": 300,
        "CAC:LTV Ratio": None,
    }
    success, errors = validate_field_dependencies(payload)
    assert success is False
    assert any("CAC:LTV Ratio must be populated" in e for e in errors)


def test_missing_annual_revenues_fails_market_share_dependency():
    """Market Share (%) without Annual Revenues must raise a dependency error."""
    payload = {"Market Share (%)": "5%", "Annual Revenues": None}
    success, errors = validate_field_dependencies(payload)
    assert success is False
    assert any("Annual Revenues must be populated" in e for e in errors)