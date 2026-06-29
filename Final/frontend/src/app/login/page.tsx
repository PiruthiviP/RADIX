'use client';

import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, ShieldAlert, Sparkles, Building2, KeyRound, User, Lock, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [shouldShake, setShouldShake] = useState(false);

  // Check if already logged in or if restricted query param is active
  useEffect(() => {
    let isMounted = true;

    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('error') === 'restricted') {
        setError('Access Denied: You tried to access a restricted section and have been automatically signed out.');
      }
    }

    const checkSession = async () => {
      try {
        const response = await fetch('/api/auth/session', { cache: 'no-store' });
        const session = await response.json();
        if (!isMounted) return;

        if (session.authenticated) {
          localStorage.setItem('radix_user', JSON.stringify({
            role: session.role.charAt(0).toUpperCase() + session.role.slice(1),
            email: session.email
          }));
          router.push(session.role === 'admin' ? '/admin' : '/');
          return;
        }
      } catch {
        // Fall through
      } finally {
        if (isMounted) {
          setIsChecking(false);
        }
      }
    };

    checkSession();
    return () => {
      isMounted = false;
    };
  }, [router]);

  // Trigger shake on login failures
  useEffect(() => {
    if (error) {
      setShouldShake(true);
      const timer = setTimeout(() => setShouldShake(false), 500);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!email) {
      setError('Username is required');
      setIsLoading(false);
      return;
    }

    if (!password) {
      setError('Password is required');
      setIsLoading(false);
      return;
    }

    const netId = email.split('@')[0].toLowerCase();

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ netId, password }),
      });

      const result = await response.json();

      if (!response.ok || !result.authenticated) {
        setError(result.error || 'Invalid NetID or password');
        setIsLoading(false);
        return;
      }

      localStorage.setItem('radix_user', JSON.stringify({
        role: result.role.charAt(0).toUpperCase() + result.role.slice(1),
        email: result.email
      }));

      router.push(result.role === 'admin' ? '/admin' : '/');
    } catch {
      setError('Unable to sign in right now. Please try again.');
      setIsLoading(false);
    }
  };

  // UX Autofill helper
  const handleAutofill = (userVal: string, passVal: string) => {
    setEmail(userVal);
    setPassword(passVal);
    setError('');
  };

  return (
    <div className="min-h-screen lg:h-screen bg-slate-950 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.15),rgba(255,255,255,0))] flex flex-col relative text-slate-100 overflow-x-hidden selection:bg-blue-600/35 selection:text-blue-100">

      {/* CSS Shaking keyframe declaration */}
      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-6px); }
          20%, 40%, 60%, 80% { transform: translateX(6px); }
        }
        .animate-shake {
          animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
        }
      `}</style>

      {isChecking ? (
        <div className="flex items-center justify-center min-h-screen flex-1">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center mx-auto shadow-2xl animate-pulse">
              <Building2 className="w-8 h-8" />
            </div>
            <p className="text-slate-400 font-semibold tracking-wider text-xs uppercase animate-pulse">Establishing Secure Session...</p>
          </div>
        </div>
      ) : (
        <>
          <div className="flex-1 flex flex-col lg:flex-row lg:overflow-hidden relative">

            {/* Left Section - Hero Brand Panel */}
            <div className="hidden lg:flex lg:w-1/2 lg:h-full flex-col justify-between p-12 relative overflow-y-auto border-r border-slate-900 bg-slate-950/40 backdrop-blur-md">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg border border-blue-400/20">
                  <Building2 className="w-5.5 h-5.5" />
                </div>
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent uppercase font-display">Company Intelligence Platform</span>
              </div>

              <div className="my-auto max-w-lg space-y-6 pt-16">
                <div className="space-y-2">
                  <p className="text-blue-500 font-bold text-xs uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-yellow-400" /> Radix RAG & Analytics
                  </p>
                  <h1 className="text-4xl font-extrabold tracking-tight text-white leading-none">
                    Unlocking Placement intelligence.
                  </h1>
                  <p className="text-slate-400 text-sm leading-relaxed pt-2">
                    Review interview round logs, evaluate focused skillsets, analyze YoY growth analytics, and search semantic vectors to navigate your placement pipeline.
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="flex items-start gap-4 p-3.5 rounded-xl bg-slate-900/35 border border-slate-900 hover:border-slate-800 transition-all group">
                    <div className="w-10 h-10 rounded-lg bg-blue-950/40 text-blue-400 border border-blue-900/35 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                      <span>🏢</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-200 text-sm">Deep Directory profiles</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Explore parameters across hundreds of hiring organizations</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4 p-3.5 rounded-xl bg-slate-900/35 border border-slate-900 hover:border-slate-800 transition-all group">
                    <div className="w-10 h-10 rounded-lg bg-indigo-950/40 text-indigo-400 border border-indigo-900/35 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                      <span>📋</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-200 text-sm">Orchestrated Hiring Tracks</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Prepare with stage-by-stage logs and interview experiences</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4 p-3.5 rounded-xl bg-slate-900/35 border border-slate-900 hover:border-slate-800 transition-all group">
                    <div className="w-10 h-10 rounded-lg bg-violet-950/40 text-violet-400 border border-violet-900/35 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                      <span>🤖</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-200 text-sm">Multi-Model LLM RAG chatbot</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Get immediate answers grounded directly on placement facts</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-red-950/20 rounded-xl border border-red-900/35 text-xs text-red-300 max-w-lg mt-8">
                <span className="font-bold flex items-center gap-1.5 text-red-400 mb-1">
                  <ShieldAlert className="w-4 h-4 text-red-500 animate-pulse" />

                </span>

              </div>
            </div>

            {/* Right Section - Glassmorphic Form Card */}
            <div className="w-full lg:w-1/2 lg:h-full flex items-center justify-center py-10 px-4 sm:px-6 lg:px-8 overflow-y-auto">
              <div
                className={`w-full max-w-md bg-slate-900/35 backdrop-blur-xl rounded-2xl border border-slate-850 p-6 sm:p-8 shadow-2xl flex flex-col justify-between transition-all duration-300 ${shouldShake ? 'animate-shake border-red-500/50 shadow-red-950/20' : ''
                  }`}
              >
                {/* Mobile Top Bar */}
                <div className="mb-6 text-center">
                  <div className="flex justify-center gap-2.5 mb-4 lg:hidden items-center">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow">
                      <Building2 className="w-4.5 h-4.5" />
                    </div>
                    <span className="font-extrabold text-sm text-slate-100 tracking-tight uppercase">Company Intelligence</span>
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Welcome Back</h2>
                  <p className="text-xs text-slate-400 mt-1">Provide placement portal credentials to log in.</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-4">
                  {/* Alert Error Box */}
                  {error && (
                    <div className="p-3 bg-red-950/30 border border-red-900/50 text-red-300 rounded-lg text-xs flex items-start gap-2 animate-pulse">
                      <ShieldAlert className="w-4.5 h-4.5 text-red-500 flex-shrink-0 mt-0.5" />
                      <p className="font-semibold">{error}</p>
                    </div>
                  )}

                  {/* NetID Field */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300 tracking-wide block">
                      NetID / Username
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-blue-500 transition-colors">
                        <User className="h-4 w-4" />
                      </div>
                      <input
                        type="text"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="admin, student, recruiter..."
                        className="w-full pl-10 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-900/30 outline-none text-slate-100 text-sm transition-all placeholder:text-slate-600"
                        required
                      />
                    </div>
                  </div>

                  {/* Password Field */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-300 tracking-wide block">
                      Password
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-blue-500 transition-colors">
                        <Lock className="h-4 w-4" />
                      </div>
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter password"
                        className="w-full pl-10 pr-10 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-900/30 outline-none text-slate-100 text-sm transition-all placeholder:text-slate-600"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                      >
                        {showPassword ? <EyeOff className="h-4.5 w-4.5" /> : <Eye className="h-4.5 w-4.5" />}
                      </button>
                    </div>
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full py-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 hover:from-blue-500 hover:via-indigo-500 hover:to-violet-500 text-white text-sm font-bold rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-blue-500/10 hover:scale-[1.02]"
                  >
                    {isLoading ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 className="w-4.5 h-4.5 animate-spin" />
                        Authenticating credentials...
                      </span>
                    ) : (
                      'Log In'
                    )}
                  </button>
                </form>

                {/* Clickable Quick-Autofill Badges */}
                <div className="mt-8 border-t border-slate-850 pt-5 space-y-3">
                  <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                    <KeyRound className="w-3.5 h-3.5" />
                    Quick Role Access (Click to autofill)
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => handleAutofill('admin', 'admin123')}
                      className="px-3 py-2 text-left rounded-xl bg-slate-950 border border-slate-900 hover:border-blue-500/50 hover:bg-slate-900/30 transition-all text-xs space-y-0.5 group"
                    >
                      <p className="font-extrabold text-slate-300 group-hover:text-blue-400">Admin</p>
                      <p className="text-[10px] text-slate-500 font-mono">admin / admin123</p>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleAutofill('student', 'student123')}
                      className="px-3 py-2 text-left rounded-xl bg-slate-950 border border-slate-900 hover:border-emerald-500/50 hover:bg-slate-900/30 transition-all text-xs space-y-0.5 group"
                    >
                      <p className="font-extrabold text-slate-300 group-hover:text-emerald-400">Student</p>
                      <p className="text-[10px] text-slate-500 font-mono">student / student123</p>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleAutofill('recruiter', 'recruiter123')}
                      className="px-3 py-2 text-left rounded-xl bg-slate-950 border border-slate-900 hover:border-indigo-500/50 hover:bg-slate-900/30 transition-all text-xs space-y-0.5 group"
                    >
                      <p className="font-extrabold text-slate-300 group-hover:text-indigo-400">Recruiter</p>
                      <p className="text-[10px] text-slate-500 font-mono">recruiter / recruiter123</p>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleAutofill('guest', 'guest123')}
                      className="px-3 py-2 text-left rounded-xl bg-slate-950 border border-slate-900 hover:border-amber-500/50 hover:bg-slate-900/30 transition-all text-xs space-y-0.5 group"
                    >
                      <p className="font-extrabold text-slate-300 group-hover:text-amber-400">Guest</p>
                      <p className="text-[10px] text-slate-500 font-mono">guest / guest123</p>
                    </button>
                  </div>
                </div>

              </div>
            </div>

          </div>

          {/* Frosty footer */}
          <div className="bg-slate-950/60 backdrop-blur-sm border-t border-slate-900 py-3 text-center">
            <p className="text-[10px] text-slate-600 font-medium">© 2026 Company Intelligence Platform. Secured access environment.</p>
          </div>
        </>
      )}
    </div>
  );
}
