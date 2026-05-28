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

ADVERSARIAL_COMPANIES = [
    {
        "name": "Delta Air Lines, Inc.",
        "short_name": "Delta Air",
        "category": "Adversarial Test",
        "incorporation_year": "1924",
        "ceo_name": "Ed Bastian",
        "headquarters_address": "Atlanta, Georgia, USA",
        "website_url": "https://www.delta.com",
        "primary_contact_email": "info@delta.com",
        "primary_phone_number": "+1-800-221-1212"
    },
    {
        "name": "Delta Controls Ltd.",
        "short_name": "Delta Controls",
        "category": "Adversarial Test",
        "incorporation_year": "1980",
        "ceo_name": "Delta Controls Executive",
        "headquarters_address": "Surrey, BC, Canada",
        "website_url": "https://www.deltacontrols.com",
        "primary_contact_email": "support@deltacontrols.com",
        "primary_phone_number": "+1-604-574-9444"
    },
    {
        "name": "Delta Dental Agency",
        "short_name": "Delta Dental",
        "category": "Adversarial Test",
        "incorporation_year": "1954",
        "ceo_name": "Delta Dental Director",
        "headquarters_address": "Oak Brook, Illinois, USA",
        "website_url": "https://www.deltadental.com",
        "primary_contact_email": "contact@deltadental.com",
        "primary_phone_number": "+1-800-524-0149"
    },
    {
        "name": "Delta Energy Corp",
        "short_name": "Delta Energy",
        "category": "Adversarial Test",
        "incorporation_year": "2005",
        "ceo_name": "Delta Energy Chief",
        "headquarters_address": "Houston, Texas, USA",
        "website_url": "https://www.deltaenergy.com",
        "primary_contact_email": "info@deltaenergy.com",
        "primary_phone_number": "+1-713-555-0155"
    },
    {
        "name": "Apple Bank",
        "short_name": "Apple Bank",
        "category": "Adversarial Test",
        "incorporation_year": "1863",
        "ceo_name": "Gerard LaRocca",
        "headquarters_address": "New York City, NY, USA",
        "website_url": "https://www.applebank.com",
        "primary_contact_email": "info@applebank.com",
        "primary_phone_number": "+1-800-990-0080"
    },
    {
        "name": "Microsoft Ireland Operations",
        "short_name": "Microsoft Ireland",
        "category": "Adversarial Test",
        "incorporation_year": "1997",
        "ceo_name": "Microsoft Ireland Director",
        "headquarters_address": "Dublin, Ireland",
        "website_url": "https://www.microsoft.com/en-ie",
        "primary_contact_email": "ireland_info@microsoft.com",
        "primary_phone_number": "+353-1-706-5000"
    },
    {
        "name": "Microsoft India Private Limited",
        "short_name": "Microsoft India",
        "category": "Adversarial Test",
        "incorporation_year": "1990",
        "ceo_name": "Anant Maheshwari",
        "headquarters_address": "Hyderabad, India",
        "website_url": "https://www.microsoft.com/en-in",
        "primary_contact_email": "india_info@microsoft.com",
        "primary_phone_number": "+91-40-6602-0000"
    }
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/9.3/9.3.csv"
    
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
            
    # 2. Add adversarial similar-named context confusion companies
    # Interleave some to test sequence logic (e.g. Apple Inc, then Apple Bank)
    # Let's create a specific adversarial order:
    # - Apple Inc. (already added)
    # - Apple Bank
    # - Delta Air Lines, Inc.
    # - Delta Controls Ltd.
    # - Delta Dental Agency
    # - Delta Energy Corp
    # - Microsoft Corporation (already added)
    # - Microsoft Ireland Operations
    # - Microsoft India Private Limited
    
    adversarial_by_name = {c["name"]: c for c in ADVERSARIAL_COMPANIES}
    
    # We will build full dictionaries matching the master headers for each adversarial company
    for adv in ADVERSARIAL_COMPANIES:
        adv_row = {h: "NA" for h in headers}
        adv_row.update(adv)
        
        # Insert them in the right locations or append them
        if adv["name"] == "Apple Bank":
            # Find Apple Inc. and insert Apple Bank right after it
            idx = next((i for i, r in enumerate(new_rows) if r["name"] == "Apple Inc."), len(new_rows) - 1)
            new_rows.insert(idx + 1, adv_row)
        elif adv["name"].startswith("Microsoft"):
            # Find Microsoft Corporation and insert right after it
            idx = next((i for i, r in enumerate(new_rows) if r["name"] == "Microsoft Corporation"), len(new_rows) - 1)
            # Insert Microsoft Ireland, then Microsoft India in sequence
            if adv["name"] == "Microsoft Ireland Operations":
                new_rows.insert(idx + 1, adv_row)
            else:
                new_rows.insert(idx + 2, adv_row)
        else:
            # Delta companies, append to the end in sequence
            new_rows.append(adv_row)
            
    # Write the rows to the output CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)
        
    print(f"Successfully wrote {len(new_rows)} target and adversarial profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
