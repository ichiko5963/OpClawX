import pino from 'pino'
import { isProduction } from './config'

const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  transport: isProduction()
    ? undefined
    : {
        target: 'pino-pretty',
        options: {
          colorize: true,
          translateTime: 'HH:MM:ss Z',
          ignore: 'pid,hostname',
        },
      },
})

export default logger

export function createChildLogger(component: string, meta?: Record<string, unknown>) {
  return logger.child({ component, ...meta })
}
