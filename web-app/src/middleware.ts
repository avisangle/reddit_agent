import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PROTECTED_PATHS = ['/admin/dashboard', '/admin/settings', '/workflow'];
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export async function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Redirect root to admin dashboard
    if (pathname === '/') {
        return NextResponse.redirect(new URL('/admin/dashboard', request.url));
    }

    // Check if path is protected
    if (PROTECTED_PATHS.some(path => pathname.startsWith(path))) {
        // Get session cookie
        const sessionCookie = request.cookies.get('admin_session');

        if (!sessionCookie) {
            // No session cookie -> Redirect to login
            console.log(`[Middleware] No session cookie, redirecting to /login from ${pathname}`);
            return NextResponse.redirect(new URL('/login', request.url));
        }

        // Validate session with backend
        try {
            const response = await fetch(`${API_BASE}/admin/api/check-auth`, {
                headers: {
                    'Cookie': `admin_session=${sessionCookie.value}`
                },
                credentials: 'include'
            });

            if (!response.ok) {
                // Invalid session -> Redirect to login
                console.log(`[Middleware] Invalid session (status ${response.status}), redirecting to /login`);
                return NextResponse.redirect(new URL('/login', request.url));
            }

            // Session valid - allow request to proceed
            console.log(`[Middleware] Session valid, allowing access to ${pathname}`);
        } catch (error) {
            // Backend unreachable -> Redirect to login
            console.error('[Middleware] Backend unreachable:', error);
            return NextResponse.redirect(new URL('/login', request.url));
        }
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/', '/admin/:path*', '/workflow/:path*']
};
