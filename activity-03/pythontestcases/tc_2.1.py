import pytest
from typing import Dict, Any, Tuple

#Completeness & Dependency Rules
# All 163 metadata schema parameters mapped with their nullability (False = Mandatory, True = Optional)
METADATA_SCHEMA = {
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

def calculate_profile_richness(payload: Dict[str, Any]) -> Tuple[bool, float, str]:
    """
    Evaluates profile completeness across the complete 163-field schema.
    - Ensures all mandatory fields (nullable=False) are present and non-empty.
    - Computes a percentage richness score based on both optional and mandatory presence.
    - Returns (validation_success, richness_percentage, error_message).
    """
    total_fields = len(METADATA_SCHEMA)
    populated_count = 0
    missing_mandatory = []

    for field_name, is_nullable in METADATA_SCHEMA.items():
        val = payload.get(field_name)
        
        # Determine if field is considered populated (non-null and non-whitespace string)
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
            # Field is mandatory and missing
            missing_mandatory.append(field_name)

    richness_score = round((populated_count / total_fields) * 100, 2)

    if missing_mandatory:
        error_msg = f"Mandatory fields missing: {', '.join(missing_mandatory)}"
        return False, richness_score, error_msg

    return True, richness_score, "Profile validated successfully."

def generate_mock_completed_profile() -> Dict[str, Any]:
    """Generates a mock profile payload with all 163 fields populated with valid placeholder values."""
    mock_profile = {}
    for field_name, is_nullable in METADATA_SCHEMA.items():
        # Assign typical mock data depending on the key name patterns
        if "Rating" in field_name or "Rate" in field_name or "Score" in field_name:
            mock_profile[field_name] = "5.0" if "Rating" in field_name else "15%"
        elif "Number" in field_name or "Size" in field_name or "Year" in field_name or "Rank" in field_name:
            mock_profile[field_name] = 2025 if "Year" in field_name else 100
        elif "URL" in field_name or "video" in field_name:
            mock_profile[field_name] = "https://example.com"
        elif "Email" in field_name:
            mock_profile[field_name] = "contact@example.com"
        else:
            mock_profile[field_name] = "Mock populated text data"
    return mock_profile


# --- Pytest Tests ---

def test_complete_profile_richness_score_100_percent():
    """Verifies that a fully populated profile returns exactly a 100% data richness score."""
    full_payload = generate_mock_completed_profile()
    success, score, msg = calculate_profile_richness(full_payload)
    
    assert success is True
    assert score == 100.0
    assert msg == "Profile validated successfully."

def test_missing_mandatory_fields_fails_validation():
    """Verifies that missing any mandatory field fails validation even if other fields are populated."""
    payload = generate_mock_completed_profile()
    # Remove mandatory field
    payload.pop("Company Name")
    
    success, score, msg = calculate_profile_richness(payload)
    
    assert success is False
    assert "Company Name" in msg
    # Score should drop by 1/163 fields (~0.61%)
    assert score < 100.0

def test_missing_optional_fields_graceful_degradation():
    """Verifies that missing optional fields degrades the richness score but passes schema validation."""
    payload = generate_mock_completed_profile()
    
    # Remove 10 optional fields
    optional_keys_to_remove = [k for k, is_nullable in METADATA_SCHEMA.items() if is_nullable][:10]
    for key in optional_keys_to_remove:
        payload.pop(key)
        
    success, score, msg = calculate_profile_richness(payload)
    
    assert success is True
    # 153 out of 163 fields populated (~93.87%)
    assert score == 93.87
    assert "validated successfully" in msg