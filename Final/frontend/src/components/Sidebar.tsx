import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {
  BarChart3,
  Building2,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  Lightbulb,
  Target,
  Sparkles,
  Search,
} from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

export const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [role, setRole] = useState<string>('guest');

  // Fetch active session role
  useEffect(() => {
    let isMounted = true;
    fetch('/api/auth/session')
      .then((res) => res.json())
      .then((data) => {
        if (isMounted && data.authenticated && data.role) {
          setRole(data.role.toLowerCase());
        }
      })
      .catch((err) => console.error('Error fetching session in sidebar:', err));

    return () => {
      isMounted = false;
    };
  }, []);

  // Filter navigation links depending on active role permissions
  const getNavItems = (): NavItem[] => {
    const baseItems: NavItem[] = [
      { label: 'Dashboard', href: '/', icon: <LayoutDashboard className="h-5 w-5" /> },
      { label: 'Companies', href: '/companies', icon: <Building2 className="h-5 w-5" /> },
    ];

    const restrictedItems: NavItem[] = [
      { label: 'Skill Set Analytics', href: '/analytics', icon: <BarChart3 className="h-5 w-5" /> },
      { label: 'Semantic Search', href: '/semantic-search', icon: <Search className="h-5 w-5" /> },
    ];

    const generalItems: NavItem[] = [
      { label: 'Hiring Rounds', href: '/hiring-rounds', icon: <Target className="h-5 w-5" /> },
      { label: 'InnovX', href: '/innovx', icon: <Sparkles className="h-5 w-5" /> },
    ];

    // Recruiter and Guest are blocked from Analytics and Semantic Search
    if (role === 'recruiter' || role === 'guest') {
      return [...baseItems, ...generalItems];
    }

    // Student and Admin have full access
    return [...baseItems, ...restrictedItems, ...generalItems];
  };

  const navItems = getNavItems();

  // Close mobile menu on resize to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setIsMobileMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Prevent body scroll when mobile menu is open
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
      {/* Mobile Menu Button - Classic Burger */}
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="lg:hidden fixed top-2 left-4 z-[9999] w-12 h-12 rounded-lg bg-white border-2 border-slate-200 hover:bg-slate-50 shadow-lg hover:shadow-xl transition-all duration-300 flex flex-col items-center justify-center gap-1.5"
        aria-label="Toggle menu"
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

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          ${isOpen || isMobileMenuOpen ? 'w-64' : 'w-20'} 
          bg-gradient-to-b from-slate-50 to-white border-r border-slate-200 
          transition-all duration-300 overflow-y-auto shadow-sm
          
          /* Mobile: Slide-in overlay */
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
            aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {isOpen ? <ChevronLeft className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
          </button>
        </div>

        <nav className="px-3 py-6">
          <ul className="space-y-2">
            {navItems.map((item) => (
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
              <p className="font-semibold mb-1">Company Intelligence Platform</p>
              <p>Enterprise Analytics Stack</p>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
