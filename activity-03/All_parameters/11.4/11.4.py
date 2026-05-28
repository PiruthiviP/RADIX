import csv
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# ==============================================================================
# VERIFIED REGISTRY — Canonical ground truth per unique legal entity
# ==============================================================================
VERIFIED_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Apple Inc.": {
        "short_name": "Apple",
        "ceo_name": "Tim Cook",
        "incorporation_year": "1976",
        "website_url": "https://www.apple.com",
        "headquarters_address": "One Apple Park Way, Cupertino, California, USA",
        "aliases": ["apple"]
    },
    "Microsoft Corporation": {
        "short_name": "Microsoft",
        "ceo_name": "Satya Nadella",
        "incorporation_year": "1975",
        "website_url": "https://www.microsoft.com",
        "headquarters_address": "One Microsoft Way, Redmond, Washington 98052, United States",
        "aliases": ["microsoft"]
    },
    "International Business Machines Corporation ": {
        "short_name": "IBM",
        "ceo_name": "Arvind Krishna ",
        "incorporation_year": "1911",
        "website_url": "https://www.ibm.com",
        "headquarters_address": "1 New Orchard Road, Armonk, NY 10504-1722, United States",
        "aliases": ["ibm", "international business machines", "international business machines corp", "international business machines corporation"]
    },
    "AT&T Inc.": {
        "short_name": "AT&T",
        "ceo_name": "John Stankey",
        "incorporation_year": "1885",
        "website_url": "https://www.att.com",
        "headquarters_address": "208 S. Akard St., Dallas, Texas, USA",
        "aliases": ["att", "american telephone & telegraph", "american telephone and telegraph", "american telephone and telegraph company"]
    },
    "3M Company": {
        "short_name": "3M",
        "ceo_name": "William M. Brown",
        "incorporation_year": "1902",
        "website_url": "https://www.3m.com",
        "headquarters_address": "3M Center, Maplewood, Minnesota, USA",
        "aliases": ["3m", "minnesota mining and manufacturing", "minnesota mining & manufacturing"]
    }
}


def strip_corp_suffixes(name: str) -> str:
    """Strips corporate designators from the end of a company name."""
    name = name.strip().lower()
    suffixes = [
        " corporation", " incorporated", " company", " limited", 
        " corp", " inc", " co", " ltd", " plc", " nv", " bv"
    ]
    # Iteratively strip if multiple suffixes exist
    changed = True
    while changed:
        changed = False
        for s in suffixes:
            if name.endswith(s):
                name = name[:-len(s)].strip()
                changed = True
    return name


def normalize_name(name: str) -> str:
    """Normalizes a name by stripping suffixes, replacing ampersands, and removing non-alphanumeric chars."""
    name = strip_corp_suffixes(name)
    name = name.replace("&", "and")
    return "".join(c for c in name if c.isalnum())


def clean_url(url: str) -> str:
    """Helper to normalize URLs by stripping protocol, www, trailing spaces/slashes/question marks."""
    if not url:
        return ""
    url = url.strip().lower()
    # Handle master CSV value "https://www.ibm.com ?"
    url = url.replace("?", "").strip()
    if url.startswith("https://"):
        url = url[8:]
    elif url.startswith("http://"):
        url = url[7:]
    if url.startswith("www."):
        url = url[4:]
    return url.rstrip("/")


def is_acronym_of(acronym: str, full_name: str) -> bool:
    """Checks if a string is a first-letter acronym of a multi-word name, with support for 3M->MMM."""
    acr_clean = "".join(c for c in acronym.lower() if c.isalnum())
    if not acr_clean or len(acr_clean) < 2:
        return False
    
    # Strip corporate suffixes first
    fn_stripped = strip_corp_suffixes(full_name)
    fn_clean = "".join(c if c.isalnum() or c.isspace() else "" for c in fn_stripped)
    words = [w for w in fn_clean.split() if w not in ["and", "or", "of", "the", "for"]]
    if len(words) < 2:
        return False
    
    first_letters = "".join(w[0] for w in words if w)
    
    # Standard acronym check
    if first_letters == acr_clean:
        return True
        
    # Special representation: 3M is 3 Ms -> "mmm"
    if acr_clean == "3m" and first_letters == "mmm":
        return True
        
    return False


def is_hq_match(hq1: str, hq2: str) -> bool:
    """Flexible HQ match checking for matching city or street keywords, ignoring formatting differences."""
    hq1_clean = hq1.strip().lower()
    hq2_clean = hq2.strip().lower()
    if hq1_clean in hq2_clean or hq2_clean in hq1_clean:
        return True
        
    # Split on space/comma and look for matching tokens of length >= 5
    words1 = {w.strip(",. ") for w in hq1_clean.split() if len(w.strip(",. ")) >= 5}
    words2 = {w.strip(",. ") for w in hq2_clean.split() if len(w.strip(",. ")) >= 5}
    common = words1.intersection(words2)
    
    exclude = {"united", "states", "street", "avenue", "road", "north", "south", "center"}
    distinctive_common = common - exclude
    return len(distinctive_common) > 0


def abbreviation_aware_resolve(record: Dict[str, Any]) -> Optional[str]:
    """
    Abbreviation-Aware Resolver.
    Uses acronym mapping, alias/synonym arrays, website domain, and other metadata scoring
    to resolve names when they are represented as abbreviations, acronyms, or full text.
    """
    ingested_name  = record.get("name", "").strip()
    ingested_short = record.get("short_name", "").strip().lower()
    ingested_url   = clean_url(record.get("website_url", ""))
    ingested_hq    = record.get("headquarters_address", "").strip().lower()
    ingested_year  = record.get("incorporation_year", "").strip()
    ingested_ceo   = record.get("ceo_name", "").strip().replace(".", "").lower()

    name_norm = normalize_name(ingested_name)
    best_candidate = None
    best_score = -1

    for reg_name, truth in VERIFIED_REGISTRY.items():
        score = 0

        # 1. Exact Name/Short Name Match
        reg_name_clean = reg_name.strip().lower()
        if ingested_name.lower() == reg_name_clean:
            score += 50
        elif ingested_short == truth["short_name"].strip().lower():
            score += 20

        # 2. Alias / Synonym List Match
        truth_aliases = [normalize_name(a) for a in truth.get("aliases", [])]
        if name_norm in truth_aliases:
            score += 45

        # 3. Acronym Match
        if is_acronym_of(ingested_name, reg_name) or is_acronym_of(reg_name, ingested_name):
            score += 40

        # 4. URL Match (Cleaned)
        truth_url = clean_url(truth["website_url"])
        if ingested_url and truth_url:
            if ingested_url == truth_url:
                score += 40
            elif ingested_url in truth_url or truth_url in ingested_url:
                score += 15

        # 5. Incorporation Year Match
        if ingested_year and ingested_year == str(truth["incorporation_year"]).strip():
            score += 30

        # 6. Headquarters Address Match (flexible)
        truth_hq = truth["headquarters_address"].strip().lower()
        if ingested_hq and truth_hq:
            if is_hq_match(ingested_hq, truth_hq):
                score += 20

        # 7. CEO Match
        truth_ceo = truth["ceo_name"].strip().replace(".", "").lower()
        if ingested_ceo and truth_ceo:
            if ingested_ceo == truth_ceo or ingested_ceo in truth_ceo or truth_ceo in ingested_ceo:
                score += 20

        if score > best_score:
            best_score = score
            best_candidate = reg_name

    return best_candidate


def naive_resolve(record: Dict[str, Any]) -> Optional[str]:
    """
    Naïve Resolver.
    Only checks for exact string matches or direct substrings on name/short_name.
    Fails on abbreviation differences (e.g. full name vs acronym).
    """
    ingested_name = record.get("name", "").strip().lower()
    ingested_short = record.get("short_name", "").strip().lower()

    for reg_name, truth in VERIFIED_REGISTRY.items():
        reg_name_clean = reg_name.strip().lower()
        truth_short = truth["short_name"].strip().lower()

        if ingested_name == reg_name_clean:
            return reg_name
        if ingested_short != "na" and ingested_short == truth_short:
            return reg_name
        if ingested_name and ingested_name in reg_name_clean:
            return reg_name
        if reg_name_clean and reg_name_clean in ingested_name:
            return reg_name

    return None


def validate_entity(
    record: Dict[str, Any],
    resolver_func
) -> Tuple[bool, float, List[str], Optional[str]]:
    """
    Validates a record against the registry using the resolver.
    Detects abbreviation mapping errors.

    Returns: (success, score, errors, matched_name)
    """
    errors = []
    ingested_name = record.get("name", "").strip()

    matched_name = resolver_func(record)
    if not matched_name:
        return False, 0.0, [
            f"Resolution Error: Could not resolve '{ingested_name}' to any registered entity."
        ], None

    truth = VERIFIED_REGISTRY[matched_name]

    # Verify if the matched entity is indeed equivalent to the ingested name
    is_same_entity = False
    ingested_norm = normalize_name(ingested_name)
    
    # Check alias match
    truth_aliases_norm = [normalize_name(a) for a in truth.get("aliases", [])]
    if ingested_norm in truth_aliases_norm:
        is_same_entity = True
    elif normalize_name(matched_name) == ingested_norm:
        is_same_entity = True
    elif is_acronym_of(ingested_name, matched_name) or is_acronym_of(matched_name, ingested_name):
        is_same_entity = True
        
    if not is_same_entity:
        errors.append(
            f"Abbreviation Conflation/Mismatch: Ingested '{ingested_name}' was resolved to "
            f"'{matched_name}', which is not a recognized abbreviation/acronym equivalent."
        )

    checks_passed = 0
    total_checks = 4

    # 1. CEO Name
    ingested_ceo = record.get("ceo_name", "").strip().replace(".", "").lower()
    truth_ceo    = str(truth["ceo_name"]).strip().replace(".", "").lower()
    if ingested_ceo == truth_ceo or ingested_ceo in truth_ceo or truth_ceo in ingested_ceo:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [CEO Name]: Ingested '{record.get('ceo_name')}', expected '{truth['ceo_name']}'")

    # 2. HQ Address
    ingested_hq = record.get("headquarters_address", "").strip().lower()
    truth_hq    = str(truth["headquarters_address"]).strip().lower()
    if is_hq_match(ingested_hq, truth_hq):
        checks_passed += 1
    else:
        errors.append(
            f"Mismatch [HQ Address]: Ingested '{record.get('headquarters_address')}', expected '{truth['headquarters_address']}'"
        )

    # 3. Website URL
    ingested_url = clean_url(record.get("website_url", ""))
    truth_url    = clean_url(truth["website_url"])
    if ingested_url == truth_url or ingested_url in truth_url or truth_url in ingested_url:
        checks_passed += 1
    else:
        errors.append(
            f"Mismatch [Website URL]: Ingested '{record.get('website_url')}', expected '{truth['website_url']}'"
        )

    # 4. Incorporation Year
    ingested_year = record.get("incorporation_year", "").strip()
    truth_year    = str(truth["incorporation_year"]).strip()
    if ingested_year == truth_year:
        checks_passed += 1
    else:
        errors.append(
            f"Mismatch [Incorporation Year]: Ingested '{record.get('incorporation_year')}', expected '{truth['incorporation_year']}'"
        )

    success = (len(errors) == 0 and checks_passed == total_checks)
    score   = round((checks_passed / total_checks) * 100, 2)
    return success, score, errors, matched_name


def load_csv_data(filepath: str) -> List[Dict[str, Any]]:
    """Loads a CSV file as a list of row dicts."""
    data = []
    if not os.path.exists(filepath):
        return data
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
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
    Runs abbreviation resolution validation for every profile in input_csv.
    Writes terminal table, CSV, and log reports.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV not found or empty: {input_csv}")
        return False

    report_rows = []
    log_lines   = []
    all_passed  = True

    header = (
        f"Abbreviation Handling Disambiguation Report ({engine_name}) "
        f"for {os.path.basename(input_csv)}"
    )
    log_lines.append(header)
    log_lines.append("=" * len(header))

    print(f"\nProcessing {len(dataset)} companies using {engine_name}...")
    print(f"{'Company Name':<45} | {'Matched Entity':<40} | {'Score':<6} | {'Status'}")
    print("-" * 115)

    for row in dataset:
        company_name = row.get("name", "Unknown").strip()
        success, score, errors, matched = validate_entity(row, resolver_func)
        status_str = "PASSED" if success else "FAILED"
        if not success:
            all_passed = False

        print(
            f"{company_name[:45]:<45} | {str(matched)[:40]:<40} | "
            f"{score:<5}% | {status_str}"
        )

        log_block = (
            f"Company: {company_name}\n"
            f"  Matched Entity: {matched}\n"
            f"  Status: {status_str}\n"
            f"  Match Score: {score}%\n"
        )
        if errors:
            log_block += "  Abbreviation Validation Issues:\n"
            for err in errors:
                log_block += f"    - {err}\n"
        log_block += "-" * 50
        log_lines.append(log_block)

        report_rows.append({
            "Company Name":       company_name,
            "Matched Entity":     matched,
            "Validation Status":  status_str,
            "Match Score (%)":    score,
            "Issues":             "; ".join(errors)
        })

    # Write CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Matched Entity", "Validation Status",
            "Match Score (%)", "Issues"
        ])
        writer.writeheader()
        writer.writerows(report_rows)

    # Write Log
    with open(output_log, mode="w", encoding="utf-8") as f_log:
        f_log.write("\n".join(log_lines))

    print(f"\n✓ Report saved to CSV: {output_csv}")
    print(f"✓ Report saved to Log: {output_log}")
    return all_passed


# ==============================================================================
# Automated System Test Suite
# ==============================================================================

def test_abbrev_resolver_resolves_ibm():
    """Abbreviation resolver correctly resolves acronym 'IBM' to 'International Business Machines Corporation'."""
    profile = {
        "name": "IBM",
        "short_name": "IBM",
        "ceo_name": "Arvind Krishna",
        "incorporation_year": "1911",
        "website_url": "https://www.ibm.com",
        "headquarters_address": "1 New Orchard Road, Armonk, New York, USA"
    }
    success, _, errors, matched = validate_entity(profile, abbreviation_aware_resolve)
    assert success, f"Failed: {errors}"
    assert matched == "International Business Machines Corporation ", f"Wrong match: {matched}"


def test_abbrev_resolver_resolves_att_full():
    """Abbreviation resolver resolves full 'American Telephone & Telegraph Company' to 'AT&T Inc.'."""
    profile = {
        "name": "American Telephone & Telegraph Company",
        "short_name": "AT&T",
        "ceo_name": "John Stankey",
        "incorporation_year": "1885",
        "website_url": "https://www.att.com",
        "headquarters_address": "Dallas, Texas, USA"
    }
    success, _, errors, matched = validate_entity(profile, abbreviation_aware_resolve)
    assert success, f"Failed: {errors}"
    assert matched == "AT&T Inc.", f"Wrong match: {matched}"


def test_abbrev_resolver_resolves_mmm_full():
    """Abbreviation resolver resolves full name 'Minnesota Mining and Manufacturing Company' to '3M Company'."""
    profile = {
        "name": "Minnesota Mining and Manufacturing Company",
        "short_name": "3M",
        "ceo_name": "William M. Brown",
        "incorporation_year": "1902",
        "website_url": "https://www.3m.com",
        "headquarters_address": "Maplewood, Minnesota, USA"
    }
    success, _, errors, matched = validate_entity(profile, abbreviation_aware_resolve)
    assert success, f"Failed: {errors}"
    assert matched == "3M Company", f"Wrong match: {matched}"


def test_naive_resolver_fails_ibm():
    """Naive resolver fails to resolve acronym 'IBM' to 'International Business Machines Corporation' without short name."""
    profile_no_short = {
        "name": "IBM",
        "short_name": "NA",
        "ceo_name": "Arvind Krishna",
        "incorporation_year": "1911",
        "website_url": "https://www.ibm.com",
        "headquarters_address": "1 New Orchard Road, Armonk, New York, USA"
    }
    success, _, errors, matched = validate_entity(profile_no_short, naive_resolve)
    assert not success, f"Expected naive resolver to fail, but got success with matched: {matched}"


def test_naive_resolver_fails_att_full():
    """Naive resolver fails to resolve full name 'American Telephone & Telegraph Company' without short name."""
    profile = {
        "name": "American Telephone & Telegraph Company",
        "short_name": "NA",
        "ceo_name": "John Stankey",
        "incorporation_year": "1885",
        "website_url": "https://www.att.com",
        "headquarters_address": "Dallas, Texas, USA"
    }
    success, _, errors, matched = validate_entity(profile, naive_resolve)
    assert not success, f"Expected naive resolver to fail, but got success with matched: {matched}"


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    data_csv = os.path.join(dir_path, "11.4.csv")

    completed_csv = os.path.join(dir_path, "11.4_completed_validation_results.csv")
    completed_log = os.path.join(dir_path, "11.4_completed_validation_results.log")
    naive_csv     = os.path.join(dir_path, "11.4_naive_validation_results.csv")
    naive_log     = os.path.join(dir_path, "11.4_naive_validation_results.log")

    print("=" * 96)
    print("1. ABBREVIATION-AWARE RESOLVER VALIDATION")
    print("=" * 96)
    generate_validation_report(data_csv, completed_csv, completed_log, abbreviation_aware_resolve,
                                "Abbreviation-Aware Resolver")

    print("\n" + "=" * 96)
    print("2. NAÏVE RESOLVER (DEMONSTRATING ABBREVIATION RESOLUTION FAILURES)")
    print("=" * 96)
    generate_validation_report(data_csv, naive_csv, naive_log, naive_resolve,
                                "Naïve Resolver")

    print("\n" + "=" * 96)
    print("3. CRITICAL SYSTEM TEST SUITE — ABBREVIATION HANDLING")
    print("=" * 96)

    TESTS = [
        test_abbrev_resolver_resolves_ibm,
        test_abbrev_resolver_resolves_att_full,
        test_abbrev_resolver_resolves_mmm_full,
        test_naive_resolver_fails_ibm,
        test_naive_resolver_fails_att_full,
    ]

    all_ok = True
    for test_fn in TESTS:
        try:
            test_fn()
            print(f"✓ {test_fn.__name__}: PASSED")
        except AssertionError as e:
            print(f"✗ {test_fn.__name__}: FAILED — {e}")
            all_ok = False

    print()
    if all_ok:
        print("All Abbreviation Handling validation assertions passed successfully!")
    else:
        print("One or more assertions FAILED. See details above.")
        sys.exit(1)
