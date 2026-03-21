import { NextRequest } from 'next/server'
import { verifyKey } from 'discord-interactions'
import logger, { createChildLogger } from '@/lib/logger'

const log = createChildLogger('DiscordWebhook')

/**
 * Verify that the request is coming from Discord
 */
function verifyDiscordRequest(
  signature: string,
  timestamp: string,
  body: string
): boolean {
  const publicKey = process.env.DISCORD_PUBLIC_KEY

  if (!publicKey) {
    log.error('DISCORD_PUBLIC_KEY not configured')
    return false
  }

  try {
    return verifyKey(body, signature, timestamp, publicKey)
  } catch (error) {
    log.error({ error }, 'Discord signature verification failed')
    return false
  }
}

/**
 * Handle Discord webhook interactions
 */
export async function POST(request: NextRequest): Promise<Response> {
  const signature = request.headers.get('x-signature-ed25519')
  const timestamp = request.headers.get('x-signature-timestamp')

  if (!signature || !timestamp) {
    return new Response('Missing signature headers', { status: 401 })
  }

  const body = await request.text()

  // Verify the request
  if (!verifyDiscordRequest(signature, timestamp, body)) {
    return new Response('Invalid request signature', { status: 401 })
  }

  const interaction = JSON.parse(body)

  log.debug({ type: interaction.type }, 'Received Discord interaction')

  // Handle PING (verification)
  if (interaction.type === 1) {
    return Response.json({ type: 1 })
  }

  // Handle APPLICATION_COMMAND
  if (interaction.type === 2) {
    return handleApplicationCommand(interaction)
  }

  // Handle MESSAGE_COMPONENT
  if (interaction.type === 3) {
    return handleMessageComponent(interaction)
  }

  return new Response('Unknown interaction type', { status: 400 })
}

function handleApplicationCommand(interaction: Record<string, unknown>): Response {
  const { name, options } = interaction.data as {
    name: string
    options?: Array<{ name: string; value: string }>
  }

  if (name === 'task') {
    const prompt = options?.find((o) => o.name === 'prompt')?.value ?? ''

    // Return immediate acknowledgement
    // The actual processing happens asynchronously
    return Response.json({
      type: 5, // DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
      data: {
        content: '🤔 Processing your task...',
      },
    })
  }

  return Response.json({
    type: 4, // CHANNEL_MESSAGE_WITH_SOURCE
    data: {
      content: 'Unknown command',
    },
  })
}

function handleMessageComponent(interaction: Record<string, unknown>): Response {
  // Handle button clicks, select menus, etc.
  const customId = (interaction.data as { custom_id: string }).custom_id

  if (customId.startsWith('task:')) {
    const taskId = customId.split(':')[1]

    return Response.json({
      type: 4,
      data: {
        content: `Task ${taskId} action received`,
      },
    })
  }

  return Response.json({
    type: 4,
    data: {
      content: 'Unknown interaction',
    },
  })
}
