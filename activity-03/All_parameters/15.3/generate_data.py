import csv
import os

TARGET_COMPANIES = [
    "Apple Inc."
]

RECENCY_COMPANIES = [
    # 1. Company with Recent Data (Last 6 months from May 2026)
    {
        "name": "Nova Tech Solutions",
        "short_name": "Nova Tech",
        "category": "Artificial Intelligence",
        "incorporation_year": "2022",
        "ceo_name": "Arthur Dent",
        "headquarters_address": "London, UK",
        "recent_news": "Announced a new AI chips launch in February 2026. Executive board restructured in April 2026."
    },
    
    # 2. Company with Acceptable Data (Last 12 months from May 2026)
    {
        "name": "Midway Systems Ltd",
        "short_name": "Midway",
        "category": "SaaS Platform",
        "incorporation_year": "2018",
        "ceo_name": "Sarah Connor",
        "headquarters_address": "Austin, Texas, USA",
        "recent_news": "Acquired a cloud security firm in August 2025. Annual financials for FY2025 published in September 2025."
    },
    
    # 3. Company with Outdated Data (>12 months from May 2026)
    {
        "name": "Legacy Manufacturing Corp",
        "short_name": "Legacy Mfg",
        "category": "Heavy Machinery",
        "incorporation_year": "1995",
        "ceo_name": "Ford Prefect",
        "headquarters_address": "Chicago, Illinois, USA",
        "recent_news": "Rebranded in early 2024. Launched their latest product line in October 2024."
    }
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/15.3/15.3.csv"

    if not os.path.exists(input_path):
        for alt in ["../companies_master.csv", "../../companies_master.csv"]:
            if os.path.exists(alt):
                input_path = alt
                break

    with open(input_path, mode="r", encoding="utf-8-sig") as f_in:
        reader = csv.DictReader(f_in)
        headers = reader.fieldnames if reader.fieldnames else []
        rows = list(reader)

    print(f"Reading from {input_path}, found {len(rows)} rows.")

    new_rows = []
    target_by_name = {row["name"].strip(): row for row in rows}

    for name in TARGET_COMPANIES:
        match = target_by_name.get(name.strip())
        if match:
            new_rows.append(match)
        else:
            for k, v in target_by_name.items():
                if name.strip().lower() in k.lower() or k.lower() in name.strip().lower():
                    new_rows.append(v)
                    break

    for rc in RECENCY_COMPANIES:
        rc_row = {h: "NA" for h in headers}
        rc_row.update(rc)
        new_rows.append(rc_row)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
