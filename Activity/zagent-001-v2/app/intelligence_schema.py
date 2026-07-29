from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

@dataclass(frozen=True)
class FieldSpec:
    name: str
    field_type: str  # "string", "url", "year", "enum", "list"
    batch: str       # "admin", "core_identity", "digital_presence", etc.
    description: str
    enum_values: Optional[List[str]] = None
    is_admin_grounded: bool = False

# The 13 admin-grounded fields
ADMIN_FIELDS_RAW = [
    ("companyName", "string", "Full legal/official name of the entity"),
    ("shortName", "string", "Commonly used short/abbreviated name"),
    ("websiteUrl", "url", "Primary headquarters website or home URL"),
    ("logo", "url", "Representative logo URL or image link"),
    ("yearOfIncorporation", "year", "Year the company was legally incorporated/founded"),
    ("companyHeadquarters", "string", "Primary headquarters address and location"),
    ("countriesOperatingIn", "list", "List of countries where the company actively operates"),
    ("natureOfCompany", "enum", "Ownership structure (Private, Public, Subsidiary, Government, Non-profit, Other)"),
    ("categoryIndustry", "string", "Primary business category or sector classification"),
    ("servicesProductsOfferings", "list", "Core products, services, or offerings provided"),
    ("employeeSize", "string", "Total headcount/employee size range"),
    ("ceoName", "string", "Name of the current CEO/highest executive officer"),
    ("linkedInProfileUrl", "url", "LinkedIn company profile page URL")
]

# The 6 batches containing 152 fields total
BATCH_DEFINITIONS: Dict[str, List[str]] = {
    "core_identity": [
        "legal_entity_type", "founding_story", "founders", "parent_company",
        "ownership_structure", "board_chair", "executive_team_overview", "mission_statement",
        "vision_statement", "company_values", "primary_business_model", "target_customer_segments",
        "primary_geographies", "hq_city", "hq_country", "registered_office",
        "top_subsidiaries", "business_units", "core_capabilities", "value_proposition",
        "market_positioning", "key_differentiators", "top_competitors", "industry_verticals",
        "regulatory_status", "brand_tagline"
    ],
    "digital_presence": [
        "linkedin_company_page", "twitter_handle", "youtube_channel", "facebook_page",
        "instagram_handle", "app_store_presence", "play_store_presence", "developer_portal_url",
        "documentation_url", "status_page_url", "support_portal_url", "community_forum_url",
        "newsletter_url", "blog_url", "podcast_presence", "press_room_url",
        "seo_strength", "domain_authority_estimate", "monthly_web_traffic_estimate", "top_traffic_countries",
        "top_traffic_channels", "email_contact_pattern", "careers_page_url", "glassdoor_presence",
        "g2_profile_url"
    ],
    "financial_intelligence": [
        "annual_revenue", "revenue_currency", "revenue_growth_rate", "profitability_status",
        "ebitda_margin", "funding_total", "latest_funding_round", "latest_round_date",
        "lead_investors", "valuation_estimate", "cash_flow_health", "debt_level",
        "burn_rate_estimate", "runway_estimate", "arr_estimate", "capex_intensity",
        "top_revenue_streams", "customer_concentration_risk", "pricing_model", "contract_terms",
        "average_contract_value", "gross_margin_profile", "financial_reporting_quality", "credit_risk_level",
        "mna_activity_recent", "ipo_readiness_signal"
    ],
    "strategy_ecosystem": [
        "strategic_priorities", "product_roadmap_signal", "innovation_focus_areas", "ai_adoption_maturity",
        "cloud_strategy", "technology_stack_overview", "core_patents", "strategic_partnerships",
        "channel_partners", "supplier_dependencies", "ecosystem_role", "go_to_market_motion",
        "sales_model", "customer_success_model", "expansion_strategy", "internationalization_stage",
        "regulatory_exposure", "cybersecurity_posture", "data_privacy_posture", "esg_commitment_level",
        "sustainability_initiatives", "major_risks", "risk_mitigation_strategies", "litigation_exposure",
        "disruption_threat_level"
    ],
    "work_culture": [
        "workforce_distribution", "hiring_velocity", "attrition_signal", "compensation_positioning",
        "benefits_quality", "remote_work_policy", "hybrid_policy", "learning_programs",
        "leadership_style_signal", "diversity_inclusion_signal", "employee_sentiment", "internal_mobility_strength",
        "performance_management_style", "manager_quality_signal", "engineering_culture_signal", "product_culture_signal",
        "sales_culture_signal", "wellbeing_programs", "culture_keywords", "employer_brand_strength",
        "glassdoor_rating_estimate", "interview_difficulty_signal", "work_life_balance_signal", "collaboration_style",
        "decision_making_style"
    ],
    "career_growth": [
        "top_job_families", "critical_hiring_roles", "entry_level_opportunities", "internship_program",
        "career_progression_paths", "promotion_velocity_signal", "manager_to_ic_ratio", "technical_ladder_maturity",
        "leadership_development_program", "mentorship_availability", "certification_support", "tuition_support",
        "global_mobility_options", "visa_sponsorship_signal", "compensation_growth_outlook", "equity_policy_signal",
        "retention_risk_roles", "skills_in_high_demand", "future_skills_focus", "talent_brand_narrative",
        "candidate_experience_signal", "offer_acceptance_signal", "alumni_network_strength", "career_stability_outlook",
        "growth_opportunity_index"
    ]
}

class SchemaManager:
    def __init__(self):
        self.fields: Dict[str, FieldSpec] = {}
        self._build_schema()

    def _build_schema(self) -> None:
        # 1. Build admin fields
        for name, f_type, desc in ADMIN_FIELDS_RAW:
            enum_vals = None
            if name == "natureOfCompany":
                enum_vals = ["Private", "Public", "Subsidiary", "Government", "Non-profit", "Other"]
            
            self.fields[name] = FieldSpec(
                name=name,
                field_type=f_type,
                batch="admin",
                description=desc,
                enum_values=enum_vals,
                is_admin_grounded=True
            )

        # 2. Build generated fields
        for batch_name, field_list in BATCH_DEFINITIONS.items():
            for name in field_list:
                f_type = self._infer_field_type(name)
                enum_vals = self._get_enum_values(name, f_type)
                desc = self._generate_description(name)
                
                self.fields[name] = FieldSpec(
                    name=name,
                    field_type=f_type,
                    batch=batch_name,
                    description=desc,
                    enum_values=enum_vals,
                    is_admin_grounded=False
                )

    def _infer_field_type(self, name: str) -> str:
        # Infer field types based on naming convention
        if name.endswith("_url") or name.endswith("_presence") and ("presence" in name and ("page" in name or "presence" in name)):
            # Wait, linkedin_company_page or g2_profile_url or careers_page_url is url
            if "page" in name or "profile" in name or "channel" in name or "url" in name:
                return "url"
        if name.endswith("_url"):
            return "url"
        
        # Matches rate, margin, estimate, index to string
        for kw in ["rate", "margin", "estimate", "index"]:
            if kw in name:
                return "string"
        
        # Matches policies to enum
        # remote_work_policy, hybrid_policy, internship_program to enum
        if name in ["remote_work_policy", "hybrid_policy", "internship_program"]:
            return "enum"
        
        # Matches collections to list
        # top_traffic_countries, top_traffic_channels, top_subsidiaries, etc.
        collections_keywords = [
            "countries", "channels", "founders", "subsidiaries", "units",
            "competitors", "verticals", "streams", "investors", "priorities",
            "areas", "partners", "dependencies", "risks", "strategies",
            "programs", "keywords", "families", "roles", "opportunities",
            "paths", "skills"
        ]
        for kw in collections_keywords:
            if kw in name:
                return "list"
                
        return "string"

    def _get_enum_values(self, name: str, f_type: str) -> Optional[List[str]]:
        if f_type != "enum":
            return None
        if name == "remote_work_policy":
            return ["Onsite", "Hybrid", "Remote", "Flexible", "Unknown"]
        elif name == "hybrid_policy":
            return ["Flexible", "Structured", "Not Applicable", "Unknown"]
        elif name == "internship_program":
            return ["Yes", "No", "Unknown"]
        return ["Yes", "No", "Flexible", "Unknown"]  # Default enum values fallback

    def _generate_description(self, name: str) -> str:
        # Generates a human-friendly description based on the field name
        parts = name.replace("_", " ").split()
        return " ".join(p.capitalize() for p in parts)

    def totals(self) -> Tuple[int, int, int]:
        """Returns counts of (admin_grounded, generated, total) fields."""
        admin_count = sum(1 for f in self.fields.values() if f.is_admin_grounded)
        gen_count = sum(1 for f in self.fields.values() if not f.is_admin_grounded)
        return admin_count, gen_count, len(self.fields)

    def get_fields_by_batch(self, batch_name: str) -> List[FieldSpec]:
        return [f for f in self.fields.values() if f.batch == batch_name]
