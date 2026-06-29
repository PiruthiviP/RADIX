import React, { useState } from 'react';
import Link from 'next/link';
import { Chip } from './UI';
import { Zap, Building2, TrendingUp, Briefcase, Clock, Coins, Heart, Book, Camera, Code, Cloud, Server } from 'lucide-react';
import { formatPercentage, getRenderableLogoUrl, getClearbitLogoUrl, getWebsiteFallbackLogoUrl } from '@/utils/data';

interface CompanyCardProps {
  id: string;
  name: string;
  short_name: string;
  logo_url: string;
  website_url?: string;
  category: string;
  employee_size: string;
  office_locations: string;
  operating_countries: string;
  yoy_growth_rate: string | number;
}

// Category configuration
const CATEGORY_CONFIG: Record<string, { color: string; bgColor: string; icon: React.ReactNode; description: string }> = {
  'Startup': { color: 'text-purple-700', bgColor: 'bg-purple-100 border-purple-200', icon: <Zap className="w-4 h-4" />, description: 'Early stage growth company' },
  'Scale-up/Unicorn': { color: 'text-amber-700', bgColor: 'bg-amber-100 border-amber-200', icon: <TrendingUp className="w-4 h-4" />, description: 'High-growth valued company' },
  'Enterprise': { color: 'text-blue-700', bgColor: 'bg-blue-100 border-blue-200', icon: <Building2 className="w-4 h-4" />, description: 'Large established company' },
  'Enterprise IT Services Company': { color: 'text-indigo-700', bgColor: 'bg-indigo-100 border-indigo-200', icon: <Briefcase className="w-4 h-4" />, description: 'IT services provider' },
  'Large Cap Public Bank': { color: 'text-green-700', bgColor: 'bg-green-100 border-green-200', icon: <Building2 className="w-4 h-4" />, description: 'Financial institution' },
  'Public Company': { color: 'text-blue-700', bgColor: 'bg-blue-100 border-blue-200', icon: <Building2 className="w-4 h-4" />, description: 'Public corporation' },
  'Public Enterprise': { color: 'text-cyan-700', bgColor: 'bg-cyan-100 border-cyan-200', icon: <Building2 className="w-4 h-4" />, description: 'Government enterprise' },
  'Private Ltd Company': { color: 'text-slate-700', bgColor: 'bg-slate-100 border-slate-200', icon: <Briefcase className="w-4 h-4" />, description: 'Private company' },
};

const getCategoryConfig = (category: string) => {
  const lowerCat = category.toLowerCase();
  
  // Check if it's a finance/fintech category
  if (
    lowerCat.includes('fintech') ||
    lowerCat.includes('financial') ||
    lowerCat.includes('banking') ||
    lowerCat.includes('bank') ||
    lowerCat.includes('investment') ||
    lowerCat.includes('wealth') ||
    lowerCat.includes('payments') ||
    lowerCat.includes('lending')
  ) {
    return {
      color: 'text-green-700',
      bgColor: 'bg-green-100 border-green-200',
      icon: <Coins className="w-4 h-4" />,
      description: 'Finance/FinTech'
    };
  }

  // Check if it's a healthcare category
  if (
    lowerCat.includes('health') ||
    lowerCat.includes('healthcare') ||
    lowerCat.includes('insurtech') ||
    lowerCat.includes('pharma') ||
    lowerCat.includes('medical')
  ) {
    return {
      color: 'text-red-700',
      bgColor: 'bg-red-100 border-red-200',
      icon: <Heart className="w-4 h-4" />,
      description: 'Healthcare/HealthTech'
    };
  }

  // Check if it's an EdTech category
  if (
    lowerCat.includes('edtech') ||
    lowerCat.includes('education') ||
    lowerCat.includes('e-learning') ||
    lowerCat.includes('learning')
  ) {
    return {
      color: 'text-blue-700',
      bgColor: 'bg-blue-100 border-blue-200',
      icon: <Book className="w-4 h-4" />,
      description: 'EdTech'
    };
  }

  // Check if it's an IT Services or Consulting category
  if (
    lowerCat.includes('it services') ||
    lowerCat.includes('consulting') ||
    lowerCat.includes('digital transformation')
  ) {
    return {
      color: 'text-indigo-700',
      bgColor: 'bg-indigo-100 border-indigo-200',
      icon: <Briefcase className="w-4 h-4" />,
      description: 'IT Services/Consulting'
    };
  }

  // Check if it's a Media category
  if (
    lowerCat.includes('media') ||
    lowerCat.includes('entertainment') ||
    lowerCat.includes('conglomerate')
  ) {
    return {
      color: 'text-pink-700',
      bgColor: 'bg-pink-100 border-pink-200',
      icon: <Camera className="w-4 h-4" />,
      description: 'Media/Entertainment'
    };
  }

  // Check if it's a Cloud Infrastructure category
  if (lowerCat.includes('cloud infrastructure')) {
    return {
      color: 'text-cyan-700',
      bgColor: 'bg-cyan-100 border-cyan-200',
      icon: <Cloud className="w-4 h-4" />,
      description: 'Cloud Infrastructure'
    };
  }

  // Check if it's a SaaS category
  if (lowerCat.includes('saas') || lowerCat.includes('software as a service')) {
    return {
      color: 'text-orange-700',
      bgColor: 'bg-orange-100 border-orange-200',
      icon: <Server className="w-4 h-4" />,
      description: 'SaaS'
    };
  }

  // Check if it's a Software category
  if (
    lowerCat.includes('software') ||
    lowerCat.includes('cybersecurity') ||
    lowerCat.includes('artificial intelligence')
  ) {
    return {
      color: 'text-violet-700',
      bgColor: 'bg-violet-100 border-violet-200',
      icon: <Code className="w-4 h-4" />,
      description: 'Software/AI'
    };
  }
  
  return CATEGORY_CONFIG[category] || {
    color: 'text-slate-700',
    bgColor: 'bg-slate-100 border-slate-200',
    icon: <Clock className="w-4 h-4" />,
    description: category
  };
};

export const CompanyCard: React.FC<CompanyCardProps> = ({
  id,
  name,
  short_name,
  logo_url,
  category,
  employee_size,
  office_locations,
  operating_countries,
  yoy_growth_rate,
  website_url,
}) => {
  const resolvedLogoUrl = getRenderableLogoUrl(logo_url, website_url);
  const clearbitLogoUrl = getClearbitLogoUrl(website_url);
  const faviconFallbackUrl = getWebsiteFallbackLogoUrl(website_url);
  const [imageSrc, setImageSrc] = useState(resolvedLogoUrl);
  const [imageError, setImageError] = useState(!resolvedLogoUrl);
  const offices = office_locations.split(';').map((o) => o.trim());
  const countries = operating_countries.split(';').map((c) => c.trim());
  const categoryConfig = getCategoryConfig(category);

  const initials = short_name.substring(0, 2).toUpperCase();
  const colors = ['bg-blue-600', 'bg-slate-700', 'bg-emerald-600', 'bg-amber-600', 'bg-indigo-600', 'bg-rose-600'];
  const colorIndex = short_name.charCodeAt(0) % colors.length;
  const bgColor = colors[colorIndex];

  return (
    <Link href={`/company/${id}`}>
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-xl hover:border-slate-300 transition-all duration-300 overflow-hidden cursor-pointer group h-full">
        {/* Card Header */}
        <div className="bg-gradient-to-r from-slate-50 to-blue-50 p-4 border-b border-slate-200">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="w-16 h-16 shrink-0 rounded-lg bg-white border border-slate-200 flex items-center justify-center overflow-hidden shadow-sm">
              {imageError ? (
                <div className={`w-full h-full ${bgColor} flex items-center justify-center`}>
                  <span className="text-white font-bold text-lg">{initials}</span>
                </div>
              ) : (
                <>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={imageSrc}
                    alt={name}
                    className="w-14 h-14 object-contain"
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
            <div className="min-w-0 max-w-[60%] text-right flex flex-col gap-2 items-end">
              <div className={`inline-flex max-w-full items-center gap-1.5 px-3 py-1.5 rounded-lg border ${categoryConfig.bgColor}`}>
                <span className={`${categoryConfig.color} shrink-0`}>{categoryConfig.icon}</span>
                <span className={`${categoryConfig.color} text-xs font-semibold truncate`}>{category}</span>
              </div>
            </div>
          </div>

          <h3 className="text-lg font-bold text-slate-900 group-hover:text-blue-600 transition-colors break-words">
            {name}
          </h3>
          <p className="text-xs text-slate-600 mt-1 break-words">{employee_size} employees</p>
        </div>

        {/* Card Body */}
        <div className="p-4 space-y-4">
          {/* Operating Countries */}
          <div>
            <p className="text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wide text-center">Operating Countries</p>
            <div className="flex flex-wrap gap-1 justify-center">
              {countries.slice(0, 3).map((country) => (
                <Chip key={country} label={country} variant="secondary" />
              ))}
              {countries.length > 3 && <Chip label={`+${countries.length - 3}`} variant="secondary" />}
            </div>
          </div>

          {/* Office Locations */}
          <div>
            <p className="text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wide text-center">Office Locations</p>
            <div className="flex flex-wrap gap-1 justify-center">
              {offices.slice(0, 2).map((office) => (
                <Chip key={office} label={office} variant="primary" />
              ))}
              {offices.length > 2 && <Chip label={`+${offices.length - 2} more`} variant="primary" />}
            </div>
          </div>

          {/* Growth Rate */}
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-3 border border-green-200">
            <p className="text-xs text-green-700 font-medium">YoY Growth Rate</p>
            <p className="text-2xl font-bold text-green-900">{formatPercentage(yoy_growth_rate)}</p>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-slate-50 px-4 py-3 border-t border-slate-200 group-hover:bg-blue-50 transition-colors">
          <p className="text-xs font-semibold text-blue-600 group-hover:text-blue-700">Explore Profile →</p>
        </div>
      </div>
    </Link>
  );
};
