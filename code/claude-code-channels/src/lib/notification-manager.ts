import { Task, StreamEvent, StreamEventType, TaskStatus } from '@/types'
import logger, { createChildLogger } from './logger'

const log = createChildLogger('NotificationManager')

type EventCallback = (event: StreamEvent) => void

interface Subscriber {
  id: string
  taskId?: string
  callback: EventCallback
}

export class NotificationManager {
  private static instance: NotificationManager
  private subscribers = new Map<string, Subscriber>()
  private globalSubscribers = new Set<string>()

  static getInstance(): NotificationManager {
    if (!NotificationManager.instance) {
      NotificationManager.instance = new NotificationManager()
    }
    return NotificationManager.instance
  }

  subscribe(callback: EventCallback, options?: { taskId?: string }): string {
    const id = typeof crypto !== 'undefined' && crypto.randomUUID 
      ? crypto.randomUUID() 
      : `sub-${Date.now()}-${Math.random().toString(36).slice(2)}`
    const subscriber: Subscriber = {
      id,
      taskId: options?.taskId,
      callback,
    }

    this.subscribers.set(id, subscriber)
    if (!options?.taskId) {
      this.globalSubscribers.add(id)
    }

    log.debug({ subscriberId: id, taskId: options?.taskId }, 'Subscriber added')
    return id
  }

  unsubscribe(id: string): void {
    this.subscribers.delete(id)
    this.globalSubscribers.delete(id)
    log.debug({ subscriberId: id }, 'Subscriber removed')
  }

  emit(event: StreamEvent): void {
    log.debug({ eventType: event.type, taskId: event.taskId }, 'Emitting event')

    for (const subscriber of this.subscribers.values()) {
      // Send to task-specific subscribers and global subscribers
      if (!subscriber.taskId || subscriber.taskId === event.taskId) {
        try {
          subscriber.callback(event)
        } catch (error) {
          log.error({ error, subscriberId: subscriber.id }, 'Error in subscriber callback')
        }
      }
    }
  }

  // Convenience methods for common events
  taskCreated(task: Task): void {
    this.emit({
      type: 'task.created',
      taskId: task.id,
      timestamp: new Date(),
      data: { task },
    })
  }

  taskQueued(taskId: string): void {
    this.emit({
      type: 'task.queued',
      taskId,
      timestamp: new Date(),
      data: { status: 'queued' },
    })
  }

  taskStarted(taskId: string): void {
    this.emit({
      type: 'task.started',
      taskId,
      timestamp: new Date(),
      data: { status: 'running', startedAt: new Date() },
    })
  }

  taskProgress(taskId: string, message: string, percentComplete?: number): void {
    this.emit({
      type: 'task.progress',
      taskId,
      timestamp: new Date(),
      data: { message, percentComplete },
    })
  }

  taskLog(taskId: string, level: 'debug' | 'info' | 'warn' | 'error', message: string, data?: Record<string, unknown>): void {
    this.emit({
      type: 'task.log',
      taskId,
      timestamp: new Date(),
      data: { level, message, data },
    })
  }

  taskCompleted(taskId: string, result: unknown): void {
    this.emit({
      type: 'task.completed',
      taskId,
      timestamp: new Date(),
      data: { result, completedAt: new Date() },
    })
  }

  taskFailed(taskId: string, error: string): void {
    this.emit({
      type: 'task.failed',
      taskId,
      timestamp: new Date(),
      data: { error },
    })
  }

  taskCancelled(taskId: string): void {
    this.emit({
      type: 'task.cancelled',
      taskId,
      timestamp: new Date(),
      data: {},
    })
  }

  artifactCreated(taskId: string, artifact: unknown): void {
    this.emit({
      type: 'artifact.created',
      taskId,
      timestamp: new Date(),
      data: { artifact },
    })
  }
}

export const notificationManager = NotificationManager.getInstance()
