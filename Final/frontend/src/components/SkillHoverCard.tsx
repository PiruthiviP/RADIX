'use client';

import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { Chip } from './UI';

interface SkillCompany {
  company_name: string;
  roles: string[];
  level?: string;
}

interface SkillHoverCardProps {
  skill_code: string;
  count: number;
  maxCount: number;
  example: string;
  companies: SkillCompany[];
  demandLabel: string;
  demandVariant: 'primary' | 'accent' | 'secondary';
}

const getDemandBg = (variant: string) => {
  switch (variant) {
    case 'primary':
      return 'bg-blue-50 border-blue-200';
    case 'accent':
      return 'bg-amber-50 border-amber-200';
    case 'secondary':
      return 'bg-slate-50 border-slate-200';
    default:
      return 'bg-slate-50 border-slate-200';
  }
};

export default function SkillHoverCard({
  skill_code,
  count,
  maxCount,
  example,
  companies,
  demandLabel,
  demandVariant,
}: SkillHoverCardProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const ratio = count / maxCount;

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
      {/* Main Card Header - Click to Expand */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`w-full p-4 text-left transition-all ${getDemandBg(demandVariant)} ${isExpanded ? 'border-b-2' : ''}`}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <p className="text-sm font-semibold text-slate-900">{skill_code}</p>
              <ChevronDown
                className={`h-4 w-4 text-slate-500 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
              />
            </div>
            {example && <p className="text-xs text-slate-600 mt-2 line-clamp-2">{example}</p>}
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="text-sm font-semibold text-slate-900">{count}</span>
            <Chip label={demandLabel} variant={demandVariant} />
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-3 h-2 bg-slate-300 rounded">
          <div
            className="h-2 rounded bg-blue-600 transition-all duration-300"
            style={{ width: `${Math.max(6, Math.round(ratio * 100))}%` }}
          />
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-slate-200 p-4 space-y-3">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-semibold text-slate-900">
              {companies.length} Companies • {count} Mentions
            </p>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-xs text-slate-500 hover:text-slate-700 font-medium"
            >
              ✕ Close
            </button>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {companies.length > 0 ? (
              companies.map((company, idx) => (
                <div
                  key={`${skill_code}-${company.company_name}-${idx}`}
                  className="border border-slate-200 rounded-lg p-3 hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <p className="font-semibold text-sm text-slate-900">{company.company_name}</p>
                    {company.level && (
                      <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded whitespace-nowrap">
                        {company.level}
                      </span>
                    )}
                  </div>

                  <div className="space-y-1">
                    <p className="text-xs text-slate-600 font-medium mb-1">Roles requiring this skill:</p>
                    {company.roles.map((role, roleIdx) => (
                      <p key={roleIdx} className="text-xs text-slate-700 pl-3 flex items-start">
                        <span className="mr-2 text-slate-500">•</span>
                        <span>{role}</span>
                      </p>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500">No company details available</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

