import re
import pytest
from typing import Dict, Any, Union

# Category Enum Regex match: ^(Startup|MSME|SMB|Enterprise|Investor|VC|Conglomerate)$
CATEGORY_REGEX = re.compile(r"^(Startup|MSME|SMB|Enterprise|Investor|VC|Conglomerate)$")

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
        
    # Rule C: Validate logical harmony between Category and Company Maturity if both are present [1]
    if maturity:
        if normalized_cat == "Enterprise" and maturity == "Startup":
            raise ValueError("Logical Error: 'Enterprise' category cannot align with a 'Startup' maturity level.")
        if normalized_cat == "Startup" and maturity == "Mature":
            raise ValueError("Logical Error: 'Startup' category cannot align with a 'Mature' maturity level.")
            
    return True


# --- Pytest Suite ---

def test_startup_validation_success():
    """
    Validates a typical seed-stage or growth-stage startup with a small headcount.
    """
    record = {
        "Company Name": "Alpha Tech",
        "Category": "Startup",
        "Employee Size": "11-50",
        "Company maturity": "Startup"
    }
    assert validate_company_classification(record) is True


def test_smb_with_large_headcount_success():
    """
    Validates standard SMB classification for larger operating headcount.
    """
    record = {
        "Company Name": "Midwest Manufacturing",
        "Category": "SMB",
        "Employee Size": "500",
        "Company maturity": "Scale-up"
    }
    assert validate_company_classification(record) is True


def test_case_insensitive_normalization_success():
    """
    Ensures lowercase category inputs (e.g. 'startup') are normalized and parsed.
    """
    record = {
        "Company Name": "Beta Software",
        "Category": "startup",
        "Employee Size": "1-10",
        "Company maturity": "Startup"
    }
    assert validate_company_classification(record) is True
    assert record["Category"] == "Startup"  # Normalized to title case


def test_invalid_category_enum_fails():
    """
    Ensures values outside the allowed taxonomy regex list fail.
    """
    record = {
        "Company Name": "Delta Partners",
        "Category": "Venture Capital",  # Incorrect enum tag (should be "VC")
        "Employee Size": "11-50"
    }
    with pytest.raises(ValueError, match="not a valid standardized business taxonomy enum"):
        validate_company_classification(record)


def test_startup_headcount_overflow_fails():
    """
    Flags logical anomalies where giant headcounts are falsely categorized as 'Startup'.
    """
    record = {
        "Company Name": "Gigantic App Corp",
        "Category": "Startup",
        "Employee Size": "2500",  # Far too large for a startup category classification
        "Company maturity": "Scale-up"
    }
    with pytest.raises(ValueError, match="Startup' classification is invalid for enterprise-scale headcount"):
        validate_company_classification(record)


def test_enterprise_and_startup_maturity_clash_fails():
    """
    Flags mismatches between Category (Enterprise) and Company Maturity (Startup).
    """
    record = {
        "Company Name": "Globex Corp",
        "Category": "Enterprise",
        "Employee Size": "1000+",
        "Company maturity": "Startup"
    }
    with pytest.raises(ValueError, match="Enterprise' category cannot align with a 'Startup' maturity level"):
        validate_company_classification(record)