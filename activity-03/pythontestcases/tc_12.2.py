import re
import pytest
from typing import Dict, Any, Set

# GICS / Industry format regex: ^[\w\s&.,\-/]+$
INDUSTRY_REGEX = re.compile(r"^[\w\s&.,\-/]+$")

# Simulated Industry Master List (GICS-aligned taxonomy)
INDUSTRY_MASTER_LIST: Set[str] = {
    "Financial Technology", "Payments", "Automotive", "Clean Energy", 
    "Energy Storage", "E-commerce", "Cloud Computing", "Software", 
    "Retail", "Technology", "Healthcare", "Financials"
}

# Semantic mapping to cross-validate products against focus sectors
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


# --- Pytest Suite ---

def test_stripe_fintech_classification_success():
    """
    Validates correct fintech taxonomy and consistency with API/Billing products.
    """
    record = {
        "Company Name": "Stripe",
        "Focus Sectors / Industries": "Financial Technology, Payments",
        "Services / Offerings / Products": "Payment Processing APIs, Billing Engine, Corporate Cards"
    }
    assert validate_industry_classification(record) is True


def test_tesla_clean_tech_classification_success():
    """
    Validates correct multi-sector mappings (Automotive, Clean Energy) and product consistency.
    """
    record = {
        "Company Name": "Tesla",
        "Focus Sectors / Industries": "Automotive, Clean Energy, Energy Storage",
        "Services / Offerings / Products": "Electric Vehicles, Solar Panels, Powerwall Batteries"
    }
    assert validate_industry_classification(record) is True


def test_amazon_hybrid_retail_cloud_success():
    """
    Validates complex dual-sector mapping for hybrid enterprise models.
    """
    record = {
        "Company Name": "Amazon",
        "Focus Sectors / Industries": "E-commerce, Cloud Computing",
        "Services / Offerings / Products": "Online Retail Platform, Amazon Web Services (AWS)"
    }
    assert validate_industry_classification(record) is True


def test_invalid_special_characters_regex_fails():
    """
    Asserts that special characters violating the formatting constraints are caught.
    """
    record = {
        "Company Name": "Stripe",
        "Focus Sectors / Industries": "Fintech!!! & Payments",  # Forbidden characters '!!!'
        "Services / Offerings / Products": "Payment processing"
    }
    with pytest.raises(ValueError, match="Regex Pattern Error"):
        validate_industry_classification(record)


def test_unauthorized_industry_fails():
    """
    Asserts that industries outside the GICS-aligned master taxonomy list are flagged.
    """
    record = {
        "Company Name": "Stripe",
        "Focus Sectors / Industries": "Financial Technology, Custom Payment Rails",  # Custom Payment Rails is outside master list
        "Services / Offerings / Products": "Payment processing"
    }
    with pytest.raises(ValueError, match="does not exist in the standardized Industry Master List"):
        validate_industry_classification(record)


def test_semantic_product_sector_mismatch_fails():
    """
    Asserts that if a product is 'Electric Vehicles', the sector cannot be classified solely as 'Financial Technology'.
    """
    record = {
        "Company Name": "Future Motors",
        "Focus Sectors / Industries": "Financial Technology",  # Blatant sector mismatch for electric vehicle product
        "Services / Offerings / Products": "Electric Vehicles, Batteries"
    }
    with pytest.raises(ValueError, match="Semantic Inconsistency: Products include 'vehicle' indications"):
        validate_industry_classification(record)