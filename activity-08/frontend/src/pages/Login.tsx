// ====================================================================
// RADIX Premium Portal Login Page
// Place in: activity-08/frontend/src/pages/Login.tsx
// ====================================================================

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, KeyRound, User, Briefcase, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const Login: React.FC = () => {
  const { login, loginGuest } = useAuth();
  const navigate = useNavigate();
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!username.trim() || !password.trim()) {
      setError('Please fill in all credential fields.');
      return;
    }

    setLoading(true);
    try {
      const success = await login(username, password);
      if (success) {
        navigate('/');
      } else {
        setError('Invalid username or password. Review suggestions below.');
      }
    } catch (err) {
      setError('An error occurred during authentication.');
    } finally {
      setLoading(false);
    }
  };

  const handleGuestLogin = () => {
    loginGuest();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#0b0c10] flex items-center justify-center p-4 relative overflow-hidden font-display">
      {/* Dynamic Background Blurs */}
      <div className="absolute top-1/4 left-1/4 w-[350px] h-[350px] bg-primary/10 rounded-full blur-[100px] animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-[350px] h-[350px] bg-indigo-500/10 rounded-full blur-[100px] animate-pulse delay-700"></div>

      <div className="w-full max-w-md bg-card/40 backdrop-blur-xl border border-border/80 shadow-2xl rounded-3xl p-8 space-y-8 relative z-10">
        
        {/* Header Title */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 bg-gradient-to-tr from-primary to-indigo-500 text-primary-foreground rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-primary/20">
            <KeyRound className="w-6 h-6" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            SRM Placements
          </h1>
          <p className="text-xs text-muted-foreground uppercase tracking-widest font-mono">
            Corporate Intelligence Exchange
          </p>
        </div>

        {/* Error Alert Panel */}
        {error && (
          <div className="flex items-start gap-2 p-3.5 bg-destructive/10 border border-destructive/20 rounded-xl text-destructive text-sm animate-in fade-in duration-200">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <p>{error}</p>
          </div>
        )}

        {/* Credentials Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Username</label>
            <div className="relative">
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. admin, student, recruiter"
                className="w-full bg-[#14151b] border border-border hover:border-border/100 focus:border-primary/50 text-slate-100 px-4 py-3 pl-10 rounded-xl text-sm focus:outline-none transition-all duration-300 placeholder:text-muted-foreground/60"
              />
              <User className="absolute left-3.5 top-3.5 w-4.5 h-4.5 text-muted-foreground" />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-[#14151b] border border-border hover:border-border/100 focus:border-primary/50 text-slate-100 px-4 py-3 pl-10 pr-10 rounded-xl text-sm focus:outline-none transition-all duration-300 placeholder:text-muted-foreground/60"
              />
              <KeyRound className="absolute left-3.5 top-3.5 w-4.5 h-4.5 text-muted-foreground" />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-3.5 text-muted-foreground hover:text-foreground"
              >
                {showPassword ? <EyeOff className="w-4.5 h-4.5" /> : <Eye className="w-4.5 h-4.5" />}
              </button>
            </div>
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full py-6 rounded-xl font-bold bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/20 transition-all duration-300 flex items-center justify-center gap-2"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-t-transparent border-white rounded-full animate-spin"></div>
            ) : (
              'Sign In'
            )}
          </Button>
        </form>

        {/* Continue as Guest */}
        <div className="text-center">
          <button
            onClick={handleGuestLogin}
            className="text-xs font-medium text-muted-foreground hover:text-primary transition-colors duration-200"
          >
            Browse system as Guest
          </button>
        </div>

        {/* suggested Credentials help */}
        <div className="border-t border-border/60 pt-5 space-y-3">
          <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest text-center">
            Suggested Logins
          </h4>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => {
                setUsername('admin');
                setPassword('admin123');
              }}
              className="p-2 border border-rose-500/20 bg-rose-500/5 hover:bg-rose-500/10 rounded-xl text-center transition-all duration-200"
            >
              <Shield className="w-4 h-4 text-rose-500 mx-auto mb-1" />
              <p className="text-[10px] font-bold text-foreground">Admin</p>
              <p className="text-[8px] text-muted-foreground font-mono mt-0.5">admin123</p>
            </button>

            <button
              onClick={() => {
                setUsername('student');
                setPassword('student123');
              }}
              className="p-2 border border-indigo-500/20 bg-indigo-500/5 hover:bg-indigo-500/10 rounded-xl text-center transition-all duration-200"
            >
              <User className="w-4 h-4 text-indigo-500 mx-auto mb-1" />
              <p className="text-[10px] font-bold text-foreground">Student</p>
              <p className="text-[8px] text-muted-foreground font-mono mt-0.5">student123</p>
            </button>

            <button
              onClick={() => {
                setUsername('recruiter');
                setPassword('recruiter123');
              }}
              className="p-2 border border-amber-500/20 bg-amber-500/5 hover:bg-amber-500/10 rounded-xl text-center transition-all duration-200"
            >
              <Briefcase className="w-4 h-4 text-amber-500 mx-auto mb-1" />
              <p className="text-[10px] font-bold text-foreground">Recruiter</p>
              <p className="text-[8px] text-muted-foreground font-mono mt-0.5">recruiter123</p>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
export default Login;
