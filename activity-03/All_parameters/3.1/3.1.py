import csv
import os
import re
from typing import Dict, Any, Tuple, List, Optional

# Mock Ground-Truth Registries compiled from SEC, LinkedIn, and Crunchbase
GROUND_TRUTH_REGISTRY: Dict[str, Dict[str, Any]] = {
    "accenture plc": {
        "Company Name": "Accenture plc",
        "Year of Incorporation": 1989,
        "CEO Name": "Julie Sweet",
        "Website URL": "https://www.accenture.com",
        "Employee Count": 740000,
        "Annual Revenues": 64100000000.0  # $64.1B
    },
    "google llc (subsidiary of alphabet inc.)": {
        "Company Name": "Google LLC (Subsidiary of Alphabet Inc.)",
        "Year of Incorporation": 1998,
        "CEO Name": "Sundar Pichai",
        "Website URL": "https://www.google.com",
        "Employee Count": 182000,
        "Annual Revenues": 307000000000.0  # $307B
    },
    "apple inc.": {
        "Company Name": "Apple Inc.",
        "Year of Incorporation": 1976,
        "CEO Name": "Tim Cook",
        "Website URL": "https://www.apple.com",
        "Employee Count": 161000,
        "Annual Revenues": 383000000000.0  # $383B
    },
    "tata consultancy services limited": {
        "Company Name": "Tata Consultancy Services Limited",
        "Year of Incorporation": 1968,
        "CEO Name": "K. Krithivasan",
        "Website URL": "https://www.tcs.com",
        "Employee Count": 601000,
        "Annual Revenues": 29000000000.0  # $29B
    },
    "infosys limited": {
        "Company Name": "Infosys Limited",
        "Year of Incorporation": 1981,
        "CEO Name": "Salil Parekh",
        "Website URL": "https://www.infosys.com",
        "Employee Count": 317000,
        "Annual Revenues": 18600000000.0  # $18.6B
    },
    "amazon.com, inc.": {
        "Company Name": "Amazon.com, Inc.",
        "Year of Incorporation": 1994,
        "CEO Name": "Andy Jassy",
        "Website URL": "https://www.amazon.com/",
        "Employee Count": 1556000,
        "Annual Revenues": 637900000000.0  # $637.9B
    },
    "microsoft corporation": {
        "Company Name": "Microsoft Corporation",
        "Year of Incorporation": 1975,
        "CEO Name": "Satya Nadella",
        "Website URL": "https://www.microsoft.com",
        "Employee Count": 228000,
        "Annual Revenues": 281700000000.0  # $281.7B
    }
}

# CSV columns mapping to critical target fields
CSV_COLUMNS = {
    'name': 'Company Name',
    'incorporation_year': 'Year of Incorporation',
    'ceo_name': 'CEO Name',
    'website_url': 'Website URL',
    'employee_size': 'Employee Size',
    'annual_revenue': 'Annual Revenues'
}

def parse_employee_count(val_str: str) -> Optional[int]:
    """Extracts numeric employee count from text strings (e.g. '740,000 employees' -> 740000)."""
    if not val_str:
        return None
    clean = "".join(c for c in str(val_str) if c.isdigit())
    return int(clean) if clean else None

def parse_revenue(val_str: str) -> Optional[float]:
    """Parses raw financial revenue strings to numeric float values supporting 'B' / 'billion' / 'million' multipliers."""
    if not val_str:
        return None
    val_str = val_str.lower().strip()
    # Remove commas
    val_clean = val_str.replace(',', '')
    num_match = re.search(r'[\d\.]+', val_clean)
    if not num_match:
        return None
    num = float(num_match.group(0))
    
    if 'b' in val_str or 'billion' in val_str:
        num *= 1000000000.0
    elif 'm' in val_str or 'million' in val_str:
        num *= 1000000.0
    return num

def validate_factual_correctness(ingested_record: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """
    Holistically validates the ingested company record against ground-truth registry data.
    Evaluates: Company Name, Year of Incorporation, CEO Name, Website, Employee Count, and Revenues.
    Returns: (success, accuracy_percentage, error_logs)
    """
    company_name_raw = ingested_record.get("name", "")
    company_key = str(company_name_raw).strip().lower()
    
    if not company_key or company_key not in GROUND_TRUTH_REGISTRY:
        return False, 0.0, [f"Validation skipped: Company '{company_name_raw}' not in ground-truth registry."]
        
    truth = GROUND_TRUTH_REGISTRY[company_key]
    errors = []
    checks_passed = 0
    total_checks = 6

    # 1. Company Name check
    ingested_name = ingested_record.get("name", "")
    if ingested_name == truth["Company Name"]:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [Company Name]: Ingested '{ingested_name}', expected '{truth['Company Name']}'")

    # 2. Year of Incorporation check
    try:
        ingested_year = int(ingested_record.get("incorporation_year", 0))
        if ingested_year == truth["Year of Incorporation"]:
            checks_passed += 1
        else:
            errors.append(f"Mismatch [Year of Incorporation]: Ingested {ingested_year}, expected {truth['Year of Incorporation']}")
    except ValueError:
        errors.append(f"Parser Error [Year of Incorporation]: Value '{ingested_record.get('incorporation_year')}' is not a valid year.")

    # 3. CEO Name check
    ingested_ceo = str(ingested_record.get("ceo_name", "")).strip()
    if ingested_ceo == truth["CEO Name"]:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [CEO Name]: Ingested '{ingested_ceo}', expected '{truth['CEO Name']}'")

    # 4. Website URL check (ignores trailing slashes)
    ingested_url = str(ingested_record.get("website_url", "")).strip().rstrip('/')
    truth_url = str(truth["Website URL"]).strip().rstrip('/')
    if ingested_url == truth_url:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [Website URL]: Ingested '{ingested_url}', expected '{truth_url}'")

    # 5. Employee Count check
    ingested_emp_str = ingested_record.get("employee_size", "")
    parsed_emp = parse_employee_count(ingested_emp_str)
    truth_emp = truth["Employee Count"]
    if parsed_emp is not None and parsed_emp == truth_emp:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [Employee Count]: Ingested '{ingested_emp_str}' (parsed: {parsed_emp}), expected {truth_emp}")

    # 6. Revenues check (reconcile with 5% tolerance)
    ingested_rev_str = ingested_record.get("annual_revenue", "")
    parsed_rev = parse_revenue(ingested_rev_str)
    truth_rev = truth["Annual Revenues"]
    
    if parsed_rev is not None:
        variance = abs(parsed_rev - truth_rev) / truth_rev
        if variance <= 0.05:  # 5% tolerance
            checks_passed += 1
        else:
            errors.append(f"Mismatch [Revenues]: Ingested '{ingested_rev_str}' (parsed: {parsed_rev:.1f}), expected {truth_rev:.1f} (variance: {variance*100:.2f}%)")
    else:
        errors.append(f"Parser Error [Revenues]: Could not parse ingested value '{ingested_rev_str}'")

    accuracy_score = round((checks_passed / total_checks) * 100, 2)
    success = (accuracy_score == 100.0)

    return success, accuracy_score, errors

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
    Validates all target companies in the input CSV against the ground-truth registry.
    Prints real-time validation results to the terminal.
    Saves a detailed report to output_csv (viewable in Excel) and output_log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return
        
    report_rows = []
    log_lines = []
    
    log_lines.append(f"Factual Accuracy Report for {os.path.basename(input_csv)}")
    log_lines.append("="*80)
    
    # Filter only companies in the registry
    target_records = [r for r in dataset if str(r.get("name", "")).strip().lower() in GROUND_TRUTH_REGISTRY]
    
    print(f"\nProcessing {len(target_records)} target companies against ground truth registry...")
    print(f"{'Company Name':<50} | {'Passed':<6} | {'Failed':<6} | {'Accuracy':<8} | {'Status':<8}")
    print("-" * 88)
    
    for row in target_records:
        company_name = row.get("name")
        success, accuracy_score, errors = validate_factual_correctness(row)
        
        failed_count = len(errors)
        passed_count = 6 - failed_count
        status_str = "ACCURATE" if success else "INACCURATE"
        
        # Print runtime message in terminal
        print(f"{company_name[:50]:<50} | {passed_count:<6} | {failed_count:<6} | {accuracy_score:<7}% | {status_str:<8}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Status: {status_str}\n"
            f"  Passed Parameters: {passed_count} / 6\n"
            f"  Failed/Mismatched Parameters: {failed_count} / 6\n"
            f"  Accuracy Score: {accuracy_score}%\n"
        )
        if errors:
            log_line += "  Factual Inaccuracies:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Validation Status": status_str,
            "Accuracy Score (%)": accuracy_score,
            "Passed Checks": passed_count,
            "Failed Checks": failed_count,
            "Inaccuracy Logs": "; ".join(errors)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Validation Status", "Accuracy Score (%)", "Passed Checks",
            "Failed Checks", "Inaccuracy Logs"
        ])
        writer.writeheader()
        writer.writerows(report_rows)
        
    # Write to Log
    with open(output_log, mode="w", encoding="utf-8") as f_log:
        f_log.write("\n".join(log_lines))
        
    print(f"\n✓ Report saved to CSV: {output_csv} (Excel compatible)")
    print(f"✓ Report saved to Log: {output_log}")

# --- Pytest Tests ---

def test_ground_truth_reconciliation_accuracy():
    """
    Verifies that all profiles in the generated 3.1.csv align 100% with the ground truth registry.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "3.1.csv")
    dataset = load_csv_data(csv_path)
    
    assert len(dataset) > 0
    
    for row in dataset:
        success, accuracy_score, errors = validate_factual_correctness(row)
        assert success is True, f"Factual correctness failed: {errors}"
        assert accuracy_score == 100.0

def test_mismatched_ceo_name_fails():
    """
    Verifies that a mismatched CEO name fails the 100% accuracy validation.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "3.1.csv")
    dataset = load_csv_data(csv_path)
    
    assert len(dataset) > 0
    mutated_row = dataset[0].copy()
    mutated_row["ceo_name"] = "Wrong CEO Name"
    
    success, accuracy_score, errors = validate_factual_correctness(mutated_row)
    assert success is False
    assert accuracy_score == 83.33
    assert any("Mismatch [CEO Name]" in err for err in errors)

def test_out_of_bounds_employee_count_fails():
    """
    Verifies that a mismatched employee count falls outside the assertion checks and fails.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "3.1.csv")
    dataset = load_csv_data(csv_path)
    
    assert len(dataset) > 0
    mutated_row = dataset[0].copy()
    mutated_row["employee_size"] = "100"  # incorrect headcount
    
    success, accuracy_score, errors = validate_factual_correctness(mutated_row)
    assert success is False
    assert accuracy_score == 83.33
    assert any("Mismatch [Employee Count]" in err for err in errors)

def test_revenue_estimation_variance_tolerance():
    """
    Verifies that revenue estimation variance is checked:
    - Within 5% variance passes.
    - Above 5% variance fails.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "3.1.csv")
    dataset = load_csv_data(csv_path)
    
    assert len(dataset) > 0
    mutated_row = dataset[0].copy()
    
    # 1. 2% variance check (should pass check #6)
    mutated_row["annual_revenue"] = "$390B"  # 1.8% variance on Apple's $383B (if Apple is first)
    # Let's check which company is first in the dataset
    company_name = mutated_row.get("name")
    truth = GROUND_TRUTH_REGISTRY[company_name.lower()]
    
    # Within 5%
    close_revenue = truth["Annual Revenues"] * 1.02
    mutated_row["annual_revenue"] = f"${close_revenue / 1000000000.0:.2f} billion"
    success, accuracy_score, errors = validate_factual_correctness(mutated_row)
    assert success is True, f"Failed within tolerance: {errors}"
    
    # Beyond 5%
    far_revenue = truth["Annual Revenues"] * 1.10
    mutated_row["annual_revenue"] = f"${far_revenue / 1000000000.0:.2f} billion"
    success, accuracy_score, errors = validate_factual_correctness(mutated_row)
    assert success is False
    assert accuracy_score == 83.33
    assert any("Mismatch [Revenues]" in err for err in errors)

if __name__ == "__main__":
    import sys
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "3.1.csv")
    
    master_out_csv = os.path.join(dir_path, "3.1_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "3.1_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "3.1_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "3.1_completed_validation_results.log")
    
    print("=" * 90)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (TARGET COMPANIES)")
    print("=" * 90)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 90)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED 3.1 DATASET")
    print("=" * 90)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 90)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 90)
    
    try:
        test_ground_truth_reconciliation_accuracy()
        print("✓ test_ground_truth_reconciliation_accuracy: PASSED")
        test_mismatched_ceo_name_fails()
        print("✓ test_mismatched_ceo_name_fails: PASSED")
        test_out_of_bounds_employee_count_fails()
        print("✓ test_out_of_bounds_employee_count_fails: PASSED")
        test_revenue_estimation_variance_tolerance()
        print("✓ test_revenue_estimation_variance_tolerance: PASSED")
        print("\nAll factual accuracy assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical factual accuracy test assertion failed:", e)
        sys.exit(1)
