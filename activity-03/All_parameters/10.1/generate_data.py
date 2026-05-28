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

TEMPORAL_COMPANIES = [
    "Capgemini",
    "Llama Logisol Private Limited",
    "Leap Finance Private Limited",
    "Swiggy Limited"
]

ALL_COMPANIES = TARGET_COMPANIES + TEMPORAL_COMPANIES

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/10.1/10.1.csv"
    
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
        company_name = row[1].strip()
        if company_name in ALL_COMPANIES:
            new_rows.append(row)
            
    # Write the target rows to the output CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(header)
        writer.writerows(new_rows)
        
    print(f"Successfully wrote {len(new_rows)} target and temporal profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
