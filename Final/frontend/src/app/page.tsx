'use client';

import React, { useState, useEffect } from 'react';
import { Building2, Crown, FileText, Flame, Globe, LineChart, Rocket, Star } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Layout, MetricCard } from '@/components';
import { GlobalSearch } from '@/components/Search';
import { getCompaniesShort, categorizeCompanies, getStatistics, formatPercentage, getRenderableLogoUrl, getClearbitLogoUrl, getWebsiteFallbackLogoUrl } from '@/utils/data';

interface DashboardCompanySummary {
  id: string;
  name: string;
  short_name: string;
  logo_url: string;
  website_url?: string;
  website?: string;
  category?: string;
  employee_size: string;
  yoy_growth_rate: string | number;
}

export default function Dashboard() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const checkSession = async () => {
      try {
        const response = await fetch('/api/auth/session', { cache: 'no-store' });
        const session = await response.json();
        if (!isMounted) return;

        if (!session.authenticated) {
          router.push('/login');
          return;
        }

        if (session.role === 'admin') {
          router.push('/admin');
          return;
        }

        setIsAuthenticated(true);
      } catch {
        if (isMounted) {
          router.push('/login');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    checkSession();

    return () => {
      isMounted = false;
    };
  }, [router]);

  if (isLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 text-white flex items-center justify-center mx-auto mb-4 shadow-lg animate-pulse">
            <span className="text-2xl font-bold">CIP</span>
          </div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  const companies = getCompaniesShort();
  const { marquee, superDream, dream, regular } = categorizeCompanies(companies);
  const stats = getStatistics(companies);

  const handleSearch = (companyId: string) => {
    router.push(`/company/${companyId}`);
  };

  const searchableCompanies = companies.map((c) => ({
    id: c.id,
    name: c.name,
    short_name: c.short_name,
  }));

  return (
    <Layout>
      <div className="space-y-6 sm:space-y-8">
        {/* Hero Section */}
        <section className="bg-gradient-to-br from-blue-600 to-blue-800 text-white px-4 sm:px-6 lg:px-8 py-8 sm:py-12 lg:py-16">
          <div className="max-w-4xl mx-auto text-center space-y-4 sm:space-y-6 lg:space-y-8">
            <div>
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold mb-3 sm:mb-4 leading-tight">
                Discover Your Dream Company
              </h1>
              <p className="text-base sm:text-lg lg:text-xl text-white mb-4 sm:mb-6 lg:mb-8 px-2">
                Explore company intelligence, skills requirements, and placement insights powered by real data.
              </p>
            </div>

            {/* Hero Search Bar */}
            <div className="bg-white bg-opacity-95 rounded-xl sm:rounded-2xl p-1.5 sm:p-2 shadow-xl sm:shadow-2xl">
              <GlobalSearch companies={searchableCompanies} onSelect={handleSearch} />
            </div>

            <div className="text-xs sm:text-sm text-white">
              <p>Search across {companies.length} companies and their placement insights</p>
            </div>
          </div>
        </section>

        {/* Summary Cards Section */}
        <section className="px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 mb-4 sm:mb-6">Intelligence at a Glance</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
            <MetricCard label="Total Companies" value={stats.total} icon={<Building2 className="h-6 w-6 sm:h-7 sm:w-7" />} />
            <MetricCard label="Marquee Companies" value={marquee.length} icon={<Crown className="h-6 w-6 sm:h-7 sm:w-7" />} />
            <MetricCard label="Super Dream Companies" value={superDream.length} icon={<Rocket className="h-6 w-6 sm:h-7 sm:w-7" />} />
            <MetricCard label="Dream Companies" value={dream.length} icon={<Star className="h-6 w-6 sm:h-7 sm:w-7" />} />
            <MetricCard label="Regular Companies" value={regular.length} icon={<FileText className="h-6 w-6 sm:h-7 sm:w-7" />} />
          </div>

          <div className="mt-4 sm:mt-6 grid grid-cols-1 md:grid-cols-3 gap-3 sm:gap-4">
            <MetricCard
              label="Average Growth Rate"
              value={`${stats.avgGrowth}%`}
              icon={<LineChart className="h-6 w-6 sm:h-7 sm:w-7" />}
              trend="up"
              trendValue="+2.5% YoY"
            />
            <MetricCard
              label="Highest Growth"
              value={`${stats.maxGrowth}%`}
              icon={<Flame className="h-6 w-6 sm:h-7 sm:w-7" />}
              description="Peak company performance"
            />
            <MetricCard
              label="Countries Covered"
              value="50+"
              icon={<Globe className="h-6 w-6 sm:h-7 sm:w-7" />}
              description="Global placement opportunities"
            />
          </div>
        </section>

        {/* Company Categories Overview */}
        <section className="px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 space-y-4 sm:space-y-6">
          <div>
            <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-3 sm:mb-4">Marquee Companies</h3>
            <p className="text-xs sm:text-sm text-slate-600 mb-3 sm:mb-4">
              Industry leaders with massive workforce and global presence
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              {marquee.map((company) => (
                <CompanyQuickCard key={company.id} company={company} onSelect={handleSearch} />
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-3 sm:mb-4">Super Dream Companies</h3>
            <p className="text-xs sm:text-sm text-slate-600 mb-3 sm:mb-4">
              High-growth companies with exceptional expansion (growth rate {'>'}15%)
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              {superDream.map((company) => (
                <CompanyQuickCard key={company.id} company={company} onSelect={handleSearch} />
              ))}
            </div>
          </div>
        </section>

        {/* Footer Section */}
        <section className="bg-slate-100 px-4 sm:px-6 lg:px-8 py-8 sm:py-10 lg:py-12">
          <div className="max-w-4xl mx-auto text-center">
            <h3 className="text-lg sm:text-xl font-bold text-slate-900 mb-2">Ready to Explore?</h3>
            <p className="text-sm sm:text-base text-slate-600 mb-4 sm:mb-6 px-2">
              Visit our All Companies section to discover detailed insights about each organization or use Skill Set Analytics to compare across companies.
            </p>
            <div className="flex gap-3 sm:gap-4 justify-center flex-wrap">
              <button
                onClick={() => router.push('/companies')}
                className="px-5 sm:px-6 py-2.5 sm:py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors text-sm sm:text-base touch-manipulation"
              >
                Explore All Companies
              </button>
              <button
                onClick={() => router.push('/analytics')}
                className="px-5 sm:px-6 py-2.5 sm:py-3 bg-white text-blue-600 rounded-lg font-semibold border border-blue-600 hover:bg-blue-50 transition-colors text-sm sm:text-base touch-manipulation"
              >
                Skill Analytics
              </button>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}

interface CompanyQuickCardProps {
  company: DashboardCompanySummary;
  onSelect: (id: string) => void;
}

const CompanyQuickCard: React.FC<CompanyQuickCardProps> = ({ company, onSelect }) => {
  const logoUrl = getRenderableLogoUrl(company.logo_url, company.website_url || company.website);
  const clearbitLogoUrl = getClearbitLogoUrl(company.website_url || company.website);
  const faviconFallbackUrl = getWebsiteFallbackLogoUrl(company.website_url || company.website);
  const [imageSrc, setImageSrc] = React.useState(logoUrl);
  const [imageError, setImageError] = React.useState(!logoUrl);
  const initials = company.short_name.substring(0, 2).toUpperCase();
  const colors = ['bg-blue-600', 'bg-slate-700', 'bg-emerald-600', 'bg-amber-600', 'bg-indigo-600', 'bg-rose-600'];
  const colorIndex = company.short_name.charCodeAt(0) % colors.length;
  const bgColor = colors[colorIndex];

  return (
    <button
      onClick={() => onSelect(company.id)}
      className="bg-white rounded-lg sm:rounded-xl border border-slate-200 p-3 sm:p-4 text-left hover:shadow-lg hover:border-blue-300 transition-all duration-300 group touch-manipulation"
    >
      <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
        <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-slate-100 flex items-center justify-center flex-shrink-0">
          {imageError ? (
            <div className={`w-full h-full ${bgColor} flex items-center justify-center rounded-lg`}>
              <span className="text-white font-bold text-xs">{initials}</span>
            </div>
          ) : (
            <>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={imageSrc}
                alt={company.name}
                className="w-8 h-8 sm:w-10 sm:h-10 object-contain"
                onError={() => {
                  if (clearbitLogoUrl && imageSrc !== clearbitLogoUrl) {
                    setImageSrc(clearbitLogoUrl);
                    return;
                  }
                  if (faviconFallbackUrl && imageSrc !== faviconFallbackUrl) {
                    setImageSrc(faviconFallbackUrl);
                    return;
                  }
                  setImageError(true);
                }}
              />
            </>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-bold text-sm sm:text-base text-slate-900 group-hover:text-blue-600 transition-colors truncate">{company.name}</p>
          <p className="text-xs text-slate-600 truncate">{company.category}</p>
        </div>
      </div>
      <p className="text-xs sm:text-sm text-slate-600 mb-1.5 sm:mb-2 truncate">{company.employee_size}</p>
      <div className="flex items-center gap-2">
        <span className="text-sm font-bold text-green-600">{formatPercentage(company.yoy_growth_rate)}</span>
        <span className="text-xs text-slate-600">YoY growth</span>
      </div>
    </button>
  );
};
