import csv
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# ==============================================================================
# VERIFIED REGISTRY — Canonical ground truth per unique legal entity
# Each key is the unique legal entity name; each value carries its canonical fields.
# For geographic variants: same brand, different HQ region, regulatory regime, URL.
# ==============================================================================
VERIFIED_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Apple Inc.": {
        "short_name": "Apple",
        "ceo_name": "Tim Cook",
        "incorporation_year": "1976",
        "website_url": "https://www.apple.com",
        "headquarters_address": "One Apple Park Way, Cupertino, California, USA",
        "region": "United States",
        "parent": None
    },
    "Microsoft Corporation": {
        "short_name": "Microsoft",
        "ceo_name": "Satya Nadella",
        "incorporation_year": "1975",
        "website_url": "https://www.microsoft.com",
        "headquarters_address": "One Microsoft Way, Redmond, Washington 98052, United States",
        "region": "United States",
        "parent": None
    },
    "Barclays PLC ": {
        "short_name": "Barclays",
        "ceo_name": "C.S. Venkatakrishnan ",
        "incorporation_year": "1896",
        "website_url": "https://home.barclays/",
        "headquarters_address": "1 Churchill Place, London, E14 5HP, United Kingdom ",
        "region": "United Kingdom",
        "parent": None
    },
    "Koninklijke Philips N.V.": {
        "short_name": "Philips",
        "ceo_name": "Roy Jakobs",
        "incorporation_year": "1891",
        "website_url": "philips.com",
        "headquarters_address": "Amsterdam, Netherlands",
        "region": "Netherlands",
        "parent": None
    },
    "Citigroup Inc.": {
        "short_name": "Citi",
        "ceo_name": "Jane Fraser",
        "incorporation_year": "1812",
        "website_url": "https://www.citigroup.com",
        "headquarters_address": "New York City, New York, USA",
        "region": "United States",
        "parent": None
    },

    # Unilever — dual-heritage UK vs Netherlands entities
    "Unilever PLC": {
        "short_name": "Unilever",
        "ceo_name": "Hein Schumacher",
        "incorporation_year": "1894",
        "website_url": "https://www.unilever.com",
        "headquarters_address": "Port Sunlight, Wirral, England, United Kingdom",
        "region": "United Kingdom",
        "parent": None
    },
    "Unilever N.V.": {
        "short_name": "Unilever",
        "ceo_name": "Hein Schumacher",
        "incorporation_year": "1927",
        "website_url": "https://www.unilever.com",
        "headquarters_address": "Rotterdam, Netherlands",
        "region": "Netherlands",
        "parent": None
    },

    # Shell — UK parent vs Dutch national subsidiary
    "Shell plc": {
        "short_name": "Shell",
        "ceo_name": "Wael Sawan",
        "incorporation_year": "1907",
        "website_url": "https://www.shell.com",
        "headquarters_address": "Shell Centre, York Road, London, SE1 7NA, United Kingdom",
        "region": "United Kingdom",
        "parent": None
    },
    "Shell Nederland B.V.": {
        "short_name": "Shell",
        "ceo_name": "Marjan van Loon",
        "incorporation_year": "1907",
        "website_url": "https://www.shell.nl",
        "headquarters_address": "Carel van Bylandtlaan 30, 2596 HR The Hague, Netherlands",
        "region": "Netherlands",
        "parent": "Shell plc"
    },

    # HSBC — Global holding vs US national banking association
    "HSBC Holdings plc": {
        "short_name": "HSBC",
        "ceo_name": "Georges Elhedery",
        "incorporation_year": "1991",
        "website_url": "https://www.hsbc.com",
        "headquarters_address": "8 Canada Square, Canary Wharf, London, E14 5HQ, United Kingdom",
        "region": "United Kingdom",
        "parent": None
    },
    "HSBC Bank USA, N.A.": {
        "short_name": "HSBC",
        "ceo_name": "Michael Roberts",
        "incorporation_year": "1850",
        "website_url": "https://www.us.hsbc.com",
        "headquarters_address": "452 Fifth Avenue, New York, NY 10018, United States",
        "region": "United States",
        "parent": "HSBC Holdings plc"
    }
}


def clean_url(url: str) -> str:
    """Helper to normalize URLs for comparison by stripping protocols, www, and trailing slashes."""
    if not url:
        return ""
    url = url.strip().lower()
    if url.startswith("https://"):
        url = url[8:]
    elif url.startswith("http://"):
        url = url[7:]
    if url.startswith("www."):
        url = url[4:]
    return url.rstrip("/")


def geo_aware_resolve(record: Dict[str, Any]) -> Optional[str]:
    """
    Geographic-Aware Resolver.
    Resolves a company profile to the correct legal entity using a multi-factor scoring approach:
      - exact/substring name match
      - exact/substring website URL match (normalized)
      - exact incorporation year match
      - region keyword match in headquarters address
      - exact/substring CEO name match
    Correctly separates regional variants that share a brand name or website domain.
    """
    ingested_name  = record.get("name", "").strip().lower()
    ingested_short = record.get("short_name", "").strip().lower()
    ingested_url   = clean_url(record.get("website_url", ""))
    ingested_hq    = record.get("headquarters_address", "").strip().lower()
    ingested_year  = record.get("incorporation_year", "").strip()
    ingested_ceo   = record.get("ceo_name", "").strip().replace(".", "").lower()

    region_keywords = {
        "United Kingdom": ["united kingdom", "england", "london", "uk", "wirral", "port sunlight"],
        "Netherlands":    ["netherlands", "rotterdam", "amsterdam", "the hague", "hague", "nederland"],
        "United States":  ["united states", "usa", "new york", "seattle", "cupertino", "us"],
    }
    detected_region = None
    for region, kws in region_keywords.items():
        if any(kw in ingested_hq for kw in kws):
            detected_region = region
            break

    best_candidate = None
    best_score = -1

    for reg_name, truth in VERIFIED_REGISTRY.items():
        score = 0
        
        # 1. Name Match
        reg_name_clean = reg_name.strip().lower()
        if ingested_name == reg_name_clean:
            score += 50
        elif ingested_name in reg_name_clean or reg_name_clean in ingested_name:
            score += 20

        # 2. Short Name Match
        truth_short = truth["short_name"].strip().lower()
        if ingested_short == truth_short:
            score += 20

        # 3. URL Match (Cleaned)
        truth_url = clean_url(truth["website_url"])
        if ingested_url and truth_url:
            if ingested_url == truth_url:
                score += 40
            elif ingested_url in truth_url or truth_url in ingested_url:
                score += 15

        # 4. Incorporation Year Match
        if ingested_year and ingested_year == str(truth["incorporation_year"]).strip():
            score += 30

        # 5. Region/HQ Match
        truth_region = truth.get("region")
        if detected_region and truth_region == detected_region:
            score += 30
        
        truth_hq = truth["headquarters_address"].strip().lower()
        if ingested_hq and truth_hq:
            if truth_hq in ingested_hq or ingested_hq in truth_hq:
                score += 20

        # 6. CEO Match
        truth_ceo = truth["ceo_name"].strip().replace(".", "").lower()
        if ingested_ceo and truth_ceo:
            if ingested_ceo == truth_ceo or ingested_ceo in truth_ceo or truth_ceo in ingested_ceo:
                score += 20

        if score > best_score:
            best_score = score
            best_candidate = reg_name

    return best_candidate


def naive_geo_resolve(record: Dict[str, Any]) -> Optional[str]:
    """
    Naïve Geographic Resolver.
    Matches only on brand short_name or name substring, returning the first registry match
    without region-aware verification — causing conflation of regional entities.
    """
    ingested_short = record.get("short_name", "").strip().lower()
    ingested_name  = record.get("name", "").strip().lower()

    # Returns the first matching entity in the registry
    for reg_name, truth in VERIFIED_REGISTRY.items():
        truth_short = truth["short_name"].lower()
        if ingested_short == truth_short or truth_short in ingested_name:
            return reg_name

    return None


def validate_entity(
    record: Dict[str, Any],
    resolver_func
) -> Tuple[bool, float, List[str], Optional[str]]:
    """
    Validates a company profile against the verified registry using the given resolver.
    Detects geographic conflation (same brand, wrong region resolved).

    Returns: (success, accuracy_score, error_list, matched_entity_name)
    """
    errors = []
    ingested_name  = record.get("name", "").strip()

    matched_name = resolver_func(record)
    if not matched_name:
        return False, 0.0, [
            f"Resolution Error: Could not resolve '{ingested_name}' to any registered entity."
        ], None

    truth = VERIFIED_REGISTRY[matched_name]

    # Geographic conflation check
    if matched_name.strip().lower() != ingested_name.strip().lower():
        truth_for_ingested = VERIFIED_REGISTRY.get(ingested_name)
        if not truth_for_ingested:
            # Try to lookup with trailing space or other variations
            for k, v in VERIFIED_REGISTRY.items():
                if k.strip().lower() == ingested_name.lower():
                    truth_for_ingested = v
                    break
        if truth_for_ingested is not None:
            # Same brand, different region → conflation
            if (truth_for_ingested.get("short_name", "").lower() == truth.get("short_name", "").lower() and
                    truth_for_ingested.get("region") != truth.get("region")):
                errors.append(
                    f"Geographic Conflation: '{ingested_name}' (region: "
                    f"{truth_for_ingested.get('region', '?')}) was incorrectly resolved to "
                    f"'{matched_name}' (region: {truth.get('region', '?')})."
                )

    checks_passed = 0
    total_checks  = 4

    # 1. CEO Name
    ingested_ceo = record.get("ceo_name", "").strip().replace(".", "").lower()
    truth_ceo    = str(truth["ceo_name"]).strip().replace(".", "").lower()
    if ingested_ceo == truth_ceo or ingested_ceo in truth_ceo or truth_ceo in ingested_ceo:
        checks_passed += 1
    else:
        errors.append(f"Mismatch [CEO Name]: Ingested '{record.get('ceo_name')}', expected '{truth['ceo_name']}'")

    # 2. HQ Address (substring)
    ingested_hq = record.get("headquarters_address", "").strip().lower()
    truth_hq    = str(truth["headquarters_address"]).strip().lower()
    if truth_hq in ingested_hq or ingested_hq in truth_hq:
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
    Runs geographic variant validation for every profile in input_csv.
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
        f"Geographic Variant Disambiguation Report ({engine_name}) "
        f"for {os.path.basename(input_csv)}"
    )
    log_lines.append(header)
    log_lines.append("=" * len(header))

    print(f"\nProcessing {len(dataset)} companies using {engine_name}...")
    print(f"{'Company Name':<42} | {'Matched Entity':<32} | {'Score':<6} | {'Status'}")
    print("-" * 106)

    for row in dataset:
        company_name = row.get("name", "Unknown").strip()
        success, score, errors, matched = validate_entity(row, resolver_func)
        status_str = "PASSED" if success else "CONFLATED/FAILED"
        if not success:
            all_passed = False

        print(
            f"{company_name[:42]:<42} | {str(matched)[:32]:<32} | "
            f"{score:<5}% | {status_str}"
        )

        log_block = (
            f"Company: {company_name}\n"
            f"  Matched Entity: {matched}\n"
            f"  Status: {status_str}\n"
            f"  Match Score: {score}%\n"
        )
        if errors:
            log_block += "  Geographic Variant Validation Issues:\n"
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

def _make_profile(name: str) -> Dict[str, Any]:
    """Constructs a profile dict from the VERIFIED_REGISTRY for a given entity name."""
    t = VERIFIED_REGISTRY[name]
    return {
        "name":                  name,
        "short_name":            t["short_name"],
        "ceo_name":              t["ceo_name"],
        "incorporation_year":    t["incorporation_year"],
        "website_url":           t["website_url"],
        "headquarters_address":  t["headquarters_address"]
    }


def test_geo_aware_resolves_unilever_plc():
    """Geo-aware resolver correctly identifies UK entity by HQ address."""
    profile = _make_profile("Unilever PLC")
    success, _, errors, matched = validate_entity(profile, geo_aware_resolve)
    assert success, f"Failed: {errors}"
    assert matched == "Unilever PLC", f"Wrong match: {matched}"


def test_geo_aware_resolves_unilever_nv():
    """Geo-aware resolver correctly identifies Netherlands entity by HQ address."""
    profile = _make_profile("Unilever N.V.")
    success, _, errors, matched = validate_entity(profile, geo_aware_resolve)
    assert success, f"Failed: {errors}"
    assert matched == "Unilever N.V.", f"Wrong match: {matched}"


def test_geo_aware_resolves_shell_plc():
    """Geo-aware resolver correctly identifies Shell plc via website URL."""
    profile = _make_profile("Shell plc")
    success, _, errors, matched = validate_entity(profile, geo_aware_resolve)
    assert success, f"Failed: {errors}"
    assert matched == "Shell plc", f"Wrong match: {matched}"


def test_geo_aware_resolves_shell_nederland():
    """Geo-aware resolver correctly identifies Shell Nederland via distinct URL."""
    profile = _make_profile("Shell Nederland B.V.")
    success, _, errors, matched = validate_entity(profile, geo_aware_resolve)
    assert success, f"Failed: {errors}"
    assert matched == "Shell Nederland B.V.", f"Wrong match: {matched}"


def test_geo_aware_resolves_hsbc_holdings():
    """Geo-aware resolver correctly identifies HSBC Holdings plc via URL."""
    profile = _make_profile("HSBC Holdings plc")
    success, _, errors, matched = validate_entity(profile, geo_aware_resolve)
    assert success, f"Failed: {errors}"
    assert matched == "HSBC Holdings plc", f"Wrong match: {matched}"


def test_geo_aware_resolves_hsbc_usa():
    """Geo-aware resolver correctly identifies HSBC USA entity via US-regional URL."""
    profile = _make_profile("HSBC Bank USA, N.A.")
    success, _, errors, matched = validate_entity(profile, geo_aware_resolve)
    assert success, f"Failed: {errors}"
    assert matched == "HSBC Bank USA, N.A.", f"Wrong match: {matched}"


def test_naive_resolver_conflates_unilever_nv():
    """Naive resolver conflates Unilever N.V. (Netherlands) to Unilever PLC (UK)."""
    profile = _make_profile("Unilever N.V.")
    success, _, errors, matched = validate_entity(profile, naive_geo_resolve)
    assert not success, "Expected CONFLATED/FAILED but got PASSED"
    assert any("Conflation" in err for err in errors), f"No conflation error raised: {errors}"


def test_naive_resolver_conflates_hsbc_usa():
    """Naive resolver conflates HSBC USA to HSBC Holdings plc (UK)."""
    profile = _make_profile("HSBC Bank USA, N.A.")
    success, _, errors, matched = validate_entity(profile, naive_geo_resolve)
    assert not success, "Expected CONFLATED/FAILED but got PASSED"
    assert any("Conflation" in err for err in errors), f"No conflation error raised: {errors}"


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    data_csv = os.path.join(dir_path, "11.3.csv")

    geo_csv  = os.path.join(dir_path, "11.3_completed_validation_results.csv")
    geo_log  = os.path.join(dir_path, "11.3_completed_validation_results.log")
    naive_csv = os.path.join(dir_path, "11.3_naive_validation_results.csv")
    naive_log = os.path.join(dir_path, "11.3_naive_validation_results.log")

    print("=" * 96)
    print("1. GEOGRAPHIC-AWARE RESOLVER VALIDATION")
    print("=" * 96)
    generate_validation_report(data_csv, geo_csv, geo_log, geo_aware_resolve,
                                "Geographic-Aware Resolver")

    print("\n" + "=" * 96)
    print("2. NAÏVE RESOLVER (DEMONSTRATING GEOGRAPHIC CONFLATION)")
    print("=" * 96)
    generate_validation_report(data_csv, naive_csv, naive_log, naive_geo_resolve,
                                "Naïve Geographic Resolver")

    print("\n" + "=" * 96)
    print("3. CRITICAL SYSTEM TEST SUITE — GEOGRAPHIC VARIANT DISAMBIGUATION")
    print("=" * 96)

    TESTS = [
        test_geo_aware_resolves_unilever_plc,
        test_geo_aware_resolves_unilever_nv,
        test_geo_aware_resolves_shell_plc,
        test_geo_aware_resolves_shell_nederland,
        test_geo_aware_resolves_hsbc_holdings,
        test_geo_aware_resolves_hsbc_usa,
        test_naive_resolver_conflates_unilever_nv,
        test_naive_resolver_conflates_hsbc_usa,
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
        print("All Geographic Variant disambiguation assertions passed successfully!")
    else:
        print("One or more assertions FAILED. See details above.")
        sys.exit(1)
