'use client';

import React, { useMemo, useState } from 'react';
import { Layout } from '@/components';
import hiringRoundsMaster from '@/data/Hiring_rounds.json';
import { getCompanySkillLevels } from '@/utils/data';
import { Search, Briefcase, Target, ChevronDown, ChevronUp, Award } from 'lucide-react';

interface HiringSkillSet {
  skill_set_code: string;
  typical_questions: string;
}

interface HiringRound {
  round_name?: string;
  skill_sets: HiringSkillSet[];
}

interface HiringRole {
  role_title: string;
  hiring_rounds: HiringRound[];
}

interface HiringEntry {
  company_name: string;
  job_role_details: HiringRole[];
}

const getProficiencyColor = (code: string) => {
  const colors: Record<string, string> = {
    CU: 'bg-slate-100 text-slate-700 border-slate-300',
    AP: 'bg-blue-100 text-blue-700 border-blue-300',
    AS: 'bg-green-100 text-green-700 border-green-300',
    EV: 'bg-orange-100 text-orange-700 border-orange-300',
    CR: 'bg-purple-100 text-purple-700 border-purple-300',
  };
  return colors[code] || 'bg-gray-100 text-gray-700 border-gray-300';
};

export default function HiringSkillSetPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCompany, setExpandedCompany] = useState<string | null>(null);
  const [expandedRole, setExpandedRole] = useState<string | null>(null);

  const hiringData = useMemo(() => {
    const entries = hiringRoundsMaster as HiringEntry[];
    const skillLevelsData = getCompanySkillLevels();
    
    // Create a map for quick skill level lookup
    const skillLevelsMap = new Map(
      skillLevelsData.companies
        .filter(c => c.company)
        .map(c => [c.company.toLowerCase().trim(), c])
    );

    // Process each company
    const companies = entries.map(entry => {
      const companySkills = skillLevelsMap.get(entry.company_name?.toLowerCase().trim() || '');
      
      let totalRounds = 0;
      let totalSkills = 0;
      const uniqueSkills = new Set<string>();

      entry.job_role_details?.forEach(role => {
        totalRounds += role.hiring_rounds?.length || 0;
        role.hiring_rounds?.forEach(round => {
          round.skill_sets?.forEach(skill => {
            if (skill.skill_set_code) {
              totalSkills += 1;
              uniqueSkills.add(skill.skill_set_code);
            }
          });
        });
      });

      return {
        company_name: entry.company_name,
        roles: entry.job_role_details || [],
        totalRoles: entry.job_role_details?.length || 0,
        totalRounds,
        totalSkills,
        uniqueSkillsCount: uniqueSkills.size,
        companySkillLevels: companySkills,
      };
    });

    return {
      companies: companies.sort((a, b) => (a.company_name || '').localeCompare(b.company_name || '')),
      totalCompanies: companies.length,
      totalRoles: companies.reduce((sum, c) => sum + c.totalRoles, 0),
      totalRounds: companies.reduce((sum, c) => sum + c.totalRounds, 0),
      totalSkills: companies.reduce((sum, c) => sum + c.totalSkills, 0),
    };
  }, []);

  const filteredCompanies = useMemo(() => {
    if (!searchQuery.trim()) return hiringData.companies;
    
    const query = searchQuery.toLowerCase();
    return hiringData.companies.filter(c =>
      c.company_name?.toLowerCase().includes(query)
    );
  }, [hiringData.companies, searchQuery]);

  return (
    <Layout>
      <div className="space-y-6 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-2">
            Company Hiring Skills
          </h1>
          <p className="text-slate-600">
            Detailed breakdown of skills required by each company in their hiring process
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-4 shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <Target className="h-5 w-5 opacity-80" />
              <p className="text-xs font-medium opacity-90">Companies</p>
            </div>
            <p className="text-3xl font-bold">{hiringData.totalCompanies}</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl p-4 shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <Briefcase className="h-5 w-5 opacity-80" />
              <p className="text-xs font-medium opacity-90">Job Roles</p>
            </div>
            <p className="text-3xl font-bold">{hiringData.totalRoles}</p>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-4 shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <Target className="h-5 w-5 opacity-80" />
              <p className="text-xs font-medium opacity-90">Hiring Rounds</p>
            </div>
            <p className="text-3xl font-bold">{hiringData.totalRounds}</p>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-xl p-4 shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <Award className="h-5 w-5 opacity-80" />
              <p className="text-xs font-medium opacity-90">Total Skills</p>
            </div>
            <p className="text-3xl font-bold">{hiringData.totalSkills}</p>
          </div>
        </div>

        {/* Search */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-500" />
            <input
              type="text"
              placeholder="Search companies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
            />
          </div>
          <div className="mt-2 text-sm text-slate-600">
            Showing <span className="font-bold text-slate-900">{filteredCompanies.length}</span> of{' '}
            <span className="font-bold text-slate-900">{hiringData.companies.length}</span> companies
          </div>
        </div>

        {/* Companies List */}
        <div className="space-y-4">
          {filteredCompanies.map((company) => {
            const isExpanded = expandedCompany === company.company_name;

            return (
              <div
                key={company.company_name}
                className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow"
              >
                {/* Company Header */}
                <div
                  className="p-5 cursor-pointer"
                  onClick={() => setExpandedCompany(isExpanded ? null : company.company_name)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-slate-900 mb-2">
                        {company.company_name}
                      </h3>

                      {/* Stats Badges */}
                      <div className="flex flex-wrap gap-2 mb-3">
                        <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">
                          {company.totalRoles} Roles
                        </span>
                        <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-medium">
                          {company.totalRounds} Rounds
                        </span>
                        <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-medium">
                          {company.uniqueSkillsCount} Unique Skills
                        </span>
                        <span className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-xs font-medium">
                          {company.totalSkills} Total Mentions
                        </span>
                      </div>
                    </div>

                    <button className="ml-4 p-2 hover:bg-slate-100 rounded-lg transition-colors">
                      {isExpanded ? (
                        <ChevronUp className="h-5 w-5 text-slate-600" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-slate-600" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="border-t border-slate-200 p-5 bg-slate-50">
                    <h4 className="text-sm font-bold text-slate-900 mb-4 uppercase tracking-wide">
                      Job Roles & Required Skills
                    </h4>

                    <div className="space-y-4">
                      {company.roles.map((role, roleIdx) => {
                        const roleKey = `${company.company_name}-${roleIdx}`;
                        const isRoleExpanded = expandedRole === roleKey;
                        
                        // Count total skills for this role
                        const roleSkillCount = role.hiring_rounds?.reduce(
                          (sum, round) => sum + (round.skill_sets?.length || 0),
                          0
                        ) || 0;

                        return (
                          <div
                            key={roleKey}
                            className="bg-white rounded-lg border border-slate-200"
                          >
                            {/* Role Header */}
                            <div
                              className="p-4 cursor-pointer hover:bg-slate-50 transition-colors"
                              onClick={() => setExpandedRole(isRoleExpanded ? null : roleKey)}
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <h5 className="text-base font-semibold text-slate-900 mb-2">
                                    {role.role_title}
                                  </h5>
                                  <div className="flex gap-2">
                                    <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded text-xs font-medium">
                                      {role.hiring_rounds?.length || 0} Rounds
                                    </span>
                                    <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-medium">
                                      {roleSkillCount} Skills
                                    </span>
                                  </div>
                                </div>
                                <button className="p-1">
                                  {isRoleExpanded ? (
                                    <ChevronUp className="h-4 w-4 text-slate-600" />
                                  ) : (
                                    <ChevronDown className="h-4 w-4 text-slate-600" />
                                  )}
                                </button>
                              </div>
                            </div>

                            {/* Role Details */}
                            {isRoleExpanded && (
                              <div className="border-t border-slate-200 p-4 bg-slate-50">
                                {role.hiring_rounds?.map((round, roundIdx) => (
                                  <div key={roundIdx} className="mb-4 last:mb-0">
                                    <div className="flex items-center gap-2 mb-3">
                                      <span className="bg-slate-700 text-white px-2 py-1 rounded text-xs font-bold">
                                        Round {roundIdx + 1}
                                      </span>
                                      {round.round_name && (
                                        <span className="text-sm text-slate-600">
                                          {round.round_name}
                                        </span>
                                      )}
                                    </div>

                                    {round.skill_sets && round.skill_sets.length > 0 ? (
                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                        {round.skill_sets.map((skill, skillIdx) => {
                                          // Try to match with company skill levels
                                          const skillLevelData = company.companySkillLevels?.skills[
                                            skill.skill_set_code.toLowerCase().replace(/\s+/g, '_')
                                          ];

                                          return (
                                            <div
                                              key={skillIdx}
                                              className="bg-white rounded-lg border border-slate-200 p-3"
                                            >
                                              <div className="flex items-start justify-between mb-2">
                                                <div className="flex-1">
                                                  <h6 className="text-sm font-semibold text-slate-900">
                                                    {skill.skill_set_code}
                                                  </h6>
                                                  {skillLevelData && (
                                                    <div className="flex items-center gap-2 mt-1">
                                                      <span
                                                        className={`px-2 py-0.5 rounded text-xs font-bold ${getProficiencyColor(
                                                          skillLevelData.proficiency_code
                                                        )}`}
                                                      >
                                                        {skillLevelData.proficiency_code}
                                                      </span>
                                                      <span className="text-xs text-slate-600">
                                                        Level {skillLevelData.level}/10
                                                      </span>
                                                    </div>
                                                  )}
                                                </div>
                                              </div>

                                              {skill.typical_questions && (
                                                <p className="text-xs text-slate-600 mt-2 italic">
                                                  &quot;{skill.typical_questions}&quot;
                                                </p>
                                              )}

                                              {skillLevelData && (
                                                <div className="mt-2">
                                                  <div className="relative h-1.5 bg-slate-100 rounded-full overflow-hidden">
                                                    <div
                                                      className="absolute left-0 top-0 h-full bg-blue-500"
                                                      style={{
                                                        width: `${(skillLevelData.level / 10) * 100}%`,
                                                      }}
                                                    />
                                                  </div>
                                                </div>
                                              )}
                                            </div>
                                          );
                                        })}
                                      </div>
                                    ) : (
                                      <p className="text-sm text-slate-500 italic">
                                        No specific skills listed for this round
                                      </p>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {filteredCompanies.length === 0 && (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <p className="text-slate-500 text-lg">No companies found matching your search.</p>
            <button
              onClick={() => setSearchQuery('')}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Clear Search
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
