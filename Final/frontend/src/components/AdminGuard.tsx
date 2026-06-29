'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface AdminGuardProps {
  children: React.ReactNode;
}

export const AdminGuard: React.FC<AdminGuardProps> = ({ children }) => {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const authorize = async () => {
      try {
        const response = await fetch('/api/auth/session', { cache: 'no-store' });
        const session = await response.json();

        if (!isMounted) return;

        if (!session.authenticated) {
          router.push('/login');
          return;
        }

        if (session.role !== 'admin') {
          router.push('/');
          return;
        }

        setReady(true);
      } catch {
        if (isMounted) {
          router.push('/login');
        }
      }
    };

    authorize();

    return () => {
      isMounted = false;
    };
  }, [router]);

  if (!ready) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 text-white flex items-center justify-center mx-auto mb-4 shadow-lg animate-pulse">
            <span className="text-2xl font-bold">ADM</span>
          </div>
          <p className="text-slate-600">Authorizing admin access...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
