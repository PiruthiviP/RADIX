import csv
import os
import re
from typing import Dict, Any, Tuple, List

# Verified factual registries for target companies
VERIFIED_REGISTRY = {
    "Accenture plc": {
        "ceo_name": ["Julie Sweet"],
        "key_leaders": [
            "Julie Sweet", "Manish Sharma", "Jack Azagury"
        ],
        "board_members": [
            "Julie Sweet", "David Rowland", "Former global executives"
        ],
        "awards_recognitions": [
            "Fortune Global 500", "Great Place to Work Certified",
            "Gartner Magic Quadrant Leader", "Forbes Most Admired Companies"
        ],
        "recent_funding_rounds": [
            "Public equity markets", "ongoing institutional investment"
        ]
    },
    "Google LLC (Subsidiary of Alphabet Inc.)": {
        "ceo_name": ["Sundar Pichai"],
        "key_leaders": [
            "Sundar Pichai", "Thomas Kurian", "Ruth Porat"
        ],
        "board_members": [
            "Sundar Pichai", "John L. Hennessy", "Roger W. Ferguson Jr.", "Frances Arnold"
        ],
        "awards_recognitions": [
            "Fortune Most Admired Companies", "Best Global Brand Interbrand", "Great Place to Work"
        ],
        "recent_funding_rounds": [
            "IPO 2004", "Ongoing public market funding"
        ]
    },
    "Apple Inc.": {
        "ceo_name": ["Tim Cook"],
        "key_leaders": [
            "Tim Cook", "Luca Maestri", "John Ternus"
        ],
        "board_members": [
            "Tim Cook", "Arthur D. Levinson", "Al Gore", "Monica Lozano"
        ],
        "awards_recognitions": [
            "Fortune Most Admired Companies", "Interbrand Best Global Brand", "TIME Most Influential Companies"
        ],
        "recent_funding_rounds": [
            "IPO 1980", "Ongoing public equity markets"
        ]
    },
    "Tata Consultancy Services Limited": {
        "ceo_name": ["K. Krithivasan", "K Krithivasan"],
        "key_leaders": [
            "K. Krithivasan", "K Krithivasan", "Samir Seksaria", "Harrick Vin"
        ],
        "board_members": [
            "Tata Group nominees", "Independent directors"
        ],
        "awards_recognitions": [
            "Forbes Global 2000", "Brand Finance IT Services Leader"
        ],
        "recent_funding_rounds": [
            "NA"
        ]
    },
    "Infosys Limited": {
        "ceo_name": ["Salil Parekh"],
        "key_leaders": [
            "Salil Parekh", "Nilanjan Roy", "Inderpreet Sawhney"
        ],
        "board_members": [
            "Independent directors", "Founders"
        ],
        "awards_recognitions": [
            "Forbes Global 2000", "Top Employer India"
        ],
        "recent_funding_rounds": [
            "NA"
        ]
    },
    "Amazon.com, Inc.": {
        "ceo_name": ["Andy Jassy"],
        "key_leaders": [
            "Andy Jassy", "Doug Herrington", "Matt Garman", "Brian Olsavsky"
        ],
        "board_members": [
            "Jeffrey P. Bezos", "Andy Jassy", "Keith B. Alexander", "Edith W. Cooper",
            "Jamie S. Gorelick", "Daniel P. Huttenlocher", "Judith A. McGrath"
        ],
        "awards_recognitions": [
            "Brand Finance Global 500 No.2", "Interbrand Best Global Brand No.3",
            "Forbes World's Best Employers", "Time100 Most Influential Companies",
            "Fortune World's Most Admired Companies"
        ],
        "recent_funding_rounds": [
            "Post-IPO Debt: $5B, Oct 2013", "Post-IPO Equity: $200M, Mar 2013"
        ]
    },
    "Microsoft Corporation": {
        "ceo_name": ["Satya Nadella"],
        "key_leaders": [
            "Satya Nadella", "Amy Hood", "Brad Smith", "Judson Althoff", "Scott Guthrie", "Takeshi Numoto"
        ],
        "board_members": [
            "Satya Nadella", "Reid Hoffman", "Hugh Johnston", "Teri List", "Catherine MacGregor",
            "Mark Mason", "John David Rainey", "Sandra Peterson", "Penny Pritzker",
            "Charles Scharf", "John Stanton", "Emma Walmsley"
        ],
        "awards_recognitions": [
            "Fortune World's Most Admired Companies", "JUST 100", "Dow Jones Sustainability Indices",
            "MSCI AAA ESG Rating", "FTSE4Good", "World's Most Ethical Companies", "Ethisphere", "Forbes Best Employers"
        ],
        "recent_funding_rounds": [
            "No equity rounds (public)", "Share repurchases/dividends ongoing",
            "quarterly returns to shareholders"
        ]
    }
}

def normalize(text: str) -> str:
    """Normalizes string to only lowercase alphanumeric characters for robust matching."""
    return "".join(c for c in text.lower() if c.isalnum())

def verify_name(input_val: str, verified_list: List[str]) -> bool:
    """Checks if an input string matches or overlaps with a verified registry list."""
    norm_input = normalize(input_val)
    if not norm_input:
        return False
    
    # Check if "na" matches "na"
    norm_verified_list = [normalize(v) for v in verified_list]
    if "na" in norm_verified_list and norm_input == "na":
        return True
        
    for verified in verified_list:
        norm_verified = normalize(verified)
        if norm_verified == norm_input:
            return True
        # Partial overlap check for longer words
        if len(norm_input) >= 3 and len(norm_verified) >= 3:
            if norm_verified in norm_input or norm_input in norm_verified:
                return True
    return False

def parse_key_leaders(leaders_str: str) -> List[str]:
    """Parses key leader names from comma/semicolon/parentheses formatted strings."""
    # Split by semicolon first
    parts = [p.strip() for p in leaders_str.split(";") if p.strip()]
    names = []
    for part in parts:
        # If parentheses are present (e.g. Satya Nadella (CEO)), extract the name before '('
        if "(" in part:
            name_part = part.split("(")[0].strip()
        # If comma is present (e.g. Julie Sweet,CEO), extract the name before the first ','
        elif "," in part:
            name_part = part.split(",")[0].strip()
        else:
            name_part = part.strip()
        if name_part:
            names.append(name_part)
    return names

def detect_fabricated_entities(record_payload: Dict[str, Any]) -> Tuple[bool, float, float, List[str]]:
    """
    Validates company profile parameters to detect fabricated entities (invented people, fake funding, fake awards).
    Checks:
    - CEO Name matches verified CEO registry.
    - Key Business Leaders match verified leaders registry.
    - Board of Directors matches verified board members registry.
    - Awards & Recognitions match verified awards registry.
    - Recent Funding Rounds match verified funding registry.
    
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
        # If the company is not in the registry, we cannot validate it. We treat it as unverified.
        return False, 0.0, 100.0, [f"Company '{company_name}' is not present in the verified registry."]

    registry = VERIFIED_REGISTRY[matched_company]
    passed_checks = 0
    total_checks = 5

    # 1. Validate CEO Name
    ceo_val = record_payload.get("ceo_name", "").strip()
    if not ceo_val:
        errors.append("Hallucination Error [CEO Name]: Field is empty.")
    elif not verify_name(ceo_val, registry["ceo_name"]):
        errors.append(f"Hallucination Error [CEO Name]: '{ceo_val}' is not a verified CEO.")
    else:
        passed_checks += 1

    # 2. Validate Key Business Leaders
    leaders_val = record_payload.get("key_leaders", "").strip()
    if not leaders_val:
        errors.append("Hallucination Error [Key Business Leaders]: Field is empty.")
    else:
        parsed_leaders = parse_key_leaders(leaders_val)
        if not parsed_leaders:
            errors.append(f"Hallucination Error [Key Business Leaders]: Could not parse leader names from '{leaders_val}'.")
        else:
            leader_errors = []
            for leader in parsed_leaders:
                if not verify_name(leader, registry["key_leaders"]):
                    leader_errors.append(leader)
            if leader_errors:
                errors.append(f"Hallucination Error [Key Business Leaders]: Fabricated key leaders detected: {', '.join(leader_errors)}")
            else:
                passed_checks += 1

    # 3. Validate Board of Directors / Advisors
    board_val = record_payload.get("board_members", "").strip()
    if not board_val:
        errors.append("Hallucination Error [Board of Directors]: Field is empty.")
    else:
        # Split by semicolon
        parsed_board = [b.strip() for b in board_val.split(";") if b.strip()]
        if not parsed_board:
            errors.append(f"Hallucination Error [Board of Directors]: Could not parse board members from '{board_val}'.")
        else:
            board_errors = []
            for member in parsed_board:
                if not verify_name(member, registry["board_members"]):
                    board_errors.append(member)
            if board_errors:
                errors.append(f"Hallucination Error [Board of Directors]: Fabricated board member/entity detected: {', '.join(board_errors)}")
            else:
                passed_checks += 1

    # 4. Validate Awards & Recognitions
    awards_val = record_payload.get("awards_recognitions", "").strip()
    if not awards_val:
        errors.append("Hallucination Error [Awards & Recognitions]: Field is empty.")
    else:
        # Split by semicolon
        parsed_awards = [a.strip() for a in awards_val.split(";") if a.strip()]
        if not parsed_awards:
            errors.append(f"Hallucination Error [Awards & Recognitions]: Could not parse awards from '{awards_val}'.")
        else:
            awards_errors = []
            for award in parsed_awards:
                if not verify_name(award, registry["awards_recognitions"]):
                    awards_errors.append(award)
            if awards_errors:
                errors.append(f"Hallucination Error [Awards & Recognitions]: Fabricated award detected: {', '.join(awards_errors)}")
            else:
                passed_checks += 1

    # 5. Validate Recent Funding Rounds
    funding_val = record_payload.get("recent_funding_rounds", "").strip()
    if not funding_val:
        errors.append("Hallucination Error [Recent Funding Rounds]: Field is empty.")
    else:
        # Split by semicolon
        parsed_funding = [f.strip() for f in funding_val.split(";") if f.strip()]
        if not parsed_funding:
            errors.append(f"Hallucination Error [Recent Funding Rounds]: Could not parse funding from '{funding_val}'.")
        else:
            funding_errors = []
            for item in parsed_funding:
                if not verify_name(item, registry["recent_funding_rounds"]):
                    funding_errors.append(item)
            if funding_errors:
                errors.append(f"Hallucination Error [Recent Funding Rounds]: Fabricated funding round details detected: {', '.join(funding_errors)}")
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
    
    log_lines.append(f"Hallucination Detection Report for {os.path.basename(input_csv)}")
    log_lines.append("="*90)
    
    # Check if this CSV contains the target columns
    required_cols = ["ceo_name", "key_leaders", "board_members", "awards_recognitions", "recent_funding_rounds"]
    has_cols = any(col in dataset[0] for col in required_cols)
    if not has_cols:
        print(f"Skipped {input_csv}: Missing target validation columns.")
        return
        
    print(f"\nProcessing {len(dataset)} companies for hallucination detection...")
    print(f"{'Company Name':<45} | {'Passed':<6} | {'Failed':<6} | {'Validity':<8} | {'Risk':<6} | {'Status':<10}")
    print("-" * 96)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company")
        
        # Run checks
        success, validity_score, risk_score, errors = detect_fabricated_entities(row)
        
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
        "ceo_name": "Tim Cook",
        "key_leaders": "Tim Cook,CEO; Luca Maestri,CFO; John Ternus,SVP Hardware Engineering",
        "board_members": "Tim Cook; Arthur D. Levinson; Al Gore; Monica Lozano",
        "awards_recognitions": "Fortune Most Admired Companies; Interbrand Best Global Brand; TIME Most Influential Companies",
        "recent_funding_rounds": "IPO 1980; Ongoing public equity markets"
    }
    success, validity, risk, errors = detect_fabricated_entities(apple_profile)
    assert success is True, f"Factual profile failed validation: {errors}"
    assert validity == 100.0
    assert risk == 0.0
    assert not errors

def test_fabricated_ceo_fails():
    """Verifies that an invented CEO name fails validation, raising risk score and error."""
    fabricated_profile = {
        "name": "Apple Inc.",
        "ceo_name": "John Smith", # Fake CEO
        "key_leaders": "Tim Cook,CEO; Luca Maestri,CFO; John Ternus,SVP Hardware Engineering",
        "board_members": "Tim Cook; Arthur D. Levinson; Al Gore; Monica Lozano",
        "awards_recognitions": "Fortune Most Admired Companies; Interbrand Best Global Brand; TIME Most Influential Companies",
        "recent_funding_rounds": "IPO 1980; Ongoing public equity markets"
    }
    success, validity, risk, errors = detect_fabricated_entities(fabricated_profile)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("not a verified CEO" in err for err in errors)

def test_fabricated_leader_fails():
    """Verifies that an invented key business leader fails validation."""
    fabricated_profile = {
        "name": "Apple Inc.",
        "ceo_name": "Tim Cook",
        "key_leaders": "Tim Cook,CEO; John Smith,CTO; John Ternus,SVP Hardware Engineering", # Fake Leader
        "board_members": "Tim Cook; Arthur D. Levinson; Al Gore; Monica Lozano",
        "awards_recognitions": "Fortune Most Admired Companies; Interbrand Best Global Brand; TIME Most Influential Companies",
        "recent_funding_rounds": "IPO 1980; Ongoing public equity markets"
    }
    success, validity, risk, errors = detect_fabricated_entities(fabricated_profile)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("Fabricated key leaders detected" in err for err in errors)

def test_fabricated_board_member_fails():
    """Verifies that an invented board member fails validation."""
    fabricated_profile = {
        "name": "Apple Inc.",
        "ceo_name": "Tim Cook",
        "key_leaders": "Tim Cook,CEO; Luca Maestri,CFO; John Ternus,SVP Hardware Engineering",
        "board_members": "Tim Cook; Arthur D. Levinson; Al Gore; Mickey Mouse", # Fake Board Member
        "awards_recognitions": "Fortune Most Admired Companies; Interbrand Best Global Brand; TIME Most Influential Companies",
        "recent_funding_rounds": "IPO 1980; Ongoing public equity markets"
    }
    success, validity, risk, errors = detect_fabricated_entities(fabricated_profile)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("Fabricated board member/entity detected" in err for err in errors)

def test_fabricated_award_fails():
    """Verifies that an invented award name fails validation."""
    fabricated_profile = {
        "name": "Apple Inc.",
        "ceo_name": "Tim Cook",
        "key_leaders": "Tim Cook,CEO; Luca Maestri,CFO; John Ternus,SVP Hardware Engineering",
        "board_members": "Tim Cook; Arthur D. Levinson; Al Gore; Monica Lozano",
        "awards_recognitions": "Fortune Most Admired Companies; Nobel Prize in Technology; TIME Most Influential Companies", # Fake Award
        "recent_funding_rounds": "IPO 1980; Ongoing public equity markets"
    }
    success, validity, risk, errors = detect_fabricated_entities(fabricated_profile)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("Fabricated award detected" in err for err in errors)

def test_fabricated_funding_fails():
    """Verifies that an invented funding round details fails validation."""
    fabricated_profile = {
        "name": "Apple Inc.",
        "ceo_name": "Tim Cook",
        "key_leaders": "Tim Cook,CEO; Luca Maestri,CFO; John Ternus,SVP Hardware Engineering",
        "board_members": "Tim Cook; Arthur D. Levinson; Al Gore; Monica Lozano",
        "awards_recognitions": "Fortune Most Admired Companies; Interbrand Best Global Brand; TIME Most Influential Companies",
        "recent_funding_rounds": "IPO 1980; Series C - $50M - Sequoia Capital" # Fake Funding
    }
    success, validity, risk, errors = detect_fabricated_entities(fabricated_profile)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("Fabricated funding round details detected" in err for err in errors)

if __name__ == "__main__":
    import sys
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "4.1.csv")
    
    master_out_csv = os.path.join(dir_path, "4.1_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "4.1_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "4.1_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "4.1_completed_validation_results.log")
    
    print("=" * 96)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (TARGET COMPANIES)")
    print("=" * 96)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 96)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED 4.1 DATASET")
    print("=" * 96)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 96)
    
    try:
        test_genuine_profiles_pass()
        print("✓ test_genuine_profiles_pass: PASSED")
        test_fabricated_ceo_fails()
        print("✓ test_fabricated_ceo_fails: PASSED")
        test_fabricated_leader_fails()
        print("✓ test_fabricated_leader_fails: PASSED")
        test_fabricated_board_member_fails()
        print("✓ test_fabricated_board_member_fails: PASSED")
        test_fabricated_award_fails()
        print("✓ test_fabricated_award_fails: PASSED")
        test_fabricated_funding_fails()
        print("✓ test_fabricated_funding_fails: PASSED")
        print("\nAll hallucination detection and factual accuracy assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical factual accuracy test assertion failed:", e)
        sys.exit(1)
