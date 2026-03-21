import { CommandParseResult } from '@/types'

const COMMAND_PREFIXES = ['!task', '/task', '!claude', '/claude']

export function parseCommand(content: string): CommandParseResult {
  const trimmed = content.trim()

  // Find matching prefix
  const prefix = COMMAND_PREFIXES.find((p) => trimmed.toLowerCase().startsWith(p.toLowerCase()))

  if (!prefix) {
    return {
      isCommand: false,
      prefix: '',
      command: '',
      args: '',
      flags: {},
    }
  }

  // Remove prefix and trim
  const withoutPrefix = trimmed.slice(prefix.length).trim()

  // Parse flags (--flag or --key=value)
  const flags: Record<string, string | boolean> = {}
  const flagRegex = /--(\w+)(?:=(\S+))?/g
  let args = withoutPrefix

  let match
  while ((match = flagRegex.exec(withoutPrefix)) !== null) {
    const [, key, value] = match
    flags[key] = value ?? true
    // Remove flag from args
    args = args.replace(match[0], '').trim()
  }

  // Extract command (first word) and remaining args
  const parts = args.split(/\s+/)
  const command = parts[0] ?? ''
  const remainingArgs = parts.slice(1).join(' ')

  return {
    isCommand: true,
    prefix,
    command,
    args: remainingArgs,
    flags,
  }
}

export function extractPrompt(content: string, prefix: string): string {
  const withoutPrefix = content.slice(prefix.length).trim()

  // Remove flags
  const flagRegex = /--\w+(?:=\S+)?/g
  return withoutPrefix.replace(flagRegex, '').trim()
}

export function isTaskCommand(content: string): boolean {
  return COMMAND_PREFIXES.some((p) => content.trim().toLowerCase().startsWith(p.toLowerCase()))
}
