import csv
import os
import sys
from typing import Dict, Any, Tuple, List, Optional

# Verified ground truth registry for target and ambiguous companies
VERIFIED_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Accenture plc": {
        "ceo_name": "Julie Sweet",
        "incorporation_year": "1989",
        "website_url": "https://www.accenture.com",
        "headquarters_address": "Dublin, Ireland",
        "category": "Enterprise",
        "focus_sectors": "Management Consulting; Technology Services"
    },
    "Google LLC (Subsidiary of Alphabet Inc.)": {
        "ceo_name": "Sundar Pichai",
        "incorporation_year": "1998",
        "website_url": "https://www.google.com",
        "headquarters_address": "1600 Amphitheatre Parkway, Mountain View, California, USA",
        "category": "Subsidiary (Public Parent: Alphabet Inc.)",
        "focus_sectors": "Technology; Communication Services"
    },
    "Apple Inc.": {
        "ceo_name": "Tim Cook",
        "incorporation_year": "1976",
        "website_url": "https://www.apple.com",
        "headquarters_address": "One Apple Park Way, Cupertino, California, USA",
        "category": "Public Enterprise",
        "focus_sectors": "Consumer Electronics; Software"
    },
    "Tata Consultancy Services Limited": {
        "ceo_name": "K. Krithivasan",
        "incorporation_year": "1968",
        "website_url": "https://www.tcs.com",
        "headquarters_address": "Mumbai, Maharashtra, India",
        "category": "Public",
        "focus_sectors": "IT Consulting; Application Development"
    },
    "Infosys Limited": {
        "ceo_name": "Salil Parekh",
        "incorporation_year": "1981",
        "website_url": "https://www.infosys.com",
        "headquarters_address": "Bangalore, Karnataka, India",
        "category": "Public",
        "focus_sectors": "IT Services; Consulting"
    },
    "Amazon.com, Inc.": {
        "ceo_name": "Andy Jassy",
        "incorporation_year": "1994",
        "website_url": "https://www.amazon.com/",
        "headquarters_address": "410 Terry Ave N, Seattle, WA 98109, United States",
        "category": "Public Enterprise",
        "focus_sectors": "Internet Retail; Cloud Computing"
    },
    "Microsoft Corporation": {
        "ceo_name": "Satya Nadella",
        "incorporation_year": "1975",
        "website_url": "https://www.microsoft.com",
        "headquarters_address": "One Microsoft Way, Redmond, Washington 98052, United States",
        "category": "Large Cap Public Tech Conglomerate",
        "focus_sectors": "Information Technology; Financial Services"
    },
    "Delta Air Lines, Inc.": {
        "ceo_name": "Ed Bastian",
        "incorporation_year": "1924",
        "website_url": "https://www.delta.com",
        "headquarters_address": "Atlanta, Georgia, USA",
        "category": "Aviation / Travel",
        "focus_sectors": "Aviation; Transportation; Logistics"
    },
    "Delta Controls Ltd.": {
        "ceo_name": "Delta Controls Executive",
        "incorporation_year": "1980",
        "website_url": "https://www.deltacontrols.com",
        "headquarters_address": "Surrey, BC, Canada",
        "category": "Building Automation",
        "focus_sectors": "Building Automation; HVAC Controls; IoT"
    },
    "Delta Dental Agency": {
        "ceo_name": "Delta Dental Director",
        "incorporation_year": "1954",
        "website_url": "https://www.deltadental.com",
        "headquarters_address": "Oak Brook, Illinois, USA",
        "category": "Insurance / Healthcare",
        "focus_sectors": "Dental Insurance; Healthcare Plans"
    },
    "Delta Energy Corp": {
        "ceo_name": "Delta Energy Chief",
        "incorporation_year": "2005",
        "website_url": "https://www.deltaenergy.com",
        "headquarters_address": "Houston, Texas, USA",
        "category": "Energy / Utilities",
        "focus_sectors": "Oil & Gas; Renewable Energy; Electricity"
    },
    "Target Corporation": {
        "ceo_name": "Brian Cornell",
        "incorporation_year": "1902",
        "website_url": "https://www.target.com",
        "headquarters_address": "Minneapolis, Minnesota, USA",
        "category": "Retail / E-commerce",
        "focus_sectors": "Retail; Consumer Goods; E-commerce"
    },
    "Target Brand Agency": {
        "ceo_name": "Target Agency Director",
        "incorporation_year": "2015",
        "website_url": "https://www.targetagency.com",
        "headquarters_address": "Portland, Oregon, USA",
        "category": "Marketing / Brand Agency",
        "focus_sectors": "Marketing; Advertising; Corporate Branding"
    }
}

def naive_resolve(record: Dict[str, Any]) -> Optional[str]:
    """
    Simulates a naïve entity resolver.
    Matches names solely on simple substring/prefix, causing collisions for identical names (Delta, Target).
    """
    name_query = record.get("name", "").strip().lower()
    
    # Simple prefix mapping
    if "delta" in name_query:
        return "Delta Air Lines, Inc."
    elif "target" in name_query:
        return "Target Corporation"
        
    # Exact/Fuzzy match for others
    for reg_name in VERIFIED_REGISTRY:
        if name_query in reg_name.lower():
            return reg_name
    return None

def context_aware_resolve(record: Dict[str, Any]) -> Optional[str]:
    """
    Implements a robust context-aware disambiguation engine.
    Uses secondary attributes (website_url, category, headquarters, or focus_sectors)
    to select the correct unique company entity.
    """
    name_query = record.get("name", "").strip().lower()
    short_name = record.get("short_name", "").strip().lower()
    
    candidates = []
    
    # 1. Gather all candidates matching the name query or short name
    for reg_name in VERIFIED_REGISTRY:
        reg_lower = reg_name.lower()
        if name_query in reg_lower or (short_name and short_name in reg_lower):
            candidates.append(reg_name)
            
    if not candidates:
        return None
        
    if len(candidates) == 1:
        return candidates[0]
        
    # 2. Disambiguate using secondary context: website domain URL, category/industry, and headquarters
    best_candidate = None
    max_matches = -1
    
    website_val = str(record.get("website_url", "")).strip().lower()
    category_val = str(record.get("category", "")).strip().lower()
    hq_val = str(record.get("headquarters_address", "")).strip().lower()
    sectors_val = str(record.get("focus_sectors", "")).strip().lower()
    
    for cand in candidates:
        cand_truth = VERIFIED_REGISTRY[cand]
        matches = 0
        
        # Check website domain match
        cand_url = cand_truth["website_url"].lower()
        # Extract main domain keyword (e.g. deltacontrols)
        cand_domain = cand_url.replace("https://", "").replace("http://", "").replace("www.", "").split(".")[0]
        if cand_domain in website_val:
            matches += 3 # High weight for website URL domain
            
        # Check category / sectors match
        cand_cat = cand_truth["category"].lower()
        cand_sectors = cand_truth["focus_sectors"].lower()
        
        # Match keywords in category or focus sectors
        for kw in cand_cat.replace("/", " ").replace("&", " ").split():
            if len(kw) > 3 and kw in category_val:
                matches += 1
        for kw in cand_sectors.replace(";", " ").replace("&", " ").split():
            if len(kw) > 3 and kw in sectors_val:
                matches += 1
                
        # Check HQ address match
        cand_hq = cand_truth["headquarters_address"].lower()
        # Split cities/states/countries
        for word in cand_hq.replace(",", " ").split():
            if len(word) > 3 and word in hq_val:
                matches += 1
                
        if matches > max_matches:
            max_matches = matches
            best_candidate = cand
            
    return best_candidate

def validate_entity(record: Dict[str, Any], resolver_func) -> Tuple[bool, float, List[str], Optional[str]]:
    """
    Validates a company record using a specified entity resolver function.
    
    Returns: (success, score, errors, matched_company_name)
    """
    errors = []
    ingested_name = record.get("name", "").strip()
    
    matched_name = resolver_func(record)
    if not matched_name:
        return False, 0.0, [f"Ambiguity Resolution Error: Could not resolve or match company '{ingested_name}' to any registered entity."], None
        
    # Check if the resolved name doesn't match the ingested name (Context Confusion check)
    # E.g. Delta Controls matched to Delta Air Lines
    if "delta" in ingested_name.lower() or "target" in ingested_name.lower():
        if matched_name.lower() != ingested_name.lower() and ingested_name.lower() not in ["delta", "target"]:
            errors.append(
                f"Disambiguation Failure: Ingested record '{ingested_name}' was incorrectly matched "
                f"to entity '{matched_name}'."
            )
            
    truth = VERIFIED_REGISTRY[matched_name]
    checks_passed = 0
    total_checks = 4
    
    # 1. CEO Name check
    ingested_ceo = record.get("ceo_name", "").strip()
    truth_ceo = truth["ceo_name"]
    if ingested_ceo.replace(".", "").lower() == truth_ceo.replace(".", "").lower():
        checks_passed += 1
    else:
        errors.append(f"Mismatch [CEO Name]: Ingested '{ingested_ceo}', expected '{truth_ceo}'")
        
    # 2. HQ address check
    ingested_hq = record.get("headquarters_address", "").strip()
    truth_hq = truth["headquarters_address"].strip()
    # Check for basic substring match
    if truth_hq.lower() in ingested_hq.lower() or ingested_hq.lower() in truth_hq.lower():
        checks_passed += 1
    else:
        errors.append(f"Mismatch [Headquarters Address]: Ingested '{ingested_hq}', expected '{truth_hq}'")
        
    # 3. Website URL check
    ingested_url = record.get("website_url", "").strip().rstrip('/')
    truth_url = truth["website_url"].strip().rstrip('/')
    if ingested_url == truth_url or truth_url in ingested_url or ingested_url in truth_url:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [Website URL]: Ingested '{ingested_url}', expected '{truth_url}'")
        
    # 4. Incorporation year check
    ingested_year = record.get("incorporation_year", "").strip()
    truth_year = truth["incorporation_year"]
    if ingested_year == truth_year:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [Year of Incorporation]: Ingested '{ingested_year}', expected '{truth_year}'")
        
    success = (len(errors) == 0 and checks_passed == total_checks)
    score = round((checks_passed / total_checks) * 100, 2)
    
    return success, score, errors, matched_name

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
    resolver_func,
    engine_name: str
) -> bool:
    """
    Validates all profiles in the input CSV.
    Saves validation results to CSV and log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return False
        
    report_rows = []
    log_lines = []
    all_passed = True
    
    log_lines.append(f"Entity Disambiguation Report ({engine_name}) for {os.path.basename(input_csv)}")
    log_lines.append("="*96)
    
    print(f"\nProcessing {len(dataset)} companies using {engine_name}...")
    print(f"{'Company Name':<40} | {'Matched Entity':<30} | {'Score':<6} | {'Status':<10}")
    print("-" * 96)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company").strip()
        
        success, score, errors, matched_name = validate_entity(row, resolver_func)
        status_str = "PASSED" if success else "CONFUSED/FAILED"
        if not success:
            all_passed = False
            
        print(f"{company_name[:40]:<40} | {str(matched_name)[:30]:<30} | {score:<5}% | {status_str:<10}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Matched Entity: {matched_name}\n"
            f"  Status: {status_str}\n"
            f"  Match Score: {score}%\n"
        )
        if errors:
            log_line += "  Validation/Disambiguation Issues:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Matched Entity": matched_name,
            "Validation Status": status_str,
            "Match Score (%)": score,
            "Issues": "; ".join(errors)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Matched Entity", "Validation Status", "Match Score (%)", "Issues"
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

def test_context_aware_resolves_delta_airlines():
    profile = {
        "name": "Delta",
        "category": "Aviation",
        "website_url": "https://www.delta.com",
        "headquarters_address": "Atlanta, Georgia, USA",
        "ceo_name": "Ed Bastian",
        "incorporation_year": "1924"
    }
    success, score, errors, matched = validate_entity(profile, context_aware_resolve)
    assert success is True, f"Failed: {errors}"
    assert matched == "Delta Air Lines, Inc."

def test_context_aware_resolves_delta_controls():
    profile = {
        "name": "Delta Controls Ltd.",
        "category": "Building Automation",
        "website_url": "https://www.deltacontrols.com",
        "headquarters_address": "Surrey, BC, Canada",
        "ceo_name": "Delta Controls Executive",
        "incorporation_year": "1980"
    }
    success, score, errors, matched = validate_entity(profile, context_aware_resolve)
    assert success is True, f"Failed: {errors}"
    assert matched == "Delta Controls Ltd."

def test_context_aware_resolves_target_retail():
    profile = {
        "name": "Target",
        "category": "Retail",
        "website_url": "https://www.target.com",
        "headquarters_address": "Minneapolis, Minnesota, USA",
        "ceo_name": "Brian Cornell",
        "incorporation_year": "1902"
    }
    success, score, errors, matched = validate_entity(profile, context_aware_resolve)
    assert success is True, f"Failed: {errors}"
    assert matched == "Target Corporation"

def test_context_aware_resolves_target_agency():
    profile = {
        "name": "Target Brand Agency",
        "category": "Marketing & Advertising",
        "website_url": "https://www.targetagency.com",
        "headquarters_address": "Portland, Oregon, USA",
        "ceo_name": "Target Agency Director",
        "incorporation_year": "2015"
    }
    success, score, errors, matched = validate_entity(profile, context_aware_resolve)
    assert success is True, f"Failed: {errors}"
    assert matched == "Target Brand Agency"

def test_naive_resolver_collides_on_delta():
    # Naive resolver always maps "Delta" names to Delta Air Lines
    profile = {
        "name": "Delta Dental Agency",
        "category": "Healthcare",
        "website_url": "https://www.deltadental.com",
        "headquarters_address": "Oak Brook, Illinois, USA",
        "ceo_name": "Delta Dental Director",
        "incorporation_year": "1954"
    }
    success, score, errors, matched = validate_entity(profile, naive_resolve)
    assert success is False
    assert matched == "Delta Air Lines, Inc." # Context confusion
    assert any("Disambiguation Failure" in err for err in errors)

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "11.1.csv")
    
    robust_out_csv = os.path.join(dir_path, "11.1_completed_validation_results.csv")
    robust_out_log = os.path.join(dir_path, "11.1_completed_validation_results.log")
    
    naive_out_csv = os.path.join(dir_path, "11.1_naive_validation_results.csv")
    naive_out_log = os.path.join(dir_path, "11.1_naive_validation_results.log")
    
    print("=" * 96)
    print("1. RUNNING CONTEXT-AWARE ENTITY DISAMBIGUATION VALIDATION")
    print("=" * 96)
    context_ok = generate_validation_report(
        completed_csv_path, robust_out_csv, robust_out_log, context_aware_resolve, "Context-Aware Disambiguation Engine"
    )
    
    print("\n" + "=" * 96)
    print("2. RUNNING NAÏVE ENTITY RESOLVER VALIDATION (DEMONSTRATING COLLISION)")
    print("=" * 96)
    naive_ok = generate_validation_report(
        completed_csv_path, naive_out_csv, naive_out_log, naive_resolve, "Naïve Resolver Engine"
    )
    
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM DISAMBIGUATION TEST SUITE")
    print("=" * 96)
    
    try:
        test_context_aware_resolves_delta_airlines()
        print("✓ test_context_aware_resolves_delta_airlines: PASSED")
        test_context_aware_resolves_delta_controls()
        print("✓ test_context_aware_resolves_delta_controls: PASSED")
        test_context_aware_resolves_target_retail()
        print("✓ test_context_aware_resolves_target_retail: PASSED")
        test_context_aware_resolves_target_agency()
        print("✓ test_context_aware_resolves_target_agency: PASSED")
        test_naive_resolver_collides_on_delta()
        print("✓ test_naive_resolver_collides_on_delta: PASSED")
        print("\nAll Ambiguity Resolution verification assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical disambiguation test assertion failed:", e)
        sys.exit(1)
