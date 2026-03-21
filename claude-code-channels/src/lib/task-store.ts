import { Task, TaskSummary, TaskStatus } from '@/types'
import { getRedisClient, isRedisAvailable } from './redis'
import logger, { createChildLogger } from './logger'

const log = createChildLogger('TaskStore')

// In-memory fallback when Redis is not available
const memoryStore = new Map<string, Task>()

const TASK_PREFIX = 'task:'
const TASK_LIST_KEY = 'tasks:list'
const ACTIVE_TASKS_KEY = 'tasks:active'

export class TaskStore {
  private static instance: TaskStore

  static getInstance(): TaskStore {
    if (!TaskStore.instance) {
      TaskStore.instance = new TaskStore()
    }
    return TaskStore.instance
  }

  async create(task: Task): Promise<void> {
    const redis = getRedisClient()
    const serialized = this.serializeTask(task)

    if (redis) {
      const pipeline = redis.pipeline()
      pipeline.set(`${TASK_PREFIX}${task.id}`, serialized)
      pipeline.zadd(TASK_LIST_KEY, { score: Date.now(), member: task.id })
      pipeline.zadd(`${TASK_PREFIX}status:${task.status}`, { score: Date.now(), member: task.id })
      await pipeline.exec()
    } else {
      memoryStore.set(task.id, task)
    }

    log.info({ taskId: task.id }, 'Task created')
  }

  async get(id: string): Promise<Task | null> {
    const redis = getRedisClient()

    if (redis) {
      const data = await redis.get<string>(`${TASK_PREFIX}${id}`)
      return data ? this.deserializeTask(data) : null
    }

    return memoryStore.get(id) ?? null
  }

  async update(id: string, updates: Partial<Task>): Promise<void> {
    const redis = getRedisClient()
    const existing = await this.get(id)

    if (!existing) {
      throw new Error(`Task not found: ${id}`)
    }

    const oldStatus = existing.status
    const updated = { ...existing, ...updates }

    if (redis) {
      const pipeline = redis.pipeline()
      pipeline.set(`${TASK_PREFIX}${id}`, this.serializeTask(updated))

      // Update status indexes if status changed
      if (updates.status && updates.status !== oldStatus) {
        pipeline.zrem(`${TASK_PREFIX}status:${oldStatus}`, id)
        pipeline.zadd(`${TASK_PREFIX}status:${updates.status}`, { score: Date.now(), member: id })

        if (updates.status === 'processing' || updates.status === 'running') {
          pipeline.zadd(ACTIVE_TASKS_KEY, { score: Date.now(), member: id })
        } else if (oldStatus === 'processing' || oldStatus === 'running') {
          pipeline.zrem(ACTIVE_TASKS_KEY, id)
        }
      }

      await pipeline.exec()
    } else {
      memoryStore.set(id, updated)
    }

    log.debug({ taskId: id, updates: Object.keys(updates) }, 'Task updated')
  }

  async delete(id: string): Promise<void> {
    const redis = getRedisClient()
    const task = await this.get(id)

    if (redis && task) {
      const pipeline = redis.pipeline()
      pipeline.del(`${TASK_PREFIX}${id}`)
      pipeline.zrem(TASK_LIST_KEY, id)
      pipeline.zrem(`${TASK_PREFIX}status:${task.status}`, id)
      pipeline.zrem(ACTIVE_TASKS_KEY, id)
      await pipeline.exec()
    } else {
      memoryStore.delete(id)
    }

    log.info({ taskId: id }, 'Task deleted')
  }

  async list(options?: {
    status?: TaskStatus
    limit?: number
    offset?: number
  }): Promise<TaskSummary[]> {
    const redis = getRedisClient()
    const { status, limit = 50, offset = 0 } = options ?? {}

    if (redis) {
      const key = status ? `${TASK_PREFIX}status:${status}` : TASK_LIST_KEY
      const ids = await redis.zrange(key, offset, offset + limit - 1, { rev: true })

      if (ids.length === 0) return []

      const pipeline = redis.pipeline()
      for (const id of ids) {
        pipeline.get(`${TASK_PREFIX}${id}`)
      }
      const results = await pipeline.exec<[string][]>()

      return results
        .map((r) => (r ? this.deserializeTask(r) : null))
        .filter((t): t is Task => t !== null)
        .map((t) => this.toSummary(t))
    }

    // In-memory fallback
    const tasks = Array.from(memoryStore.values())
    const filtered = status ? tasks.filter((t) => t.status === status) : tasks
    const sorted = filtered.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
    const paginated = sorted.slice(offset, offset + limit)

    return paginated.map((t) => this.toSummary(t))
  }

  async getActive(): Promise<Task[]> {
    const redis = getRedisClient()

    if (redis) {
      const ids = await redis.zrange(ACTIVE_TASKS_KEY, 0, -1)
      if (ids.length === 0) return []

      const pipeline = redis.pipeline()
      for (const id of ids) {
        pipeline.get(`${TASK_PREFIX}${id}`)
      }
      const results = await pipeline.exec<[string][]>()

      return results
        .map((r) => (r ? this.deserializeTask(r) : null))
        .filter((t): t is Task => t !== null)
    }

    return Array.from(memoryStore.values()).filter(
      (t) => t.status === 'processing' || t.status === 'running'
    )
  }

  async getStats(): Promise<{
    total: number
    byStatus: Record<TaskStatus, number>
  }> {
    const redis = getRedisClient()

    if (redis) {
      const statuses: TaskStatus[] = ['pending', 'queued', 'processing', 'running', 'completed', 'failed', 'cancelled']
      const pipeline = redis.pipeline()
      pipeline.zcard(TASK_LIST_KEY)
      for (const status of statuses) {
        pipeline.zcard(`${TASK_PREFIX}status:${status}`)
      }
      const results = await pipeline.exec<[number, ...number[]]>()
      const [total, ...counts] = results

      const byStatus = {} as Record<TaskStatus, number>
      statuses.forEach((status, i) => {
        byStatus[status] = counts[i] ?? 0
      })

      return { total, byStatus }
    }

    const tasks = Array.from(memoryStore.values())
    const byStatus = {} as Record<TaskStatus, number>

    for (const task of tasks) {
      byStatus[task.status] = (byStatus[task.status] ?? 0) + 1
    }

    return { total: tasks.length, byStatus }
  }

  private serializeTask(task: Task): string {
    return JSON.stringify({
      ...task,
      createdAt: task.createdAt.toISOString(),
      startedAt: task.startedAt?.toISOString(),
      completedAt: task.completedAt?.toISOString(),
      message: {
        ...task.message,
        timestamp: task.message.timestamp.toISOString(),
      },
      logs: task.logs.map((l) => ({
        ...l,
        timestamp: l.timestamp.toISOString(),
      })),
    })
  }

  private deserializeTask(data: string): Task {
    const parsed = JSON.parse(data)
    return {
      ...parsed,
      createdAt: new Date(parsed.createdAt),
      startedAt: parsed.startedAt ? new Date(parsed.startedAt) : undefined,
      completedAt: parsed.completedAt ? new Date(parsed.completedAt) : undefined,
      message: {
        ...parsed.message,
        timestamp: new Date(parsed.message.timestamp),
      },
      logs: parsed.logs?.map((l: { timestamp: string | number | Date }) => ({
        ...l,
        timestamp: new Date(l.timestamp),
      })) ?? [],
    }
  }

  private toSummary(task: Task): TaskSummary {
    return {
      id: task.id,
      status: task.status,
      source: task.message.source,
      user: task.message.user.username,
      preview: task.prompt.slice(0, 100) + (task.prompt.length > 100 ? '...' : ''),
      createdAt: task.createdAt,
      completedAt: task.completedAt,
    }
  }
}

export const taskStore = TaskStore.getInstance()
