'use client';

import React, { use, useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Brain, Target, Edit3, Save, X, Loader2 } from 'lucide-react';
import { AdminGuard } from '@/components/AdminGuard';
import { AdminLayout } from '@/components/AdminLayout';
import { getCompaniesShort } from '@/utils/data';
import CompanyHero from '@/components/CompanyDetail/CompanyHero';
import CompanyTabs from '@/components/CompanyDetail/CompanyTabs';
import RightSideCards from '@/components/CompanyDetail/RightSideCards';
import { fetchApi } from '@/lib/api';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function AdminCompanyViewPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const companyId = resolvedParams.id;
  
  const [company, setCompany] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Edit modal controls
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editForm, setEditForm] = useState<any>({
    name: '',
    website_url: '',
    headquarters_address: '',
    category: '',
    nature_of_company: '',
    employee_size: '',
    ceo_name: '',
    yoy_growth_rate: '',
    overview_text: '',
    tech_stack: ''
  });

  const loadCompanyDetails = async () => {
    try {
      const res = await fetchApi('/api/companies');
      if (res.companies) {
        // Find by name matching or ID matching
        const target = res.companies.find((c: any) => String(c.company_id) === companyId);
        if (target) {
          setCompany(target);
          setEditForm({
            name: target.name || '',
            website_url: target.website_url || target.website || '',
            headquarters_address: target.headquarters_address || target.company_headquarters || target.headquarters || '',
            category: target.category || '',
            nature_of_company: target.nature_of_company || target.nature || '',
            employee_size: target.employee_size || '',
            ceo_name: target.ceo_name || '',
            yoy_growth_rate: target.yoy_growth_rate || '',
            overview_text: target.overview_text || '',
            tech_stack: target.tech_stack || ''
          });
        }
      }
    } catch (err) {
      console.error("Error loading company details:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCompanyDetails();
  }, [companyId]);

  const handleEditSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      // Build a consolidated payload by merging edited parameters onto the existing company profile
      const updatedConsolidated = {
        ...company,
        name: editForm.name,
        website_url: editForm.website_url,
        website: editForm.website_url, // keep legacy field synced
        headquarters_address: editForm.headquarters_address,
        company_headquarters: editForm.headquarters_address,
        category: editForm.category,
        nature_of_company: editForm.nature_of_company,
        nature: editForm.nature_of_company,
        employee_size: editForm.employee_size,
        ceo_name: editForm.ceo_name,
        yoy_growth_rate: editForm.yoy_growth_rate,
        overview_text: editForm.overview_text,
        tech_stack: editForm.tech_stack
      };

      const res = await fetchApi('/api/save', {
        method: 'POST',
        body: JSON.stringify({ consolidated: updatedConsolidated })
      });

      if (!res.success) {
        throw new Error(res.message || "Failed to save.");
      }

      setIsEditOpen(false);
      // Reload company details to show updated data
      await loadCompanyDetails();
    } catch (err: any) {
      alert(`Save failed: ${err.message || 'Error occurred.'}`);
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return (
      <AdminGuard>
        <AdminLayout>
          <div className="flex items-center justify-center min-h-[50vh]">
            <div className="text-center space-y-3">
              <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-slate-600 font-medium text-sm">Querying company details...</p>
            </div>
          </div>
        </AdminLayout>
      </AdminGuard>
    );
  }

  if (!company) {
    return (
      <AdminGuard>
        <AdminLayout>
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-center space-y-4">
              <p className="text-xl text-slate-600 font-medium">Company not found</p>
              <Link
                href="/admin/companies"
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Companies
              </Link>
            </div>
          </div>
        </AdminLayout>
      </AdminGuard>
    );
  }

  // Format mapping to make it compatible with detail children components
  const displayCompany = {
    id: String(company.company_id),
    company_id: company.company_id,
    name: company.name,
    short_name: company.short_name || company.name.substring(0, 10),
    logo_url: company.logo_url || '',
    website_url: company.website_url || company.website || 'https://example.com',
    category: company.category || 'Enterprise',
    employee_size: company.employee_size || '100+',
    operating_countries: company.operating_countries || company.countries_operating_in || 'Global',
    office_locations: company.headquarters_address || company.company_headquarters || 'NA',
    yoy_growth_rate: company.yoy_growth_rate || '10%',
    overview_text: company.overview_text || 'No description available.',
    unique_differentiators: company.unique_differentiators || 'NA',
    ai_ml_adoption_level: company.ai_ml_adoption_level || 'Medium',
    weaknesses_gaps: company.weaknesses_gaps || 'NA',
    key_challenges_needs: company.key_challenges_needs || 'NA',
    tech_stack: company.tech_stack || 'NA',
    focus_sectors: company.focus_sectors || 'NA',
    core_value_proposition: company.core_value_proposition || 'NA'
  };

  return (
    <AdminGuard>
      <AdminLayout>
        {/* Back nav */}
        <div className="px-4 sm:px-6 lg:px-8 py-3 border-b border-slate-200 bg-white flex items-center justify-between">
          <Link
            href="/admin/companies"
            className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-900 transition-colors font-medium"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Companies
          </Link>
          
          <button
            onClick={() => setIsEditOpen(true)}
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold inline-flex items-center gap-1.5 shadow"
          >
            <Edit3 className="h-3.5 w-3.5" />
            Edit Profile Details
          </button>
        </div>

        {/* Company overview */}
        <div className="space-y-0">
          <CompanyHero
            company={displayCompany}
            showNavigationLinks={false}
            customNavigationLinks={
              <div className="flex w-full max-w-sm flex-row items-center justify-center gap-2">
                <Link
                  href={`/admin/hiring-processes?company=${encodeURIComponent(displayCompany.name)}`}
                  className="inline-flex flex-1 min-w-0 justify-center items-center gap-1.5 sm:gap-2 px-2.5 sm:px-4 py-1.5 sm:py-2 bg-white border border-slate-300 rounded-lg text-slate-800 hover:bg-blue-50 hover:border-blue-400 hover:text-blue-800 transition-all"
                >
                  <Target className="h-4 w-4 text-blue-600" />
                  <span className="text-xs sm:text-sm font-medium whitespace-nowrap">Hiring Rounds</span>
                </Link>
                <Link
                  href={`/admin/skills-intelligence?company=${encodeURIComponent(displayCompany.name)}`}
                  className="inline-flex flex-1 min-w-0 justify-center items-center gap-1.5 sm:gap-2 px-2.5 sm:px-4 py-1.5 sm:py-2 bg-white border border-slate-300 rounded-lg text-slate-800 hover:bg-purple-50 hover:border-purple-400 hover:text-purple-800 transition-all"
                >
                  <Brain className="h-4 w-4 text-purple-600" />
                  <span className="text-xs sm:text-sm font-medium whitespace-nowrap">Hiring Skills</span>
                </Link>
              </div>
            }
          />

          <div className="px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-8 sm:space-y-10">
            <div className="min-w-0">
              <CompanyTabs company={displayCompany} activeTab={activeTab} onTabChange={setActiveTab} />
            </div>
            <div>
              <RightSideCards company={displayCompany} />
            </div>
          </div>
        </div>

        {/* Edit Modal Dialog */}
        {isEditOpen && (
          <div className="fixed inset-0 z-[10000] flex items-center justify-center bg-black/50 p-4 overflow-y-auto">
            <div className="bg-white rounded-xl shadow-2xl border border-slate-200 w-full max-w-2xl overflow-hidden flex flex-col my-8 max-h-[85vh]">
              {/* Header */}
              <div className="bg-slate-50 border-b border-slate-200 px-6 py-4 flex items-center justify-between">
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Edit3 className="h-4 w-4 text-blue-600" />
                  Edit Profile: {displayCompany.name}
                </h3>
                <button 
                  onClick={() => setIsEditOpen(false)}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Form content */}
              <form onSubmit={handleEditSave} className="flex-1 overflow-y-auto p-6 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Website URL</label>
                    <input 
                      type="url"
                      value={editForm.website_url}
                      onChange={(e) => setEditForm({...editForm, website_url: e.target.value})}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Headquarters</label>
                    <input 
                      type="text"
                      value={editForm.headquarters_address}
                      onChange={(e) => setEditForm({...editForm, headquarters_address: e.target.value})}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Category / Industry</label>
                    <input 
                      type="text"
                      value={editForm.category}
                      onChange={(e) => setEditForm({...editForm, category: e.target.value})}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Nature of Company</label>
                    <input 
                      type="text"
                      value={editForm.nature_of_company}
                      onChange={(e) => setEditForm({...editForm, nature_of_company: e.target.value})}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Employee Size</label>
                    <input 
                      type="text"
                      value={editForm.employee_size}
                      onChange={(e) => setEditForm({...editForm, employee_size: e.target.value})}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">CEO Name</label>
                    <input 
                      type="text"
                      value={editForm.ceo_name}
                      onChange={(e) => setEditForm({...editForm, ceo_name: e.target.value})}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">YoY Growth Rate</label>
                    <input 
                      type="text"
                      value={editForm.yoy_growth_rate}
                      onChange={(e) => setEditForm({...editForm, yoy_growth_rate: e.target.value})}
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Overview Description</label>
                  <textarea 
                    rows={4}
                    value={editForm.overview_text}
                    onChange={(e) => setEditForm({...editForm, overview_text: e.target.value})}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Technology Stack</label>
                  <input 
                    type="text"
                    value={editForm.tech_stack}
                    onChange={(e) => setEditForm({...editForm, tech_stack: e.target.value})}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
                  />
                </div>

                {/* Submit panel */}
                <div className="pt-4 border-t border-slate-200 flex justify-end gap-3 bg-white">
                  <button
                    type="button"
                    onClick={() => setIsEditOpen(false)}
                    className="px-4 py-2 border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-sm font-semibold"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSaving}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold inline-flex items-center gap-1.5 disabled:opacity-50"
                  >
                    {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                    Save Changes
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </AdminLayout>
    </AdminGuard>
  );
}
