import Anthropic from '@anthropic-ai/sdk'
import { TaskResult, Artifact } from '@/types'
import { TaskHandler, ExecutionContext } from './task-executor'
import { getConfig } from './config'
import logger, { createChildLogger } from './logger'

const log = createChildLogger('ClaudeHandler')

export function createClaudeHandler(): TaskHandler {
  const config = getConfig()

  if (!config.claude.apiKey) {
    log.warn('No Anthropic API key configured, using mock handler')
    return createMockHandler()
  }

  const anthropic = new Anthropic({
    apiKey: config.claude.apiKey,
  })

  return async (context: ExecutionContext): Promise<TaskResult> => {
    const { taskId, prompt, onProgress, onLog, onArtifact } = context

    onProgress('Initializing Claude Code session...', 10)
    onLog('info', 'Starting Claude Code session', { model: config.claude.model })

    const startTime = Date.now()

    try {
      onProgress('Sending request to Claude...', 30)

      const response = await anthropic.messages.create({
        model: config.claude.model,
        max_tokens: config.claude.maxTokens,
        temperature: config.claude.temperature,
        system: `You are Claude Code, an AI assistant integrated into a task execution system. 
You help users by executing tasks, writing code, analyzing data, and providing detailed responses.
When writing code, always use proper markdown code blocks with language identifiers.
When providing files or artifacts, clearly indicate them with [ARTIFACT:filename] tags.`,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
        stream: true,
      })

      onProgress('Receiving response stream...', 50)

      let fullResponse = ''
      let inputTokens = 0
      let outputTokens = 0

      for await (const chunk of response) {
        if (chunk.type === 'message_start') {
          inputTokens = chunk.message.usage?.input_tokens ?? 0
        } else if (chunk.type === 'content_block_delta') {
          if (chunk.delta.type === 'text_delta') {
            fullResponse += chunk.delta.text
          }
        } else if (chunk.type === 'message_delta') {
          outputTokens = chunk.usage?.output_tokens ?? 0
        }

        // Emit progress periodically
        if (fullResponse.length % 500 === 0) {
          onProgress(`Processing... (${fullResponse.length} chars)`, 50 + Math.min(40, fullResponse.length / 100))
        }
      }

      onProgress('Processing artifacts...', 90)

      // Extract artifacts from the response
      const artifacts = extractArtifacts(fullResponse)
      for (const artifact of artifacts) {
        onArtifact(artifact)
      }

      const executionTimeMs = Date.now() - startTime

      onProgress('Complete!', 100)
      onLog('info', 'Claude response received', {
        inputTokens,
        outputTokens,
        executionTimeMs,
      })

      return {
        success: true,
        output: fullResponse,
        artifacts: artifacts.length > 0 ? artifacts : undefined,
        executionTimeMs,
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      log.error({ taskId, error: errorMessage }, 'Claude API error')
      throw error
    }
  }
}

function extractArtifacts(content: string): Artifact[] {
  const artifacts: Artifact[] = []

  // Extract code blocks
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g
  let match
  let index = 0

  while ((match = codeBlockRegex.exec(content)) !== null) {
    const [, lang, code] = match
    const filename = extractFilenameFromContext(content, match.index) || `snippet-${++index}.${lang || 'txt'}`

    artifacts.push({
      id: `artifact-${Date.now()}-${index}`,
      type: 'code',
      name: filename,
      content: code.trim(),
      mimeType: getMimeTypeFromLang(lang),
    })
  }

  // Extract explicit artifact tags
  const artifactRegex = /\[ARTIFACT:([^\]]+)\]\n?([\s\S]*?)(?=\[ARTIFACT:|$)/g
  while ((match = artifactRegex.exec(content)) !== null) {
    const [, filename, artifactContent] = match

    artifacts.push({
      id: `artifact-${Date.now()}-${++index}`,
      type: 'file',
      name: filename.trim(),
      content: artifactContent.trim(),
    })
  }

  return artifacts
}

function extractFilenameFromContext(content: string, position: number): string | undefined {
  // Look for filename hints before the code block
  const before = content.slice(Math.max(0, position - 200), position)
  const filenameMatch = before.match(/(?:file|filename|path)[`:]\s*['"]?([^'"\n]+)['"]?/i)
  return filenameMatch?.[1]
}

function getMimeTypeFromLang(lang?: string): string {
  const mimeTypes: Record<string, string> = {
    'typescript': 'text/typescript',
    'ts': 'text/typescript',
    'javascript': 'text/javascript',
    'js': 'text/javascript',
    'python': 'text/python',
    'py': 'text/python',
    'json': 'application/json',
    'html': 'text/html',
    'css': 'text/css',
    'markdown': 'text/markdown',
    'md': 'text/markdown',
    'yaml': 'text/yaml',
    'yml': 'text/yaml',
    'sql': 'text/sql',
  }

  return mimeTypes[lang?.toLowerCase() ?? ''] ?? 'text/plain'
}

function createMockHandler(): TaskHandler {
  return async (context: ExecutionContext): Promise<TaskResult> => {
    const { prompt, onProgress, onLog } = context

    onProgress('Processing (MOCK MODE - no API key configured)...', 50)
    onLog('warn', 'Running in mock mode - Anthropic API key not configured')

    // Simulate processing delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    return {
      success: true,
      output: `## Mock Response\n\nReceived prompt:\n\`\`\`\n${prompt}\n\`\`\`\n\nThis is a mock response. To get real Claude responses, please configure the ANTHROPIC_API_KEY environment variable.`,
      executionTimeMs: 1000,
    }
  }
}
