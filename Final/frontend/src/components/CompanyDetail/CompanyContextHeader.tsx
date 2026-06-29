import React, { useState } from 'react';
import Link from 'next/link';
import { Building2, MapPin, Users } from 'lucide-react';
import { CompanyFull } from '@/utils/data';

interface CompanyContextHeaderProps {
  company: CompanyFull;
  active: 'skills' | 'process' | 'innovx';
  fromHref?: string;
}

export default function CompanyContextHeader({ company, active, fromHref }: CompanyContextHeaderProps) {
  const headquartersAddress =
    typeof company.headquarters_address === 'string' ? company.headquarters_address : undefined;
  const headquartersFallback =
    typeof company.headquarters === 'string' ? company.headquarters : undefined;
  const headquarters = headquartersAddress || headquartersFallback;

  const incorporationYear =
    typeof company.incorporation_year === 'number' || typeof company.incorporation_year === 'string'
      ? company.incorporation_year
      : undefined;
  const foundedYear =
    typeof company.founded_year === 'number' || typeof company.founded_year === 'string'
      ? company.founded_year
      : undefined;
  const establishedYear = incorporationYear || foundedYear;
  const employeeSize = company.employee_size;
  const companyId = company.id || company.company_id?.toString();
  const logoUrl = typeof company.logo_url === 'string' ? company.logo_url : '';
  const initials = company.short_name.substring(0, 2).toUpperCase();
  const [logoError, setLogoError] = useState(false);

  const makeTabHref = (segment: 'skills' | 'process' | 'innovx') => {
    const basePath = `/companies/${companyId}/${segment}`;
    if (!fromHref) {
      return basePath;
    }
    return `${basePath}?from=${encodeURIComponent(fromHref)}`;
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 sticky top-0 z-20">
      <div className="flex flex-col lg:flex-row lg:items-center gap-4">
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center overflow-hidden">
            {logoUrl && !logoError ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img 
                src={logoUrl} 
                alt={company.name} 
                className="w-8 h-8 object-contain" 
                onError={() => setLogoError(true)}
              />
            ) : (
              <span className="text-xs font-bold text-slate-700">{initials}</span>
            )}
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">{company.name}</h2>
            <div className="flex flex-wrap gap-4 text-xs text-slate-600 mt-2">
              {headquarters && (
                <div className="flex items-center gap-2">
                  <MapPin className="h-3 w-3 text-blue-700" />
                  <span>{headquarters}</span>
                </div>
              )}
              {establishedYear && (
                <div className="flex items-center gap-2">
                  <Building2 className="h-3 w-3 text-blue-700" />
                  <span>Est. {establishedYear}</span>
                </div>
              )}
              {employeeSize && (
                <div className="flex items-center gap-2">
                  <Users className="h-3 w-3 text-blue-700" />
                  <span>{employeeSize}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {companyId && (
          <div className="flex items-center gap-2 flex-wrap justify-center lg:justify-start">
            <Link
              href={makeTabHref('skills')}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold border ${
                active === 'skills'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              Hiring Skill Sets
            </Link>
            <Link
              href={makeTabHref('process')}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold border ${
                active === 'process'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              Hiring Rounds
            </Link>
            <Link
              href={makeTabHref('innovx')}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold border ${
                active === 'innovx'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              InnovX
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
