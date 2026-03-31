# Changelog

## 1.0.0

### Features

- **Task Router**: Detects messages with `!task` (Discord) or `/task` (Telegram) prefixes
- **Session Bridge**: Forwards tasks to Claude Code (Anthropic API) for execution
- **Real-time Updates**: Server-Sent Events (SSE) stream for live task progress
- **Discord Integration**: Full bot support with slash commands and message handling
- **Telegram Integration**: Bot support with webhook and polling modes
- **Dashboard**: Web UI for monitoring tasks and viewing statistics
- **Task Store**: Redis/Upstash persistence with in-memory fallback
- **Rate Limiting**: Configurable request throttling
- **Error Handling**: Comprehensive error handling and logging

### API Endpoints

- `GET /api/health` - Health check
- `POST /api/webhooks/discord` - Discord interactions
- `POST /api/webhooks/telegram` - Telegram updates
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/:id` - Get task details
- `DELETE /api/tasks/:id` - Cancel task
- `GET /api/stream` - SSE for real-time updates
- `GET /api/stats` - Dashboard statistics

### Deployment

- Vercel (serverless)
- Docker (containerized)
- Self-hosted (Next.js standalone)
