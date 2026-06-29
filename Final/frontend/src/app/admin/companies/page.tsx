'use client';

import React, { useMemo, useState, useEffect } from 'react';
import Link from 'next/link';
import { Building2, Globe, Pencil, Plus, Search, Trash2 } from 'lucide-react';
import { AdminGuard } from '@/components/AdminGuard';
import { AdminLayout } from '@/components/AdminLayout';
import { Input } from '@/components/UI';
import { fetchApi } from '@/lib/api';

export default function AdminCompaniesPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTheme, setSelectedTheme] = useState('all');

  useEffect(() => {
    let isMounted = true;
    const loadCompanies = async () => {
      try {
        const res = await fetchApi('/api/companies');
        if (!isMounted) return;
        if (res.companies) {
          const mapped = res.companies.map((c: any) => ({
            id: String(c.company_id),
            company_id: c.company_id,
            name: c.name,
            industry: c.category || 'Enterprise',
            coreTheme: c.nature_of_company || c.nature || 'Product Company',
            website: c.website_url || c.website || 'https://example.com',
            headquarters: c.headquarters_address || c.company_headquarters || 'NA',
            category: c.category || 'Enterprise',
            averagePackageLpa: c.average_package_lpa || '12',
            roles: c.roles_offered ? (Array.isArray(c.roles_offered) ? c.roles_offered : String(c.roles_offered).split(', ')) : ['Software Engineer']
          }));
          setCompanies(mapped);
        }
      } catch (err) {
        console.error("Failed to load companies for admin:", err);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    loadCompanies();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleDelete = async (companyId: number, companyName: string) => {
    if (!confirm(`Are you sure you want to delete ${companyName} from Supabase?`)) {
      return;
    }
    try {
      await fetchApi(`/api/companies/${companyId}`, {
        method: 'DELETE'
      });
      setCompanies((prev) => prev.filter((c) => c.company_id !== companyId));
    } catch (err: any) {
      alert(`Failed to delete company: ${err.message || 'Error occurred.'}`);
    }
  };

  const themes = useMemo(() => {
    return ['all', ...new Set(companies.map((company) => company.coreTheme))];
  }, [companies]);

  const filteredCompanies = useMemo(() => {
    return companies.filter((company) => {
      const queryMatch =
        company.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.industry.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.headquarters.toLowerCase().includes(searchQuery.toLowerCase());

      const categoryMatch = selectedTheme === 'all' || company.coreTheme === selectedTheme;

      return queryMatch && categoryMatch;
    });
  }, [companies, searchQuery, selectedTheme]);

  if (loading) {
    return (
      <AdminGuard>
        <AdminLayout>
          <div className="flex items-center justify-center min-h-[50vh]">
            <div className="text-center space-y-3">
              <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-slate-600 font-medium text-sm">Querying Supabase directory...</p>
            </div>
          </div>
        </AdminLayout>
      </AdminGuard>
    );
  }

  return (
    <AdminGuard>
      <AdminLayout>
        <div className="space-y-6 sm:space-y-8 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Company Management</h1>
              <p className="text-sm sm:text-base text-slate-600">Add, edit, delete, and categorize company intelligence profiles.</p>
            </div>
            <Link
              href="/admin/companies/add"
              className="px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Company
            </Link>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 lg:p-6 space-y-4">
            <div>
              <label className="block text-xs sm:text-sm font-semibold text-slate-700 mb-2">Search Company</label>
              <Input
                icon={<Search className="h-4 w-4" />}
                type="text"
                placeholder="Search by company, industry, or headquarters..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
              />
            </div>

            <div>
              <label className="block text-xs sm:text-sm font-semibold text-slate-700 mb-2">Core Theme</label>
              <div className="flex flex-wrap gap-2">
                {themes.map((category) => (
                  <button
                     key={category}
                     onClick={() => setSelectedTheme(category)}
                     className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg font-medium text-xs sm:text-sm transition-all ${
                       selectedTheme === category ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-900 hover:bg-slate-300'
                     }`}
                  >
                    {category === 'all' ? 'All Core Themes' : category}
                  </button>
                ))}
              </div>
            </div>

            <p className="text-xs sm:text-sm text-slate-600">Showing {filteredCompanies.length} of {companies.length} companies</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-5">
            {filteredCompanies.map((company) => (
              <div key={company.id} className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow flex flex-col">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">{company.name}</h3>
                    <p className="text-sm text-slate-600">{company.industry}</p>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700">{company.coreTheme}</span>
                </div>

                <div className="space-y-2 text-sm text-slate-700">
                  <p className="flex items-center gap-2"><Globe className="h-4 w-4 text-slate-500" /> {company.website}</p>
                  <p className="flex items-center gap-2"><Building2 className="h-4 w-4 text-slate-500" /> {company.headquarters}</p>
                  <p className="text-xs text-slate-600">Original Category: {company.category}</p>
                  <p>Average Package: <span className="font-semibold text-emerald-700">{company.averagePackageLpa} LPA</span></p>
                  <p className="text-xs text-slate-600">Roles: {company.roles.join(', ')}</p>
                </div>

                <div className="mt-auto pt-4 flex gap-2">
                  <Link href={`/admin/companies/${company.id}`} className="flex-1 px-3 py-2 bg-slate-100 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-200 inline-flex items-center justify-center gap-2" title="Edit Profile">
                    <Pencil className="h-4 w-4" />
                    Edit Profile
                  </Link>
                  <button 
                    onClick={() => handleDelete(company.company_id, company.name)} 
                    className="px-3 py-2 border border-red-200 rounded-lg hover:bg-red-50" 
                    title="Delete Company"
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </AdminLayout>
    </AdminGuard>
  );
}
