import csv
import os

TARGET_COMPANIES = [
    "Apple Inc."
]

DEFAULT_HANDLING_COMPANIES = [
    # 1. Private Startup: revenue stays None, remote policy defaults to 'Unknown', relocation to 'No'
    {
        "name": "Dynamic Startup Inc.",
        "short_name": "Dynamic Startup",
        "category": "Mobile Tech",
        "incorporation_year": "2024",
        "ceo_name": "Zaphod Beeblebrox",
        "headquarters_address": "Austin, Texas, USA",
        "nature_of_company": "Private Company",
        "annual_revenue": "NA",
        "remote_policy_details": "NA",
        "relocation_support": "NA",
        "regulatory_status": "NA"
    },
    
    # 2. Public Corp: revenue stays None, regulatory_status has context-dependent default (Public -> SEC Regulated)
    {
        "name": "Standard Corp plc",
        "short_name": "Standard Corp",
        "category": "Industrial Manufacturing",
        "incorporation_year": "2010",
        "ceo_name": "Slartibartfast",
        "headquarters_address": "London, United Kingdom",
        "nature_of_company": "Public Company",
        "annual_revenue": "NA",
        "remote_policy_details": "NA",
        "relocation_support": "NA",
        "regulatory_status": "NA"
    }
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/14.4/14.4.csv"

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

    for dh in DEFAULT_HANDLING_COMPANIES:
        dh_row = {h: "NA" for h in headers}
        dh_row.update(dh)
        new_rows.append(dh_row)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
