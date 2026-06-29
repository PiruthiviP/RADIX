'use client';

import React from 'react';
import { Briefcase } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { Layout } from '@/components';
import hiringRoundData from '@/data/Hiring_rounds.json';
import { getCompaniesShort } from '@/utils/data';

interface HiringCompany {
  name: string;
  logoUrl: string;
  jobRoles: string[];
  totalRounds: number;
}

interface HiringRoleDetail {
  role_title: string;
  hiring_rounds?: unknown[];
}

interface HiringRoundCompany {
  company_name: string;
  job_role_details?: HiringRoleDetail[];
}

// Get unique companies from hiring data with logos
function getUniqueCompaniesFromHiring(): HiringCompany[] {
  const allCompanies = getCompaniesShort();
  const data = hiringRoundData as HiringRoundCompany[];
  
  return data.map((company) => {
    const companyData = allCompanies.find(c => c.name === company.company_name);
    return {
      name: company.company_name,
      logoUrl: companyData?.logo_url || '',
      jobRoles: company.job_role_details?.map((role) => role.role_title) || [],
      totalRounds: company.job_role_details?.reduce((sum, role) => sum + (role.hiring_rounds?.length || 0), 0) || 0,
    };
  });
}

export default function HiringRoundsPage() {
  const companies = getUniqueCompaniesFromHiring();

  return (
    <Layout>
      <div className="space-y-6 sm:space-y-8 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Hiring Rounds</h1>
          <p className="text-sm sm:text-base text-slate-600">Select a company to explore their recruitment process and interview rounds</p>
        </div>

        {/* Companies Grid */}
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 mb-3 sm:mb-4">All Companies</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">
            {companies.map((company, idx) => (
              <Link
                key={idx}
                href={`/hiring-rounds/${encodeURIComponent(company.name)}`}
                className="cursor-pointer transition-all transform hover:scale-105 active:scale-95 p-4 sm:p-5 lg:p-6 rounded-lg sm:rounded-xl border-2 border-slate-200 bg-white hover:border-blue-400 hover:shadow-lg touch-manipulation"
              >
                {/* Company Logo and Name */}
                <div className="flex items-center gap-3 sm:gap-4 mb-3 sm:mb-4 pb-3 sm:pb-4 border-b border-slate-200">
                  {company.logoUrl ? (
                    <div className="relative w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 flex-shrink-0 bg-white rounded-lg border border-slate-200 p-2">
                      <Image
                        src={company.logoUrl}
                        alt={`${company.name} logo`}
                        fill
                        className="object-contain"
                        unoptimized
                      />
                    </div>
                  ) : (
                    <div className="w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 flex-shrink-0 bg-slate-100 rounded-lg flex items-center justify-center">
                      <Briefcase className="h-6 w-6 sm:h-7 sm:w-7 lg:h-8 lg:w-8 text-slate-500" />
                    </div>
                  )}
                  <h3 className="text-base sm:text-lg font-bold text-slate-900 flex-1 break-words">{company.name}</h3>
                </div>
                
                <div className="space-y-3 sm:space-y-4">
                  {/* Available Job Roles */}
                  <div>
                    <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">Available Job Roles</p>
                    <div className="space-y-2 max-h-32 sm:max-h-40 overflow-y-auto">
                      {company.jobRoles.map((role, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-xs sm:text-sm text-slate-700">
                          <Briefcase className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-600 flex-shrink-0" />
                          <span className="break-words">{role}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Hiring Rounds Count */}
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 border border-blue-200">
                    <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Total Hiring Rounds</p>
                    <p className="text-2xl font-bold text-blue-700 mt-1">{company.totalRounds}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
