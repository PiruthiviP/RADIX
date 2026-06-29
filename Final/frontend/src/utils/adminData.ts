import hiringRoundsData from '@/data/Hiring_rounds.json';
import { getCategoryGroup, getCompaniesShort, getCompanySkillLevels } from './data';

export interface AdminCompany {
  id: string;
  name: string;
  category: string;
  coreTheme: string;
  industry: string;
  headquarters: string;
  website: string;
  averagePackageLpa: number;
  roles: string[];
  visitingThisYear: boolean;
}

export interface HiringRound {
  id: string;
  companyId: string;
  round: string;
  sequence: number;
  description: string;
}

export interface InterviewExperience {
  id: string;
  companyId: string;
  role: string;
  year: number;
  status: 'Pending' | 'Approved' | 'Rejected';
}

export interface PlacementDrive {
  id: string;
  companyId: string;
  date: string;
  eligibleBranches: string[];
  cgpa: number;
  role: string;
  packageLpa: number;
}

export interface SkillTag {
  company: string;
  role: string;
  skill: string;
  proficiencyCode: string;
  level: number;
  importance: 'High' | 'Medium' | 'Low';
}

interface HiringRoundEntryRole {
  role_title?: string;
}

interface HiringRoundEntry {
  company_name?: string;
  job_role_details?: HiringRoundEntryRole[];
}

const companiesShort = getCompaniesShort();
const skillLevelsData = getCompanySkillLevels();

const inferSalaryByTheme = (theme: string): number => {
  const map: Record<string, number> = {
    'Software/SaaS/Cloud': 16,
    'Finance/FinTech': 14,
    'Startup/Scale-up': 18,
    'IT Services/Consulting': 7,
    Enterprise: 12,
    'Public/Listed': 11,
    'Healthcare/HealthTech': 12,
    EdTech: 10,
    'Infrastructure/Other': 9,
  };
  return map[theme] ?? 10;
};

const formatSkillTaxonomyName = (skill: string): string => {
  return skill
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

export const studentSkillTaxonomy = skillLevelsData.metadata.skill_categories;
export const studentProficiencyLevels = skillLevelsData.proficiency_levels;

export const adminCompanies: AdminCompany[] = companiesShort.map((company) => {
  const coreTheme = getCategoryGroup(company.category);
  const headquarters = company.office_locations?.split(';')[0]?.trim() || 'N/A';

  const hiringEntry = (hiringRoundsData as HiringRoundEntry[]).find(
    (entry) => entry.company_name?.toLowerCase().trim() === company.name.toLowerCase().trim()
  );
  const roles: string[] = hiringEntry?.job_role_details
    ?.map((r) => r.role_title as string)
    .filter(Boolean)
    .slice(0, 3) ?? [];

  return {
    id: company.id,
    name: company.name,
    category: company.category,
    coreTheme,
    industry: coreTheme,
    headquarters,
    website: company.website_url || company.website || 'N/A',
    averagePackageLpa: inferSalaryByTheme(coreTheme),
    roles: roles.length > 0 ? roles : ['Software Engineering'],
    visitingThisYear: true,
  };
});

export const hiringRounds: HiringRound[] = [
  { id: '1', companyId: 'comp_4', round: 'Online Aptitude Test', sequence: 1, description: 'Quantitative and logical reasoning.' },
  { id: '2', companyId: 'comp_4', round: 'Coding Test', sequence: 2, description: 'DSA-based coding problems.' },
  { id: '3', companyId: 'comp_4', round: 'Technical Interview', sequence: 3, description: 'Problem solving and system thinking.' },
  { id: '4', companyId: 'comp_4', round: 'HR Interview', sequence: 4, description: 'Behavioral and culture fit.' },
  { id: '5', companyId: 'comp_10', round: 'Programming Round', sequence: 1, description: 'Language and fundamentals test.' },
  { id: '6', companyId: 'comp_10', round: 'Advanced Coding', sequence: 2, description: 'Algorithmic coding and optimization.' },
  { id: '7', companyId: 'comp_10', round: 'Technical Panel', sequence: 3, description: 'Project and applied engineering discussion.' },
];

export const interviewExperiences: InterviewExperience[] = [
  { id: 'e1', companyId: 'comp_4', role: 'Software Engineering', year: 2025, status: 'Pending' },
  { id: 'e2', companyId: 'comp_10', role: 'Data Structures And Algorithms', year: 2025, status: 'Approved' },
  { id: 'e3', companyId: 'comp_11', role: 'Software Engineering', year: 2024, status: 'Rejected' },
  { id: 'e4', companyId: 'comp_14', role: 'System Design And Architecture', year: 2025, status: 'Pending' },
];

export const placementDrives: PlacementDrive[] = [
  {
    id: 'd1',
    companyId: 'comp_4',
    date: '2026-08-21',
    eligibleBranches: ['CSE', 'IT'],
    cgpa: 8.0,
    role: 'Software Engineering',
    packageLpa: 22,
  },
  {
    id: 'd2',
    companyId: 'comp_10',
    date: '2026-07-30',
    eligibleBranches: ['CSE', 'IT', 'ECE', 'EEE'],
    cgpa: 6.5,
    role: 'Data Structures And Algorithms',
    packageLpa: 8,
  },
  {
    id: 'd3',
    companyId: 'comp_14',
    date: '2026-09-10',
    eligibleBranches: ['CSE', 'IT'],
    cgpa: 7.5,
    role: 'System Design And Architecture',
    packageLpa: 18,
  },
];

export const skillTags: SkillTag[] = skillLevelsData.companies.flatMap((company) =>
  Object.entries(company.skills).map(([skill, detail]) => ({
    company: company.company,
    role: 'General Hiring Expectation',
    skill: formatSkillTaxonomyName(skill),
    proficiencyCode: detail.proficiency_code,
    level: detail.level,
    importance: detail.level >= 7 ? 'High' : detail.level >= 5 ? 'Medium' : 'Low',
  }))
);

export const coreThemeDistribution = Object.entries(
  adminCompanies.reduce<Record<string, number>>((acc, company) => {
    acc[company.coreTheme] = (acc[company.coreTheme] ?? 0) + 1;
    return acc;
  }, {})
)
  .map(([theme, companies]) => ({ theme, companies }))
  .sort((a, b) => b.companies - a.companies);

export const hiringRoundDistribution = [
  { round: 'Aptitude', count: 3 },
  { round: 'Coding', count: 4 },
  { round: 'Technical', count: 3 },
  { round: 'HR', count: 2 },
];

export const placementTrend = [
  { year: 2022, placed: 980 },
  { year: 2023, placed: 1120 },
  { year: 2024, placed: 1250 },
  { year: 2025, placed: 1390 },
];

export const getCompanyName = (companyId: string): string => {
  return adminCompanies.find((company) => company.id === companyId)?.name ?? companyId;
};

export const getAdminSummaryStats = () => {
  const totalCompanies = adminCompanies.length;
  const visitingThisYear = adminCompanies.filter((company) => company.visitingThisYear).length;
  const totalRoles = adminCompanies.reduce((sum, company) => sum + company.roles.length, 0);
  const totalExperiences = interviewExperiences.length;

  const skillScoreMap = skillTags.reduce<Record<string, { totalLevel: number; count: number }>>((acc, item) => {
    const existing = acc[item.skill] ?? { totalLevel: 0, count: 0 };
    existing.totalLevel += item.level;
    existing.count += 1;
    acc[item.skill] = existing;
    return acc;
  }, {});

  const topSkills = Object.entries(skillScoreMap)
    .map(([skill, value]) => ({ skill, score: Number((value.totalLevel / value.count).toFixed(1)) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  return {
    totalCompanies,
    visitingThisYear,
    totalRoles,
    totalExperiences,
    topSkills,
  };
};
