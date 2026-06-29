export type UserRole = 'student' | 'admin' | 'recruiter' | 'guest';

export interface SessionPayload {
  email: string;
  role: UserRole;
  iat: number;
  exp: number;
}

export const SESSION_COOKIE_NAME = 'srm_session';
export const SESSION_TTL_SECONDS = 60 * 60 * 8;

const encoder = new TextEncoder();

const getAuthSecret = (): string => {
  const fromEnv = process.env.AUTH_SECRET?.trim();
  if (fromEnv) return fromEnv;
  return 'dev-auth-secret-change-me';
};

const toBase64Url = (value: string): string => {
  const bytes = encoder.encode(value);
  let binary = '';
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
};

const fromBase64Url = (value: string): string => {
  const padded = value.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(value.length / 4) * 4, '=');
  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new TextDecoder().decode(bytes);
};

const toHex = (bytes: Uint8Array): string => {
  return Array.from(bytes)
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
};

const signingKey = async (): Promise<CryptoKey> => {
  return crypto.subtle.importKey(
    'raw',
    encoder.encode(getAuthSecret()),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign', 'verify']
  );
};

const sign = async (value: string): Promise<string> => {
  const key = await signingKey();
  const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(value));
  return toHex(new Uint8Array(signature));
};

export const createSessionToken = async (email: string, role: UserRole): Promise<string> => {
  const now = Math.floor(Date.now() / 1000);
  const payload: SessionPayload = {
    email,
    role,
    iat: now,
    exp: now + SESSION_TTL_SECONDS,
  };
  const payloadEncoded = toBase64Url(JSON.stringify(payload));
  const signature = await sign(payloadEncoded);
  return `${payloadEncoded}.${signature}`;
};

export const parseSessionToken = async (token?: string): Promise<SessionPayload | null> => {
  if (!token) return null;

  const [payloadEncoded, signature] = token.split('.');
  if (!payloadEncoded || !signature) return null;

  const expectedSignature = await sign(payloadEncoded);
  if (signature !== expectedSignature) return null;

  try {
    const parsed = JSON.parse(fromBase64Url(payloadEncoded)) as SessionPayload;
    if (!parsed?.email || !parsed?.role || !parsed?.exp) return null;
    if (parsed.exp <= Math.floor(Date.now() / 1000)) return null;
    if (parsed.role !== 'student' && parsed.role !== 'admin' && parsed.role !== 'recruiter' && parsed.role !== 'guest') return null;
    return parsed;
  } catch {
    return null;
  }
};
