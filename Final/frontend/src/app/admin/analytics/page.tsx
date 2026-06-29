'use client';

import React from 'react';
import { BarChart3, Flame, LineChart, Trophy } from 'lucide-react';
import { AdminGuard } from '@/components/AdminGuard';
import { AdminLayout } from '@/components/AdminLayout';
import { adminCompanies, getAdminSummaryStats, placementTrend } from '@/utils/adminData';

type HiringStatus = 'active' | 'inactive';

export default function AdminAnalyticsPage() {
  const stats = getAdminSummaryStats();
  const highestPaying = [...adminCompanies].sort((a, b) => b.averagePackageLpa - a.averagePackageLpa).slice(0, 3);
  const [hiringStatusByCompany, setHiringStatusByCompany] = React.useState<Record<string, HiringStatus>>(() =>
    Object.fromEntries(
      adminCompanies
        .filter((company) => company.visitingThisYear)
        .map((company) => [company.id, 'active'])
    ) as Record<string, HiringStatus>
  );

  return (
    <AdminGuard>
      <AdminLayout>
        <div className="space-y-6 sm:space-y-8 px-4 sm:px-6 lg:px-8 pt-2 sm:pt-4 lg:pt-6 pb-4 sm:pb-6 lg:pb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Analytics & Insights</h1>
            <p className="text-sm sm:text-base text-slate-600">Track trends, identify demand patterns, and benchmark placement outcomes.</p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Year-wise Placement Trend</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {placementTrend.map((item, index) => {
                const previous = placementTrend[index - 1]?.placed ?? item.placed;
                const growth = Math.round(((item.placed - previous) / previous) * 100);
                return (
                  <div key={item.year} className="border border-slate-200 rounded-lg p-4 bg-slate-50">
                    <p className="text-xs text-slate-600 mb-1">{item.year}</p>
                    <p className="text-2xl font-bold text-slate-900">{item.placed}</p>
                    <p className="text-xs text-emerald-700">{index === 0 ? 'Baseline Year' : `+${growth}% YoY`}</p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-5">
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-center gap-2 text-slate-900 font-semibold mb-2"><BarChart3 className="h-4 w-4 text-blue-700" /> Skill Demand Score</div>
              <p className="text-2xl font-bold text-blue-700">{stats.topSkills.length * 18}</p>
              <p className="text-xs text-slate-600">Heatmap-ready metric for required skills concentration.</p>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-center gap-2 text-slate-900 font-semibold mb-2"><Flame className="h-4 w-4 text-red-600" /> Process Toughness Index</div>
              <p className="text-2xl font-bold text-red-600">78 / 100</p>
              <p className="text-xs text-slate-600">Based on multi-round complexity and coding intensity.</p>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-center gap-2 text-slate-900 font-semibold mb-2"><LineChart className="h-4 w-4 text-emerald-700" /> Intelligence Coverage</div>
              <p className="text-2xl font-bold text-emerald-700">92%</p>
              <p className="text-xs text-slate-600">Profiles with verified hiring process and skill mappings.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5">
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <h2 className="text-lg font-bold text-slate-900 mb-3">Most Visiting Companies</h2>
              <div className="space-y-3">
                {adminCompanies
                  .filter((company) => company.visitingThisYear)
                  .map((company) => {
                    const status = hiringStatusByCompany[company.id] ?? 'inactive';

                    return (
                      <div key={company.id} className="flex justify-between items-center bg-slate-50 rounded-lg px-3 py-2 gap-3">
                        <span className="text-sm font-medium text-slate-800">{company.name}</span>
                        <select
                          aria-label={`Hiring status for ${company.name}`}
                          value={status}
                          onChange={(event) => {
                            const value = event.target.value as HiringStatus;
                            setHiringStatusByCompany((prev) => ({ ...prev, [company.id]: value }));
                          }}
                          className={`text-xs font-semibold rounded-md px-2 py-1 capitalize outline-none focus:ring-2 appearance-none ${
                            status === 'active'
                              ? 'text-emerald-700 border-emerald-300 bg-emerald-50 focus:ring-emerald-200'
                              : 'text-red-600 border-red-300 bg-red-50 focus:ring-red-200'
                          }`}
                        >
                          <option value="active">Active</option>
                          <option value="inactive">Inactive</option>
                        </select>
                      </div>
                    );
                  })}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <h2 className="text-lg font-bold text-slate-900 mb-3">Highest Paying Companies</h2>
              <div className="space-y-3">
                {highestPaying.map((company, idx) => (
                  <div key={company.id} className="flex justify-between items-center bg-slate-50 rounded-lg px-3 py-2">
                    <div className="flex items-center gap-2">
                      <Trophy className={`h-4 w-4 ${idx === 0 ? 'text-amber-600' : 'text-slate-500'}`} />
                      <span className="text-sm font-medium text-slate-800">{company.name}</span>
                    </div>
                    <span className="text-xs text-emerald-700 font-semibold">{company.averagePackageLpa} LPA</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      </AdminLayout>
    </AdminGuard>
  );
}
