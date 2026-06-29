import { NextRequest, NextResponse } from 'next/server';
import { parseSessionToken, SESSION_COOKIE_NAME } from '@/lib/auth-session';

export async function GET(request: NextRequest) {
  const token = request.cookies.get(SESSION_COOKIE_NAME)?.value;
  const session = await parseSessionToken(token);

  if (!session) {
    return NextResponse.json({ authenticated: false, role: null, email: null });
  }

  return NextResponse.json({
    authenticated: true,
    role: session.role,
    email: session.email,
    exp: session.exp,
  });
}
