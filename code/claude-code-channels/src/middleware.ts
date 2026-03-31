import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export const config = {
  matcher: ['/api/:path*'],
}

export function middleware(request: NextRequest): NextResponse | undefined {
  // Skip auth for webhooks and health checks
  const path = request.nextUrl.pathname
  if (
    path.startsWith('/api/webhooks/') ||
    path === '/api/health' ||
    path === '/api'
  ) {
    return undefined
  }

  // Optional API key auth
  const apiKey = process.env.API_KEY
  if (apiKey) {
    const authHeader = request.headers.get('authorization')
    const providedKey = authHeader?.replace('Bearer ', '')

    if (providedKey !== apiKey) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }
  }

  return undefined
}
