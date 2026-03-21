// Task Status Types
export type TaskStatus = 
  | 'pending' 
  | 'queued' 
  | 'processing' 
  | 'running' 
  | 'completed' 
  | 'failed' 
  | 'cancelled'

// Source Platform Types
export type MessageSource = 'discord' | 'telegram' | 'api'

// Task Priority
export type TaskPriority = 'low' | 'normal' | 'high' | 'urgent'

// User Information
export interface UserInfo {
  id: string
  username: string
  displayName?: string
  avatarUrl?: string
}

// Channel Information
export interface ChannelInfo {
  id: string
  name: string
  type: 'dm' | 'group' | 'channel'
  platform: MessageSource
}

// Task Message
export interface TaskMessage {
  id: string
  content: string
  user: UserInfo
  channel: ChannelInfo
  source: MessageSource
  attachments?: AttachmentInfo[]
  timestamp: Date
  replyTo?: string
}

// Attachment Information
export interface AttachmentInfo {
  id: string
  filename: string
  contentType: string
  size: number
  url: string
}

// Task Definition
export interface Task {
  id: string
  message: TaskMessage
  status: TaskStatus
  priority: TaskPriority
  commandPrefix: string
  prompt: string
  context?: string
  createdAt: Date
  startedAt?: Date
  completedAt?: Date
  error?: string
  result?: TaskResult
  logs: TaskLogEntry[]
  metadata: TaskMetadata
}

// Task Result
export interface TaskResult {
  success: boolean
  output: string
  artifacts?: Artifact[]
  executionTimeMs: number
}

// Artifact (files, images, etc.)
export interface Artifact {
  id: string
  type: 'file' | 'image' | 'code' | 'link'
  name: string
  content?: string
  url?: string
  mimeType?: string
}

// Task Log Entry
export interface TaskLogEntry {
  id: string
  timestamp: Date
  level: 'debug' | 'info' | 'warn' | 'error'
  message: string
  data?: Record<string, unknown>
}

// Task Metadata
export interface TaskMetadata {
  model?: string
  tokenUsage?: {
    input: number
    output: number
    total: number
  }
  processingTimeMs?: number
  retryCount?: number
  tags?: string[]
}

// Stream Event Types
export type StreamEventType =
  | 'task.created'
  | 'task.queued'
  | 'task.started'
  | 'task.progress'
  | 'task.log'
  | 'task.completed'
  | 'task.failed'
  | 'task.cancelled'
  | 'artifact.created'

// Stream Event
export interface StreamEvent {
  type: StreamEventType
  taskId: string
  timestamp: Date
  data: unknown
}

// Task Progress Update
export interface TaskProgressUpdate {
  status: TaskStatus
  message: string
  percentComplete?: number
}

// Command Parse Result
export interface CommandParseResult {
  isCommand: boolean
  prefix: string
  command: string
  args: string
  flags: Record<string, string | boolean>
}

// Bot Configuration
export interface BotConfig {
  discord?: {
    enabled: boolean
    token: string
    allowedChannelIds: string[]
    commandPrefix: string
  }
  telegram?: {
    enabled: boolean
    token: string
    allowedChatIds: string[]
    commandPrefix: string
  }
  claude: {
    apiKey: string
    model: string
    maxTokens: number
    temperature: number
  }
  rateLimit: {
    requestsPerMinute: number
    maxConcurrent: number
  }
}

// Dashboard Stats
export interface DashboardStats {
  totalTasks: number
  activeTasks: number
  completedTasks: number
  failedTasks: number
  averageProcessingTimeMs: number
  tasksByStatus: Record<TaskStatus, number>
  tasksBySource: Record<MessageSource, number>
  recentTasks: TaskSummary[]
}

export interface DashboardStatsResponse {
  totalTasks: number
  activeTasks: number
  completedTasks: number
  failedTasks: number
  averageProcessingTimeMs: number
  tasksByStatus: Record<TaskStatus, number>
  tasksBySource: Record<MessageSource, number>
  recentTasks: TaskSummary[]
}

// Task Summary (for lists)
export interface TaskSummary {
  id: string
  status: TaskStatus
  source: MessageSource
  user: string
  preview: string
  createdAt: Date
  completedAt?: Date
}

// Webhook Payload (Discord)
export interface DiscordWebhookPayload {
  id: string
  type: number
  token: string
  channel_id: string
  guild_id?: string
  member?: {
    user: {
      id: string
      username: string
      avatar?: string
    }
  }
  user?: {
    id: string
    username: string
    avatar?: string
  }
  data: {
    id: string
    name: string
    options?: Array<{
      name: string
      value: string
    }>
  }
  message?: {
    id: string
    content: string
    author: {
      id: string
      username: string
      avatar?: string
    }
    timestamp: string
    attachments: Array<{
      id: string
      filename: string
      content_type: string
      size: number
      url: string
    }>
  }
}

// Webhook Payload (Telegram)
export interface TelegramWebhookPayload {
  update_id: number
  message?: {
    message_id: number
    from: {
      id: number
      is_bot: boolean
      first_name: string
      username?: string
    }
    chat: {
      id: number
      type: 'private' | 'group' | 'supergroup' | 'channel'
      title?: string
    }
    date: number
    text?: string
    reply_to_message?: {
      message_id: number
      text?: string
    }
  }
}
