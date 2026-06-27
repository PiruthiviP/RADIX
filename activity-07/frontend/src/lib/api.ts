const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchApi(path: string, options?: RequestInit) {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  if (!response.ok) {
    const errText = await response.text();
    throw new Error(errText || `API error: ${response.statusText}`);
  }
  return response.json();
}
