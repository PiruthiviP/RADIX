import companiesShort from '@/data/company_short.json';
import companiesFull from '@/data/company_full.json';
import hiringRounds from '@/data/Hiring_rounds.json';
import innovxMaster from '@/data/innovx_master.json';
import companySkillLevels from '@/data/company_skill_levels.json';

export interface CompanyShort {
  company_id?: number;
  id?: string;
  name: string;
  short_name: string;
  logo_url: string;
  website_url?: string;
  website?: string;
  category: string;
  employee_size: string;
  operating_countries: string;
  office_locations: string;
  yoy_growth_rate: string | number;
}

export interface CompanyFull extends CompanyShort {
  overview_text?: string;
  vision_statement?: string;
  mission_statement?: string;
  core_values?: string;
  incorporation_year?: number | string;
  founded_year?: number | string;
  headquarters_address?: string;
  headquarters?: string;
  nature_of_company?: string;
  office_count?: string;
  unique_differentiators?: string;
  history_timeline?: string;
  recent_news?: string;
  awards_recognitions?: string;
  brand_positioning?: string;
  target_markets?: string;
  market_share?: string;
  competitive_advantages?: string;
  key_competitors?: string;
  tam?: string | number;
  sam?: string | number;
  som?: string | number;
  market_share_percentage?: string | number;
  focus_sectors?: string;
  weaknesses_gaps?: string;
  key_challenges_needs?: string;
  top_customers?: string;
  core_value_proposition?: string;
  pain_points_addressed?: string;
  net_promoter_score?: number | string;
  churn_rate?: string;
  customer_lifetime_value?: string;
  customer_acquisition_cost?: string;
  business_model?: string;
  revenue_streams?: string;
  offerings_description?: string;
  product_pipeline?: string;
  go_to_market_strategy?: string;
  sales_motion?: string;
  cac_ltv_ratio?: string;
  key_leaders?: string;
  board_members?: string;
  leadership_style?: string;
  ceo_name?: string;
  ceo_linkedin_url?: string;
  cfo_name?: string;
  cto_name?: string;
  coo_name?: string;
  contact_person_name?: string;
  contact_person_title?: string;
  primary_phone_number?: string;
  contact_person_phone?: string;
  warm_intro_pathways?: string;
  decision_maker_access?: string;
  revenue?: string;
  profitability?: string;
  annual_revenue?: string;
  annual_profit?: string;
  profitability_status?: string;
  revenue_mix?: string;
  key_investors?: string;
  funding_stage?: string;
  capital_structure?: string;
  cash_flow?: string;
  valuation?: string;
  burn_rate?: string;
  runway_months?: string;
  burn_multiplier?: string;
  tech_stack?: string;
  cloud_infrastructure?: string;
  ai_adoption_level?: string;
  ai_maturity_stage?: string;
  ai_use_cases?: string;
  automation_tools?: string;
  ml_frameworks?: string;
  data_infrastructure?: string;
  cyber_security_posture?: string;
  patents?: string;
  technology_partnerships?: string;
  r_and_d_investment?: string;
  r_and_d_focus_areas?: string;
  work_culture?: string;
  dei_initiatives?: string;
  diversity_metrics?: string;
  learning_development_programs?: string;
  employee_benefits?: string;
  avg_retention_tenure?: string;
  employee_turnover?: string;
  hiring_velocity?: string;
  training_budget_per_employee?: string;
  mentorship_program?: string;
  compensation_philosophy?: string;
  performance_bonus_structure?: string;
  hybrid_remote_policy?: string;
  workplace_safety_record?: string;
  employee_satisfaction?: string;
  attrition_rate?: string;
  esg_ratings?: string;
  sustainability_goals?: string;
  environmental_commitment?: string;
  governance_model?: string;
  compliance_certifications?: string;
  cybersecurity_posture?: string;
  geopolitical_risks?: string;
  macro_risks?: string;
  crisis_history?: string;
  supply_chain_dependencies?: string;
  strategic_priorities?: string;
  innovation_roadmap?: string;
  growth_trajectory?: string;
  future_outlook?: string;
  market_expansion_plans?: string;
  market_opportunities?: string;
  competitive_threats?: string;
  strategic_partnerships?: string;
  joint_ventures?: string;
  partnership_opportunities?: string;
  linkedin_url?: string;
  twitter_handle?: string;
  instagram_handle?: string;
  primary_contact_email?: string;
  contact_person_email?: string;
  phone?: string;
  [key: string]: string | number | boolean | null | undefined | string[];
}

interface HiringRoundSkill {
  skill_set_code?: string;
  typical_questions?: string;
}

interface HiringRound {
  round_number?: number;
  round_name?: string;
  round_category?: string;
  evaluation_type?: string;
  assessment_mode?: string;
  skill_sets?: HiringRoundSkill[];
}

interface HiringRole {
  role_title?: string;
  role_category?: string;
  opportunity_type?: string;
  job_description?: string;
  compensation?: string;
  ctc_or_stipend?: number;
  bonus?: string;
  benefits_summary?: string;
  hiring_rounds?: HiringRound[];
}

interface HiringRoundsEntry {
  company_name?: string;
  job_role_details?: HiringRole[];
}

interface InnovxEntry {
  innovx_master?: {
    company_name?: string;
  };
  industry_trends?: Array<{
    trend_name: string;
    trend_description: string;
    trend_drivers: string[];
  }>;
  competitive_landscape?: Array<{
    competitor_name: string;
    market_positioning: string;
    innovation_category: string;
    threat_level: string;
  }>;
  innovation_roadmap?: Array<{
    innovation_theme: string;
    problem_statement: string;
    innovation_type: string;
    time_horizon: string;
  }>;
  innovx_projects?: Array<{
    tier_level: string;
    project_name: string;
    problem_statement: string;
    backend_technologies: string[];
    business_value: string;
  }>;
}

type RawCompany = Partial<CompanyFull> & {
  id?: string | number;
  company_id?: string | number;
};

const normalizeCompanyId = (id: string | number | undefined): string | undefined => {
  if (id === undefined || id === null) return undefined;
  const idString = String(id).trim();
  if (!idString) return undefined;
  return idString.startsWith('comp_') ? idString : `comp_${idString}`;
};

const extractFirstHttpUrl = (rawValue: string): string => {
  const markdownLinkMatch = rawValue.match(/\((https?:\/\/[^\s)]+)\)/i);
  const base = markdownLinkMatch?.[1] || rawValue;

  const withoutOuterBrackets =
    base.startsWith('[') && base.endsWith(']') ? base.slice(1, -1) : base;

  const parts = withoutOuterBrackets
    .split(/[;,]\s*/)
    .map((part) => part.trim().replace(/^['"]|['"]$/g, ''))
    .filter(Boolean);

  const firstValid = parts.find((part) => /^https?:\/\//i.test(part));
  if (firstValid) return firstValid;

  const directMatch = withoutOuterBrackets.match(/https?:\/\/[^\s;,)\]]+/i);
  return directMatch?.[0] || '';
};

const extractDomain = (urlValue: string): string => {
  const cleaned = extractFirstHttpUrl(urlValue);
  const fallbackCleaned = cleaned || urlValue.trim();
  if (!fallbackCleaned) return '';

  try {
    const normalized = /^https?:\/\//i.test(fallbackCleaned)
      ? fallbackCleaned
      : `https://${fallbackCleaned}`;
    const hostname = new URL(normalized).hostname.toLowerCase();
    return hostname.replace(/^www\./, '');
  } catch {
    return '';
  }
};

const extractDomainFromEmail = (email?: string): string => {
  if (!email || typeof email !== 'string') return '';
  const match = email.trim().match(/@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$/);
  return match?.[1]?.toLowerCase() || '';
};

export const getClearbitLogoUrl = (websiteUrl?: string): string => {
  if (!websiteUrl) return '';
  const domain = extractDomain(websiteUrl);
  return domain ? `https://www.google.com/s2/favicons?domain=${domain}&sz=256` : '';
};

export const getRenderableLogoUrl = (logoUrl?: string, websiteUrl?: string): string => {
  const normalizedLogoUrl = logoUrl ? extractFirstHttpUrl(logoUrl.trim()) : '';
  if (normalizedLogoUrl) return normalizedLogoUrl;

  if (!websiteUrl) return '';
  const domain = extractDomain(websiteUrl);
  return domain ? `https://www.google.com/s2/favicons?domain=${domain}&sz=256` : '';
};

export const getWebsiteFallbackLogoUrl = (websiteUrl?: string): string => {
  if (!websiteUrl) return '';
  const domain = extractDomain(websiteUrl);
  return domain ? `https://www.google.com/s2/favicons?domain=${domain}&sz=128` : '';
};

// Normalize company ID
const normalizeCompany = (company: RawCompany): CompanyFull & { id: string } => {
  const normalizedId = normalizeCompanyId(company.id ?? company.company_id);
  return {
    ...(company as CompanyFull),
    id: normalizedId || '',
  };
};

export const getCompaniesShort = (): (CompanyShort & { id: string })[] => {
  const fullCompanies = Array.isArray(companiesFull) ? companiesFull : [companiesFull];
  const fullById = new Map(
    fullCompanies.map(normalizeCompany).map((company) => [company.id, company])
  );

  const companies = Array.isArray(companiesShort) ? companiesShort : [companiesShort];
  return companies.map(normalizeCompany).map((company) => {
    const fullCompany = fullById.get(company.id);
    if (!fullCompany) return company;

    const derivedWebsiteFromEmail =
      extractDomainFromEmail(fullCompany.primary_contact_email) ||
      extractDomainFromEmail(fullCompany.contact_person_email);

    return {
      ...company,
      website_url:
        company.website_url ||
        fullCompany.website_url ||
        fullCompany.website ||
        (derivedWebsiteFromEmail ? `https://${derivedWebsiteFromEmail}` : undefined),
    };
  });
};

export const getCompaniesFull = (): (CompanyFull & { id: string })[] => {
  const companies = Array.isArray(companiesFull) ? companiesFull : [companiesFull];
  return companies.map(normalizeCompany);
};

export const getCompanyById = (id: string): (CompanyFull & { id: string }) | undefined => {
  const normalizedSearchId = normalizeCompanyId(id);
  return getCompaniesFull().find((company) => company.id === normalizedSearchId);
};

export const searchCompanies = (query: string): (CompanyShort & { id: string })[] => {
  const lowerQuery = query.toLowerCase();
  return getCompaniesShort().filter(
    (company) =>
      company.name.toLowerCase().includes(lowerQuery) ||
      company.short_name.toLowerCase().includes(lowerQuery)
  );
};

export const getHiringRoundsData = (companyName?: string) => {
  if (!companyName) return undefined;
  const data = (Array.isArray(hiringRounds) ? hiringRounds : [hiringRounds]) as HiringRoundsEntry[];
  const normalizedSearch = companyName.toLowerCase().trim();
  return data.find((company) => 
    company.company_name?.toLowerCase().trim() === normalizedSearch
  );
};

export const getInnovxDataForCompany = (companyName?: string) => {
  if (!companyName) return undefined;
  const data = (innovxMaster.companies || []) as InnovxEntry[];
  const normalizedSearch = companyName.toLowerCase().trim();
  return data.find((company) => 
    company.innovx_master?.company_name?.toLowerCase().trim() === normalizedSearch
  );
};

export const categorizeCompanies = (companies: (CompanyShort & { id: string })[]) => {
  // Categorize by employee size for dashboard
  const marquee = companies.filter((c) => {
    const size = c.employee_size.toLowerCase();
    return size.includes('thousand') || size.includes('million') || parseInt(size) > 100000;
  });
  
  const parseGrowth = (rate: string | number): number => {
    if (typeof rate === 'number') return rate;
    return parseFloat(rate.toString().replace('%', '')) || 0;
  };
  
  const superDream = companies.filter((c) => parseGrowth(c.yoy_growth_rate) > 15);
  const dream = companies.filter((c) => {
    const growth = parseGrowth(c.yoy_growth_rate);
    return growth > 10 && growth <= 15;
  });
  const regular = companies.filter((c) => parseGrowth(c.yoy_growth_rate) <= 10);

  return { marquee, superDream, dream, regular };
};

export const getStatistics = (companies: (CompanyShort & { id: string })[]) => {
  const parseGrowth = (rate: string | number): number => {
    if (typeof rate === 'number') return rate;
    return parseFloat(rate.toString().replace('%', '')) || 0;
  };
  
  const growthRates = companies.map((c) => parseGrowth(c.yoy_growth_rate));
  return {
    total: companies.length,
    avgGrowth: (growthRates.reduce((sum, c) => sum + c, 0) / companies.length).toFixed(1),
    maxGrowth: Math.max(...growthRates).toFixed(1),
  };
};

export const formatPercentage = (value: string | number): string => {
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) return 'N/A';
    return `${value}%`;
  }

  const normalized = value.toString().trim();
  if (!normalized) return '0%';

  const lower = normalized.toLowerCase();
  if (lower === 'n/a' || lower === 'na' || lower === '-') return 'N/A';

  const numericMatch = normalized.match(/[-+]?\d*\.?\d+/);
  if (numericMatch) {
    return `${numericMatch[0]}%`;
  }

  // Fall back to de-duplicated percent symbols for unusual values.
  const compact = normalized.replace(/%+/g, '%');
  return compact.endsWith('%') ? compact : `${compact}%`;
};

// Bloom's Taxonomy levels
export const BLOOM_LEVELS = ['CU', 'AP', 'AN', 'EV', 'CR'] as const;
export type BloomLevel = (typeof BLOOM_LEVELS)[number];

export interface SkillProficiency {
  bloom: BloomLevel;
  level: number; // 1-10
  proficiency: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';
  topics: string[];
}

// Company Skill Levels Types
export interface ProficiencyLevel {
  name: string;
  code: string;
  description: string;
}

export interface SkillDetail {
  level: number;
  proficiency_code: string;
  proficiency_name: string;
  proficiency_description: string;
}

export interface CompanySkills {
  company: string;
  skills: Record<string, SkillDetail>;
}

export interface SkillLevelsData {
  metadata: {
    description: string;
    total_companies: number;
    skill_categories: string[];
    proficiency_levels: ProficiencyLevel[];
    generated_at: string;
  };
  proficiency_levels: ProficiencyLevel[];
  companies: CompanySkills[];
}

// Get company skill levels data
export const getCompanySkillLevels = (): SkillLevelsData => {
  return companySkillLevels as SkillLevelsData;
};

// Get skill levels for a specific company
export const getCompanySkillLevel = (companyName: string): CompanySkills | undefined => {
  const data = getCompanySkillLevels();
  const normalizedSearch = companyName.toLowerCase().trim();
  return data.companies.find((c) => c.company.toLowerCase().trim() === normalizedSearch);
};

// Get average skill level across all companies for a specific skill
export const getAverageSkillLevel = (skillCategory: string): number => {
  const data = getCompanySkillLevels();
  const levels = data.companies
    .map((c) => c.skills[skillCategory]?.level)
    .filter((l) => l !== undefined);
  
  if (levels.length === 0) return 0;
  return levels.reduce((sum, l) => sum + l, 0) / levels.length;
};

// Get skill statistics across all companies
export const getSkillStatistics = () => {
  const data = getCompanySkillLevels();
  const skillStats: Record<string, {
    average: number;
    min: number;
    max: number;
    proficiencyDistribution: Record<string, number>;
  }> = {};

  data.metadata.skill_categories.forEach((skill) => {
    const levels = data.companies
      .map((c) => c.skills[skill])
      .filter((s) => s !== undefined);

    const levelValues = levels.map((s) => s.level);
    const proficiencyCodes = levels.map((s) => s.proficiency_code);

    const distribution: Record<string, number> = {};
    proficiencyCodes.forEach((code) => {
      distribution[code] = (distribution[code] || 0) + 1;
    });

    skillStats[skill] = {
      average: levelValues.reduce((sum, l) => sum + l, 0) / levelValues.length,
      min: Math.min(...levelValues),
      max: Math.max(...levelValues),
      proficiencyDistribution: distribution,
    };
  });

  return skillStats;
};

// Get companies by skill level threshold
export const getCompaniesBySkillLevel = (
  skillCategory: string,
  minLevel: number
): CompanySkills[] => {
  const data = getCompanySkillLevels();
  return data.companies.filter(
    (c) => c.skills[skillCategory]?.level >= minLevel
  );
};

// Mock skills data generator
export const generateMockSkills = (): Record<string, Record<BloomLevel, number>> => {
  const skills = [
    'Python',
    'Java',
    'TypeScript',
    'System Design',
    'Data Structures',
    'Machine Learning',
    'Cloud Architecture',
    'DevOps',
  ];

  const skillsMap: Record<string, Record<BloomLevel, number>> = {};

  skills.forEach((skill) => {
    skillsMap[skill] = {
      CU: Math.floor(Math.random() * 10) + 1,
      AP: Math.floor(Math.random() * 10) + 1,
      AN: Math.floor(Math.random() * 10) + 1,
      EV: Math.floor(Math.random() * 10) + 1,
      CR: Math.floor(Math.random() * 10) + 1,
    };
  });

  return skillsMap;
};

export const getBloomDescription = (level: BloomLevel): string => {
  const descriptions: Record<BloomLevel, string> = {
    CU: 'Conceptual Understanding - Grasp fundamental concepts and terminology',
    AP: 'Application - Apply knowledge to solve practical problems',
    AN: 'Analysis - Break down complex problems and understand relationships',
    EV: 'Evaluation - Make informed judgments based on criteria',
    CR: 'Creation - Develop innovative solutions and frameworks',
  };
  return descriptions[level];
};

// Category grouping by common themes
export const getCategoryGroup = (category: string): string => {
  const lowerCat = category.toLowerCase();

  if (
    lowerCat.includes('startup') ||
    lowerCat.includes('scale-up') ||
    lowerCat.includes('unicorn')
  ) {
    return 'Startup/Scale-up';
  }

  if (
    lowerCat.includes('fintech') ||
    lowerCat.includes('financial services') ||
    lowerCat.includes('banking') ||
    lowerCat.includes('investment') ||
    lowerCat.includes('wealth') ||
    lowerCat.includes('digital payments') ||
    lowerCat.includes('lending')
  ) {
    return 'Finance/FinTech';
  }

  if (
    lowerCat.includes('health') ||
    lowerCat.includes('healthcare') ||
    lowerCat.includes('insurtech') ||
    lowerCat.includes('pharma')
  ) {
    return 'Healthcare/HealthTech';
  }

  if (
    lowerCat.includes('saas') ||
    lowerCat.includes('software') ||
    lowerCat.includes('cloud') ||
    lowerCat.includes('cybersecurity') ||
    lowerCat.includes('artificial intelligence') ||
    lowerCat.includes('technology & ip')
  ) {
    return 'Software/SaaS/Cloud';
  }

  if (
    lowerCat.includes('it services') ||
    lowerCat.includes('consulting') ||
    lowerCat.includes('digital transformation')
  ) {
    return 'IT Services/Consulting';
  }

  if (
    lowerCat.includes('public') ||
    lowerCat.includes('large cap') ||
    lowerCat.includes('publicly listed')
  ) {
    return 'Public/Listed';
  }

  if (
    lowerCat.includes('edtech') ||
    lowerCat.includes('e-learning') ||
    lowerCat.includes('education')
  ) {
    return 'EdTech';
  }

  if (
    lowerCat.includes('aerospace') ||
    lowerCat.includes('logistics') ||
    lowerCat.includes('retail') ||
    lowerCat.includes('telecommunications') ||
    lowerCat.includes('travel') ||
    lowerCat.includes('grocery')
  ) {
    return 'Infrastructure/Other';
  }

  return 'Enterprise';
};
