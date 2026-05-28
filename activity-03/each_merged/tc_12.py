import re
from typing import Dict, Any, Union, Set
import pytest

# =====================================================================
# Constants, Registries, and Regex Patterns
# =====================================================================

CATEGORY_REGEX = re.compile(r"^(Startup|MSME|SMB|Enterprise|Investor|VC|Conglomerate)$")
INDUSTRY_REGEX = re.compile(r"^[\w\s&.,\-/]+$")
NATURE_OF_COMPANY_REGEX = re.compile(r"^(Private|Public|Subsidiary|Partnership|Non-Profit|Govt)$")
BRAND_SENTIMENT_REGEX = re.compile(r"^(Positive|Neutral|Negative)$|^\d{1,3}$")
GLASSDOOR_REGEX = re.compile(r"^[1-5](\.\d)?$")
NPS_REGEX = re.compile(r"^-?(100|[1-9]\d?|0)$")
CONCENTRATION_REGEX = re.compile(r"^(Yes|No|High|Low)(.*)$", re.IGNORECASE)
BURNOUT_REGEX = re.compile(r"^(Low|Medium|High|Severe)(.*)$", re.IGNORECASE)

INDUSTRY_MASTER_LIST: Set[str] = {
    "Financial Technology", "Payments", "Automotive", "Clean Energy", 
    "Energy Storage", "E-commerce", "Cloud Computing", "Software", 
    "Retail", "Technology", "Healthcare", "Financials"
}

PRODUCT_SECTOR_KEYWORDS = {
    "payment": ["financial technology", "payments", "financials"],
    "billing": ["financial technology", "payments", "financials"],
    "card": ["financial technology", "payments", "financials"],
    "vehicle": ["automotive"],
    "car": ["automotive"],
    "solar": ["clean energy"],
    "battery": ["energy storage", "clean energy"],
    "retail": ["e-commerce", "retail"],
    "web services": ["cloud computing", "technology", "software"],
    "aws": ["cloud computing", "technology", "software"]
}

PARENT_OWNERSHIP_KEYWORDS = ["owned by", "subsidiary of", "acquired by", "part of", "division of"]


# =====================================================================
# Parsing & Validation Core Logic
# =====================================================================

def parse_employee_size(emp_size: Union[str, int]) -> int:
    """
    Parses exact headcount or headcount ranges to extract the maximum upper limit.
    Example: '11-50' -> 50, '500+' -> 500, 150 -> 150
    """
    if isinstance(emp_size, int):
        return emp_size
        
    cleaned = str(emp_size).strip().replace(",", "")
    
    # Range check e.g. "11-50"
    range_match = re.match(r"^(\d+)-(\d+)$", cleaned)
    if range_match:
        return int(range_match.group(2))
        
    # Standard digital extraction
    digits = re.findall(r"\d+", cleaned)
    if digits:
        return int(digits[0])
        
    return 0


def validate_company_classification(record: Dict[str, Any]) -> bool:
    """
    Validates category constraints and enforces cross-field business logic 
    relating Category, Employee Size, and Company Maturity.
    """
    category = record.get("Category")
    employee_size = record.get("Employee Size")
    maturity = record.get("Company maturity")
    
    # 1. Nullability & Case Normalization
    if not category:
        raise ValueError("Field Validation Error: 'Category' is Not Null.")
        
    # Attempt normalization for case-insensitive matches
    normalized_cat = category.strip().title()
    # Special handling for acronyms
    if normalized_cat.lower() == "vc":
        normalized_cat = "VC"
    elif normalized_cat.lower() == "msme":
        normalized_cat = "MSME"
        
    if not CATEGORY_REGEX.match(normalized_cat):
        raise ValueError(f"Regex Pattern Error: '{category}' is not a valid standardized business taxonomy enum.")
        
    # Assign back normalized category for downstream accuracy
    record["Category"] = normalized_cat
    
    # 2. Extract numeric headcount for logical checks
    num_employees = parse_employee_size(employee_size) if employee_size else 0
    
    # 3. Cross-Field Business Logic Rules
    # Rule A: If category is MSME, headcount must not exceed standard global SMB definitions (typically under 250)
    if normalized_cat == "MSME" and num_employees > 250:
        raise ValueError(
            f"Classification Mismatch: Entity classified as 'MSME' has too many employees ({num_employees}). "
            f"Expected <= 250."
        )
        
    # Rule B: A 'Startup' should not have mature enterprise-scale employee levels (e.g., over 500 employees)
    if normalized_cat == "Startup" and num_employees > 500:
        raise ValueError(
            f"Classification Mismatch: 'Startup' classification is invalid for "
            f"enterprise-scale headcount of {num_employees}."
        )
        
    # Rule C: Validate logical harmony between Category and Company Maturity if both are present
    if maturity:
        if normalized_cat == "Enterprise" and maturity == "Startup":
            raise ValueError("Logical Error: 'Enterprise' category cannot align with a 'Startup' maturity level.")
        if normalized_cat == "Startup" and maturity == "Mature":
            raise ValueError("Logical Error: 'Startup' category cannot align with a 'Mature' maturity level.")
            
    return True


def validate_industry_classification(record: Dict[str, Any]) -> bool:
    """
    Validates formatting and GICS alignment of the 'Focus Sectors / Industries' field,
    and checks consistency against actual company products/services.
    """
    sectors_string = record.get("Focus Sectors / Industries")
    products_string = record.get("Services / Offerings / Products")
    
    # 1. Nullability Check
    if not sectors_string:
        raise ValueError("Field Validation Error: 'Focus Sectors / Industries' is Not Null.")
        
    # 2. Regex Format Validation
    if not INDUSTRY_REGEX.match(sectors_string):
        raise ValueError(
            f"Regex Pattern Error: '{sectors_string}' contains invalid characters. "
            f"Expected only alphanumeric, spaces, commas, hyphens, slashes, ampersands, and periods."
        )
        
    # 3. Industry Master List Verification
    # Split by comma and clean whitespace
    sectors = [s.strip() for s in sectors_string.split(",") if s.strip()]
    
    for sector in sectors:
        if sector not in INDUSTRY_MASTER_LIST:
            raise ValueError(
                f"Taxonomy Error: Sector '{sector}' does not exist in the standardized Industry Master List."
            )
            
    # 4. Cross-Field Semantic Consistency Check
    if products_string:
        normalized_products = products_string.lower()
        normalized_sectors = [s.lower() for s in sectors]
        
        # Verify if product keywords demand specific GICS categories
        for keyword, required_sectors in PRODUCT_SECTOR_KEYWORDS.items():
            if keyword in normalized_products:
                # Check if at least one expected sector matches the classification
                if not any(req in normalized_sectors for req in required_sectors):
                    raise ValueError(
                        f"Semantic Inconsistency: Products include '{keyword}' indications, "
                        f"but Focus Sectors '{sectors_string}' lack related categories: {required_sectors}."
                    )
                    
    return True


def validate_nature_of_company(record: Dict[str, Any]) -> bool:
    """
    Validates formatting and enum compliance of 'Nature of Company',
    and checks consistency against funding rounds and description summaries.
    """
    nature = record.get("Nature of Company")
    company_name = record.get("Company Name")
    funding_rounds = record.get("Recent Funding Rounds")
    overview = record.get("Overview of the Company")
    
    # 1. Nullability Check
    if not nature:
        raise ValueError("Field Validation Error: 'Nature of Company' is Not Null.")
        
    # 2. Case Normalization to Match Regex
    normalized_nature = nature.strip().title()
    if normalized_nature == "Non-Profit" or normalized_nature == "Nonprofit":
        normalized_nature = "Non-Profit"
        
    if not NATURE_OF_COMPANY_REGEX.match(normalized_nature):
        raise ValueError(
            f"Regex Pattern Error: '{nature}' is not a recognized legal structure enum. "
            f"Expected: Private, Public, Subsidiary, Partnership, Non-Profit, Govt."
        )
        
    # Write back normalized value
    record["Nature of Company"] = normalized_nature
    
    # 3. Cross-Field Business Logic Validation
    # Rule A: Publicly traded companies do not raise typical startup venture series rounds
    if normalized_nature == "Public" and funding_rounds:
        # Check if the funding rounds text contains venture indicators (Series A/B/C/D, Seed)
        venture_pattern = re.compile(r"(Series\s+[A-Z]|Seed|Angel)", re.IGNORECASE)
        if venture_pattern.search(str(funding_rounds)):
            raise ValueError(
                f"Classification Mismatch: '{company_name}' is marked as 'Public', "
                f"but has private venture funding rounds: '{funding_rounds}'."
            )
            
    # Rule B: Subsidiary structures should exhibit parent relationship markers in their overview
    if normalized_nature == "Subsidiary" and overview:
        normalized_overview = overview.lower()
        has_ownership_marker = any(marker in normalized_overview for marker in PARENT_OWNERSHIP_KEYWORDS)
        if not has_ownership_marker:
            raise ValueError(
                f"Classification Mismatch: '{company_name}' is classified as a 'Subsidiary', "
                f"but its overview does not outline parent-subsidiary relationship terms."
            )
            
    return True


def validate_sentiment_metrics(record: Dict[str, Any]) -> bool:
    """
    Validates structural patterns and boundary ranges of brand sentiment, 
    Glassdoor employee scores, and Net Promoter Score (NPS).
    """
    brand_sentiment = record.get("Brand Sentiment Score")
    glassdoor_rating = record.get("Glassdoor Rating")
    nps = record.get("Net Promoter Score (NPS)")
    burnout_risk = record.get("Burnout risk")
    
    # 1. Validate Brand Sentiment Score (Nullable)
    if brand_sentiment is not None:
        val_str = str(brand_sentiment).strip()
        if not BRAND_SENTIMENT_REGEX.match(val_str):
            raise ValueError(
                f"Format Error: Brand Sentiment '{brand_sentiment}' must be "
                f"'Positive', 'Neutral', 'Negative' or an index (0-100)."
            )
            
        # If numeric index, enforce the standard 0-100 range constraints
        if val_str.isdigit():
            index_val = int(val_str)
            if not (0 <= index_val <= 100):
                raise ValueError(f"Boundary Error: Brand Sentiment Index '{index_val}' must be between 0 and 100.")
                
    # 2. Validate Glassdoor Rating (Nullable)
    if glassdoor_rating is not None:
        rating_str = str(glassdoor_rating).strip()
        if not GLASSDOOR_REGEX.match(rating_str):
            raise ValueError(
                f"Format Error: Glassdoor Rating '{glassdoor_rating}' "
                f"must match decimal format between 1.0 and 5.0."
            )
        rating_val = float(rating_str)
        if not (1.0 <= rating_val <= 5.0):
            raise ValueError(f"Boundary Error: Glassdoor Rating '{rating_val}' must be between 1.0 and 5.0.")

    # 3. Validate Net Promoter Score (NPS) (Nullable)
    if nps is not None:
        nps_str = str(nps).strip()
        if not NPS_REGEX.match(nps_str):
            raise ValueError(f"Format Error: NPS '{nps}' must be an integer between -100 and 100.")
            
        nps_val = int(nps_str)
        if not (-100 <= nps_val <= 100):
            raise ValueError(f"Boundary Error: Net Promoter Score '{nps_val}' must be between -100 and 100.")

    # 4. Logical Relational Checks (e.g. Glassdoor vs. Burnout Risk Alignment)
    if glassdoor_rating is not None and burnout_risk:
        rating_val = float(str(glassdoor_rating).strip())
        if rating_val >= 4.5 and str(burnout_risk).strip().title() == "Severe":
            raise ValueError(
                f"Relational Error: High Glassdoor Rating of {rating_val} "
                f"contradicts a 'Severe' Burnout Risk level."
            )

    return True


def validate_risk_classifications(record: Dict[str, Any]) -> bool:
    """
    Validates structural formatting and logical constraints for Customer Concentration Risk,
    Burnout Risk, and Operational Runway.
    """
    concentration = record.get("Customer Concentration Risk")
    burnout = record.get("Burnout risk")
    runway = record.get("Runway")
    weekend_work = record.get("Weekend work")
    overtime_exp = record.get("Overtime expectations")

    # 1. Validate Customer Concentration Risk
    if concentration is not None:
        con_str = str(concentration).strip()
        match = CONCENTRATION_REGEX.match(con_str)
        if not match:
            raise ValueError(
                f"Format Error: 'Customer Concentration Risk' value '{concentration}' "
                f"must start with 'Yes', 'No', 'High', or 'Low'."
            )
        
        # Cross-field logical check: Extract percentage if specified in string
        percent_match = re.search(r"(\d+)%", con_str)
        if percent_match:
            percent_val = int(percent_match.group(1))
            prefix = match.group(1).title()
            
            # If concentration > 20%, prefix must flag risk (cannot be 'No' or 'Low')
            if percent_val > 20 and prefix in ["No", "Low"]:
                raise ValueError(
                    f"Logical Mismatch: Customer concentration is {percent_val}%, "
                    f"but risk level is marked as '{prefix}'. Expected 'Yes' or 'High'."
                )

    # 2. Validate Burnout Risk Alignment
    if burnout is not None:
        burn_str = str(burnout).strip()
        match = BURNOUT_REGEX.match(burn_str)
        if not match:
            raise ValueError(
                f"Format Error: 'Burnout risk' value '{burnout}' "
                f"must start with 'Low', 'Medium', 'High', or 'Severe'."
            )
            
        prefix = match.group(1).title()
        
        # Relational Check: Extreme work patterns cannot map to Low/Medium burnout risk
        if weekend_work == "Always" and overtime_exp == "Frequent":
            if prefix in ["Low", "Medium"]:
                raise ValueError(
                    f"Logical Mismatch: Workplace has 'Always' weekend work and 'Frequent' "
                    f"overtime, but Burnout Risk is classified as '{prefix}'. Expected 'High' or 'Severe'."
                )

    # 3. Validate Runway Financial Risk Flag
    if runway is not None:
        try:
            runway_val = float(str(runway).strip())
        except ValueError:
            raise ValueError(f"Data Type Error: Runway '{runway}' must be a valid float value.")
            
        if runway_val < 0:
            raise ValueError("Boundary Error: Runway cannot be negative.")
            
        # Log a warning or return state if runway is critical (under 6 months)
        record["is_critical_runway"] = runway_val < 6.0

    return True


# =====================================================================
# Unit Tests
# =====================================================================

# --- Tests from tc_12.1.py ---

def test_startup_validation_success():
    """Validates a typical seed-stage or growth-stage startup with a small headcount."""
    record = {
        "Company Name": "Alpha Tech",
        "Category": "Startup",
        "Employee Size": "11-50",
        "Company maturity": "Startup"
    }
    assert validate_company_classification(record) is True


def test_smb_with_large_headcount_success():
    """Validates standard SMB classification for larger operating headcount."""
    record = {
        "Company Name": "Midwest Manufacturing",
        "Category": "SMB",
        "Employee Size": "500",
        "Company maturity": "Scale-up"
    }
    assert validate_company_classification(record) is True


def test_case_insensitive_normalization_success():
    """Ensures lowercase category inputs (e.g. 'startup') are normalized and parsed."""
    record = {
        "Company Name": "Beta Software",
        "Category": "startup",
        "Employee Size": "1-10",
        "Company maturity": "Startup"
    }
    assert validate_company_classification(record) is True
    assert record["Category"] == "Startup"


def test_invalid_category_enum_fails():
    """Ensures values outside the allowed taxonomy regex list fail."""
    record = {
        "Company Name": "Delta Partners",
        "Category": "Venture Capital",
        "Employee Size": "11-50"
    }
    with pytest.raises(ValueError, match="not a valid standardized business taxonomy enum"):
        validate_company_classification(record)


def test_startup_headcount_overflow_fails():
    """Flags logical anomalies where giant headcounts are falsely categorized as 'Startup'."""
    record = {
        "Company Name": "Gigantic App Corp",
        "Category": "Startup",
        "Employee Size": "2500",
        "Company maturity": "Scale-up"
    }
    with pytest.raises(ValueError, match="Startup' classification is invalid for enterprise-scale headcount"):
        validate_company_classification(record)


def test_enterprise_and_startup_maturity_clash_fails():
    """Flags mismatches between Category (Enterprise) and Company Maturity (Startup)."""
    record = {
        "Company Name": "Globex Corp",
        "Category": "Enterprise",
        "Employee Size": "1000+",
        "Company maturity": "Startup"
    }
    with pytest.raises(ValueError, match="Enterprise' category cannot align with a 'Startup' maturity level"):
        validate_company_classification(record)


# --- Tests from tc_12.2.py ---

def test_stripe_fintech_classification_success():
    """Validates correct fintech taxonomy and consistency with API/Billing products."""
    record = {
        "Company Name": "Stripe",
        "Focus Sectors / Industries": "Financial Technology, Payments",
        "Services / Offerings / Products": "Payment Processing APIs, Billing Engine, Corporate Cards"
    }
    assert validate_industry_classification(record) is True


def test_tesla_clean_tech_classification_success():
    """Validates correct multi-sector mappings (Automotive, Clean Energy) and product consistency."""
    record = {
        "Company Name": "Tesla",
        "Focus Sectors / Industries": "Automotive, Clean Energy, Energy Storage",
        "Services / Offerings / Products": "Electric Vehicles, Solar Panels, Powerwall Batteries"
    }
    assert validate_industry_classification(record) is True


def test_amazon_hybrid_retail_cloud_success():
    """Validates complex dual-sector mapping for hybrid enterprise models."""
    record = {
        "Company Name": "Amazon",
        "Focus Sectors / Industries": "E-commerce, Cloud Computing",
        "Services / Offerings / Products": "Online Retail Platform, Amazon Web Services (AWS)"
    }
    assert validate_industry_classification(record) is True


def test_invalid_special_characters_regex_fails():
    """Asserts that special characters violating the formatting constraints are caught."""
    record = {
        "Company Name": "Stripe",
        "Focus Sectors / Industries": "Fintech!!! & Payments",
        "Services / Offerings / Products": "Payment processing"
    }
    with pytest.raises(ValueError, match="Regex Pattern Error"):
        validate_industry_classification(record)


def test_unauthorized_industry_fails():
    """Asserts that industries outside the GICS-aligned master taxonomy list are flagged."""
    record = {
        "Company Name": "Stripe",
        "Focus Sectors / Industries": "Financial Technology, Custom Payment Rails",
        "Services / Offerings / Products": "Payment processing"
    }
    with pytest.raises(ValueError, match="does not exist in the standardized Industry Master List"):
        validate_industry_classification(record)


def test_semantic_product_sector_mismatch_fails():
    """Asserts that if a product is 'Electric Vehicles', the sector cannot be classified solely as 'Financial Technology'."""
    record = {
        "Company Name": "Future Motors",
        "Focus Sectors / Industries": "Financial Technology",
        "Services / Offerings / Products": "Electric Vehicles, Batteries"
    }
    with pytest.raises(ValueError, match="Semantic Inconsistency: Products include 'vehicle' indications"):
        validate_industry_classification(record)


# --- Tests from tc_12.3.py ---

def test_private_company_with_funding_success():
    """Validates typical private venture-backed startup profile."""
    record = {
        "Company Name": "Space Exploration Technologies Corp.",
        "Nature of Company": "Private",
        "Recent Funding Rounds": "2025-01-15 - $250,000,000",
        "Overview of the Company": "An independent aerospace manufacturer founded by Elon Musk."
    }
    assert validate_nature_of_company(record) is True


def test_public_company_success():
    """Validates public enterprise without venture rounds."""
    record = {
        "Company Name": "Apple Inc.",
        "Nature of Company": "Public",
        "Recent Funding Rounds": None,
        "Overview of the Company": "A global consumer electronics manufacturer."
    }
    assert validate_nature_of_company(record) is True


def test_subsidiary_company_success():
    """Validates subsidiary status when supported by description ownership terms."""
    record = {
        "Company Name": "WhatsApp LLC",
        "Nature of Company": "Subsidiary",
        "Recent Funding Rounds": None,
        "Overview of the Company": "A messaging platform owned by Meta Platforms, Inc."
    }
    assert validate_nature_of_company(record) is True


def test_lowercase_normalization_success():
    """Ensures incorrect casing (e.g., 'subsidiary') is corrected to match the regex."""
    record = {
        "Company Name": "WhatsApp LLC",
        "Nature of Company": "subsidiary",
        "Recent Funding Rounds": None,
        "Overview of the Company": "A messaging platform owned by Meta."
    }
    assert validate_nature_of_company(record) is True
    assert record["Nature of Company"] == "Subsidiary"


def test_invalid_structure_enum_fails():
    """Rejects legal structure values that are outside the standardized enum list."""
    record = {
        "Company Name": "SpaceX",
        "Nature of Company": "private-owned",
        "Recent Funding Rounds": "2025-01-15 - $250,000,000"
    }
    with pytest.raises(ValueError, match="is not a recognized legal structure enum"):
        validate_nature_of_company(record)


def test_public_with_venture_rounds_fails():
    """Flags anomalies where a public company lists active private venture capital rounds."""
    record = {
        "Company Name": "Apple Inc.",
        "Nature of Company": "Public",
        "Recent Funding Rounds": "2025-01-15 - Series B - $50,000,000",
        "Overview of the Company": "A global consumer electronics manufacturer."
    }
    with pytest.raises(ValueError, match="is marked as 'Public', but has private venture funding"):
        validate_nature_of_company(record)


def test_subsidiary_lacking_ownership_text_fails():
    """Flags subsidiaries whose overview reports no parent-ownership relationships."""
    record = {
        "Company Name": "WhatsApp LLC",
        "Nature of Company": "Subsidiary",
        "Recent Funding Rounds": None,
        "Overview of the Company": "An independent messaging platform."
    }
    with pytest.raises(ValueError, match="is classified as a 'Subsidiary', but its overview does not outline"):
        validate_nature_of_company(record)


# --- Tests from tc_12.4.py ---

def test_valid_categorical_brand_sentiment_success():
    """Validates standard categorical brand sentiment representation."""
    record = {
        "Brand Sentiment Score": "Positive",
        "Glassdoor Rating": "4.2",
        "Net Promoter Score (NPS)": "75"
    }
    assert validate_sentiment_metrics(record) is True


def test_valid_numeric_brand_sentiment_success():
    """Validates numeric index brand sentiment representation."""
    record = {
        "Brand Sentiment Score": "82",
        "Glassdoor Rating": "3.8",
        "Net Promoter Score (NPS)": "45"
    }
    assert validate_sentiment_metrics(record) is True


def test_negative_nps_boundary_success():
    """Ensures negative NPS boundaries are accepted when within range limits."""
    record = {
        "Brand Sentiment Score": "Negative",
        "Glassdoor Rating": "2.5",
        "Net Promoter Score (NPS)": "-40"
    }
    assert validate_sentiment_metrics(record) is True


def test_invalid_brand_sentiment_adjective_fails():
    """Ensures invalid adjectives outside 'Positive'/'Neutral'/'Negative' fail."""
    record = {
        "Brand Sentiment Score": "Excellent",
        "Glassdoor Rating": "4.2"
    }
    with pytest.raises(ValueError, match="must be 'Positive', 'Neutral', 'Negative' or an index"):
        validate_sentiment_metrics(record)


def test_out_of_bound_brand_sentiment_index_fails():
    """Flags numerical indexes that exceed 100."""
    record = {
        "Brand Sentiment Score": "125",
        "Glassdoor Rating": "4.2"
    }
    with pytest.raises(ValueError, match="Brand Sentiment Index '125' must be between 0 and 100"):
        validate_sentiment_metrics(record)


def test_out_of_bound_glassdoor_rating_fails():
    """Flags Glassdoor ratings that violate the standard 1.0 - 5.0 range."""
    record = {
        "Brand Sentiment Score": "Positive",
        "Glassdoor Rating": "5.5"
    }
    with pytest.raises(ValueError, match="must match decimal format between 1.0 and 5.0"):
        validate_sentiment_metrics(record)


def test_out_of_bound_nps_fails():
    """Flags NPS records that exceed 100 or fall below -100."""
    record = {
        "Brand Sentiment Score": "Positive",
        "Net Promoter Score (NPS)": "150"
    }
    with pytest.raises(ValueError, match="must be an integer between -100 and 100"):
        validate_sentiment_metrics(record)


def test_contradictory_glassdoor_and_burnout_metrics_fails():
    """Flags relational anomalies between high employer score and severe burnout risk."""
    record = {
        "Company Name": "FutureTech",
        "Brand Sentiment Score": "Positive",
        "Glassdoor Rating": "4.8",
        "Burnout risk": "Severe"
    }
    with pytest.raises(ValueError, match="contradicts a 'Severe' Burnout Risk level"):
        validate_sentiment_metrics(record)


# --- Tests from tc_12.5.py ---

def test_concentration_risk_high_success():
    """Validates high concentration risk where percentage exceeds boundary and matches prefix."""
    record = {
        "Customer Concentration Risk": "High - 35% from top client",
        "Burnout risk": "Medium",
        "Runway": "18.0"
    }
    assert validate_risk_classifications(record) is True


def test_intense_work_severe_burnout_success():
    """Validates extreme work conditions mapped to severe burnout risk."""
    record = {
        "Weekend work": "Always",
        "Overtime expectations": "Frequent",
        "Burnout risk": "Severe risk of attrition"
    }
    assert validate_risk_classifications(record) is True


def test_critical_runway_risk_logged():
    """Ensures runway under 6 months triggers a critical flag within the metadata dictionary."""
    record = {
        "Runway": "4.5"
    }
    assert validate_risk_classifications(record) is True
    assert record["is_critical_runway"] is True


def test_invalid_concentration_prefix_fails():
    """Rejects concentration risk strings that use arbitrary non-standard prefixes."""
    record = {
        "Customer Concentration Risk": "Maybe - about 15%"
    }
    with pytest.raises(ValueError, match="must start with 'Yes', 'No', 'High', or 'Low'"):
        validate_risk_classifications(record)


def test_contradictory_concentration_and_percentage_fails():
    """Rejects records that claim 'Low' or 'No' concentration risk despite >20% revenue from one client."""
    record = {
        "Customer Concentration Risk": "Low - 30% from anchor client"
    }
    with pytest.raises(ValueError, match="Expected 'Yes' or 'High'"):
        validate_risk_classifications(record)


def test_contradictory_work_conditions_and_burnout_fails():
    """Rejects records that attempt to greenwash high work-pressure as 'Low' burnout risk."""
    record = {
        "Weekend work": "Always",
        "Overtime expectations": "Frequent",
        "Burnout risk": "Low"
    }
    with pytest.raises(ValueError, match="Expected 'High' or 'Severe'"):
        validate_risk_classifications(record)