import csv
import os

TARGET_COMPANIES = [
    "Apple Inc."
]

NOT_APPLICABLE_COMPANIES = [
    # 1. VC Firm where Products / Offerings are N/A
    {
        "name": "Alpha Venture Capital",
        "short_name": "Alpha VC",
        "category": "Venture Capital / Investment",
        "incorporation_year": "2015",
        "ceo_name": "Marcus Aurelius",
        "headquarters_address": "Menlo Park, California, USA",
        "nature_of_company": "Venture Capital Firm",
        "offerings_description": "N/A (Investment Services Only)",
        "top_customers": "N/A",
        "key_investors": "LPs (Undisclosed)",
        "office_locations": "Silicon Valley Office",
        "cab_policy": "Standard cab policy"
    },
    
    # 2. Bootstrapped Startup where Key Investors is N/A
    {
        "name": "Bootstrapped SaaS Corp",
        "short_name": "Bootstrapped SaaS",
        "category": "Software as a Service",
        "incorporation_year": "2020",
        "ceo_name": "Sarah Connor",
        "headquarters_address": "Austin, Texas, USA",
        "nature_of_company": "Private Bootstrapped Company",
        "offerings_description": "Automated Email Marketing Software",
        "key_investors": "N/A (Bootstrapped)",
        "recent_funding_rounds": "N/A (No external funding)",
        "office_locations": "Austin HQ",
        "cab_policy": "Standard cab policy"
    },
    
    # 3. Fully Remote Company where Office Locations / Commute policies are N/A
    {
        "name": "Cloud Distributed LLC",
        "short_name": "Cloud Distributed",
        "category": "Cloud Infrastructure",
        "incorporation_year": "2018",
        "ceo_name": "Linus Torvalds",
        "headquarters_address": "Virtual / Remote",
        "nature_of_company": "Privately Held (Fully Remote)",
        "offerings_description": "Cloud Services Infrastructure",
        "key_investors": "Founder owned",
        "office_locations": "N/A (Fully Remote / Distributed)",
        "cab_policy": "N/A",
        "airport_commute_time": "N/A"
    }
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/14.2/14.2.csv"

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

    for nac in NOT_APPLICABLE_COMPANIES:
        nac_row = {h: "NA" for h in headers}
        nac_row.update(nac)
        new_rows.append(nac_row)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
