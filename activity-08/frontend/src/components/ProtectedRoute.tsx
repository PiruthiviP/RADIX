// ====================================================================
// RADIX URL-Level Access Guard (ProtectedRoute with Strict Redirection)
// Place in: activity-08/frontend/src/components/ProtectedRoute.tsx
// ====================================================================

import React, { useEffect } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth, UserRole } from '../context/AuthContext';
import { toast } from 'sonner';

interface ProtectedRouteProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles, children }) => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  const userRole = user?.role || 'Guest';
  const isAuthorized = allowedRoles.includes(userRole);

  useEffect(() => {
    if (!loading) {
      if (!user) {
        navigate('/login', { replace: true });
      } else if (!isAuthorized) {
        toast.error(`Access Denied: Your role (${userRole}) is restricted from accessing this URL path.`);
        navigate('/', { replace: true });
      }
    }
  }, [user, userRole, loading, isAuthorized, navigate]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <div className="w-12 h-12 border-4 border-t-primary border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
        <p className="text-muted-foreground animate-pulse text-sm">Verifying URL access permissions...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!isAuthorized) {
    return null; // Handled by the redirect hook
  }

  return <>{children}</>;
};

export default ProtectedRoute;

