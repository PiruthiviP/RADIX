import pytest
from typing import Dict, Any

# High reliability data sources
HIGH_RELIABILITY_SOURCES = {"Company Registry / SEC Filings", "SEC Filings", "Company Registry"}

# Speculative/Estimated data sources
SPECULATIVE_SOURCES = {"AI inference", "3rd Party DB Estimates", "Manual Research", "Inference"}


def validate_record_confidence_boundaries(record: Dict[str, Any]) -> bool:
    """
    Evaluates the company record's confidence metrics.
    Enforces strict rules that map overall data source reliability to the 
    declared overall confidence_level.
    """
    company_name = record.get("Company Name")
    data_source = record.get("data_source")
    overall_confidence = record.get("confidence_level")
    revenues = record.get("Annual Revenues")
    work_culture = record.get("Work culture")

    if not company_name or not data_source or not overall_confidence:
        raise ValueError("Field Validation Error: Missing critical record-level identifiers.")

    # 1. Standardize text strings
    clean_source = str(data_source).strip()
    clean_confidence = str(overall_confidence).strip().title()

    # Determine if core financials are estimated
    has_estimated_financials = False
    if revenues:
        if "estimate" in str(revenues).lower() or "inferred" in str(revenues).lower():
            has_estimated_financials = True

    # Determine if subjective metrics exist (e.g. culture extracted via sentiment)
    has_subjective_metrics = False
    if work_culture:
        if "inferred" in str(work_culture).lower() or "sentiment" in str(work_culture).lower():
            has_subjective_metrics = True

    # 2. Strict Confidence Level Boundary Enforcements
    # Rule A: If data source is explicitly speculative, the record CANNOT have a High confidence level
    if clean_source in SPECULATIVE_SOURCES and clean_confidence == "High":
        raise ValueError(
            f"Confidence Mismatch: Record for '{company_name}' is sourced via '{data_source}' "
            f"but claims an overall 'High' confidence level. This is not permitted for speculative data."
        )

    # Rule B: If core financials are estimated/inferred, overall confidence must be capped at Medium or Low
    if has_estimated_financials and clean_confidence == "High":
        raise ValueError(
            f"Confidence Mismatch: Record for '{company_name}' contains estimated financial figures, "
            f"capping the overall 'confidence_level' at 'Medium' or 'Low'."
        )

    # Rule C: If the record has mixed sources (verified legal but inferred culture), High is disallowed unless 
    # explicitly approved. It should generally map to Medium or lower.
    if clean_source == "Mixed" and has_subjective_metrics and clean_confidence == "High":
        raise ValueError(
            f"Confidence Mismatch: Mixed data record with subjective elements for '{company_name}' "
            f"must be capped at 'Medium' or 'Low' confidence levels."
        )

    return True


# --- Pytest Auditor Suite ---

def test_high_confidence_regulatory_profile_success():
    """
    Validates a public enterprise record sourced completely from official regulatory filings.
    """
    record = {
        "Company Name": "Apple Inc.",
        "data_source": "Company Registry / SEC Filings",
        "confidence_level": "High",
        "Annual Revenues": "$383,000,000,000 (Confirmed)",
        "Work culture": "Standard corporate policies enforced."
    }
    assert validate_record_confidence_boundaries(record) is True


def test_mixed_medium_confidence_profile_success():
    """
    Validates a mixed-source record with subjective culture indicators.
    """
    record = {
        "Company Name": "GitLab Inc.",
        "data_source": "Mixed",
        "confidence_level": "Medium",
        "Annual Revenues": "$500,000,000",
        "Work culture": "Collaborative (Glassdoor Inferred)"
    }
    assert validate_record_confidence_boundaries(record) is True


def test_speculative_source_false_high_confidence_fails():
    """
    Asserts that a record heavily dependent on speculative AI inference is
    rejected if it claims an unverified 'High' confidence level.
    """
    record = {
        "Company Name": "Stealth Tech",
        "data_source": "AI inference",
        "confidence_level": "High",  # Conflict: Sourced via AI inference but claiming High confidence
        "Annual Revenues": "$5,000,000 (Estimated)"
    }
    with pytest.raises(ValueError, match="is not permitted for speculative data"):
        validate_record_confidence_boundaries(record)


def test_estimated_financials_false_high_confidence_fails():
    """
    Asserts that a record with estimated financials cannot claim 'High' confidence.
    """
    record = {
        "Company Name": "Apex SaaS LLC",
        "data_source": "Company Registry",
        "confidence_level": "High",
        "Annual Revenues": "$10,000,000 (Estimated)"  # Conflict: Estimated financials present
    }
    with pytest.raises(ValueError, match="capping the overall 'confidence_level' at 'Medium' or 'Low'"):
        validate_record_confidence_boundaries(record)


def test_mixed_record_with_subjective_excessive_confidence_fails():
    """
    Asserts that a mixed record containing subjective metrics (e.g. Glassdoor inferred culture)
    cannot claim 'High' confidence.
    """
    record = {
        "Company Name": "GitLab Inc.",
        "data_source": "Mixed",
        "confidence_level": "High",  # Conflict: Mixed record with subjective culture
        "Annual Revenues": "$500,000,000",
        "Work culture": "Collaborative (Glassdoor Inferred)"
    }
    with pytest.raises(ValueError, match="must be capped at 'Medium' or 'Low' confidence levels"):
        validate_record_confidence_boundaries(record)