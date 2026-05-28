import csv
import os

TARGET_COMPANIES = [
    "Apple Inc."
]

SOURCE_TIER_COMPANIES = [
    # 1. Company with Tier 1 and Tier 2 source data
    {
        "name": "Alpha Corporate Holdings",
        "short_name": "Alpha Corp",
        "category": "Technology holding",
        "incorporation_year": "2012",
        "ceo_name": "Marcus Aurelius",
        "headquarters_address": "Austin, Texas, USA",
        "nature_of_company": "Public",
        "website_url": "https://www.alphacorp.com",
        "linkedin_url": "https://www.linkedin.com/company/alphacorp",
        "recent_news": "Officially filed Form 10-K with the SEC for FY2025. Consolidated earnings audited by E&Y."
    },
    
    # 2. Company with Tier 3 source data (mostly news articles and speculative blogs)
    {
        "name": "Beta Tech Speculations",
        "short_name": "Beta Tech",
        "category": "Cryptocurrency Infrastructure",
        "incorporation_year": "2022",
        "ceo_name": "Satoshi Nakamoto",
        "headquarters_address": "Unknown",
        "nature_of_company": "Privately Held Company",
        "website_url": "NA",
        "linkedin_url": "NA",
        "recent_news": "Rumored exit strategy posted on CoinDesk. Employees discussed layoffs on Reddit and local tech blogs."
    }
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/15.2/15.2.csv"

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

    for st in SOURCE_TIER_COMPANIES:
        st_row = {h: "NA" for h in headers}
        st_row.update(st)
        new_rows.append(st_row)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
