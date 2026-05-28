import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
import pytest

# =====================================================================
# Constants, Registries, and Databases
# =====================================================================

HIGH_RELIABILITY_SOURCES = {"Company Registry / SEC Filings", "SEC Filings", "Company Registry"}

SPECULATIVE_SOURCES = {"AI inference", "3rd Party DB Estimates", "Manual Research", "Inference"}

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

# Friday, May 22, 2026
SYSTEM_BASELINE_DATE = datetime(2026, 5, 22)

# Criticality weights based on schema parameters
FIELD_WEIGHTS = {
    # Critical Parameters (Weight = 10)
    "Company Name": 10,
    "Category": 10,
    "Year of Incorporation": 10,
    "Nature of Company": 10,
    "Company Headquarters": 10,
    "Employee Size": 10,
    "Website URL": 10,
    "CEO Name": 10,
    
    # High Importance Parameters (Weight = 5)
    "Recent News": 5,
    "Annual Revenues": 5,
    "Recent Funding Rounds": 5,
    "Total Capital Raised": 5,
    "Hiring Velocity": 5,
    "Employee Turnover": 5,
    
    # Medium Importance Parameters (Weight = 2)
    "Short Name": 2,
    "Logo": 2,
    "Countries Operating In": 2,
    "Office Locations": 2,
    "Market Share (%)": 2,
    "Key Investors / Backers": 2,
    
    # Low Importance Parameters (Weight = 1)
    "Quality of Website": 1,
    "Website Rating": 1,
    "Website Traffic Rank": 1,
    "Glassdoor Rating": 1,
    "Indeed Rating": 1
}


# =====================================================================
# Validation & Calculation Functions
# =====================================================================

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

    # Rule C: If the record has mixed sources (verified legal but inferred culture), High is disallowed
    if clean_source == "Mixed" and has_subjective_metrics and clean_confidence == "High":
        raise ValueError(
            f"Confidence Mismatch: Mixed data record with subjective elements for '{company_name}' "
            f"must be capped at 'Medium' or 'Low' confidence levels."
        )

    return True


def get_source_tier(source_string: str) -> int:
    """Classifies a data source string into Tier 1, 2, or 3."""
    clean_src = str(source_string).strip().lower()
    
    if any(p in clean_src for p in TIER_1_PRIMARY):
        return 1
    if any(s in clean_src for s in TIER_2_SECONDARY):
        return 2
    if any(t in clean_src for t in TIER_3_TERTIARY):
        return 3
        
    return 3


def validate_source_quality_tiers(record: Dict[str, Any]) -> bool:
    """
    Enforces quality checks based on source tiers. Critical identity fields 
    must rely on Tier 1 or Tier 2 verification.
    """
    company_name = record.get("Company Name")
    overall_confidence = record.get("confidence_level", "Low").strip().title()

    critical_fields_sources = {
        "Company Name": record.get("source_company_name"),
        "Year of Incorporation": record.get("source_year_founded"),
        "Company Headquarters": record.get("source_hq")
    }

    # Verify that we have declared sources for these critical fields
    for field_name, source in critical_fields_sources.items():
        if not source:
            raise ValueError(f"Field Validation Error: Sourcing data missing for critical field '{field_name}'.")

    # Enforce compliance rules
    for field_name, source in critical_fields_sources.items():
        tier = get_source_tier(source)
        
        # Rule A: Critical identity parameters must never rely strictly on Tier 3 (Tertiary) sources
        if tier == 3:
            raise ValueError(
                f"Source Tier Exception: Critical parameter '{field_name}' for '{company_name}' "
                f"is sourced via a speculative Tier 3 source: '{source}'. "
                f"Expected Tier 1 (Primary) or Tier 2 (Secondary) verification."
            )

    # Rule B: If overall confidence is High, all critical fields must be Tier 1.
    if overall_confidence == "High":
        for field_name, source in critical_fields_sources.items():
            tier = get_source_tier(source)
            if tier != 1:
                raise ValueError(
                    f"Confidence Mismatch: Overall record is classified as 'High' confidence, "
                    f"but critical parameter '{field_name}' relies on a non-primary Tier {tier} source: '{source}'."
                )

    return True


def extract_dates_from_string(text: str) -> List[datetime]:
    """Extracts YYYY-MM-DD or YYYY-MM dates from a text string."""
    full_dates = re.findall(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    extracted = []
    for y, m, d in full_dates:
        try:
            extracted.append(datetime(int(y), int(m), int(d)))
        except ValueError:
            pass
            
    month_dates = re.findall(r"\b(\d{4})-(\d{2})\b", text)
    for y, m in month_dates:
        if not any(d.year == int(y) and d.month == int(m) for d in extracted):
            try:
                extracted.append(datetime(int(y), int(m), 1))
            except ValueError:
                pass
                
    return extracted


def calculate_months_difference(date_a: datetime, date_b: datetime) -> int:
    """Calculates the absolute difference in months between two datetime objects."""
    return abs((date_a.year - date_b.year) * 12 + date_a.month - date_b.month)


def validate_record_recency(record: Dict[str, Any]) -> bool:
    """
    Audits the recency of the company profile.
    Ensures that volatile records with stale updates (>12 months) cannot carry
    a 'High' confidence level.
    """
    company_name = record.get("Company Name")
    recent_news = record.get("Recent News")
    overall_confidence = record.get("confidence_level", "Low").strip().title()
    
    if not recent_news:
        if overall_confidence == "High":
            raise ValueError(
                f"Recency Exception: Record for '{company_name}' lacks a recent timeline "
                f"to verify operational freshness. 'High' confidence level is disallowed."
            )
        return True

    extracted_dates = extract_dates_from_string(str(recent_news))
    if not extracted_dates:
        if overall_confidence == "High":
            raise ValueError(
                f"Recency Exception: Cannot verify recency for '{company_name}' due to "
                f"malformed dates. 'High' confidence level is disallowed."
            )
        return True

    newest_date = max(extracted_dates)
    months_old = calculate_months_difference(SYSTEM_BASELINE_DATE, newest_date)

    if months_old <= 6:
        record["recency_tier"] = "Recent"
    elif months_old <= 12:
        record["recency_tier"] = "Acceptable"
    else:
        record["recency_tier"] = "Outdated"

    # Freshness Rules
    if record["recency_tier"] == "Outdated":
        record["requires_refresh"] = True
        if overall_confidence == "High":
            raise ValueError(
                f"Recency Mismatch: Record for '{company_name}' is 'Outdated' (latest data is "
                f"{months_old} months old). A 'High' confidence level is disallowed until refreshed."
            )
    else:
        record["requires_refresh"] = False

    return True


def calculate_composite_quality_score(record: Dict[str, Any]) -> Tuple[float, str]:
    """
    Calculates the weighted composite quality score for a company record.
    
    Formula:
      - Completeness: Sum(weights of populated fields) / Sum(all field weights)
      - Accuracy: Average confidence level of populated fields (High=100%, Medium=70%, Low=40%)
      - Recency: Freshness of record (Recent=100%, Acceptable=85%, Outdated=50%, Unknown=0%)
      
      Composite = (Completeness * 0.4) + (Accuracy * 0.4) + (Recency * 0.2)
    """
    total_possible_weight = sum(FIELD_WEIGHTS.values())
    populated_weight = 0.0
    confidence_sum = 0.0
    populated_count = 0

    # 1. Evaluate Completeness & Accuracy
    for field, weight in FIELD_WEIGHTS.items():
        val = record.get(field)
        if val is not None and str(val).strip() != "" and str(val).lower() != "n/a":
            populated_weight += weight
            populated_count += 1
            
            field_conf = record.get(f"confidence_{field.lower().replace(' ', '_')}", "Medium").strip().title()
            if field_conf == "High":
                confidence_sum += 1.0
            elif field_conf == "Medium":
                confidence_sum += 0.7
            else:
                confidence_sum += 0.4

    completeness_score = (populated_weight / total_possible_weight) * 100
    accuracy_score = (confidence_sum / populated_count * 100) if populated_count > 0 else 0.0

    # 2. Evaluate Recency
    recency_tier = record.get("recency_tier", "Unknown").strip().title()
    if recency_tier == "Recent":
        recency_score = 100.0
    elif recency_tier == "Acceptable":
        recency_score = 85.0
    elif recency_tier == "Outdated":
        recency_score = 50.0
    else:
        recency_score = 0.0

    # 3. Calculate Weighted Composite Percentage
    composite_score = (completeness_score * 0.4) + (accuracy_score * 0.4) + (recency_score * 0.2)

    # 4. Map to Quality Grades
    if composite_score >= 90.0:
        grade = "A"
    elif composite_score >= 80.0:
        grade = "B"
    elif composite_score >= 70.0:
        grade = "C"
    elif composite_score >= 60.0:
        grade = "D"
    else:
        grade = "F"

    # Downgrade to F if any critical field is completely missing
    critical_fields = [f for f, w in FIELD_WEIGHTS.items() if w == 10]
    for field in critical_fields:
        if record.get(field) is None or str(record.get(field)).strip() == "":
            grade = "F"
            break

    return round(composite_score, 2), grade


def validate_record_quality_threshold(record: Dict[str, Any]) -> bool:
    """Enforces overall quality thresholds. Halts execution if 'F' grade."""
    score, grade = calculate_composite_quality_score(record)
    record["composite_quality_score"] = score
    record["quality_grade"] = grade

    if grade == "F":
        raise ValueError(
            f"Quality Threshold Violated: Record has failed quality grading with "
            f"an 'F' grade (Score: {score}%). Processing halted."
        )

    return True


# =====================================================================
# Pytest Suites
# =====================================================================

# --- Tests from tc_15.1.py ---

def test_high_confidence_regulatory_profile_success():
    """Validates public enterprise record sourced from official regulatory filings."""
    record = {
        "Company Name": "Apple Inc.",
        "data_source": "Company Registry / SEC Filings",
        "confidence_level": "High",
        "Annual Revenues": "$383,000,000,000 (Confirmed)",
        "Work culture": "Standard corporate policies enforced."
    }
    assert validate_record_confidence_boundaries(record) is True


def test_mixed_medium_confidence_profile_success():
    """Validates mixed-source record with subjective culture indicators."""
    record = {
        "Company Name": "GitLab Inc.",
        "data_source": "Mixed",
        "confidence_level": "Medium",
        "Annual Revenues": "$500,000,000",
        "Work culture": "Collaborative (Glassdoor Inferred)"
    }
    assert validate_record_confidence_boundaries(record) is True


def test_speculative_source_false_high_confidence_fails():
    """Asserts that speculative AI inference source is rejected with High confidence."""
    record = {
        "Company Name": "Stealth Tech",
        "data_source": "AI inference",
        "confidence_level": "High",
        "Annual Revenues": "$5,000,000 (Estimated)"
    }
    with pytest.raises(ValueError, match="is not permitted for speculative data"):
        validate_record_confidence_boundaries(record)


def test_estimated_financials_false_high_confidence_fails():
    """Asserts that a record with estimated financials cannot claim 'High' confidence."""
    record = {
        "Company Name": "Apex SaaS LLC",
        "data_source": "Company Registry",
        "confidence_level": "High",
        "Annual Revenues": "$10,000,000 (Estimated)"
    }
    with pytest.raises(ValueError, match="capping the overall 'confidence_level' at 'Medium' or 'Low'"):
        validate_record_confidence_boundaries(record)


def test_mixed_record_with_subjective_excessive_confidence_fails():
    """Asserts that mixed record with subjective metrics cannot claim 'High' confidence."""
    record = {
        "Company Name": "GitLab Inc.",
        "data_source": "Mixed",
        "confidence_level": "High",
        "Annual Revenues": "$500,000,000",
        "Work culture": "Collaborative (Glassdoor Inferred)"
    }
    with pytest.raises(ValueError, match="must be capped at 'Medium' or 'Low' confidence levels"):
        validate_record_confidence_boundaries(record)


# --- Tests from tc_15.2.py ---

def test_high_quality_primary_record_success():
    """Validates record where all critical parameters rely strictly on Tier 1 sources."""
    record = {
        "Company Name": "Microsoft Corporation",
        "confidence_level": "High",
        "source_company_name": "SEC Filings",
        "source_year_founded": "Company Registry",
        "source_hq": "Company Website"
    }
    assert validate_source_quality_tiers(record) is True


def test_mixed_tier_medium_confidence_record_success():
    """Validates mixed-tier record where critical parameters are Tier 1/2."""
    record = {
        "Company Name": "GitLab Inc.",
        "confidence_level": "Medium",
        "source_company_name": "SEC Filings",
        "source_year_founded": "Company Registry",
        "source_hq": "Website Contact Page"
    }
    assert validate_source_quality_tiers(record) is True


def test_critical_fields_sourced_from_tertiary_fails():
    """Asserts critical corporate parameters cannot rely strictly on Tier 3 sources."""
    record = {
        "Company Name": "Stealth Corp",
        "confidence_level": "Medium",
        "source_company_name": "Blog Posts",
        "source_year_founded": "Company Registry",
        "source_hq": "Twitter"
    }
    with pytest.raises(ValueError, match="is sourced via a speculative Tier 3 source"):
        validate_source_quality_tiers(record)


def test_high_confidence_claimed_with_secondary_sources_fails():
    """Asserts record cannot claim 'High' confidence if critical fields use Tier 2 sources."""
    record = {
        "Company Name": "Tesla Inc.",
        "confidence_level": "High",
        "source_company_name": "SEC Filings",
        "source_year_founded": "LinkedIn",
        "source_hq": "Company Website"
    }
    with pytest.raises(ValueError, match="relies on a non-primary Tier 2 source"):
        validate_source_quality_tiers(record)


# --- Tests from tc_15.3.py ---

def test_recent_timeline_success():
    """Validates record recency with events in the last 6 months."""
    record = {
        "Company Name": "NeuraLaunch Corp",
        "Recent News": "2026-03-10 - Acquired New Startup, 2025-12-25 - Launched Version 2.0",
        "confidence_level": "High"
    }
    
    assert validate_record_recency(record) is True
    assert record["recency_tier"] == "Recent"
    assert record["requires_refresh"] is False


def test_acceptable_timeline_success():
    """Validates record recency with events between 6 and 12 months old."""
    record = {
        "Company Name": "Apex SaaS LLC",
        "Recent News": "2025-08-15 - Opened New Office",
        "confidence_level": "Medium"
    }
    
    assert validate_record_recency(record) is True
    assert record["recency_tier"] == "Acceptable"
    assert record["requires_refresh"] is False


def test_outdated_timeline_low_confidence_success():
    """Ensures outdated record passes if confidence is correctly restricted."""
    record = {
        "Company Name": "Legacy Tech Corp",
        "Recent News": "2024-02-10 - Series A Funding",
        "confidence_level": "Medium"
    }
    
    assert validate_record_recency(record) is True
    assert record["recency_tier"] == "Outdated"
    assert record["requires_refresh"] is True


def test_outdated_timeline_false_high_confidence_fails():
    """Asserts outdated details cause rejection if claiming High confidence."""
    record = {
        "Company Name": "Legacy Tech Corp",
        "Recent News": "2024-02-10 - Series A Funding",
        "confidence_level": "High"
    }
    
    with pytest.raises(ValueError, match="is 'Outdated' .* A 'High' confidence level is disallowed"):
        validate_record_recency(record)


def test_malformed_dates_prevent_high_confidence_fails():
    """Asserts that malformed dates block 'High' confidence claims."""
    record = {
        "Company Name": "Unresolved LLC",
        "Recent News": "Sometime last year - Opened new headquarters",
        "confidence_level": "High"
    }
    
    with pytest.raises(ValueError, match="Cannot verify recency .* 'High' confidence level is disallowed"):
        validate_record_recency(record)


# --- Tests from tc_15.5.py ---

def test_perfect_enterprise_profile_grade_a():
    """Validates completely populated, high-confidence enterprise record yields grade A."""
    record = {
        # Critical Fields
        "Company Name": "Microsoft Corp.",
        "Category": "Enterprise",
        "Year of Incorporation": 1975,
        "Nature of Company": "Public",
        "Company Headquarters": "Redmond, USA",
        "Employee Size": "100000+",
        "Website URL": "https://www.microsoft.com",
        "CEO Name": "Satya Nadella",
        
        # High Fields
        "Recent News": "2026-03-10 - Acquired New Startup",
        "Annual Revenues": "$211B",
        "Recent Funding Rounds": "N/A",
        "Total Capital Raised": "$10B",
        "Hiring Velocity": "High",
        "Employee Turnover": "10%",
        
        "recency_tier": "Recent",
        
        "confidence_company_name": "High",
        "confidence_category": "High",
        "confidence_year_of_incorporation": "High",
        "confidence_nature_of_company": "High",
        "confidence_company_headquarters": "High",
        "confidence_employee_size": "High",
        "confidence_website_url": "High",
        "confidence_ceo_name": "High",
        "confidence_recent_news": "High",
        "confidence_annual_revenues": "High"
    }
    
    assert validate_record_quality_threshold(record) is True
    assert record["quality_grade"] == "A"
    assert record["composite_quality_score"] >= 90.0


def test_mixed_startup_profile_grade_b_or_c():
    """Validates standard startup missing several optional parameters gets passing grade."""
    record = {
        "Company Name": "SaaSLauncher",
        "Category": "Startup",
        "Year of Incorporation": 2022,
        "Nature of Company": "Private",
        "Company Headquarters": "Boston, USA",
        "Employee Size": "11-50",
        "Website URL": "https://www.saaslaunch.com",
        "CEO Name": "Jane Doe",
        
        "Recent News": None,
        "Annual Revenues": None,
        "Total Capital Raised": None,
        
        "recency_tier": "Acceptable"
    }
    
    assert validate_record_quality_threshold(record) is True
    assert record["quality_grade"] in ["B", "C"]


def test_missing_critical_field_auto_fails_to_f():
    """Asserts missing critical parameter (CEO Name) downgrades record to F."""
    record = {
        "Company Name": "SaaSLauncher",
        "Category": "Startup",
        "Year of Incorporation": 2022,
        "Nature of Company": "Private",
        "Company Headquarters": "Boston, USA",
        "Employee Size": "11-50",
        "Website URL": "https://www.saaslaunch.com",
        "CEO Name": None,
        "recency_tier": "Recent"
    }
    
    with pytest.raises(ValueError, match="failed quality grading with an 'F' grade"):
        validate_record_quality_threshold(record)


def test_low_confidence_and_outdated_fails_to_f():
    """Asserts heavily low-confidence and outdated fields drop score below threshold."""
    record = {
        "Company Name": "Stale Corp",
        "Category": "Startup",
        "Year of Incorporation": 2010,
        "Nature of Company": "Private",
        "Company Headquarters": "Detroit, USA",
        "Employee Size": "1-10",
        "Website URL": "https://www.stale.com",
        "CEO Name": "John Stale",
        
        "recency_tier": "Outdated",
        
        "confidence_company_name": "Low",
        "confidence_category": "Low",
        "confidence_year_of_incorporation": "Low",
        "confidence_nature_of_company": "Low",
        "confidence_company_headquarters": "Low",
        "confidence_employee_size": "Low",
        "confidence_website_url": "Low",
        "confidence_ceo_name": "Low"
    }
    
    with pytest.raises(ValueError, match="failed quality grading with an 'F' grade"):
        validate_record_quality_threshold(record)