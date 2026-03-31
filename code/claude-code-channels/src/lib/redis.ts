import { Redis } from '@upstash/redis'
import { getRedisConfig } from './config'
import logger from './logger'

let redisClient: Redis | null = null

export function getRedisClient(): Redis | null {
  if (redisClient) return redisClient

  const config = getRedisConfig()

  if (config.type === 'upstash') {
    redisClient = new Redis({
      url: config.url,
      token: config.token,
    })
    logger.info('Redis client initialized (Upstash)')
    return redisClient
  }

  // For local development without Redis, return null
  // The app will fallback to in-memory storage
  logger.warn('No Redis configuration found, using in-memory storage')
  return null
}

export async function isRedisAvailable(): Promise<boolean> {
  const client = getRedisClient()
  if (!client) return false

  try {
    await client.ping()
    return true
  } catch (error) {
    logger.warn({ error }, 'Redis connection failed')
    return false
  }
}
