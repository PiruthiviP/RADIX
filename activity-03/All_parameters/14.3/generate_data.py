import csv
import os

TARGET_COMPANIES = [
    "Apple Inc."
]

AMBIGUOUS_COMPANIES = [
    # 1. New Company (founded 2026): data not yet generated
    {
        "name": "Nova Tech Systems",
        "short_name": "Nova Tech",
        "category": "Artificial Intelligence",
        "incorporation_year": "2026",
        "ceo_name": "Arthur Dent",
        "headquarters_address": "London, United Kingdom",
        "nature_of_company": "Privately Held Company",
        "yoy_growth_rate": "Not Generated (New Company)",
        "exit_strategy_history": "Not Generated Yet"
    },
    
    # 2. Secretive Private Company: data exists but is not public
    {
        "name": "SecureFlow Cyber Ltd",
        "short_name": "SecureFlow",
        "category": "Cybersecurity Services",
        "incorporation_year": "2019",
        "ceo_name": "Tricia McMillan",
        "headquarters_address": "Boston, Massachusetts, USA",
        "nature_of_company": "Private Company",
        "annual_revenue": "Restricted (Non-Public)",
        "total_capital_raised": "Private (Undisclosed)"
    },
    
    # 3. Rebranded/Acquired Company: data previously existed but was removed
    {
        "name": "Legacy Brands Inc.",
        "short_name": "Legacy Brands",
        "category": "Retail Infrastructure",
        "incorporation_year": "2008",
        "ceo_name": "Ford Prefect",
        "headquarters_address": "Chicago, Illinois, USA",
        "nature_of_company": "Subsidiary",
        "recent_funding_rounds": "Removed (Post-Acquisition)",
        "exit_strategy_history": "Archived (Acquired by Amazon)"
    }
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/14.3/14.3.csv"

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

    for ac in AMBIGUOUS_COMPANIES:
        ac_row = {h: "NA" for h in headers}
        ac_row.update(ac)
        new_rows.append(ac_row)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
