export default function GlobalLoading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center px-4">
      <div className="text-center">
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 text-white flex items-center justify-center mx-auto mb-4 shadow-lg animate-pulse">
          <span className="text-2xl font-bold">SRM</span>
        </div>
        <p className="text-slate-700 font-medium">Loading workspace...</p>
      </div>
    </div>
  );
}
