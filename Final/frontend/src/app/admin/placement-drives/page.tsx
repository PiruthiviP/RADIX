'use client';

import React from 'react';
import { CalendarDays, Pencil, Plus } from 'lucide-react';
import { AdminGuard } from '@/components/AdminGuard';
import { AdminLayout } from '@/components/AdminLayout';
import { getCompanyName, placementDrives } from '@/utils/adminData';

export default function AdminPlacementDrivesPage() {
  return (
    <AdminGuard>
      <AdminLayout>
        <div className="space-y-6 sm:space-y-8 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Placement Drive Management</h1>
              <p className="text-sm sm:text-base text-slate-600">Schedule drives, define eligibility criteria, and link drives to company role offerings.</p>
            </div>
            <button
              onClick={() => alert('Add Placement Drive form coming soon!')}
              className="px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Placement Drive
            </button>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[840px]">
                <thead className="bg-slate-100 text-left text-xs sm:text-sm text-slate-700">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Company</th>
                    <th className="px-4 py-3 font-semibold">Date</th>
                    <th className="px-4 py-3 font-semibold">Branches</th>
                    <th className="px-4 py-3 font-semibold">CGPA</th>
                    <th className="px-4 py-3 font-semibold">Role</th>
                    <th className="px-4 py-3 font-semibold">Package</th>
                    <th className="px-4 py-3 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {placementDrives.map((drive) => (
                    <tr key={drive.id} className="border-t border-slate-200 text-sm text-slate-700">
                      <td className="px-4 py-3 font-semibold text-slate-900">{getCompanyName(drive.companyId)}</td>
                      <td className="px-4 py-3">{drive.date}</td>
                      <td className="px-4 py-3">{drive.eligibleBranches.join(', ')}</td>
                      <td className="px-4 py-3">{drive.cgpa}</td>
                      <td className="px-4 py-3">{drive.role}</td>
                      <td className="px-4 py-3 text-emerald-700 font-semibold">{drive.packageLpa} LPA</td>
                      <td className="px-4 py-3">
                        <button onClick={() => alert(`Edit drive for ${getCompanyName(drive.companyId)}`)} className="p-1.5 rounded-md bg-slate-100 hover:bg-slate-200 mr-2" title="Edit Drive">
                          <Pencil className="h-4 w-4 text-slate-700" />
                        </button>
                        <button onClick={() => { if (confirm(`Remove drive for ${getCompanyName(drive.companyId)}?`)) alert('Drive removed.'); }} className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200">Remove</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-4 py-3 border-t border-slate-200 text-xs text-slate-600 flex items-center gap-2">
              <CalendarDays className="h-4 w-4 text-slate-500" />
              Drive entries enforce data consistency across branch eligibility, dates, and offered package.
            </div>
          </div>
        </div>
      </AdminLayout>
    </AdminGuard>
  );
}
