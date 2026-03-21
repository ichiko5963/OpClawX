import { NextRequest } from 'next/server'
import { Task, TaskStatus } from '@/types'
import { taskStore } from '@/lib/task-store'
import { taskExecutor } from '@/lib/task-executor'
import { notificationManager } from '@/lib/notification-manager'
import { v4 as uuidv4 } from 'uuid'
import logger, { createChildLogger } from '@/lib/logger'

const log = createChildLogger('TasksAPI')

/**
 * GET /api/tasks
 * List tasks with optional filtering
 */
export async function GET(request: NextRequest): Promise<Response> {
  const { searchParams } = new URL(request.url)

  const status = searchParams.get('status') as TaskStatus | undefined
  const limit = parseInt(searchParams.get('limit') ?? '50', 10)
  const offset = parseInt(searchParams.get('offset') ?? '0', 10)

  try {
    const tasks = await taskStore.list({ status, limit, offset })
    return Response.json({ tasks, limit, offset })
  } catch (error) {
    log.error({ error }, 'Error listing tasks')
    return Response.json(
      { error: 'Failed to list tasks' },
      { status: 500 }
    )
  }
}

/**
 * POST /api/tasks
 * Create a new task
 */
export async function POST(request: NextRequest): Promise<Response> {
  try {
    const body = await request.json()

    // Validate required fields
    if (!body.prompt || typeof body.prompt !== 'string') {
      return Response.json(
        { error: 'Missing required field: prompt' },
        { status: 400 }
      )
    }

    const task: Task = {
      id: uuidv4(),
      message: {
        id: `api-${Date.now()}`,
        content: body.prompt,
        user: {
          id: body.userId ?? 'api-user',
          username: body.userName ?? 'API User',
        },
        channel: {
          id: 'api',
          name: 'API',
          type: 'channel',
          platform: 'api',
        },
        source: 'api',
        timestamp: new Date(),
      },
      status: 'pending',
      priority: body.priority ?? 'normal',
      commandPrefix: body.commandPrefix ?? '!task',
      prompt: body.prompt,
      context: body.context,
      createdAt: new Date(),
      logs: [],
      metadata: {
        tags: body.tags,
        ...body.metadata,
      },
    }

    // Store task
    await taskStore.create(task)
    notificationManager.taskCreated(task)

    log.info({ taskId: task.id }, 'Task created via API')

    // Start execution asynchronously
    taskExecutor.execute(task).catch((error) => {
      log.error({ taskId: task.id, error }, 'Task execution error')
    })

    return Response.json(
      {
        task: {
          id: task.id,
          status: task.status,
          createdAt: task.createdAt,
        },
      },
      { status: 201 }
    )
  } catch (error) {
    log.error({ error }, 'Error creating task')
    return Response.json(
      { error: 'Failed to create task' },
      { status: 500 }
    )
  }
}
