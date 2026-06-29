'use client';

import React, { useMemo, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Search, Tags, Pencil, Save, X, ChevronDown } from 'lucide-react';
import { AdminGuard } from '@/components/AdminGuard';
import { AdminLayout } from '@/components/AdminLayout';
import { Input } from '@/components/UI';
import { skillTags, studentProficiencyLevels } from '@/utils/adminData';
import { getHiringRoundsData } from '@/utils/data';

type LocalSkillTag = (typeof skillTags)[number] & { localId: string };

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

const getImportanceColor = (importance: string) => {
  switch (importance) {
    case 'High':
      return { bg: 'bg-red-100', text: 'text-red-700' };
    case 'Medium':
      return { bg: 'bg-amber-100', text: 'text-amber-700' };
    case 'Low':
      return { bg: 'bg-green-100', text: 'text-green-700' };
    default:
      return { bg: 'bg-slate-100', text: 'text-slate-700' };
  }
};

const normalizeSkillKey = (value: string) => value.toLowerCase().replace(/_/g, ' ').replace(/\s+/g, ' ').trim();

export default function AdminSkillsIntelligencePage() {
  const searchParams = useSearchParams();
  const companyFilterFromRoute = searchParams.get('company') || '';
  const [query, setQuery] = useState(companyFilterFromRoute);
  const [importanceFilter, setImportanceFilter] = useState('all');
  const [skillData, setSkillData] = useState<LocalSkillTag[]>(() =>
    skillTags.map((item, index) => ({ ...item, localId: `skill-${index}` }))
  );
  const [editingCompany, setEditingCompany] = useState<string | null>(null);
  const [companyDraft, setCompanyDraft] = useState<Record<string, LocalSkillTag[]>>({});
  const [expandedCompanies, setExpandedCompanies] = useState<Record<string, boolean>>(
    companyFilterFromRoute ? { [companyFilterFromRoute]: true } : {}
  );

  const filteredSkills = useMemo(() => {
    return skillData.filter((item) => {
      const queryMatch =
        item.skill.toLowerCase().includes(query.toLowerCase()) ||
        item.role.toLowerCase().includes(query.toLowerCase()) ||
        item.company.toLowerCase().includes(query.toLowerCase());

      const importanceMatch = importanceFilter === 'all' || item.importance === importanceFilter;
      return queryMatch && importanceMatch;
    });
  }, [query, importanceFilter, skillData]);

  const skillsByCompany = useMemo(() => {
    return filteredSkills.reduce<Record<string, typeof filteredSkills>>((groups, item) => {
      if (!groups[item.company]) {
        groups[item.company] = [];
      }
      groups[item.company].push(item);
      return groups;
    }, {});
  }, [filteredSkills]);

  const proficiencyMetaByCode = useMemo(() => {
    return studentProficiencyLevels.reduce<Record<string, { name: string; description: string }>>((acc, level) => {
      acc[level.code] = { name: level.name, description: level.description };
      return acc;
    }, {});
  }, []);

  const companySkillMentions = useMemo(() => {
    return Object.keys(skillsByCompany).reduce<
      Record<string, Record<string, { count: number; examples: string[]; roles: Set<string> }>>
    >((companyAcc, companyName) => {
      const hiringData = getHiringRoundsData(companyName);
      const mentionsBySkill: Record<string, { count: number; examples: string[]; roles: Set<string> }> = {};

      if (hiringData?.job_role_details) {
        hiringData.job_role_details.forEach((role) => {
          role.hiring_rounds?.forEach((round) => {
            round.skill_sets?.forEach((skill) => {
              const skillName = normalizeSkillKey(skill.skill_set_code || '');
              if (!skillName) return;

              if (!mentionsBySkill[skillName]) {
                mentionsBySkill[skillName] = { count: 0, examples: [], roles: new Set<string>() };
              }

              mentionsBySkill[skillName].count += 1;
              if (role.role_title) {
                mentionsBySkill[skillName].roles.add(role.role_title);
              }
              if (skill.typical_questions && mentionsBySkill[skillName].examples.length < 2) {
                mentionsBySkill[skillName].examples.push(skill.typical_questions);
              }
            });
          });
        });
      }

      companyAcc[companyName] = mentionsBySkill;
      return companyAcc;
    }, {});
  }, [skillsByCompany]);

  const importanceOptions = ['all', 'High', 'Medium', 'Low'];
  const proficiencyOptions = ['CU', 'AP', 'AS', 'EV', 'CR'];

  const startCompanyEdit = (companyName: string, companySkills: LocalSkillTag[]) => {
    setEditingCompany(companyName);
    setCompanyDraft((prev) => ({
      ...prev,
      [companyName]: companySkills.map((item) => ({ ...item })),
    }));
  };

  const cancelCompanyEdit = (companyName: string) => {
    setEditingCompany((prev) => (prev === companyName ? null : prev));
    setCompanyDraft((prev) => {
      const next = { ...prev };
      delete next[companyName];
      return next;
    });
  };

  const saveCompanyEdit = (companyName: string) => {
    const draft = companyDraft[companyName] || [];
    if (!draft.length) {
      cancelCompanyEdit(companyName);
      return;
    }

    const draftById = new Map(draft.map((item) => [item.localId, item]));
    setSkillData((prev) => prev.map((item) => draftById.get(item.localId) || item));
    cancelCompanyEdit(companyName);
  };

  const updateCompanyDraftField = (
    companyName: string,
    localId: string,
    field: keyof Omit<LocalSkillTag, 'localId' | 'company'>,
    value: string | number
  ) => {
    setCompanyDraft((prev) => {
      const companyItems = prev[companyName] || [];
      return {
        ...prev,
        [companyName]: companyItems.map((item) => {
          if (item.localId !== localId) return item;
          return {
            ...item,
            [field]: field === 'level' ? Number(value) || 0 : value,
          } as LocalSkillTag;
        }),
      };
    });
  };

  const toggleCompanyExpansion = (companyName: string) => {
    setExpandedCompanies((prev) => ({
      ...prev,
      [companyName]: !prev[companyName],
    }));
  };

  return (
    <AdminGuard>
      <AdminLayout>
        <div className="space-y-6 sm:space-y-8 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          <div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Skill Intelligence Management</h1>
            <p className="text-sm sm:text-base text-slate-600">Map role-wise skill requirements and define importance levels for better preparation guidance.</p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 lg:p-6 space-y-4">
            {companyFilterFromRoute && (
              <div className="text-xs sm:text-sm text-blue-700 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
                Company filter active: <span className="font-semibold">{companyFilterFromRoute}</span>
              </div>
            )}

            <Input
              icon={<Search className="h-4 w-4" />}
              type="text"
              placeholder="Search by skill, role, or company..."
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />

            <div className="flex flex-wrap gap-2">
              {importanceOptions.map((option) => (
                <button
                  key={option}
                  onClick={() => setImportanceFilter(option)}
                  className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                    importanceFilter === option ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-800 hover:bg-slate-300'
                  }`}
                >
                  {option === 'all' ? 'All Importance Levels' : option}
                </button>
              ))}
            </div>
          </div>

          {filteredSkills.length > 0 ? (
            <div className="space-y-4 sm:space-y-6">
              {Object.entries(skillsByCompany)
                .sort(([companyA], [companyB]) => companyA.localeCompare(companyB))
                .map(([companyName, companySkills]) => {
                  const isEditing = editingCompany === companyName;
                  const isExpanded = isEditing || !!expandedCompanies[companyName];
                  const visibleSkills = isEditing ? companyDraft[companyName] || companySkills : companySkills;

                  return (
                  <div key={companyName} className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                    <div
                      onClick={() => toggleCompanyExpansion(companyName)}
                      className="bg-gradient-to-r from-blue-50 to-blue-100 border-b border-blue-200 p-4 sm:p-5 cursor-pointer"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <h2 className="text-lg sm:text-xl font-bold text-slate-900 break-words">{companyName}</h2>
                        <div className="flex items-center gap-2">
                          <span className="text-xs sm:text-sm px-2.5 py-1 rounded-full bg-white text-slate-700 font-medium border border-slate-200">
                            {companySkills.length} skill mappings
                          </span>
                          {isEditing ? (
                            <>
                              <button
                                onClick={(event) => { event.stopPropagation(); saveCompanyEdit(companyName); }}
                                className="px-2.5 py-1.5 rounded-lg bg-green-600 text-white text-xs font-medium hover:bg-green-700 inline-flex items-center gap-1.5"
                              >
                                <Save className="h-3.5 w-3.5" />
                                Save
                              </button>
                              <button
                                onClick={(event) => { event.stopPropagation(); cancelCompanyEdit(companyName); }}
                                className="px-2.5 py-1.5 rounded-lg bg-slate-200 text-slate-700 text-xs font-medium hover:bg-slate-300 inline-flex items-center gap-1.5"
                              >
                                <X className="h-3.5 w-3.5" />
                                Cancel
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={(event) => { event.stopPropagation(); startCompanyEdit(companyName, companySkills); }}
                              className="p-1.5 rounded-md bg-blue-600 text-white hover:bg-blue-700 inline-flex items-center justify-center"
                              title="Edit Company Skills"
                              aria-label="Edit Company Skills"
                            >
                              <Pencil className="h-4 w-4" />
                            </button>
                          )}
                          <span
                            className={`text-slate-600 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                            aria-hidden="true"
                          >
                            <ChevronDown className="h-4 w-4" />
                          </span>
                        </div>
                      </div>
                    </div>

                    {isExpanded && <div className="p-4 sm:p-5">
                      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                        {visibleSkills.map((item, index) => {
                          const colors = getProficiencyColor(item.proficiencyCode);
                          const importanceColors = getImportanceColor(item.importance);
                          const proficiencyMeta = proficiencyMetaByCode[item.proficiencyCode];
                          const mentions = companySkillMentions[companyName]?.[normalizeSkillKey(item.skill)];

                          return (
                            <div
                              key={`${companyName}-${item.role}-${item.skill}-${index}`}
                              className="bg-slate-50 rounded-lg border border-slate-200 p-4 hover:shadow-md transition-shadow"
                            >
                              <div className="space-y-3">
                                <div>
                                  {isEditing ? (
                                    <div className="space-y-2">
                                      <input
                                        value={item.role}
                                        onChange={(event) => updateCompanyDraftField(companyName, item.localId, 'role', event.target.value)}
                                        className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-xs"
                                        placeholder="Role"
                                      />
                                      <input
                                        value={item.skill}
                                        onChange={(event) => updateCompanyDraftField(companyName, item.localId, 'skill', event.target.value)}
                                        className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm font-semibold"
                                        placeholder="Skill"
                                      />
                                    </div>
                                  ) : (
                                    <>
                                      <p className="text-xs text-slate-600 font-medium mb-1">{item.role}</p>
                                      <h3 className="text-base font-semibold text-slate-900">{item.skill}</h3>
                                    </>
                                  )}
                                </div>

                                <div className="space-y-2">
                                  <div className="flex items-center justify-between">
                                    <span className="text-xs text-slate-600 font-medium">Proficiency</span>
                                    {isEditing ? (
                                      <select
                                        value={item.proficiencyCode}
                                        onChange={(event) => updateCompanyDraftField(companyName, item.localId, 'proficiencyCode', event.target.value)}
                                        className="rounded-lg border border-slate-300 px-2 py-1 text-xs"
                                      >
                                        {proficiencyOptions.map((option) => (
                                          <option key={option} value={option}>{option}</option>
                                        ))}
                                      </select>
                                    ) : (
                                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
                                        {item.proficiencyCode}
                                      </span>
                                    )}
                                  </div>

                                  <div className="flex items-center justify-between">
                                    <span className="text-xs text-slate-600 font-medium">Level</span>
                                    {isEditing ? (
                                      <input
                                        type="number"
                                        min={0}
                                        max={10}
                                        value={item.level}
                                        onChange={(event) => updateCompanyDraftField(companyName, item.localId, 'level', event.target.value)}
                                        className="w-16 rounded-lg border border-slate-300 px-2 py-1 text-xs text-right"
                                      />
                                    ) : (
                                      <span className="text-sm font-semibold text-slate-900">{item.level}/10</span>
                                    )}
                                  </div>

                                  {!isEditing && (
                                    <div className="space-y-1">
                                      <div className="relative h-2 bg-slate-200 rounded-full overflow-hidden">
                                        <div
                                          className="absolute left-0 top-0 h-full bg-gradient-to-r from-blue-400 to-blue-600"
                                          style={{ width: `${Math.max(0, Math.min(10, item.level)) * 10}%` }}
                                        />
                                      </div>
                                      {proficiencyMeta && (
                                        <>
                                          <p className="text-xs font-medium text-slate-700">{proficiencyMeta.name}</p>
                                          <p className="text-xs text-slate-600 line-clamp-2">{proficiencyMeta.description}</p>
                                        </>
                                      )}
                                    </div>
                                  )}

                                  <div className="flex items-center justify-between">
                                    <span className="text-xs text-slate-600 font-medium">Importance</span>
                                    {isEditing ? (
                                      <select
                                        value={item.importance}
                                        onChange={(event) => updateCompanyDraftField(companyName, item.localId, 'importance', event.target.value)}
                                        className="rounded-lg border border-slate-300 px-2 py-1 text-xs"
                                      >
                                        <option value="High">High</option>
                                        <option value="Medium">Medium</option>
                                        <option value="Low">Low</option>
                                      </select>
                                    ) : (
                                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${importanceColors.bg} ${importanceColors.text}`}>
                                        {item.importance}
                                      </span>
                                    )}
                                  </div>

                                  {!isEditing && mentions && (
                                    <div className="pt-2 border-t border-slate-200">
                                      <p className="text-xs font-medium text-blue-700">Tested in {mentions.count} rounds</p>
                                      {mentions.examples.length > 0 && (
                                        <p className="text-xs text-slate-600 italic line-clamp-2">&quot;{mentions.examples[0]}&quot;</p>
                                      )}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>}
                  </div>
                );
                })}
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center">
              <p className="text-slate-600 text-sm">No skills found matching your search criteria.</p>
            </div>
          )}

          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <h2 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
              <Tags className="h-4 w-4" />
              Bloom Proficiency Reference
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
              {studentProficiencyLevels.map((level) => {
                const colors = getProficiencyColor(level.code);
                return (
                  <div
                    key={level.code}
                    className={`px-3 py-2 rounded-lg text-xs font-medium ${colors.bg} ${colors.text} text-center`}
                  >
                    <div className="font-bold">{level.code}</div>
                    <div className="text-xs">{level.name}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </AdminLayout>
    </AdminGuard>
  );
}
