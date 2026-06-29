import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center px-4">
      <div className="max-w-lg w-full bg-white border border-slate-200 rounded-xl p-6 shadow-sm text-center space-y-4">
        <h1 className="text-3xl font-bold text-slate-900">404</h1>
        <p className="text-sm text-slate-600">The page you are looking for does not exist.</p>
        <Link
          href="/"
          className="inline-flex px-5 py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
