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

PARENT_SUBSIDIARY_COMPANIES = [
    {
        "name": "Alphabet Inc.",
        "short_name": "Alphabet",
        "category": "Parent Holding Company",
        "incorporation_year": "2015",
        "ceo_name": "Sundar Pichai",
        "headquarters_address": "1600 Amphitheatre Parkway, Mountain View, California, USA",
        "website_url": "https://abc.xyz",
        "focus_sectors": "Technology; AI Research; Autonomous Vehicles; Life Sciences"
    },
    {
        "name": "YouTube, LLC",
        "short_name": "YouTube",
        "category": "Subsidiary of Google LLC",
        "incorporation_year": "2005",
        "ceo_name": "Neal Mohan",
        "headquarters_address": "901 Cherry Ave, San Bruno, California, USA",
        "website_url": "https://www.youtube.com",
        "focus_sectors": "Video Streaming; Digital Advertising; Content Creation"
    },
    {
        "name": "Meta Platforms, Inc.",
        "short_name": "Meta",
        "category": "Parent Social Tech Company",
        "incorporation_year": "2004",
        "ceo_name": "Mark Zuckerberg",
        "headquarters_address": "1 Hacker Way, Menlo Park, California, USA",
        "website_url": "https://about.meta.com",
        "focus_sectors": "Social Media; Augmented Reality; Metaverse; Digital Advertising"
    },
    {
        "name": "Instagram, LLC",
        "short_name": "Instagram",
        "category": "Subsidiary of Meta Platforms, Inc.",
        "incorporation_year": "2010",
        "ceo_name": "Adam Mosseri",
        "headquarters_address": "1601 Willow Road, Menlo Park, California, USA",
        "website_url": "https://www.instagram.com",
        "focus_sectors": "Photo Sharing; Social Networking; Influencer Marketing"
    }
]

def generate_csv():
    input_path = "companies_master.csv"
    output_path = "All_parameters/11.2/11.2.csv"

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

    # 1. Extract target major companies in order
    target_by_name = {row["name"].strip(): row for row in rows}
    for name in TARGET_COMPANIES:
        if name in target_by_name:
            new_rows.append(target_by_name[name])

    # 2. Inject parent/subsidiary ambiguity records
    for ps in PARENT_SUBSIDIARY_COMPANIES:
        ps_row = {h: "NA" for h in headers}
        ps_row.update(ps)
        new_rows.append(ps_row)

    # Write the rows to the output CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"Successfully wrote {len(new_rows)} target and parent/subsidiary profiles to {output_path}.")

if __name__ == "__main__":
    generate_csv()
