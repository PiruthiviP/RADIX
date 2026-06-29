import React from 'react';
import Image from 'next/image';
import { Sidebar } from './Sidebar';
import { UserAccountBadge } from './UserAccountBadge';
import { FloatingChatbot } from './FloatingChatbot';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex bg-slate-50 min-h-screen">
      {/* Mobile Top Bar */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b border-slate-200 shadow-sm z-[9998] flex items-center justify-center px-20 gap-2">
        <div className="w-7 h-7 rounded bg-blue-600 flex items-center justify-center text-white flex-shrink-0">
          <span className="font-extrabold text-xs">C</span>
        </div>
        <span className="font-bold text-xs text-slate-800 uppercase tracking-wider font-display">Company Intelligence</span>
      </div>
      
      <Sidebar />
      <main className="flex-1 overflow-auto w-full pt-16 lg:pt-0">
        {children}
      </main>
      <UserAccountBadge />
      <FloatingChatbot />
    </div>
  );
};
