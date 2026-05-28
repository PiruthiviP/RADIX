import csv
import os

TARGET_COMPANIES = [
    "Apple Inc.",
    "Microsoft Corporation",
    "International Business Machines Corporation "
]

ABBREVIATION_VARIANTS = [
    # IBM: Acronym query variant
    {
        "name": "IBM",
        "short_name": "NA",
        "category": "Enterprise Technology & Consulting",
        "incorporation_year": "1911",
        "ceo_name": "Arvind Krishna",
        "headquarters_address": "1 New Orchard Road, Armonk, New York, USA",
        "website_url": "https://www.ibm.com",
        "focus_sectors": "Cloud Computing; Cognitive Computing; AI (Watson); Mainframes",
        "nature_of_company": "Public (NYSE: IBM)",
        "regulatory_status": "SEC Registered"
    },
    
    # AT&T: Both acronym and full name variant
    {
        "name": "AT&T Inc.",
        "short_name": "NA",
        "category": "Telecommunications Conglomerate",
        "incorporation_year": "1885",
        "ceo_name": "John Stankey",
        "headquarters_address": "208 S. Akard St., Dallas, Texas, USA",
        "website_url": "https://www.att.com",
        "focus_sectors": "Telecommunications; 5G; Broadband; Satellite; Media",
        "nature_of_company": "Public (NYSE: T)",
        "regulatory_status": "FCC Regulated; SEC Registered"
    },
    {
        "name": "American Telephone & Telegraph Company",
        "short_name": "NA",
        "category": "Telecommunications Conglomerate",
        "incorporation_year": "1885",
        "ceo_name": "John Stankey",
        "headquarters_address": "Dallas, Texas, USA",
        "website_url": "https://www.att.com",
        "focus_sectors": "Telecommunications; 5G; Broadband",
        "nature_of_company": "Public (NYSE: T)",
        "regulatory_status": "FCC Regulated"
    },

    # 3M: Both abbreviation and full name variant
    {
        "name": "3M Company",
        "short_name": "NA",
        "category": "Industrial & Consumer Conglomerate",
        "incorporation_year": "1902",
        "ceo_name": "William M. Brown",
        "headquarters_address": "3M Center, Maplewood, Minnesota, USA",
        "website_url": "https://www.3m.com",
        "focus_sectors": "Abrasives; Adhesive Tapes; Consumer Goods; Healthcare Products",
        "nature_of_company": "Public (NYSE: MMM)",
        "regulatory_status": "SEC Registered"
    },
    {
        "name": "Minnesota Mining and Manufacturing Company",
        "short_name": "NA",
        "category": "Industrial & Consumer Conglomerate",
        "incorporation_year": "1902",
        "ceo_name": "William M. Brown",
        "headquarters_address": "Maplewood, Minnesota, USA",
        "website_url": "https://www.3m.com",
        "focus_sectors": "Industrial; Healthcare; Consumer Goods",
        "nature_of_company": "Public (NYSE: MMM)",
        "regulatory_status": "SEC Registered"
    }
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/11.4/11.4.csv"

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
            # Try substring
            for k, v in target_by_name.items():
                if name.strip() in k or k in name.strip():
                    new_rows.append(v)
                    break

    for av in ABBREVIATION_VARIANTS:
        av_row = {h: "NA" for h in headers}
        av_row.update(av)
        new_rows.append(av_row)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} profiles to {output_path}.")
    print("  Anchor companies:", [c["name"].strip() for c in new_rows[:len(TARGET_COMPANIES)]])
    print("  Abbreviation variants:", [c["name"] for c in ABBREVIATION_VARIANTS])

if __name__ == "__main__":
    generate_csv()
