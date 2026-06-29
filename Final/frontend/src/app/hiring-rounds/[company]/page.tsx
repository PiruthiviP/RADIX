'use client';

import React from 'react';
import { Lightbulb, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Layout } from '@/components';
import { getHiringRoundsData } from '@/utils/data';
import { Chip } from '@/components/UI';

export default function CompanyHiringDetailsPage() {
  const params = useParams();
  const companyName = params?.company ? decodeURIComponent(params.company as string) : '';
  const hiringData = React.useMemo(() => {
    if (!companyName) return undefined;
    return getHiringRoundsData(companyName);
  }, [companyName]);

  const isLoading = !companyName;

  const hiringRounds = hiringData?.job_role_details || [];

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <p className="text-lg text-slate-600">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-4 sm:space-y-6 lg:space-y-8 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {/* Back Button */}
        <Link 
          href="/hiring-rounds"
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 font-semibold transition-colors touch-manipulation"
        >
          <ArrowLeft className="h-4 w-4 sm:h-5 sm:w-5" />
          <span className="text-sm sm:text-base">Back to All Companies</span>
        </Link>

        {/* Company Header */}
        <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-4 sm:p-5 lg:p-6">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 mb-2 break-words">{companyName}</h1>
          <p className="text-sm sm:text-base text-slate-700">{hiringRounds.length} active hiring roles</p>
        </div>

        {/* Debug Info - Remove after testing */}
        {!hiringData && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">
              <strong>Debug:</strong> Looking for company: &quot;{companyName}&quot;
            </p>
          </div>
        )}

        {/* Hiring Details */}
        {hiringRounds.length > 0 ? (
          <div className="space-y-4 sm:space-y-6">
            {hiringRounds.map((role, idx: number) => (
              <div key={idx} className="bg-white border border-slate-200 rounded-xl overflow-hidden hover:shadow-lg transition-shadow">
                <div className="bg-gradient-to-r from-slate-50 to-slate-100 p-4 sm:p-5 lg:p-6 border-b border-slate-200">
                  <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-slate-900 mb-3 sm:mb-4 break-words">{role.role_title}</h2>
                  <p className="text-xs sm:text-sm text-slate-600 mb-3 sm:mb-4 break-words">{role.job_description}</p>
                  
                  {/* Info Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                    <div className="bg-white rounded-lg border border-green-200 p-3 sm:p-4">
                      <p className="text-xs text-slate-600 font-semibold mb-1 sm:mb-2">Compensation ({role.compensation})</p>
                      <p className="text-xl sm:text-2xl font-bold text-green-600 break-words">₹{role.ctc_or_stipend?.toLocaleString()}</p>
                      {role.bonus && (
                        <p className="text-xs text-slate-600 mt-1 sm:mt-2 break-words">{role.bonus}</p>
                      )}
                    </div>

                    <div className="bg-white rounded-lg border border-blue-200 p-3 sm:p-4">
                      <p className="text-xs text-slate-600 font-semibold mb-1 sm:mb-2">Role Category</p>
                      <p className="text-base sm:text-lg font-bold text-blue-700 break-words">{role.role_category}</p>
                      <p className="text-xs text-slate-600 mt-1 sm:mt-2 break-words">Opportunity: {role.opportunity_type}</p>
                    </div>

                    <div className="bg-white rounded-lg border border-purple-200 p-3 sm:p-4 sm:col-span-2 lg:col-span-1">
                      <p className="text-xs text-slate-600 font-semibold mb-1 sm:mb-2">Benefits</p>
                      <p className="text-xs sm:text-sm text-slate-700 font-medium break-words">{role.benefits_summary}</p>
                    </div>
                  </div>
                </div>

                <div className="p-4 sm:p-5 lg:p-6 space-y-4 sm:space-y-6">
                  {/* Hiring Rounds */}
                  {role.hiring_rounds && role.hiring_rounds.length > 0 && (
                    <div>
                      <h3 className="font-bold text-slate-900 mb-3 sm:mb-4 text-base sm:text-lg lg:text-xl">Interview Rounds ({role.hiring_rounds.length})</h3>
                      <div className="space-y-3 sm:space-y-4">
                        {role.hiring_rounds.map((round, i: number) => (
                          <div
                            key={i}
                            className="border border-slate-200 rounded-lg p-3 sm:p-4 bg-slate-50"
                          >
                            <div className="flex items-start gap-3 sm:gap-4">
                              <span className="font-bold text-white bg-blue-600 rounded-full w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center flex-shrink-0 text-sm sm:text-base">
                                {i + 1}
                              </span>
                              <div className="flex-1 space-y-2 sm:space-y-3 min-w-0">
                                <div>
                                  <p className="font-bold text-slate-900 text-base sm:text-lg break-words">{round.round_name}</p>
                                  <p className="text-xs sm:text-sm text-slate-600 mt-1 break-words">
                                    <span className="font-semibold">{round.round_category}</span> • {round.assessment_mode}
                                  </p>
                                </div>
                                
                                {/* Skills */}
                                {round.skill_sets && round.skill_sets.length > 0 && (
                                  <div>
                                    <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Required Skills</p>
                                    <div className="flex flex-wrap gap-2">
                                      {round.skill_sets.map((skill, si: number) => (
                                        <Chip key={si} label={skill.skill_set_code || 'General Skill'} variant="secondary" />
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Preparation Tips */}
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 sm:p-5">
                    <p className="text-xs sm:text-sm font-semibold text-green-900 mb-2 sm:mb-3 flex items-center gap-2">
                      <Lightbulb className="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" />
                      <span className="break-words">Preparation Tips for {role.role_title}</span>
                    </p>
                    <ul className="text-xs sm:text-sm text-green-800 space-y-1.5 sm:space-y-2 list-disc list-inside">
                      <li className="break-words">Review the role description and key requirements thoroughly</li>
                      <li className="break-words">Practice each round type in the order mentioned above</li>
                      <li className="break-words">Focus on the specific skills listed for each round</li>
                      <li className="break-words">Prepare real-world examples matching the role category</li>
                      <li className="break-words">Research {companyName}&apos;s technology stack and company culture</li>
                      <li className="break-words">Practice coding/technical problems for {role.role_category} positions</li>
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 lg:p-12 text-center">
            <p className="text-base sm:text-lg text-slate-600 break-words">No hiring rounds data available for {companyName}</p>
            <Link 
              href="/hiring-rounds"
              className="mt-4 inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 font-semibold touch-manipulation"
            >
              <ArrowLeft className="h-4 w-4" />
              <span className="text-sm sm:text-base">Back to All Companies</span>
            </Link>
          </div>
        )}
      </div>
    </Layout>
  );
}
