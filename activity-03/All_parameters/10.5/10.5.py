import csv
import os
import sys
from typing import Dict, Any, Tuple, List

# Verified registry of post-cutoff crisis events (layoffs, controversies, disruptions)
CRISIS_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    "Amazon.com, Inc.": [
        {
            "description": "2025 major workforce layoffs (14,000 jobs cut)",
            "field": "recent_news",
            "keywords": ["cuts 14000 jobs", "2025-10-28"]
        }
    ],
    "Microsoft Corporation": [
        {
            "description": "2025 workforce reductions",
            "field": "layoff_history",
            "keywords": ["2025", "4%"]
        }
    ],
    "Commonwealth Bank of Australia": [
        {
            "description": "2025 Consumer Data Right penalty",
            "field": "recent_news",
            "keywords": ["penalty", "consumer data right", "2025-12-09"]
        },
        {
            "description": "2025 Spam Law regulator delay controversy",
            "field": "recent_news",
            "keywords": ["delay spam law", "2025-12-30"]
        }
    ],
    "Swiggy Limited": [
        {
            "description": "2025 gig worker strikes controversy",
            "field": "legal_issues",
            "keywords": ["strikes", "2025"]
        }
    ],
    "Dunzo Digital Private Limited": [
        {
            "description": "2025 App operations shutdown",
            "field": "recent_news",
            "keywords": ["app operations shut down", "2025"]
        }
    ],
    "Morgan Stanley": [
        {
            "description": "2025 SEC supervision failure settlement ($15M)",
            "field": "recent_news",
            "keywords": ["sec settlement", "2025", "15m"]
        }
    ]
}

def validate_crisis_validity(record: Dict[str, Any]) -> Tuple[bool, float, float, List[str]]:
    """
    Validates if a company profile correctly represents post-cutoff crisis events (layoffs, controversies, disruptions).
    
    Returns: (success, validity_score, risk_score, errors)
    """
    errors = []
    company_name = record.get("name", "").strip()
    
    # Check if the company is registered for crisis cutoff tests
    matched_key = None
    for key in CRISIS_REGISTRY:
        if company_name.lower().strip() == key.lower().strip():
            matched_key = key
            break
            
    if not matched_key:
        # If no checks are defined for this company, it is compliant by default
        return True, 100.0, 0.0, []
        
    checks = CRISIS_REGISTRY[matched_key]
    passed_checks = 0
    total_checks = len(checks)
    
    for check in checks:
        desc = check["description"]
        field_name = check["field"]
        keywords = check["keywords"]
        
        field_val = str(record.get(field_name, "")).lower().strip()
        
        # Verify that all keywords are present in the target field value (case-insensitive)
        missing_kw = [kw for kw in keywords if kw.lower() not in field_val]
        
        if not missing_kw:
            passed_checks += 1
        else:
            errors.append(
                f"Crisis Validity Error [{desc} in field '{field_name}']: "
                f"Outdated or missing profile risk/crisis details. Missing keywords: {missing_kw}."
            )
            
    validity_score = round((passed_checks / total_checks) * 100, 2)
    risk_score = round(100.0 - validity_score, 2)
    success = (passed_checks == total_checks)
    
    return success, validity_score, risk_score, errors

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
    Validates all companies in the input CSV against post-cutoff crisis events.
    Prints real-time validation results to the terminal.
    Saves a detailed report to output_csv (viewable in Excel) and output_log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return
        
    report_rows = []
    log_lines = []
    
    log_lines.append(f"Crisis Validity (Layoffs/Controversies Cutoff) Report for {os.path.basename(input_csv)}")
    log_lines.append("="*96)
    
    print(f"\nProcessing {len(dataset)} companies from {os.path.basename(input_csv)} for crisis validity...")
    print(f"{'Company Name':<45} | {'Passed':<6} | {'Failed':<6} | {'Validity':<8} | {'Risk':<6} | {'Status':<10}")
    print("-" * 96)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company").strip()
        
        success, validity_score, risk_score, errors = validate_crisis_validity(row)
        
        failed_count = len(errors)
        matched_key = next((k for k in CRISIS_REGISTRY if k.lower().strip() == company_name.lower().strip()), None)
        total_checks = len(CRISIS_REGISTRY[matched_key]) if matched_key else 0
        passed_count = total_checks - failed_count
        status_str = "CURRENT" if success else "OUTDATED"
        
        # Print runtime message in terminal
        print(f"{company_name[:45]:<45} | {passed_count:<6} | {failed_count:<6} | {validity_score:<7}% | {risk_score:<5}% | {status_str:<10}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Status: {status_str}\n"
            f"  Crisis Validity Score: {validity_score}%\n"
            f"  Stagnation Risk Score: {risk_score}%\n"
        )
        if errors:
            log_line += "  Missing Cutoff Crisis Events:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Validation Status": status_str,
            "Crisis Validity Score (%)": validity_score,
            "Stagnation Risk Score (%)": risk_score,
            "Passed Checks": passed_count,
            "Failed Checks": failed_count,
            "Crisis Errors": "; ".join(errors)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Validation Status", "Crisis Validity Score (%)", "Stagnation Risk Score (%)",
            "Passed Checks", "Failed Checks", "Crisis Errors"
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
    """Verifies that authentic profiles containing correct post-cutoff crisis events pass validation with 100% validity."""
    profile = {
        "name": "Dunzo Digital Private Limited",
        "recent_news": "App operations shut down 2025; major layoffs announced in 2023."
    }
    success, score, risk, errors = validate_crisis_validity(profile)
    assert success is True, f"Factual profile failed crisis validity checks: {errors}"
    assert score == 100.0
    assert risk == 0.0
    assert not errors

def test_outdated_layoffs_fails():
    """Verifies that Amazon fails validation if the 2025 major job cuts (14,000) are missing."""
    outdated_profile = {
        "name": "Amazon.com, Inc.",
        "recent_news": "AWS partners with OpenAI in 2025; launches new AI features in 2025." # Missing cuts 14000 jobs
    }
    success, score, risk, errors = validate_crisis_validity(outdated_profile)
    assert success is False
    assert score == 0.0
    assert risk == 100.0
    assert any("2025 major workforce layoffs" in err for err in errors)

def test_outdated_controversy_fails():
    """Verifies that CBA fails validation if the CDR fine is missing."""
    outdated_profile = {
        "name": "Commonwealth Bank of Australia",
        "recent_news": "2025-12-30: Delay spam law breach announcement; 2025-08: AI job cuts backflip" # Missing CDR breach penalty 2025-12-09
    }
    success, score, risk, errors = validate_crisis_validity(outdated_profile)
    assert success is False
    assert score == 50.0
    assert risk == 50.0
    assert any("2025 Consumer Data Right penalty" in err for err in errors)

def test_outdated_disruption_fails():
    """Verifies that Dunzo fails validation if the 2025 operations shutdown details are missing."""
    outdated_profile = {
        "name": "Dunzo Digital Private Limited",
        "recent_news": "Major layoffs announced 2023; in talks for debt restructuring" # Missing app operations shut down 2025
    }
    success, score, risk, errors = validate_crisis_validity(outdated_profile)
    assert success is False
    assert score == 0.0
    assert risk == 100.0
    assert any("2025 App operations shutdown" in err for err in errors)

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "10.5.csv")
    
    master_out_csv = os.path.join(dir_path, "10.5_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "10.5_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "10.5_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "10.5_completed_validation_results.log")
    
    print("=" * 96)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (TARGET COMPANIES)")
    print("=" * 96)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 96)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED 10.5 DATASET")
    print("=" * 96)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 96)
    
    try:
        test_genuine_profiles_pass()
        print("✓ test_genuine_profiles_pass: PASSED")
        test_outdated_layoffs_fails()
        print("✓ test_outdated_layoffs_fails: PASSED")
        test_outdated_controversy_fails()
        print("✓ test_outdated_controversy_fails: PASSED")
        test_outdated_disruption_fails()
        print("✓ test_outdated_disruption_fails: PASSED")
        print("\nAll Crisis Validity verification assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical crisis validity test assertion failed:", e)
        sys.exit(1)
