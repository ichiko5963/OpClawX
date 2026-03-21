import { NextRequest } from 'next/server'
import { taskStore } from '@/lib/task-store'
import logger, { createChildLogger } from '@/lib/logger'

const log = createChildLogger('StatsAPI')

/**
 * GET /api/stats
 * Get dashboard statistics
 */
export async function GET(request: NextRequest): Promise<Response> {
  try {
    const stats = await taskStore.getStats()
    const activeTasks = await taskStore.getActive()
    const recentTasks = await taskStore.list({ limit: 10 })

    // Calculate average processing time
    const completedTasks = await taskStore.list({ status: 'completed', limit: 100 })
    const totalProcessingTime = completedTasks.reduce((sum, task) => {
      const time = task.completedAt && task.createdAt
        ? task.completedAt.getTime() - task.createdAt.getTime()
        : 0
      return sum + time
    }, 0)
    const averageProcessingTimeMs = completedTasks.length > 0
      ? totalProcessingTime / completedTasks.length
      : 0

    return Response.json({
      totalTasks: stats.total,
      activeTasks: activeTasks.length,
      completedTasks: stats.byStatus.completed ?? 0,
      failedTasks: stats.byStatus.failed ?? 0,
      averageProcessingTimeMs: Math.round(averageProcessingTimeMs),
      tasksByStatus: stats.byStatus,
      tasksBySource: {
        discord: recentTasks.filter((t) => t.source === 'discord').length,
        telegram: recentTasks.filter((t) => t.source === 'telegram').length,
        api: recentTasks.filter((t) => t.source === 'api').length,
      },
      recentTasks,
    })
  } catch (error) {
    log.error({ error }, 'Error fetching stats')
    return Response.json(
      { error: 'Failed to fetch statistics' },
      { status: 500 }
    )
  }
}
