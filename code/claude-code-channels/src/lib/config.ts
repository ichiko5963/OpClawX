import { BotConfig } from '@/types'

export function getConfig(): BotConfig {
  const discordEnabled = !!process.env.DISCORD_BOT_TOKEN
  const telegramEnabled = !!process.env.TELEGRAM_BOT_TOKEN

  return {
    discord: discordEnabled
      ? {
          enabled: true,
          token: process.env.DISCORD_BOT_TOKEN!,
          allowedChannelIds: process.env.DISCORD_ALLOWED_CHANNEL_IDS?.split(',') ?? [],
          commandPrefix: '!task',
        }
      : undefined,
    telegram: telegramEnabled
      ? {
          enabled: true,
          token: process.env.TELEGRAM_BOT_TOKEN!,
          allowedChatIds: process.env.TELEGRAM_ALLOWED_CHAT_IDS?.split(',').map(Number) ?? [],
          commandPrefix: '/task',
        }
      : undefined,
    claude: {
      apiKey: process.env.ANTHROPIC_API_KEY ?? '',
      model: process.env.CLAUDE_MODEL ?? 'claude-3-5-sonnet-20241022',
      maxTokens: 4096,
      temperature: 0.7,
    },
    rateLimit: {
      requestsPerMinute: Number(process.env.RATE_LIMIT_REQUESTS_PER_MINUTE ?? '10'),
      maxConcurrent: 3,
    },
  }
}

export function getAppUrl(): string {
  return process.env.APP_URL ?? 'http://localhost:3000'
}

export function isProduction(): boolean {
  return process.env.NODE_ENV === 'production'
}

export function getRedisConfig() {
  if (process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN) {
    return {
      type: 'upstash' as const,
      url: process.env.UPSTASH_REDIS_REST_URL,
      token: process.env.UPSTASH_REDIS_REST_TOKEN,
    }
  }

  if (process.env.REDIS_URL) {
    return {
      type: 'url' as const,
      url: process.env.REDIS_URL,
    }
  }

  return {
    type: 'host' as const,
    host: process.env.REDIS_HOST ?? 'localhost',
    port: Number(process.env.REDIS_PORT ?? '6379'),
    password: process.env.REDIS_PASSWORD,
  }
}
