import re
from typing import Dict, Any, List, Optional, Tuple, Union
import pytest

# =====================================================================
# Constants, Registries, and Databases
# =====================================================================

MANDATORY_FIELDS = [
    "Company Name", 
    "Category", 
    "Year of Incorporation", 
    "Overview of the Company", 
    "Nature of Company", 
    "Company Headquarters", 
    "Employee Size"
]

STRING_NULL_PLACEHOLDERS = {"n/a", "na", "null", "none", "unknown", "undisclosed", ""}

CURRENT_YEAR = 2026

HQ_COUNTRY_MAP = {
    "usa": "United States",
    "united states": "United States",
    "india": "India",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "germany": "Germany"
}


# =====================================================================
# Core Validation & Calculation Logic
# =====================================================================

def validate_nullable_data_integrity(record: Dict[str, Any]) -> bool:
    """
    Evaluates the record for nullability and NA data rules. 
    Enforces exceptions on missing mandatory parameters while allowing 
    flexible, graceful mapping on optional parameters.
    """
    # 1. Check all mandatory parameters
    for field in MANDATORY_FIELDS:
        val = record.get(field)
        
        # Check for python None
        if val is None:
            raise ValueError(f"Nullability Violation: Mandatory field '{field}' cannot be Null.")
            
        # Check for string placeholders representing nulls (e.g. "N/A" or "Unknown")
        if isinstance(val, str):
            cleaned_val = val.strip().lower()
            if cleaned_val in STRING_NULL_PLACEHOLDERS:
                raise ValueError(
                    f"Nullability Violation: Mandatory field '{field}' contains "
                    f"an invalid placeholder value '{val}'."
                )

    # 2. Parse and normalize optional parameters (e.g., Private Financials)
    optional_fields = ["Annual Revenues", "Annual Profits", "Company Valuation", "Total Capital Raised"]
    for field in optional_fields:
        val = record.get(field)
        if val is not None:
            if isinstance(val, str):
                cleaned_val = val.strip().lower()
                if cleaned_val in STRING_NULL_PLACEHOLDERS:
                    # Gracefully normalize the placeholder to Python None
                    record[field] = None

    # 3. Graceful parsing check of text fields containing undisclosed values
    funding_rounds = record.get("Recent Funding Rounds")
    if funding_rounds:
        # Verify that containing the word "Undisclosed" doesn't crash any financial logic,
        # but is treated as a valid textual history.
        if "undisclosed" in str(funding_rounds).lower():
            # Ensure total capital is safely handled as null/None if undisclosed
            if record.get("Total Capital Raised") is not None:
                # If capital was populated as a string like "Undisclosed", normalize to None
                if str(record["Total Capital Raised"]).strip().lower() in STRING_NULL_PLACEHOLDERS:
                    record["Total Capital Raised"] = None

    return True


def validate_not_applicable_fields(record: Dict[str, Any]) -> bool:
    """
    Validates company metadata by dynamically adjusting constraint rules 
    for fields that do not apply to specific corporate profiles.
    """
    category = record.get("Category")
    company_name = record.get("Company Name")
    products = record.get("Services / Offerings / Products")
    total_capital = record.get("Total Capital Raised")
    investors = record.get("Key Investors / Backers")
    remote_policy = record.get("Remote Work Policy")
    offices_count = record.get("Number of Offices (beyond HQ)")
    office_locations = record.get("Office Locations")

    # Enforce basic identity requirements
    if not company_name or not category:
        raise ValueError("Field Validation Error: 'Company Name' and 'Category' are required.")

    # 1. VC / Investor Products Rule
    if category in ["VC", "Investor"]:
        if products is None or "n/a" in str(products).lower():
            pass
    else:
        # Standard commercial companies must have tangible products/services
        if not products or "n/a" in str(products).lower():
            raise ValueError(
                f"Validation Failure: Standard commercial category '{category}' "
                f"must list actual products. '{products}' is not permitted."
            )

    # 2. Bootstrapped Investors Rule
    if total_capital == 0 or total_capital is None:
        if investors is not None and "n/a" not in str(investors).lower() and "none" not in str(investors).lower():
            raise ValueError(
                f"Logical Conflict: Capital raised is 0, but investors are listed: '{investors}'."
            )
    else:
        # If they raised capital, they must list valid investors (cannot be N/A)
        if investors is not None and "n/a" in str(investors).lower():
            raise ValueError(
                f"Validation Failure: Capital was raised ({total_capital}), "
                f"so 'Key Investors / Backers' cannot be N/A."
            )

    # 3. Fully Remote Office Locations Rule
    if remote_policy in ["Remote-First", "Remote"]:
        if offices_count == 0:
            if office_locations is not None and "n/a" not in str(office_locations).lower():
                raise ValueError(
                    f"Logical Conflict: Remote company has 0 physical offices, "
                    f"but listed locations: '{office_locations}'."
                )
    else:
        # Standard office-based companies cannot have N/A for locations
        if office_locations is not None and "n/a" in str(office_locations).lower():
            raise ValueError(
                f"Validation Failure: Physical company with policy '{remote_policy}' "
                f"cannot have 'N/A' for office locations."
            )

    return True


def validate_ambiguous_availability(record: Dict[str, Any]) -> bool:
    """
    Validates company metadata by dynamically evaluating the source of 
    missing data. Normalizes generic null values into context-rich 
    ambiguity classifications depending on the company lifecycle.
    """
    company_name = record.get("Company Name")
    year_founded = record.get("Year of Incorporation")
    retention_tenure = record.get("Average Retention Tenure")
    layoff_history = record.get("Layoff history")
    website_url = record.get("Website URL")
    glassdoor_rating = record.get("Glassdoor Rating")
    confidence_level = record.get("confidence_level")
    validation_mode = record.get("validation_mode", "Automated")

    if not company_name:
         raise ValueError("Field Validation Error: 'Company Name' is required.")

    # 1. Temporal Ambiguity Rule (Data Not Yet Generated)
    if year_founded and (CURRENT_YEAR - int(year_founded)) <= 1:
        if retention_tenure is None or retention_tenure == "":
            record["Average Retention Tenure"] = "N/A - New Company"
        if layoff_history is None or layoff_history == "":
            record["Layoff history"] = "None - New Company"

    # 2. Stealth/Confidential Ambiguity Rule (Exists but Not Public)
    is_stealth = False
    if website_url and "stealth" in str(website_url).lower():
        is_stealth = True
    elif "stealth" in str(company_name).lower():
        is_stealth = True

    if is_stealth:
        if glassdoor_rating is None or glassdoor_rating == "":
            record["Glassdoor Rating"] = "N/A - Stealth Mode"
        
        # Enforce that a stealth profile must have its confidence level restricted
        if confidence_level == "High":
            raise ValueError(
                f"Confidence Conflict: Stealth entity '{company_name}' cannot have "
                f"a 'High' confidence level due to unresolvable, non-public data fields."
            )

    # 3. Decommissioned/Deactivated Assets Rule (Previously Existed)
    is_url_deactivated = record.get("is_url_deactivated", False)
    if is_url_deactivated:
        if validation_mode == "Automated":
            raise ValueError(
                f"Processing Exception: Deactivated assets detected for '{company_name}'. "
                f"Validation mode must be shifted to 'Supervised' or 'Manual' for human auditing."
            )

    return True


def validate_default_value_logic(record: Dict[str, Any]) -> bool:
    """
    Validates company metadata by ensuring appropriate defaults are applied
    and inappropriate defaults are flagged and rejected.
    """
    company_name = record.get("Company Name")
    category = record.get("Category")
    maturity = record.get("Company maturity")
    revenues = record.get("Annual Revenues")
    hq = record.get("Company Headquarters")
    countries = record.get("Countries Operating In")
    offices_count = record.get("Number of Offices (beyond HQ)")

    if not company_name or not category:
        raise ValueError("Field Validation Error: 'Company Name' and 'Category' are required.")

    # 1. Reject Inappropriate Financial Defaults
    if revenues is not None:
        clean_rev = str(revenues).strip().replace("$", "").replace(",", "")
        
        if clean_rev in ["0", "0.00", "free", "none"]:
            if maturity in ["Scale-up", "Mature"] and category not in ["Non-Profit", "Govt"]:
                raise ValueError(
                    f"Inappropriate Default Detected: Active, mature commercial entity '{company_name}' "
                    f"cannot have its revenue defaulted to zero. Unknown revenue must be represented as Null/None."
                )

    # 2. Execute Context-Dependent Defaults
    if countries is None or str(countries).strip() == "":
        if hq:
            hq_lower = str(hq).lower()
            resolved_country = None
            
            # Extract country from the HQ address string
            for keyword, country_name in HQ_COUNTRY_MAP.items():
                if keyword in hq_lower:
                    resolved_country = country_name
                    break
                    
            if resolved_country:
                record["Countries Operating In"] = resolved_country
            else:
                record["Countries Operating In"] = "Unknown"
        else:
            record["Countries Operating In"] = "Unknown"

    # 3. Execute Safe Structural Defaults
    if offices_count is None:
        record["Number of Offices (beyond HQ)"] = 0

    return True


def calculate_yoy_growth(current_rev: Optional[float], prev_rev: Optional[float]) -> Optional[float]:
    """YoY Growth engine with strict Null propagation."""
    if current_rev is None or prev_rev is None:
        return None
    if prev_rev == 0:
        return None  # Avoid division by zero
    return ((current_rev - prev_rev) / prev_rev) * 100


def calculate_profitability_status(profits: Optional[float]) -> Optional[str]:
    """Profitability Status engine with strict Null propagation."""
    if profits is None:
        return None
    if profits > 0:
        return "Profitable"
    elif profits < 0:
        return "Loss-making"
    else:
        return "Break-even"


def calculate_market_share(revenue: Optional[float], tam: Optional[float]) -> Optional[float]:
    """Market Share (%) engine with strict Null propagation."""
    if revenue is None or tam is None:
        return None
    if tam == 0:
        return None
    return (revenue / tam) * 100


def sum_total_capital_raised(rounds_text: Optional[str]) -> Optional[float]:
    """Total Capital Raised engine with strict Null propagation."""
    if not rounds_text:
        return None
        
    amounts = re.findall(r"\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*([KkMmBb]?)", rounds_text)
    if not amounts:
        return None  # All rounds undisclosed or parsing yielded no numbers
        
    total = 0.0
    for val, suffix in amounts:
        num = float(val.replace(",", ""))
        if suffix.lower() == "k":
            num *= 1_000
        elif suffix.lower() == "m":
            num *= 1_000_000
        elif suffix.lower() == "b":
            num *= 1_000_000_000
        total += num
        
    return total


def calculate_cac_ltv_ratio(cac: Optional[float], ltv: Optional[float]) -> Optional[str]:
    """CAC:LTV Ratio engine with strict Null propagation."""
    if cac is None or ltv is None:
        return None
    if ltv == 0:
        return None
    ratio_val = cac / ltv
    return f"{ratio_val:.1f}:1"


def calculate_runway(cash: Optional[float], burn_rate: Optional[float]) -> Optional[float]:
    """Runway (Months) engine with strict Null propagation."""
    if cash is None or burn_rate is None:
        return None
    if burn_rate <= 0:
        return None  # Infinite runway or division by zero handled as Null
    return cash / burn_rate


def calculate_burn_multiplier(net_burn: Optional[float], net_new_arr: Optional[float]) -> Optional[float]:
    """Burn Multiplier engine with strict Null propagation."""
    if net_burn is None or net_new_arr is None:
        return None
    if net_new_arr == 0:
        return None
    return net_burn / net_new_arr


# =====================================================================
# Unit Tests
# =====================================================================

# --- Tests from tc_14.1.py ---

def test_private_stealth_startup_null_financials_success():
    """Verifies stealth company with empty optional financials passes with critical mandatory parameters."""
    stealth_company = {
        "Company Name": "Stealth AI Inc.",
        "Category": "Startup",
        "Year of Incorporation": 2025,
        "Overview of the Company": "Building advanced LLM security testing tools in stealth.",
        "Nature of Company": "Private",
        "Company Headquarters": "Boston, USA",
        "Employee Size": "1-10",
        "Annual Revenues": None,
        "Annual Profits": None,
        "Company Valuation": "N/A",
        "Recent Funding Rounds": "2025-04-10 - Undisclosed - Seed"
    }
    
    assert validate_nullable_data_integrity(stealth_company) is True
    assert stealth_company["Company Valuation"] is None


def test_public_company_full_data_success():
    """Ensures a fully populated public company profile with active financial metrics passes."""
    public_company = {
        "Company Name": "Alphabet Inc.",
        "Category": "Enterprise",
        "Year of Incorporation": 1998,
        "Overview of the Company": "A global technology company specializing in search and cloud solutions.",
        "Nature of Company": "Public",
        "Company Headquarters": "Mountain View, USA",
        "Employee Size": "100000+",
        "Annual Revenues": "$307,000,000,000",
        "Annual Profits": "$73,000,000,000",
        "Company Valuation": "$1,800,000,000,000"
    }
    assert validate_nullable_data_integrity(public_company) is True


def test_missing_mandatory_field_fails():
    """Rejects the record if a mandatory parameter is entirely absent (evaluates to None)."""
    malformed_record = {
        "Company Name": "Alpha Partners",
        "Category": None,
        "Year of Incorporation": 2020,
        "Overview of the Company": "A venture fund seeking tech investments.",
        "Nature of Company": "Partnership",
        "Company Headquarters": "New York, USA",
        "Employee Size": "11-50"
    }
    with pytest.raises(ValueError, match="Mandatory field 'Category' cannot be Null"):
        validate_nullable_data_integrity(malformed_record)


def test_placeholder_string_nulls_in_mandatory_field_fails():
    """Rejects the record if a mandatory parameter is populated with a string placeholder like 'N/A'."""
    malformed_record = {
        "Company Name": "Unknown Co.",
        "Category": "Startup",
        "Year of Incorporation": 2021,
        "Overview of the Company": "N/A",
        "Nature of Company": "Private",
        "Company Headquarters": "Seattle, USA",
        "Employee Size": "1-10"
    }
    with pytest.raises(ValueError, match="Mandatory field 'Overview of the Company' contains an invalid placeholder"):
        validate_nullable_data_integrity(malformed_record)


# --- Tests from tc_14.2.py ---

def test_vc_firm_na_products_success():
    """Ensures an investment firm (VC) passes validation when its products parameter is 'N/A'."""
    record = {
        "Company Name": "Sequoia Capital",
        "Category": "VC",
        "Services / Offerings / Products": "N/A - Financial Investment Services",
        "Total Capital Raised": 0,
        "Key Investors / Backers": "None - General Partners",
        "Remote Work Policy": "Hybrid",
        "Number of Offices (beyond HQ)": 3,
        "Office Locations": "London, UK; Beijing, China"
    }
    assert validate_not_applicable_fields(record) is True


def test_bootstrapped_company_na_investors_success():
    """Ensures self-funded startup passes validation with investors set to 'N/A' and capital raised set to 0."""
    record = {
        "Company Name": "Bootstrapped SaaS LLC",
        "Category": "Startup",
        "Services / Offerings / Products": "Subscription Email Marketing Software",
        "Total Capital Raised": 0,
        "Key Investors / Backers": "N/A - Bootstrapped",
        "Remote Work Policy": "On-Site",
        "Number of Offices (beyond HQ)": 1,
        "Office Locations": "Austin, Texas"
    }
    assert validate_not_applicable_fields(record) is True


def test_remote_first_company_na_offices_success():
    """Ensures a remote-first company passes validation with 0 offices and locations set to 'N/A'."""
    record = {
        "Company Name": "GitLab Inc.",
        "Category": "Enterprise",
        "Services / Offerings / Products": "DevSecOps Platform",
        "Total Capital Raised": 100000000,
        "Key Investors / Backers": "Khosla Ventures, Y Combinator",
        "Remote Work Policy": "Remote-First",
        "Number of Offices (beyond HQ)": 0,
        "Office Locations": "N/A - Fully Distributed"
    }
    assert validate_not_applicable_fields(record) is True


def test_standard_company_na_products_fails():
    """Asserts that standard commercial startups are not permitted to bypass products field with 'N/A'."""
    record = {
        "Company Name": "Standard Soft LLC",
        "Category": "Startup",
        "Services / Offerings / Products": "N/A",
        "Total Capital Raised": 500000,
        "Key Investors / Backers": "Angel Investors",
        "Remote Work Policy": "Hybrid",
        "Number of Offices (beyond HQ)": 1,
        "Office Locations": "New York, USA"
    }
    with pytest.raises(ValueError, match="must list actual products"):
        validate_not_applicable_fields(record)


def test_funded_company_na_investors_fails():
    """Asserts that a company stating it has raised millions cannot set its investors field to 'N/A'."""
    record = {
        "Company Name": "WellFunded Tech",
        "Category": "Startup",
        "Services / Offerings / Products": "AI Copilot Suite",
        "Total Capital Raised": 12000000,
        "Key Investors / Backers": "N/A",
        "Remote Work Policy": "Remote-First",
        "Number of Offices (beyond HQ)": 0,
        "Office Locations": "N/A - Fully Distributed"
    }
    with pytest.raises(ValueError, match="cannot be N/A"):
        validate_not_applicable_fields(record)


# --- Tests from tc_14.3.py ---

def test_newly_founded_company_ambiguity_handled():
    """Ensures that a company founded in 2025/2026 maps missing historical parameters to 'N/A - New Company'."""
    new_company = {
        "Company Name": "NeuraLaunch",
        "Year of Incorporation": 2025,
        "Average Retention Tenure": None,
        "Layoff history": None,
        "confidence_level": "High"
    }
    
    assert validate_ambiguous_availability(new_company) is True
    assert new_company["Average Retention Tenure"] == "N/A - New Company"
    assert new_company["Layoff history"] == "None - New Company"


def test_stealth_company_ambiguity_handled():
    """Ensures stealth profiles are permitted to have missing digital parameters and constrains confidence."""
    stealth_company = {
        "Company Name": "Stealth Crypto Labs",
        "Website URL": "N/A - Stealth Mode",
        "Glassdoor Rating": None,
        "confidence_level": "Medium"
    }
    
    assert validate_ambiguous_availability(stealth_company) is True
    assert stealth_company["Glassdoor Rating"] == "N/A - Stealth Mode"


def test_stealth_company_invalid_high_confidence_fails():
    """Asserts that a stealth-mode profile cannot claim a 'High' data confidence level."""
    stealth_company = {
        "Company Name": "Stealth Crypto Labs",
        "Website URL": "N/A - Stealth Mode",
        "Glassdoor Rating": None,
        "confidence_level": "High"
    }
    with pytest.raises(ValueError, match="cannot have a 'High' confidence level"):
        validate_ambiguous_availability(stealth_company)


def test_deactivated_url_demands_manual_validation_fails():
    """Asserts that if a company's target URL is deactivated, automated validation shifts mode."""
    deactivated_record = {
        "Company Name": "Retired Brand Inc.",
        "Website URL": "https://www.oldbrand.com",
        "is_url_deactivated": True,
        "validation_mode": "Automated"
    }
    with pytest.raises(ValueError, match="Validation mode must be shifted to 'Supervised' or 'Manual'"):
        validate_ambiguous_availability(deactivated_record)


def test_deactivated_url_supervised_run_success():
    """Ensures deactivated assets pass checks if mode is configured for manual or supervised auditing."""
    deactivated_record = {
        "Company Name": "Retired Brand Inc.",
        "Website URL": "https://www.oldbrand.com",
        "is_url_deactivated": True,
        "validation_mode": "Manual"
    }
    assert validate_ambiguous_availability(deactivated_record) is True


# --- Tests from tc_14.4.py ---

def test_context_dependent_hq_country_default_success():
    """Ensures missing operating country is safely defaulted from headquarters block."""
    record = {
        "Company Name": "Apex SaaS LLC",
        "Category": "Startup",
        "Company maturity": "Startup",
        "Company Headquarters": "San Francisco, USA",
        "Countries Operating In": None,
        "Number of Offices (beyond HQ)": 1
    }
    
    assert validate_default_value_logic(record) is True
    assert record["Countries Operating In"] == "United States"


def test_safe_structural_office_count_default_success():
    """Ensures that a missing office count is safely defaulted to 0."""
    record = {
        "Company Name": "Apex SaaS LLC",
        "Category": "Startup",
        "Company maturity": "Startup",
        "Company Headquarters": "San Francisco, USA",
        "Countries Operating In": "United States",
        "Number of Offices (beyond HQ)": None
    }
    
    assert validate_default_value_logic(record) is True
    assert record["Number of Offices (beyond HQ)"] == 0


def test_inappropriate_financial_zero_default_fails():
    """Asserts active, mature company is rejected if revenue is inappropriately defaulted to zero."""
    record = {
        "Company Name": "Enterprise Solutions Inc.",
        "Category": "Enterprise",
        "Company maturity": "Mature",
        "Company Headquarters": "London, UK",
        "Annual Revenues": "$0"
    }
    
    with pytest.raises(ValueError, match="Active, mature commercial entity .* cannot have its revenue defaulted to zero"):
        validate_default_value_logic(record)


def test_legitimate_non_profit_zero_revenue_success():
    """Ensures zero-revenue states for non-profits are accepted without default failures."""
    record = {
        "Company Name": "Green Earth Foundation",
        "Category": "Non-Profit",
        "Company maturity": "Mature",
        "Company Headquarters": "Berlin, Germany",
        "Annual Revenues": "$0"
    }
    assert validate_default_value_logic(record) is True


# --- Tests from tcc_14.5.py ---

def test_yoy_growth_null_propagation():
    """Asserts that YoY growth rate cleanly propagates as None if dependencies are missing."""
    assert calculate_yoy_growth(None, 10_000_000.0) is None
    assert calculate_yoy_growth(15_000_000.0, None) is None
    assert calculate_yoy_growth(15_000_000.0, 10_000_000.0) == 50.0


def test_profitability_status_null_propagation():
    """Asserts that if annual profits are undisclosed, derived status propagates as None."""
    assert calculate_profitability_status(None) is None
    assert calculate_profitability_status(2_500_000.0) == "Profitable"


def test_market_share_null_propagation():
    """Asserts that if TAM or Revenues are unknown, derived market share is None."""
    assert calculate_market_share(None, 100_000_000.0) is None
    assert calculate_market_share(5_000_000.0, None) is None
    assert calculate_market_share(5_000_000.0, 100_000_000.0) == 5.0


def test_total_capital_raised_null_propagation():
    """Asserts that if all rounds are undisclosed, total capital is None."""
    undisclosed_rounds = "2025-01-10 - Undisclosed - Series A, 2024-03-05 - Undisclosed - Seed"
    assert sum_total_capital_raised(undisclosed_rounds) is None
    
    valid_rounds = "2025-01-10 - $5M - Series A, 2024-03-05 - $1.5M - Seed"
    assert sum_total_capital_raised(valid_rounds) == 6_500_000.0


def test_cac_ltv_ratio_null_propagation():
    """Asserts that if LTV or CAC is missing, ratio propagates cleanly as None."""
    assert calculate_cac_ltv_ratio(None, 5000.0) is None
    assert calculate_cac_ltv_ratio(1500.0, None) is None
    assert calculate_cac_ltv_ratio(1500.0, 5000.0) == "0.3:1"


def test_runway_null_propagation():
    """Asserts that if cash or burn rate is missing, runway propagates as None."""
    assert calculate_runway(None, 100_000.0) is None
    assert calculate_runway(500_000.0, None) is None
    assert calculate_runway(500_000.0, 0.0) is None
    assert calculate_runway(500_000.0, 100_000.0) == 5.0


def test_burn_multiplier_null_propagation():
    """Asserts that if net burn or net new ARR is missing, burn multiplier is None."""
    assert calculate_burn_multiplier(None, 1_000_000.0) is None
    assert calculate_burn_multiplier(500_000.0, None) is None
    assert calculate_burn_multiplier(500_000.0, 1_000_000.0) == 0.5