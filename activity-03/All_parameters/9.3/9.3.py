import csv
import os
import sys
from typing import Dict, Any, Tuple, List, Optional

# Verified ground truth registry for target and adversarial companies
VERIFIED_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Accenture plc": {
        "ceo_name": "Julie Sweet",
        "incorporation_year": "1989",
        "website_url": "https://www.accenture.com",
        "headquarters_address": "Dublin, Ireland"
    },
    "Google LLC (Subsidiary of Alphabet Inc.)": {
        "ceo_name": "Sundar Pichai",
        "incorporation_year": "1998",
        "website_url": "https://www.google.com",
        "headquarters_address": "1600 Amphitheatre Parkway, Mountain View, California, USA"
    },
    "Apple Inc.": {
        "ceo_name": "Tim Cook",
        "incorporation_year": "1976",
        "website_url": "https://www.apple.com",
        "headquarters_address": "One Apple Park Way, Cupertino, California, USA"
    },
    "Tata Consultancy Services Limited": {
        "ceo_name": "K. Krithivasan",
        "incorporation_year": "1968",
        "website_url": "https://www.tcs.com",
        "headquarters_address": "Mumbai, Maharashtra, India"
    },
    "Infosys Limited": {
        "ceo_name": "Salil Parekh",
        "incorporation_year": "1981",
        "website_url": "https://www.infosys.com",
        "headquarters_address": "Bangalore, Karnataka, India"
    },
    "Amazon.com, Inc.": {
        "ceo_name": "Andy Jassy",
        "incorporation_year": "1994",
        "website_url": "https://www.amazon.com/",
        "headquarters_address": "410 Terry Ave N, Seattle, WA 98109, United States"
    },
    "Microsoft Corporation": {
        "ceo_name": "Satya Nadella",
        "incorporation_year": "1975",
        "website_url": "https://www.microsoft.com",
        "headquarters_address": "One Microsoft Way, Redmond, Washington 98052, United States"
    },
    "Delta Air Lines, Inc.": {
        "ceo_name": "Ed Bastian",
        "incorporation_year": "1924",
        "website_url": "https://www.delta.com",
        "headquarters_address": "Atlanta, Georgia, USA"
    },
    "Delta Controls Ltd.": {
        "ceo_name": "Delta Controls Executive",
        "incorporation_year": "1980",
        "website_url": "https://www.deltacontrols.com",
        "headquarters_address": "Surrey, BC, Canada"
    },
    "Delta Dental Agency": {
        "ceo_name": "Delta Dental Director",
        "incorporation_year": "1954",
        "website_url": "https://www.deltadental.com",
        "headquarters_address": "Oak Brook, Illinois, USA"
    },
    "Delta Energy Corp": {
        "ceo_name": "Delta Energy Chief",
        "incorporation_year": "2005",
        "website_url": "https://www.deltaenergy.com",
        "headquarters_address": "Houston, Texas, USA"
    },
    "Apple Bank": {
        "ceo_name": "Gerard LaRocca",
        "incorporation_year": "1863",
        "website_url": "https://www.applebank.com",
        "headquarters_address": "New York City, NY, USA"
    },
    "Microsoft Ireland Operations": {
        "ceo_name": "Microsoft Ireland Director",
        "incorporation_year": "1997",
        "website_url": "https://www.microsoft.com/en-ie",
        "headquarters_address": "Dublin, Ireland"
    },
    "Microsoft India Private Limited": {
        "ceo_name": "Anant Maheshwari",
        "incorporation_year": "1990",
        "website_url": "https://www.microsoft.com/en-in",
        "headquarters_address": "Hyderabad, India"
    }
}

def robust_match(company_name: str) -> Optional[str]:
    """Matches strictly on canonical name ignoring whitespace and case."""
    clean_name = company_name.strip().lower()
    for reg_name in VERIFIED_REGISTRY:
        if clean_name == reg_name.lower():
            return reg_name
    return None

def buggy_match(company_name: str) -> Optional[str]:
    """
    Simulates a buggy matching engine with context confusion.
    Matches naive prefixes (first word), leading to state leakage for similar-named companies.
    """
    clean_name = company_name.strip().lower()
    first_word = clean_name.split()[0] if clean_name.split() else clean_name
    
    # Remove punctuation or commas from the first word
    first_word = first_word.replace(",", "").replace(".", "")
    
    for reg_name in VERIFIED_REGISTRY:
        reg_clean = reg_name.lower()
        reg_first_word = reg_clean.split()[0] if reg_clean.split() else reg_clean
        reg_first_word = reg_first_word.replace(",", "").replace(".", "")
        if first_word == reg_first_word:
            return reg_name
    return None

def validate_factual_correctness(
    record: Dict[str, Any], 
    matcher_func
) -> Tuple[bool, float, List[str], Optional[str]]:
    """
    Validates a company record against the matched verified registry.
    Detects context confusion if matched to the wrong company.
    
    Returns: (success, accuracy_score, errors, matched_company_name)
    """
    errors = []
    ingested_name = record.get("name", "").strip()
    
    matched_name = matcher_func(ingested_name)
    if not matched_name:
        return False, 0.0, [f"Validation Error: Company '{ingested_name}' not found in registry."], None
        
    # Check context confusion (matched name differs from ingested name)
    if matched_name.lower() != ingested_name.lower():
        errors.append(
            f"Context Confusion Error: Ingested record '{ingested_name}' was incorrectly matched "
            f"to registry company '{matched_name}'."
        )
        
    truth = VERIFIED_REGISTRY[matched_name]
    checks_passed = 0
    total_checks = 4
    
    # 1. CEO Name check
    ingested_ceo = record.get("ceo_name", "").strip()
    truth_ceo = truth["ceo_name"]
    # Handle optional cleanups
    if ingested_ceo.replace(".", "").lower() == truth_ceo.replace(".", "").lower():
        checks_passed += 1
    else:
        errors.append(f"Mismatch [CEO Name]: Ingested '{ingested_ceo}', expected '{truth_ceo}'")
        
    # 2. Year of Incorporation check
    ingested_year = record.get("incorporation_year", "").strip()
    truth_year = truth["incorporation_year"]
    if ingested_year == truth_year:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [Year of Incorporation]: Ingested '{ingested_year}', expected '{truth_year}'")
        
    # 3. Website URL check (ignores trailing slash)
    ingested_url = record.get("website_url", "").strip().rstrip('/')
    truth_url = truth["website_url"].strip().rstrip('/')
    if ingested_url == truth_url:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [Website URL]: Ingested '{ingested_url}', expected '{truth_url}'")
        
    # 4. Headquarters Address check
    ingested_hq = record.get("headquarters_address", "").strip()
    truth_hq = truth["headquarters_address"].strip()
    if ingested_hq == truth_hq:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [Headquarters Address]: Ingested '{ingested_hq}', expected '{truth_hq}'")
        
    # If context confusion occurred, we penalize the success flag
    success = (len(errors) == 0 and checks_passed == total_checks)
    accuracy_score = round((checks_passed / total_checks) * 100, 2)
    
    return success, accuracy_score, errors, matched_name

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

def generate_validation_report(
    input_csv: str, 
    output_csv: str, 
    output_log: str, 
    matcher_func,
    engine_name: str
) -> bool:
    """
    Validates all records in the input CSV.
    Prints real-time validation results to the terminal.
    Saves a detailed report to output_csv (viewable in Excel) and output_log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return False
        
    report_rows = []
    log_lines = []
    all_passed = True
    
    log_lines.append(f"Context Confusion Validation Report ({engine_name}) for {os.path.basename(input_csv)}")
    log_lines.append("="*96)
    
    print(f"\nProcessing {len(dataset)} companies using {engine_name}...")
    print(f"{'Company Name':<40} | {'Matched Registry':<30} | {'Score':<6} | {'Status':<10}")
    print("-" * 96)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company")
        
        success, accuracy_score, errors, matched_name = validate_factual_correctness(row, matcher_func)
        status_str = "PASSED" if success else "CONFUSED/FAILED"
        if not success:
            all_passed = False
            
        print(f"{company_name[:40]:<40} | {str(matched_name)[:30]:<30} | {accuracy_score:<5}% | {status_str:<10}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Matched Registry: {matched_name}\n"
            f"  Status: {status_str}\n"
            f"  Accuracy Score: {accuracy_score}%\n"
        )
        if errors:
            log_line += "  Validation Issues:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Matched Registry": matched_name,
            "Validation Status": status_str,
            "Accuracy Score (%)": accuracy_score,
            "Issues": "; ".join(errors)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Matched Registry", "Validation Status", "Accuracy Score (%)", "Issues"
        ])
        writer.writeheader()
        writer.writerows(report_rows)
        
    # Write to Log
    with open(output_log, mode="w", encoding="utf-8") as f_log:
        f_log.write("\n".join(log_lines))
        
    print(f"\n✓ Report saved to CSV: {output_csv} (Excel compatible)")
    print(f"✓ Report saved to Log: {output_log}")
    return all_passed


# --- Automated System Test Suite ---

def test_robust_engine_passes():
    """Verifies that the robust engine parses all similar-named companies without context leakage."""
    csv_path = os.path.join(os.path.dirname(__file__), "9.3.csv")
    dataset = load_csv_data(csv_path)
    assert len(dataset) > 0
    
    for row in dataset:
        success, score, errors, matched_name = validate_factual_correctness(row, robust_match)
        assert success is True, f"Robust validation failed on {row.get('name')}: {errors}"
        assert score == 100.0
        assert not errors

def test_buggy_engine_detects_confusion_apple():
    """Verifies that the buggy matching engine fails when 'Apple Bank' is matched to 'Apple Inc.'."""
    apple_bank_row = {
        "name": "Apple Bank",
        "ceo_name": "Gerard LaRocca",
        "incorporation_year": "1863",
        "website_url": "https://www.applebank.com",
        "headquarters_address": "New York City, NY, USA"
    }
    success, score, errors, matched_name = validate_factual_correctness(apple_bank_row, buggy_match)
    assert success is False
    assert matched_name == "Apple Inc."
    assert any("Context Confusion Error" in err for err in errors)
    assert any("Mismatch [CEO Name]" in err for err in errors)  # Apple Inc. has CEO Tim Cook

def test_buggy_engine_detects_confusion_delta():
    """Verifies that the buggy matching engine fails when different Delta companies collide."""
    delta_controls_row = {
        "name": "Delta Controls Ltd.",
        "ceo_name": "Delta Controls Executive",
        "incorporation_year": "1980",
        "website_url": "https://www.deltacontrols.com",
        "headquarters_address": "Surrey, BC, Canada"
    }
    success, score, errors, matched_name = validate_factual_correctness(delta_controls_row, buggy_match)
    assert success is False
    assert matched_name == "Delta Air Lines, Inc."
    assert any("Context Confusion Error" in err for err in errors)
    assert any("Mismatch [CEO Name]" in err for err in errors)  # Delta Air Lines has CEO Ed Bastian

def test_buggy_engine_detects_confusion_microsoft():
    """Verifies that the buggy matching engine fails when Microsoft variations collide."""
    ms_ireland_row = {
        "name": "Microsoft Ireland Operations",
        "ceo_name": "Microsoft Ireland Director",
        "incorporation_year": "1997",
        "website_url": "https://www.microsoft.com/en-ie",
        "headquarters_address": "Dublin, Ireland"
    }
    success, score, errors, matched_name = validate_factual_correctness(ms_ireland_row, buggy_match)
    assert success is False
    assert matched_name == "Microsoft Corporation"
    assert any("Context Confusion Error" in err for err in errors)
    assert any("Mismatch [CEO Name]" in err for err in errors)  # Microsoft Corp has CEO Satya Nadella

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "9.3.csv")
    
    robust_out_csv = os.path.join(dir_path, "9.3_completed_validation_results.csv")
    robust_out_log = os.path.join(dir_path, "9.3_completed_validation_results.log")
    
    buggy_out_csv = os.path.join(dir_path, "9.3_buggy_validation_results.csv")
    buggy_out_log = os.path.join(dir_path, "9.3_buggy_validation_results.log")
    
    print("=" * 96)
    print("1. RUNNING ROBUST (CONTEXT-ISOLATED) INGEL VALIDATION")
    print("=" * 96)
    robust_ok = generate_validation_report(
        completed_csv_path, robust_out_csv, robust_out_log, robust_match, "Robust Context-Isolated Engine"
    )
    
    print("\n" + "=" * 96)
    print("2. RUNNING BUGGY (FUZZY/PREFIX-MATCHING) INGEL VALIDATION")
    print("=" * 96)
    buggy_ok = generate_validation_report(
        completed_csv_path, buggy_out_csv, buggy_out_log, buggy_match, "Buggy First-Word Matching Engine"
    )
    
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM ADVERSARIAL TEST SUITE")
    print("=" * 96)
    
    try:
        test_robust_engine_passes()
        print("✓ test_robust_engine_passes: PASSED")
        test_buggy_engine_detects_confusion_apple()
        print("✓ test_buggy_engine_detects_confusion_apple: PASSED")
        test_buggy_engine_detects_confusion_delta()
        print("✓ test_buggy_engine_detects_confusion_delta: PASSED")
        test_buggy_engine_detects_confusion_microsoft()
        print("✓ test_buggy_engine_detects_confusion_microsoft: PASSED")
        print("\nAll Context Confusion adversarial assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical context confusion test assertion failed:", e)
        sys.exit(1)
