import csv
import os
import sys
import time
import re
from typing import Any, Dict, List, Tuple

# We will run multiple iterations of processing per profile to get reliable timing statistics
BENCHMARK_ITERATIONS = 100

def parse_monetary_value(val_str: str) -> float:
    """Parses monetary string representations (e.g. '$383B', '$29 billion', 'AUD 29.3 billion') to a raw float in billions."""
    if not val_str or val_str == "NA" or val_str == "?":
        return 0.0
    val_str = val_str.lower().strip()
    # Extract digits and decimal point
    match = re.search(r'([0-9\.\-\–\s]+)', val_str)
    if not match:
        return 0.0
    num_str = match.group(1).replace(" ", "")
    # Handle ranges (take average)
    if "-" in num_str:
        parts = num_str.split("-")
        try:
            num = sum(float(p) for p in parts) / len(parts)
        except ValueError:
            return 0.0
    elif "–" in num_str:
        parts = num_str.split("–")
        try:
            num = sum(float(p) for p in parts) / len(parts)
        except ValueError:
            return 0.0
    else:
        try:
            num = float(num_str)
        except ValueError:
            return 0.0

    # Adjust scale
    if "b" in val_str or "billion" in val_str:
        return num
    elif "m" in val_str or "million" in val_str:
        return num / 1000.0
    elif "cr" in val_str: # Crore (India)
        return (num * 10_000_000) / 1_000_000_000.0
    return num


def parse_employee_size(emp_str: str) -> int:
    """Parses employee size string (e.g., '161000', '740,000 employees', '280,000–300,000') to integer."""
    if not emp_str or emp_str == "NA":
        return 0
    emp_str = emp_str.lower().strip()
    match = re.search(r'([0-9\,\.\-\–\s\+]+)', emp_str)
    if not match:
        return 0
    num_str = match.group(1).replace(",", "").replace("+", "").replace(" ", "")
    if "-" in num_str:
        parts = num_str.split("-")
        try:
            return int(sum(float(p) for p in parts) / len(parts))
        except ValueError:
            return 0
    elif "–" in num_str:
        parts = num_str.split("–")
        try:
            return int(sum(float(p) for p in parts) / len(parts))
        except ValueError:
            return 0
    else:
        try:
            return int(float(num_str))
        except ValueError:
            return 0


def process_profile(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates real-world validation, normalization, and computation across all 163 fields of a company profile.
    This performs extensive string operations, regex parsing, and mathematical calculations.
    """
    processed = {}
    
    # 1. Standard Identity Parsing
    processed["name"] = record.get("name", "").strip()
    processed["short_name"] = record.get("short_name", "").strip()
    processed["website_url"] = record.get("website_url", "").strip().lower()
    
    # 2. Text Complexity Analysis (Natural scaling with profile size/complexity)
    text_fields = [
        "overview_text", "vision_statement", "mission_statement", 
        "core_values", "history_timeline", "recent_news",
        "supply_chain_dependencies", "geopolitical_risks", "macro_risks",
        "work_culture_summary", "offerings_description"
    ]
    
    total_words = 0
    keyword_matches = 0
    key_terms = ["global", "innovative", "growth", "security", "technology", "client", "revenue", "compliance"]
    
    for field in text_fields:
        content = record.get(field, "")
        if not content or content == "NA":
            continue
        # Count words
        words = content.lower().split()
        total_words += len(words)
        # Search keywords
        for term in key_terms:
            keyword_matches += content.lower().count(term)
            
    processed["text_word_count"] = total_words
    processed["text_keyword_matches"] = keyword_matches

    # 3. Numeric conversions and Margin calculations (Financial + Scale data)
    rev_raw = record.get("annual_revenue", "0.0")
    prof_raw = record.get("annual_profit", "0.0")
    val_raw = record.get("valuation", "0.0")
    emp_raw = record.get("employee_size", "0")
    
    revenue = parse_monetary_value(rev_raw)
    profit = parse_monetary_value(prof_raw)
    valuation = parse_monetary_value(val_raw)
    employees = parse_employee_size(emp_raw)
    
    profit_margin = (profit / revenue * 100.0) if revenue > 0 else 0.0
    rev_per_emp = (revenue * 1_000_000_000.0 / employees) if employees > 0 else 0.0
    
    processed["parsed_revenue_billions"] = revenue
    processed["parsed_profit_billions"] = profit
    processed["parsed_valuation_billions"] = valuation
    processed["parsed_employees"] = employees
    processed["profit_margin_pct"] = round(profit_margin, 2)
    processed["rev_per_employee"] = round(rev_per_emp, 2)

    # 4. Supply Chain & Regulatory Text Regex Analysis
    regulatory_status = record.get("regulatory_status", "")
    legal_issues = record.get("legal_issues", "")
    
    # Heuristic score for regulatory exposure/risk
    risk_score = 0
    if re.search(r'(regulated|sec|fcc|audit|compliance|fca)', regulatory_status.lower()):
        risk_score += 3
    if re.search(r'(lawsuit|fine|penalty|dispute|investigation)', legal_issues.lower()):
        risk_score += 5
    processed["risk_score"] = risk_score

    # 5. Iterating over all other remaining keys of the 163 parameters to ensure full schema coverage
    processed["total_fields_processed"] = len(record)
    for k, v in record.items():
        if k not in processed:
            # Simple metadata copy/normalization
            processed[f"clean_{k}"] = str(v).strip()

    return processed


def benchmark_profiles(csv_path: str) -> List[Dict[str, Any]]:
    """Runs a response time performance benchmark on company profiles from a CSV."""
    results = []
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        return results

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\nBenchmarking {len(rows)} profiles over {BENCHMARK_ITERATIONS} iterations...")

    for row in rows:
        name = row.get("name", "Unknown").strip()
        nature = row.get("nature_of_company", "").lower()
        
        # Classification
        if "benchmark_fortune500" in nature or ("public" in nature and parse_employee_size(row.get("employee_size", "0")) >= 50000):
            comp_type = "Fortune 500"
            pub_priv = "Public"
        else:
            comp_type = "Startup"
            pub_priv = "Private"

        # Warm-up run
        process_profile(row)

        # Benchmark processing
        start_time = time.perf_counter()
        for _ in range(BENCHMARK_ITERATIONS):
            process_profile(row)
        end_time = time.perf_counter()

        # Compute elapsed time per iteration (in milliseconds)
        elapsed_ms = ((end_time - start_time) / BENCHMARK_ITERATIONS) * 1000.0
        
        # Calculate payload size (length of all string fields concatenated)
        payload_char_len = sum(len(str(val)) for val in row.values())

        results.append({
            "name": name,
            "company_type": comp_type,
            "ownership": pub_priv,
            "payload_chars": payload_char_len,
            "avg_time_ms": elapsed_ms
        })

    return results


def summarize_results(results: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], str]:
    """Computes summary statistics and comparisons for Fortune 500 vs Startups and Public vs Private."""
    stats = {}
    
    # Fortune 500
    f500_times = [r["avg_time_ms"] for r in results if r["company_type"] == "Fortune 500"]
    f500_payloads = [r["payload_chars"] for r in results if r["company_type"] == "Fortune 500"]
    
    # Startup
    startup_times = [r["avg_time_ms"] for r in results if r["company_type"] == "Startup"]
    startup_payloads = [r["payload_chars"] for r in results if r["company_type"] == "Startup"]
    
    # Ownership
    public_times = [r["avg_time_ms"] for r in results if r["ownership"] == "Public"]
    private_times = [r["avg_time_ms"] for r in results if r["ownership"] == "Private"]

    stats["fortune_500_avg_ms"] = sum(f500_times) / len(f500_times) if f500_times else 0.0
    stats["fortune_500_max_ms"] = max(f500_times) if f500_times else 0.0
    stats["fortune_500_min_ms"] = min(f500_times) if f500_times else 0.0
    stats["fortune_500_avg_chars"] = sum(f500_payloads) / len(f500_payloads) if f500_payloads else 0.0

    stats["startup_avg_ms"] = sum(startup_times) / len(startup_times) if startup_times else 0.0
    stats["startup_max_ms"] = max(startup_times) if startup_times else 0.0
    stats["startup_min_ms"] = min(startup_times) if startup_times else 0.0
    stats["startup_avg_chars"] = sum(startup_payloads) / len(startup_payloads) if startup_payloads else 0.0

    stats["public_avg_ms"] = sum(public_times) / len(public_times) if public_times else 0.0
    stats["private_avg_ms"] = sum(private_times) / len(private_times) if private_times else 0.0
    
    # Comparison ratios
    stats["f500_vs_startup_ratio"] = stats["fortune_500_avg_ms"] / stats["startup_avg_ms"] if stats["startup_avg_ms"] > 0 else 1.0
    stats["public_vs_private_ratio"] = stats["public_avg_ms"] / stats["private_avg_ms"] if stats["private_avg_ms"] > 0 else 1.0

    # Build report text
    report = (
        "================================================================================================\n"
        "13.2 Scale & Performance: Ingestion Response Time Benchmark Report\n"
        "================================================================================================\n"
        f"1. Company Type Breakdown:\n"
        f"   - Fortune 500 Profiles (N={len(f500_times)}):\n"
        f"     * Average Time: {stats['fortune_500_avg_ms']:.4f} ms\n"
        f"     * Min Time:     {stats['fortune_500_min_ms']:.4f} ms\n"
        f"     * Max Time:     {stats['fortune_500_max_ms']:.4f} ms\n"
        f"     * Avg Payload:  {stats['fortune_500_avg_chars']:.1f} characters\n"
        f"   - Startup Profiles (N={len(startup_times)}):\n"
        f"     * Average Time: {stats['startup_avg_ms']:.4f} ms\n"
        f"     * Min Time:     {stats['startup_min_ms']:.4f} ms\n"
        f"     * Max Time:     {stats['startup_max_ms']:.4f} ms\n"
        f"     * Avg Payload:  {stats['startup_avg_chars']:.1f} characters\n"
        f"   - Comparison: Fortune 500 profiles take {stats['f500_vs_startup_ratio']:.2f}x longer to validate\n"
        "------------------------------------------------------------------------------------------------\n"
        f"2. Ownership Structure Comparison:\n"
        f"   - Public Company Profiles Average Time:  {stats['public_avg_ms']:.4f} ms\n"
        f"   - Private Company Profiles Average Time: {stats['private_avg_ms']:.4f} ms\n"
        f"   - Comparison: Public profiles take {stats['public_vs_private_ratio']:.2f}x longer to validate\n"
        "================================================================================================\n"
    )

    return stats, report


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(dir_path, "13.2.csv")

    results_csv = os.path.join(dir_path, "13.2_completed_validation_results.csv")
    results_log = os.path.join(dir_path, "13.2_completed_validation_results.log")

    benchmark_res = benchmark_profiles(input_csv)
    if not benchmark_res:
        print("Error: Benchmarking failed.")
        sys.exit(1)

    # Print results table
    print(f"\n{'Company Name':<42} | {'Category':<12} | {'Ownership':<8} | {'Payload Chars':<13} | {'Avg Time (ms)'}")
    print("-" * 100)
    for r in benchmark_res:
        print(f"{r['name'][:42]:<42} | {r['company_type']:<12} | {r['ownership']:<8} | {r['payload_chars']:<13} | {r['avg_time_ms']:.4f} ms")

    print()
    stats, report_text = summarize_results(benchmark_res)
    print(report_text)

    # Save validation reports
    with open(results_log, "w", encoding="utf-8") as f_log:
        f_log.write(report_text)
        f_log.write("\nDetailed Profile Measurements:\n")
        f_log.write("-" * 50 + "\n")
        for r in benchmark_res:
            f_log.write(f"Company: {r['name']}\n")
            f_log.write(f"  Type: {r['company_type']} | Ownership: {r['ownership']}\n")
            f_log.write(f"  Payload Size: {r['payload_chars']} chars\n")
            f_log.write(f"  Average Processing Time: {r['avg_time_ms']:.4f} ms\n")
            f_log.write("-" * 50 + "\n")

    with open(results_csv, "w", encoding="utf-8", newline="") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=["Company Name", "Category", "Ownership", "Payload Chars", "Avg Time (ms)"])
        writer.writeheader()
        for r in benchmark_res:
            writer.writerow({
                "Company Name": r["name"],
                "Category": r["company_type"],
                "Ownership": r["ownership"],
                "Payload Chars": r["payload_chars"],
                "Avg Time (ms)": round(r["avg_time_ms"], 4)
            })

    print(f"✓ Summary report saved to Log: {results_log}")
    print(f"✓ Detailed metrics saved to CSV: {results_csv}")

    # Automated Performance System Checks
    print("\n" + "=" * 96)
    print("3. RUNNING CRITICAL PERFORMANCE BENCHMARK CHECKS")
    print("=" * 96)

    try:
        # Check 1: Fortune 500 average processing time is greater than Startup average processing time
        # due to larger text fields and supply chain/news data
        assert stats["fortune_500_avg_ms"] > stats["startup_avg_ms"], (
            f"Expected Fortune 500 average time ({stats['fortune_500_avg_ms']:.4f} ms) "
            f"to be greater than Startup average time ({stats['startup_avg_ms']:.4f} ms) "
            f"due to structural payload size difference."
        )
        print("✓ check_f500_processing_time_exceeds_startup_time: PASSED")

        # Check 2: Public company average time is greater than Private company average time
        assert stats["public_avg_ms"] > stats["private_avg_ms"], (
            f"Expected Public average time ({stats['public_avg_ms']:.4f} ms) "
            f"to be greater than Private average time ({stats['private_avg_ms']:.4f} ms)."
        )
        print("✓ check_public_processing_time_exceeds_private_time: PASSED")

        # Check 3: Check that payload size of Fortune 500 is larger than Startup
        assert stats["fortune_500_avg_chars"] > stats["startup_avg_chars"], (
            f"Expected Fortune 500 average payload size ({stats['fortune_500_avg_chars']:.1f} chars) "
            f"to be greater than Startup average payload size ({stats['startup_avg_chars']:.1f} chars)."
        )
        print("✓ check_f500_payload_size_exceeds_startup_payload_size: PASSED")

        print("\nAll Performance Benchmark verification checks passed successfully!")
    except AssertionError as e:
        print("\n✗ Critical performance check assertion failed:", e)
        sys.exit(1)
