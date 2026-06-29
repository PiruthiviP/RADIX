'use client';

import React, { use } from 'react';
import { Layout } from '@/components';
import { getCompanyById } from '@/utils/data';
import CompanyHero from '@/components/CompanyDetail/CompanyHero';
import CompanyTabs from '@/components/CompanyDetail/CompanyTabs';
import RightSideCards from '@/components/CompanyDetail/RightSideCards';

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function CompanyDetailPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const company = getCompanyById(resolvedParams.id);
  const [activeTab, setActiveTab] = React.useState('overview');

  if (!company) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <p className="text-xl text-slate-600">Company not found</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-0">
        {/* Hero Section */}
        <CompanyHero company={company} />

        {/* Main Content */}
        <div className="px-8 py-8 space-y-10">
          <div className="min-w-0">
            <CompanyTabs company={company} activeTab={activeTab} onTabChange={setActiveTab} />
          </div>

          {/* Bottom Cards */}
          <div>
            <RightSideCards company={company} />
          </div>
        </div>
      </div>
    </Layout>
  );
}
