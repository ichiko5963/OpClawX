export const runtime = 'edge'

import { NextRequest } from 'next/server'
import { notificationManager } from '@/lib/notification-manager'
import { StreamEvent } from '@/types'
import logger, { createChildLogger } from '@/lib/logger'

const log = createChildLogger('SSEStream')

/**
 * GET /api/stream
 * Server-Sent Events endpoint for real-time task updates
 */
export async function GET(request: NextRequest): Promise<Response> {
  const { searchParams } = new URL(request.url)
  const taskId = searchParams.get('taskId') ?? undefined

  log.info({ taskId: taskId ?? 'all' }, 'New SSE connection')

  const encoder = new TextEncoder()
  let subscriberId: string | null = null

  const stream = new ReadableStream({
    start(controller) {
      // Send initial connection message
      controller.enqueue(
        encoder.encode(`event: connected\ndata: ${JSON.stringify({ taskId: taskId ?? null, timestamp: new Date().toISOString() })}\n\n`)
      )

      // Subscribe to notifications
      subscriberId = notificationManager.subscribe(
        (event: StreamEvent) => {
          try {
            const data = `event: ${event.type}\ndata: ${JSON.stringify({
              taskId: event.taskId,
              timestamp: event.timestamp.toISOString(),
              data: event.data,
            })}\n\n`
            controller.enqueue(encoder.encode(data))
          } catch (error) {
            log.error({ error, event }, 'Error sending SSE event')
          }
        },
        { taskId }
      )

      // Keep-alive ping every 30 seconds
      const pingInterval = setInterval(() => {
        try {
          controller.enqueue(encoder.encode(`event: ping\ndata: {}\n\n`))
        } catch {
          clearInterval(pingInterval)
        }
      }, 30000)

      // Cleanup on close
      request.signal.addEventListener('abort', () => {
        clearInterval(pingInterval)
        if (subscriberId) {
          notificationManager.unsubscribe(subscriberId)
        }
        log.info({ taskId: taskId ?? 'all', subscriberId }, 'SSE connection closed')
      })
    },

    cancel() {
      if (subscriberId) {
        notificationManager.unsubscribe(subscriberId)
      }
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
    },
  })
}
