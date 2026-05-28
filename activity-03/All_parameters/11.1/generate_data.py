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

AMBIGUOUS_COMPANIES = [
    {
        "name": "Delta Air Lines, Inc.",
        "short_name": "Delta",
        "category": "Aviation / Travel",
        "incorporation_year": "1924",
        "ceo_name": "Ed Bastian",
        "headquarters_address": "Atlanta, Georgia, USA",
        "website_url": "https://www.delta.com",
        "focus_sectors": "Aviation; Transportation; Logistics"
    },
    {
        "name": "Delta Controls Ltd.",
        "short_name": "Delta",
        "category": "Building Automation",
        "incorporation_year": "1980",
        "ceo_name": "Delta Controls Executive",
        "headquarters_address": "Surrey, BC, Canada",
        "website_url": "https://www.deltacontrols.com",
        "focus_sectors": "Building Automation; HVAC Controls; IoT"
    },
    {
        "name": "Delta Dental Agency",
        "short_name": "Delta",
        "category": "Insurance / Healthcare",
        "incorporation_year": "1954",
        "ceo_name": "Delta Dental Director",
        "headquarters_address": "Oak Brook, Illinois, USA",
        "website_url": "https://www.deltadental.com",
        "focus_sectors": "Dental Insurance; Healthcare Plans"
    },
    {
        "name": "Delta Energy Corp",
        "short_name": "Delta",
        "category": "Energy / Utilities",
        "incorporation_year": "2005",
        "ceo_name": "Delta Energy Chief",
        "headquarters_address": "Houston, Texas, USA",
        "website_url": "https://www.deltaenergy.com",
        "focus_sectors": "Oil & Gas; Renewable Energy; Electricity"
    },
    {
        "name": "Target Corporation",
        "short_name": "Target",
        "category": "Retail / E-commerce",
        "incorporation_year": "1902",
        "ceo_name": "Brian Cornell",
        "headquarters_address": "Minneapolis, Minnesota, USA",
        "website_url": "https://www.target.com",
        "focus_sectors": "Retail; Consumer Goods; E-commerce"
    },
    {
        "name": "Target Brand Agency",
        "short_name": "Target",
        "category": "Marketing / Brand Agency",
        "incorporation_year": "2015",
        "ceo_name": "Target Agency Director",
        "headquarters_address": "Portland, Oregon, USA",
        "website_url": "https://www.targetagency.com",
        "focus_sectors": "Marketing; Advertising; Corporate Branding"
    }
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/11.1/11.1.csv"
    
    if not os.path.exists(input_path):
        input_path = "../companies_master.csv"
        if not os.path.exists(input_path):
            input_path = "../../companies_master.csv"
            
    with open(input_path, mode="r", encoding="utf-8-sig") as f_in:
        reader = csv.DictReader(f_in)
        headers = reader.fieldnames if reader.fieldnames else []
        rows = list(reader)
        
    print(f"Reading from {input_path}, found {len(rows)} rows.")
    
    new_rows = []
    
    # 1. Add target major companies
    target_by_name = {}
    for row in rows:
        company_name = row["name"].strip()
        if company_name in TARGET_COMPANIES:
            target_by_name[company_name] = row
            
    # Add target companies in standard sequence
    for name in TARGET_COMPANIES:
        if name in target_by_name:
            new_rows.append(target_by_name[name])
            
    # 2. Add ambiguous companies, filling missing columns with "NA"
    for amb in AMBIGUOUS_COMPANIES:
        amb_row = {h: "NA" for h in headers}
        amb_row.update(amb)
        new_rows.append(amb_row)
        
    # Write the rows to the output CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)
        
    print(f"Successfully wrote {len(new_rows)} target and ambiguous profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
