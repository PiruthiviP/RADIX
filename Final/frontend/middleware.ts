import { NextRequest, NextResponse } from 'next/server';
import { parseSessionToken, SESSION_COOKIE_NAME } from '@/lib/auth-session';

const PUBLIC_PATHS = new Set(['/login']);

const isStaticAsset = (pathname: string): boolean => {
  return (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/logos') ||
    pathname === '/favicon.ico' ||
    pathname.endsWith('.png') ||
    pathname.endsWith('.jpg') ||
    pathname.endsWith('.jpeg') ||
    pathname.endsWith('.svg') ||
    pathname.endsWith('.webp') ||
    pathname.endsWith('.gif') ||
    pathname.endsWith('.ico') ||
    pathname.endsWith('.css') ||
    pathname.endsWith('.js') ||
    pathname.endsWith('.map')
  );
};

const withSecurityHeaders = (response: NextResponse): NextResponse => {
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  response.headers.set('Cross-Origin-Opener-Policy', 'same-origin');
  return response;
};

export async function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  if (pathname.startsWith('/api/auth') || isStaticAsset(pathname)) {
    return withSecurityHeaders(NextResponse.next());
  }

  const token = request.cookies.get(SESSION_COOKIE_NAME)?.value;
  const session = await parseSessionToken(token);

  if (PUBLIC_PATHS.has(pathname)) {
    if (session) {
      const target = session.role === 'admin' ? '/admin' : '/';
      return withSecurityHeaders(NextResponse.redirect(new URL(target, request.url)));
    }
    return withSecurityHeaders(NextResponse.next());
  }

  if (!session) {
    const redirectTo = `/login?next=${encodeURIComponent(`${pathname}${search}`)}`;
    return withSecurityHeaders(NextResponse.redirect(new URL(redirectTo, request.url)));
  }

  if (pathname.startsWith('/admin') && session.role !== 'admin') {
    const response = NextResponse.redirect(new URL('/login?error=restricted', request.url));
    response.cookies.delete(SESSION_COOKIE_NAME);
    return withSecurityHeaders(response);
  }

  // Restrict guest and recruiter roles from accessing analytics, chatbot, or semantic-search URLs
  const isRestrictedPath = pathname.startsWith('/analytics') || pathname.startsWith('/chatbot') || pathname.startsWith('/semantic-search');
  if (isRestrictedPath && (session.role === 'recruiter' || session.role === 'guest')) {
    const response = NextResponse.redirect(new URL('/login?error=restricted', request.url));
    response.cookies.delete(SESSION_COOKIE_NAME);
    return withSecurityHeaders(response);
  }

  return withSecurityHeaders(NextResponse.next());
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image).*)'],
};
