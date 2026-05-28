import pytest
from typing import Dict, Any

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
    # Normally, 'Services / Offerings / Products' is Not Null and requires tangible products.
    # We dynamically allow "N/A" bypasses if the Category is VC or Investor.
    if category in ["VC", "Investor"]:
        if products is None or "n/a" in str(products).lower():
            # Accept N/A gracefully for VCs
            pass
    else:
        # Standard commercial companies must have tangible products/services
        if not products or "n/a" in str(products).lower():
            raise ValueError(
                f"Validation Failure: Standard commercial category '{category}' "
                f"must list actual products. '{products}' is not permitted."
            )

    # 2. Bootstrapped Investors Rule
    # If the company is bootstrapped (represented by 0 capital or Null), 
    # we allow "N/A" or "None" for investors.
    if total_capital == 0 or total_capital is None:
        if investors is not None and "n/a" not in str(investors).lower() and "none" not in str(investors).lower():
            # If they didn't raise capital but listed active investors, this is a flag to audit
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
    # If the company is Remote-First, we allow 0 offices and N/A for physical office locations.
    if remote_policy in ["Remote-First", "Remote"]:
        if offices_count == 0:
            if office_locations is not None and "n/a" not in str(office_locations).lower():
                # If they have 0 physical offices but listed locations, flag it
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


# --- Pytest Suite ---

def test_vc_firm_na_products_success():
    """
    Ensures an investment firm (VC) successfully passes validation when its 
    products parameter is mapped to 'N/A'.
    """
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
    """
    Ensures a self-funded startup successfully passes validation with 
    investors set to 'N/A' and capital raised set to 0.
    """
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
    """
    Ensures a fully distributed, remote-first company successfully passes validation 
    with 0 offices and locations set to 'N/A'.
    """
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
    """
    Asserts that standard commercial startups are not permitted to bypass
    the mandatory products field with 'N/A' values.
    """
    record = {
        "Company Name": "Standard Soft LLC",
        "Category": "Startup",
        "Services / Offerings / Products": "N/A",  # Invalid for standard startups
        "Total Capital Raised": 500000,
        "Key Investors / Backers": "Angel Investors",
        "Remote Work Policy": "Hybrid",
        "Number of Offices (beyond HQ)": 1,
        "Office Locations": "New York, USA"
    }
    with pytest.raises(ValueError, match="must list actual products"):
        validate_not_applicable_fields(record)


def test_funded_company_na_investors_fails():
    """
    Asserts that a company stating it has raised millions cannot set its
    investors field to 'N/A'.
    """
    record = {
        "Company Name": "WellFunded Tech",
        "Category": "Startup",
        "Services / Offerings / Products": "AI Copilot Suite",
        "Total Capital Raised": 12000000,
        "Key Investors / Backers": "N/A",  # Conflict: millions raised, but no investors listed
        "Remote Work Policy": "Remote-First",
        "Number of Offices (beyond HQ)": 0,
        "Office Locations": "N/A - Fully Distributed"
    }
    with pytest.raises(ValueError, match="cannot be N/A"):
        validate_not_applicable_fields(record)