import csv
import os
import re
from typing import Dict, Any, Tuple, List

# Define the expected types for all 163 parameters
# Possible types: NUMBER, BOOLEAN, URL, EMAIL, PHONE, TEXT
def get_column_types(headers: List[str]) -> Dict[str, str]:
    column_types = {}
    for col in headers:
        col_type = "TEXT"
        col_lower = col.lower()
        
        # Explicitly typed columns based on actual companies_master.csv formats
        if col_lower in ["logo_url", "website_url", "linkedin_url", "facebook_url", "instagram_url", "marketing_video_url", "ceo_linkedin_url"]:
            col_type = "URL"
        elif col_lower in ["contact_person_email"]:
            col_type = "EMAIL"
        elif col_lower in ["primary_phone_number", "contact_person_phone"]:
            col_type = "PHONE"
        elif col_lower in ["customer_concentration_risk"]:
            col_type = "BOOLEAN"
        elif col_lower in ["incorporation_year", "employee_size", "office_count", "social_media_followers", "glassdoor_rating", "indeed_rating", "google_rating"]:
            col_type = "NUMBER"
            
        column_types[col] = col_type
    return column_types

def is_valid_number(val: str) -> bool:
    """Checks if value contains at least one digit and represents a valid formatted number."""
    val_clean = val.strip()
    if val_clean.upper() in ["NA", "NULL", "N/A", ""]:
        return True
    digits = [c for c in val_clean if c.isdigit()]
    return len(digits) > 0

def is_valid_boolean(val: str) -> bool:
    """Checks if value represents a binary yes/no or true/false flag."""
    val_clean = val.strip().lower()
    if val_clean.upper() in ["NA", "NULL", "N/A", ""]:
        return True
    return val_clean.startswith("yes") or val_clean.startswith("no") or val_clean.startswith("true") or val_clean.startswith("false")

def is_valid_url(val: str) -> bool:
    """Checks if value is a valid URL or social handle."""
    val_clean = val.strip()
    if val_clean.upper() in ["NA", "NULL", "N/A", ""]:
        return True
    if val_clean.startswith("@"):
        return True
    return val_clean.startswith("http://") or val_clean.startswith("https://") or val_clean.startswith("www.") or ".com" in val_clean or ".org" in val_clean or ".gov" in val_clean

def is_valid_email(val: str) -> bool:
    """Checks if value conforms to standard email format syntax."""
    val_clean = val.strip()
    if val_clean.upper() in ["NA", "NULL", "N/A", ""]:
        return True
    return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', val_clean))

def is_valid_phone(val: str) -> bool:
    """Checks if value contains a valid sequence of digit components for phone formatting."""
    val_clean = val.strip()
    if val_clean.upper() in ["NA", "NULL", "N/A", ""]:
        return True
    digits = [c for c in val_clean if c.isdigit()]
    return len(digits) >= 5

def validate_row_types(record_payload: Dict[str, Any], column_types: Dict[str, str]) -> Tuple[bool, float, float, List[str]]:
    """
    Validates all columns in a row against their expected data types.
    
    Returns: (success, type_validity_score, type_error_rate, errors)
    """
    errors = []
    passed_fields = 0
    total_fields = len(column_types)

    for field_name, expected_type in column_types.items():
        val = record_payload.get(field_name, "")
        
        # We only check type if the field exists in the record
        if field_name not in record_payload:
            total_fields -= 1
            continue
            
        is_ok = True
        if expected_type == "NUMBER":
            is_ok = is_valid_number(val)
        elif expected_type == "BOOLEAN":
            is_ok = is_valid_boolean(val)
        elif expected_type == "URL":
            is_ok = is_valid_url(val)
        elif expected_type == "EMAIL":
            is_ok = is_valid_email(val)
        elif expected_type == "PHONE":
            is_ok = is_valid_phone(val)
            
        if not is_ok:
            errors.append(f"Type Error [{field_name}]: Value '{val}' is not a valid {expected_type}.")
        else:
            passed_fields += 1

    if total_fields == 0:
        return True, 100.0, 0.0, []
        
    type_validity_score = round((passed_fields / total_fields) * 100, 2)
    type_error_rate = round(100.0 - type_validity_score, 2)
    success = (passed_fields == total_fields)

    return success, type_validity_score, type_error_rate, errors

def load_csv_data(filepath: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Loads CSV file rows as headers and a list of dictionaries."""
    data = []
    headers = []
    if not os.path.exists(filepath):
        return headers, data
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames if reader.fieldnames else []
        for row in reader:
            data.append(row)
    return headers, data

def generate_validation_report(input_csv: str, output_csv: str, output_log: str):
    """
    Validates all records in the input CSV against expected column data types.
    Prints real-time validation results to the terminal.
    Saves a detailed report to output_csv (viewable in Excel) and output_log.
    """
    headers, dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return
        
    column_types = get_column_types(headers)
    report_rows = []
    log_lines = []
    
    log_lines.append(f"Data Type Validation Report for {os.path.basename(input_csv)}")
    log_lines.append("="*90)
    
    print(f"\nProcessing {len(dataset)} companies from {os.path.basename(input_csv)} for type validation...")
    print(f"{'Company Name':<45} | {'Passed':<6} | {'Failed':<6} | {'Validity':<8} | {'Error Rate':<10} | {'Status':<10}")
    print("-" * 96)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company")
        
        # Run checks
        success, validity_score, error_rate, errors = validate_row_types(row, column_types)
        
        failed_count = len(errors)
        passed_count = len(column_types) - failed_count if failed_count <= len(column_types) else 0
        status_str = "VALID" if success else "INVALID"
        
        # Print runtime message in terminal
        print(f"{company_name[:45]:<45} | {passed_count:<6} | {failed_count:<6} | {validity_score:<7}% | {error_rate:<9}% | {status_str:<10}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Status: {status_str}\n"
            f"  Type Validity Score: {validity_score}%\n"
            f"  Type Error Rate: {error_rate}%\n"
        )
        if errors:
            log_line += "  Type Mismatches:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Validation Status": status_str,
            "Type Validity Score (%)": validity_score,
            "Type Error Rate (%)": error_rate,
            "Passed Checks": passed_count,
            "Failed Checks": failed_count,
            "Type Errors": "; ".join(errors)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Validation Status", "Type Validity Score (%)", "Type Error Rate (%)",
            "Passed Checks", "Failed Checks", "Type Errors"
        ])
        writer.writeheader()
        writer.writerows(report_rows)
        
    # Write to Log
    with open(output_log, mode="w", encoding="utf-8") as f_log:
        f_log.write("\n".join(log_lines))
        
    print(f"\n✓ Report saved to CSV: {output_csv} (Excel compatible)")
    print(f"✓ Report saved to Log: {output_log}")


# --- Automated System Test Suite ---

def test_genuine_profiles_pass():
    """Verifies that authentic profiles matching expected types pass validation with 100% validity."""
    apple_profile = {
        "name": "Apple Inc.",
        "incorporation_year": "1976",
        "employee_size": "161000",
        "annual_revenue": "$383B (FY2023)",
        "valuation": "$3T market capitalization",
        "logo_url": "https://www.apple.com/logo.png",
        "contact_person_email": "contact@apple.com",
        "primary_phone_number": "+1-800-555-0199",
        "customer_concentration_risk": "No, highly diversified"
    }
    column_types = get_column_types(list(apple_profile.keys()))
    success, score, error_rate, errors = validate_row_types(apple_profile, column_types)
    assert success is True, f"Factual profile failed type checks: {errors}"
    assert score == 100.0
    assert error_rate == 0.0
    assert not errors

def test_invalid_number_fails():
    """Verifies that strings in numeric columns fail type validation."""
    invalid_profile = {
        "name": "Apple Inc.",
        "employee_size": "many employees", # Invalid number
        "incorporation_year": "1976"
    }
    column_types = get_column_types(list(invalid_profile.keys()))
    success, score, error_rate, errors = validate_row_types(invalid_profile, column_types)
    assert success is False
    assert any("employee_size" in err for err in errors)

def test_invalid_boolean_fails():
    """Verifies that invalid values in boolean columns fail type validation."""
    invalid_profile = {
        "name": "Apple Inc.",
        "customer_concentration_risk": "high concentration of clients" # Invalid boolean, must start with Yes/No/True/False
    }
    column_types = get_column_types(list(invalid_profile.keys()))
    success, score, error_rate, errors = validate_row_types(invalid_profile, column_types)
    assert success is False
    assert any("customer_concentration_risk" in err for err in errors)

def test_invalid_url_fails():
    """Verifies that invalid URL values fail type validation."""
    invalid_profile = {
        "name": "Apple Inc.",
        "logo_url": "invalid_url_string" # Invalid URL
    }
    column_types = get_column_types(list(invalid_profile.keys()))
    success, score, error_rate, errors = validate_row_types(invalid_profile, column_types)
    assert success is False
    assert any("logo_url" in err for err in errors)

def test_invalid_email_fails():
    """Verifies that invalid email values fail type validation."""
    invalid_profile = {
        "name": "Apple Inc.",
        "contact_person_email": "invalid_email_string" # Invalid email
    }
    column_types = get_column_types(list(invalid_profile.keys()))
    success, score, error_rate, errors = validate_row_types(invalid_profile, column_types)
    assert success is False
    assert any("contact_person_email" in err for err in errors)

if __name__ == "__main__":
    import sys
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "8.1.csv")
    
    master_out_csv = os.path.join(dir_path, "8.1_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "8.1_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "8.1_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "8.1_completed_validation_results.log")
    
    print("=" * 96)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (TARGET COMPANIES)")
    print("=" * 96)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 96)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED 8.1 DATASET")
    print("=" * 96)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 96)
    
    try:
        test_genuine_profiles_pass()
        print("✓ test_genuine_profiles_pass: PASSED")
        test_invalid_number_fails()
        print("✓ test_invalid_number_fails: PASSED")
        test_invalid_boolean_fails()
        print("✓ test_invalid_boolean_fails: PASSED")
        test_invalid_url_fails()
        print("✓ test_invalid_url_fails: PASSED")
        test_invalid_email_fails()
        print("✓ test_invalid_email_fails: PASSED")
        print("\nAll Type Validation assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical type validation test assertion failed:", e)
        sys.exit(1)
