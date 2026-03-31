import { createClaudeHandler } from './claude-handler'
import { taskExecutor } from './task-executor'
import logger, { createChildLogger } from './logger'

const log = createChildLogger('Init')

let initialized = false

export async function initialize(): Promise<void> {
  if (initialized) {
    return
  }

  log.info('Initializing Claude Code Channels...')

  // Register default task handlers
  const claudeHandler = createClaudeHandler()
  taskExecutor.registerHandler('!task', claudeHandler)
  taskExecutor.registerHandler('/task', claudeHandler)
  taskExecutor.registerHandler('!claude', claudeHandler)
  taskExecutor.registerHandler('/claude', claudeHandler)
  taskExecutor.registerHandler('default', claudeHandler)

  log.info('Task handlers registered')

  initialized = true
  log.info('Initialization complete')
}
