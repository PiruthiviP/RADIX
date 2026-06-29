'use client';

import React, { useMemo, useState } from 'react';
import { Layout } from '@/components';
import { getCompanySkillLevels } from '@/utils/data';
import { Search, Filter, TrendingUp, Award, BarChart3, Activity, ChevronDown, ChevronUp } from 'lucide-react';

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

const getProficiencyGradient = (code: string) => {
  const gradients: Record<string, string> = {
    CU: 'from-slate-400 to-slate-600',
    AP: 'from-blue-400 to-blue-600',
    AS: 'from-green-400 to-green-600',
    EV: 'from-orange-400 to-orange-600',
    CR: 'from-purple-400 to-purple-600',
  };
  return gradients[code] || 'from-gray-400 to-gray-600';
};

const formatSkillName = (skill: string) => {
  return skill
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

export default function AnalyticsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProficiency, setSelectedProficiency] = useState<string>('all');
  const [selectedSkill, setSelectedSkill] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'avgLevel'>('name');
  const [expandedCompany, setExpandedCompany] = useState<string | null>(null);

  const skillData = useMemo(() => {
    const data = getCompanySkillLevels();
    
    // Calculate company averages
    const companiesWithAvg = data.companies.map(company => {
      const levels = Object.values(company.skills).map(s => s.level);
      const avgLevel = levels.reduce((sum, l) => sum + l, 0) / levels.length;
      const proficiencyCounts: Record<string, number> = {};
      
      Object.values(company.skills).forEach(skill => {
        proficiencyCounts[skill.proficiency_code] = (proficiencyCounts[skill.proficiency_code] || 0) + 1;
      });
      
      return {
        ...company,
        avgLevel,
        proficiencyCounts,
      };
    });

    // Calculate skill statistics
    const skillStats: Record<string, { 
      avgLevel: number; 
      companies: number; 
      proficiencyDist: Record<string, number>;
    }> = {};
    
    data.metadata.skill_categories.forEach(skillName => {
      const levels: number[] = [];
      const profDist: Record<string, number> = {};
      
      data.companies.forEach(company => {
        const skill = company.skills[skillName];
        if (skill) {
          levels.push(skill.level);
          profDist[skill.proficiency_code] = (profDist[skill.proficiency_code] || 0) + 1;
        }
      });
      
      skillStats[skillName] = {
        avgLevel: levels.reduce((sum, l) => sum + l, 0) / levels.length,
        companies: levels.length,
        proficiencyDist: profDist,
      };
    });

    return {
      metadata: data.metadata,
      proficiencyLevels: data.proficiency_levels,
      companies: companiesWithAvg,
      skillStats,
    };
  }, []);

  // Filtering and sorting
  const filteredCompanies = useMemo(() => {
    let filtered = skillData.companies;

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(c => 
        c.company.toLowerCase().includes(query)
      );
    }

    // Proficiency filter
    if (selectedProficiency !== 'all') {
      filtered = filtered.filter(c => 
        Object.values(c.skills).some(skill => skill.proficiency_code === selectedProficiency)
      );
    }

    // Skill filter
    if (selectedSkill !== 'all') {
      filtered = filtered.filter(c => c.skills[selectedSkill]);
    }

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'name') {
        return a.company.localeCompare(b.company);
      } else {
        return b.avgLevel - a.avgLevel;
      }
    });

    return filtered;
  }, [skillData.companies, searchQuery, selectedProficiency, selectedSkill, sortBy]);

  return (
    <Layout>
      <div className="space-y-6 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Skill Set Analytics Dashboard</h1>
          <p className="text-slate-600">Comprehensive analysis of company skill requirements and proficiency levels</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-4 shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="h-5 w-5 opacity-80" />
              <p className="text-xs font-medium opacity-90">Companies</p>
            </div>
            <p className="text-3xl font-bold">{skillData.metadata.total_companies}</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl p-4 shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <Award className="h-5 w-5 opacity-80" />
              <p className="text-xs font-medium opacity-90">Skill Categories</p>
            </div>
            <p className="text-3xl font-bold">{skillData.metadata.skill_categories.length}</p>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-4 shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="h-5 w-5 opacity-80" />
              <p className="text-xs font-medium opacity-90">Data Points</p>
            </div>
            <p className="text-3xl font-bold">
              {(skillData.metadata.total_companies * skillData.metadata.skill_categories.length).toLocaleString()}
            </p>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-xl p-4 shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-5 w-5 opacity-80" />
              <p className="text-xs font-medium opacity-90">Proficiency Levels</p>
            </div>
            <p className="text-3xl font-bold">{skillData.proficiencyLevels.length}</p>
          </div>
        </div>

        {/* Proficiency Legend */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Proficiency Levels Reference</h3>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            {skillData.proficiencyLevels.map((level) => {
              const colors = getProficiencyColor(level.code);
              return (
                <div
                  key={level.code}
                  className={`${colors.bg} ${colors.text} border ${colors.border} rounded-lg p-3`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-lg">{level.code}</span>
                    <span className="text-xs font-semibold">{level.name}</span>
                  </div>
                  <p className="text-xs opacity-90">{level.description}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search companies..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
              />
            </div>

            {/* Proficiency Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-500" />
              <select
                value={selectedProficiency}
                onChange={(e) => setSelectedProficiency(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
              >
                <option value="all">All Proficiency Levels</option>
                {skillData.proficiencyLevels.map((level) => (
                  <option key={level.code} value={level.code}>
                    {level.code} - {level.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Skill Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-500" />
              <select
                value={selectedSkill}
                onChange={(e) => setSelectedSkill(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
              >
                <option value="all">All Skills</option>
                {skillData.metadata.skill_categories.map((skill) => (
                  <option key={skill} value={skill}>
                    {formatSkillName(skill)}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort */}
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'name' | 'avgLevel')}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
              >
                <option value="name">Sort by Name</option>
                <option value="avgLevel">Sort by Avg Level</option>
              </select>
            </div>
          </div>

          <div className="mt-3 text-sm text-slate-600">
            Showing <span className="font-bold text-slate-900">{filteredCompanies.length}</span> of{' '}
            <span className="font-bold text-slate-900">{skillData.companies.length}</span> companies
          </div>
        </div>

        {/* Companies List */}
        <div className="space-y-4">
          {filteredCompanies.map((company) => {
            const isExpanded = expandedCompany === company.company;
            const colors = getProficiencyColor(
              Object.values(company.skills).sort((a, b) => b.level - a.level)[0].proficiency_code
            );

            return (
              <div key={company.company} className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                {/* Company Header */}
                <div
                  className="p-5 cursor-pointer"
                  onClick={() => setExpandedCompany(isExpanded ? null : company.company)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-bold text-slate-900">{company.company}</h3>
                        <span className={`${colors.bg} ${colors.text} border ${colors.border} px-2 py-1 rounded text-xs font-bold`}>
                          Avg: {company.avgLevel.toFixed(1)}
                        </span>
                      </div>

                      {/* Proficiency Distribution Badges */}
                      <div className="flex flex-wrap gap-2 mb-3">
                        {Object.entries(company.proficiencyCounts)
                          .sort((a, b) => b[1] - a[1])
                          .map(([code, count]) => {
                            const profColors = getProficiencyColor(code);
                            return (
                              <span
                                key={code}
                                className={`${profColors.bg} ${profColors.text} border ${profColors.border} px-2 py-1 rounded-md text-xs font-medium`}
                              >
                                {code}: {count} skills
                              </span>
                            );
                          })}
                      </div>

                      {/* Avg Level Progress Bar */}
                      <div className="relative h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className={`absolute left-0 top-0 h-full bg-gradient-to-r ${getProficiencyGradient(
                            Object.values(company.skills).sort((a, b) => b.level - a.level)[0].proficiency_code
                          )}`}
                          style={{ width: `${(company.avgLevel / 10) * 100}%` }}
                        />
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

                {/* Expanded Skills Details */}
                {isExpanded && (
                  <div className="border-t border-slate-200 p-5 bg-slate-50">
                    <h4 className="text-sm font-bold text-slate-900 mb-4 uppercase tracking-wide">Skill Requirements</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {Object.entries(company.skills)
                        .sort((a, b) => b[1].level - a[1].level)
                        .map(([skillName, skillData]) => {
                          const skillColors = getProficiencyColor(skillData.proficiency_code);
                          return (
                            <div
                              key={skillName}
                              className="bg-white rounded-lg border border-slate-200 p-4 hover:shadow-md transition-shadow"
                            >
                              <div className="flex items-start justify-between mb-3">
                                <h5 className="text-sm font-semibold text-slate-900 flex-1">
                                  {formatSkillName(skillName)}
                                </h5>
                                <span
                                  className={`${skillColors.bg} ${skillColors.text} border ${skillColors.border} px-2 py-1 rounded text-xs font-bold ml-2`}
                                >
                                  {skillData.proficiency_code}
                                </span>
                              </div>

                              {/* Level Display */}
                              <div className="mb-3">
                                <div className="flex items-center justify-between mb-1">
                                  <span className="text-xs text-slate-600">Level</span>
                                  <span className="text-lg font-bold text-slate-900">{skillData.level}/10</span>
                                </div>
                                <div className="relative h-2 bg-slate-100 rounded-full overflow-hidden">
                                  <div
                                    className={`absolute left-0 top-0 h-full bg-gradient-to-r ${getProficiencyGradient(
                                      skillData.proficiency_code
                                    )}`}
                                    style={{ width: `${(skillData.level / 10) * 100}%` }}
                                  />
                                </div>
                              </div>

                              {/* Proficiency Info */}
                              <div className="text-xs text-slate-600">
                                <p className="font-medium mb-1">{skillData.proficiency_name}</p>
                                <p className="text-xs opacity-75">{skillData.proficiency_description}</p>
                              </div>
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
            <p className="text-slate-500 text-lg">No companies found matching your filters.</p>
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedProficiency('all');
                setSelectedSkill('all');
              }}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
