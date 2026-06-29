'use client';

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: GlobalErrorProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center px-4">
      <div className="max-w-lg w-full bg-white border border-slate-200 rounded-xl p-6 shadow-sm text-center space-y-4">
        <h1 className="text-2xl font-bold text-slate-900">Something went wrong</h1>
        <p className="text-sm text-slate-600">
          We hit an unexpected error while rendering this page. You can retry now.
        </p>
        {error?.digest && (
          <p className="text-xs text-slate-500">Reference: {error.digest}</p>
        )}
        <button
          onClick={reset}
          className="px-5 py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}
