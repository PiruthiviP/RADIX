import csv
import os
import re
import json
import datetime
from typing import Dict, Any, Tuple, List, Optional

# Allowed source mappings as defined by the metadata schema
ALLOWED_SOURCES_BY_FIELD = {
    "Company Name": ["Company Registry", "SEC Filings", "Government Database"],
    "Logo": ["Official Website", "LinkedIn"],
    "Employee Size": ["LinkedIn", "HR Tools", "Crunchbase"],
    "Annual Revenues": ["SEC Filings", "Annual Reports", "Company Registry"],
    "Website URL": ["Official Registry", "Company Registry"],
    "Recent News": ["PR Newswire", "Crunchbase", "Official Press Releases"]
}

# Non-credible domains to check credibility
CREDIBILITY_BLACKLIST = ["random-blog.com", "leakforums.net", "wikipedia.org", "blogspot.com"]

# Bidirectional mapping between CSV headers and METADATA_SCHEMA keys
CSV_HEADER_MAP: Dict[str, str] = {
    'name': 'Company Name',
    'logo_url': 'Logo',
    'employee_size': 'Employee Size',
    'annual_revenue': 'Annual Revenues',
    'website_url': 'Website URL',
    'recent_news': 'Recent News'
}

def validate_lineage_attribution(record_payload: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """
    Validates the source attribution and lineage of critical company fields.
    Checks:
    - Presence of attribution for populated critical fields.
    - Allowed source types.
    - Non-blacklisted source domains.
    - Timestamp validity (not in future, not older than 1 year, format YYYY-MM-DD).
    Returns: (success, lineage_score, errors)
    """
    errors = []
    current_date = datetime.date(2026, 5, 26)  # Current execution date context
    min_acceptable_date = current_date - datetime.timedelta(days=365) # max 1 year old source
    
    checked_fields = 0
    passed_checks = 0

    for csv_col, schema_key in CSV_HEADER_MAP.items():
        field_value = record_payload.get(csv_col)
        
        # Validate only if the field is populated
        if field_value is not None and str(field_value).strip() != "" and str(field_value).upper() != "NA":
            checked_fields += 1
            
            # Retrieve attribution string from CSV row
            attribution_raw = record_payload.get(f"_attribution_{csv_col}")
            
            if not attribution_raw or str(attribution_raw).strip() == "" or str(attribution_raw).upper() == "NA":
                errors.append(f"Lineage Error [{schema_key}]: Missing '_attribution_{csv_col}' block.")
                continue
                
            # Parse JSON block if it's a string
            attribution = {}
            if isinstance(attribution_raw, str):
                try:
                    attribution = json.loads(attribution_raw)
                except json.JSONDecodeError:
                    errors.append(f"Lineage Error [{schema_key}]: Invalid JSON in '_attribution_{csv_col}': '{attribution_raw}'")
                    continue
            elif isinstance(attribution_raw, dict):
                attribution = attribution_raw
                
            source_type = attribution.get("source_type")
            source_url = attribution.get("source_url", "")
            timestamp_str = attribution.get("timestamp", "")
            
            field_errors = []
            
            # Check 1: Allowed source type check
            allowed_origins = ALLOWED_SOURCES_BY_FIELD[schema_key]
            if source_type not in allowed_origins:
                field_errors.append(f"Unpermitted source '{source_type}'. Allowed: {allowed_origins}")
                
            # Check 2: Domain credibility check
            if any(blacklisted in source_url.lower() for blacklisted in CREDIBILITY_BLACKLIST):
                field_errors.append(f"Blacklisted untrusted domain cited: '{source_url}'")
                
            # Check 3: Timestamp validity check
            try:
                source_date = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d").date()
                if source_date > current_date:
                    field_errors.append(f"Future source date: '{timestamp_str}'")
                elif source_date < min_acceptable_date:
                    field_errors.append(f"Expired source date: '{timestamp_str}' (older than {min_acceptable_date})")
            except ValueError:
                field_errors.append(f"Malformed date format '{timestamp_str}'. Use YYYY-MM-DD")
                
            if len(field_errors) == 0:
                passed_checks += 1
            else:
                for err in field_errors:
                    errors.append(f"Attribution Mismatch [{schema_key}]: {err}")

    if checked_fields == 0:
        return True, 100.0, []
        
    lineage_score = round((passed_checks / checked_fields) * 100, 2)
    success = (lineage_score == 100.0)
    
    return success, lineage_score, errors

def load_csv_data(filepath: str) -> List[Dict[str, Any]]:
    """Loads CSV file rows as a list of dictionaries."""
    data = []
    if not os.path.exists(filepath):
        return data
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def generate_validation_report(input_csv: str, output_csv: str, output_log: str):
    """
    Validates all companies in the input CSV against source attribution rules.
    Prints real-time validation results to the terminal.
    Saves a detailed report to output_csv (viewable in Excel) and output_log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return
        
    report_rows = []
    log_lines = []
    
    log_lines.append(f"Source Attribution Report for {os.path.basename(input_csv)}")
    log_lines.append("="*80)
    
    # We only process rows that have attribution fields populated in the header
    has_attribution = any(col in dataset[0] for col in ["_attribution_name", "_attribution_logo_url"])
    if not has_attribution:
        print(f"Skipped {input_csv}: No source attribution columns found.")
        return
        
    print(f"\nProcessing {len(dataset)} companies for source attribution...")
    print(f"{'Company Name':<50} | {'Passed':<6} | {'Failed':<6} | {'Score':<8} | {'Status':<8}")
    print("-" * 88)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company")
        
        # Calculate lineage checks
        success, lineage_score, errors = validate_lineage_attribution(row)
        
        # We checked 6 critical fields
        failed_count = len(errors)
        passed_count = 6 - failed_count if failed_count <= 6 else 0
        status_str = "VERIFIED" if success else "UNVERIFIED"
        
        # Print runtime message in terminal
        print(f"{company_name[:50]:<50} | {passed_count:<6} | {failed_count:<6} | {lineage_score:<7}% | {status_str:<8}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Status: {status_str}\n"
            f"  Lineage Score: {lineage_score}%\n"
        )
        if errors:
            log_line += "  Lineage Attribution Errors:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Validation Status": status_str,
            "Lineage Score (%)": lineage_score,
            "Passed Checks": passed_count,
            "Failed Checks": failed_count,
            "Attribution Errors": "; ".join(errors)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Validation Status", "Lineage Score (%)", "Passed Checks",
            "Failed Checks", "Attribution Errors"
        ])
        writer.writeheader()
        writer.writerows(report_rows)
        
    # Write to Log
    with open(output_log, mode="w", encoding="utf-8") as f_log:
        f_log.write("\n".join(log_lines))
        
    print(f"\n✓ Report saved to CSV: {output_csv} (Excel compatible)")
    print(f"✓ Report saved to Log: {output_log}")

# --- Pytest Tests ---

def test_valid_lineage_profile_passes():
    """Verifies that a fully traceable, credible profile record passes validation."""
    valid_record = {
        "name": "Apple Inc.",
        "_attribution_name": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov",
            "timestamp": "2026-04-15"
        },
        "logo_url": "https://logo.com/apple",
        "_attribution_logo_url": {
            "source_type": "LinkedIn",
            "source_url": "https://www.linkedin.com/company/apple",
            "timestamp": "2026-05-10"
        },
        "employee_size": "161000",
        "_attribution_employee_size": {
            "source_type": "Crunchbase",
            "source_url": "https://www.crunchbase.com/organization/apple",
            "timestamp": "2026-05-12"
        },
        "annual_revenue": "$383B",
        "_attribution_annual_revenue": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov",
            "timestamp": "2026-04-15"
        },
        "website_url": "https://www.apple.com",
        "_attribution_website_url": {
            "source_type": "Official Registry",
            "source_url": "https://www.sec.gov",
            "timestamp": "2026-04-15"
        },
        "recent_news": "Introduced M3 chip",
        "_attribution_recent_news": {
            "source_type": "PR Newswire",
            "source_url": "https://www.prnewswire.com",
            "timestamp": "2026-05-18"
        }
    }
    
    success, score, errors = validate_lineage_attribution(valid_record)
    assert success is True, f"Failed lineage check: {errors}"
    assert score == 100.0
    assert not errors

def test_missing_attribution_block_fails():
    """Verifies that populating a field without providing its source attribution fails validation."""
    invalid_record = {
        "name": "Apple Inc."
        # Missing '_attribution_name'
    }
    success, score, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("Missing '_attribution_name'" in err for err in errors)

def test_untrusted_blacklisted_source_fails():
    """Verifies that citing a blacklisted or non-credible domain for a metric fails validation."""
    invalid_record = {
        "name": "Apple Inc.",
        "_attribution_name": {
            "source_type": "SEC Filings",
            "source_url": "https://random-blog.com/leak/details",  # Blacklisted domain
            "timestamp": "2026-04-15"
        }
    }
    success, score, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("Blacklisted untrusted domain" in err for err in errors)

def test_unpermitted_source_type_fails():
    """Verifies that using an unpermitted source type for a specific parameter fails validation."""
    invalid_record = {
        "annual_revenue": "$383B",
        "_attribution_annual_revenue": {
            "source_type": "LinkedIn",  # Not a permitted source type for financials
            "source_url": "https://www.linkedin.com/company/apple",
            "timestamp": "2026-04-15"
        }
    }
    success, score, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("Unpermitted source" in err for err in errors)

def test_future_attribution_timestamp_fails():
    """Verifies that an attribution timestamp set in the future is caught and rejected."""
    invalid_record = {
        "name": "Apple Inc.",
        "_attribution_name": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov",
            "timestamp": "2027-10-12"  # Future date relative to May 26, 2026
        }
    }
    success, score, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("Future source date" in err for err in errors)

def test_expired_attribution_timestamp_fails():
    """Verifies that an attribution timestamp older than 1 year is rejected."""
    invalid_record = {
        "name": "Apple Inc.",
        "_attribution_name": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov",
            "timestamp": "2024-01-01"  # Older than 1 year
        }
    }
    success, score, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("Expired source date" in err for err in errors)

def test_malformed_timestamp_format_fails():
    """Verifies that a malformed date format is caught and rejected."""
    invalid_record = {
        "name": "Apple Inc.",
        "_attribution_name": {
            "source_type": "SEC Filings",
            "source_url": "https://www.sec.gov",
            "timestamp": "15/04/2026"  # Malformed date
        }
    }
    success, score, errors = validate_lineage_attribution(invalid_record)
    assert success is False
    assert any("Malformed date format" in err for err in errors)

if __name__ == "__main__":
    import sys
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "3.5.csv")
    
    master_out_csv = os.path.join(dir_path, "3.5_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "3.5_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "3.5_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "3.5_completed_validation_results.log")
    
    print("=" * 90)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (TARGET COMPANIES)")
    print("=" * 90)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 90)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED 3.5 DATASET")
    print("=" * 90)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 90)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 90)
    
    try:
        test_valid_lineage_profile_passes()
        print("✓ test_valid_lineage_profile_passes: PASSED")
        test_missing_attribution_block_fails()
        print("✓ test_missing_attribution_block_fails: PASSED")
        test_untrusted_blacklisted_source_fails()
        print("✓ test_untrusted_blacklisted_source_fails: PASSED")
        test_unpermitted_source_type_fails()
        print("✓ test_unpermitted_source_type_fails: PASSED")
        test_future_attribution_timestamp_fails()
        print("✓ test_future_attribution_timestamp_fails: PASSED")
        test_expired_attribution_timestamp_fails()
        print("✓ test_expired_attribution_timestamp_fails: PASSED")
        test_malformed_timestamp_format_fails()
        print("✓ test_malformed_timestamp_format_fails: PASSED")
        print("\nAll lineage and source attribution assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical factual accuracy test assertion failed:", e)
        sys.exit(1)
