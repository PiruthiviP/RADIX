'use client';

import React from 'react';
import { CheckCircle2, Pencil, XCircle } from 'lucide-react';
import { AdminGuard } from '@/components/AdminGuard';
import { AdminLayout } from '@/components/AdminLayout';
import { getCompanyName, interviewExperiences } from '@/utils/adminData';

export default function AdminInterviewExperiencesPage() {
  return (
    <AdminGuard>
      <AdminLayout>
        <div className="space-y-6 sm:space-y-8 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          <div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Interview Experience Management</h1>
            <p className="text-sm sm:text-base text-slate-600">Moderate submitted experiences and map approved content to company and role.</p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px]">
                <thead className="bg-slate-100 text-left text-xs sm:text-sm text-slate-700">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Company</th>
                    <th className="px-4 py-3 font-semibold">Role</th>
                    <th className="px-4 py-3 font-semibold">Year</th>
                    <th className="px-4 py-3 font-semibold">Status</th>
                    <th className="px-4 py-3 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {interviewExperiences.map((item) => (
                    <tr key={item.id} className="border-t border-slate-200 text-sm text-slate-700">
                      <td className="px-4 py-3 font-semibold text-slate-900">{getCompanyName(item.companyId)}</td>
                      <td className="px-4 py-3">{item.role}</td>
                      <td className="px-4 py-3">{item.year}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            item.status === 'Approved'
                              ? 'bg-green-100 text-green-700'
                              : item.status === 'Rejected'
                              ? 'bg-red-100 text-red-700'
                              : 'bg-amber-100 text-amber-700'
                          }`}
                        >
                          {item.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button onClick={() => alert(`Approved experience for ${getCompanyName(item.companyId)} (${item.year})`)} className="p-1.5 rounded-md bg-green-100 hover:bg-green-200" title="Approve">
                            <CheckCircle2 className="h-4 w-4 text-green-700" />
                          </button>
                          <button onClick={() => alert(`Rejected experience for ${getCompanyName(item.companyId)} (${item.year})`)} className="p-1.5 rounded-md bg-red-100 hover:bg-red-200" title="Reject">
                            <XCircle className="h-4 w-4 text-red-700" />
                          </button>
                          <button onClick={() => alert(`Edit formatting for ${getCompanyName(item.companyId)} — ${item.role}`)} className="p-1.5 rounded-md bg-slate-100 hover:bg-slate-200" title="Edit Formatting">
                            <Pencil className="h-4 w-4 text-slate-700" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </AdminLayout>
    </AdminGuard>
  );
}
