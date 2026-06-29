// ====================================================================
// RADIX Premium Role Switcher Header Dropdown
// Place in: activity-08/frontend/src/components/layout/RoleSwitcher.tsx
// ====================================================================

// ====================================================================
// RADIX Enterprise User Profile Panel & Sign Out Trigger
// Place in: activity-08/frontend/src/components/layout/RoleSwitcher.tsx
// ====================================================================

import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { 
  Shield, 
  GraduationCap, 
  Briefcase, 
  User, 
  LogOut 
} from 'lucide-react';
import { cn } from '@/lib/utils';

export const RoleSwitcher: React.FC = () => {
  const { user, logout } = useAuth();

  const getRoleStyle = (role: string) => {
    switch (role) {
      case 'Admin':
        return {
          icon: Shield,
          color: 'text-rose-500 bg-rose-500/10 border-rose-500/20',
        };
      case 'Student':
        return {
          icon: GraduationCap,
          color: 'text-indigo-500 bg-indigo-500/10 border-indigo-500/20',
        };
      case 'Recruiter':
        return {
          icon: Briefcase,
          color: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
        };
      default:
        return {
          icon: User,
          color: 'text-slate-500 bg-slate-500/10 border-slate-500/20',
        };
    }
  };

  const style = getRoleStyle(user?.role || 'Guest');
  const Icon = style.icon;

  return (
    <div className="w-full flex flex-col gap-3 p-3 rounded-xl border border-sidebar-border bg-sidebar-accent/30">
      <div className="flex items-center gap-3">
        <div className={cn("w-9 h-9 rounded-lg flex items-center justify-center border flex-shrink-0", style.color)}>
          <Icon className="w-4.5 h-4.5" />
        </div>
        <div className="min-w-0 flex-1">
          <h4 className="text-[9px] font-bold text-sidebar-foreground/50 uppercase tracking-widest font-mono">Signed In As</h4>
          <p className="text-xs font-bold truncate text-sidebar-foreground mt-0.5" title={user?.name}>{user?.name || 'Loading...'}</p>
          <p className="text-[10px] text-sidebar-foreground/60 truncate" title={user?.email}>{user?.email}</p>
        </div>
      </div>

      <button
        onClick={logout}
        className="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold rounded-lg bg-destructive/10 text-destructive border border-destructive/20 hover:bg-destructive hover:text-white transition-all duration-200 active:scale-95"
      >
        <LogOut className="w-3.5 h-3.5" />
        Sign Out
      </button>
    </div>
  );
};

export default RoleSwitcher;
