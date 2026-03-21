import { Telegraf, Context } from 'telegraf'
import { Message, Update } from 'telegraf/typings/core/types/typegram'
import { Task, TaskMessage, UserInfo, ChannelInfo } from '@/types'
import { getConfig } from '../config'
import { isTaskCommand, extractPrompt } from '../command-parser'
import { taskStore } from '../task-store'
import { taskExecutor } from '../task-executor'
import { notificationManager } from '../notification-manager'
import logger, { createChildLogger } from '../logger'
import { v4 as uuidv4 } from 'uuid'

const log = createChildLogger('TelegramBot')

export class TelegramBot {
  private static instance: TelegramBot
  private bot: Telegraf<Context<Update>> | null = null
  private isRunning = false

  static getInstance(): TelegramBot {
    if (!TelegramBot.instance) {
      TelegramBot.instance = new TelegramBot()
    }
    return TelegramBot.instance
  }

  async start(): Promise<void> {
    const config = getConfig().telegram

    if (!config?.enabled) {
      log.info('Telegram bot is disabled')
      return
    }

    if (this.isRunning) {
      log.warn('Telegram bot is already running')
      return
    }

    this.bot = new Telegraf(config.token)

    // Middleware to check allowed chats
    this.bot.use(this.checkAllowedChat.bind(this))

    // Handle text messages
    this.bot.on('text', this.handleTextMessage.bind(this))

    // Error handling
    this.bot.catch((err: unknown, ctx: Context<Update>) => {
      log.error({ error: err, updateId: ctx.update.update_id }, 'Telegram bot error')
    })

    // Start bot
    if (process.env.NODE_ENV === 'production') {
      // Use webhook in production
      const webhookUrl = `${process.env.APP_URL}/api/webhooks/telegram`
      await this.bot.launch({ webhook: { domain: webhookUrl, port: undefined } })
      log.info({ webhookUrl }, 'Telegram bot started with webhook')
    } else {
      // Use polling in development
      await this.bot.launch()
      log.info('Telegram bot started with polling')
    }

    this.isRunning = true

    // Subscribe to notifications
    this.subscribeToNotifications()

    // Graceful shutdown
    process.once('SIGINT', () => this.stop())
    process.once('SIGTERM', () => this.stop())
  }

  async stop(): Promise<void> {
    if (this.bot) {
      this.bot.stop()
      this.isRunning = false
      log.info('Telegram bot stopped')
    }
  }

  private async checkAllowedChat(ctx: Context<Update>, next: () => Promise<void>): Promise<void> {
    const config = getConfig().telegram

    if (!config?.enabled) {
      return
    }

    // Skip check if no allowed chats configured
    if (config.allowedChatIds.length === 0) {
      return next()
    }

    const chatId = ctx.chat?.id

    if (!chatId || !config.allowedChatIds.includes(chatId)) {
      log.debug({ chatId }, 'Message from non-allowed chat ignored')
      return
    }

    return next()
  }

  private async handleTextMessage(ctx: Context<Update>): Promise<void> {
    const message = ctx.message as Message.TextMessage
    const text = message.text

    if (!text) return

    // Check if it's a task command
    if (!isTaskCommand(text)) {
      return
    }

    const config = getConfig().telegram!

    log.info({
      user: message.from?.username ?? message.from?.first_name,
      chatId: ctx.chat?.id,
      preview: text.slice(0, 50),
    }, 'Received task command')

    try {
      // Send acknowledgment
      const thinkingMsg = await ctx.reply('🤔 Processing your task...')

      // Create task
      const taskMessage = this.createTaskMessage(message, ctx)
      const prompt = extractPrompt(text, config.commandPrefix)

      const task: Task = {
        id: uuidv4(),
        message: taskMessage,
        status: 'pending',
        priority: 'normal',
        commandPrefix: config.commandPrefix,
        prompt,
        createdAt: new Date(),
        logs: [],
        metadata: {
          telegramChatId: ctx.chat?.id,
          telegramMessageId: message.message_id,
          telegramThinkingMessageId: (thinkingMsg as Message.TextMessage).message_id,
        },
      }

      // Store and execute
      await taskStore.create(task)
      notificationManager.taskCreated(task)

      // Start execution in background
      taskExecutor.execute(task).catch((error) => {
        log.error({ taskId: task.id, error }, 'Task execution error')
      })

    } catch (error) {
      log.error({ error, messageId: message.message_id }, 'Error handling message')
      await ctx.reply('❌ Sorry, something went wrong processing your task.').catch(() => {})
    }
  }

  private createTaskMessage(message: Message.TextMessage, ctx: Context<Update>): TaskMessage {
    const user: UserInfo = {
      id: String(message.from?.id),
      username: message.from?.username ?? message.from?.first_name ?? 'unknown',
      displayName: message.from?.first_name,
    }

    const chatType = ctx.chat?.type
    const channelInfo: ChannelInfo = {
      id: String(ctx.chat?.id),
      name: chatType === 'private' ? 'DM' : (ctx.chat as { title?: string })?.title ?? 'unknown',
      type: chatType === 'private' ? 'dm' : 'channel',
      platform: 'telegram',
    }

    return {
      id: String(message.message_id),
      content: message.text,
      user,
      channel: channelInfo,
      source: 'telegram',
      timestamp: new Date(message.date * 1000),
      replyTo: message.reply_to_message ? String(message.reply_to_message.message_id) : undefined,
    }
  }

  private subscribeToNotifications(): void {
    notificationManager.subscribe(async (event) => {
      if (event.type === 'task.completed' || event.type === 'task.failed') {
        await this.sendTaskResult(event.taskId, event.type === 'task.completed')
      }
    })
  }

  private async sendTaskResult(taskId: string, success: boolean): Promise<void> {
    const task = await taskStore.get(taskId)
    if (!task || task.message.source !== 'telegram' || !this.bot) return

    const { telegramChatId, telegramMessageId, telegramThinkingMessageId } = task.metadata as {
      telegramChatId: number
      telegramMessageId: number
      telegramThinkingMessageId: number
    }

    try {
      // Delete thinking message
      await this.bot.telegram.deleteMessage(telegramChatId, telegramThinkingMessageId).catch(() => {})

      // Prepare response
      let content: string
      const MAX_LENGTH = 4000

      if (success && task.result) {
        let output = task.result.output
        if (output.length > MAX_LENGTH) {
          output = output.slice(0, MAX_LENGTH) + '\n\n... (truncated)'
        }
        content = `✅ <b>Task Complete</b>\n\n${this.escapeHtml(output)}`
      } else {
        const error = task.error ?? 'Unknown error'
        content = `❌ <b>Task Failed</b>\n\n${this.escapeHtml(error.slice(0, MAX_LENGTH))}`
      }

      // Send reply
      await this.bot.telegram.sendMessage(telegramChatId, content, {
        reply_to_message_id: telegramMessageId,
        parse_mode: 'HTML',
      })

    } catch (error) {
      log.error({ taskId, error }, 'Error sending Telegram result')
    }
  }

  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
  }

  // For webhook handling
  async handleWebhook(update: unknown): Promise<void> {
    if (this.bot) {
      await this.bot.handleUpdate(update as Update)
    }
  }
}

export const telegramBot = TelegramBot.getInstance()
