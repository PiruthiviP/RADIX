// Company data types for SRM Placements Portal

export type CompanyCategory = 'Marquee' | 'SuperDream' | 'Dream' | 'Regular' | 'Enterprise';

export interface CompanyShort {
  company_id: number;
  name: string;
  short_name: string;
  logo_url: string;
  category: string;
  operating_countries: string;
  office_locations: string;
  employee_size: string;
  yoy_growth_rate: string;
}

export interface CompanyFull {
  company_id: number;
  name: string;
  short_name: string;
  logo_url: string;
  category: string;
  incorporation_year: number;
  overview_text: string;
  nature_of_company: string;
  headquarters_address: string;
  operating_countries: string;
  office_count: string;
  office_locations: string;
  employee_size: string;
  hiring_velocity: string;
  employee_turnover: string;
  avg_retention_tenure: string;
  pain_points_addressed: string;
  focus_sectors: string;
  offerings_description: string;
  top_customers: string;
  core_value_proposition: string;
  vision_statement: string;
  mission_statement: string;
  core_values: string;
  unique_differentiators: string;
  competitive_advantages: string;
  weaknesses_gaps: string;
  key_challenges_needs: string;
  key_competitors: string;
  technology_partners: string;
  history_timeline: string;
  recent_news: string;
  website_url: string;
  website_quality: string;
  website_rating: string;
  website_traffic_rank: string;
  social_media_followers: number;
  glassdoor_rating: number;
  indeed_rating: number;
  google_rating: number;
  linkedin_url: string;
  twitter_handle: string;
  facebook_url: string;
  instagram_url: string;
  ceo_name: string;
  ceo_linkedin_url: string;
  key_leaders: string;
  warm_intro_pathways: string;
  decision_maker_access: string;
  primary_contact_email: string;
  primary_phone_number: string;
  contact_person_name: string;
  contact_person_title: string;
  contact_person_email: string;
  contact_person_phone: string;
  awards_recognitions: string;
  brand_sentiment_score: string;
  event_participation: string;
  regulatory_status: string;
  legal_issues: string;
  annual_revenue: string;
  annual_profit: string;
  revenue_mix: string;
  valuation: string;
  yoy_growth_rate: number;
  profitability_status: string;
  market_share_percentage: string;
  key_investors: string;
  recent_funding_rounds: string;
  total_capital_raised: string;
  esg_ratings: string;
  sales_motion: string;
  customer_acquisition_cost: string;
  customer_lifetime_value: string;
  cac_ltv_ratio: string;
  churn_rate: string;
  net_promoter_score: number;
  customer_concentration_risk: string;
  burn_rate: string;
  runway_months: string;
  burn_multiplier: string;
  intellectual_property: string;
  r_and_d_investment: string;
  ai_ml_adoption_level: string;
  tech_stack: string;
  cybersecurity_posture: string;
  supply_chain_dependencies: string;
  geopolitical_risks: string;
  macro_risks: string;
  diversity_metrics: string;
  remote_policy_details: string;
  training_spend: string;
  partnership_ecosystem: string;
  exit_strategy_history: string;
  carbon_footprint: string;
  ethical_sourcing: string;
  benchmark_vs_peers: string;
  future_projections: string;
  strategic_priorities: string;
  industry_associations: string;
  case_studies: string;
  go_to_market_strategy: string;
  innovation_roadmap: string;
  product_pipeline: string;
  board_members: string;
  marketing_video_url: string;
  customer_testimonials: string;
  tech_adoption_rating: string;
  tam: string;
  sam: string;
  som: number;
  work_culture_summary: string;
  manager_quality: string;
  psychological_safety: string;
  feedback_culture: string;
  diversity_inclusion_score: string;
  ethical_standards: string;
  typical_hours: string;
  overtime_expectations: string;
  weekend_work: string;
  flexibility_level: string;
  leave_policy: string;
  burnout_risk: string;
  location_centrality: string;
  public_transport_access: string;
  cab_policy: string;
  airport_commute_time: string;
  office_zone_type: string;
  area_safety: string;
  safety_policies: string;
  infrastructure_safety: string;
  emergency_preparedness: string;
  health_support: string;
  onboarding_quality: string;
  learning_culture: string;
  exposure_quality: string;
  mentorship_availability: string;
  internal_mobility: string;
  promotion_clarity: string;
  tools_access: string;
  role_clarity: string;
  early_ownership: string;
  work_impact: string;
  execution_thinking_balance: string;
  automation_level: string;
  cross_functional_exposure: string;
  company_maturity: string;
  brand_value: string;
  client_quality: string;
  layoff_history: string;
  fixed_vs_variable_pay: string;
  bonus_predictability: string;
  esops_incentives: string;
  family_health_insurance: string;
  relocation_support: string;
  lifestyle_benefits: string;
  exit_opportunities: string;
  skill_relevance: string;
  external_recognition: string;
  network_strength: string;
  global_exposure: string;
  mission_clarity: string;
  sustainability_csr: string;
  crisis_behavior: string;
}

export interface SkillSet {
  skill_set_code: string;
  typical_questions: string;
}

export interface HiringRound {
  round_number: number;
  round_name: string;
  round_category: string;
  evaluation_type: string;
  assessment_mode: string;
  skill_sets: SkillSet[];
}

export interface JobRoleDetail {
  opportunity_type: string;
  role_title: string;
  role_category: string;
  job_description: string;
  compensation: string;
  ctc_or_stipend: number;
  bonus: string;
  benefits_summary: string;
  hiring_rounds: HiringRound[];
}

export interface HiringRoundsData {
  company_name: string;
  job_role_details: JobRoleDetail[];
}

// InnovX Types
export interface IndustryTrend {
  trend_name: string;
  trend_description: string;
  time_horizon_years: number;
  trend_drivers: string[];
  impact_areas: string[];
  strategic_importance: string;
}

export interface InnovationRoadmapItem {
  innovation_theme: string;
  problem_statement: string;
  target_customer: string;
  innovation_type: string;
  time_horizon: string;
  expected_outcome: string;
  required_capabilities: string[];
  dependent_trend_names: string[];
}

export interface Competitor {
  competitor_name: string;
  competitor_type: string;
  core_strength: string;
  market_positioning: string;
  bet_name: string;
  bet_description: string;
  innovation_category: string;
  futuristic_level: string;
  strategic_objective: string;
  threat_level: string;
}

export interface StrategicPillar {
  cto_vision_statement: string;
  pillar_name: string;
  pillar_description: string;
  focus_area: string;
  key_technologies: string[];
  strategic_risks: string;
  strategic_assumptions: string;
}

export interface InnovxProject {
  project_name: string;
  problem_statement: string;
  target_users: string;
  innovation_objective: string;
  tier_level: string;
  differentiation_factor: string;
  aligned_pillar_names: string[];
  architecture_style: string;
  backend_technologies: string[];
  frontend_technologies: string[];
  ai_ml_technologies: string[];
  data_storage_processing: string;
  integrations_apis: string[];
  infrastructure_cloud: string;
  security_compliance: string;
  primary_use_case: string;
  secondary_use_cases: string[];
  scenario_description: string;
  user_journey_summary: string;
  business_value: string;
  success_metrics: string[];
}

export interface InnovxMaster {
  company_name: string;
  industry: string;
  sub_industry: string;
  core_business_model: string;
  target_market: string;
  geographic_focus: string;
}

export interface InnovxData {
  innovx_master: InnovxMaster;
  industry_trends: IndustryTrend[];
  innovation_roadmap: InnovationRoadmapItem[];
  competitive_landscape: Competitor[];
  strategic_pillars: StrategicPillar[];
  innovx_projects: InnovxProject[];
}
