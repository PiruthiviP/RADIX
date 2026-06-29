// ====================================================================
// RADIX Enterprise Auth & Credential Validation Context
// Place in: activity-08/frontend/src/context/AuthContext.tsx
// ====================================================================

import React, { createContext, useContext, useState } from 'react';

export type UserRole = 'Admin' | 'Student' | 'Recruiter' | 'Guest';

export interface UserContextType {
  id: string;
  name: string;
  email: string;
  role: UserRole;
}

interface AuthContextProps {
  user: UserContextType | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  loginGuest: () => void;
  setRole: (role: UserRole) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserContextType | null>(() => {
    const saved = localStorage.getItem('radix_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);

  const userMap: Record<UserRole, UserContextType> = {
    Admin: {
      id: 'admin_usr_01',
      name: 'Faculty Placement Officer',
      email: 'placement.officer@srm.edu.in',
      role: 'Admin',
    },
    Student: {
      id: 'student_usr_02',
      name: 'Piruthivi (Candidate)',
      email: 'piruthivi.s@srm.edu.in',
      role: 'Student',
    },
    Recruiter: {
      id: 'recruiter_usr_03',
      name: 'Google Campus Recruiter',
      email: 'recruiter@google.com',
      role: 'Recruiter',
    },
    Guest: {
      id: 'guest_visitor',
      name: 'Unverified Guest',
      email: 'visitor@guest.srm.edu',
      role: 'Guest',
    },
  };

  const login = async (username: string, parsePassword: string): Promise<boolean> => {
    setLoading(true);
    // Simulate slight authentication request latency
    await new Promise((resolve) => setTimeout(resolve, 600));

    const uname = username.trim().toLowerCase();
    let authenticatedUser: UserContextType | null = null;

    if (uname === 'admin' && parsePassword === 'admin123') {
      authenticatedUser = userMap.Admin;
    } else if (uname === 'student' && parsePassword === 'student123') {
      authenticatedUser = userMap.Student;
    } else if (uname === 'recruiter' && parsePassword === 'recruiter123') {
      authenticatedUser = userMap.Recruiter;
    }

    setLoading(false);

    if (authenticatedUser) {
      setUser(authenticatedUser);
      localStorage.setItem('radix_user', JSON.stringify(authenticatedUser));
      localStorage.setItem('radix_role', authenticatedUser.role);
      return true;
    }

    return false;
  };

  const loginGuest = () => {
    const guestUser = userMap.Guest;
    setUser(guestUser);
    localStorage.setItem('radix_user', JSON.stringify(guestUser));
    localStorage.setItem('radix_role', guestUser.role);
  };

  const setRole = (newRole: UserRole) => {
    setLoading(true);
    const targetUser = userMap[newRole];
    setUser(targetUser);
    localStorage.setItem('radix_user', JSON.stringify(targetUser));
    localStorage.setItem('radix_role', newRole);
    setTimeout(() => {
      setLoading(false);
    }, 150);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('radix_user');
    localStorage.removeItem('radix_role');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, loginGuest, setRole, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside an AuthProvider component');
  }
  return context;
};

