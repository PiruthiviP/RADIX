import pytest
from typing import Dict, Any, Tuple

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


def calculate_composite_quality_score(record: Dict[str, Any]) -> Tuple[float, str]:
    """
    Calculates the weighted composite quality score for a company record [1, 3].
    
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
            
            # Map field-specific confidence levels to percentages
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

    # Strict Rule: If any critical field is missing entirely, automatically downgrade to F
    critical_fields = [f for f, w in FIELD_WEIGHTS.items() if w == 10]
    for field in critical_fields:
        if record.get(field) is None or str(record.get(field)).strip() == "":
            grade = "F"
            break

    return round(composite_score, 2), grade


def validate_record_quality_threshold(record: Dict[str, Any]) -> bool:
    """
    SDET Validator: Enforces overall quality thresholds.
    Halts execution if the composite score calculates to an 'F' grade [1].
    """
    score, grade = calculate_composite_quality_score(record)
    record["composite_quality_score"] = score
    record["quality_grade"] = grade

    if grade == "F":
        raise ValueError(
            f"Quality Threshold Violated: Record has failed quality grading with "
            f"an 'F' grade (Score: {score}%). Processing halted."
        )

    return True


# --- Pytest Ingestion & Scoring Suite ---

def test_perfect_enterprise_profile_grade_a():
    """
    Validates a completely populated, high-confidence, fresh public enterprise 
    record. Expects a score of >= 90% and a grade of 'A'.
    """
    record = {
        # Critical Fields (Populated)
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
        
        # Freshness / Recency
        "recency_tier": "Recent",
        
        # Set High Confidence across all critical fields
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
    """
    Validates a standard startup record missing several optional parameters.
    Expects a passing grade (B or C) because critical parameters are intact.
    """
    record = {
        # Critical Fields (Populated)
        "Company Name": "SaaSLauncher",
        "Category": "Startup",
        "Year of Incorporation": 2022,
        "Nature of Company": "Private",
        "Company Headquarters": "Boston, USA",
        "Employee Size": "11-50",
        "Website URL": "https://www.saaslaunch.com",
        "CEO Name": "Jane Doe",
        
        # Missing non-critical fields (Leaves them as None)
        "Recent News": None,
        "Annual Revenues": None,
        "Total Capital Raised": None,
        
        # Freshness / Recency
        "recency_tier": "Acceptable"
    }
    
    assert validate_record_quality_threshold(record) is True
    assert record["quality_grade"] in ["B", "C"]


def test_missing_critical_field_auto_fails_to_f():
    """
    Asserts that if any critical identity parameter (like CEO Name) is missing,
    the scoring engine automatically downgrades the record to 'F' and halts ingestion.
    """
    record = {
        "Company Name": "SaaSLauncher",
        "Category": "Startup",
        "Year of Incorporation": 2022,
        "Nature of Company": "Private",
        "Company Headquarters": "Boston, USA",
        "Employee Size": "11-50",
        "Website URL": "https://www.saaslaunch.com",
        "CEO Name": None,  # Critical field missing
        "recency_tier": "Recent"
    }
    
    with pytest.raises(ValueError, match="failed quality grading with an 'F' grade"):
        validate_record_quality_threshold(record)


def test_low_confidence_and_outdated_fails_to_f():
    """
    Asserts that a record heavily populated with low-confidence and outdated
    parameters mathematically falls below the passing score threshold, failing with an 'F'.
    """
    record = {
        # Critical Fields present but low quality
        "Company Name": "Stale Corp",
        "Category": "Startup",
        "Year of Incorporation": 2010,
        "Nature of Company": "Private",
        "Company Headquarters": "Detroit, USA",
        "Employee Size": "1-10",
        "Website URL": "https://www.stale.com",
        "CEO Name": "John Stale",
        
        "recency_tier": "Outdated",  # Outdated data
        
        # Low confidence settings across everything
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