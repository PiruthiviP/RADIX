import csv
import os

TARGET_COMPANIES = [
    "Apple Inc.",
    "Microsoft Corporation",
    "Google LLC (Subsidiary of Alphabet Inc.)",
    "Accenture plc",
    "Amazon.com, Inc.",
    "Tata Consultancy Services Limited",
    "Infosys Limited"
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/4.3/4.3.csv"
    
    if not os.path.exists(input_path):
        input_path = "../companies_master.csv"
        if not os.path.exists(input_path):
            input_path = "../../companies_master.csv"
            
    with open(input_path, mode="r", encoding="utf-8-sig") as f_in:
        reader = csv.reader(f_in)
        header = next(reader)
        rows = list(reader)
        
    print(f"Reading from {input_path}, found {len(rows)} rows.")
    
    new_rows = []
    for row in rows:
        company_name = row[1]
        if company_name in TARGET_COMPANIES:
            new_rows.append(row)
            
    # Write the target rows to the output CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(header)
        writer.writerows(new_rows)
        
    print(f"Successfully wrote {len(new_rows)} target profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
