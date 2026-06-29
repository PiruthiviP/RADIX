import React from 'react';
import { ArrowDownRight, ArrowUpRight } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle, action }) => {
  return (
    <div className="border-b border-slate-200 bg-white sticky top-0 z-30 shadow-sm">
      <div className="px-4 sm:px-6 lg:px-8 py-4 sm:py-5 lg:py-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 truncate">{title}</h1>
          {subtitle && <p className="text-xs sm:text-sm text-slate-600 mt-1">{subtitle}</p>}
        </div>
        {action && <div className="flex-shrink-0 w-full sm:w-auto">{action}</div>}
      </div>
    </div>
  );
};

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  description?: string;
  trend?: 'up' | 'down';
  trendValue?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  icon,
  description,
  trend,
  trendValue,
}) => {
  return (
    <div className="bg-white rounded-xl p-4 sm:p-5 lg:p-6 border border-slate-200 shadow-sm hover:shadow-md hover:border-slate-300 transition-all duration-300 touch-manipulation">
      <div className="flex items-start justify-between gap-3 sm:gap-4">
        <div className="flex-1 min-w-0 overflow-hidden">
          <p className="text-xs sm:text-sm font-medium text-slate-600 mb-1.5 sm:mb-2 truncate">{label}</p>
          <p className="text-2xl sm:text-3xl font-bold text-slate-900 break-words">{value}</p>
          {description && <p className="text-xs text-slate-500 mt-1.5 sm:mt-2 truncate">{description}</p>}
        </div>
        <div className="flex-shrink-0 text-blue-700">{icon}</div>
      </div>
      {trend && trendValue && (
        <div className={`mt-3 sm:mt-4 text-xs sm:text-sm font-semibold ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
          {trend === 'up' ? <ArrowUpRight className="inline h-3.5 w-3.5 sm:h-4 sm:w-4" /> : <ArrowDownRight className="inline h-3.5 w-3.5 sm:h-4 sm:w-4" />} {trendValue}
        </div>
      )}
    </div>
  );
};

interface SectionCardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export const SectionCard: React.FC<SectionCardProps> = ({ children, className = '', hover = false }) => {
  return (
    <div
      className={`bg-white rounded-xl border border-slate-200 shadow-sm ${
        hover ? 'hover:shadow-lg hover:border-slate-300 transition-all duration-300 cursor-pointer' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
};
