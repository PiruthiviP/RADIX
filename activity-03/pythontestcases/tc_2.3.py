import pytest
from typing import Any

# Nullability schema lookup representing all 163 fields from the conceptual setting.
# False = Mandatory (Not Null), True = Optional (Nullable)
SCHEMA_NULLABILITY_REGISTRY = {
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

def simulate_pipeline_extraction(company_name: str) -> dict:
    """
    Simulates a data ingestion pipeline.
    If the target company is non-existent, it returns None/NULL for all 163 fields.
    """
    # List of known companies
    known_entities = {"Microsoft", "Apple", "Tesla", "Google"}
    
    extracted_data = {}
    
    if company_name in known_entities:
        # Simulate populated data payload for valid entities
        for field in SCHEMA_NULLABILITY_REGISTRY.keys():
            extracted_data[field] = "Valid Data"
    else:
        # Entity does not exist: Ingestion pipeline generates NULL for all 163 fields
        for field in SCHEMA_NULLABILITY_REGISTRY.keys():
            extracted_data[field] = None
            
    return extracted_data

def validate_extracted_field(field_name: str, extracted_value: Any) -> bool:
    """
    Validates field input rules:
    - If extracted value is None:
        - Returns True if the field is optional (Nullable = True).
        - Returns False if the field is mandatory (Nullable = False).
    """
    is_nullable = SCHEMA_NULLABILITY_REGISTRY.get(field_name)
    if is_nullable is None:
        raise ValueError(f"Field '{field_name}' not defined in nullability registry.")

    if extracted_value is None:
        return is_nullable

    return True


# --- Pytest Tests ---

@pytest.mark.parametrize("field_name, is_nullable", SCHEMA_NULLABILITY_REGISTRY.items())
def test_non_existent_company_extraction_handling(field_name, is_nullable):
    """
    Systematically verifies parameter behavior when target entity does not exist:
    - Verifies that mandatory parameters reject NULL and raise/return False.
    - Verifies that optional parameters accept NULL and return True.
    """
    # 1. Trigger extraction for a non-existent company
    extracted_payload = simulate_pipeline_extraction("FakeCorpXYZ")
    
    # 2. Extract resolved parameter value (always None for non-existent entities)
    field_value = extracted_payload.get(field_name)
    assert field_value is None, f"Expected {field_name} to be extracted as None, but got {field_value}."
    
    # 3. Validate constraint rules matching schema specifications
    validation_status = validate_extracted_field(field_name, field_value)
    
    assert validation_status == is_nullable, (
        f"Validation failure on '{field_name}' with Nullable={is_nullable}. "
        f"Expected validation response of {is_nullable}, but got {validation_status}."
    )