import csv
import os
import sys
from typing import Dict, Any, Tuple, List

# Verified registry of post-cutoff structural changes (M&A, restructuring, subsidiaries)
STRUCTURAL_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    "Accenture plc": [
        {
            "description": "2024 acquisitions in Europe",
            "field": "recent_news",
            "keywords": ["acquired multiple cloud and ai", "europe"]
        }
    ],
    "Amazon.com, Inc.": [
        {
            "description": "2025 healthcare startup acquisition",
            "field": "recent_news",
            "keywords": ["acquires healthcare startup", "2025-06-25"]
        }
    ],
    "International Business Machines Corporation ": [
        {
            "description": "Confluent acquisition announcement",
            "field": "history_timeline",
            "keywords": ["acquisition of confluent"]
        },
        {
            "description": "2025 software focus and job cuts",
            "field": "history_timeline",
            "keywords": ["job cuts in 2025", "software"]
        }
    ],
    "Barclays PLC ": [
        {
            "description": "2024 corporate restructuring",
            "field": "recent_news",
            "keywords": ["restructuring in early 2024"]
        }
    ],
    "Blink Commerce Private Limited ": [
        {
            "description": "Zomato acquisition",
            "field": "recent_news",
            "keywords": ["acquired by zomato"]
        },
        {
            "description": "Subsidiary nature of company",
            "field": "nature_of_company",
            "keywords": ["subsidiary"]
        }
    ],
    "ServiceNow, Inc.": [
        {
            "description": "G2K acquisition",
            "field": "recent_news",
            "keywords": ["acquisition of ai startup g2k"]
        }
    ],
    "Morgan Stanley": [
        {
            "description": "2025 fintech platform stake acquisition",
            "field": "recent_news",
            "keywords": ["acquired minority stake in fintech", "nov 2025"]
        }
    ],
    "Byju’s": [
        {
            "description": "2025 debt restructuring",
            "field": "recent_news",
            "keywords": ["debt restructuring", "2025"]
        }
    ],
    "DXC Technology Company": [
        {
            "description": "2024 margin restructuring",
            "field": "recent_news",
            "keywords": ["restructuring", "2024"]
        }
    ],
    "Google LLC (Subsidiary of Alphabet Inc.)": [
        {
            "description": "Subsidiary nature of company",
            "field": "nature_of_company",
            "keywords": ["subsidiary"]
        }
    ]
}

def validate_structural_validity(record: Dict[str, Any]) -> Tuple[bool, float, float, List[str]]:
    """
    Validates if a company profile correctly represents post-cutoff structural changes (M&A, restructuring, subsidiaries).
    
    Returns: (success, validity_score, risk_score, errors)
    """
    errors = []
    company_name = record.get("name", "").strip()
    
    # Check if the company is registered for structural cutoff tests
    matched_key = None
    for key in STRUCTURAL_REGISTRY:
        if company_name.lower().strip() == key.lower().strip():
            matched_key = key
            break
            
    if not matched_key:
        # If no checks are defined for this company, it is compliant by default
        return True, 100.0, 0.0, []
        
    checks = STRUCTURAL_REGISTRY[matched_key]
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
                f"Structural Validity Error [{desc} in field '{field_name}']: "
                f"Outdated profile structural details. Missing keywords: {missing_kw}."
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
    Validates all companies in the input CSV against post-cutoff structural changes.
    Prints real-time validation results to the terminal.
    Saves a detailed report to output_csv (viewable in Excel) and output_log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return
        
    report_rows = []
    log_lines = []
    
    log_lines.append(f"Structural Validity (M&A/Restructuring Cutoff) Report for {os.path.basename(input_csv)}")
    log_lines.append("="*96)
    
    print(f"\nProcessing {len(dataset)} companies from {os.path.basename(input_csv)} for structural validity...")
    print(f"{'Company Name':<45} | {'Passed':<6} | {'Failed':<6} | {'Validity':<8} | {'Risk':<6} | {'Status':<10}")
    print("-" * 96)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company").strip()
        
        success, validity_score, risk_score, errors = validate_structural_validity(row)
        
        failed_count = len(errors)
        matched_key = next((k for k in STRUCTURAL_REGISTRY if k.lower().strip() == company_name.lower().strip()), None)
        total_checks = len(STRUCTURAL_REGISTRY[matched_key]) if matched_key else 0
        passed_count = total_checks - failed_count
        status_str = "CURRENT" if success else "OUTDATED"
        
        # Print runtime message in terminal
        print(f"{company_name[:45]:<45} | {passed_count:<6} | {failed_count:<6} | {validity_score:<7}% | {risk_score:<5}% | {status_str:<10}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Status: {status_str}\n"
            f"  Structural Validity Score: {validity_score}%\n"
            f"  Structural Stagnation Risk Score: {risk_score}%\n"
        )
        if errors:
            log_line += "  Missing Cutoff Structural Events:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Validation Status": status_str,
            "Structural Validity Score (%)": validity_score,
            "Structural Stagnation Risk Score (%)": risk_score,
            "Passed Checks": passed_count,
            "Failed Checks": failed_count,
            "Structural Errors": "; ".join(errors)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Validation Status", "Structural Validity Score (%)", "Structural Stagnation Risk Score (%)",
            "Passed Checks", "Failed Checks", "Structural Errors"
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
    """Verifies that authentic profiles containing correct post-cutoff structural changes pass validation with 100% validity."""
    profile = {
        "name": "Barclays PLC ",
        "recent_news": "Announced a major restructuring in early 2024 to boost shareholder returns and focus on UK retail."
    }
    success, score, risk, errors = validate_structural_validity(profile)
    assert success is True, f"Factual profile failed structural validity checks: {errors}"
    assert score == 100.0
    assert risk == 0.0
    assert not errors

def test_outdated_acquisition_fails():
    """Verifies that IBM fails validation if the Confluent acquisition is missing."""
    outdated_profile = {
        "name": "International Business Machines Corporation ",
        "history_timeline": "IBM generated $62.8B revenue in 2024; workforce expected to see job cuts in 2025 as focus shifts to software.", # Missing Confluent acquisition
        "recent_news": ""
    }
    success, score, risk, errors = validate_structural_validity(outdated_profile)
    assert success is False
    assert score == 50.0
    assert risk == 50.0
    assert any("Confluent acquisition announcement" in err for err in errors)

def test_outdated_restructuring_fails():
    """Verifies that Barclays fails validation if the early 2024 restructuring details are missing."""
    outdated_profile = {
        "name": "Barclays PLC ",
        "recent_news": "Reported quarterly revenues in late 2024" # Missing early 2024 major restructuring news
    }
    success, score, risk, errors = validate_structural_validity(outdated_profile)
    assert success is False
    assert score == 0.0
    assert risk == 100.0
    assert any("2024 corporate restructuring" in err for err in errors)

def test_outdated_subsidiary_relationship_fails():
    """Verifies that Blinkit fails validation if the Zomato acquisition is missing or misrepresented."""
    outdated_profile = {
        "name": "Blink Commerce Private Limited ",
        "recent_news": "Plans to launch 1,000 dark stores by March 2025.", # Missing "acquired by Zomato"
        "nature_of_company": "Subsidiary"
    }
    success, score, risk, errors = validate_structural_validity(outdated_profile)
    assert success is False
    assert score == 50.0
    assert risk == 50.0
    assert any("Zomato acquisition" in err for err in errors)

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "10.2.csv")
    
    master_out_csv = os.path.join(dir_path, "10.2_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "10.2_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "10.2_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "10.2_completed_validation_results.log")
    
    print("=" * 96)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (TARGET COMPANIES)")
    print("=" * 96)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 96)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED 10.2 DATASET")
    print("=" * 96)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 96)
    
    try:
        test_genuine_profiles_pass()
        print("✓ test_genuine_profiles_pass: PASSED")
        test_outdated_acquisition_fails()
        print("✓ test_outdated_acquisition_fails: PASSED")
        test_outdated_restructuring_fails()
        print("✓ test_outdated_restructuring_fails: PASSED")
        test_outdated_subsidiary_relationship_fails()
        print("✓ test_outdated_subsidiary_relationship_fails: PASSED")
        print("\nAll Structural Validity verification assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical structural validity test assertion failed:", e)
        sys.exit(1)
