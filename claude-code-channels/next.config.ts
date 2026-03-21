import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',
  experimental: {
    serverComponentsExternalPackages: ['discord.js', 'bull', 'ioredis', '@anthropic-ai/sdk'],
  },
  async headers() {
    return [
      {
        source: '/api/stream/:path*',
        headers: [
          {
            key: 'Content-Type',
            value: 'text/event-stream',
          },
          {
            key: 'Cache-Control',
            value: 'no-cache, no-transform',
          },
          {
            key: 'Connection',
            value: 'keep-alive',
          },
        ],
      },
    ]
  },
}

export default nextConfig
