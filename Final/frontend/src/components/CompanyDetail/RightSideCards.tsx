import React from 'react';
import { CompanyFull } from '@/utils/data';

interface RightSideCardsProps {
  company: CompanyFull;
}

export default function RightSideCards({ company }: RightSideCardsProps) {
  return (
    <div className="lg:sticky lg:top-24 space-y-3 sm:space-y-4">
      {/* Key Metrics */}
      <div className="bg-white border border-slate-200 rounded-xl p-3 sm:p-4 space-y-2 sm:space-y-3">
        <h4 className="font-bold text-sm sm:text-base text-slate-900">Quick Stats</h4>
        <div className="space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
          {company.incorporation_year && (
            <div className="flex justify-between gap-2">
              <span className="text-slate-600">Founded</span>
              <span className="font-semibold text-slate-900">{company.incorporation_year}</span>
            </div>
          )}
          {company.nature_of_company && (
            <div className="flex justify-between gap-2">
              <span className="text-slate-600 break-words">Type</span>
              <span className="font-semibold text-slate-900 text-right break-words">{company.nature_of_company}</span>
            </div>
          )}
          {company.valuation && (
            <div className="flex justify-between gap-2">
              <span className="text-slate-600">Valuation</span>
              <span className="font-semibold text-slate-900 text-right break-words">{company.valuation}</span>
            </div>
          )}
          {company.annual_revenue && (
            <div className="flex justify-between gap-2">
              <span className="text-slate-600">Revenue</span>
              <span className="font-semibold text-slate-900 text-right break-words">{company.annual_revenue}</span>
            </div>
          )}
          {company.employee_size && (
            <div className="flex justify-between gap-2">
              <span className="text-slate-600">Employees</span>
              <span className="font-semibold text-slate-900 text-right break-words">{company.employee_size}</span>
            </div>
          )}
        </div>
      </div>

      {/* ESG Rating */}
      {company.esg_ratings && (
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-3 sm:p-4">
          <p className="text-xs font-semibold text-green-700 mb-2">ESG COMMITMENT</p>
          <p className="text-xs text-green-800">{company.esg_ratings}</p>
        </div>
      )}
    </div>
  );
}
