import csv
import os
import sys
from typing import Dict, Any, Tuple, List

# Factual ground truth registries for post-cutoff (2025/2026) events
TEMPORAL_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    "Capgemini": [
        {
            "description": "2025 executive changes (new Americas CEO)",
            "keywords": ["americas ceo", "feb 2025"]
        }
    ],
    "Llama Logisol Private Limited": [
        {
            "description": "2025 executive changes (new CTO/CRO)",
            "keywords": ["new cto/cro", "apr 2025"]
        },
        {
            "description": "2025 Sydney HQ expansion",
            "keywords": ["sydney", "jun 2025"]
        }
    ],
    "Leap Finance Private Limited": [
        {
            "description": "2025 Series E funding round ($65M)",
            "keywords": ["series e", "apis partners", "2025-01-29"]
        },
        {
            "description": "2025 HSBC debt funding ($100M)",
            "keywords": ["hsbc", "debt", "2025-03-05"]
        }
    ],
    "Microsoft Corporation": [
        {
            "description": "2025 Copilot+ PC expansion",
            "keywords": ["copilot+ pc", "2025-07"]
        },
        {
            "description": "2025 Azure OpenAI reasoning models",
            "keywords": ["azure openai", "reasoning models", "2025-06"]
        }
    ],
    "Amazon.com, Inc.": [
        {
            "description": "2025 AWS OpenAI partnership",
            "keywords": ["aws partners with openai", "2025-11-19"]
        },
        {
            "description": "2025 AI features launch",
            "keywords": ["new ai features", "2025-09-12"]
        }
    ],
    "Swiggy Limited": [
        {
            "description": "2025 Instamart 100 cities expansion",
            "keywords": ["instamart to 100 cities", "2025"]
        },
        {
            "description": "2025 QIP capital raise (Rs 10,000 Cr)",
            "keywords": ["qip", "dec 2025"]
        }
    ]
}

def validate_temporal_validity(record: Dict[str, Any]) -> Tuple[bool, float, float, List[str]]:
    """
    Validates if a company profile contains recent 2025/2026 events.
    Checks for latest CEO changes, funding rounds, and product launches.
    
    Returns: (success, validity_score, risk_score, errors)
    """
    errors = []
    company_name = record.get("name", "").strip()
    
    # Check if the company is registered for temporal cutoff tests
    matched_key = None
    for key in TEMPORAL_REGISTRY:
        if company_name.lower() == key.lower():
            matched_key = key
            break
            
    if not matched_key:
        # If no checks are defined for this company, it is compliant by default
        return True, 100.0, 0.0, []
        
    checks = TEMPORAL_REGISTRY[matched_key]
    passed_checks = 0
    total_checks = len(checks)
    
    news_text = record.get("recent_news", "").lower()
    
    for check in checks:
        desc = check["description"]
        keywords = check["keywords"]
        
        # Verify that all keywords are present in recent_news (case-insensitive)
        missing_kw = [kw for kw in keywords if kw.lower() not in news_text]
        
        if not missing_kw:
            passed_checks += 1
        else:
            errors.append(
                f"Temporal Validity Error [{desc}]: Profile lacks news about this event. "
                f"Missing keywords: {missing_kw}."
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
    Validates all companies in the input CSV against post-cutoff events.
    Prints real-time validation results to the terminal.
    Saves a detailed report to output_csv (viewable in Excel) and output_log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return
        
    report_rows = []
    log_lines = []
    
    log_lines.append(f"Temporal Validity (Knowledge Cutoff) Report for {os.path.basename(input_csv)}")
    log_lines.append("="*96)
    
    print(f"\nProcessing {len(dataset)} companies from {os.path.basename(input_csv)} for temporal validity...")
    print(f"{'Company Name':<45} | {'Passed':<6} | {'Failed':<6} | {'Validity':<8} | {'Risk':<6} | {'Status':<10}")
    print("-" * 96)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company")
        
        success, validity_score, risk_score, errors = validate_temporal_validity(row)
        
        failed_count = len(errors)
        matched_key = next((k for k in TEMPORAL_REGISTRY if k.lower() == company_name.lower()), None)
        total_checks = len(TEMPORAL_REGISTRY[matched_key]) if matched_key else 0
        passed_count = total_checks - failed_count
        status_str = "CURRENT" if success else "OUTDATED"
        
        # Print runtime message in terminal
        print(f"{company_name[:45]:<45} | {passed_count:<6} | {failed_count:<6} | {validity_score:<7}% | {risk_score:<5}% | {status_str:<10}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Status: {status_str}\n"
            f"  Temporal Validity Score: {validity_score}%\n"
            f"  Temporal Stagnation Risk Score: {risk_score}%\n"
        )
        if errors:
            log_line += "  Missing Cutoff Events:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Validation Status": status_str,
            "Temporal Validity Score (%)": validity_score,
            "Temporal Stagnation Risk Score (%)": risk_score,
            "Passed Checks": passed_count,
            "Failed Checks": failed_count,
            "Temporal Errors": "; ".join(errors)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Validation Status", "Temporal Validity Score (%)", "Temporal Stagnation Risk Score (%)",
            "Passed Checks", "Failed Checks", "Temporal Errors"
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
    """Verifies that authentic profiles containing correct 2025 events pass validation with 100% validity."""
    profile = {
        "name": "Capgemini",
        "recent_news": "Revenues €5.4B in Q3 2025; Executive changes including new Americas CEO (Feb 2025)"
    }
    success, score, risk, errors = validate_temporal_validity(profile)
    assert success is True, f"Factual profile failed temporal validity checks: {errors}"
    assert score == 100.0
    assert risk == 0.0
    assert not errors

def test_outdated_ceo_change_fails():
    """Verifies that Capgemini fails validation if the 2025 CEO change is missing."""
    outdated_profile = {
        "name": "Capgemini",
        "recent_news": "Revenues €5.4B in Q3 2024; Executive changes in 2024" # Missing Feb 2025 new Americas CEO
    }
    success, score, risk, errors = validate_temporal_validity(outdated_profile)
    assert success is False
    assert score == 0.0
    assert risk == 100.0
    assert any("2025 executive changes (new Americas CEO)" in err for err in errors)

def test_outdated_funding_round_fails():
    """Verifies that Leap Finance fails validation if the Series E or HSBC debt round is missing."""
    outdated_profile = {
        "name": "Leap Finance Private Limited",
        "recent_news": "Raised $100M in talks in 2024; Raised Series D in 2022" # Missing Series E / HSBC debt in 2025
    }
    success, score, risk, errors = validate_temporal_validity(outdated_profile)
    assert success is False
    assert score == 0.0
    assert risk == 100.0
    assert any("2025 Series E" in err for err in errors)
    assert any("2025 HSBC debt" in err for err in errors)

def test_outdated_product_launch_fails():
    """Verifies that Microsoft fails validation if the 2025 Azure OpenAI reasoning models event is missing."""
    outdated_profile = {
        "name": "Microsoft Corporation",
        "recent_news": "2025-07: Expanded Copilot+ PC lineup; 2024: Copilot launch" # Missing Azure OpenAI reasoning models in 2025-06
    }
    success, score, risk, errors = validate_temporal_validity(outdated_profile)
    assert success is False
    assert score == 50.0
    assert risk == 50.0
    assert any("2025 Azure OpenAI reasoning models" in err for err in errors)

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "10.1.csv")
    
    master_out_csv = os.path.join(dir_path, "10.1_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "10.1_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "10.1_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "10.1_completed_validation_results.log")
    
    print("=" * 96)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (TARGET COMPANIES)")
    print("=" * 96)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 96)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED 10.1 DATASET")
    print("=" * 96)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 96)
    
    try:
        test_genuine_profiles_pass()
        print("✓ test_genuine_profiles_pass: PASSED")
        test_outdated_ceo_change_fails()
        print("✓ test_outdated_ceo_change_fails: PASSED")
        test_outdated_funding_round_fails()
        print("✓ test_outdated_funding_round_fails: PASSED")
        test_outdated_product_launch_fails()
        print("✓ test_outdated_product_launch_fails: PASSED")
        print("\nAll Temporal Validity verification assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical temporal validity test assertion failed:", e)
        sys.exit(1)
