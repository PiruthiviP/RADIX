import csv
import os
import re
from typing import Dict, Any, Tuple, List

# Verified factual registries for target companies
VERIFIED_REGISTRY = {
    "Accenture plc": {
        "incorporation_year": "1989",
        "employee_size": "740,000 employees",
        "annual_revenue": "$64.1B (FY2024)",
        "valuation": "$220B market capitalization ",
        "market_share_percentage": "6–7% of global IT services market",
        "vision_statement": "To drive continuous innovation and help the world’s leading organizations build their digital core and achieve greater value.",
        "core_value_proposition": "End-to-end transformation; Global delivery scale; Deep industry expertise; Strong technology partnerships; Innovation leadership"
    },
    "Google LLC (Subsidiary of Alphabet Inc.)": {
        "incorporation_year": "1998",
        "employee_size": "182000",
        "annual_revenue": "$307B (Alphabet FY2023)",
        "valuation": "$1.8T market capitalization",
        "market_share_percentage": "90% global search market",
        "vision_statement": "To provide access to the world's information in one click.",
        "core_value_proposition": "Market-leading AI and data infrastructure; Global reach and scale; Integrated digital ecosystem; High-performance cloud services"
    },
    "Apple Inc.": {
        "incorporation_year": "1976",
        "employee_size": "161000",
        "annual_revenue": "$383B (FY2023)",
        "valuation": "$3T market capitalization",
        "market_share_percentage": "20% global smartphone shipments",
        "vision_statement": "To make the best products on earth and leave the world better than we found it.",
        "core_value_proposition": "Seamless ecosystem integration; Premium design and quality; Strong privacy and security; High-performance proprietary silicon"
    },
    "Tata Consultancy Services Limited": {
        "incorporation_year": "1968",
        "employee_size": "601000",
        "annual_revenue": "$29 billion",
        "valuation": "$180 billion",
        "market_share_percentage": "12% global IT services",
        "vision_statement": "To be the most trusted partner in digital transformation for global enterprises",
        "core_value_proposition": "Scalable delivery model; Deep domain expertise; Global delivery network; Cost efficiency"
    },
    "Infosys Limited": {
        "incorporation_year": "1981",
        "employee_size": "317000",
        "annual_revenue": "$18.6 billion",
        "valuation": "$80 billion",
        "market_share_percentage": "7% global IT services",
        "vision_statement": "To navigate the next for clients using digital and cloud technologies",
        "core_value_proposition": "Agile delivery; Digital-first strategy; Strong engineering talent; Cost efficiency"
    },
    "Amazon.com, Inc.": {
        "incorporation_year": "1994",
        "employee_size": "1556000",
        "annual_revenue": "$637.9 billion ",
        "valuation": "$2 trillion+",
        "market_share_percentage": "37.8% e-commerce; 29% cloud",
        "vision_statement": "To be Earth’s most customer-centric company",
        "core_value_proposition": "One-click shopping convenience; 99.99% AWS uptime SLA; Prime fast delivery; Lowest price guarantee; Personalized recommendations"
    },
    "Microsoft Corporation": {
        "incorporation_year": "1975",
        "employee_size": "228000",
        "annual_revenue": "$281.7 billion (FY2025 full year);Trailing twelve months ~$293.8 billion (as of late 2025)",
        "valuation": "$3.6 trillion market cap (early 2026)",
        "market_share_percentage": "Cloud (Azure): 23-25%;Productivity (Office): 85-90%;Desktop OS (Windows): 70-75%",
        "vision_statement": "Empower every person and every organization on the planet to achieve more",
        "core_value_proposition": "Integrated intelligent cloud & productivity ecosystem;Trusted enterprise-grade security;Rapid AI innovation at scale;Seamless cross-device experience;Strong partner ecosystem"
    }
}

CONFIDENT_INCORRECTNESS_KEYWORDS = [
    "always", "only", "unparalleled", "guaranteed", "world-leading", "best", "unbeatable", "exclusively", "first"
]

def normalize(text: str) -> str:
    """Normalizes string to only lowercase alphanumeric characters for robust matching."""
    return "".join(c for c in text.lower() if c.isalnum())

def extract_numbers(text: str) -> List[str]:
    """Extracts all sequence of numbers from a string (including decimals like 64.1)."""
    # Clean commas and spaces, find digits
    cleaned = text.replace(',', '')
    return re.findall(r'\d+(?:\.\d+)?', cleaned)

def verify_numerical_field(input_val: str, verified_val: str) -> bool:
    """Checks if numbers in the input value match numbers in the verified registry value."""
    input_nums = extract_numbers(input_val)
    verified_nums = extract_numbers(verified_val)
    
    if not input_nums or not verified_nums:
        # Fall back to normalized exact string compare if no numbers found
        return normalize(input_val) == normalize(verified_val)
        
    # Verify that all numbers in verified are found in the input, or vice versa
    for num in verified_nums:
        if num not in input_nums:
            return False
    return True

def check_unverifiable_claims(field_val: str, verified_val: str) -> Tuple[bool, str]:
    """Checks if a mismatching text field contains bold, unverified claims."""
    if normalize(field_val) == normalize(verified_val):
        return True, ""
        
    # Find any bold, unverified keywords in input
    words = re.findall(r'\b\w+\b', field_val.lower())
    found_bold = [w for w in words if w in CONFIDENT_INCORRECTNESS_KEYWORDS]
    if found_bold:
        return False, f"Definitive claims without source or verification (contains assertive terms: {list(set(found_bold))})"
    return False, "Factual mismatch in text description."

def detect_confident_incorrectness(record_payload: Dict[str, Any]) -> Tuple[bool, float, float, List[str]]:
    """
    Validates company profile parameters to detect Confident Incorrectness (wrong numbers, bold unverified claims).
    
    Returns: (success, validity_score, risk_score, errors)
    """
    errors = []
    company_name = record_payload.get("name", "").strip()
    
    # Find matching company in our registry
    matched_company = None
    for name in VERIFIED_REGISTRY:
        if normalize(name) in normalize(company_name) or normalize(company_name) in normalize(name):
            matched_company = name
            break
            
    if not matched_company:
        return False, 0.0, 100.0, [f"Company '{company_name}' is not present in the verified registry."]

    registry = VERIFIED_REGISTRY[matched_company]
    passed_checks = 0
    total_checks = 5

    # 1. Validate Incorporation Year (Numerical Match)
    inc_year_val = record_payload.get("incorporation_year", "").strip()
    if not inc_year_val:
        errors.append("Hallucination Error [Year of Incorporation]: Field is empty.")
    elif not verify_numerical_field(inc_year_val, registry["incorporation_year"]):
        errors.append(f"Confident Incorrectness Error [Year of Incorporation]: Wrong incorporation year '{inc_year_val}' (expected '{registry['incorporation_year']}').")
    else:
        passed_checks += 1

    # 2. Validate Employee Size (Numerical Number Match)
    employee_val = record_payload.get("employee_size", "").strip()
    if not employee_val:
        errors.append("Hallucination Error [Employee Size]: Field is empty.")
    elif not verify_numerical_field(employee_val, registry["employee_size"]):
        errors.append(f"Confident Incorrectness Error [Employee Size]: Wrong employee count '{employee_val}' (expected '{registry['employee_size']}').")
    else:
        passed_checks += 1

    # 3. Validate Financial Revenue (Numerical Match)
    rev_val = record_payload.get("annual_revenue", "").strip()
    if not rev_val:
        errors.append("Hallucination Error [Annual Revenues]: Field is empty.")
    elif not verify_numerical_field(rev_val, registry["annual_revenue"]):
        errors.append(f"Confident Incorrectness Error [Annual Revenues]: Wrong revenue '{rev_val}' (expected '{registry['annual_revenue']}').")
    else:
        passed_checks += 1

    # 4. Validate Valuation (Numerical Match)
    val_val = record_payload.get("valuation", "").strip()
    if not val_val:
        errors.append("Hallucination Error [Company Valuation]: Field is empty.")
    elif not verify_numerical_field(val_val, registry["valuation"]):
        errors.append(f"Confident Incorrectness Error [Company Valuation]: Wrong valuation '{val_val}' (expected '{registry['valuation']}').")
    else:
        passed_checks += 1

    # 5. Validate Vision Statement & Core Value Proposition (Bold Unverifiable Claims check)
    vision_val = record_payload.get("vision_statement", "").strip()
    core_val = record_payload.get("core_value_proposition", "").strip()
    
    vision_ok, vision_err = check_unverifiable_claims(vision_val, registry["vision_statement"])
    core_ok, core_err = check_unverifiable_claims(core_val, registry["core_value_proposition"])
    
    if not vision_ok or not core_ok:
        if not vision_ok:
            errors.append(f"Confident Incorrectness Error [Vision]: Mismatch. {vision_err}")
        if not core_ok:
            errors.append(f"Confident Incorrectness Error [Core Value Proposition]: Mismatch. {core_err}")
    else:
        passed_checks += 1

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
    Validates all companies in the input CSV against factual registries.
    Prints real-time validation results to the terminal.
    Saves a detailed report to output_csv (viewable in Excel) and output_log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return
        
    report_rows = []
    log_lines = []
    
    log_lines.append(f"Hallucination Detection (Confident Incorrectness) Report for {os.path.basename(input_csv)}")
    log_lines.append("="*90)
    
    # Check if this CSV contains the target columns
    required_cols = ["incorporation_year", "employee_size", "annual_revenue", "valuation", "vision_statement", "core_value_proposition"]
    has_cols = any(col in dataset[0] for col in required_cols)
    if not has_cols:
        print(f"Skipped {input_csv}: Missing target validation columns.")
        return
        
    print(f"\nProcessing {len(dataset)} companies for 'Confident Incorrectness' detection...")
    print(f"{'Company Name':<45} | {'Passed':<6} | {'Failed':<6} | {'Validity':<8} | {'Risk':<6} | {'Status':<10}")
    print("-" * 96)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company")
        
        # Run checks
        success, validity_score, risk_score, errors = detect_confident_incorrectness(row)
        
        failed_count = len(errors)
        passed_count = 5 - failed_count if failed_count <= 5 else 0
        status_str = "VERIFIED" if success else "FLAGGED"
        
        # Print runtime message in terminal
        print(f"{company_name[:45]:<45} | {passed_count:<6} | {failed_count:<6} | {validity_score:<7}% | {risk_score:<5}% | {status_str:<10}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Status: {status_str}\n"
            f"  Validity Score: {validity_score}%\n"
            f"  Hallucination Risk Score: {risk_score}%\n"
        )
        if errors:
            log_line += "  Fabrication Errors:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Validation Status": status_str,
            "Validity Score (%)": validity_score,
            "Hallucination Risk Score (%)": risk_score,
            "Passed Checks": passed_count,
            "Failed Checks": failed_count,
            "Factual Errors": "; ".join(errors)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Validation Status", "Validity Score (%)", "Hallucination Risk Score (%)",
            "Passed Checks", "Failed Checks", "Factual Errors"
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
    """Verifies that authentic profiles matching factual ground truth pass validation with 0% risk."""
    apple_profile = {
        "name": "Apple Inc.",
        "incorporation_year": "1976",
        "employee_size": "161000",
        "annual_revenue": "$383B (FY2023)",
        "valuation": "$3T market capitalization",
        "market_share_percentage": "20% global smartphone shipments",
        "vision_statement": "To make the best products on earth and leave the world better than we found it.",
        "mission_statement": "To bring the best user experience to customers through innovative hardware, software, and services.",
        "core_value_proposition": "Seamless ecosystem integration; Premium design and quality; Strong privacy and security; High-performance proprietary silicon"
    }
    success, validity, risk, errors = detect_confident_incorrectness(apple_profile)
    assert success is True, f"Factual profile failed validation: {errors}"
    assert validity == 100.0
    assert risk == 0.0
    assert not errors

def test_incorrect_number_fails():
    """Verifies that specific wrong numbers presented with high certainty fail validation."""
    fabricated_profile = {
        "name": "Apple Inc.",
        "incorporation_year": "1976",
        "employee_size": "250000", # Wrong employee count, presented with high certainty
        "annual_revenue": "$383B (FY2023)",
        "valuation": "$3T market capitalization",
        "market_share_percentage": "20% global smartphone shipments",
        "vision_statement": "To make the best products on earth and leave the world better than we found it.",
        "mission_statement": "To bring the best user experience to customers through innovative hardware, software, and services.",
        "core_value_proposition": "Seamless ecosystem integration; Premium design and quality; Strong privacy and security; High-performance proprietary silicon"
    }
    success, validity, risk, errors = detect_confident_incorrectness(fabricated_profile)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("Wrong employee count" in err for err in errors)

def test_bold_unverified_claim_fails():
    """Verifies that unverified bold claims (using keywords like 'only', 'unparalleled') fail validation."""
    fabricated_profile = {
        "name": "Apple Inc.",
        "incorporation_year": "1976",
        "employee_size": "161000",
        "annual_revenue": "$383B (FY2023)",
        "valuation": "$3T market capitalization",
        "market_share_percentage": "20% global smartphone shipments",
        "vision_statement": "To make the best products on earth and leave the world better than we found it.",
        "mission_statement": "To bring the best user experience to customers through innovative hardware, software, and services.",
        "core_value_proposition": "We are exclusively and always the best, providing unparalleled performance." # Fake bold claims
    }
    success, validity, risk, errors = detect_confident_incorrectness(fabricated_profile)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("Definitive claims without source" in err for err in errors)
    assert any("unparalleled" in err for err in errors)

if __name__ == "__main__":
    import sys
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "4.3.csv")
    
    master_out_csv = os.path.join(dir_path, "4.3_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "4.3_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "4.3_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "4.3_completed_validation_results.log")
    
    print("=" * 96)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (TARGET COMPANIES)")
    print("=" * 96)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 96)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED 4.3 DATASET")
    print("=" * 96)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 96)
    
    try:
        test_genuine_profiles_pass()
        print("✓ test_genuine_profiles_pass: PASSED")
        test_incorrect_number_fails()
        print("✓ test_incorrect_number_fails: PASSED")
        test_bold_unverified_claim_fails()
        print("✓ test_bold_unverified_claim_fails: PASSED")
        print("\nAll Confident Incorrectness verification assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical factual accuracy test assertion failed:", e)
        sys.exit(1)
