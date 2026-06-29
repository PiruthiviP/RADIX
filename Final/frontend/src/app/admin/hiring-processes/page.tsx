'use client';

import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { ArrowUpDown, Edit2, Lightbulb, Trash2 } from 'lucide-react';
import { AdminGuard } from '@/components/AdminGuard';
import { AdminLayout } from '@/components/AdminLayout';
import { getCompaniesShort, getRenderableLogoUrl } from '@/utils/data';
import hiringRoundsMaster from '@/data/Hiring_rounds.json';
import { Chip } from '@/components/UI';

interface SkillSet {
  skill_set_code: string;
  typical_questions?: string;
}

interface HiringRoundItem {
  round_number: number;
  round_name: string;
  round_category: string;
  assessment_mode: string;
  skill_sets?: SkillSet[];
}

interface JobRoleDetail {
  opportunity_type: string;
  role_title: string;
  role_category: string;
  job_description: string;
  compensation: string;
  ctc_or_stipend: number;
  bonus?: string;
  benefits_summary?: string;
  hiring_rounds?: HiringRoundItem[];
}

interface CompanyHiringProcess {
  company_name: string;
  job_role_details: JobRoleDetail[];
}

interface RoleEditorState {
  companyIndex: number;
  roleIndex: number;
  draft: JobRoleDetail;
}

const ADMIN_HIRING_PROCESS_STORAGE_KEY = 'adminHiringProcessMasterData';
const isDefined = <T,>(value: T | null): value is T => value !== null;

const normalizeProcessData = (input: unknown): CompanyHiringProcess[] => {
  if (!Array.isArray(input)) return [];

  return input
    .map((company): CompanyHiringProcess | null => {
      if (!company || typeof company !== 'object') return null;
      const companyRecord = company as Record<string, unknown>;
      const companyName = typeof companyRecord.company_name === 'string' ? companyRecord.company_name : 'Unknown Company';

      const rolesRaw = Array.isArray(companyRecord.job_role_details) ? companyRecord.job_role_details : [];
      const roles = rolesRaw
        .map((role): JobRoleDetail | null => {
          if (!role || typeof role !== 'object') return null;
          const roleRecord = role as Record<string, unknown>;
          const roundsRaw = Array.isArray(roleRecord.hiring_rounds) ? roleRecord.hiring_rounds : [];

          const rounds = roundsRaw
            .map((round, roundIndex): HiringRoundItem | null => {
              if (!round || typeof round !== 'object') return null;
              const roundRecord = round as Record<string, unknown>;
              const skillsRaw = Array.isArray(roundRecord.skill_sets) ? roundRecord.skill_sets : [];

              const skillSets = skillsRaw
                .map((skill): SkillSet | null => {
                  if (!skill || typeof skill !== 'object') return null;
                  const skillRecord = skill as Record<string, unknown>;
                  const code = typeof skillRecord.skill_set_code === 'string' ? skillRecord.skill_set_code : '';
                  if (!code) return null;

                  const typicalQuestions =
                    typeof skillRecord.typical_questions === 'string' ? skillRecord.typical_questions : undefined;

                  return typicalQuestions
                    ? { skill_set_code: code, typical_questions: typicalQuestions }
                    : { skill_set_code: code };
                })
                .filter(isDefined);

              return {
                round_number:
                  typeof roundRecord.round_number === 'number'
                    ? roundRecord.round_number
                    : roundIndex + 1,
                round_name:
                  typeof roundRecord.round_name === 'string'
                    ? roundRecord.round_name
                    : 'Untitled Round',
                round_category:
                  typeof roundRecord.round_category === 'string'
                    ? roundRecord.round_category
                    : 'General',
                assessment_mode:
                  typeof roundRecord.assessment_mode === 'string'
                    ? roundRecord.assessment_mode
                    : 'Online',
                skill_sets: skillSets,
              };
            })
            .filter(isDefined);

          return {
            opportunity_type:
              typeof roleRecord.opportunity_type === 'string'
                ? roleRecord.opportunity_type
                : 'Employment',
            role_title:
              typeof roleRecord.role_title === 'string' ? roleRecord.role_title : 'Untitled Role',
            role_category:
              typeof roleRecord.role_category === 'string' ? roleRecord.role_category : 'General',
            job_description:
              typeof roleRecord.job_description === 'string'
                ? roleRecord.job_description
                : 'Role details and expectations',
            compensation:
              typeof roleRecord.compensation === 'string' ? roleRecord.compensation : 'CTC',
            ctc_or_stipend:
              typeof roleRecord.ctc_or_stipend === 'number' ? roleRecord.ctc_or_stipend : 0,
            bonus: typeof roleRecord.bonus === 'string' ? roleRecord.bonus : undefined,
            benefits_summary:
              typeof roleRecord.benefits_summary === 'string'
                ? roleRecord.benefits_summary
                : undefined,
            hiring_rounds: rounds,
          };
        })
        .filter(isDefined);

      return {
        company_name: companyName,
        job_role_details: roles,
      };
    })
    .filter((company): company is CompanyHiringProcess => company !== null);
};

export default function AdminHiringProcessesPage() {
  const searchParams = useSearchParams();
  const companyFilterFromRoute = searchParams.get('company') || '';
  const [companySearch, setCompanySearch] = useState(companyFilterFromRoute);
  const [processData, setProcessData] = useState<CompanyHiringProcess[]>(() => {
    const defaultData = normalizeProcessData(hiringRoundsMaster);
    if (typeof window === 'undefined') return defaultData;

    try {
      const stored = localStorage.getItem(ADMIN_HIRING_PROCESS_STORAGE_KEY);
      if (!stored) return defaultData;
      const parsed = normalizeProcessData(JSON.parse(stored));
      return parsed.length > 0 ? parsed : defaultData;
    } catch {
      return defaultData;
    }
  });
  const [roleEditor, setRoleEditor] = useState<RoleEditorState | null>(null);
  const [expandedRoleCard, setExpandedRoleCard] = useState<{ companyIndex: number; roleIndex: number } | null>(null);
  const allCompanies = getCompaniesShort();
  const companyNames = allCompanies.map((company) => company.name);
  const companyLogoMap = Object.fromEntries(
    allCompanies.map((c) => [c.name.toLowerCase().trim(), getRenderableLogoUrl(c.logo_url, c.website_url ?? c.website)])
  );

  const toggleRoleCardExpansion = (companyIndex: number, roleIndex: number) => {
    setExpandedRoleCard((prev) => {
      if (prev?.companyIndex === companyIndex && prev?.roleIndex === roleIndex) {
        return null;
      }
      return { companyIndex, roleIndex };
    });
  };

  const addDefaultRole = (companyIndex: number) => {
    setProcessData((prev) =>
      prev.map((company, index) => {
        if (index !== companyIndex) return company;
        const nextRole: JobRoleDetail = {
          role_title: 'New Role',
          role_category: 'SDE',
          opportunity_type: 'Employment',
          job_description: 'Role details and expectations',
          compensation: 'CTC',
          ctc_or_stipend: 600000,
          bonus: undefined,
          benefits_summary: 'Standard company benefits',
          hiring_rounds: [],
        };

        return {
          ...company,
          job_role_details: [...company.job_role_details, nextRole],
        };
      })
    );
  };

  const openRoleEditor = (companyIndex: number, roleIndex: number) => {
    const role = processData[companyIndex]?.job_role_details[roleIndex];
    if (!role) return;

    setRoleEditor({
      companyIndex,
      roleIndex,
      draft: {
        ...role,
        hiring_rounds: [...(role.hiring_rounds || [])],
      },
    });
  };

  const closeRoleEditor = () => {
    setRoleEditor(null);
  };

  const updateRoleDraftField = <K extends keyof JobRoleDetail>(field: K, value: JobRoleDetail[K]) => {
    setRoleEditor((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        draft: {
          ...prev.draft,
          [field]: value,
        },
      };
    });
  };

  const updateDraftRoundField = (roundIndex: number, field: keyof HiringRoundItem, value: string | number) => {
    setRoleEditor((prev) => {
      if (!prev) return prev;
      const rounds = [...(prev.draft.hiring_rounds || [])];
      const targetRound = rounds[roundIndex];
      if (!targetRound) return prev;

      rounds[roundIndex] = {
        ...targetRound,
        [field]: value,
      };

      return {
        ...prev,
        draft: {
          ...prev.draft,
          hiring_rounds: rounds,
        },
      };
    });
  };

  const updateDraftRoundSkills = (roundIndex: number, csvValue: string) => {
    setRoleEditor((prev) => {
      if (!prev) return prev;
      const rounds = [...(prev.draft.hiring_rounds || [])];
      const targetRound = rounds[roundIndex];
      if (!targetRound) return prev;

      rounds[roundIndex] = {
        ...targetRound,
        skill_sets: csvValue
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean)
          .map((code) => ({ skill_set_code: code })),
      };

      return {
        ...prev,
        draft: {
          ...prev.draft,
          hiring_rounds: rounds,
        },
      };
    });
  };

  const addDraftRound = () => {
    setRoleEditor((prev) => {
      if (!prev) return prev;
      const rounds = [...(prev.draft.hiring_rounds || [])];
      rounds.push({
        round_number: rounds.length + 1,
        round_name: '',
        round_category: '',
        assessment_mode: '',
        skill_sets: [],
      });
      return {
        ...prev,
        draft: {
          ...prev.draft,
          hiring_rounds: rounds,
        },
      };
    });
  };

  const removeDraftRound = (roundIndex: number) => {
    setRoleEditor((prev) => {
      if (!prev) return prev;
      const rounds = (prev.draft.hiring_rounds || [])
        .filter((_, index) => index !== roundIndex)
        .map((round, index) => ({ ...round, round_number: index + 1 }));
      return {
        ...prev,
        draft: {
          ...prev.draft,
          hiring_rounds: rounds,
        },
      };
    });
  };

  const saveRoleEditor = () => {
    setProcessData((prev) => {
      if (!roleEditor) return prev;

      return prev.map((company, cIndex) => {
        if (cIndex !== roleEditor.companyIndex) return company;
        const nextRoles = company.job_role_details.map((role, rIndex) => {
          if (rIndex !== roleEditor.roleIndex) return role;
          return {
            ...roleEditor.draft,
            role_title: roleEditor.draft.role_title.trim() || 'Untitled Role',
            role_category: roleEditor.draft.role_category.trim() || 'General',
            opportunity_type: roleEditor.draft.opportunity_type.trim() || 'Employment',
            job_description: roleEditor.draft.job_description.trim() || 'Role details and expectations',
            compensation: roleEditor.draft.compensation.trim() || 'CTC',
            ctc_or_stipend: Number(roleEditor.draft.ctc_or_stipend) || 0,
            hiring_rounds: (roleEditor.draft.hiring_rounds || []).map((round, index) => ({
              ...round,
              round_number: index + 1,
              round_name: round.round_name?.trim() || `Round ${index + 1}`,
              round_category: round.round_category?.trim() || 'General',
              assessment_mode: round.assessment_mode?.trim() || 'Online',
            })),
          };
        });
        return { ...company, job_role_details: nextRoles };
      });
    });

    closeRoleEditor();
  };

  const handleDeleteRole = (companyIndex: number, roleIndex: number) => {
    const role = processData[companyIndex]?.job_role_details[roleIndex];
    if (!role) return;
    if (!confirm(`Delete role ${role.role_title}?`)) return;

    setProcessData((prev) =>
      prev.map((company, index) => {
        if (index !== companyIndex) return company;
        return { ...company, job_role_details: company.job_role_details.filter((_, rIndex) => rIndex !== roleIndex) };
      })
    );
  };

  const normalizeRoundOrder = (companyIndex: number, roleIndex: number) => {
    setProcessData((prev) =>
      prev.map((company, cIndex) => {
        if (cIndex !== companyIndex) return company;
        const nextRoles = company.job_role_details.map((role, rIndex) => {
          if (rIndex !== roleIndex) return role;
          const normalized = (role.hiring_rounds || []).map((round, index) => ({ ...round, round_number: index + 1 }));
          return { ...role, hiring_rounds: normalized };
        });
        return { ...company, job_role_details: nextRoles };
      })
    );
  };

  useEffect(() => {
    try {
      localStorage.setItem(ADMIN_HIRING_PROCESS_STORAGE_KEY, JSON.stringify(processData));
    } catch {
      // Ignore storage quota or serialization errors.
    }
  }, [processData]);

  const normalizedSearch = companySearch.toLowerCase().trim();

  const visibleProcessEntries = processData
    .map((company, companyIndex) => ({ company, companyIndex }))
    .filter(({ company }) => {
      const companyName = company.company_name.toLowerCase().trim();
      const routeMatch = !companyFilterFromRoute || companyName === companyFilterFromRoute.toLowerCase().trim();
      const searchMatch = !normalizedSearch || companyName.includes(normalizedSearch);
      return routeMatch && searchMatch;
    });

  return (
    <AdminGuard>
      <AdminLayout>
        <div className="space-y-6 sm:space-y-8 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Hiring Process Management</h1>
              <p className="text-sm sm:text-base text-slate-600">Student-style hiring process view with admin CRUD for company roles and interview rounds.</p>
            </div>
          </div>

          {companyFilterFromRoute && (
            <div className="text-xs sm:text-sm text-blue-700 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
              Company filter active: <span className="font-semibold">{companyFilterFromRoute}</span>
            </div>
          )}

          <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5">
            <label className="block text-xs sm:text-sm font-semibold text-slate-700 mb-2">Search Company</label>
            <input
              type="text"
              value={companySearch}
              onChange={(event) => setCompanySearch(event.target.value)}
              placeholder="Search companies in hiring process..."
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
            />
          </div>

          <div className="space-y-4 sm:space-y-6">
            {visibleProcessEntries.map(({ company, companyIndex }) => {
              return (
              <div key={`${company.company_name}-${companyIndex}`} className="bg-white border border-slate-200 rounded-xl overflow-hidden">
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 border-b border-blue-200 p-4 sm:p-5 lg:p-6">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      {companyLogoMap[company.company_name.toLowerCase().trim()] ? (
                        /* eslint-disable-next-line @next/next/no-img-element */
                        <img
                          src={companyLogoMap[company.company_name.toLowerCase().trim()]}
                          alt={`${company.company_name} logo`}
                          className="w-10 h-10 rounded-lg object-contain bg-white border border-slate-200 p-1 flex-shrink-0"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-white border border-slate-200 flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-bold text-slate-500">{company.company_name.charAt(0)}</span>
                        </div>
                      )}
                      <div>
                        <h2 className="text-xl sm:text-2xl font-bold text-slate-900 break-words">{company.company_name}</h2>
                        <p className="text-sm text-slate-700">{company.job_role_details?.length || 0} active hiring roles</p>
                      </div>
                    </div>
                    <button onClick={() => addDefaultRole(companyIndex)} className="px-3 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700">Add Process</button>
                  </div>
                </div>

                <div className="p-4 sm:p-5 lg:p-6 space-y-4 sm:space-y-6">
                  {(company.job_role_details || []).length > 0 ? (
                    (company.job_role_details || []).map((role, roleIndex) => (
                      <div key={`${company.company_name}-${companyIndex}-${role.role_title}-${roleIndex}`} className="bg-slate-50 border border-slate-200 rounded-xl overflow-hidden">
                        {/* Collapsed/Expanded Toggle */}
                        <div
                          onClick={() => toggleRoleCardExpansion(companyIndex, roleIndex)}
                          className="p-4 sm:p-5 bg-white border-b border-slate-200 cursor-pointer hover:bg-blue-50 transition-colors"
                        >
                          <div className="flex flex-wrap items-center justify-between gap-3">
                            <div className="space-y-1 min-w-0 flex-1">
                              <h3 className="text-lg sm:text-xl font-bold text-slate-900 break-words">{role.role_title}</h3>
                              <p className="text-sm text-slate-700 line-clamp-1">{role.job_description}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <button onClick={(e) => { e.stopPropagation(); openRoleEditor(companyIndex, roleIndex); }} className="p-1.5 rounded-md bg-slate-200 text-slate-700 hover:bg-slate-300 transition-colors" title="Edit Role">
                                <Edit2 className="h-4 w-4" />
                              </button>
                              <button onClick={(e) => { e.stopPropagation(); handleDeleteRole(companyIndex, roleIndex); }} className="p-1.5 rounded-md bg-red-100 text-red-700 hover:bg-red-200 transition-colors" title="Delete Role">
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        </div>

                        {/* Expanded Content */}
                        {expandedRoleCard?.companyIndex === companyIndex && expandedRoleCard?.roleIndex === roleIndex && (
                          <>
                            {roleEditor?.companyIndex === companyIndex && roleEditor?.roleIndex === roleIndex ? (
                          <div className="p-4 sm:p-5 space-y-4 bg-white border-b border-slate-200">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              <label className="text-xs font-semibold text-slate-700">
                                Role Title
                                <input
                                  value={roleEditor.draft.role_title}
                                  onChange={(event) => updateRoleDraftField('role_title', event.target.value)}
                                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                                />
                              </label>
                              <label className="text-xs font-semibold text-slate-700">
                                Role Category
                                <input
                                  value={roleEditor.draft.role_category}
                                  onChange={(event) => updateRoleDraftField('role_category', event.target.value)}
                                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                                />
                              </label>
                              <label className="text-xs font-semibold text-slate-700">
                                Opportunity Type
                                <input
                                  value={roleEditor.draft.opportunity_type}
                                  onChange={(event) => updateRoleDraftField('opportunity_type', event.target.value)}
                                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                                />
                              </label>
                              <label className="text-xs font-semibold text-slate-700">
                                Compensation Type
                                <input
                                  value={roleEditor.draft.compensation}
                                  onChange={(event) => updateRoleDraftField('compensation', event.target.value)}
                                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                                />
                              </label>
                              <label className="text-xs font-semibold text-slate-700 md:col-span-2">
                                Job Description
                                <textarea
                                  value={roleEditor.draft.job_description}
                                  onChange={(event) => updateRoleDraftField('job_description', event.target.value)}
                                  rows={3}
                                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                                />
                              </label>
                              <label className="text-xs font-semibold text-slate-700">
                                CTC / Stipend
                                <input
                                  type="number"
                                  value={String(roleEditor.draft.ctc_or_stipend ?? 0)}
                                  onChange={(event) => updateRoleDraftField('ctc_or_stipend', Number(event.target.value))}
                                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                                />
                              </label>
                              <label className="text-xs font-semibold text-slate-700">
                                Bonus
                                <input
                                  value={roleEditor.draft.bonus || ''}
                                  onChange={(event) => updateRoleDraftField('bonus', event.target.value)}
                                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                                />
                              </label>
                              <label className="text-xs font-semibold text-slate-700 md:col-span-2">
                                Benefits Summary
                                <textarea
                                  value={roleEditor.draft.benefits_summary || ''}
                                  onChange={(event) => updateRoleDraftField('benefits_summary', event.target.value)}
                                  rows={2}
                                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                                />
                              </label>
                            </div>

                            <div className="space-y-3">
                              <div className="flex items-center justify-between">
                                <h4 className="font-bold text-slate-900">Interview Rounds</h4>
                                <button
                                  onClick={addDraftRound}
                                  className="px-2.5 py-1.5 rounded-md bg-blue-100 text-blue-700 text-xs font-semibold hover:bg-blue-200"
                                >
                                  Add Round
                                </button>
                              </div>

                              {(roleEditor.draft.hiring_rounds || []).map((round, roundIndex) => (
                                <div key={`${round.round_name}-${roundIndex}`} className="grid grid-cols-1 md:grid-cols-2 gap-3 rounded-lg border border-slate-200 p-3 bg-slate-50">
                                  <label className="text-xs font-semibold text-slate-700">
                                    Round Name
                                    <input
                                      value={round.round_name}
                                      onChange={(event) => updateDraftRoundField(roundIndex, 'round_name', event.target.value)}
                                      className="mt-1 w-full rounded-md border border-slate-300 px-2.5 py-1.5 text-sm"
                                    />
                                  </label>
                                  <label className="text-xs font-semibold text-slate-700">
                                    Round Category
                                    <input
                                      value={round.round_category}
                                      onChange={(event) => updateDraftRoundField(roundIndex, 'round_category', event.target.value)}
                                      className="mt-1 w-full rounded-md border border-slate-300 px-2.5 py-1.5 text-sm"
                                    />
                                  </label>
                                  <label className="text-xs font-semibold text-slate-700">
                                    Assessment Mode
                                    <input
                                      value={round.assessment_mode}
                                      onChange={(event) => updateDraftRoundField(roundIndex, 'assessment_mode', event.target.value)}
                                      className="mt-1 w-full rounded-md border border-slate-300 px-2.5 py-1.5 text-sm"
                                    />
                                  </label>
                                  <label className="text-xs font-semibold text-slate-700">
                                    Skill Codes (comma separated)
                                    <input
                                      value={(round.skill_sets || []).map((item) => item.skill_set_code).join(', ')}
                                      onChange={(event) => updateDraftRoundSkills(roundIndex, event.target.value)}
                                      className="mt-1 w-full rounded-md border border-slate-300 px-2.5 py-1.5 text-sm"
                                    />
                                  </label>
                                  <div className="md:col-span-2 flex justify-end">
                                    <button
                                      onClick={() => removeDraftRound(roundIndex)}
                                      className="text-xs px-2 py-1 rounded-md bg-red-100 text-red-700 hover:bg-red-200 inline-flex items-center gap-1"
                                    >
                                      <Trash2 className="h-3.5 w-3.5" />
                                      Remove Round
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>

                            <div className="flex flex-wrap justify-end gap-2">
                              <button onClick={closeRoleEditor} className="px-3 py-2 rounded-lg border border-slate-300 text-sm font-medium text-slate-700 hover:bg-slate-100">Cancel</button>
                              <button onClick={saveRoleEditor} className="px-3 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700">Save Role</button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <div className="p-4 sm:p-5 border-b border-slate-200 bg-white">

                              <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                                <div className="bg-white rounded-lg border border-green-200 p-3">
                                  <p className="text-xs text-slate-600 font-semibold mb-1">Compensation ({role.compensation})</p>
                                  <p className="text-xl font-bold text-green-600">₹{Number(role.ctc_or_stipend || 0).toLocaleString()}</p>
                                </div>
                                <div className="bg-white rounded-lg border border-blue-200 p-3">
                                  <p className="text-xs text-slate-600 font-semibold mb-1">Role Category</p>
                                  <p className="text-base font-bold text-blue-700 break-words">{role.role_category}</p>
                                  <p className="text-xs text-slate-600">Opportunity: {role.opportunity_type}</p>
                                </div>
                                <div className="bg-white rounded-lg border border-purple-200 p-3 sm:col-span-2 lg:col-span-1">
                                  <p className="text-xs text-slate-600 font-semibold mb-1">Benefits</p>
                                  <p className="text-xs text-slate-700 break-words">{role.benefits_summary || 'Standard benefits package'}</p>
                                </div>
                              </div>
                            </div>

                            <div className="p-4 sm:p-5 space-y-3">
                              <div className="flex items-center justify-between">
                                <h4 className="font-bold text-slate-900 text-base sm:text-lg">Interview Rounds ({role.hiring_rounds?.length || 0})</h4>
                                <button onClick={() => normalizeRoundOrder(companyIndex, roleIndex)} className="text-xs px-2 py-1 rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 inline-flex items-center gap-1">
                                  <ArrowUpDown className="h-3.5 w-3.5" />
                                  Reorder
                                </button>
                              </div>

                              {(role.hiring_rounds || []).length > 0 ? (
                                (role.hiring_rounds || []).map((round, roundIndex) => (
                                  <div key={`${round.round_name}-${roundIndex}`} className="border border-slate-200 rounded-lg p-3 bg-white">
                                    <div className="flex items-start gap-3">
                                      <span className="font-bold text-white bg-blue-600 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 text-sm">{roundIndex + 1}</span>
                                      <div className="flex-1 space-y-2 min-w-0">
                                        <div>
                                          <p className="font-bold text-slate-900 text-base break-words">{round.round_name}</p>
                                          <p className="text-xs text-slate-600"><span className="font-semibold">{round.round_category}</span> • {round.assessment_mode}</p>
                                        </div>
                                        {!!round.skill_sets?.length && (
                                          <div className="flex flex-wrap gap-2">
                                            {round.skill_sets.map((skill, skillIndex) => (
                                              <Chip key={`${skill.skill_set_code}-${skillIndex}`} label={skill.skill_set_code} variant="secondary" />
                                            ))}
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                ))
                              ) : (
                                <p className="text-sm text-slate-500">No rounds defined yet. Use Edit Role to add rounds.</p>
                              )}
                            </div>
                          </>
                        )}

                            <div className="px-4 sm:px-5 pb-4 sm:pb-5">
                            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                              <p className="text-xs font-semibold text-green-900 mb-1 flex items-center gap-2">
                                <Lightbulb className="h-4 w-4" />
                                Preparation Hint
                              </p>
                              <p className="text-xs text-green-800">Align each round with concrete skill checks and keep ordering consistent with candidate journey.</p>
                            </div>
                          </div>
                          </>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-sm text-slate-600">
                      No roles added yet. Use Add Role to create hiring process details for this company.
                    </div>
                  )}
                </div>
              </div>
              );
            })}

            {visibleProcessEntries.length === 0 && (
              <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
                <p className="text-base text-slate-600">No hiring process entries available.</p>
                <p className="text-sm text-slate-500 mt-1">Use Add Company Process to start building one.</p>
              </div>
            )}

            <div className="bg-white border border-slate-200 rounded-xl p-4">
              <p className="text-xs text-slate-600">
                Suggested company names: {companyNames.slice(0, 10).join(', ')}{companyNames.length > 10 ? '...' : ''}
              </p>
            </div>
          </div>
        </div>
      </AdminLayout>
    </AdminGuard>
  );
}
