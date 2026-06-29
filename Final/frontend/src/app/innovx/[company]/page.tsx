'use client';

import React, { useMemo, useState } from 'react';
import { Layout } from '@/components';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { 
  TrendingUp, 
  Lightbulb, 
  Users, 
  Target, 
  Clock,
  AlertCircle,
  Zap,
  Award,
  Layers,
  CheckCircle,
  Building2,
  Globe,
  Compass,
  Code,
  Database,
  Cpu,
  ArrowLeft,
  Briefcase
} from 'lucide-react';
import innovxData from '@/data/innovx_master.json';

type TabType = 'competitive-landscape' | 'innovx-projects' | 'strategic-pillars' | 'innovation-roadmap' | 'industry-trends';

interface CompanyMaster {
  company_name: string;
  industry: string;
  geographic_focus: string;
  target_market: string;
}

interface IndustryTrend {
  trend_name: string;
  trend_description: string;
  strategic_importance: 'Critical' | 'High' | string;
  time_horizon_years: number;
  trend_drivers?: string[];
  impact_areas?: string[];
}

interface InnovationRoadmapItem {
  innovation_theme: string;
  innovation_type: string;
  time_horizon: 'Now' | 'Next' | string;
  problem_statement: string;
  expected_outcome: string;
  target_customer: string;
  required_capabilities?: string[];
}

interface StrategicPillar {
  pillar_name: string;
  focus_area: 'Efficiency' | 'Defense' | 'Growth' | string;
  pillar_description: string;
  cto_vision_statement: string;
  key_technologies?: string[];
  strategic_risks: string;
  strategic_assumptions: string;
}

interface InnovxProject {
  project_name: string;
  tier_level: 'Tier 1' | 'Tier 2' | 'Tier 3' | string;
  architecture_style: string;
  problem_statement: string;
  innovation_objective: string;
  differentiation_factor: string;
  target_users: string;
  business_value: string;
  backend_technologies?: string[];
  frontend_technologies?: string[];
  ai_ml_technologies?: string[];
  infrastructure_cloud?: string;
  aligned_pillar_names?: string[];
}

interface CompetitiveLandscape {
  competitor_name: string;
  threat_level: 'High' | 'Medium' | string;
  core_strength: string;
  market_positioning: string;
  bet_name: string;
  bet_description: string;
  innovation_category: string;
  futuristic_level: string;
  competitor_type: string;
}

interface InnovxCompany {
  innovx_master: CompanyMaster;
  industry_trends?: IndustryTrend[];
  innovation_roadmap?: InnovationRoadmapItem[];
  strategic_pillars?: StrategicPillar[];
  innovx_projects?: InnovxProject[];
  competitive_landscape?: CompetitiveLandscape[];
}

export default function CompanyInnovXPage() {
  const params = useParams();
  const companyName = params?.company ? decodeURIComponent(params.company as string) : '';
  
  const [selectedTab, setSelectedTab] = useState<TabType>('industry-trends');
  const companies = innovxData.companies as InnovxCompany[];
  const companyInfo = useMemo(
    () =>
      companies.find(
        (c) => c.innovx_master?.company_name?.toLowerCase() === companyName.toLowerCase()
      ) || null,
    [companies, companyName]
  );
  const loading = !companyName;

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-slate-600">Loading company data...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!companyInfo) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-slate-900 mb-2">Company Not Found</h1>
            <p className="text-slate-600 mb-4">No data found for: {companyName}</p>
            <Link href="/innovx" className="text-blue-600 hover:text-blue-700 font-semibold">
              ← Back to Companies
            </Link>
          </div>
        </div>
      </Layout>
    );
  }

  const companyData = companyInfo.innovx_master;
  const trends = companyInfo.industry_trends || [];
  const roadmap = companyInfo.innovation_roadmap || [];
  const competitors = companyInfo.competitive_landscape || [];
  const pillars = companyInfo.strategic_pillars || [];
  const projects = companyInfo.innovx_projects || [];

  const tabs = [
    { id: 'industry-trends' as TabType, label: 'Industry Trends', count: trends.length, icon: TrendingUp },
    { id: 'innovation-roadmap' as TabType, label: 'Innovation Roadmap', count: roadmap.length, icon: Lightbulb },
    { id: 'strategic-pillars' as TabType, label: 'Strategic Pillars', count: pillars.length, icon: Compass },
    { id: 'innovx-projects' as TabType, label: 'InnovX Projects', count: projects.length, icon: Code },
    { id: 'competitive-landscape' as TabType, label: 'Competitive Landscape', count: competitors.length, icon: Users },
  ];

  const renderTabContent = () => {
    switch (selectedTab) {
      case 'industry-trends':
        return (
          <div className="space-y-3 sm:space-y-4">
            {trends.map((trend, idx: number) => (
              <div 
                key={idx} 
                className="border-2 border-slate-200 rounded-lg sm:rounded-xl p-4 sm:p-5 lg:p-6 hover:border-blue-400 hover:shadow-lg transition-all duration-300 bg-white"
              >
                <div className="flex flex-col sm:flex-row items-start justify-between mb-3 sm:mb-4 gap-3">
                  <div className="flex items-start gap-2 sm:gap-3 flex-1 w-full">
                    <div className={`p-2 sm:p-3 rounded-lg flex-shrink-0 ${
                      trend.strategic_importance === 'Critical' ? 'bg-red-100' :
                      trend.strategic_importance === 'High' ? 'bg-orange-100' :
                      'bg-yellow-100'
                    }`}>
                      <Zap className={`h-5 w-5 sm:h-6 sm:w-6 ${
                        trend.strategic_importance === 'Critical' ? 'text-red-600' :
                        trend.strategic_importance === 'High' ? 'text-orange-600' :
                        'text-yellow-600'
                      }`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-base sm:text-lg lg:text-xl font-bold text-slate-900 mb-1.5 sm:mb-2 break-words">
                        {trend.trend_name}
                      </h4>
                      <p className="text-sm sm:text-base text-slate-700 leading-relaxed">{trend.trend_description}</p>
                    </div>
                  </div>
                  <div className="flex sm:flex-col gap-2 w-full sm:w-auto sm:ml-4">
                    <span className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm font-bold whitespace-nowrap text-center flex-1 sm:flex-none ${
                      trend.strategic_importance === 'Critical' ? 'bg-red-500 text-white' :
                      trend.strategic_importance === 'High' ? 'bg-orange-500 text-white' :
                      'bg-yellow-500 text-white'
                    }`}>
                      {trend.strategic_importance}
                    </span>
                    <div className="flex items-center gap-1.5 sm:gap-2 text-slate-600 bg-slate-100 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-full justify-center flex-1 sm:flex-none">
                      <Clock className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                      <span className="text-xs sm:text-sm font-semibold">{trend.time_horizon_years}y</span>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-slate-200">
                  <div>
                    <p className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1.5 sm:gap-2">
                      <CheckCircle className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                      Key Drivers
                    </p>
                    <div className="flex flex-wrap gap-1.5 sm:gap-2">
                      {trend.trend_drivers?.map((driver: string, i: number) => (
                        <span key={i} className="bg-blue-100 text-blue-800 px-2.5 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium">
                          {driver}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1.5 sm:gap-2">
                      <Target className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                      Impact Areas
                    </p>
                    <div className="flex flex-wrap gap-1.5 sm:gap-2">
                      {trend.impact_areas?.map((area: string, i: number) => (
                        <span key={i} className="bg-slate-100 text-slate-700 px-2.5 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium border border-slate-300">
                          {area}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      case 'innovation-roadmap':
        return (
          <div className="space-y-6">
            {roadmap.map((item, idx: number) => (
              <div 
                key={idx} 
                className="border-2 border-slate-200 rounded-xl overflow-hidden hover:border-blue-400 hover:shadow-lg transition-all duration-300"
              >
                <div className="bg-gradient-to-r from-slate-50 to-slate-100 p-6 border-b border-slate-200">
                  <div className="flex items-start gap-3">
                    <Award className="h-8 w-8 text-blue-600 flex-shrink-0" />
                    <div className="flex-1">
                      <h4 className="text-xl font-bold text-slate-900 mb-2">
                        {item.innovation_theme}
                      </h4>
                      <div className="flex gap-2 flex-wrap">
                        <span className="bg-white border-2 border-slate-300 text-slate-700 px-3 py-1 rounded-full text-sm font-bold">
                          {item.innovation_type}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                          item.time_horizon === 'Now' ? 'bg-blue-600 text-white' :
                          item.time_horizon === 'Next' ? 'bg-slate-600 text-white' :
                          'bg-slate-400 text-white'
                        }`}>
                          {item.time_horizon}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="p-6 space-y-4 bg-white">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                      <p className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-2">
                        <AlertCircle className="h-4 w-4" />
                        Problem Statement
                      </p>
                      <p className="text-slate-800 font-medium">{item.problem_statement}</p>
                    </div>
                    
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p className="text-xs font-bold text-blue-700 uppercase tracking-wider mb-2 flex items-center gap-2">
                        <CheckCircle className="h-4 w-4" />
                        Expected Outcome
                      </p>
                      <p className="text-slate-800 font-medium">{item.expected_outcome}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        Target Customer
                      </p>
                      <p className="text-slate-900 font-semibold bg-blue-50 px-3 py-2 rounded-lg">
                        {item.target_customer}
                      </p>
                    </div>
                    
                    <div>
                      <p className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-2">
                        <Layers className="h-4 w-4" />
                        Required Capabilities
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {item.required_capabilities?.map((cap: string, i: number) => (
                          <span key={i} className="bg-slate-100 text-slate-800 px-3 py-1 rounded-full text-sm font-bold border border-slate-300">
                            {cap}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      case 'strategic-pillars':
        return (
          <div className="space-y-4">
            {pillars.map((pillar, idx: number) => (
              <div 
                key={idx} 
                className="border-2 border-slate-200 rounded-xl p-6 hover:border-blue-400 hover:shadow-lg transition-all duration-300 bg-white"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className={`p-3 rounded-lg ${
                    pillar.focus_area === 'Efficiency' ? 'bg-green-100' :
                    pillar.focus_area === 'Defense' ? 'bg-red-100' :
                    pillar.focus_area === 'Growth' ? 'bg-blue-100' :
                    'bg-slate-100'
                  }`}>
                    <Target className={`h-6 w-6 ${
                      pillar.focus_area === 'Efficiency' ? 'text-green-600' :
                      pillar.focus_area === 'Defense' ? 'text-red-600' :
                      pillar.focus_area === 'Growth' ? 'text-blue-600' :
                      'text-slate-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-xl font-bold text-slate-900">
                        {pillar.pillar_name}
                      </h4>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                        pillar.focus_area === 'Efficiency' ? 'bg-green-100 text-green-700' :
                        pillar.focus_area === 'Defense' ? 'bg-red-100 text-red-700' :
                        pillar.focus_area === 'Growth' ? 'bg-blue-100 text-blue-700' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {pillar.focus_area}
                      </span>
                    </div>
                    <p className="text-slate-700 leading-relaxed mb-3">{pillar.pillar_description}</p>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                      <p className="text-xs font-bold text-blue-700 uppercase tracking-wider mb-1">CTO Vision</p>
                      <p className="text-slate-800 font-medium italic">&quot;{pillar.cto_vision_statement}&quot;</p>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-200">
                  <div>
                    <p className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-2">
                      <Code className="h-4 w-4" />
                      Key Technologies
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {pillar.key_technologies?.map((tech: string, i: number) => (
                        <span key={i} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium border border-blue-300">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-2">
                      <AlertCircle className="h-4 w-4" />
                      Strategic Risks
                    </p>
                    <p className="text-slate-700 font-medium">{pillar.strategic_risks}</p>
                  </div>
                  
                  <div>
                    <p className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-2">
                      <CheckCircle className="h-4 w-4" />
                      Assumptions
                    </p>
                    <p className="text-slate-700 font-medium">{pillar.strategic_assumptions}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      case 'innovx-projects':
        const tier1Projects = projects.filter((p) => p.tier_level === 'Tier 1');
        const tier2Projects = projects.filter((p) => p.tier_level === 'Tier 2');
        const tier3Projects = projects.filter((p) => p.tier_level === 'Tier 3');

        const renderProjectCard = (project: InnovxProject, idx: number) => (
          <div 
            key={idx} 
            className="border-2 border-slate-200 rounded-xl overflow-hidden hover:border-blue-400 hover:shadow-lg transition-all duration-300"
          >
            <div className="bg-gradient-to-r from-slate-50 to-slate-100 p-4 border-b border-slate-200">
              <div className="flex items-start gap-3">
                <Cpu className="h-7 w-7 text-blue-600 flex-shrink-0" />
                <div className="flex-1">
                  <h4 className="text-xl font-bold text-slate-900 mb-1.5">
                    {project.project_name}
                  </h4>
                  <div className="flex gap-2 flex-wrap">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                      project.tier_level === 'Tier 1' ? 'bg-blue-600 text-white' :
                      project.tier_level === 'Tier 2' ? 'bg-slate-600 text-white' :
                      'bg-slate-400 text-white'
                    }`}>
                      {project.tier_level}
                    </span>
                    <span className="bg-white border border-slate-300 text-slate-700 px-2.5 py-0.5 rounded-full text-xs font-bold">
                      {project.architecture_style}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-4 space-y-3 bg-white">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                  <p className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <AlertCircle className="h-3.5 w-3.5" />
                    Problem Statement
                  </p>
                  <p className="text-slate-800 font-medium">{project.problem_statement}</p>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-xs font-bold text-blue-700 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Target className="h-3.5 w-3.5" />
                    Innovation Objective
                  </p>
                  <p className="text-slate-800 font-medium">{project.innovation_objective}</p>
                </div>
              </div>
              
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                <p className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <Zap className="h-3.5 w-3.5" />
                  Differentiation Factor
                </p>
                <p className="text-slate-800 font-medium">{project.differentiation_factor}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <p className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Users className="h-3.5 w-3.5" />
                    Target Users
                  </p>
                  <p className="text-slate-900 font-semibold bg-blue-50 px-3 py-2 rounded-lg">
                    {project.target_users}
                  </p>
                </div>
                
                <div>
                  <p className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <CheckCircle className="h-3.5 w-3.5" />
                    Business Value
                  </p>
                  <p className="text-slate-900 font-semibold bg-blue-50 px-3 py-2 rounded-lg">
                    {project.business_value}
                  </p>
                </div>
              </div>
              
              <div className="border-t border-slate-200 pt-3">
                <p className="text-sm font-bold text-slate-600 uppercase tracking-wider mb-2">Technology Stack</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-3">
                  {project.backend_technologies && (
                    <div>
                      <p className="text-sm font-bold text-slate-500 mb-1 flex items-center gap-1">
                        <Database className="h-3 w-3" /> Backend
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {project.backend_technologies.map((tech: string, i: number) => (
                          <span key={i} className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-sm font-medium border border-slate-300">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {project.frontend_technologies && (
                    <div>
                      <p className="text-sm font-bold text-slate-500 mb-1 flex items-center gap-1">
                        <Code className="h-3 w-3" /> Frontend
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {project.frontend_technologies.map((tech: string, i: number) => (
                          <span key={i} className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-sm font-medium border border-blue-300">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {project.ai_ml_technologies && (
                    <div>
                      <p className="text-sm font-bold text-slate-500 mb-1 flex items-center gap-1">
                        <Cpu className="h-3 w-3" /> AI/ML
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {project.ai_ml_technologies.map((tech: string, i: number) => (
                          <span key={i} className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-sm font-medium border border-blue-300">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {project.infrastructure_cloud && (
                    <div>
                      <p className="text-sm font-bold text-slate-500 mb-1 flex items-center gap-1">
                        <Globe className="h-3 w-3" /> Cloud
                      </p>
                      <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-sm font-medium border border-slate-300">
                        {project.infrastructure_cloud}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              {project.aligned_pillar_names && project.aligned_pillar_names.length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-2.5">
                  <p className="text-xs font-bold text-blue-700 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Compass className="h-3.5 w-3.5" />
                    Aligned Strategic Pillars
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {project.aligned_pillar_names.map((pillar: string, i: number) => (
                      <span key={i} className="bg-blue-600 text-white px-2.5 py-0.5 rounded-full text-sm font-bold">
                        {pillar}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        );

        return (
          <div className="space-y-8">
            {/* Tier 1 Projects */}
            {tier1Projects.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border-2 border-blue-200 overflow-hidden">
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Award className="h-8 w-8" />
                      <div>
                        <h3 className="text-2xl font-bold">Tier 1 Projects</h3>
                        <p className="text-blue-50 text-sm">Highest priority strategic initiatives</p>
                      </div>
                    </div>
                    <div className="bg-white bg-opacity-20 px-4 py-2 rounded-lg">
                      <span className="text-2xl font-bold">{tier1Projects.length}</span>
                    </div>
                  </div>
                </div>
                <div className="p-6 space-y-6">
                  {tier1Projects.map((project, idx: number) => renderProjectCard(project, idx))}
                </div>
              </div>
            )}

            {/* Tier 2 Projects */}
            {tier2Projects.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border-2 border-slate-300 overflow-hidden">
                <div className="bg-gradient-to-r from-slate-600 to-slate-700 text-white p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Layers className="h-8 w-8" />
                      <div>
                        <h3 className="text-2xl font-bold">Tier 2 Projects</h3>
                        <p className="text-slate-300 text-sm">Medium priority strategic initiatives</p>
                      </div>
                    </div>
                    <div className="bg-white bg-opacity-20 px-4 py-2 rounded-lg">
                      <span className="text-2xl font-bold">{tier2Projects.length}</span>
                    </div>
                  </div>
                </div>
                <div className="p-6 space-y-6">
                  {tier2Projects.map((project, idx: number) => renderProjectCard(project, idx))}
                </div>
              </div>
            )}

            {/* Tier 3 Projects */}
            {tier3Projects.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border-2 border-slate-200 overflow-hidden">
                <div className="bg-gradient-to-r from-slate-400 to-slate-500 text-white p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Code className="h-8 w-8" />
                      <div>
                        <h3 className="text-2xl font-bold">Tier 3 Projects</h3>
                        <p className="text-slate-100 text-sm">Supporting and exploratory initiatives</p>
                      </div>
                    </div>
                    <div className="bg-white bg-opacity-20 px-4 py-2 rounded-lg">
                      <span className="text-2xl font-bold">{tier3Projects.length}</span>
                    </div>
                  </div>
                </div>
                <div className="p-6 space-y-6">
                  {tier3Projects.map((project, idx: number) => renderProjectCard(project, idx))}
                </div>
              </div>
            )}
          </div>
        );

      case 'competitive-landscape':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {competitors.map((comp, idx: number) => (
              <div 
                key={idx} 
                className="border-2 border-slate-200 rounded-xl p-6 hover:border-blue-400 hover:shadow-lg transition-all duration-300 bg-white"
              >
                <div className="flex items-start justify-between mb-4">
                  <h4 className="text-xl font-bold text-slate-900 flex-1">
                    {comp.competitor_name}
                  </h4>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap ml-2 ${
                    comp.threat_level === 'High' ? 'bg-red-500 text-white' :
                    comp.threat_level === 'Medium' ? 'bg-yellow-500 text-white' :
                    'bg-green-500 text-white'
                  }`}>
                    {comp.threat_level} Threat
                  </span>
                </div>
                
                <div className="space-y-3 text-sm">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-1">Core Strength</p>
                    <p className="text-slate-800 font-medium">{comp.core_strength}</p>
                  </div>
                  
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                    <p className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Market Positioning</p>
                    <p className="text-slate-800 font-medium">{comp.market_positioning}</p>
                  </div>
                  
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p className="text-xs font-bold text-blue-700 uppercase tracking-wider mb-1 flex items-center gap-2">
                      <Target className="h-4 w-4" />
                      Strategic Bet: {comp.bet_name}
                    </p>
                    <p className="text-slate-700">{comp.bet_description}</p>
                  </div>
                  
                  <div className="flex items-center gap-2 pt-2 flex-wrap">
                    <span className="bg-slate-100 text-slate-800 px-3 py-1 rounded-full text-xs font-bold border border-slate-300">
                      {comp.innovation_category}
                    </span>
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-bold border border-blue-300">
                      {comp.futuristic_level}
                    </span>
                    <span className="bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-xs font-bold border border-slate-300">
                      {comp.competitor_type}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-slate-50">
        {/* Header with Back Button */}
        <div className="bg-white border-b border-slate-200">
          <div className="px-4 sm:px-6 lg:px-8 py-4 sm:py-5 lg:py-6 max-w-7xl mx-auto">
            <Link 
              href="/innovx" 
              className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold mb-3 sm:mb-4 transition-colors text-sm sm:text-base touch-manipulation"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to All Companies
            </Link>
            
            <div className="flex flex-col sm:flex-row items-start gap-3 sm:gap-4">
              <div className="bg-blue-100 p-3 sm:p-4 rounded-lg">
                <Building2 className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 mb-2 break-words">{companyData.company_name}</h1>
                <div className="flex flex-wrap gap-2 sm:gap-3 text-xs sm:text-sm">
                  <span className="inline-flex items-center gap-1 bg-blue-100 text-blue-700 px-2.5 sm:px-3 py-1 rounded-full font-semibold">
                    <Briefcase className="h-3 w-3" />
                    {companyData.industry}
                  </span>
                  <span className="inline-flex items-center gap-1 bg-slate-100 text-slate-700 px-2.5 sm:px-3 py-1 rounded-full font-semibold">
                    <Globe className="h-3 w-3" />
                    {companyData.geographic_focus}
                  </span>
                  <span className="inline-flex items-center gap-1 bg-slate-100 text-slate-700 px-2.5 sm:px-3 py-1 rounded-full font-semibold">
                    <Target className="h-3 w-3" />
                    {companyData.target_market}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white border-b border-slate-200 sticky top-0 z-10">
          <div className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
            <div className="flex gap-1 overflow-x-auto scrollbar-hide -mx-4 sm:mx-0 px-4 sm:px-0">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = selectedTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setSelectedTab(tab.id)}
                    className={`flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 font-semibold text-xs sm:text-sm whitespace-nowrap border-b-2 transition-colors touch-manipulation ${
                      isActive 
                        ? 'border-blue-600 text-blue-600' 
                        : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                    <span className="hidden sm:inline">{tab.label}</span>
                    <span className="sm:hidden">{tab.label.split(' ')[0]}</span>
                    <span className={`px-1.5 sm:px-2 py-0.5 rounded-full text-xs font-bold ${
                      isActive ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {tab.count}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <div className="px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 max-w-7xl mx-auto">
          {renderTabContent()}
        </div>
      </div>
    </Layout>
  );
}
