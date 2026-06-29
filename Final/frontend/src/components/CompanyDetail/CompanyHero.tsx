import React, { useState } from 'react';
import { Globe, Instagram, Linkedin, MapPin, Twitter, Target, Brain, Lightbulb } from 'lucide-react';
import Link from 'next/link';
import { Chip } from '../UI';
import { CompanyFull, formatPercentage, getRenderableLogoUrl, getClearbitLogoUrl, getWebsiteFallbackLogoUrl } from '@/utils/data';

interface CompanyHeroProps {
  company: CompanyFull;
  showNavigationLinks?: boolean;
  customNavigationLinks?: React.ReactNode;
}

export default function CompanyHero({ company, showNavigationLinks = true, customNavigationLinks }: CompanyHeroProps) {
  const logoUrl = getRenderableLogoUrl(company.logo_url, company.website_url || company.website);
  const clearbitLogoUrl = getClearbitLogoUrl(company.website_url || company.website);
  const faviconLogoUrl = getWebsiteFallbackLogoUrl(company.website_url || company.website);
  const headquartersAddress =
    typeof company.headquarters_address === 'string' ? company.headquarters_address : undefined;
  const headquartersFallback =
    typeof company.headquarters === 'string' ? company.headquarters : undefined;
  const headquarters = headquartersAddress || headquartersFallback || 'N/A';
  const website = typeof company.website === 'string' ? company.website : undefined;
  const linkedinUrl = typeof company.linkedin_url === 'string' ? company.linkedin_url : undefined;
  const twitterHandle = typeof company.twitter_handle === 'string' ? company.twitter_handle : undefined;
  const instagramHandle = typeof company.instagram_handle === 'string' ? company.instagram_handle : undefined;
  const primaryContactEmail =
    typeof company.primary_contact_email === 'string' ? company.primary_contact_email : undefined;
  const phone = typeof company.phone === 'string' ? company.phone : undefined;
  const [imageSrc, setImageSrc] = useState(logoUrl);
  const [imageError, setImageError] = useState(!logoUrl);
  const offices = company.office_locations.split(';').map((o) => o.trim());
  const countries = company.operating_countries.split(';').map((c) => c.trim());
  const initials = company.short_name.substring(0, 2).toUpperCase();
  const colors = ['bg-blue-600', 'bg-slate-700', 'bg-emerald-600', 'bg-amber-600', 'bg-indigo-600', 'bg-rose-600'];
  const colorIndex = company.short_name.charCodeAt(0) % colors.length;
  const bgColor = colors[colorIndex];

  return (
    <div className="bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 border-b border-slate-200 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
      {(showNavigationLinks || customNavigationLinks) && (
        <div className="mb-4 sm:mb-6 flex flex-col items-center gap-2 sm:gap-3 lg:flex-row lg:justify-end">
          {customNavigationLinks}

          {showNavigationLinks && (
            <>
              <Link
                href={`/companies/${company.id}/process`}
                className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 bg-white border border-slate-300 rounded-lg text-slate-800 hover:bg-blue-50 hover:border-blue-400 hover:text-blue-800 transition-all touch-manipulation shadow-sm hover:shadow-md"
              >
                <Target className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-600" />
                <span className="text-xs sm:text-sm font-medium">Hiring Rounds</span>
              </Link>
              <Link
                href={`/companies/${company.id}/skills`}
                className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 bg-white border border-slate-300 rounded-lg text-slate-800 hover:bg-purple-50 hover:border-purple-400 hover:text-purple-800 transition-all touch-manipulation shadow-sm hover:shadow-md"
              >
                <Brain className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-purple-600" />
                <span className="text-xs sm:text-sm font-medium">Hiring Skills</span>
              </Link>
              <Link
                href={`/companies/${company.id}/innovx`}
                className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 bg-white border border-slate-300 rounded-lg text-slate-800 hover:bg-amber-50 hover:border-amber-400 hover:text-amber-800 transition-all touch-manipulation shadow-sm hover:shadow-md"
              >
                <Lightbulb className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-amber-600" />
                <span className="text-xs sm:text-sm font-medium">InnovX</span>
              </Link>
            </>
          )}
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 lg:gap-8">
        {/* Logo and Basic Info */}
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 lg:gap-6 w-full">
          <div className="w-20 h-20 sm:w-24 sm:h-24 lg:w-32 lg:h-32 rounded-xl sm:rounded-2xl bg-white border border-slate-200 flex items-center justify-center shadow-md flex-shrink-0 mx-auto sm:mx-0">
            {imageError ? (
              <div className={`w-full h-full ${bgColor} flex items-center justify-center rounded-xl sm:rounded-2xl`}>
                <span className="text-white font-bold text-2xl sm:text-3xl lg:text-4xl">{initials}</span>
              </div>
            ) : (
              <>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={imageSrc}
                  alt={company.name}
                  className="w-16 h-16 sm:w-20 sm:h-20 lg:w-28 lg:h-28 object-contain"
                  onError={() => {
                    if (clearbitLogoUrl && imageSrc !== clearbitLogoUrl) {
                      setImageSrc(clearbitLogoUrl);
                      return;
                    }
                    if (faviconLogoUrl && imageSrc !== faviconLogoUrl) {
                      setImageSrc(faviconLogoUrl);
                      return;
                    }
                    setImageError(true);
                  }}
                />
              </>
            )}
          </div>

          <div className="flex-1 text-center sm:text-left min-w-0">
            <div className="mb-2 sm:mb-3">
              <p className="text-xs sm:text-sm font-semibold text-slate-600 uppercase tracking-wide break-words">{company.category}</p>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-1 break-words">{company.name}</h1>
              <p className="text-sm sm:text-base text-slate-700 break-words">{company.short_name}</p>
            </div>

            <div className="mt-3 sm:mt-4 flex flex-col sm:flex-row items-center gap-3 sm:gap-4 flex-wrap justify-center sm:justify-start">
              <div className="inline-flex items-center gap-2">
                <span className="text-xl sm:text-2xl font-bold text-blue-600">{company.employee_size}</span>
                <span className="text-xs sm:text-sm text-slate-600">employees</span>
              </div>

              <div className="inline-flex items-center gap-2">
                <span className="text-xl sm:text-2xl font-bold text-green-600">{formatPercentage(company.yoy_growth_rate)}</span>
                <span className="text-xs sm:text-sm text-slate-600">YoY Growth</span>
              </div>

              <div className="inline-flex items-center gap-2">
                <MapPin className="h-4 w-4 text-blue-700 flex-shrink-0" />
                <span className="text-xs sm:text-sm text-slate-700 break-words">{headquarters}</span>
              </div>
            </div>

            {/* Quick Links */}
            <div className="mt-4 sm:mt-6 flex gap-2 sm:gap-3 flex-wrap justify-center sm:justify-start">
              {website && (
                <a
                  href={website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 bg-white border border-slate-300 rounded-lg text-slate-800 hover:bg-blue-50 hover:text-blue-800 transition-colors touch-manipulation"
                >
                  <Globe className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-700" />
                  <span className="text-xs sm:text-sm font-medium">Website</span>
                </a>
              )}
              {linkedinUrl && (
                <a
                  href={linkedinUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 bg-white border border-slate-300 rounded-lg text-slate-800 hover:bg-blue-50 hover:text-blue-800 transition-colors touch-manipulation"
                >
                  <Linkedin className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-700" />
                  <span className="text-xs sm:text-sm font-medium">LinkedIn</span>
                </a>
              )}
              {twitterHandle && (
                <a
                  href={`https://twitter.com/${twitterHandle.replace('@', '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 bg-white border border-slate-300 rounded-lg text-slate-800 hover:bg-blue-50 hover:text-blue-800 transition-colors touch-manipulation"
                >
                  <Twitter className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-700" />
                  <span className="text-xs sm:text-sm font-medium">Twitter</span>
                </a>
              )}
              {instagramHandle && (
                <a
                  href={`https://instagram.com/${instagramHandle.replace('@', '')}`
                  }
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 bg-white border border-slate-300 rounded-lg text-slate-800 hover:bg-blue-50 hover:text-blue-800 transition-colors touch-manipulation"
                >
                  <Instagram className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-700" />
                  <span className="text-xs sm:text-sm font-medium">Instagram</span>
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Contact Info */}
      {(primaryContactEmail || phone) && (
        <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-slate-200">
          <h3 className="text-xs sm:text-sm font-semibold text-slate-700 mb-2 sm:mb-3">Contact Information</h3>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-6 flex-wrap">
            {primaryContactEmail && (
              <div>
                <p className="text-xs text-slate-600 mb-1">Email</p>
                <a href={`mailto:${primaryContactEmail}`} className="text-xs sm:text-sm text-blue-600 hover:underline break-all">
                  {primaryContactEmail}
                </a>
              </div>
            )}
            {phone && (
              <div>
                <p className="text-xs text-slate-600 mb-1">Phone</p>
                <a href={`tel:${phone}`} className="text-xs sm:text-sm text-blue-600 hover:underline">
                  {phone}
                </a>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Operating Info */}
      <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-slate-200">
        <div className="space-y-3 sm:space-y-6">
          <div>
            <p className="text-xs font-semibold text-slate-700 mb-2 uppercase text-center">Operating Countries</p>
            <div className="flex flex-wrap gap-1 justify-center">
              {countries.slice(0, 10).map((country) => (
                <Chip key={country} label={country} variant="secondary" />
              ))}
              {countries.length > 10 && (
                <Chip label={`+${countries.length - 10} more`} variant="secondary" />
              )}
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-700 mb-2 uppercase text-center">Office Locations</p>
            <div className="flex flex-wrap gap-1 justify-center">
              {offices.slice(0, 8).map((office) => (
                <Chip key={office} label={office} variant="primary" />
              ))}
              {offices.length > 8 && (
                <Chip label={`+${offices.length - 8} more`} variant="primary" />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
