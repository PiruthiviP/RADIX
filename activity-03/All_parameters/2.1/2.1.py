import csv
import os
from typing import Dict, Any, Tuple, List
# Complete 163 schema parameters defined by nullability: False = Mandatory (Not Null), True = Optional (Nullable)
METADATA_SCHEMA: Dict[str, bool] = {
    "Company Name": False, "Short Name": True, "Logo": False, "Category": False,
    "Year of Incorporation": False, "Overview of the Company": False, "Nature of Company": False,
    "Company Headquarters": False, "Countries Operating In": True, "Number of Offices (beyond HQ)": True,
    "Office Locations": True, "Employee Size": False, "Hiring Velocity": True,
    "Employee Turnover": True, "Average Retention Tenure": True, "Pain Points Being Addressed": False,
    "Focus Sectors / Industries": False, "Services / Offerings / Products": False,
    "Top Customers by Client Segments": True, "Core Value Proposition": False, "Vision": True,
    "Mission": True, "Values": True, "Unique Differentiators": True, "Competitive Advantages": True,
    "Weaknesses / Gaps in Offering": True, "Key Challenges and Unmet Needs": True, "Key Competitors": False,
    "Technology Partners": True, "Interesting Facts": True, "Recent News": True, "Website URL": False,
    "Quality of Website": True, "Website Rating": True, "Website Traffic Rank": True,
    "Social Media Followers – Combined": False, "Glassdoor Rating": True, "Indeed Rating": True,
    "Google Reviews Rating": True, "LinkedIn Profile URL": True, "Twitter (X) Handle": True,
    "Facebook Page URL": True, "Instagram Page URL": True, "CEO Name": False, "CEO LinkedIn URL": True,
    "Key Business Leaders": False, "Warm Introduction Pathways": True, "Decision Maker Accessibility": True,
    "Company Contact Email": True, "Company Phone Number": True, "Primary Contact Person's Name": True,
    "Primary Contact Person's Title": True, "Primary Contact Person's Email": True,
    "Primary Contact Person's Phone Number": True, "Awards & Recognitions": True, "Brand Sentiment Score": True,
    "Event Participation": True, "Regulatory & Compliance Status": True, "Legal Issues / Controversies": True,
    "Annual Revenues": True, "Annual Profits": True, "Revenue Mix": True, "Company Valuation": True,
    "Year-over-Year Growth Rate": True, "Profitability Status": False, "Market Share (%)": True,
    "Key Investors / Backers": True, "Recent Funding Rounds": True, "Total Capital Raised": True,
    "ESG Practices or Ratings": True, "Sales Motion": False, "Customer Acquisition Cost (CAC)": True,
    "Customer Lifetime Value (CLV)": True, "CAC:LTV Ratio": True, "Churn Rate": True,
    "Net Promoter Score (NPS)": True, "Customer Concentration Risk": True, "Burn Rate": True,
    "Runway": True, "Burn Multiplier": True, "Intellectual Property": True, "R&D Investment": True,
    "AI/ML Adoption Level": True, "Tech Stack/Tools Used": True, "Cybersecurity Posture": True,
    "Supply Chain Dependencies": True, "Geopolitical Risks": True, "Macro Risks": True,
    "Diversity Metrics": True, "Remote Work Policy": False, "Training/Development Spend": True,
    "Partnership Ecosystem": True, "Exit Strategy/History": True, "Carbon Footprint/Environmental Impact": True,
    "Ethical Sourcing Practices": True, "Benchmark vs. Peers": True, "Future Projections": True,
    "Strategic Priorities": False, "Industry Associations / Memberships": True,
    "Case Studies / Public Success Stories": True, "Go-to-Market Strategy": False, "Innovation Roadmap ": True,
    "Product Pipeline": True, "Board of Directors / Advisors": False,
    "Company Introduction / Marketing videos": True, "Customer testimonial": True,
    "Industry Benchmark Technology Adoption Rating": True, "Total Addressable Market (TAM)": True,
    "Serviceable Addressable Market (SAM)": True, "Serviceable Obtainable Market (SOM)": True,
    "Work culture": True, "Manager quality": True, "Psychological safety": True, "Feedback culture": True,
    "Diversity & inclusion": True, "Ethical standards": True, "Typical working hours": True,
    "Overtime expectations": True, "Weekend work": True, "Remote / hybrid / on-site flexibility": False,
    "Leave policy": True, "Burnout risk": True, "Central vs peripheral location": True,
    "Public transport access": True, "Cab availability and company cab policy": True,
    "Commute time from airport": True, "Office zone type": True, "Area safety": True,
    "Company safety policies": True, "Office infrastructure safety": True, "Emergency response preparedness": True,
    "Health support": True, "Onboarding and training quality": True, "Learning culture": True,
    "Exposure quality": True, "Mentorship availability": True, "Internal mobility": True,
    "Promotion clarity": True, "Tools and technology access": True, "Role clarity": True,
    "Early ownership": True, "Work impact": True, "Execution vs thinking balance": True,
    "Automation level": True, "Cross-functional exposure": True, "Company maturity": False,
    "Brand value": True, "Client quality": True, "Layoff history": True, "Fixed vs variable pay": True,
    "Bonus predictability": True, "ESOPs and long-term incentives": True, "Family health insurance": True,
    "Relocation support": True, "Lifestyle and wellness benefits": True, "Exit opportunities": True,
    "Skill relevance": True, "External recognition": True, "Network strength": True, "Global exposure": True,
    "Mission clarity": True, "Sustainability and CSR": True, "Crisis behavior": True
}

# Bidirectional mapping between companies_master.csv headers and METADATA_SCHEMA keys
CSV_HEADER_MAP: Dict[str, str] = {
    'name': 'Company Name',
    'short_name': 'Short Name',
    'logo_url': 'Logo',
    'category': 'Category',
    'incorporation_year': 'Year of Incorporation',
    'overview_text': 'Overview of the Company',
    'nature_of_company': 'Nature of Company',
    'headquarters_address': 'Company Headquarters',
    'operating_countries': 'Countries Operating In',
    'office_count': 'Number of Offices (beyond HQ)',
    'office_locations': 'Office Locations',
    'employee_size': 'Employee Size',
    'hiring_velocity': 'Hiring Velocity',
    'employee_turnover': 'Employee Turnover',
    'avg_retention_tenure': 'Average Retention Tenure',
    'pain_points_addressed': 'Pain Points Being Addressed',
    'focus_sectors': 'Focus Sectors / Industries',
    'offerings_description': 'Services / Offerings / Products',
    'top_customers': 'Top Customers by Client Segments',
    'core_value_proposition': 'Core Value Proposition',
    'vision_statement': 'Vision',
    'mission_statement': 'Mission',
    'core_values': 'Values',
    'unique_differentiators': 'Unique Differentiators',
    'competitive_advantages': 'Competitive Advantages',
    'weaknesses_gaps': 'Weaknesses / Gaps in Offering',
    'key_challenges_needs': 'Key Challenges and Unmet Needs',
    'key_competitors': 'Key Competitors',
    'technology_partners': 'Technology Partners',
    'history_timeline': 'Interesting Facts',
    'recent_news': 'Recent News',
    'website_url': 'Website URL',
    'website_quality': 'Quality of Website',
    'website_rating': 'Website Rating',
    'website_traffic_rank': 'Website Traffic Rank',
    'social_media_followers': 'Social Media Followers – Combined',
    'glassdoor_rating': 'Glassdoor Rating',
    'indeed_rating': 'Indeed Rating',
    'google_rating': 'Google Reviews Rating',
    'linkedin_url': 'LinkedIn Profile URL',
    'twitter_handle': 'Twitter (X) Handle',
    'facebook_url': 'Facebook Page URL',
    'instagram_url': 'Instagram Page URL',
    'ceo_name': 'CEO Name',
    'ceo_linkedin_url': 'CEO LinkedIn URL',
    'key_leaders': 'Key Business Leaders',
    'warm_intro_pathways': 'Warm Introduction Pathways',
    'decision_maker_access': 'Decision Maker Accessibility',
    'primary_contact_email': 'Company Contact Email',
    'primary_phone_number': 'Company Phone Number',
    'contact_person_name': "Primary Contact Person's Name",
    'contact_person_title': "Primary Contact Person's Title",
    'contact_person_email': "Primary Contact Person's Email",
    'contact_person_phone': "Primary Contact Person's Phone Number",
    'awards_recognitions': 'Awards & Recognitions',
    'brand_sentiment_score': 'Brand Sentiment Score',
    'event_participation': 'Event Participation',
    'regulatory_status': 'Regulatory & Compliance Status',
    'legal_issues': 'Legal Issues / Controversies',
    'annual_revenue': 'Annual Revenues',
    'annual_profit': 'Annual Profits',
    'revenue_mix': 'Revenue Mix',
    'valuation': 'Company Valuation',
    'yoy_growth_rate': 'Year-over-Year Growth Rate',
    'profitability_status': 'Profitability Status',
    'market_share_percentage': 'Market Share (%)',
    'key_investors': 'Key Investors / Backers',
    'recent_funding_rounds': 'Recent Funding Rounds',
    'total_capital_raised': 'Total Capital Raised',
    'esg_ratings': 'ESG Practices or Ratings',
    'sales_motion': 'Sales Motion',
    'customer_acquisition_cost': 'Customer Acquisition Cost (CAC)',
    'customer_lifetime_value': 'Customer Lifetime Value (CLV)',
    'cac_ltv_ratio': 'CAC:LTV Ratio',
    'churn_rate': 'Churn Rate',
    'net_promoter_score': 'Net Promoter Score (NPS)',
    'customer_concentration_risk': 'Customer Concentration Risk',
    'burn_rate': 'Burn Rate',
    'runway_months': 'Runway',
    'burn_multiplier': 'Burn Multiplier',
    'intellectual_property': 'Intellectual Property',
    'r_and_d_investment': 'R&D Investment',
    'ai_ml_adoption_level': 'AI/ML Adoption Level',
    'tech_stack': 'Tech Stack/Tools Used',
    'cybersecurity_posture': 'Cybersecurity Posture',
    'supply_chain_dependencies': 'Supply Chain Dependencies',
    'geopolitical_risks': 'Geopolitical Risks',
    'macro_risks': 'Macro Risks',
    'diversity_metrics': 'Diversity Metrics',
    'remote_policy_details': 'Remote Work Policy',
    'training_spend': 'Training/Development Spend',
    'partnership_ecosystem': 'Partnership Ecosystem',
    'exit_strategy_history': 'Exit Strategy/History',
    'carbon_footprint': 'Carbon Footprint/Environmental Impact',
    'ethical_sourcing': 'Ethical Sourcing Practices',
    'benchmark_vs_peers': 'Benchmark vs. Peers',
    'future_projections': 'Future Projections',
    'strategic_priorities': 'Strategic Priorities',
    'industry_associations': 'Industry Associations / Memberships',
    'case_studies': 'Case Studies / Public Success Stories',
    'go_to_market_strategy': 'Go-to-Market Strategy',
    'innovation_roadmap': 'Innovation Roadmap ',
    'product_pipeline': 'Product Pipeline',
    'board_members': 'Board of Directors / Advisors',
    'marketing_video_url': 'Company Introduction / Marketing videos',
    'customer_testimonials': 'Customer testimonial',
    'tech_adoption_rating': 'Industry Benchmark Technology Adoption Rating',
    'tam': 'Total Addressable Market (TAM)',
    'sam': 'Serviceable Addressable Market (SAM)',
    'som': 'Serviceable Obtainable Market (SOM)',
    'work_culture_summary': 'Work culture',
    'manager_quality': 'Manager quality',
    'psychological_safety': 'Psychological safety',
    'feedback_culture': 'Feedback culture',
    'diversity_inclusion_score': 'Diversity & inclusion',
    'ethical_standards': 'Ethical standards',
    'typical_hours': 'Typical working hours',
    'overtime_expectations': 'Overtime expectations',
    'weekend_work': 'Weekend work',
    'flexibility_level': 'Remote / hybrid / on-site flexibility',
    'leave_policy': 'Leave policy',
    'burnout_risk': 'Burnout risk',
    'location_centrality': 'Central vs peripheral location',
    'public_transport_access': 'Public transport access',
    'cab_policy': 'Cab availability and company cab policy',
    'airport_commute_time': 'Commute time from airport',
    'office_zone_type': 'Office zone type',
    'area_safety': 'Area safety',
    'safety_policies': 'Company safety policies',
    'infrastructure_safety': 'Office infrastructure safety',
    'emergency_preparedness': 'Emergency response preparedness',
    'health_support': 'Health support',
    'onboarding_quality': 'Onboarding and training quality',
    'learning_culture': 'Learning culture',
    'exposure_quality': 'Exposure quality',
    'mentorship_availability': 'Mentorship availability',
    'internal_mobility': 'Internal mobility',
    'promotion_clarity': 'Promotion clarity',
    'tools_access': 'Tools and technology access',
    'role_clarity': 'Role clarity',
    'early_ownership': 'Early ownership',
    'work_impact': 'Work impact',
    'execution_thinking_balance': 'Execution vs thinking balance',
    'automation_level': 'Automation level',
    'cross_functional_exposure': 'Cross-functional exposure',
    'company_maturity': 'Company maturity',
    'brand_value': 'Brand value',
    'client_quality': 'Client quality',
    'layoff_history': 'Layoff history',
    'fixed_vs_variable_pay': 'Fixed vs variable pay',
    'bonus_predictability': 'Bonus predictability',
    'esops_incentives': 'ESOPs and long-term incentives',
    'family_health_insurance': 'Family health insurance',
    'relocation_support': 'Relocation support',
    'lifestyle_benefits': 'Lifestyle and wellness benefits',
    'exit_opportunities': 'Exit opportunities',
    'skill_relevance': 'Skill relevance',
    'external_recognition': 'External recognition',
    'network_strength': 'Network strength',
    'global_exposure': 'Global exposure',
    'mission_clarity': 'Mission clarity',
    'sustainability_csr': 'Sustainability and CSR',
    'crisis_behavior': 'Crisis behavior'
}

# Reverse mapping: Schema keys -> CSV column name
SCHEMA_KEY_TO_CSV_COLUMN = {v: k for k, v in CSV_HEADER_MAP.items()}

# List of target Fortune 500 companies
FORTUNE_500_COMPANIES = [
    "Accenture plc",
    "Google LLC (Subsidiary of Alphabet Inc.)",
    "Apple Inc.",
    "Mitsubishi UFJ Financial Group, Inc.",
    "Commonwealth Bank of Australia",
    "Tata Consultancy Services Limited",
    "Infosys Limited",
    "Amazon.com, Inc.",
    "Cisco Systems, Inc.",
    "Citigroup Inc.",
    "SAP Labs India Private Limited",
    "Capgemini",
    "JPMorgan Chase & Co.",
    "Airbus SE",
    "Wells Fargo & Company",
    "Dell Technologies Inc.",
    "Walmart Inc.",
    "NVIDIA Corporation",
    "Microsoft Corporation",
    "PayPal Holdings, Inc.",
    "Wipro Limited",
    "Tech Mahindra Limited",
    "Kyndryl Holdings Inc."
]

def calculate_profile_richness(payload: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
    """
    Evaluates profile completeness across the 163-field schema.
    - Check presence and validity of mandatory fields.
    - Calculate score based on all present fields.
    Returns: (validation_success, richness_percentage, missing_mandatory_fields)
    """
    total_fields = len(METADATA_SCHEMA)
    populated_count = 0
    missing_mandatory = []

    for field_name, is_nullable in METADATA_SCHEMA.items():
        # Convert schema key to CSV column key to check the payload
        csv_col = SCHEMA_KEY_TO_CSV_COLUMN.get(field_name)
        val = payload.get(csv_col) if csv_col else None
        
        is_populated = False
        if val is not None:
            if isinstance(val, str):
                val_clean = val.strip()
                if val_clean != "" and val_clean.upper() != "NA" and val_clean.upper() != "NULL":
                    is_populated = True
            else:
                is_populated = True

        if is_populated:
            populated_count += 1
        elif not is_nullable:
            missing_mandatory.append(field_name)

    richness_score = round((populated_count / total_fields) * 100, 2)
    success = len(missing_mandatory) == 0

    return success, richness_score, missing_mandatory

def load_csv_data(filepath: str) -> List[Dict[str, Any]]:
    """Loads CSV file rows as a list of dictionaries."""
    data = []
    if not os.path.exists(filepath):
        return data
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def generate_validation_report(input_csv: str, output_csv: str, output_log: str):
    """
    Validates all companies in the input CSV against the 163-field schema.
    Prints real-time validation results to the terminal.
    Saves a detailed report to output_csv (viewable in Excel) and output_log.
    """
    dataset = load_csv_data(input_csv)
    if not dataset:
        print(f"Error: Input CSV at {input_csv} not found or empty.")
        return
        
    report_rows = []
    log_lines = []
    
    log_lines.append(f"Validation Report for {os.path.basename(input_csv)}")
    log_lines.append("="*80)
    
    print(f"\nProcessing {len(dataset)} companies from {input_csv}...")
    print(f"{'Company Name':<50} | {'Passed':<6} | {'Failed':<6} | {'Richness':<8} | {'Status':<8}")
    print("-" * 88)
    
    for row in dataset:
        company_name = row.get("name", "Unknown Company")
        
        # Calculate completeness
        success, richness_score, missing_mandatory = calculate_profile_richness(row)
        
        # Find all missing optional fields as well
        missing_optional = []
        passed_count = 0
        failed_count = 0
        
        for field_name, is_nullable in METADATA_SCHEMA.items():
            csv_col = SCHEMA_KEY_TO_CSV_COLUMN.get(field_name)
            val = row.get(csv_col) if csv_col else None
            
            is_populated = False
            if val is not None:
                if isinstance(val, str):
                    val_clean = val.strip()
                    if val_clean != "" and val_clean.upper() != "NA" and val_clean.upper() != "NULL":
                        is_populated = True
                else:
                    is_populated = True
                    
            if is_populated:
                passed_count += 1
            else:
                failed_count += 1
                if is_nullable:
                    missing_optional.append(field_name)
                    
        status_str = "PASSED" if success else "FAILED"
        
        # Print runtime message in terminal
        print(f"{company_name[:50]:<50} | {passed_count:<6} | {failed_count:<6} | {richness_score:<7}% | {status_str:<8}")
        
        # Build log line
        log_line = (
            f"Company: {company_name}\n"
            f"  Status: {status_str}\n"
            f"  Passed Parameters: {passed_count} / 163\n"
            f"  Failed/Missing Parameters: {failed_count} / 163\n"
            f"  Richness Score: {richness_score}%\n"
        )
        if missing_mandatory:
            log_line += f"  Missing Mandatory: {', '.join(missing_mandatory)}\n"
        if missing_optional:
            # show first 10 missing optionals in log summary, keep it concise
            log_line += f"  Missing Optional (first 10): {', '.join(missing_optional[:10])}...\n"
        log_line += "-" * 50
        log_lines.append(log_line)
        
        # Build report row for CSV (Excel)
        report_rows.append({
            "Company Name": company_name,
            "Validation Status": status_str,
            "Parameters Passed": passed_count,
            "Parameters Failed": failed_count,
            "Total Parameters": 163,
            "Richness Score (%)": richness_score,
            "Missing Mandatory": "; ".join(missing_mandatory),
            "Missing Optional": "; ".join(missing_optional)
        })
        
    # Write to CSV (Excel format)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=[
            "Company Name", "Validation Status", "Parameters Passed", "Parameters Failed",
            "Total Parameters", "Richness Score (%)", "Missing Mandatory", "Missing Optional"
        ])
        writer.writeheader()
        writer.writerows(report_rows)
        
    # Write to Log
    with open(output_log, mode="w", encoding="utf-8") as f_log:
        f_log.write("\n".join(log_lines))
        
    print(f"\n✓ Report saved to CSV: {output_csv} (Excel compatible)")
    print(f"✓ Report saved to Log: {output_log}")


# --- Pytest Tests ---

def test_fortune500_dataset_comprehensive_completeness():
    """
    Verifies that all Fortune 500 companies in the generated 2.1.csv 
    have a 100% data richness score (all 163 fields populated).
    """
    csv_path = os.path.join(os.path.dirname(__file__), "2.1.csv")
    dataset = load_csv_data(csv_path)
    
    assert len(dataset) > 0, f"Completed dataset at {csv_path} is empty or missing."
    
    for row in dataset:
        company_name = row.get("name")
        success, richness_score, missing = calculate_profile_richness(row)
        
        assert success is True, f"{company_name} failed validation. Missing mandatory fields: {missing}"
        assert richness_score == 100.0, f"{company_name} richness score is {richness_score}%, expected 100.0%."

def test_master_dataset_fortune500_richness_boundaries():
    """
    Verifies that in the main companies_master.csv file:
    - All target Fortune 500 companies have at least 135+ fields populated.
    - Top-tier Fortune 500 companies have 150+ fields populated.
    - All mandatory fields in the schema are populated.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "../../companies_master.csv")
    dataset = load_csv_data(csv_path)
    
    assert len(dataset) > 0, f"Master dataset at {csv_path} is empty or missing."
    
    tested_count = 0
    for row in dataset:
        company_name = row.get("name")
        if company_name in FORTUNE_500_COMPANIES:
            tested_count += 1
            success, richness_score, missing = calculate_profile_richness(row)
            
            # Count of populated fields: richness_score% of 163 fields
            populated_fields_count = round((richness_score / 100.0) * len(METADATA_SCHEMA))
            
            assert success is True, f"Master profile for {company_name} is missing mandatory fields: {missing}"
            
            # Ensure absolute minimum of 135+ populated fields for any Fortune 500 in master
            assert populated_fields_count >= 135, (
                f"Master profile for {company_name} only has {populated_fields_count} fields populated. "
                f"Expected at least 135. Richness score: {richness_score}%"
            )
            
            # For known top-tier populated ones, verify 150+
            if company_name not in ["PayPal Holdings, Inc.", "Kyndryl Holdings Inc.", "Tech Mahindra Limited"]:
                assert populated_fields_count >= 150, (
                    f"Top-tier master profile for {company_name} only has {populated_fields_count} fields. "
                    f"Expected at least 150. Richness score: {richness_score}%"
                )
            
    assert tested_count == len(FORTUNE_500_COMPANIES), (
        f"Only found {tested_count} out of {len(FORTUNE_500_COMPANIES)} target Fortune 500 companies in master CSV."
    )

def test_missing_mandatory_field_causes_validation_failure():
    """
    Verifies that if any mandatory field is missing/empty, validation fails.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "2.1.csv")
    dataset = load_csv_data(csv_path)
    
    assert len(dataset) > 0
    # Take the first record and mutate it (e.g. set mandatory "name" to empty)
    mutated_row = dataset[0].copy()
    mutated_row["name"] = ""
    
    success, richness_score, missing = calculate_profile_richness(mutated_row)
    assert success is False
    assert "Company Name" in missing
    assert richness_score < 100.0

def test_missing_optional_field_fails_only_score_richness():
    """
    Verifies that missing an optional field doesn't fail validation,
    but decreases the richness score.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "2.1.csv")
    dataset = load_csv_data(csv_path)
    
    assert len(dataset) > 0
    # Take first record and clear an optional field (e.g. "short_name")
    mutated_row = dataset[0].copy()
    mutated_row["short_name"] = "NA"
    
    success, richness_score, missing = calculate_profile_richness(mutated_row)
    assert success is True
    assert len(missing) == 0
    assert richness_score < 100.0

if __name__ == "__main__":
    import sys
    
    # Paths for files
    dir_path = os.path.dirname(os.path.abspath(__file__))
    master_csv_path = os.path.join(dir_path, "../../companies_master.csv")
    completed_csv_path = os.path.join(dir_path, "2.1.csv")
    
    master_out_csv = os.path.join(dir_path, "2.1_master_validation_results.csv")
    master_out_log = os.path.join(dir_path, "2.1_master_validation_results.log")
    
    completed_out_csv = os.path.join(dir_path, "2.1_completed_validation_results.csv")
    completed_out_log = os.path.join(dir_path, "2.1_completed_validation_results.log")
    
    print("=" * 90)
    print("1. GENERATING VALIDATION REPORT FOR MASTER DATASET (ALL 116 COMPANIES)")
    print("=" * 90)
    generate_validation_report(master_csv_path, master_out_csv, master_out_log)
    
    print("\n" + "=" * 90)
    print("2. GENERATING VALIDATION REPORT FOR COMPLETED FORTUNE 500 DATASET")
    print("=" * 90)
    generate_validation_report(completed_csv_path, completed_out_csv, completed_out_log)
    
    print("\n" + "=" * 90)
    print("3. RUNNING CRITICAL SYSTEM TEST SUITE ASSERTIONS")
    print("=" * 90)
    
    try:
        test_fortune500_dataset_comprehensive_completeness()
        print("✓ test_fortune500_dataset_comprehensive_completeness: PASSED")
        test_master_dataset_fortune500_richness_boundaries()
        print("✓ test_master_dataset_fortune500_richness_boundaries: PASSED")
        test_missing_mandatory_field_causes_validation_failure()
        print("✓ test_missing_mandatory_field_causes_validation_failure: PASSED")
        test_missing_optional_field_fails_only_score_richness()
        print("✓ test_missing_optional_field_fails_only_score_richness: PASSED")
        print("\nAll assertions passed successfully! Validation process complete.")
    except AssertionError as e:
        print("\n✗ Critical system test assertion failed:", e)
        sys.exit(1)


