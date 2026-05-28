import csv
import os

TARGET_COMPANIES = [
    "Apple Inc.",
    "Schneider Electric",
    "Llama Logisol Private Limited"
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/15.1/15.1.csv"

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

    # Add a custom highly speculative startup
    speculative_company = {h: "NA" for h in headers}
    speculative_company.update({
        "name": "Speculative AI Labs",
        "short_name": "SpecAI",
        "nature_of_company": "Privately Held Company",
        "employee_size": "15-25 (estimated based on LinkedIn)",
        "annual_revenue": "~$1.5M (inferred from employee size)",
        "valuation": "$10M (speculative Series A pitch)"
    })
    new_rows.append(speculative_company)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
