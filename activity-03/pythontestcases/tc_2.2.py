import pytest
from typing import Dict, Any, Tuple, Optional

# Complete 163 schema parameters defined by nullability: False = Mandatory (Not Null), True = Optional (Nullable)
SCHEMA_DEFINITIONS = {
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
    "Mission clarity": True, "Sustainability and CSR": True, "Crisis behavior": True
}

def parse_derived_runway(total_capital: Optional[float], burn_rate: Optional[float]) -> Optional[float]:
    """
    Calculates derived runway metric.
    Safely degrades to None if parent values are missing, avoiding division/null errors.
    """
    if total_capital is None or burn_rate is None:
        return None
    if burn_rate == 0:
        return None
    return round(total_capital / burn_rate, 2)

def evaluate_profile(payload: Dict[str, Any]) -> Tuple[bool, float, Optional[float], str]:
    """
    Validates complete profile payload.
    - Fails if mandatory fields are missing.
    - Calculates overall richness score.
    - Safely evaluates derived financial metrics.
    Returns: (success, richness_percentage, calculated_runway, message)
    """
    total_fields = len(SCHEMA_DEFINITIONS)
    populated_count = 0
    missing_mandatory = []

    for field, is_nullable in SCHEMA_DEFINITIONS.items():
        val = payload.get(field)
        is_populated = False
        
        if val is not None:
            if isinstance(val, str):
                if val.strip() != "":
                    is_populated = True
            else:
                is_populated = True

        if is_populated:
            populated_count += 1
        elif not is_nullable:
            missing_mandatory.append(field)

    richness_score = round((populated_count / total_fields) * 100, 2)

    if missing_mandatory:
        return False, richness_score, None, f"Failed: Mandatory fields missing - {', '.join(missing_mandatory)}"

    # Evaluate derived metric
    raw_capital = payload.get("Total Capital Raised")
    raw_burn = payload.get("Burn Rate")
    runway = parse_derived_runway(raw_capital, raw_burn)

    return True, richness_score, runway, "Profile processed successfully."

def build_minimal_mandatory_profile() -> Dict[str, Any]:
    """Generates a profile with only mandatory fields populated (minimally complete)."""
    minimal_profile = {}
    for field, is_nullable in SCHEMA_DEFINITIONS.items():
        if not is_nullable:
            # Populating mandatory values with basic placeholders
            if "Year" in field:
                minimal_profile[field] = 2026
            elif "followers" in field.lower() or "followers" in field:
                minimal_profile[field] = 500
            elif "URL" in field:
                minimal_profile[field] = "https://example.com"
            else:
                minimal_profile[field] = "Mandatory Text Placeholder"
        else:
            # Optional fields are set explicitly to None
            minimal_profile[field] = None
    return minimal_profile


# --- Pytest Tests ---

def test_minimal_mandatory_profile_passes_validation():
    """Verifies that a profile containing only mandatory fields successfully passes validation."""
    minimal_payload = build_minimal_mandatory_profile()
    success, score, runway, msg = evaluate_profile(minimal_payload)
    
    # 25 mandatory fields out of 163 is roughly 15.34% richness
    assert success is True
    assert score == 15.34
    assert runway is None  # Runway base parameters are missing, should default to None
    assert msg == "Profile processed successfully."

def test_derived_runway_calculation_success():
    """Verifies that runway calculation evaluates correctly when base optional fields are provided."""
    payload = build_minimal_mandatory_profile()
    payload["Total Capital Raised"] = 1200000.0  # Optional field populated
    payload["Burn Rate"] = 100000.0             # Optional field populated
    
    success, score, runway, msg = evaluate_profile(payload)
    
    assert success is True
    assert score == 16.56  # Richness score increases to 27/163 fields
    assert runway == 12.0  # 1,200,000 / 100,000 = 12.0 months

def test_derived_runway_by_zero_handling():
    """Verifies that division-by-zero errors are caught and handled gracefully as None."""
    payload = build_minimal_mandatory_profile()
    payload["Total Capital Raised"] = 100000.0
    payload["Burn Rate"] = 0.0
    
    success, score, runway, msg = evaluate_profile(payload)
    
    assert success is True
    assert runway is None  # Division by zero handled gracefully