import { Client, GatewayIntentBits, Message, TextChannel, DMChannel, NewsChannel, ThreadChannel } from 'discord.js'
import { Task, TaskMessage, UserInfo, ChannelInfo } from '@/types'
import { getConfig } from '../config'
import { isTaskCommand, extractPrompt } from '../command-parser'
import { taskStore } from '../task-store'
import { taskExecutor } from '../task-executor'
import { notificationManager } from '../notification-manager'
import logger, { createChildLogger } from '../logger'
import { v4 as uuidv4 } from 'uuid'

const log = createChildLogger('DiscordBot')

export type SendableChannel = TextChannel | DMChannel | NewsChannel | ThreadChannel

export class DiscordBot {
  private static instance: DiscordBot
  private client: Client | null = null
  private isRunning = false

  static getInstance(): DiscordBot {
    if (!DiscordBot.instance) {
      DiscordBot.instance = new DiscordBot()
    }
    return DiscordBot.instance
  }

  async start(): Promise<void> {
    const config = getConfig().discord

    if (!config?.enabled) {
      log.info('Discord bot is disabled')
      return
    }

    if (this.isRunning) {
      log.warn('Discord bot is already running')
      return
    }

    this.client = new Client({
      intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.DirectMessages,
      ],
    })

    this.client.on('ready', () => {
      log.info({ user: this.client?.user?.tag }, 'Discord bot connected')
      this.isRunning = true
    })

    this.client.on('messageCreate', this.handleMessage.bind(this))

    this.client.on('error', (error) => {
      log.error({ error }, 'Discord client error')
    })

    await this.client.login(config.token)

    // Subscribe to notifications to send updates back to Discord
    this.subscribeToNotifications()
  }

  async stop(): Promise<void> {
    if (this.client) {
      await this.client.destroy()
      this.isRunning = false
      log.info('Discord bot disconnected')
    }
  }

  private async handleMessage(message: Message): Promise<void> {
    // Ignore bot messages
    if (message.author.bot) return

    const config = getConfig().discord!

    // Check if in allowed channel (if configured)
    if (config.allowedChannelIds.length > 0) {
      const channelId = message.channelId
      const isAllowed = config.allowedChannelIds.includes(channelId)
      const isDM = message.channel.isDMBased()

      if (!isAllowed && !isDM) {
        log.debug({ channelId }, 'Message from non-allowed channel ignored')
        return
      }
    }

    // Check if it's a task command
    if (!isTaskCommand(message.content)) {
      return
    }

    log.info({
      user: message.author.username,
      channel: message.channelId,
      preview: message.content.slice(0, 50),
    }, 'Received task command')

    try {
      // Send acknowledgment
      const thinking = await message.reply('🤔 Processing your task...')

      // Create task
      const taskMessage = this.createTaskMessage(message)
      const prompt = extractPrompt(message.content, config.commandPrefix)

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
          discordMessageId: message.id,
          discordThinkingMessageId: thinking.id,
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
      log.error({ error, messageId: message.id }, 'Error handling message')
      await message.reply('❌ Sorry, something went wrong processing your task.').catch(() => {})
    }
  }

  private createTaskMessage(message: Message): TaskMessage {
    const user: UserInfo = {
      id: message.author.id,
      username: message.author.username,
      displayName: message.author.displayName,
      avatarUrl: message.author.displayAvatarURL(),
    }

    const channelInfo: ChannelInfo = {
      id: message.channelId,
      name: message.channel.isDMBased()
        ? 'DM'
        : (message.channel as TextChannel).name ?? 'unknown',
      type: message.channel.isDMBased() ? 'dm' : 'channel',
      platform: 'discord',
    }

    return {
      id: message.id,
      content: message.content,
      user,
      channel: channelInfo,
      source: 'discord',
      attachments: message.attachments.map((a) => ({
        id: a.id,
        filename: a.name,
        contentType: a.contentType ?? 'application/octet-stream',
        size: a.size,
        url: a.url,
      })),
      timestamp: message.createdAt,
      replyTo: message.reference?.messageId,
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
    if (!task || task.message.source !== 'discord') return

    const { discordMessageId, discordThinkingMessageId } = task.metadata as {
      discordMessageId: string
      discordThinkingMessageId: string
    }

    try {
      const channel = await this.client?.channels.fetch(task.message.channel.id)
      if (!channel?.isSendable()) return

      // Fetch and delete thinking message
      const thinkingMessage = await (channel as SendableChannel).messages.fetch(discordThinkingMessageId).catch(() => null)
      if (thinkingMessage) {
        await thinkingMessage.delete()
      }

      // Prepare response
      let content: string
      const MAX_LENGTH = 1900

      if (success && task.result) {
        let output = task.result.output
        if (output.length > MAX_LENGTH) {
          output = output.slice(0, MAX_LENGTH) + '\n\n... (truncated)'
        }
        content = `✅ **Task Complete**\n\n${output}`
      } else {
        const error = task.error ?? 'Unknown error'
        content = `❌ **Task Failed**\n\n${error.slice(0, MAX_LENGTH)}`
      }

      // Send or reply
      const originalMessage = await (channel as SendableChannel).messages.fetch(discordMessageId).catch(() => null)
      if (originalMessage) {
        await originalMessage.reply(content)
      } else {
        await (channel as SendableChannel).send(content)
      }

    } catch (error) {
      log.error({ taskId, error }, 'Error sending Discord result')
    }
  }
}

export const discordBot = DiscordBot.getInstance()
