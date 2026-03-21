import { Task, TaskResult, TaskLogEntry, TaskStatus } from '@/types'
import { taskStore } from './task-store'
import { notificationManager } from './notification-manager'
import logger, { createChildLogger } from './logger'
import { v4 as uuidv4 } from 'uuid'

const log = createChildLogger('TaskExecutor')

export interface ExecutionContext {
  taskId: string
  prompt: string
  onProgress: (message: string, percentComplete?: number) => void
  onLog: (level: TaskLogEntry['level'], message: string, data?: Record<string, unknown>) => void
  onArtifact: (artifact: unknown) => void
}

export type TaskHandler = (context: ExecutionContext) => Promise<TaskResult>

export class TaskExecutor {
  private static instance: TaskExecutor
  private handlers = new Map<string, TaskHandler>()
  private runningTasks = new Map<string, AbortController>()

  static getInstance(): TaskExecutor {
    if (!TaskExecutor.instance) {
      TaskExecutor.instance = new TaskExecutor()
    }
    return TaskExecutor.instance
  }

  registerHandler(name: string, handler: TaskHandler): void {
    this.handlers.set(name, handler)
    log.info({ handlerName: name }, 'Handler registered')
  }

  async execute(task: Task): Promise<void> {
    const abortController = new AbortController()
    this.runningTasks.set(task.id, abortController)

    const startTime = Date.now()

    try {
      // Update status to processing
      await taskStore.update(task.id, {
        status: 'processing',
        startedAt: new Date(),
      })
      notificationManager.taskStarted(task.id)

      this.addLog(task.id, 'info', 'Task execution started', {
        handler: task.commandPrefix,
        prompt: task.prompt.slice(0, 100),
      })

      // Get the appropriate handler
      const handler = this.handlers.get(task.commandPrefix) ?? this.handlers.get('default')

      if (!handler) {
        throw new Error(`No handler found for command: ${task.commandPrefix}`)
      }

      // Create execution context
      const context: ExecutionContext = {
        taskId: task.id,
        prompt: task.prompt,
        onProgress: (message, percentComplete) => {
          notificationManager.taskProgress(task.id, message, percentComplete)
        },
        onLog: (level, message, data) => {
          this.addLog(task.id, level, message, data)
        },
        onArtifact: (artifact) => {
          notificationManager.artifactCreated(task.id, artifact)
        },
      }

      // Execute with timeout
      const result = await this.executeWithTimeout(
        handler(context),
        Number(process.env.MAX_TASK_DURATION_MS ?? '300000'),
        abortController.signal
      )

      // Update task with result
      await taskStore.update(task.id, {
        status: 'completed',
        completedAt: new Date(),
        result,
        metadata: {
          ...task.metadata,
          processingTimeMs: Date.now() - startTime,
        },
      })

      notificationManager.taskCompleted(task.id, result)
      this.addLog(task.id, 'info', 'Task completed successfully', {
        executionTimeMs: Date.now() - startTime,
      })

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)

      log.error({ taskId: task.id, error: errorMessage }, 'Task execution failed')

      await taskStore.update(task.id, {
        status: 'failed',
        completedAt: new Date(),
        error: errorMessage,
        metadata: {
          ...task.metadata,
          processingTimeMs: Date.now() - startTime,
        },
      })

      notificationManager.taskFailed(task.id, errorMessage)
      this.addLog(task.id, 'error', 'Task execution failed', { error: errorMessage })

    } finally {
      this.runningTasks.delete(task.id)
    }
  }

  async cancel(taskId: string): Promise<boolean> {
    const controller = this.runningTasks.get(taskId)

    if (controller) {
      controller.abort()
      this.runningTasks.delete(taskId)

      await taskStore.update(taskId, {
        status: 'cancelled',
        completedAt: new Date(),
      })

      notificationManager.taskCancelled(taskId)
      this.addLog(taskId, 'warn', 'Task cancelled by user')

      return true
    }

    return false
  }

  private async executeWithTimeout<T>(
    promise: Promise<T>,
    timeoutMs: number,
    signal: AbortSignal
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error(`Task execution timed out after ${timeoutMs}ms`))
      }, timeoutMs)

      const onAbort = () => {
        clearTimeout(timeout)
        reject(new Error('Task cancelled'))
      }

      signal.addEventListener('abort', onAbort)

      promise
        .then((result) => {
          clearTimeout(timeout)
          signal.removeEventListener('abort', onAbort)
          resolve(result)
        })
        .catch((error) => {
          clearTimeout(timeout)
          signal.removeEventListener('abort', onAbort)
          reject(error)
        })
    })
  }

  private async addLog(
    taskId: string,
    level: TaskLogEntry['level'],
    message: string,
    data?: Record<string, unknown>
  ): Promise<void> {
    const logEntry: TaskLogEntry = {
      id: uuidv4(),
      timestamp: new Date(),
      level,
      message,
      data,
    }

    const task = await taskStore.get(taskId)
    if (task) {
      await taskStore.update(taskId, {
        logs: [...task.logs, logEntry],
      })
    }

    notificationManager.taskLog(taskId, level, message, data)
  }
}

export const taskExecutor = TaskExecutor.getInstance()
