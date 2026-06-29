'use client';

import React from 'react';
import { Layout } from '@/components';
import Link from 'next/link';
import { 
  Sparkles, 
  Building2,
  Globe,
  Target,
  Briefcase,
  ChevronRight
} from 'lucide-react';
import innovxData from '@/data/innovx_master.json';

export default function InnovXPage() {
  const companies = innovxData.companies;

  return (
    <Layout>
      <div className="min-h-screen">
        {/* Hero Section */}
        <div className="relative bg-gradient-to-br from-blue-600 to-blue-800 text-white overflow-hidden">
          <div className="relative px-4 sm:px-6 lg:px-8 py-8 sm:py-12 lg:py-16 max-w-7xl mx-auto">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 mb-4 sm:mb-6">
              <div className="relative">
                <Sparkles className="h-12 w-12 sm:h-14 sm:w-14 lg:h-16 lg:w-16" />
              </div>
              <div>
                <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">InnovX Intelligence</h1>
                <p className="text-base sm:text-lg lg:text-xl text-blue-50 mt-1 sm:mt-2">Innovation Insights & Strategic Analysis Platform</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mt-6 sm:mt-8">
              <div className="bg-white/95 rounded-lg sm:rounded-xl p-3 sm:p-4 border border-white/70 shadow-sm">
                <div className="flex items-center gap-2 sm:gap-3">
                  <Building2 className="h-6 w-6 sm:h-7 sm:w-7 lg:h-8 lg:w-8 text-blue-600" />
                  <div>
                    <p className="text-2xl sm:text-3xl font-bold text-slate-900">{innovxData.total_companies}</p>
                    <p className="text-xs sm:text-sm text-slate-600">Companies Analyzed</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white/95 rounded-lg sm:rounded-xl p-3 sm:p-4 border border-white/70 shadow-sm">
                <div className="flex items-center gap-2 sm:gap-3">
                  <Target className="h-6 w-6 sm:h-7 sm:w-7 lg:h-8 lg:w-8 text-blue-600" />
                  <div>
                    <p className="text-2xl sm:text-3xl font-bold text-slate-900">5</p>
                    <p className="text-xs sm:text-sm text-slate-600">Data Sections</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white/95 rounded-lg sm:rounded-xl p-3 sm:p-4 border border-white/70 shadow-sm">
                <div className="flex items-center gap-2 sm:gap-3">
                  <Sparkles className="h-6 w-6 sm:h-7 sm:w-7 lg:h-8 lg:w-8 text-blue-600" />
                  <div>
                    <p className="text-2xl sm:text-3xl font-bold text-slate-900">360°</p>
                    <p className="text-xs sm:text-sm text-slate-600">Innovation View</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="px-4 sm:px-6 lg:px-8 py-6 sm:py-8 max-w-7xl mx-auto">
          <div className="mb-4 sm:mb-6">
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 mb-2">Select a Company</h2>
            <p className="text-sm sm:text-base text-slate-600">Click on any company card to view detailed innovation intelligence</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">
            {companies.map((company, idx) => {
              const companyData = company.innovx_master;
              if (!companyData) return null;

              return (
                <Link
                  key={idx}
                  href={`/innovx/${encodeURIComponent(companyData.company_name)}`}
                  className="group"
                >
                  <div className="bg-white rounded-xl shadow-lg border-2 border-slate-200 p-6 hover:border-blue-400 hover:shadow-xl transition-all duration-300 h-full">
                    {/* Company Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start gap-3 flex-1">
                        <div className="bg-blue-100 p-3 rounded-lg">
                          <Building2 className="h-6 w-6 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-bold text-slate-900 group-hover:text-blue-600 transition-colors mb-1">
                            {companyData.company_name}
                          </h3>
                          <span className="inline-block bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold">
                            {companyData.industry}
                          </span>
                        </div>
                      </div>
                      <ChevronRight className="h-5 w-5 text-slate-500 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                    </div>

                    {/* Company Details */}
                    <div className="space-y-3">
                      <div className="flex items-start gap-2">
                        <Briefcase className="h-4 w-4 text-slate-500 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Sub-Industry</p>
                          <p className="text-sm text-slate-900 font-medium">{companyData.sub_industry}</p>
                        </div>
                      </div>

                      <div className="flex items-start gap-2">
                        <Target className="h-4 w-4 text-slate-500 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Target Market</p>
                          <p className="text-sm text-slate-900 font-medium">{companyData.target_market}</p>
                        </div>
                      </div>

                      <div className="flex items-start gap-2">
                        <Globe className="h-4 w-4 text-slate-500 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Geographic Focus</p>
                          <p className="text-sm text-slate-900 font-medium">{companyData.geographic_focus}</p>
                        </div>
                      </div>

                      <div className="pt-3 border-t border-slate-200">
                        <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">Business Model</p>
                        <p className="text-sm text-slate-900 font-medium line-clamp-2">{companyData.core_business_model}</p>
                      </div>
                    </div>

                    {/* View Details Button */}
                    <div className="mt-4 pt-4 border-t border-slate-200">
                      <div className="flex items-center justify-between text-blue-600 group-hover:text-blue-700 font-semibold text-sm">
                        <span>View Innovation Intelligence</span>
                        <ChevronRight className="h-4 w-4" />
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </Layout>
  );
}

