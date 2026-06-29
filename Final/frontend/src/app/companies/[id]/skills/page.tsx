'use client';

import React, { useMemo } from 'react';
import { use } from 'react';
import { Layout } from '@/components';
import { getCompanyById, getCompanySkillLevel, getHiringRoundsData } from '@/utils/data';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import CompanyContextHeader from '@/components/CompanyDetail/CompanyContextHeader';

interface PageProps {
  params: Promise<{ id: string }>;
}

const getProficiencyColor = (code: string) => {
  const colors: Record<string, { bg: string; text: string; border: string }> = {
    CU: { bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-300' },
    AP: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
    AS: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
    EV: { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-300' },
    CR: { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-300' },
  };
  return colors[code] || { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-300' };
};

const formatSkillName = (skill: string) => {
  return skill
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

export default function CompanySkillPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const searchParams = useSearchParams();
  const company = getCompanyById(resolvedParams.id);
  
  const skillData = useMemo(() => {
    if (!company) return null;
    
    const companySkillLevels = getCompanySkillLevel(company.name);
    const hiringData = getHiringRoundsData(company.name);
    
    // Process hiring rounds to get skill mentions
    const skillMentions = new Map<string, { count: number; examples: string[]; roles: Set<string> }>();
    
    if (hiringData?.job_role_details) {
      hiringData.job_role_details.forEach((role) => {
        role.hiring_rounds?.forEach((round) => {
          round.skill_sets?.forEach((skill) => {
            const skillCode = skill.skill_set_code;
            if (!skillCode) return;
            
            if (!skillMentions.has(skillCode)) {
              skillMentions.set(skillCode, { count: 0, examples: [], roles: new Set() });
            }
            
            const data = skillMentions.get(skillCode)!;
            data.count += 1;
            data.roles.add(role.role_title || 'General Role');
            if (skill.typical_questions && data.examples.length < 3) {
              data.examples.push(skill.typical_questions);
            }
          });
        });
      });
    }
    
    return {
      skillLevels: companySkillLevels,
      hiringData,
      skillMentions,
      totalRoles: hiringData?.job_role_details?.length || 0,
      totalRounds: hiringData?.job_role_details?.reduce(
        (sum, role) => sum + (role.hiring_rounds?.length || 0),
        0
      ) || 0,
    };
  }, [company]);

  if (!company) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <p className="text-lg text-slate-600">Company not found</p>
        </div>
      </Layout>
    );
  }

  if (!skillData) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <p className="text-lg text-slate-600">Loading...</p>
        </div>
      </Layout>
    );
  }

  const requestedFrom = searchParams.get('from');
  const fromHref = requestedFrom && requestedFrom.startsWith('/') ? requestedFrom : `/companies/${company.id}`;

  return (
    <Layout>
      <div className="px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 space-y-4 sm:space-y-6">
        <div className="flex items-center gap-2 text-xs sm:text-sm text-slate-600 flex-wrap">
          <Link href={fromHref} className="text-blue-700 hover:underline break-words">
            {company.name}
          </Link>
          <span>/</span>
          <span>Hiring Skill Sets</span>
        </div>

        <CompanyContextHeader company={company} active="skills" fromHref={fromHref} />

        <div>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 mb-2 break-words">
            Hiring Skill Requirements
          </h1>
          <p className="text-sm sm:text-base text-slate-600">
            Comprehensive breakdown of skill proficiency levels and hiring process requirements
          </p>
        </div>

        {/* Skill Proficiency Levels */}
        {skillData.skillLevels && (
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Required Skill Proficiency Levels</h2>
            <p className="text-sm text-slate-600 mb-6">
              Expected proficiency levels for technical skills at {company.name}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(skillData.skillLevels.skills)
                .sort((a, b) => b[1].level - a[1].level)
                .map(([skillName, skillInfo]) => {
                  const colors = getProficiencyColor(skillInfo.proficiency_code);
                  const mentions = skillData.skillMentions.get(skillName.replace(/_/g, ' '));

                  return (
                    <div
                      key={skillName}
                      className="bg-white rounded-lg border border-slate-200 p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <h3 className="text-base font-semibold text-slate-900 flex-1">
                          {formatSkillName(skillName)}
                        </h3>
                        <span
                          className={`${colors.bg} ${colors.text} border ${colors.border} px-2 py-1 rounded text-xs font-bold ml-2`}
                        >
                          {skillInfo.proficiency_code}
                        </span>
                      </div>

                      {/* Level Display */}
                      <div className="mb-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-slate-600">Required Level</span>
                          <span className="text-lg font-bold text-slate-900">
                            {skillInfo.level}/10
                          </span>
                        </div>
                        <div className="relative h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className="absolute left-0 top-0 h-full bg-gradient-to-r from-blue-400 to-blue-600"
                            style={{ width: `${(skillInfo.level / 10) * 100}%` }}
                          />
                        </div>
                      </div>

                      {/* Proficiency Description */}
                      <div className="mb-3">
                        <p className="text-xs font-medium text-slate-700 mb-1">
                          {skillInfo.proficiency_name}
                        </p>
                        <p className="text-xs text-slate-600">{skillInfo.proficiency_description}</p>
                      </div>

                      {/* Hiring Process Mentions */}
                      {mentions && (
                        <div className="pt-3 border-t border-slate-200">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs font-medium text-blue-600">
                              Tested in {mentions.count} rounds
                            </span>
                          </div>
                          {mentions.examples.length > 0 && (
                            <p className="text-xs text-slate-500 italic line-clamp-2">
                              &quot;{mentions.examples[0]}&quot;
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {/* Hiring Process Breakdown */}
        {skillData.hiringData?.job_role_details && skillData.hiringData.job_role_details.length > 0 && (
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Hiring Process Skills</h2>
            <p className="text-sm text-slate-600 mb-6">
              Skills tested during the hiring process for various roles
            </p>

            <div className="space-y-4">
              {skillData.hiringData.job_role_details.map((role, roleIdx: number) => {
                const totalSkills = role.hiring_rounds?.reduce(
                  (sum: number, round) => sum + (round.skill_sets?.length || 0),
                  0
                ) || 0;

                return (
                  <div key={roleIdx} className="border border-slate-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-slate-900">{role.role_title}</h3>
                      <div className="flex gap-2">
                        <span className="bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-xs font-medium">
                          {role.hiring_rounds?.length || 0} Rounds
                        </span>
                        <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">
                          {totalSkills} Skills
                        </span>
                      </div>
                    </div>

                    {role.hiring_rounds?.map((round, roundIdx: number) => (
                      <div key={roundIdx} className="mb-4 last:mb-0">
                        <div className="flex items-center gap-2 mb-3">
                          <span className="bg-slate-700 text-white px-2 py-1 rounded text-xs font-bold">
                            Round {roundIdx + 1}
                          </span>
                          {round.round_name && (
                            <span className="text-sm font-medium text-slate-600">
                              {round.round_name}
                            </span>
                          )}
                        </div>

                        {round.skill_sets && round.skill_sets.length > 0 ? (
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 ml-4">
                            {round.skill_sets.map((skill, skillIdx: number) => {
                              // Try to find matching skill level data
                              const skillKey = skill.skill_set_code?.toLowerCase().replace(/\s+/g, '_');
                              const levelData = skillKey ? skillData.skillLevels?.skills[skillKey] : undefined;

                              return (
                                <div
                                  key={skillIdx}
                                  className="bg-slate-50 rounded-lg border border-slate-200 p-3"
                                >
                                  <div className="flex items-start justify-between mb-2">
                                    <h4 className="text-sm font-semibold text-slate-900 flex-1">
                                      {skill.skill_set_code}
                                    </h4>
                                    {levelData && (
                                      <span
                                        className={`px-2 py-0.5 rounded text-xs font-bold ml-2 ${
                                          getProficiencyColor(levelData.proficiency_code).bg
                                        } ${getProficiencyColor(levelData.proficiency_code).text}`}
                                      >
                                        {levelData.proficiency_code} {levelData.level}
                                      </span>
                                    )}
                                  </div>

                                  {skill.typical_questions && (
                                    <p className="text-xs text-slate-600 italic">
                                      &quot;{skill.typical_questions}&quot;
                                    </p>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <p className="text-sm text-slate-500 italic ml-4">
                            No specific skills listed
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* No Data Message */}
        {!skillData.skillLevels && !skillData.hiringData && (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <p className="text-slate-500 text-lg">
              No skill data available for {company.name} at this time.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
