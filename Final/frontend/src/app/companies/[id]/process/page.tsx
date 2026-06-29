'use client';

import React, { useState } from 'react';
import { use } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Layout } from '@/components';
import { getCompanyById, getHiringRoundsData } from '@/utils/data';
import { Chip } from '@/components/UI';
import CompanyContextHeader from '@/components/CompanyDetail/CompanyContextHeader';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function CompanyHiringProcessPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const searchParams = useSearchParams();
  const company = getCompanyById(resolvedParams.id);
  const hiringData = getHiringRoundsData(company?.name);
  const [activeRoleIndex, setActiveRoleIndex] = useState(0);

  if (!company) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <p className="text-lg text-slate-600">Company not found</p>
        </div>
      </Layout>
    );
  }

  const roles = hiringData?.job_role_details || [];
  const activeRole = roles[Math.min(activeRoleIndex, Math.max(roles.length - 1, 0))];
  const requestedFrom = searchParams.get('from');
  const fromHref = requestedFrom && requestedFrom.startsWith('/') ? requestedFrom : `/companies/${company.id}`;

  return (
    <Layout>
      <div className="px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 space-y-4 sm:space-y-6">
        <div className="flex items-center gap-2 text-xs sm:text-sm text-slate-600 flex-wrap">
          <Link href={fromHref} className="text-blue-700 hover:underline break-words">{company.name}</Link>
          <span>/</span>
          <span>Hiring Process</span>
        </div>

        <CompanyContextHeader company={company} active="process" fromHref={fromHref} />

        <div>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 mb-2 break-words">Hiring Process</h1>
          <p className="text-sm sm:text-base text-slate-600">Round-by-round selection flow</p>
        </div>

        {roles.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 text-center">
            <p className="text-sm sm:text-base text-slate-600">No hiring rounds data available for this company yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
            <aside className="lg:col-span-4">
              <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 space-y-3 sm:space-y-4">
                <div>
                  <h2 className="text-base sm:text-lg font-bold text-slate-900">Roles</h2>
                  <p className="text-xs sm:text-sm text-slate-600 mt-1">Pick a role to see its round timeline.</p>
                </div>

                <div className="space-y-2 sm:space-y-3">
                  {roles.map((role, index) => {
                    const isActive = index === activeRoleIndex;
                    return (
                      <button
                        key={`${role.role_title}-${role.opportunity_type}`}
                        onClick={() => setActiveRoleIndex(index)}
                        className={`w-full text-left border rounded-xl p-3 sm:p-4 transition-colors touch-manipulation ${
                          isActive ? 'border-blue-500 bg-blue-50' : 'border-slate-200 bg-white hover:bg-slate-50'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2 sm:gap-3">
                          <div className="min-w-0">
                            <p className="text-xs sm:text-sm font-semibold text-slate-900 break-words">{role.role_title}</p>
                            <p className="text-xs text-slate-600 mt-1 break-words">{role.role_category}</p>
                          </div>
                          <div className="flex-shrink-0">
                            <Chip label={role.opportunity_type || 'Employment'} variant={isActive ? 'primary' : 'secondary'} />
                          </div>
                        </div>
                        <p className="text-xs text-slate-500 mt-2 sm:mt-3">{role.hiring_rounds?.length || 0} rounds</p>
                      </button>
                    );
                  })}
                </div>
              </div>
            </aside>

            <section className="lg:col-span-8 space-y-4 sm:space-y-6">
              <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 lg:p-6">
                <div className="flex flex-wrap items-start justify-between gap-3 sm:gap-4">
                  <div className="min-w-0">
                    <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-slate-900 break-words">{activeRole?.role_title}</h2>
                    <p className="text-xs sm:text-sm text-slate-600 mt-2 break-words">{activeRole?.job_description}</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {activeRole?.role_category && <Chip label={activeRole.role_category} variant="primary" />}
                    {activeRole?.opportunity_type && <Chip label={activeRole.opportunity_type} variant="secondary" />}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mt-4 sm:mt-6">
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 sm:p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">Compensation</p>
                    {(activeRole?.compensation || activeRole?.ctc_or_stipend) && (
                      <p className="text-xs sm:text-sm font-semibold text-slate-900 mt-1 break-words">
                        {activeRole?.compensation}{activeRole?.compensation && activeRole?.ctc_or_stipend ? ' · ' : ''}{activeRole?.ctc_or_stipend}
                      </p>
                    )}
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 sm:p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">Bonus</p>
                    {activeRole?.bonus && <p className="text-xs sm:text-sm font-semibold text-slate-900 mt-1 break-words">{activeRole?.bonus}</p>}
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 sm:p-4 sm:col-span-3 lg:col-span-1">
                    <p className="text-xs uppercase tracking-wide text-slate-500">Benefits</p>
                    {activeRole?.benefits_summary && <p className="text-xs sm:text-sm font-semibold text-slate-900 mt-1 break-words">{activeRole?.benefits_summary}</p>}
                  </div>
                </div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 lg:p-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-base sm:text-lg font-bold text-slate-900">Round Timeline</h3>
                  <span className="text-xs sm:text-sm text-slate-600">{activeRole?.hiring_rounds?.length || 0} rounds</span>
                </div>

                <div className="mt-4 sm:mt-6 space-y-4 sm:space-y-6">
                  {activeRole?.hiring_rounds?.map((round, index) => (
                    <div key={`${activeRole?.role_title}-${round.round_number ?? index + 1}`} className="relative pl-8 sm:pl-10">
                      <div className="absolute left-0 top-1.5 h-6 w-6 sm:h-7 sm:w-7 rounded-full bg-blue-600 text-white text-xs font-semibold flex items-center justify-center">
                        {round.round_number ?? index + 1}
                      </div>
                      {index < (activeRole?.hiring_rounds?.length || 0) - 1 && (
                        <div className="absolute left-2.5 sm:left-3 top-9 sm:top-10 bottom-0 w-px bg-slate-200" />
                      )}

                      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 sm:p-5">
                        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                          <span className="text-xs sm:text-sm font-semibold text-slate-900 break-words">{round.round_name || `Round ${index + 1}`}</span>
                          <Chip label={round.round_category || 'General'} variant="primary" />
                          <Chip label={`${round.evaluation_type || 'Evaluation'} · ${round.assessment_mode || 'Online'}`} variant="secondary" />
                        </div>

                        <div className="mt-3 sm:mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                          {(round.skill_sets || []).map((skill, skillIndex) => (
                            <div key={`${round.round_number ?? index + 1}-${skill.skill_set_code ?? skillIndex}`} className="bg-white border border-slate-200 rounded-lg p-3 sm:p-4">
                              <p className="text-xs sm:text-sm font-semibold text-slate-900 break-words">{skill.skill_set_code || 'General Skill'}</p>
                              <p className="text-xs text-slate-600 mt-2 break-words">{skill.typical_questions || 'No sample question available.'}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>
        )}
      </div>
    </Layout>
  );
}
