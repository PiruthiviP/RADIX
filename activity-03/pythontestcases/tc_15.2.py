import pytest
from typing import Dict, Any

# Standard Source Quality Tier definitions
TIER_1_PRIMARY = {
    "company registry / sec filings", "sec filings", "company registry", 
    "company website", "official registry", "sec"
}

TIER_2_SECONDARY = {
    "linkedin", "crunchbase", "pr newswire", "careers page", 
    "job boards", "apollo", "clearbit", "website contact page"
}

TIER_3_TERTIARY = {
    "news articles", "blog posts", "glassdoor", "indeed", "yelp", 
    "analyst reports", "3rd party db estimates", "ai inference", 
    "court records", "twitter", "x", "social media"
}


def get_source_tier(source_string: str) -> int:
    """
    Classifies a data source string into Tier 1, 2, or 3.
    """
    clean_src = str(source_string).strip().lower()
    
    # Check for direct matches or substrings
    if any(p in clean_src for p in TIER_1_PRIMARY):
        return 1
    if any(s in clean_src for s in TIER_2_SECONDARY):
        return 2
    if any(t in clean_src for t in TIER_3_TERTIARY):
        return 3
        
    return 3  # Default to speculative Tier 3 if unknown


def validate_source_quality_tiers(record: Dict[str, Any]) -> bool:
    """
    Enforces quality checks based on source tiers. Critical identity fields 
    must rely on Tier 1 or Tier 2 verification, preventing unverified or 
    speculative tertiary data from being accepted as High confidence [1].
    """
    company_name = record.get("Company Name")
    overall_confidence = record.get("confidence_level", "Low").strip().title()

    # We validate the source of critical fields that define legal entity existence
    critical_fields_sources = {
        "Company Name": record.get("source_company_name"),
        "Year of Incorporation": record.get("source_year_founded"),
        "Company Headquarters": record.get("source_hq")
    }

    # Verify that we have declared sources for these critical fields
    for field_name, source in critical_fields_sources.items():
        if not source:
            raise ValueError(f"Field Validation Error: Sourcing data missing for critical field '{field_name}'.")

    # Enforce strict compliance rules
    for field_name, source in critical_fields_sources.items():
        tier = get_source_tier(source)
        
        # Rule A: Critical identity parameters must never rely strictly on Tier 3 (Tertiary) sources
        if tier == 3:
            raise ValueError(
                f"Source Tier Exception: Critical parameter '{field_name}' for '{company_name}' "
                f"is sourced via a speculative Tier 3 source: '{source}'. "
                f"Expected Tier 1 (Primary) or Tier 2 (Secondary) verification."
            )

    # Rule B: Overall record cannot be classified as "High" confidence if any critical parameter relies on Tier 2
    # without a Tier 1 anchor. Or more strictly, if overall confidence is High, all critical fields must be Tier 1.
    if overall_confidence == "High":
        for field_name, source in critical_fields_sources.items():
            tier = get_source_tier(source)
            if tier != 1:
                raise ValueError(
                    f"Confidence Mismatch: Overall record is classified as 'High' confidence, "
                    f"but critical parameter '{field_name}' relies on a non-primary Tier {tier} source: '{source}'."
                )

    return True


# --- Pytest Auditor Suite ---

def test_high_quality_primary_record_success():
    """
    Validates a record where all critical parameters rely strictly on Tier 1 sources.
    """
    record = {
        "Company Name": "Microsoft Corporation",
        "confidence_level": "High",
        "source_company_name": "SEC Filings",               # Tier 1
        "source_year_founded": "Company Registry",          # Tier 1
        "source_hq": "Company Website"                      # Tier 1
    }
    assert validate_source_quality_tiers(record) is True


def test_mixed_tier_medium_confidence_record_success():
    """
    Validates a standard mixed-tier record. Critical parameters are Tier 1/2,
    making it acceptable for a Medium confidence classification.
    """
    record = {
        "Company Name": "GitLab Inc.",
        "confidence_level": "Medium",
        "source_company_name": "SEC Filings",               # Tier 1
        "source_year_founded": "Company Registry",          # Tier 1
        "source_hq": "Website Contact Page"                # Tier 2
    }
    assert validate_source_quality_tiers(record) is True


def test_critical_fields_sourced_from_tertiary_fails():
    """
    Asserts that critical corporate parameters cannot be extracted from
    speculative Tier 3 sources like blogs or Twitter.
    """
    record = {
        "Company Name": "Stealth Corp",
        "confidence_level": "Medium",
        "source_company_name": "Blog Posts",                # Tier 3 - Fails!
        "source_year_founded": "Company Registry",          # Tier 1
        "source_hq": "Twitter"                              # Tier 3 - Fails!
    }
    with pytest.raises(ValueError, match="is sourced via a speculative Tier 3 source"):
        validate_source_quality_tiers(record)


def test_high_confidence_claimed_with_secondary_sources_fails():
    """
    Asserts that a record cannot claim 'High' confidence if any of its
    critical parameters rely on secondary (Tier 2) sources instead of Tier 1.
    """
    record = {
        "Company Name": "Tesla Inc.",
        "confidence_level": "High",                         # Conflict: High confidence claimed
        "source_company_name": "SEC Filings",               # Tier 1
        "source_year_founded": "LinkedIn",                  # Tier 2 - Prevents High confidence
        "source_hq": "Company Website"                      # Tier 1
    }
    with pytest.raises(ValueError, match="relies on a non-primary Tier 2 source"):
        validate_source_quality_tiers(record)