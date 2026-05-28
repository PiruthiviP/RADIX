import csv
import os
import re
from typing import Dict, Any, Tuple, List

def extract_first_float(text: str) -> float:
    """Extracts the first numeric value from a string as a float."""
    nums = re.findall(r'\d+(?:\.\d+)?', text.replace(',', ''))
    return float(nums[0]) if nums else 0.0

def extract_max_int(text: str) -> int:
    """Extracts all integers from a string and returns the maximum one."""
    nums = [int(s) for s in re.findall(r'\d+', text.replace(',', ''))]
    return max(nums) if nums else 0

def has_active_hiring(hiring_str: str) -> bool:
    """Evaluates if the hiring velocity string indicates active hiring activity."""
    cleaned = hiring_str.lower()
    if not cleaned or cleaned == "na":
        return False
    if "engineer" in cleaned or "consulting" in cleaned or "developer" in cleaned or "open roles" in cleaned or "roles" in cleaned:
        return True
    nums = extract_max_int(hiring_str)
    return nums > 100

def extract_churn_rate(churn_str: str) -> float:
    """Extracts churn rate from string, converting words like 'low' to sensible defaults."""
    cleaned = churn_str.lower()
    if "low" in cleaned:
        return 2.0
    nums = re.findall(r'\d+(?:\.\d+)?', churn_str)
    return float(nums[0]) if nums else 0.0

def validate_internal_consistency(record_payload: Dict[str, Any]) -> Tuple[bool, float, float, List[str]]:
    """
    Validates company profile parameters to detect Internal Consistency errors.
    Checks:
    - Hiring Velocity & Turnover vs YoY Growth
    - Employee Size vs Office Count (Scale check)
    - Net Promoter Score vs Churn Rate (Satisfaction check)
    
    Returns: (success, consistency_score, risk_score, errors)
    """
    errors = []
    passed_checks = 0
    total_checks = 3

    # 1. Hiring Velocity & Turnover vs YoY Growth
    hiring_str = record_payload.get("hiring_velocity", "").strip()
    turnover_str = record_payload.get("employee_turnover", "").strip()
    growth_str = record_payload.get("yoy_growth_rate", "").strip()
    
    hiring_active = has_active_hiring(hiring_str)
    turnover_rate = extract_max_int(turnover_str)
    growth_rate = extract_first_float(growth_str)
    
    # If growth string explicitly indicates decline/negative growth (e.g. -5%)
    is_negative_growth = "-" in growth_str or (growth_rate < 0.0)
    
    if hiring_active and turnover_rate < 25 and is_negative_growth:
        errors.append(
            f"Internal Consistency Error [Growth]: High hiring velocity and low turnover ({turnover_rate}%) "
            f"are reported, but YoY growth rate is negative ({growth_str})."
        )
    else:
        passed_checks += 1

    # 2. Employee Size vs Office Count
    employee_str = record_payload.get("employee_size", "").strip()
    office_str = record_payload.get("office_count", "").strip()
    
    employees = extract_max_int(employee_str)
    offices = extract_max_int(office_str)
    
    if employees > 50000 and offices <= 2:
        errors.append(
            f"Internal Consistency Error [Scale]: Large employee size ({employees} employees) "
            f"but has only {offices} offices reported."
        )
    elif offices > 50 and employees < 500:
        errors.append(
            f"Internal Consistency Error [Scale]: Large office footprint ({offices} offices) "
            f"but only has {employees} employees reported."
        )
    else:
        passed_checks += 1

    # 3. Net Promoter Score vs Churn Rate
    nps_str = record_payload.get("net_promoter_score", "").strip()
    churn_str = record_payload.get("churn_rate", "").strip()
    
    nps = extract_max_int(nps_str)
    churn = extract_churn_rate(churn_str)
    
    # High NPS (> 40) but extremely high churn (> 20%) is a contradiction
    if nps > 40 and churn > 20.0:
        errors.append(
            f"Internal Consistency Error [Customer Satisfaction]: High NPS ({nps}) indicates "
            f"high client satisfaction, but churn rate is extremely high ({churn}%)."
        )
    else:
        passed_checks += 1

    consistency_score = round((passed_checks / total_checks) * 100, 2)
    risk_score = round(100.0 - consistency_score, 2)
    success = (passed_checks == total_checks)

    return success, consistency_score, risk_score, errors

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
    Validates all companies in the input CSV against internal consistency rules.
    Prints real-time validation results to the terminal.
    Saves a detailed report to output_csv (viewable in Excel) and output_log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return
        
    report_rows = []
    log_lines = []
    
    log_lines.append(f"Internal Consistency Report for {os.path.basename(input_csv)}")
    log_lines.append("="*90)
    
    # Check if this CSV contains the target columns
    required_cols = ["hiring_velocity", "employee_turnover", "yoy_growth_rate", "employee_size", "office_count", "net_promoter_score", "churn_rate"]
    has_cols = any(col in dataset[0] for col in required_cols)
    if not has_cols:
        print(f"Skipped {input_csv}: Missing target validation columns.")
        return
        
    print(f"\nProcessing {len(dataset)} companies for internal consistency...")
    print(f"{'Company Name':<45} | {'Passed':<6} | {'Failed':<6} | {'Consistency':<11} | {'Risk':<6} | {'Status':<10}")
    print("-" * 96)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company")
        
        # Run checks
        success, consistency_score, risk_score, errors = validate_internal_consistency(row)
        
        failed_count = len(errors)
        passed_count = 3 - failed_count if failed_count <= 3 else 0
        status_str = "CONSISTENT" if success else "INCONSISTENT"
        
        # Print runtime message in terminal
        print(f"{company_name[:45]:<45} | {passed_count:<6} | {failed_count:<6} | {consistency_score:<10}% | {risk_score:<5}% | {status_str:<10}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Status: {status_str}\n"
            f"  Consistency Score: {consistency_score}%\n"
            f"  Consistency Risk Score: {risk_score}%\n"
        )
        if errors:
            log_line += "  Consistency Contradictions:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Validation Status": status_str,
            "Consistency Score (%)": consistency_score,
            "Consistency Risk Score (%)": risk_score,
            "Passed Checks": passed_count,
            "Failed Checks": failed_count,
            "Consistency Errors": "; ".join(errors)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Validation Status", "Consistency Score (%)", "Consistency Risk Score (%)",
            "Passed Checks", "Failed Checks", "Consistency Errors"
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
    """Verifies that authentic, internally consistent profiles pass validation with 0% risk."""
    apple_profile = {
        "name": "Apple Inc.",
        "hiring_velocity": "Engineering ~2,500 roles; Retail ~1,800 roles",
        "employee_turnover": "10% annually",
        "yoy_growth_rate": "2%",
        "employee_size": "161000",
        "office_count": "100+",
        "net_promoter_score": "70",
        "churn_rate": "<10%"
    }
    success, score, risk, errors = validate_internal_consistency(apple_profile)
    assert success is True, f"Factual profile failed consistency check: {errors}"
    assert score == 100.0
    assert risk == 0.0
    assert not errors

def test_growth_inconsistency_fails():
    """Verifies that flat/shrinking growth while hiring aggressively with low turnover is caught."""
    inconsistent_profile = {
        "name": "Apple Inc.",
        "hiring_velocity": "Engineering ~2,500 roles; Retail ~1,800 roles",
        "employee_turnover": "10% annually",
        "yoy_growth_rate": "-5%", # Negative growth, inconsistent with high hiring & low turnover
        "employee_size": "161000",
        "office_count": "100+",
        "net_promoter_score": "70",
        "churn_rate": "<10%"
    }
    success, score, risk, errors = validate_internal_consistency(inconsistent_profile)
    assert success is False
    assert score == 66.67
    assert risk == 33.33
    assert any("YoY growth rate is negative" in err for err in errors)

def test_scale_inconsistency_employee_fails():
    """Verifies that a massive employee count with a single office fails scale consistency."""
    inconsistent_profile = {
        "name": "Apple Inc.",
        "hiring_velocity": "Engineering ~2,500 roles; Retail ~1,800 roles",
        "employee_turnover": "10% annually",
        "yoy_growth_rate": "2%",
        "employee_size": "500000", # Massive employee size
        "office_count": "1", # But only 1 office
        "net_promoter_score": "70",
        "churn_rate": "<10%"
    }
    success, score, risk, errors = validate_internal_consistency(inconsistent_profile)
    assert success is False
    assert score == 66.67
    assert risk == 33.33
    assert any("Large employee size" in err for err in errors)

def test_scale_inconsistency_office_fails():
    """Verifies that a massive office footprint with a tiny employee size fails scale consistency."""
    inconsistent_profile = {
        "name": "Apple Inc.",
        "hiring_velocity": "Engineering ~2,500 roles; Retail ~1,800 roles",
        "employee_turnover": "10% annually",
        "yoy_growth_rate": "2%",
        "employee_size": "50", # Tiny employee count
        "office_count": "100+", # But 100 offices
        "net_promoter_score": "70",
        "churn_rate": "<10%"
    }
    success, score, risk, errors = validate_internal_consistency(inconsistent_profile)
    assert success is False
    assert score == 66.67
    assert risk == 33.33
    assert any("Large office footprint" in err for err in errors)

def test_satisfaction_inconsistency_fails():
    """Verifies that high customer NPS with extremely high churn is caught as an inconsistency."""
    inconsistent_profile = {
        "name": "Apple Inc.",
        "hiring_velocity": "Engineering ~2,500 roles; Retail ~1,800 roles",
        "employee_turnover": "10% annually",
        "yoy_growth_rate": "2%",
        "employee_size": "161000",
        "office_count": "100+",
        "net_promoter_score": "80", # High customer NPS
        "churn_rate": "35%" # But extremely high churn
    }
    success, score, risk, errors = validate_internal_consistency(inconsistent_profile)
    assert success is False
    assert score == 66.67
    assert risk == 33.33
    assert any("churn rate is extremely high" in err for err in errors)

if __name__ == "__main__":
    import sys
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "5.5.csv")
    
    master_out_csv = os.path.join(dir_path, "5.5_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "5.5_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "5.5_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "5.5_completed_validation_results.log")
    
    print("=" * 96)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (TARGET COMPANIES)")
    print("=" * 96)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 96)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED 5.5 DATASET")
    print("=" * 96)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 96)
    
    try:
        test_genuine_profiles_pass()
        print("✓ test_genuine_profiles_pass: PASSED")
        test_growth_inconsistency_fails()
        print("✓ test_growth_inconsistency_fails: PASSED")
        test_scale_inconsistency_employee_fails()
        print("✓ test_scale_inconsistency_employee_fails: PASSED")
        test_scale_inconsistency_office_fails()
        print("✓ test_scale_inconsistency_office_fails: PASSED")
        test_satisfaction_inconsistency_fails()
        print("✓ test_satisfaction_inconsistency_fails: PASSED")
        print("\nAll Internal Consistency verification assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical factual accuracy test assertion failed:", e)
        sys.exit(1)
