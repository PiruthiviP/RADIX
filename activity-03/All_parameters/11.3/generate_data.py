import csv
import os

TARGET_COMPANIES = [
    "Apple Inc.",
    "Microsoft Corporation",
    "Barclays PLC ",
    "Koninklijke Philips N.V.",
    "Citigroup Inc.",
]

# Geographic variant records — same brand, different legal entities per region
GEOGRAPHIC_VARIANT_COMPANIES = [
    # Unilever: UK-incorporated PLC vs Netherlands-incorporated NV (dual-listed until 2020 unification)
    {
        "name": "Unilever PLC",
        "short_name": "Unilever",
        "category": "FMCG / Consumer Goods",
        "incorporation_year": "1894",
        "ceo_name": "Hein Schumacher",
        "headquarters_address": "Port Sunlight, Wirral, England, United Kingdom",
        "website_url": "https://www.unilever.com",
        "focus_sectors": "Consumer Goods; FMCG; Home Care; Beauty; Food & Beverages",
        "operating_countries": "190+",
        "nature_of_company": "Public (LSE / NYSE)",
        "regulatory_status": "FCA Regulated; SEC Registered; UK Companies Act"
    },
    {
        "name": "Unilever N.V.",
        "short_name": "Unilever",
        "category": "FMCG / Consumer Goods",
        "incorporation_year": "1927",
        "ceo_name": "Hein Schumacher",
        "headquarters_address": "Rotterdam, Netherlands",
        "website_url": "https://www.unilever.com",
        "focus_sectors": "Consumer Goods; FMCG; Home Care; Beauty; Food & Beverages",
        "operating_countries": "190+",
        "nature_of_company": "Public (Euronext Amsterdam / NYSE)",
        "regulatory_status": "AFM Regulated; SEC Registered; Dutch Civil Code"
    },

    # Shell: UK-incorporated plc vs Netherlands-incorporated N.V. (merged in 2005, re-simplified in 2022)
    {
        "name": "Shell plc",
        "short_name": "Shell",
        "category": "Energy / Oil & Gas",
        "incorporation_year": "1907",
        "ceo_name": "Wael Sawan",
        "headquarters_address": "Shell Centre, York Road, London, SE1 7NA, United Kingdom",
        "website_url": "https://www.shell.com",
        "focus_sectors": "Oil & Gas; LNG; Renewables; Chemicals; Petrochemicals",
        "operating_countries": "70+",
        "nature_of_company": "Public (LSE / NYSE)",
        "regulatory_status": "FCA Regulated; SEC Registered; UK Companies Act"
    },
    {
        "name": "Shell Nederland B.V.",
        "short_name": "Shell",
        "category": "Energy / Oil & Gas",
        "incorporation_year": "1907",
        "ceo_name": "Marjan van Loon",
        "headquarters_address": "Carel van Bylandtlaan 30, 2596 HR The Hague, Netherlands",
        "website_url": "https://www.shell.nl",
        "focus_sectors": "Oil & Gas; LNG; Renewables; Chemicals; Petrochemicals",
        "operating_countries": "Netherlands (primary)",
        "nature_of_company": "Private (Dutch Subsidiary)",
        "regulatory_status": "AFM Supervised; Dutch Civil Code"
    },

    # HSBC: Global holding vs North America entity
    {
        "name": "HSBC Holdings plc",
        "short_name": "HSBC",
        "category": "Banking / Financial Services",
        "incorporation_year": "1991",
        "ceo_name": "Georges Elhedery",
        "headquarters_address": "8 Canada Square, Canary Wharf, London, E14 5HQ, United Kingdom",
        "website_url": "https://www.hsbc.com",
        "focus_sectors": "Retail Banking; Commercial Banking; Investment Banking; Wealth Management",
        "operating_countries": "60+",
        "nature_of_company": "Public (LSE / HKEX / NYSE)",
        "regulatory_status": "PRA & FCA Regulated; SEC Registered; HKMA Licensed"
    },
    {
        "name": "HSBC Bank USA, N.A.",
        "short_name": "HSBC",
        "category": "Banking / Financial Services",
        "incorporation_year": "1850",
        "ceo_name": "Michael Roberts",
        "headquarters_address": "452 Fifth Avenue, New York, NY 10018, United States",
        "website_url": "https://www.us.hsbc.com",
        "focus_sectors": "Retail Banking; Commercial Banking; Wealth Management",
        "operating_countries": "United States (primary)",
        "nature_of_company": "National Banking Association",
        "regulatory_status": "OCC Regulated; FDIC Insured; Federal Reserve Supervised"
    }
]


def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/11.3/11.3.csv"

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
        match = target_by_name.get(name)
        if match:
            new_rows.append(match)
        else:
            # Try partial match
            for k, v in target_by_name.items():
                if name.strip() in k or k in name.strip():
                    new_rows.append(v)
                    break

    for gv in GEOGRAPHIC_VARIANT_COMPANIES:
        gv_row = {h: "NA" for h in headers}
        gv_row.update(gv)
        new_rows.append(gv_row)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} profiles to {output_path}.")
    print("  Anchor companies:", [c["name"].strip() for c in new_rows[:len(TARGET_COMPANIES)]])
    print("  Geographic variants:", [c["name"] for c in GEOGRAPHIC_VARIANT_COMPANIES])


if __name__ == "__main__":
    generate_csv()
