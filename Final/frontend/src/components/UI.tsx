import React from 'react';

interface ChipProps {
  label: string;
  variant?: 'primary' | 'secondary' | 'accent' | 'success' | 'warning';
  onRemove?: () => void;
  icon?: React.ReactNode;
}

export const Chip: React.FC<ChipProps> = ({ label, variant = 'secondary', onRemove, icon }) => {
  const variants: Record<string, string> = {
    primary: 'bg-blue-100 text-blue-800 border-blue-200',
    secondary: 'bg-slate-100 text-slate-800 border-slate-200',
    accent: 'bg-purple-100 text-purple-800 border-purple-200',
    success: 'bg-green-100 text-green-800 border-green-200',
    warning: 'bg-orange-100 text-orange-800 border-orange-200',
  };

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${variants[variant]} text-sm font-medium`}>
      {icon && <span>{icon}</span>}
      <span>{label}</span>
      {onRemove && (
        <button
          onClick={onRemove}
          className="ml-1 text-xs font-bold hover:opacity-70 transition-opacity"
        >
          ×
        </button>
      )}
    </div>
  );
};

interface TabsProps {
  tabs: Array<{ id: string; label: string; icon?: React.ReactNode }>;
  activeTab: string;
  onChange: (tabId: string) => void;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, activeTab, onChange }) => {
  return (
    <div className="border-b border-slate-200">
      <div className="flex gap-1 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`px-4 py-3 font-medium text-sm whitespace-nowrap border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            {tab.icon && <span className="mr-2">{tab.icon}</span>}
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
};

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  icon,
  children,
  className = '',
  ...props
}) => {
  const baseClasses = 'font-medium rounded-lg transition-all duration-200 flex items-center gap-2';

  const variants: Record<string, string> = {
    primary: 'bg-blue-700 text-white hover:bg-blue-800 shadow-sm',
    secondary: 'bg-blue-50 text-blue-900 hover:bg-blue-100',
    outline: 'border border-blue-700 text-blue-700 hover:bg-blue-50',
    ghost: 'text-blue-700 hover:bg-blue-50',
  };

  const sizes: Record<string, string> = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {icon && <span>{icon}</span>}
      {children}
    </button>
  );
};

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ icon, error, className = '', ...props }) => {
  const baseClasses = `w-full px-3 py-2 text-sm border rounded-lg font-medium text-slate-900 placeholder-slate-500 bg-white focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400 transition-all ${
    icon ? 'pl-10' : ''
  } ${error ? 'border-red-500' : 'border-slate-300'}`;

  return (
    <div className="relative">
      <input className={`${baseClasses} ${className}`} {...props} />
      {icon && (
        <div className="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-700 pointer-events-none">
          {icon}
        </div>
      )}
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
    </div>
  );
};
