import csv
import os

TARGET_COMPANIES = [
    "Apple Inc.",
    "Microsoft Corporation"
]

NULL_HANDLING_COMPANIES = [
    # 1. Private company with undisclosed financials & funding
    {
        "name": "Secretive Private Startup Ltd",
        "short_name": "Secretive",
        "category": "Software as a Service",
        "incorporation_year": "2023",
        "ceo_name": "John Doe",
        "headquarters_address": "San Francisco, California, USA",
        "nature_of_company": "Privately Held Company",
        "annual_revenue": "Undisclosed",
        "annual_profit": "NA",
        "valuation": "?",
        "recent_funding_rounds": "Series A (Undisclosed amount)",
        "total_capital_raised": "Undisclosed"
    },
    
    # 2. Bootstrapped company with no funding
    {
        "name": "Bootstrapped Tech Co.",
        "short_name": "Bootstrapped",
        "category": "E-commerce Infrastructure",
        "incorporation_year": "2021",
        "ceo_name": "Jane Smith",
        "headquarters_address": "Austin, Texas, USA",
        "nature_of_company": "Private Company (Family-owned)",
        "annual_revenue": "$1.2M",
        "annual_profit": "Undisclosed",
        "valuation": "NA",
        "recent_funding_rounds": "None (Bootstrapped)",
        "total_capital_raised": "0"
    }
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/14.1/14.1.csv"

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

    for nh in NULL_HANDLING_COMPANIES:
        nh_row = {h: "NA" for h in headers}
        nh_row.update(nh)
        new_rows.append(nh_row)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} profiles to {output_path}.")
    print("  Anchor companies:", [c["name"].strip() for c in new_rows[:len(TARGET_COMPANIES)]])
    print("  Null-handling companies:", [c["name"] for c in NULL_HANDLING_COMPANIES])

if __name__ == "__main__":
    generate_csv()
