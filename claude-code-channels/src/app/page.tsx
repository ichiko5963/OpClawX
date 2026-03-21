'use client'

import { useEffect, useState } from 'react'
import { TaskSummary, TaskStatus, DashboardStatsResponse } from '@/types'

const statusColors: Record<TaskStatus, string> = {
  pending: 'bg-yellow-500',
  queued: 'bg-blue-500',
  processing: 'bg-purple-500',
  running: 'bg-indigo-500',
  completed: 'bg-green-500',
  failed: 'bg-red-500',
  cancelled: 'bg-gray-500',
}

const statusIcons: Record<TaskStatus, string> = {
  pending: '⏳',
  queued: '📥',
  processing: '⚙️',
  running: '🔄',
  completed: '✅',
  failed: '❌',
  cancelled: '🚫',
}

export default function Dashboard(): JSX.Element {
  const [stats, setStats] = useState<DashboardStatsResponse | null>(null)
  const [recentTasks, setRecentTasks] = useState<TaskSummary[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Fetch initial stats
    fetchStats()

    // Set up SSE connection
    const eventSource = new EventSource('/api/stream')

    eventSource.addEventListener('connected', () => {
      setIsConnected(true)
      setError(null)
    })

    eventSource.addEventListener('task.created', () => {
      fetchStats()
    })

    eventSource.addEventListener('task.completed', () => {
      fetchStats()
    })

    eventSource.addEventListener('task.failed', () => {
      fetchStats()
    })

    eventSource.addEventListener('error', () => {
      setIsConnected(false)
      setError('Connection lost. Retrying...')
    })

    // Refresh stats periodically
    const interval = setInterval(fetchStats, 10000)

    return () => {
      eventSource.close()
      clearInterval(interval)
    }
  }, [])

  const fetchStats = async (): Promise<void> => {
    try {
      const response = await fetch('/api/stats')
      if (!response.ok) throw new Error('Failed to fetch stats')
      const data = await response.json()
      setStats(data)
      setRecentTasks(data.recentTasks)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms}ms`
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
    return `${(ms / 60000).toFixed(1)}m`
  }

  const formatTime = (date: Date): string => {
    return new Date(date).toLocaleTimeString()
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Claude Code Channels</h1>
              <p className="text-gray-600 dark:text-gray-400">
                Remote task execution via Discord/Telegram messages
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span
                className={`inline-block w-3 h-3 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </header>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              title="Total Tasks"
              value={stats.totalTasks}
              icon="📊"
              color="blue"
            />
            <StatCard
              title="Active Tasks"
              value={stats.activeTasks}
              icon="⚡"
              color="yellow"
            />
            <StatCard
              title="Completed"
              value={stats.completedTasks}
              icon="✅"
              color="green"
            />
            <StatCard
              title="Failed"
              value={stats.failedTasks}
              icon="❌"
              color="red"
            />
          </div>
        )}

        {/* Status Distribution */}
        {stats && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Tasks by Status</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
              {Object.entries(stats.tasksByStatus).map(([status, count]) => (
                <div
                  key={status}
                  className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div className="text-2xl mb-1">{statusIcons[status as TaskStatus]}</div>
                  <div className="text-2xl font-bold">{count}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                    {status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Tasks */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold">Recent Tasks</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Source
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Preview
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Created
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {recentTasks.length === 0 ? (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-6 py-8 text-center text-gray-500 dark:text-gray-400"
                    >
                      No tasks yet. Send a message starting with !task or /task to get started.
                    </td>
                  </tr>
                ) : (
                  recentTasks.map((task) => (
                    <tr key={task.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium text-white ${
                            statusColors[task.status]
                          }`}
                        >
                          {statusIcons[task.status]} {task.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="capitalize">{task.source}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">{task.user}</td>
                      <td className="px-6 py-4 max-w-md truncate">{task.preview}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {formatTime(task.createdAt)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>
            Use <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">!task</code> in Discord or{' '}
            <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">/task</code> in Telegram to create tasks
          </p>
        </footer>
      </div>
    </main>
  )
}

function StatCard({
  title,
  value,
  icon,
  color,
}: {
  title: string
  value: number
  icon: string
  color: string
}): JSX.Element {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    green: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    yellow: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    red: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  }

  return (
    <div className={`rounded-lg shadow p-6 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">{title}</p>
          <p className="text-3xl font-bold mt-1">{value}</p>
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  )
}
