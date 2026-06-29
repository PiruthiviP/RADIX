'use client';

import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {
  BarChart3,
  Briefcase,
  Building2,
  ChevronLeft,
  ChevronRight,
  Database,
  FileText,
  LayoutDashboard,
  ShieldCheck,
  Users,
  Wrench,
  BookOpen,
} from 'lucide-react';

interface AdminNavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const adminNavItems: AdminNavItem[] = [
  { label: 'Dashboard', href: '/admin', icon: <LayoutDashboard className="h-5 w-5" /> },
  { label: 'Companies', href: '/admin/companies', icon: <Building2 className="h-5 w-5" /> },
  { label: 'Hiring Processes', href: '/admin/hiring-processes', icon: <Briefcase className="h-5 w-5" /> },
  { label: 'Skills Intelligence', href: '/admin/skills-intelligence', icon: <Database className="h-5 w-5" /> },
  { label: 'Placement Drives', href: '/admin/placement-drives', icon: <ShieldCheck className="h-5 w-5" /> },
  { label: 'Interview Experiences', href: '/admin/interview-experiences', icon: <FileText className="h-5 w-5" /> },
  { label: 'Analytics', href: '/admin/analytics', icon: <BarChart3 className="h-5 w-5" /> },
  { label: 'Users', href: '/admin/users', icon: <Users className="h-5 w-5" /> },
];

export const AdminSidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setIsMobileMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);

  return (
    <>
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="lg:hidden fixed top-2 left-4 z-[9999] w-12 h-12 rounded-lg bg-white border-2 border-slate-200 hover:bg-slate-50 shadow-lg hover:shadow-xl transition-all duration-300 flex flex-col items-center justify-center gap-1.5"
        aria-label="Toggle admin menu"
      >
        <span
          className={`block h-0.5 w-6 bg-blue-700 transition-all duration-300 ease-in-out ${
            isMobileMenuOpen ? 'rotate-45 translate-y-2' : ''
          }`}
        />
        <span
          className={`block h-0.5 w-6 bg-blue-700 transition-all duration-300 ease-in-out ${
            isMobileMenuOpen ? 'opacity-0' : 'opacity-100'
          }`}
        />
        <span
          className={`block h-0.5 w-6 bg-blue-700 transition-all duration-300 ease-in-out ${
            isMobileMenuOpen ? '-rotate-45 -translate-y-2' : ''
          }`}
        />
      </button>

      {isMobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => setIsMobileMenuOpen(false)} />
      )}

      <aside
        className={`
          ${isOpen || isMobileMenuOpen ? 'w-64' : 'w-20'}
          bg-gradient-to-b from-slate-50 to-white border-r border-slate-200
          transition-all duration-300 overflow-y-auto shadow-sm
          fixed lg:sticky top-0 h-screen z-40
          ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className={`p-4 flex items-center ${isOpen || isMobileMenuOpen ? 'justify-between' : 'justify-center'} gap-2`}>
          {isOpen || isMobileMenuOpen ? (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white flex-shrink-0">
                <Building2 className="h-4 w-4" />
              </div>
              <span className="font-bold text-[10px] text-slate-800 tracking-tight leading-tight uppercase font-display">Company Intelligence Platform</span>
            </div>
          ) : (
            <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white flex-shrink-0">
              <Building2 className="h-5 w-5" />
            </div>
          )}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="hidden lg:block text-blue-700 hover:text-blue-900 transition-colors flex-shrink-0"
            aria-label={isOpen ? 'Collapse admin sidebar' : 'Expand admin sidebar'}
          >
            {isOpen ? <ChevronLeft className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
          </button>
        </div>

        <nav className="px-3 py-6">
          <ul className="space-y-2">
            {adminNavItems.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-700 hover:bg-blue-50 hover:text-blue-900 transition-colors duration-200 group touch-manipulation"
                >
                  <span className="text-blue-700 group-hover:text-blue-900">{item.icon}</span>
                  {(isOpen || isMobileMenuOpen) && <span className="font-medium text-sm">{item.label}</span>}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 sm:p-6 border-t border-slate-200 bg-gradient-to-t from-slate-50 to-transparent">
          {(isOpen || isMobileMenuOpen) && (
            <div className="text-xs text-slate-600">
              <p className="font-semibold mb-1">CIP Admin</p>
              <p>Placement Intelligence Control</p>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
