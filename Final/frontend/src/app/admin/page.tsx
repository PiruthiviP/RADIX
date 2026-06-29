'use client';

import React from 'react';
import { BarChart3, Briefcase, Building2, FileText, Flame, LineChart, ShieldCheck, Target } from 'lucide-react';
import { AdminGuard } from '@/components/AdminGuard';
import { AdminLayout } from '@/components/AdminLayout';
import { MetricCard } from '@/components';
import {
  coreThemeDistribution,
  getAdminSummaryStats,
  hiringRoundDistribution,
  skillTags,
  placementTrend,
} from '@/utils/adminData';

export default function AdminDashboardPage() {
  const stats = getAdminSummaryStats();
  const mostRequiredSkills = stats.topSkills;

  return (
    <AdminGuard>
      <AdminLayout>
        <div className="space-y-6 sm:space-y-8 px-4 sm:px-6 lg:px-8 pt-2 sm:pt-4 lg:pt-6 pb-4 sm:pb-6 lg:pb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Admin Dashboard</h1>
            <p className="text-sm sm:text-base text-slate-600">System-level overview of placement intelligence and operational health.</p>
          </div>

          <section className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-5">
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
          </section>

          <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
            <MetricCard label="Total Companies" value={stats.totalCompanies} icon={<Building2 className="h-6 w-6" />} />
            <MetricCard label="Visiting This Year" value={stats.visitingThisYear} icon={<Target className="h-6 w-6" />} />
            <MetricCard label="Total Roles" value={stats.totalRoles} icon={<Briefcase className="h-6 w-6" />} />
            <MetricCard label="Interview Experiences" value={stats.totalExperiences} icon={<FileText className="h-6 w-6" />} />
          </section>

          <section className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-5">
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <h2 className="text-lg font-bold text-slate-900 mb-4">Companies by Core Theme</h2>
              <div className="space-y-3">
                {coreThemeDistribution.map((item) => (
                  <div key={item.theme}>
                    <div className="flex justify-between text-sm text-slate-700 mb-1">
                      <span>{item.theme}</span>
                      <span>{item.companies}</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2.5">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full"
                        style={{ width: `${(item.companies / stats.totalCompanies) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <h2 className="text-lg font-bold text-slate-900 mb-4">Hiring Rounds Distribution</h2>
              <div className="space-y-3">
                {hiringRoundDistribution.map((item) => (
                  <div key={item.round}>
                    <div className="flex justify-between text-sm text-slate-700 mb-1">
                      <span>{item.round}</span>
                      <span>{item.count}</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2.5">
                      <div
                        className="bg-emerald-600 h-2.5 rounded-full"
                        style={{ width: `${(item.count / 4) * 25}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <h2 className="text-lg font-bold text-slate-900 mb-4">Most Required Skills</h2>
              <div className="space-y-2.5">
                {mostRequiredSkills.map((item) => (
                  <div key={item.skill} className="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2">
                    <span className="text-sm font-medium text-slate-800">{item.skill}</span>
                    <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded-full">Score {item.score}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-500 mt-3">Based on {skillTags.length} skill mappings across active roles.</p>
            </div>
          </section>

          <section className="bg-white rounded-xl border border-slate-200 p-5">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Placement Statistics Trend</h2>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              {placementTrend.map((trend) => (
                <div key={trend.year} className="rounded-lg border border-slate-200 p-4 bg-slate-50">
                  <p className="text-xs text-slate-600 mb-1">{trend.year}</p>
                  <p className="text-2xl font-bold text-slate-900">{trend.placed}</p>
                  <p className="text-xs text-emerald-700">Students placed</p>
                </div>
              ))}
            </div>
            <div className="mt-4 text-sm text-slate-600 flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-blue-700" />
              Year-wise upward movement indicates a stronger placement ecosystem.
            </div>
          </section>

          <section className="bg-blue-50 border border-blue-200 rounded-xl p-5">
            <h3 className="text-base font-bold text-blue-900 mb-2">Concept Statement</h3>
            <p className="text-sm text-blue-800 leading-relaxed">
              The administrative module acts as the operational backbone of the Placement Company Intelligence Platform, enabling authorized users to manage company profiles, hiring processes, placement drives, skill requirements, and analytics. This ensures that the platform maintains accurate, structured, and continuously updated placement intelligence for students and faculty users.
            </p>
            <div className="mt-3 text-xs text-blue-700 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4" />
              Data quality, verification, and moderation are centralized for controlled governance.
            </div>
          </section>
        </div>
      </AdminLayout>
    </AdminGuard>
  );
}
