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

STRUCTURAL_COMPANIES = [
    "International Business Machines Corporation ",
    "Barclays PLC ",
    "Blink Commerce Private Limited ",
    "ServiceNow, Inc.",
    "Morgan Stanley",
    "Byju’s",
    "DXC Technology Company"
]

ALL_COMPANIES_STRIPPED = [name.strip().lower() for name in TARGET_COMPANIES + STRUCTURAL_COMPANIES]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/10.2/10.2.csv"
    
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
        company_name = row[1].strip().lower()
        if company_name in ALL_COMPANIES_STRIPPED:
            new_rows.append(row)
            
    # Write the target rows to the output CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(header)
        writer.writerows(new_rows)
        
    print(f"Successfully wrote {len(new_rows)} target and structural profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
