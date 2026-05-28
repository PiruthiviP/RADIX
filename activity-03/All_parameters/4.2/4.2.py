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
        "office_cities": [
            "New York", "London", "Bangalore", "Paris", "Tokyo", "Toronto", "Sydney", "Frankfurt"
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
        "office_cities": [
            "New York", "London", "Bangalore", "Dublin", "Tokyo", "Toronto", "Sydney"
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
        "office_cities": [
            "Cupertino", "Austin", "London", "Shanghai", "Bangalore", "Tokyo", "Munich"
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
        "office_cities": [
            "Bangalore", "Chennai", "Pune", "Hyderabad", "New York", "London"
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
        "office_cities": [
            "Bangalore", "Pune", "Chennai", "Hyderabad", "New York", "London", "Frankfurt", "Sydney", "Tokyo"
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
        "office_cities": [
            "Seattle", "Arlington", "New York", "Austin", "Bangalore", "Hyderabad", "London", "Berlin", "Tokyo", "Sydney"
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
        "office_cities": [
            "Redmond", "London", "Munich", "Paris", "Hyderabad", "Tokyo", "Shanghai", "Toronto", "Sydney", "Sao Paulo"
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

# Plausible but false reference lists for cross-company mapping & known entities
FAMOUS_FORMER_CEOS = ["Steve Jobs", "Bill Gates", "Steve Ballmer", "Larry Page", "Sergey Brin", "Jeff Bezos"]
ALL_VERIFIED_CEOS = [c for r in VERIFIED_REGISTRY.values() for c in r["ceo_name"]] + FAMOUS_FORMER_CEOS
ALL_VERIFIED_LEADERS = [l for r in VERIFIED_REGISTRY.values() for l in r["key_leaders"]] + ["Paul Allen", "Steve Wozniak"]
ALL_VERIFIED_CITIES = list(set([c for r in VERIFIED_REGISTRY.values() for c in r["office_cities"]])) + ["San Francisco", "Boston", "San Jose"]
ALL_VERIFIED_AWARDS = [a for r in VERIFIED_REGISTRY.values() for a in r["awards_recognitions"]]

def normalize(text: str) -> str:
    """Normalizes string to only lowercase alphanumeric characters for robust matching."""
    return "".join(c for c in text.lower() if c.isalnum())

def verify_name(input_val: str, verified_list: List[str]) -> bool:
    """Checks if an input string matches or overlaps with a verified registry list."""
    norm_input = normalize(input_val)
    if not norm_input:
        return False
    
    norm_verified_list = [normalize(v) for v in verified_list]
    if "na" in norm_verified_list and norm_input == "na":
        return True
        
    for verified in verified_list:
        norm_verified = normalize(verified)
        if norm_verified == norm_input:
            return True
        if len(norm_input) >= 3 and len(norm_verified) >= 3:
            if norm_verified in norm_input or norm_input in norm_verified:
                return True
    return False

def parse_key_leaders(leaders_str: str) -> List[str]:
    """Parses key leader names from comma/semicolon/parentheses formatted strings."""
    parts = [p.strip() for p in leaders_str.split(";") if p.strip()]
    names = []
    for part in parts:
        if "(" in part:
            name_part = part.split("(")[0].strip()
        elif "," in part:
            name_part = part.split(",")[0].strip()
        else:
            name_part = part.strip()
        if name_part:
            names.append(name_part)
    return names

def parse_office_cities(office_str: str) -> List[str]:
    """Parses cities from semicolon-separated 'City, Country' strings."""
    parts = [p.strip() for p in office_str.split(";") if p.strip()]
    cities = []
    for part in parts:
        if "," in part:
            city = part.split(",")[0].strip()
        else:
            city = part.strip()
        if city:
            cities.append(city)
    return cities

def detect_plausible_but_false(record_payload: Dict[str, Any]) -> Tuple[bool, float, float, List[str]]:
    """
    Validates company profile parameters to detect plausible but false entities (wrong CEO, wrong city, wrong funding).
    
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

    # 1. Validate CEO Name (Plausible but wrong person check)
    ceo_val = record_payload.get("ceo_name", "").strip()
    if not ceo_val:
        errors.append("Hallucination Error [CEO Name]: Field is empty.")
    elif not verify_name(ceo_val, registry["ceo_name"]):
        # Check if the name belongs to another verified CEO or is a famous former executive (plausible)
        is_plausible = verify_name(ceo_val, ALL_VERIFIED_CEOS)
        if is_plausible:
            errors.append(f"Plausible but False Error [CEO Name]: CEO '{ceo_val}' belongs to another company or is a former CEO, and does not lead '{matched_company}'.")
        else:
            errors.append(f"Hallucination Error [CEO Name]: '{ceo_val}' is incorrect.")
    else:
        passed_checks += 1

    # 2. Validate Key Business Leaders (Plausible but wrong company leaders check)
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
                    is_plausible = verify_name(leader, ALL_VERIFIED_LEADERS)
                    if is_plausible:
                        leader_errors.append(f"'{leader}' (plausible but leads another company)")
                    else:
                        leader_errors.append(f"'{leader}' (unverified)")
            if leader_errors:
                errors.append(f"Hallucination Error [Key Business Leaders]: Fabricated key leaders detected: {', '.join(leader_errors)}")
            else:
                passed_checks += 1

    # 3. Validate Office Locations (Office exists but company not there check)
    office_val = record_payload.get("office_locations", "").strip()
    if not office_val:
        errors.append("Hallucination Error [Office Locations]: Field is empty.")
    else:
        parsed_cities = parse_office_cities(office_val)
        if not parsed_cities:
            errors.append(f"Hallucination Error [Office Locations]: Could not parse office locations from '{office_val}'.")
        else:
            office_errors = []
            for city in parsed_cities:
                if not verify_name(city, registry["office_cities"]):
                    is_plausible = verify_name(city, ALL_VERIFIED_CITIES)
                    if is_plausible:
                        office_errors.append(f"'{city}' (city has major tech offices but {matched_company} has no presence there)")
                    else:
                        office_errors.append(f"'{city}' (unverified city)")
            if office_errors:
                errors.append(f"Plausible but False Error [Office Locations]: Office locations mismatch: {', '.join(office_errors)}")
            else:
                passed_checks += 1

    # 4. Validate Awards & Recognitions (Plausible but wrong award check)
    awards_val = record_payload.get("awards_recognitions", "").strip()
    if not awards_val:
        errors.append("Hallucination Error [Awards & Recognitions]: Field is empty.")
    else:
        parsed_awards = [a.strip() for a in awards_val.split(";") if a.strip()]
        if not parsed_awards:
            errors.append(f"Hallucination Error [Awards & Recognitions]: Could not parse awards from '{awards_val}'.")
        else:
            awards_errors = []
            for award in parsed_awards:
                if not verify_name(award, registry["awards_recognitions"]):
                    is_plausible = verify_name(award, ALL_VERIFIED_AWARDS)
                    if is_plausible:
                        awards_errors.append(f"'{award}' (real award but incorrect for this company)")
                    else:
                        awards_errors.append(f"'{award}' (unverified)")
            if awards_errors:
                errors.append(f"Hallucination Error [Awards & Recognitions]: Fabricated awards: {', '.join(awards_errors)}")
            else:
                passed_checks += 1

    # 5. Validate Recent Funding Rounds (Plausible but incorrect funding amount check)
    funding_val = record_payload.get("recent_funding_rounds", "").strip()
    if not funding_val:
        errors.append("Hallucination Error [Recent Funding Rounds]: Field is empty.")
    else:
        parsed_funding = [f.strip() for f in funding_val.split(";") if f.strip()]
        if not parsed_funding:
            errors.append(f"Hallucination Error [Recent Funding Rounds]: Could not parse funding details from '{funding_val}'.")
        else:
            funding_errors = []
            for item in parsed_funding:
                if not verify_name(item, registry["recent_funding_rounds"]):
                    # Extract any dollar amounts in the string to see if the amount itself is plausible but wrong
                    amounts = re.findall(r'\$\d+(?:\.\d+)?[B|M]', item)
                    verified_str = " ".join(registry["recent_funding_rounds"])
                    verified_amounts = re.findall(r'\$\d+(?:\.\d+)?[B|M]', verified_str)
                    
                    if amounts:
                        # Check if any amount in item is different from verified amounts but is a plausible quantity
                        is_wrong_amount = any(amt not in verified_amounts for amt in amounts)
                        if is_wrong_amount:
                            funding_errors.append(f"'{item}' (funding amount {amounts} is plausible but incorrect)")
                        else:
                            funding_errors.append(f"'{item}' (details/date incorrect)")
                    else:
                        # Check if company is public and shouldn't have funding rounds
                        if "NA" in registry["recent_funding_rounds"] or "No equity rounds" in verified_str:
                            funding_errors.append(f"'{item}' (mature public company has no recent private funding rounds)")
                        else:
                            funding_errors.append(f"'{item}' (unverified details)")
            if funding_errors:
                errors.append(f"Plausible but False Error [Recent Funding Rounds]: Funding rounds mismatch: {', '.join(funding_errors)}")
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
    
    log_lines.append(f"Hallucination Detection (Plausible but False) Report for {os.path.basename(input_csv)}")
    log_lines.append("="*90)
    
    # Check if this CSV contains the target columns
    required_cols = ["ceo_name", "key_leaders", "office_locations", "awards_recognitions", "recent_funding_rounds"]
    has_cols = any(col in dataset[0] for col in required_cols)
    if not has_cols:
        print(f"Skipped {input_csv}: Missing target validation columns.")
        return
        
    print(f"\nProcessing {len(dataset)} companies for 'Plausible but False' detection...")
    print(f"{'Company Name':<45} | {'Passed':<6} | {'Failed':<6} | {'Validity':<8} | {'Risk':<6} | {'Status':<10}")
    print("-" * 96)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company")
        
        # Run checks
        success, validity_score, risk_score, errors = detect_plausible_but_false(row)
        
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
        "office_locations": "Cupertino, United States; Austin, United States; London, United Kingdom; Shanghai, China; Bangalore, India; Tokyo, Japan; Munich, Germany",
        "awards_recognitions": "Fortune Most Admired Companies; Interbrand Best Global Brand; TIME Most Influential Companies",
        "recent_funding_rounds": "IPO 1980; Ongoing public equity markets"
    }
    success, validity, risk, errors = detect_plausible_but_false(apple_profile)
    assert success is True, f"Factual profile failed validation: {errors}"
    assert validity == 100.0
    assert risk == 0.0
    assert not errors

def test_plausible_but_wrong_ceo_fails():
    """Verifies that a real CEO from another company or former CEO is caught as Plausible but False."""
    fabricated_profile_1 = {
        "name": "Apple Inc.",
        "ceo_name": "Satya Nadella", # Real CEO of Microsoft, wrong for Apple
        "key_leaders": "Tim Cook,CEO; Luca Maestri,CFO; John Ternus,SVP Hardware Engineering",
        "office_locations": "Cupertino, United States; Austin, United States; London, United Kingdom; Shanghai, China; Bangalore, India; Tokyo, Japan; Munich, Germany",
        "awards_recognitions": "Fortune Most Admired Companies; Interbrand Best Global Brand; TIME Most Influential Companies",
        "recent_funding_rounds": "IPO 1980; Ongoing public equity markets"
    }
    success, validity, risk, errors = detect_plausible_but_false(fabricated_profile_1)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("belongs to another company" in err for err in errors)

    fabricated_profile_2 = {
        "name": "Apple Inc.",
        "ceo_name": "Steve Jobs", # Former CEO of Apple, wrong for today
        "key_leaders": "Tim Cook,CEO; Luca Maestri,CFO; John Ternus,SVP Hardware Engineering",
        "office_locations": "Cupertino, United States; Austin, United States; London, United Kingdom; Shanghai, China; Bangalore, India; Tokyo, Japan; Munich, Germany",
        "awards_recognitions": "Fortune Most Admired Companies; Interbrand Best Global Brand; TIME Most Influential Companies",
        "recent_funding_rounds": "IPO 1980; Ongoing public equity markets"
    }
    success, validity, risk, errors = detect_plausible_but_false(fabricated_profile_2)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("former CEO" in err for err in errors)

def test_plausible_but_wrong_funding_amount_fails():
    """Verifies that a reasonable-sounding incorrect funding amount is caught as Plausible but False."""
    fabricated_profile = {
        "name": "Amazon.com, Inc.",
        "ceo_name": "Andy Jassy",
        "key_leaders": "Andy Jassy, CEO; Doug Herrington, CEO Worldwide Amazon Stores; Matt Garman, CEO AWS; Brian Olsavsky, CFO",
        "office_locations": "Seattle, United States; Arlington, United States; New York, United States; Austin, United States; Bangalore, India; Hyderabad, India; London, United Kingdom; Berlin, Germany; Tokyo, Japan; Sydney, Australia",
        "awards_recognitions": "Brand Finance Global 500 No.2; Interbrand Best Global Brand No.3; Forbes World's Best Employers; Time100 Most Influential Companies; Fortune World's Most Admired Companies",
        "recent_funding_rounds": "Post-IPO Debt: $10B, Oct 2013; Post-IPO Equity: $200M, Mar 2013" # Plausible ($10B instead of $5B), but false
    }
    success, validity, risk, errors = detect_plausible_but_false(fabricated_profile)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("plausible but incorrect" in err for err in errors)

def test_plausible_but_wrong_office_location_fails():
    """Verifies that an office location that exists in the ecosystem but is incorrect for the company fails."""
    fabricated_profile = {
        "name": "Apple Inc.",
        "ceo_name": "Tim Cook",
        "key_leaders": "Tim Cook,CEO; Luca Maestri,CFO; John Ternus,SVP Hardware Engineering",
        "office_locations": "Cupertino, United States; Redmond, United States; London, United Kingdom", # Redmond exists in ecosystem (Microsoft) but wrong for Apple
        "awards_recognitions": "Fortune Most Admired Companies; Interbrand Best Global Brand; TIME Most Influential Companies",
        "recent_funding_rounds": "IPO 1980; Ongoing public equity markets"
    }
    success, validity, risk, errors = detect_plausible_but_false(fabricated_profile)
    assert success is False
    assert validity == 80.0
    assert risk == 20.0
    assert any("has no presence there" in err for err in errors)

if __name__ == "__main__":
    import sys
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "4.2.csv")
    
    master_out_csv = os.path.join(dir_path, "4.2_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "4.2_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "4.2_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "4.2_completed_validation_results.log")
    
    print("=" * 96)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (TARGET COMPANIES)")
    print("=" * 96)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 96)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED 4.2 DATASET")
    print("=" * 96)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 96)
    
    try:
        test_genuine_profiles_pass()
        print("✓ test_genuine_profiles_pass: PASSED")
        test_plausible_but_wrong_ceo_fails()
        print("✓ test_plausible_but_wrong_ceo_fails: PASSED")
        test_plausible_but_wrong_funding_amount_fails()
        print("✓ test_plausible_but_wrong_funding_amount_fails: PASSED")
        test_plausible_but_wrong_office_location_fails()
        print("✓ test_plausible_but_wrong_office_location_fails: PASSED")
        print("\nAll Plausible but False verification assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical factual accuracy test assertion failed:", e)
        sys.exit(1)
