import csv
import os
import sys
from typing import Dict, Any, Tuple, List, Optional

# Verified registry — each entry is a unique legal entity with its canonical fields
VERIFIED_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Apple Inc.": {
        "short_name": "Apple",
        "ceo_name": "Tim Cook",
        "incorporation_year": "1976",
        "website_url": "https://www.apple.com",
        "headquarters_address": "One Apple Park Way, Cupertino, California, USA",
        "parent": None
    },
    "Microsoft Corporation": {
        "short_name": "Microsoft",
        "ceo_name": "Satya Nadella",
        "incorporation_year": "1975",
        "website_url": "https://www.microsoft.com",
        "headquarters_address": "One Microsoft Way, Redmond, Washington 98052, United States",
        "parent": None
    },
    "Google LLC (Subsidiary of Alphabet Inc.)": {
        "short_name": "Google",
        "ceo_name": "Sundar Pichai",
        "incorporation_year": "1998",
        "website_url": "https://www.google.com",
        "headquarters_address": "1600 Amphitheatre Parkway, Mountain View, California, USA",
        "parent": "Alphabet Inc."
    },
    "Accenture plc": {
        "short_name": "Accenture",
        "ceo_name": "Julie Sweet",
        "incorporation_year": "1989",
        "website_url": "https://www.accenture.com",
        "headquarters_address": "Dublin, Ireland",
        "parent": None
    },
    "Amazon.com, Inc.": {
        "short_name": "Amazon",
        "ceo_name": "Andy Jassy",
        "incorporation_year": "1994",
        "website_url": "https://www.amazon.com/",
        "headquarters_address": "410 Terry Ave N, Seattle, WA 98109, United States",
        "parent": None
    },
    "Tata Consultancy Services Limited": {
        "short_name": "TCS",
        "ceo_name": "K. Krithivasan",
        "incorporation_year": "1968",
        "website_url": "https://www.tcs.com",
        "headquarters_address": "Mumbai, Maharashtra, India",
        "parent": None
    },
    "Infosys Limited": {
        "short_name": "Infosys",
        "ceo_name": "Salil Parekh",
        "incorporation_year": "1981",
        "website_url": "https://www.infosys.com",
        "headquarters_address": "Bangalore, Karnataka, India",
        "parent": None
    },
    "Alphabet Inc.": {
        "short_name": "Alphabet",
        "ceo_name": "Sundar Pichai",
        "incorporation_year": "2015",
        "website_url": "https://abc.xyz",
        "headquarters_address": "1600 Amphitheatre Parkway, Mountain View, California, USA",
        "parent": None
    },
    "YouTube, LLC": {
        "short_name": "YouTube",
        "ceo_name": "Neal Mohan",
        "incorporation_year": "2005",
        "website_url": "https://www.youtube.com",
        "headquarters_address": "901 Cherry Ave, San Bruno, California, USA",
        "parent": "Alphabet Inc."
    },
    "Meta Platforms, Inc.": {
        "short_name": "Meta",
        "ceo_name": "Mark Zuckerberg",
        "incorporation_year": "2004",
        "website_url": "https://about.meta.com",
        "headquarters_address": "1 Hacker Way, Menlo Park, California, USA",
        "parent": None
    },
    "Instagram, LLC": {
        "short_name": "Instagram",
        "ceo_name": "Adam Mosseri",
        "incorporation_year": "2010",
        "website_url": "https://www.instagram.com",
        "headquarters_address": "1601 Willow Road, Menlo Park, California, USA",
        "parent": "Meta Platforms, Inc."
    }
}

# Map of short names to their parent companies for the naive conflation resolver
PARENT_MAP = {
    "google": "Alphabet Inc.",
    "youtube": "Alphabet Inc.",
    "instagram": "Meta Platforms, Inc.",
    "whatsapp": "Meta Platforms, Inc."
}


def strict_resolve(record: Dict[str, Any]) -> Optional[str]:
    """
    Strict Parent-Subsidiary Resolver.
    Uses website_url (primary), then short_name + incorporation_year to pinpoint the
    exact registered entity, correctly separating subsidiaries from their parents.
    """
    ingested_url = record.get("website_url", "").strip().rstrip("/")
    ingested_short = record.get("short_name", "").strip().lower()
    ingested_year = record.get("incorporation_year", "").strip()

    # First: try exact website URL match (strongest signal)
    for reg_name, truth in VERIFIED_REGISTRY.items():
        if ingested_url == truth["website_url"].rstrip("/"):
            return reg_name

    # Second: match by short name + year combination
    for reg_name, truth in VERIFIED_REGISTRY.items():
        if (ingested_short == truth["short_name"].lower() and
                ingested_year == truth["incorporation_year"]):
            return reg_name

    # Third: broad short name partial match (fallback)
    for reg_name, truth in VERIFIED_REGISTRY.items():
        if ingested_short and ingested_short in truth["short_name"].lower():
            return reg_name

    return None


def naive_resolve(record: Dict[str, Any]) -> Optional[str]:
    """
    Naïve Parent-Subsidiary Resolver.
    Matches on shared keyword in name or short_name, always collapsing
    subsidiaries to their parent entity — demonstrating conflation failures.
    """
    name_q = record.get("name", "").strip().lower()
    short_q = record.get("short_name", "").strip().lower()

    # Check PARENT_MAP (subsidiaries get collapsed to parent)
    for kw, parent in PARENT_MAP.items():
        if kw in name_q or kw in short_q:
            return parent

    # For all others: simple direct name lookup
    for reg_name in VERIFIED_REGISTRY:
        if name_q in reg_name.lower():
            return reg_name

    return None


def validate_entity(record: Dict[str, Any], resolver_func) -> Tuple[bool, float, List[str], Optional[str]]:
    """
    Validates a company record against the verified registry using the specified resolver.
    Detects parent/subsidiary conflation when a subsidiary is matched to its parent entity.

    Returns: (success, score, errors, matched_entity_name)
    """
    errors = []
    ingested_name = record.get("name", "").strip()
    ingested_short = record.get("short_name", "").strip()

    matched_name = resolver_func(record)
    if not matched_name:
        return False, 0.0, [
            f"Resolution Error: Could not resolve '{ingested_name}' to any registered entity."
        ], None

    # Conflation detection: check if the matched entity is the parent of the ingested entity
    # This fires when a naive resolver maps a subsidiary to its parent
    is_subsidiary = ingested_name.lower() != matched_name.lower()
    if is_subsidiary:
        truth_for_ingested = next(
            (t for n, t in VERIFIED_REGISTRY.items() if n.lower() == ingested_name.lower()),
            None
        )
        matched_truth = VERIFIED_REGISTRY.get(matched_name, {})
        # Only flag conflation if matched entity is a parent of the ingested one
        ingested_is_known_sub = (
            truth_for_ingested is not None and
            truth_for_ingested.get("parent") == matched_name
        )
        if ingested_is_known_sub:
            errors.append(
                f"Conflation Failure: Subsidiary record '{ingested_short}' was incorrectly "
                f"matched to parent '{matched_name}'."
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

    # 2. HQ address check (substring)
    ingested_hq = record.get("headquarters_address", "").strip()
    truth_hq = truth["headquarters_address"].strip()
    if truth_hq.lower() in ingested_hq.lower() or ingested_hq.lower() in truth_hq.lower():
        checks_passed += 1
    else:
        errors.append(
            f"Mismatch [Headquarters Address]: Ingested '{ingested_hq}', expected '{truth_hq}'"
        )

    # 3. Website URL check
    ingested_url = record.get("website_url", "").strip().rstrip("/")
    truth_url = truth["website_url"].strip().rstrip("/")
    if ingested_url == truth_url:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [Website URL]: Ingested '{ingested_url}', expected '{truth_url}'")

    # 4. Incorporation year check
    ingested_year = record.get("incorporation_year", "").strip()
    truth_year = truth["incorporation_year"]
    if ingested_year == truth_year:
        checks_passed += 1
    else:
        errors.append(
            f"Mismatch [Year of Incorporation]: Ingested '{ingested_year}', expected '{truth_year}'"
        )

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
    Validates all profiles in the input CSV for parent/subsidiary conflation.
    Prints real-time results to the terminal.
    Saves detailed reports to CSV and log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return False

    report_rows = []
    log_lines = []
    all_passed = True

    log_lines.append(
        f"Parent/Subsidiary Disambiguation Report ({engine_name}) for {os.path.basename(input_csv)}"
    )
    log_lines.append("=" * 96)

    print(f"\nProcessing {len(dataset)} companies using {engine_name}...")
    print(f"{'Company Name':<40} | {'Matched Entity':<35} | {'Score':<6} | {'Status':<15}")
    print("-" * 105)

    for row in dataset:
        company_name = row.get("name", "Unknown Company").strip()

        success, score, errors, matched_name = validate_entity(row, resolver_func)
        status_str = "PASSED" if success else "CONFLATED/FAILED"
        if not success:
            all_passed = False

        print(f"{company_name[:40]:<40} | {str(matched_name)[:35]:<35} | {score:<5}% | {status_str:<15}")

        # Build log entry
        log_line = (
            f"Company: {company_name}\n"
            f"  Matched Entity: {matched_name}\n"
            f"  Status: {status_str}\n"
            f"  Match Score: {score}%\n"
        )
        if errors:
            log_line += "  Parent/Subsidiary Validation Issues:\n"
            for err in errors:
                log_line += f"    - {err}\n"
        log_line += "-" * 50
        log_lines.append(log_line)

        report_rows.append({
            "Company Name": company_name,
            "Matched Entity": matched_name,
            "Validation Status": status_str,
            "Match Score (%)": score,
            "Issues": "; ".join(errors)
        })

    # Write to CSV
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

def test_strict_resolver_separates_google_from_alphabet():
    """Strict resolver must correctly identify Google LLC, not Alphabet Inc."""
    profile = {
        "name": "Google LLC (Subsidiary of Alphabet Inc.)",
        "short_name": "Google",
        "ceo_name": "Sundar Pichai",
        "incorporation_year": "1998",
        "website_url": "https://www.google.com",
        "headquarters_address": "1600 Amphitheatre Parkway, Mountain View, California, USA"
    }
    success, score, errors, matched = validate_entity(profile, strict_resolve)
    assert success is True, f"Failed: {errors}"
    assert matched == "Google LLC (Subsidiary of Alphabet Inc.)"


def test_strict_resolver_separates_youtube_from_alphabet():
    """Strict resolver must correctly identify YouTube, LLC, not Alphabet Inc."""
    profile = {
        "name": "YouTube, LLC",
        "short_name": "YouTube",
        "ceo_name": "Neal Mohan",
        "incorporation_year": "2005",
        "website_url": "https://www.youtube.com",
        "headquarters_address": "901 Cherry Ave, San Bruno, California, USA"
    }
    success, score, errors, matched = validate_entity(profile, strict_resolve)
    assert success is True, f"Failed: {errors}"
    assert matched == "YouTube, LLC"


def test_strict_resolver_separates_instagram_from_meta():
    """Strict resolver must correctly identify Instagram, LLC, not Meta Platforms."""
    profile = {
        "name": "Instagram, LLC",
        "short_name": "Instagram",
        "ceo_name": "Adam Mosseri",
        "incorporation_year": "2010",
        "website_url": "https://www.instagram.com",
        "headquarters_address": "1601 Willow Road, Menlo Park, California, USA"
    }
    success, score, errors, matched = validate_entity(profile, strict_resolve)
    assert success is True, f"Failed: {errors}"
    assert matched == "Instagram, LLC"


def test_naive_resolver_conflates_youtube_to_alphabet():
    """Naive resolver collapses YouTube to Alphabet Inc. — demonstrating conflation."""
    profile = {
        "name": "YouTube, LLC",
        "short_name": "YouTube",
        "ceo_name": "Neal Mohan",
        "incorporation_year": "2005",
        "website_url": "https://www.youtube.com",
        "headquarters_address": "901 Cherry Ave, San Bruno, California, USA"
    }
    success, score, errors, matched = validate_entity(profile, naive_resolve)
    assert success is False
    assert matched == "Alphabet Inc."
    assert any("Conflation Failure" in err for err in errors)


def test_naive_resolver_conflates_instagram_to_meta():
    """Naive resolver collapses Instagram to Meta Platforms — demonstrating conflation."""
    profile = {
        "name": "Instagram, LLC",
        "short_name": "Instagram",
        "ceo_name": "Adam Mosseri",
        "incorporation_year": "2010",
        "website_url": "https://www.instagram.com",
        "headquarters_address": "1601 Willow Road, Menlo Park, California, USA"
    }
    success, score, errors, matched = validate_entity(profile, naive_resolve)
    assert success is False
    assert matched == "Meta Platforms, Inc."
    assert any("Conflation Failure" in err for err in errors)


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    completed_csv_path = os.path.join(dir_path, "11.2.csv")

    strict_out_csv = os.path.join(dir_path, "11.2_completed_validation_results.csv")
    strict_out_log = os.path.join(dir_path, "11.2_completed_validation_results.log")

    naive_out_csv = os.path.join(dir_path, "11.2_naive_validation_results.csv")
    naive_out_log = os.path.join(dir_path, "11.2_naive_validation_results.log")

    print("=" * 96)
    print("1. RUNNING STRICT PARENT-SUBSIDIARY RESOLVER VALIDATION")
    print("=" * 96)
    generate_validation_report(
        completed_csv_path, strict_out_csv, strict_out_log,
        strict_resolve, "Strict Parent-Subsidiary Resolver"
    )

    print("\n" + "=" * 96)
    print("2. RUNNING NAÏVE PARENT-SUBSIDIARY RESOLVER (DEMONSTRATING CONFLATION)")
    print("=" * 96)
    generate_validation_report(
        completed_csv_path, naive_out_csv, naive_out_log,
        naive_resolve, "Naïve Parent-Subsidiary Resolver"
    )

    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL SYSTEM CONFLATION TEST SUITE")
    print("=" * 96)

    try:
        test_strict_resolver_separates_google_from_alphabet()
        print("✓ test_strict_resolver_separates_google_from_alphabet: PASSED")
        test_strict_resolver_separates_youtube_from_alphabet()
        print("✓ test_strict_resolver_separates_youtube_from_alphabet: PASSED")
        test_strict_resolver_separates_instagram_from_meta()
        print("✓ test_strict_resolver_separates_instagram_from_meta: PASSED")
        test_naive_resolver_conflates_youtube_to_alphabet()
        print("✓ test_naive_resolver_conflates_youtube_to_alphabet: PASSED")
        test_naive_resolver_conflates_instagram_to_meta()
        print("✓ test_naive_resolver_conflates_instagram_to_meta: PASSED")
        print("\nAll Parent/Subsidiary Conflation verification assertions passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical conflation test assertion failed:", e)
        sys.exit(1)
