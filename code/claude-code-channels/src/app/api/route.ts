export async function GET(): Promise<Response> {
  return Response.json({
    name: 'Claude Code Channels API',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      'GET /api/health': 'Health check',
      'POST /api/webhooks/discord': 'Discord webhook endpoint',
      'POST /api/webhooks/telegram': 'Telegram webhook endpoint',
      'GET /api/tasks': 'List tasks',
      'POST /api/tasks': 'Create task',
      'GET /api/tasks/:id': 'Get task details',
      'DELETE /api/tasks/:id': 'Cancel/delete task',
      'GET /api/stream': 'SSE stream for real-time updates',
      'GET /api/stats': 'Dashboard statistics',
    },
  })
}
