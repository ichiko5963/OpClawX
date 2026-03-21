import { NextRequest } from 'next/server'
import { taskStore } from '@/lib/task-store'
import { taskExecutor } from '@/lib/task-executor'
import logger, { createChildLogger } from '@/lib/logger'

const log = createChildLogger('TaskAPI')

interface RouteParams {
  params: Promise<{ id: string }>
}

/**
 * GET /api/tasks/:id
 * Get task details
 */
export async function GET(
  request: NextRequest,
  { params }: RouteParams
): Promise<Response> {
  const { id } = await params

  try {
    const task = await taskStore.get(id)

    if (!task) {
      return Response.json(
        { error: 'Task not found' },
        { status: 404 }
      )
    }

    return Response.json({ task })
  } catch (error) {
    log.error({ taskId: id, error }, 'Error fetching task')
    return Response.json(
      { error: 'Failed to fetch task' },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/tasks/:id
 * Cancel or delete a task
 */
export async function DELETE(
  request: NextRequest,
  { params }: RouteParams
): Promise<Response> {
  const { id } = await params

  try {
    const task = await taskStore.get(id)

    if (!task) {
      return Response.json(
        { error: 'Task not found' },
        { status: 404 }
      )
    }

    // If task is running, try to cancel it
    if (task.status === 'processing' || task.status === 'running') {
      const cancelled = await taskExecutor.cancel(id)

      if (!cancelled) {
        return Response.json(
          { error: 'Failed to cancel task' },
          { status: 500 }
        )
      }

      return Response.json({
        message: 'Task cancelled',
        taskId: id,
      })
    }

    // Otherwise, delete the task
    await taskStore.delete(id)

    return Response.json({
      message: 'Task deleted',
      taskId: id,
    })
  } catch (error) {
    log.error({ taskId: id, error }, 'Error deleting task')
    return Response.json(
      { error: 'Failed to delete task' },
      { status: 500 }
    )
  }
}
