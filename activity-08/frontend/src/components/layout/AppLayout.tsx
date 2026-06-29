import { ReactNode, useState } from 'react';
import { AppSidebar } from './AppSidebar';
import { FloatingChatbot } from './FloatingChatbot';

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <AppSidebar collapsed={collapsed} setCollapsed={setCollapsed} />
      <main className={`min-h-screen transition-all duration-300 ${collapsed ? 'ml-[80px]' : 'ml-[280px]'}`}>
        <div className="p-8">
          {children}
        </div>
      </main>

      {/* Global Floating Copilot Chatbot */}
      <FloatingChatbot />
    </div>
  );
}

