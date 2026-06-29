import React from 'react';
import Link from 'next/link';
import {
  Brain,
  Briefcase,
  ClipboardList,
  Cpu,
  Leaf,
  Shield,
  Target,
  Users,
  Wallet,
  MapPin,
  Building2,
  TrendingUp,
  Globe,
  Award,
  Code,
  Zap,
  Heart,
  Lightbulb,
  BookOpen,
  AlertTriangle,
} from 'lucide-react';
import { Tabs, Chip } from '../UI';
import { CompanyFull, formatPercentage } from '@/utils/data';
import hiringRoundsMaster from '@/data/Hiring_rounds.json';

interface CompanyTabsProps {
  company: CompanyFull;
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

interface HiringSkillSet {
  skill_set_code: string;
}

interface HiringRoundDetail {
  round_number: number;
  round_name: string;
  round_category: string;
  evaluation_type: string;
  assessment_mode: string;
  skill_sets?: HiringSkillSet[];
}

interface HiringRoleDetail {
  role_title: string;
  role_category: string;
  opportunity_type: string;
  compensation: string;
  ctc_or_stipend: number;
  job_description: string;
  benefits_summary?: string;
  hiring_rounds?: HiringRoundDetail[];
}

interface CompanyHiringEntry {
  company_name: string;
  job_role_details?: HiringRoleDetail[];
}

export default function CompanyTabs({ company, activeTab, onTabChange }: CompanyTabsProps) {
  // Get hiring data for this company
  const hiringData = (hiringRoundsMaster as CompanyHiringEntry[]).find(
    (entry) => 
      entry.company_name === company.name || 
      entry.company_name === company.short_name
  );

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <ClipboardList className="h-4 w-4" /> },
    { id: 'business', label: 'Business & Market', icon: <Briefcase className="h-4 w-4" /> },
    { id: 'leadership', label: 'Leadership', icon: <Users className="h-4 w-4" /> },
    { id: 'financials', label: 'Financials', icon: <Wallet className="h-4 w-4" /> },
    { id: 'technology', label: 'Technology', icon: <Cpu className="h-4 w-4" /> },
    { id: 'culture', label: 'Culture & Work Life', icon: <Leaf className="h-4 w-4" /> },
    { id: 'risk', label: 'Risk & ESG', icon: <Shield className="h-4 w-4" /> },
    { id: 'strategy', label: 'Strategy', icon: <Target className="h-4 w-4" /> },
    { id: 'skills', label: 'Skills & Hiring', icon: <Brain className="h-4 w-4" /> },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
            {/* Company Overview Text */}
            {company.overview_text && (
              <Section title="About the Company" icon={<Building2 className="h-5 w-5" />}>
                <p className="text-slate-700 leading-relaxed">{company.overview_text}</p>
              </Section>
            )}

            {/* Vision, Mission, Values */}
            {(company.vision_statement || company.mission_statement || company.core_values) && (
              <Section title="Vision, Mission & Values" icon={<Target className="h-5 w-5" />}>
                {company.vision_statement && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-slate-900 mb-2">Vision</h4>
                    <p className="text-slate-700">{company.vision_statement}</p>
                  </div>
                )}
                {company.mission_statement && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-slate-900 mb-2">Mission</h4>
                    <p className="text-slate-700">{company.mission_statement}</p>
                  </div>
                )}
                {company.core_values && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2">Core Values</h4>
                    <div className="flex flex-wrap gap-2">
                      {company.core_values.split(';').map((value: string) => (
                        <Chip key={value.trim()} label={value.trim()} variant="accent" />
                      ))}
                    </div>
                  </div>
                )}
              </Section>
            )}

            {/* Company Information */}
            <Section title="Company Information" icon={<ClipboardList className="h-5 w-5" />}>
              <InfoGrid
                data={{
                  'Founded': company.incorporation_year?.toString(),
                  'Headquarters': company.headquarters_address,
                  'Nature': company.nature_of_company,
                  'Employee Size': company.employee_size,
                  'Office Count': company.office_count,
                  'Operating Countries': company.operating_countries,
                }}
              />
            </Section>

            {/* Unique Differentiators */}
            {company.unique_differentiators && (
              <Section title="Unique Differentiators" icon={<Award className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.unique_differentiators.split(';').map((diff: string) => (
                    <Chip key={diff.trim()} label={diff.trim()} variant="accent" />
                  ))}
                </div>
              </Section>
            )}

            {/* Company History */}
            {(company.history_timeline || company.recent_news) && (
              <Section title="Company History & Recent News" icon={<BookOpen className="h-5 w-5" />}>
                {company.history_timeline && (
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-2">
                      {company.history_timeline.split(';').map((item: string, idx: number) => (
                        <Chip key={idx} label={item.trim()} variant="secondary" />
                      ))}
                    </div>
                  </div>
                )}
                {company.recent_news && (
                  <div className="space-y-2">
                    {company.recent_news.split(';').map((news: string, idx: number) => (
                      <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                        <p className="text-sm text-slate-700">{news.trim()}</p>
                      </div>
                    ))}
                  </div>
                )}
              </Section>
            )}

            {/* Awards & Recognition */}
            {company.awards_recognitions && (
              <Section title="Awards & Recognition" icon={<Award className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.awards_recognitions.split(';').map((award: string) => (
                    <Chip key={award.trim()} label={award.trim()} variant="primary" />
                  ))}
                </div>
              </Section>
            )}
          </div>
        );

      case 'business':
        return (
          <div className="space-y-6">
            {/* Market Overview */}
            <Section title="Market Overview" icon={<Globe className="h-5 w-5" />}>
              <InfoGrid
                data={{
                  'TAM': company.tam,
                  'SAM': company.sam,
                  'SOM': company.som,
                  'Market Share': company.market_share_percentage,
                  'Focus Sectors': company.focus_sectors,
                }}
              />
            </Section>

            {/* Competitive Landscape */}
            <Section title="Competitive Landscape" icon={<TrendingUp className="h-5 w-5" />}>
              {company.competitive_advantages && (
                <div className="mb-4">
                  <h4 className="font-semibold text-slate-900 mb-2">Competitive Advantages</h4>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {company.competitive_advantages.split(';').map((advantage: string) => (
                      <Chip key={advantage.trim()} label={advantage.trim()} variant="primary" />
                    ))}
                  </div>
                </div>
              )}
              
              {company.key_competitors && (
                <div className="mb-4">
                  <h4 className="font-semibold text-slate-900 mb-2">Key Competitors</h4>
                  <div className="flex flex-wrap gap-2">
                    {company.key_competitors.split(';').map((competitor: string) => (
                      <Chip key={competitor.trim()} label={competitor.trim()} variant="secondary" />
                    ))}
                  </div>
                </div>
              )}

              {(company.weaknesses_gaps || company.key_challenges_needs) && (
                <InfoGrid
                  data={{
                    'Weaknesses': company.weaknesses_gaps,
                    'Key Challenges': company.key_challenges_needs,
                  }}
                />
              )}
            </Section>

            {/* Customers & Value Proposition */}
            <Section title="Customers & Value Proposition" icon={<Heart className="h-5 w-5" />}>
              {company.top_customers && (
                <div className="mb-4">
                  <h4 className="font-semibold text-slate-900 mb-2">Top Customers</h4>
                  <div className="flex flex-wrap gap-2">
                    {company.top_customers.split(';').map((customer: string) => (
                      <Chip key={customer.trim()} label={customer.trim()} variant="accent" />
                    ))}
                  </div>
                </div>
              )}

              {company.core_value_proposition && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <h4 className="font-semibold text-slate-900 mb-2">Value Proposition</h4>
                  <div className="flex flex-wrap gap-2">
                    {company.core_value_proposition.split(';').map((prop: string) => (
                      <Chip key={prop.trim()} label={prop.trim()} variant="primary" />
                    ))}
                  </div>
                </div>
              )}

              {company.pain_points_addressed && (
                <div className="mb-4">
                  <h4 className="font-semibold text-slate-900 mb-2">Pain Points Addressed</h4>
                  <ul className="list-disc list-inside space-y-1 text-slate-700">
                    {company.pain_points_addressed.split(';').map((pain: string) => (
                      <li key={pain.trim()}>{pain.trim()}</li>
                    ))}
                  </ul>
                </div>
              )}

              <InfoGrid
                data={{
                  'Net Promoter Score': company.net_promoter_score?.toString(),
                  'Churn Rate': company.churn_rate,
                  'Customer Lifetime Value': company.customer_lifetime_value,
                  'Customer Acquisition Cost': company.customer_acquisition_cost,
                }}
              />
            </Section>

            {/* Products & Offerings */}
            {company.offerings_description && (
              <Section title="Products & Offerings" icon={<Briefcase className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2 mb-4">
                  {company.offerings_description.split(';').map((offering: string) => (
                    <Chip key={offering.trim()} label={offering.trim()} variant="primary" />
                  ))}
                </div>
                
                {company.product_pipeline && (
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <h4 className="font-semibold text-slate-900 mb-2">Product Pipeline</h4>
                    <div className="flex flex-wrap gap-2">
                      {company.product_pipeline.split(';').map((product: string) => (
                        <Chip key={product.trim()} label={product.trim()} variant="accent" />
                      ))}
                    </div>
                  </div>
                )}
              </Section>
            )}

            {/* Go-To-Market Strategy */}
            {(company.go_to_market_strategy || company.sales_motion) && (
              <Section title="Go-To-Market Strategy" icon={<Target className="h-5 w-5" />}>
                <InfoGrid
                  data={{
                    'Sales Motion': company.sales_motion,
                    'GTM Strategy': company.go_to_market_strategy,
                    'CAC:LTV Ratio': company.cac_ltv_ratio,
                  }}
                />
              </Section>
            )}
          </div>
        );

      case 'leadership':
        return (
          <div className="space-y-6">
            {/* Executive Leadership */}
            <Section title="Executive Leadership" icon={<Users className="h-5 w-5" />}>
              <div className="space-y-4">
                {company.ceo_name && (
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-semibold text-slate-900 mb-2">Chief Executive Officer</h4>
                    <p className="text-slate-900 font-medium text-lg">{company.ceo_name}</p>
                    {company.ceo_linkedin_url && (
                      <a href={company.ceo_linkedin_url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
                        LinkedIn Profile
                      </a>
                    )}
                  </div>
                )}
                
                <InfoGrid
                  data={{
                    'CFO': company.cfo_name,
                    'CTO': company.cto_name,
                    'COO': company.coo_name,
                  }}
                />
              </div>
            </Section>

            {/* Key Leaders */}
            {company.key_leaders && (
              <Section title="Key Leaders" icon={<Award className="h-5 w-5" />}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {company.key_leaders.split(';').map((leader: string, idx: number) => {
                    const [name, title] = leader.split(',').map((s: string) => s.trim());
                    return (
                      <div key={idx} className="bg-white border border-slate-200 rounded-lg p-3">
                        <p className="font-semibold text-slate-900">{name}</p>
                        <p className="text-sm text-slate-600">{title}</p>
                      </div>
                    );
                  })}
                </div>
              </Section>
            )}

            {/* Board Members */}
            {company.board_members && (
              <Section title="Board of Directors" icon={<Building2 className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.board_members.split(';').map((member: string) => (
                    <Chip key={member.trim()} label={member.trim()} variant="primary" />
                  ))}
                </div>
              </Section>
            )}

            {/* Contact Information */}
            <Section title="Contact Information" icon={<Globe className="h-5 w-5" />}>
              <InfoGrid
                data={{
                  'Primary Contact': company.contact_person_name,
                  'Contact Title': company.contact_person_title,
                  'Email': company.primary_contact_email || company.contact_person_email,
                  'Phone': company.primary_phone_number || company.contact_person_phone,
                }}
              />
            </Section>

            {/* Warm Intro Pathways */}
            {(company.warm_intro_pathways || company.decision_maker_access) && (
              <Section title="Access & Networking" icon={<Target className="h-5 w-5" />}>
                <InfoGrid
                  data={{
                    'Warm Intro Pathways': company.warm_intro_pathways,
                    'Decision Maker Access': company.decision_maker_access,
                  }}
                />
              </Section>
            )}
          </div>
        );

      case 'financials':
        return (
          <div className="space-y-6">
            {/* Financial Snapshot */}
            <Section title="Financial Snapshot" icon={<TrendingUp className="h-5 w-5" />}>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
                  <p className="text-xs font-semibold text-green-700 mb-1">Revenue</p>
                  <p className="text-xl font-bold text-green-900">{company.annual_revenue || 'N/A'}</p>
                </div>
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
                  <p className="text-xs font-semibold text-blue-700 mb-1">Profit</p>
                  <p className="text-xl font-bold text-blue-900">{company.annual_profit || 'N/A'}</p>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
                  <p className="text-xs font-semibold text-purple-700 mb-1">Valuation</p>
                  <p className="text-xl font-bold text-purple-900">{company.valuation || 'N/A'}</p>
                </div>
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 rounded-lg p-4">
                  <p className="text-xs font-semibold text-orange-700 mb-1">YoY Growth</p>
                  <p className="text-xl font-bold text-orange-900">{formatPercentage(company.yoy_growth_rate)}</p>
                </div>
              </div>

              <InfoGrid
                data={{
                  'Profitability Status': company.profitability_status,
                  'Market Share': company.market_share_percentage,
                }}
              />
            </Section>

            {/* Revenue Mix */}
            {company.revenue_mix && (
              <Section title="Revenue Mix" icon={<Wallet className="h-5 w-5" />}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {company.revenue_mix.split(';').map((mix: string) => {
                    const parts = mix.split(':');
                    if (parts.length === 2) {
                      const [source, percentage] = parts.map((s: string) => s.trim());
                      return (
                        <div key={source} className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <p className="font-semibold text-slate-900">{source}</p>
                            <p className="text-lg font-bold text-blue-600">{percentage}</p>
                          </div>
                          <div className="w-full bg-slate-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: percentage }}
                            />
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })}
                </div>
              </Section>
            )}

            {/* Investors */}
            {company.key_investors && (
              <Section title="Key Investors" icon={<Users className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.key_investors.split(';').map((investor: string) => (
                    <Chip key={investor.trim()} label={investor.trim()} variant="accent" />
                  ))}
                </div>
              </Section>
            )}

            {/* Burn & Runway */}
            {(company.burn_rate || company.runway_months) && (
              <Section title="Burn Rate & Runway" icon={<AlertTriangle className="h-5 w-5" />}>
                <InfoGrid
                  data={{
                    'Burn Rate': company.burn_rate,
                    'Runway': company.runway_months,
                    'Burn Multiplier': company.burn_multiplier,
                  }}
                />
              </Section>
            )}

            {/* R&D Investment */}
            {company.r_and_d_investment && (
              <Section title="R&D Investment" icon={<Zap className="h-5 w-5" />}>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <p className="text-lg font-bold text-purple-900">{company.r_and_d_investment}</p>
                  <p className="text-sm text-purple-700">Annual R&D Spending</p>
                </div>
              </Section>
            )}
          </div>
        );

      case 'technology':
        return (
          <div className="space-y-6">
            {/* Tech Stack */}
            {company.tech_stack && (
              <Section title="Technology Stack" icon={<Code className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.tech_stack.split(';').map((tech: string) => (
                    <Chip key={tech.trim()} label={tech.trim()} variant="primary" />
                  ))}
                </div>
              </Section>
            )}

            {/* AI/ML Capabilities */}
            <Section title="AI & Machine Learning" icon={<Zap className="h-5 w-5" />}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-xs font-semibold text-blue-700 mb-1">AI Adoption Level</p>
                  <p className="text-lg font-bold text-blue-900">{company.ai_adoption_level || 'N/A'}</p>
                </div>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <p className="text-xs font-semibold text-purple-700 mb-1">AI Maturity Stage</p>
                  <p className="text-lg font-bold text-purple-900">{company.ai_maturity_stage || 'N/A'}</p>
                </div>
              </div>

              {company.ml_frameworks && (
                <div className="mt-4">
                  <p className="text-xs font-semibold text-slate-700 mb-2">ML Frameworks</p>
                  <div className="flex flex-wrap gap-2">
                    {company.ml_frameworks.split(';').map((framework: string) => (
                      <Chip key={framework.trim()} label={framework.trim()} variant="accent" />
                    ))}
                  </div>
                </div>
              )}

              <InfoGrid
                data={{
                  'AI Use Cases': company.ai_use_cases,
                  'Automation Tools': company.automation_tools,
                }}
              />
            </Section>

            {/* Data Infrastructure */}
            {company.data_infrastructure && (
              <Section title="Data Infrastructure" icon={<Building2 className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.data_infrastructure.split(';').map((infra: string) => (
                    <Chip key={infra.trim()} label={infra.trim()} variant="primary" />
                  ))}
                </div>
              </Section>
            )}

            {/* Cybersecurity */}
            {company.cyber_security_posture && (
              <Section title="Cybersecurity" icon={<Shield className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.cyber_security_posture.split(';').map((sec: string) => (
                    <Chip key={sec.trim()} label={sec.trim()} variant="primary" />
                  ))}
                </div>
              </Section>
            )}

            {/* Patents & IP */}
            {company.patents && (
              <Section title="Patents & Intellectual Property" icon={<Award className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.patents.split(';').map((patent: string) => (
                    <Chip key={patent.trim()} label={patent.trim()} variant="accent" />
                  ))}
                </div>
              </Section>
            )}

            {/* Technology Partnerships */}
            {company.technology_partnerships && (
              <Section title="Technology Partnerships" icon={<Globe className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.technology_partnerships.split(';').map((partner: string) => (
                    <Chip key={partner.trim()} label={partner.trim()} variant="primary" />
                  ))}
                </div>
              </Section>
            )}

            {/* R&D Investment */}
            {company.r_and_d_investment && (
              <Section title="Research & Development" icon={<Lightbulb className="h-5 w-5" />}>
                <InfoGrid
                  data={{
                    'R&D Investment': company.r_and_d_investment,
                    'R&D Focus Areas': company.r_and_d_focus_areas,
                  }}
                />
              </Section>
            )}
          </div>
        );

      case 'culture':
        return (
          <div className="space-y-6">
            {/* Workforce Metrics */}
            <Section title="Workforce Metrics" icon={<Users className="h-5 w-5" />}>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-xs font-semibold text-blue-700 mb-1">Employee Count</p>
                  <p className="text-xl font-bold text-blue-900">{company.employee_size || 'N/A'}</p>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-xs font-semibold text-green-700 mb-1">Avg Retention Tenure</p>
                  <p className="text-xl font-bold text-green-900">{company.avg_retention_tenure || 'N/A'}</p>
                </div>
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <p className="text-xs font-semibold text-orange-700 mb-1">Employee Turnover</p>
                  <p className="text-xl font-bold text-orange-900">{company.employee_turnover || 'N/A'}</p>
                </div>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <p className="text-xs font-semibold text-purple-700 mb-1">Hiring Velocity</p>
                  <p className="text-sm font-bold text-purple-900">{company.hiring_velocity || 'N/A'}</p>
                </div>
              </div>
            </Section>

            {/* Work Culture */}
            {company.work_culture && (
              <Section title="Work Culture" icon={<Heart className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.work_culture.split(';').map((culture: string) => (
                    <Chip key={culture.trim()} label={culture.trim()} variant="primary" />
                  ))}
                </div>
              </Section>
            )}

            {/* DEI Initiatives */}
            {company.dei_initiatives && (
              <Section title="Diversity, Equity & Inclusion" icon={<Award className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.dei_initiatives.split(';').map((initiative: string) => (
                    <Chip key={initiative.trim()} label={initiative.trim()} variant="accent" />
                  ))}
                </div>
                {company.diversity_metrics && (
                  <div className="mt-4 bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <p className="text-sm font-semibold text-slate-700 mb-2">Diversity Metrics</p>
                    <div className="flex flex-wrap gap-2">
                      {company.diversity_metrics.split(';').map((metric: string) => (
                        <Chip key={metric.trim()} label={metric.trim()} variant="secondary" />
                      ))}
                    </div>
                  </div>
                )}
              </Section>
            )}

            {/* Learning & Development */}
            {company.learning_development_programs && (
              <Section title="Learning & Development" icon={<Lightbulb className="h-5 w-5" />}>
                <div className="space-y-3">
                  {company.learning_development_programs.split(';').map((program: string) => (
                    <div key={program.trim()} className="bg-white border border-slate-200 rounded-lg p-3">
                      <p className="text-slate-800">{program.trim()}</p>
                    </div>
                  ))}
                </div>
                <InfoGrid
                  data={{
                    'Training Budget': company.training_budget_per_employee,
                    'Mentorship Program': company.mentorship_program,
                  }}
                />
              </Section>
            )}

            {/* Benefits & Compensation */}
            {company.employee_benefits && (
              <Section title="Benefits & Compensation" icon={<Wallet className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2 mb-4">
                  {company.employee_benefits.split(';').map((benefit: string) => (
                    <Chip key={benefit.trim()} label={benefit.trim()} variant="primary" />
                  ))}
                </div>
                <InfoGrid
                  data={{
                    'Compensation Philosophy': company.compensation_philosophy,
                    'Performance Bonus': company.performance_bonus_structure,
                  }}
                />
              </Section>
            )}

            {/* Work Environment */}
            <Section title="Work Environment" icon={<MapPin className="h-5 w-5" />}>
              <InfoGrid
                data={{
                  'Work Model': company.hybrid_remote_policy,
                  'Office Locations': company.office_locations,
                  'Workplace Safety': company.workplace_safety_record,
                }}
              />
            </Section>
          </div>
        );

      case 'risk':
        return (
          <div className="space-y-6">
            {/* ESG Ratings */}
            {company.esg_ratings && (
              <Section title="ESG Commitment" icon={<Leaf className="h-5 w-5" />}>
                <div className="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-6">
                  <div className="flex flex-wrap gap-2">
                    {company.esg_ratings.split(';').map((rating: string) => (
                      <Chip key={rating.trim()} label={rating.trim()} variant="accent" />
                    ))}
                  </div>
                </div>
              </Section>
            )}

            {/* Sustainability Goals */}
            {company.sustainability_goals && (
              <Section title="Sustainability Goals" icon={<Target className="h-5 w-5" />}>
                <div className="space-y-3">
                  {company.sustainability_goals.split(';').map((goal: string) => (
                    <div key={goal.trim()} className="bg-white border border-slate-200 rounded-lg p-3 flex items-start gap-3">
                      <div className="flex-shrink-0 w-2 h-2 rounded-full bg-green-500 mt-2" />
                      <p className="text-slate-800">{goal.trim()}</p>
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {/* Environmental Commitment */}
            {company.environmental_commitment && (
              <Section title="Environmental Commitment" icon={<Leaf className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.environmental_commitment.split(';').map((commitment: string) => (
                    <Chip key={commitment.trim()} label={commitment.trim()} variant="accent" />
                  ))}
                </div>
              </Section>
            )}

            {/* Risk Management */}
            <Section title="Risk Management" icon={<Shield className="h-5 w-5" />}>
              <InfoGrid
                data={{
                  'Cybersecurity Posture': company.cybersecurity_posture,
                  'Geopolitical Risks': company.geopolitical_risks,
                  'Macro Risks': company.macro_risks,
                  'Supply Chain Dependencies': company.supply_chain_dependencies,
                }}
              />
            </Section>

            {/* Compliance & Certifications */}
            {company.compliance_certifications && (
              <Section title="Compliance & Certifications" icon={<Award className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.compliance_certifications.split(';').map((cert: string) => (
                    <Chip key={cert.trim()} label={cert.trim()} variant="primary" />
                  ))}
                </div>
              </Section>
            )}

            {/* Cybersecurity */}
            {company.cyber_security_posture && (
              <Section title="Cybersecurity Posture" icon={<Shield className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.cyber_security_posture.split(';').map((sec: string) => (
                    <Chip key={sec.trim()} label={sec.trim()} variant="primary" />
                  ))}
                </div>
              </Section>
            )}

            {/* Crisis History */}
            {company.crisis_history && (
              <Section title="Crisis Management History" icon={<AlertTriangle className="h-5 w-5" />}>
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="flex flex-wrap gap-2">
                    {company.crisis_history.split(';').map((crisis: string, idx: number) => (
                      <Chip key={idx} label={crisis.trim()} variant="secondary" />
                    ))}
                  </div>
                </div>
              </Section>
            )}

            {/* Supply Chain */}
            {company.supply_chain_dependencies && (
              <Section title="Supply Chain Dependencies" icon={<Globe className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.supply_chain_dependencies.split(';').map((dep: string) => (
                    <Chip key={dep.trim()} label={dep.trim()} variant="accent" />
                  ))}
                </div>
              </Section>
            )}
          </div>
        );

      case 'strategy':
        return (
          <div className="space-y-6">
            {/* Strategic Vision */}
            {company['5_year_vision'] && (
              <Section title="5-Year Vision" icon={<Target className="h-5 w-5" />}>
                <div className="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-6">
                  <p className="text-slate-900 text-lg leading-relaxed">{company['5_year_vision']}</p>
                </div>
              </Section>
            )}

            {/* Strategic Priorities */}
            {company.strategic_priorities && (
              <Section title="Strategic Priorities" icon={<Briefcase className="h-5 w-5" />}>
                <div className="space-y-3">
                  {company.strategic_priorities.split(';').map((priority: string, idx: number) => (
                    <div key={idx} className="bg-white border border-slate-200 rounded-lg p-4 flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                        {idx + 1}
                      </div>
                      <p className="text-slate-800 flex-1 pt-1">{priority.trim()}</p>
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {/* Growth Strategy */}
            <Section title="Growth Trajectory" icon={<TrendingUp className="h-5 w-5" />}>
              <InfoGrid
                data={{
                  'Growth Trajectory': company.growth_trajectory,
                  'Future Outlook': company.future_outlook,
                  'Market Expansion': company.market_expansion_plans,
                }}
              />
            </Section>

            {/* Innovation Roadmap */}
            {company.innovation_roadmap && (
              <Section title="Innovation Roadmap" icon={<Lightbulb className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2">
                  {company.innovation_roadmap.split(';').map((item: string) => (
                    <Chip key={item.trim()} label={item.trim()} variant="accent" />
                  ))}
                </div>
              </Section>
            )}

            {/* Market Opportunities */}
            {company.market_opportunities && (
              <Section title="Market Opportunities" icon={<Globe className="h-5 w-5" />}>
                <div className="space-y-2">
                  {company.market_opportunities.split(';').map((opp: string) => (
                    <div key={opp.trim()} className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <p className="text-slate-800">{opp.trim()}</p>
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {/* Competitive Threats */}
            {company.competitive_threats && (
              <Section title="Competitive Threats" icon={<AlertTriangle className="h-5 w-5" />}>
                <div className="space-y-2">
                  {company.competitive_threats.split(';').map((threat: string) => (
                    <div key={threat.trim()} className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                      <p className="text-slate-800">{threat.trim()}</p>
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {/* Strategic Partnerships */}
            {company.strategic_partnerships && (
              <Section title="Strategic Partnerships & Ecosystem" icon={<Users className="h-5 w-5" />}>
                <div className="flex flex-wrap gap-2 mb-4">
                  {company.strategic_partnerships.split(';').map((partner: string) => (
                    <Chip key={partner.trim()} label={partner.trim()} variant="primary" />
                  ))}
                </div>
                <InfoGrid
                  data={{
                    'Joint Ventures': company.joint_ventures,
                    'Partnership Opportunities': company.partnership_opportunities,
                  }}
                />
              </Section>
            )}
          </div>
        );

      case 'skills':
        // Parse hiring data for this company
        const companyHiringData = hiringData?.job_role_details || [];
        
        // Calculate skill frequencies across all hiring rounds
        const skillFrequencyMap = new Map<string, number>();
        companyHiringData.forEach((role) => {
          role.hiring_rounds?.forEach((round) => {
            round.skill_sets?.forEach((skill) => {
              const code = skill.skill_set_code;
              skillFrequencyMap.set(code, (skillFrequencyMap.get(code) || 0) + 1);
            });
          });
        });
        
        const sortedSkills = Array.from(skillFrequencyMap.entries())
          .sort((a, b) => b[1] - a[1])
          .slice(0, 10);

        return (
          <div className="space-y-6">
            {/* Skill Frequency Analysis - TOP SECTION */}
            {sortedSkills.length > 0 && (
              <Section title="Top Skills in Hiring" icon={<Brain className="h-5 w-5" />}>
                <div className="space-y-3">
                  {sortedSkills.map(([skill, count]) => {
                    const totalRounds = companyHiringData.reduce(
                      (sum, role) => sum + (role.hiring_rounds?.length || 0),
                      0
                    );
                    const percentage = totalRounds > 0 ? (count / totalRounds) * 100 : 0;
                    return (
                      <div key={skill} className="bg-white border border-slate-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold text-slate-900">{skill}</h4>
                          <div className="text-sm font-bold text-blue-600">
                            {count} round{count > 1 ? 's' : ''}
                          </div>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all"
                            style={{ width: `${Math.min(percentage * 2, 100)}%` }}
                          ></div>
                        </div>
                        <p className="text-xs text-slate-600 mt-1">
                          {percentage.toFixed(1)}% of all rounds
                        </p>
                      </div>
                    );
                  })}
                </div>
              </Section>
            )}

            {/* Job Roles Overview */}
            {companyHiringData.length > 0 && (
              <Section title="Active Job Roles" icon={<Briefcase className="h-5 w-5" />}>
                <div className="space-y-4">
                  {companyHiringData.map((role, idx: number) => (
                    <Link
                      key={idx}
                      href={`/hiring-rounds/${encodeURIComponent(company.name)}`}
                      className="block bg-white border border-slate-200 rounded-lg p-4 hover:shadow-lg hover:border-blue-300 transition-all duration-200 cursor-pointer"
                    >
                      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-3">
                        <div>
                          <h4 className="font-bold text-lg text-slate-900 hover:text-blue-600 transition-colors">{role.role_title}</h4>
                          <p className="text-sm text-slate-600">
                            {role.role_category} • {role.opportunity_type}
                          </p>
                        </div>
                        <div className="bg-green-50 border border-green-200 rounded-lg px-4 py-2 text-center">
                          <p className="text-xs font-semibold text-green-700">
                            {role.compensation}
                          </p>
                          <p className="text-lg font-bold text-green-900">
                            ₹{(role.ctc_or_stipend / 100000).toFixed(1)}L
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-slate-700 mb-3 line-clamp-2">
                        {role.job_description}
                      </p>
                      <div className="flex flex-wrap gap-2 mb-2">
                        <Chip label={`${role.hiring_rounds?.length || 0} Rounds`} variant="primary" />
                        {role.benefits_summary && (
                          <Chip label="Benefits Available" variant="accent" />
                        )}
                      </div>
                    </Link>
                  ))}
                </div>
              </Section>
            )}

            {/* Hiring Rounds Breakdown */}
            {companyHiringData.length > 0 && companyHiringData[0]?.hiring_rounds && (
              <Section title="Hiring Process" icon={<ClipboardList className="h-5 w-5" />}>
                <div className="space-y-4">
                  {companyHiringData[0].hiring_rounds.map((round) => (
                    <div key={round.round_number} className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                      <div className="flex items-start gap-3 mb-3">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                          {round.round_number}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-bold text-slate-900">{round.round_name}</h4>
                          <p className="text-sm text-slate-600">
                            {round.round_category} • {round.evaluation_type} • {round.assessment_mode}
                          </p>
                        </div>
                      </div>
                      <div className="ml-11">
                        <p className="text-xs font-semibold text-slate-700 mb-2">Skills Tested:</p>
                        <div className="flex flex-wrap gap-2">
                          {round.skill_sets?.map((skill, idx: number) => (
                            <Chip key={idx} label={skill.skill_set_code} variant="primary" />
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {/* Hiring Stats Summary */}
            {companyHiringData.length > 0 && (
              <Section title="Hiring Summary" icon={<Target className="h-5 w-5" />}>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-blue-900">{companyHiringData.length}</p>
                    <p className="text-xs text-blue-700">Active Roles</p>
                  </div>
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-purple-900">
                      {companyHiringData[0]?.hiring_rounds?.length || 0}
                    </p>
                    <p className="text-xs text-purple-700">Hiring Rounds</p>
                  </div>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-green-900">
                      ₹{Math.max(...companyHiringData.map((r) => r.ctc_or_stipend)) / 100000}L
                    </p>
                    <p className="text-xs text-green-700">Max CTC</p>
                  </div>
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-orange-900">{skillFrequencyMap.size}</p>
                    <p className="text-xs text-orange-700">Unique Skills</p>
                  </div>
                </div>
              </Section>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200">
      <Tabs tabs={tabs} activeTab={activeTab} onChange={onTabChange} />
      <div className="p-4 sm:p-5 lg:p-6">{renderTabContent()}</div>
    </div>
  );
}

interface SectionProps {
  title: string;
  children: React.ReactNode;
  icon?: React.ReactNode;
}

const Section: React.FC<SectionProps> = ({ title, children, icon }) => (
  <div>
    <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-3 sm:mb-4 break-words flex items-center gap-2">
      {icon}
      {title}
    </h3>
    {children}
  </div>
);

interface InfoGridProps {
  data: Record<string, string | number | undefined | null>;
}

const InfoGrid: React.FC<InfoGridProps> = ({ data }) => {
  const entries = Object.entries(data).filter(([, value]) => value !== undefined && value !== null);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
      {entries.map(([key, value]) => {
        // Check if value is a string and contains semicolons (delimiter)
        const stringValue = String(value);
        const hasDelimiter = stringValue.includes(';');
        
        return (
          <div key={key} className="bg-slate-50 rounded-lg p-3 border border-slate-100">
            <p className="text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wide break-words">{key}</p>
            {hasDelimiter ? (
              <div className="flex flex-wrap gap-1.5">
                {stringValue.split(';').map((item: string, index: number) => {
                  const trimmedItem = item.trim();
                  return trimmedItem ? (
                    <Chip key={index} label={trimmedItem} variant="secondary" />
                  ) : null;
                })}
              </div>
            ) : (
              <p className="text-sm text-slate-900 break-words">{stringValue}</p>
            )}
          </div>
        );
      })}
    </div>
  );
};
