'use client';

import React from 'react';
import { KeyRound, UserCheck, UserMinus } from 'lucide-react';
import { AdminGuard } from '@/components/AdminGuard';
import { AdminLayout } from '@/components/AdminLayout';

const users = [
  { id: 'u1', name: 'Arun K', email: 'arunk@srmist.edu.in', role: 'Student', status: 'Pending' },
  { id: 'u2', name: 'Nithya V', email: 'nithyav@srmist.edu.in', role: 'Student', status: 'Active' },
  { id: 'u3', name: 'Placement Officer', email: 'placement@srmist.edu.in', role: 'Admin', status: 'Active' },
  { id: 'u4', name: 'Alumni Mentor', email: 'alumni@srmist.edu.in', role: 'Mentor', status: 'Inactive' },
];

export default function AdminUsersPage() {
  return (
    <AdminGuard>
      <AdminLayout>
        <div className="space-y-6 sm:space-y-8 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          <div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">User Management</h1>
            <p className="text-sm sm:text-base text-slate-600">Approve students, manage roles, remove inactive accounts, and reset credentials.</p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px]">
                <thead className="bg-slate-100 text-left text-xs sm:text-sm text-slate-700">
                  <tr>
                    <th className="px-4 py-3 font-semibold">User</th>
                    <th className="px-4 py-3 font-semibold">Email</th>
                    <th className="px-4 py-3 font-semibold">Role</th>
                    <th className="px-4 py-3 font-semibold">Status</th>
                    <th className="px-4 py-3 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-t border-slate-200 text-sm text-slate-700">
                      <td className="px-4 py-3 font-semibold text-slate-900">{user.name}</td>
                      <td className="px-4 py-3">{user.email}</td>
                      <td className="px-4 py-3">{user.role}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            user.status === 'Active'
                              ? 'bg-green-100 text-green-700'
                              : user.status === 'Inactive'
                              ? 'bg-slate-200 text-slate-700'
                              : 'bg-amber-100 text-amber-700'
                          }`}
                        >
                          {user.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button onClick={() => alert(`${user.name} approved.`)} className="p-1.5 rounded-md bg-green-100 hover:bg-green-200" title="Approve">
                            <UserCheck className="h-4 w-4 text-green-700" />
                          </button>
                          <button onClick={() => alert(`Password reset link sent to ${user.email}.`)} className="p-1.5 rounded-md bg-slate-100 hover:bg-slate-200" title="Reset Password">
                            <KeyRound className="h-4 w-4 text-slate-700" />
                          </button>
                          <button onClick={() => { if (confirm(`Remove ${user.name}?`)) alert(`${user.name} removed.`); }} className="p-1.5 rounded-md bg-red-100 hover:bg-red-200" title="Remove User">
                            <UserMinus className="h-4 w-4 text-red-700" />
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
