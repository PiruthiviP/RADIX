import csv
import os

FORTUNE_500_COMPANIES = [
    "Apple Inc.",
    "Microsoft Corporation",
    "Amazon.com, Inc.",
    "Tata Consultancy Services Limited",
    "Accenture plc"
]

STARTUP_COMPANIES = [
    "KALVI CAREER EDUCATION PRIVATE LIMITED",
    "FLAM Gaming Private Limited",
    "MintAir Corp",
    "Dunzo Digital Private Limited",
    "Dunzo" # Fallback/fuzzy check
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/13.2/13.2.csv"

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
    
    # Track which companies are matched to avoid duplicates
    matched_names = set()

    # Helper function to find a company in rows
    def add_company(name_query, company_type):
        for row in rows:
            name = row["name"].strip()
            if name in matched_names:
                continue
            if name_query.lower() == name.lower() or name_query.lower() in name.lower():
                # Add type identifier as a metadata field
                row_copy = dict(row)
                row_copy["nature_of_company"] = row_copy.get("nature_of_company", "") + f" | benchmark_{company_type}"
                new_rows.append(row_copy)
                matched_names.add(name)
                print(f"Added {company_type}: {name}")
                return True
        return False

    for name in FORTUNE_500_COMPANIES:
        add_company(name, "fortune500")

    for name in STARTUP_COMPANIES:
        add_company(name, "startup")

    # If we still have fewer than 10 total records, pad with some others
    if len(new_rows) < 10:
        print("Warning: Under 10 benchmark rows found, padding with private and public examples.")
        # Try to find any other public company and private company
        for row in rows:
            name = row["name"].strip()
            if name in matched_names:
                continue
            nature = row.get("nature_of_company", "").lower()
            emp = row.get("employee_size", "").lower()
            
            # Simple heuristic
            is_public = "public" in nature or "listed" in nature
            is_private = "private" in nature or "held" in nature
            
            if is_public and len(matched_names) < 10:
                row_copy = dict(row)
                row_copy["nature_of_company"] = row_copy.get("nature_of_company", "") + " | benchmark_fortune500"
                new_rows.append(row_copy)
                matched_names.add(name)
                print(f"Added Pad Public: {name}")
            elif is_private and len(matched_names) < 10:
                row_copy = dict(row)
                row_copy["nature_of_company"] = row_copy.get("nature_of_company", "") + " | benchmark_startup"
                new_rows.append(row_copy)
                matched_names.add(name)
                print(f"Added Pad Private: {name}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
