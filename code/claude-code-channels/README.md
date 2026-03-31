# Claude Code Channels

Remote task execution via Discord/Telegram messages with Claude Code integration.

## Features

- **Task Router**: Detect messages with `!task` or `/task` prefixes
- **Session Bridge**: Forward tasks to Claude Code for execution
- **Real-time Updates**: Stream execution progress via Server-Sent Events
- **Multi-platform**: Supports Discord and Telegram
- **Dashboard**: Web interface to monitor tasks

## Quick Start

### 1. Clone and Install

```bash
git clone <repository>
cd claude-code-channels
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env.local` and fill in your credentials:

```bash
cp .env.example .env.local
```

Required environment variables:

```env
# Discord (optional - disable by leaving blank)
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_APPLICATION_ID=your_app_id
DISCORD_PUBLIC_KEY=your_public_key

# Telegram (optional - disable by leaving blank)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Anthropic/Claude (required for AI responses)
ANTHROPIC_API_KEY=your_anthropic_api_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Redis/Upstash (optional - uses memory if not configured)
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token

# App
APP_URL=https://your-app.vercel.app
```

### 3. Run Development Server

```bash
npm run dev
```

Visit `http://localhost:3000` for the dashboard.

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import to Vercel
3. Add environment variables
4. Deploy

For Discord webhooks, set the webhook URL in Discord Developer Portal to:
```
https://your-app.vercel.app/api/webhooks/discord
```

For Telegram, set the webhook:
```bash
curl -F "url=https://your-app.vercel.app/api/webhooks/telegram" \
  https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
```

## Usage

### Discord

In allowed channels or DMs:
```
!task Write a Python function to sort a list
```

### Telegram

In allowed chats:
```
/task Summarize this article
```

### API

```bash
curl -X POST http://localhost:3000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing"}'
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   Discord   │     │  Telegram   │     │      API        │
└──────┬──────┘     └──────┬──────┘     └────────┬────────┘
       │                   │                      │
       └───────────────────┼──────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Task Router │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ Task Store  │
                    └──────┬──────┘
                           │
                    ┌──────▼────────┐
                    │Task Executor  │
                    └──────┬────────┘
                           │
                    ┌──────▼────────┐
                    │Claude Handler │
                    └──────┬────────┘
                           │
                    ┌──────▼────────┐
                    │  Anthropic    │
                    │     API       │
                    └───────────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/tasks` | GET | List tasks |
| `/api/tasks` | POST | Create task |
| `/api/tasks/:id` | GET | Get task details |
| `/api/tasks/:id` | DELETE | Cancel/delete task |
| `/api/stream` | GET | SSE for real-time updates |
| `/api/stats` | GET | Dashboard statistics |
| `/api/webhooks/discord` | POST | Discord webhook |
| `/api/webhooks/telegram` | POST | Telegram webhook |

## License

MIT
