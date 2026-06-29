// ====================================================================
// RADIX API Fetch Client with Automatic RBAC Headers Injection
// Place in: activity-08/frontend/src/lib/api.ts
// ====================================================================

// Default to relative paths so Nginx/Vite proxy maps calls to the backend
const API_BASE = import.meta.env.VITE_API_URL || '';

export async function fetchApi(path: string, options?: RequestInit) {
  const url = `${API_BASE}${path}`;
  
  // Retrieve the active user session from local storage to inject RBAC headers
  const savedUser = localStorage.getItem('radix_user');
  const user = savedUser ? JSON.parse(savedUser) : null;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (user) {
    // Inject headers parsed by backend auth_guards
    headers['X-User-Role'] = user.role;
    headers['X-User-Email'] = user.email;
  }

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
      // Try parsing json error payload
      const jsonErr = JSON.parse(errText);
      parsedErr = jsonErr.detail || errText;
    } catch {
      // Fallback to text
    }
    throw new Error(parsedErr || `API error: ${response.statusText}`);
  }
  return response.json();
}

