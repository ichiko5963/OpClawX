export async function GET(): Promise<Response> {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV,
    version: process.env.npm_package_version ?? '1.0.0',
  }

  return Response.json(health)
}
