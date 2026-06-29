'use client';

import React from 'react';
import { use } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Layout } from '@/components';
import { getCompanyById, getInnovxDataForCompany } from '@/utils/data';
import { Chip } from '@/components/UI';
import CompanyContextHeader from '@/components/CompanyDetail/CompanyContextHeader';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function CompanyInnovxPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const searchParams = useSearchParams();
  const company = getCompanyById(resolvedParams.id);
  const innovx = company ? getInnovxDataForCompany(company.name) : null;

  if (!company) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <p className="text-lg text-slate-600">Company not found</p>
        </div>
      </Layout>
    );
  }

  if (!innovx) {
    const requestedFrom = searchParams.get('from');
    const fromHref = requestedFrom && requestedFrom.startsWith('/') ? requestedFrom : `/companies/${company.id}`;

    return (
      <Layout>
        <div className="px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 space-y-4 sm:space-y-6">
          <div className="flex items-center gap-2 text-xs sm:text-sm text-slate-600 flex-wrap">
            <Link href={fromHref} className="text-blue-700 hover:underline break-words">{company.name}</Link>
            <span>/</span>
            <span>InnovX</span>
          </div>
          <CompanyContextHeader company={company} active="innovx" fromHref={fromHref} />
          <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 text-center">
            <p className="text-sm sm:text-base text-slate-600">InnovX data is not yet available for this company.</p>
          </div>
        </div>
      </Layout>
    );
  }

  const tier1 = innovx.innovx_projects?.filter((p) => p.tier_level === 'Tier 1') || [];
  const tier2 = innovx.innovx_projects?.filter((p) => p.tier_level === 'Tier 2') || [];
  const tier3 = innovx.innovx_projects?.filter((p) => p.tier_level === 'Tier 3') || [];
  const requestedFrom = searchParams.get('from');
  const fromHref = requestedFrom && requestedFrom.startsWith('/') ? requestedFrom : `/companies/${company.id}`;

  return (
    <Layout>
      <div className="px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 space-y-4 sm:space-y-6">
        <div className="flex items-center gap-2 text-xs sm:text-sm text-slate-600 flex-wrap">
          <Link href={fromHref} className="text-blue-700 hover:underline break-words">{company.name}</Link>
          <span>/</span>
          <span>InnovX</span>
        </div>

        <CompanyContextHeader company={company} active="innovx" fromHref={fromHref} />

        <div>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 mb-2 break-words">InnovX</h1>
          <p className="text-sm sm:text-base text-slate-600 break-words">Innovation insights for {innovx.innovx_master?.company_name || company.name}</p>
        </div>

        <section className="space-y-3 sm:space-y-4">
          <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-slate-900">Industry Trends</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            {innovx.industry_trends?.map((trend) => (
              <div key={trend.trend_name} className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 lg:p-6">
                <h3 className="text-base sm:text-lg font-bold text-slate-900 break-words">{trend.trend_name}</h3>
                <p className="text-xs sm:text-sm text-slate-600 mt-2 break-words">{trend.trend_description}</p>
                <div className="flex flex-wrap gap-2 mt-3 sm:mt-4">
                  {trend.trend_drivers.map((driver) => (
                    <Chip key={driver} label={driver} variant="secondary" />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-3 sm:space-y-4">
          <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-slate-900">Competitive Landscape</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            {innovx.competitive_landscape?.map((competitor) => (
              <div key={competitor.competitor_name} className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 lg:p-6">
                <h3 className="text-base sm:text-lg font-bold text-slate-900 break-words">{competitor.competitor_name}</h3>
                <p className="text-xs sm:text-sm text-slate-600 mt-2 break-words">{competitor.market_positioning}</p>
                <div className="flex flex-wrap gap-2 mt-3 sm:mt-4">
                  <Chip label={competitor.innovation_category} variant="primary" />
                  <Chip label={competitor.threat_level} variant="warning" />
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-3 sm:space-y-4">
          <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-slate-900">Innovation Roadmap</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {innovx.innovation_roadmap?.map((item) => (
              <div key={item.innovation_theme} className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 lg:p-6">
                <h3 className="text-base sm:text-lg font-bold text-slate-900 break-words">{item.innovation_theme}</h3>
                <p className="text-xs sm:text-sm text-slate-600 mt-2 break-words">{item.problem_statement}</p>
                <div className="flex flex-wrap gap-2 mt-3 sm:mt-4">
                  <Chip label={item.innovation_type} variant="primary" />
                  <Chip label={item.time_horizon} variant="secondary" />
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-4 sm:space-y-6">
          <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-slate-900">Student Innovation Projects</h2>

          <div>
            <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-3">Tier 1 - Foundational Innovation</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {tier1.map((project) => (
                <div key={project.project_name} className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 lg:p-6 space-y-2 sm:space-y-3">
                  <h4 className="text-base sm:text-lg font-semibold text-slate-900 break-words">{project.project_name}</h4>
                  <p className="text-xs sm:text-sm text-slate-600 break-words">{project.problem_statement}</p>
                  <div className="flex flex-wrap gap-2">
                    {project.backend_technologies.map((tech) => (
                      <Chip key={tech} label={tech} variant="secondary" />
                    ))}
                  </div>
                  <p className="text-xs text-slate-500 break-words">Why it matters: {project.business_value}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-3">Tier 2 - Advanced Innovation</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {tier2.map((project) => (
                <div key={project.project_name} className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 lg:p-6 space-y-2 sm:space-y-3">
                  <h4 className="text-base sm:text-lg font-semibold text-slate-900 break-words">{project.project_name}</h4>
                  <p className="text-xs sm:text-sm text-slate-600 break-words">{project.problem_statement}</p>
                  <div className="flex flex-wrap gap-2">
                    {project.backend_technologies.map((tech) => (
                      <Chip key={tech} label={tech} variant="secondary" />
                    ))}
                  </div>
                  <p className="text-xs text-slate-500 break-words">Why it matters: {project.business_value}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-3">Tier 3 - Breakthrough Innovation</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {tier3.map((project) => (
                <div key={project.project_name} className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 lg:p-6 space-y-2 sm:space-y-3">
                  <h4 className="text-base sm:text-lg font-semibold text-slate-900 break-words">{project.project_name}</h4>
                  <p className="text-xs sm:text-sm text-slate-600 break-words">{project.problem_statement}</p>
                  <div className="flex flex-wrap gap-2">
                    {project.backend_technologies.map((tech) => (
                      <Chip key={tech} label={tech} variant="secondary" />
                    ))}
                  </div>
                  <p className="text-xs text-slate-500 break-words">Why it matters: {project.business_value}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}
