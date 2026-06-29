// ====================================================================
// RADIX API Fetch Client for Next.js Application
// Place in: Final/frontend/src/lib/api.ts
// ====================================================================

// In Next.js, we use relative paths so Nginx proxies /api/ requests to the backend.
const API_BASE = '';

export async function fetchApi(path: string, options?: RequestInit) {
  const url = `${API_BASE}${path}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Merge any custom headers passed in options
  if (options?.headers) {
    Object.assign(headers, options.headers);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errText = await response.text();
    let parsedErr = errText;
    try {
      const jsonErr = JSON.parse(errText);
      parsedErr = jsonErr.detail || errText;
    } catch {
      // Fallback
    }
    throw new Error(parsedErr || `API error: ${response.statusText}`);
  }
  return response.json();
}
