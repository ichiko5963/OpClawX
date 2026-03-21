import { NextRequest } from 'next/server'
import { telegramBot } from '@/lib/bots/telegram'
import logger, { createChildLogger } from '@/lib/logger'

const log = createChildLogger('TelegramWebhook')

/**
 * Handle Telegram webhook updates
 */
export async function POST(request: NextRequest): Promise<Response> {
  const secretToken = request.headers.get('x-telegram-bot-api-secret-token')

  // Optional: Verify secret token if configured
  const expectedToken = process.env.WEBHOOK_SECRET
  if (expectedToken && secretToken !== expectedToken) {
    log.warn('Invalid webhook secret token')
    return new Response('Unauthorized', { status: 401 })
  }

  try {
    const update = await request.json()

    log.debug({ updateId: update.update_id }, 'Received Telegram update')

    // Pass to Telegram bot handler
    await telegramBot.handleWebhook(update)

    return new Response('OK', { status: 200 })
  } catch (error) {
    log.error({ error }, 'Error handling Telegram webhook')
    return new Response('Internal Server Error', { status: 500 })
  }
}

/**
 * Set up webhook (called during deployment)
 */
export async function GET(request: NextRequest): Promise<Response> {
  const { searchParams } = new URL(request.url)
  const action = searchParams.get('action')

  if (action === 'setup') {
    try {
      const webhookUrl = `${process.env.APP_URL}/api/webhooks/telegram`
      const secretToken = process.env.WEBHOOK_SECRET

      // Initialize bot and set webhook
      await telegramBot.start()

      log.info({ webhookUrl }, 'Telegram webhook configured')

      return Response.json({
        success: true,
        webhookUrl,
        message: 'Webhook configured successfully',
      })
    } catch (error) {
      log.error({ error }, 'Failed to setup Telegram webhook')
      return Response.json(
        { success: false, error: String(error) },
        { status: 500 }
      )
    }
  }

  return Response.json({
    status: 'Telegram webhook endpoint',
    usage: 'POST to receive updates, GET ?action=setup to configure',
  })
}
