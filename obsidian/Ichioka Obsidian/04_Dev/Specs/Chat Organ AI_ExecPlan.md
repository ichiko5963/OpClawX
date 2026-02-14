# Chat Organ AI ExecPlan

This ExecPlan is governed by the standards in `/Users/ichiokanaoto/Downloads/Ichioka Obsidian/09-開発/0_参考資料/PLANS.md.md` and must remain self-contained so that a novice can deliver Chat Organ AI per the initial requirement specification.

## Purpose / Big Picture

Organizations running business or school operations need a single workspace where chat, tasks, knowledge, automation, and AI agents operate on the same timeline. After executing this plan, a workspace owner can post a conversation, see AI-generated task suggestions, turn them into tracked assignments, surface canonical knowledge via RAG (Retrieval-Augmented Generation), trigger scheduled reminders, and audit all activity from one UI spanning web, desktop, and mobile. Success is demonstrated by running the local stack, posting a message in the chat interface, seeing it synchronized through the backend, converting part of it into a task, and receiving an automated reminder plus a knowledge answer grounded in stored documents.

## Progress

- [x] (2025-02-14 05:05Z) Captured MVP→β→GA scope and authored this baseline ExecPlan.
- [x] (2025-02-14 05:20Z) Requirements canon + domain models documented (要件定義書、ERD、AIプロンプトを追加)。
- [x] (2025-02-14 05:55Z) Workspace UIを再構築し、チャット／タスク／ナレッジ／自動化／アナリティクス／管理ページを Next.js App Router 上（`2_実装/Chat Organ AI`）に配置。
- [ ] (2025-02-14 06:15Z) Backend/automation/AI services: Next.js API層＋モックDBでAI/Minutes/Automationフローをエミュレーション（Nest/Temporal/DB実装は未着手）。
- [ ] (2025-02-14 06:10Z) Integrations, analytics, security controls, and validation suites completed.

## Surprises & Discoveries

- Observation: The only runnable app today is the `create-next-app` starter (現在は `2_実装/Chat Organ AI` 配下)、which does not include chat, task, or AI logic. Evidence: `/Users/ichiokanaoto/Downloads/Ichioka Obsidian/09-開発/2_実装/Chat Organ AI/app/page.tsx` renders the stock Next.js Supabase demo, so we must refactor it heavily rather than iterating on an existing Chat Organ AI client.
- Observation: `npm run lint` fails because既存の mastra/Excel/RAG ツール群が `require` 禁止や `any` 使用で ESLint 違反を多数抱えている。Evidence: lint ログに `src/mastra/tools/*` の警告が列挙され、新規実装コードにはエラーが出ていない。

## Decision Log

- Decision: Use the existing Next.js App Router project (現在は `2_実装/Chat Organ AI` に配置) as the foundation for the tri-platform workspace experience. Rationale: It already ships with Tailwind, theming, supabase SSR helpers, and AI SDK dependencies that align with the desired stack, reducing setup time. Date/Author: 2025-02-14 / Codex.
- Decision: Stand up a new NestJS backend with Temporal workers and PostgreSQL/Redis/OpenSearch instead of piggybacking on Supabase RPCs. Rationale: Requirements demand multi-agent orchestration, RBAC, SCIM-ready auth, automation rules, and GitHub integrations that exceed what the current frontend-only repo can provide. Date/Author: 2025-02-14 / Codex.
- Decision: Until Kubernetes/Nest 層を構築できるまでの暫定策として、Next.js API Routes とサーバーモックDBで Minutes/Automation フローをシミュレートし、UIとAPIの契約を固める。Rationale: 早期にエンドツーエンド操作感を確認しつつ、将来の Nest/Temporal 実装に差し替え可能な境界を定義できる。Date/Author: 2025-02-14 / Codex.
- Decision: すべての実装資産は `/Users/ichiokanaoto/Downloads/Ichioka Obsidian/09-開発/2_実装/<プロジェクト名>/` 配下に配置する。Rationale: ドキュメント群と整合した場所でコードを管理し、再現性とアクセス性を高めるため。Date/Author: 2025-02-14 / Codex.

## Outcomes & Retrospective

This section will track delta versus goals once implementation milestones complete. At present, no code beyond documentation has shipped, so there are no outcomes to compare except that the plan now translates the requirement definition into actionable engineering steps.

## Context and Orientation

The working tree root contains many artifacts. The relevant assets for Chat Organ AI are: (1) `/Users/ichiokanaoto/Downloads/Ichioka Obsidian/09-開発/2_実装/Chat Organ AI`, a Next.js + Supabase starter (もともと create-next-app から生成) with Tailwind and AI SDK dependencies; (2) `ChatOrganAI_UI_Mock.html`, an HTML mock that informs the chat/task UI; and (3) `ChatOrganAI_Security_Operations_Runbook.md`, which enumerates SRE/SecOps expectations. There is no backend folder yet, so all API surfaces must be introduced. Data currently lives only in CSV/HTML mock assets, so PostgreSQL schemas, Redis caches, and OpenSearch indexes will be created from scratch. Abbreviations used later: RAG means Retrieval-Augmented Generation; STT means Speech-To-Text; Temporal is an open-source workflow orchestrator that provides durable timers for reminders and automation.

## Plan of Work

Begin by codifying the textual requirements into source-controlled documents. Create `1_要件定義書/Chat Organ AI_要件定義書.md` that normalizes the user's narrative into numbered sections, plus an entity-relation diagram file under `1_要件定義書/models/chat_organ_ai_erd.drawio` summarizing Organization, User, Department, Channel, Message, Task, Minutes, KnowledgeMemory, AutomationRule, AnalyticsEvent, and Integration. Record AI prompt templates (Minutes, Knowledge, Automation) under `1_要件定義書/prompts/` and ensure every future engineer can read the canon without referring back to chat transcripts.

Next refactor `/Users/ichiokanaoto/Downloads/Ichioka Obsidian/09-開発/2_実装/Chat Organ AI` (generated via `create-next-app`) into the production workspace. Convert it into a pnpm-based app named `apps/web` to prepare for a monorepo, update `package.json` metadata (name, scripts), and add environment variables for API base URLs, WebSocket gateway, Supabase/SSO endpoints, and GitHub OAuth. Replace `app/page.tsx` with a real workspace shell that introduces navigation for Chat, Tasks, Knowledge, Automations, Analytics, Admin, and Settings. Implement chat UI in `app/(workspace)/chat/page.tsx`, reusing components in `components/` for message lists, composer, thread view, and inline task suggestion cards. Build a Task board in `app/(workspace)/tasks/page.tsx` with Kanban/Gantt toggles, a Knowledge page with scoped RAG search, an Automations builder with GUI rule nodes, an Analytics dashboard with charts, and administration panels for departments, channels, and integrations. Introduce shared hooks (`lib/data-hooks.ts`) that connect to backend REST/gRPC endpoints via tRPC-like adapters, and WebSocket listeners for real-time updates (Socket.IO client). Ensure UI-specific requirements (inline task conversion, reminder buttons, audio upload, mention pickers, private channel suggestions) have dedicated components.

Stand up the backend under `chat-organ-ai-server`. Use `nest new chat-organ-ai-server` to generate the scaffold, add modules for `auth`, `users`, `departments`, `channels`, `messages`, `tasks`, `minutes`, `knowledge`, `automations`, `integrations`, and `analytics`. Implement PostgreSQL via Prisma or TypeORM with schemas matching the ERD, configure Redis for sessions/rate limiting, and wire OpenSearch + pgvector for search/RAG indexes. Add Socket.IO gateway for chats/tasks, REST controllers for CRUD operations, Temporal workers (in `server/workers/`) for reminders and automation rules, and a transcription service wrapper (Whisper) for audio ingestion. Provide GitHub integration service (Actions dispatch, PR/Issue linking), calendar/webhook connectors, and RBAC middleware supporting Owner/Admin/Manager/Member/Guest roles. Expose gRPC endpoints for AI agents to request metadata.

Add AI/automation services under `ai/` with LangGraph or custom orchestration. Define `ai/minutes-agent.ts` to accept audio transcripts, summarize agendas/decisions/actions, propose assignees/due candidates, and push candidate tasks to the backend via REST. Define `ai/knowledge-agent.ts` to select a memory scope, run semantic search, and return answers with citations. Define `ai/automation-agent.ts` to ingest Temporal-triggered rules, enforce guardrails, and log tool calls. Provide `ai/devops-agent.ts` to call GitHub Actions and summarize outputs. Store prompts and guardrail policies in version control and load provider keys through configuration.

Introduce infrastructure, analytics, and security layers. Author Terraform modules under `infra/terraform` for PostgreSQL, Redis, OpenSearch, S3-compatible storage, Kubernetes clusters, and Temporal. Containerize frontend, backend, and workers via Dockerfiles under each app, add GitHub Actions workflows for CI/CD with lint/test/build/deploy stages, integrate OIDC-based secrets, and provide monitoring dashboards (OpenTelemetry exporters, Prometheus, Grafana). Implement analytics aggregators in `server/src/analytics/analytics.service.ts` to compute participation rates, reaction trends, unanswered threads, and weekly digest data, pushing results to the frontend via scheduled jobs. Wire audit logging middleware for all privileged operations and build export endpoints.

Finally, define validation assets and onboarding templates. Create automated tests (frontend Playwright, backend Jest/e2e, worker integration). Populate seed data scripts (departments, templates, automation presets) under `scripts/seeds/`. Document runbooks referencing `ChatOrganAI_Security_Operations_Runbook.md`, ensuring SSO, RBAC, and audit requirements are verifiable. Keep the ExecPlan updated as features land.

## Concrete Steps

Run dependency installs for the frontend:

    cd "/Users/ichiokanaoto/Downloads/Ichioka Obsidian/09-開発/2_実装/Chat Organ AI"
    npm install

Migrate the project into a pnpm-based monorepo structure (if/when needed):

    cd "/Users/ichiokanaoto/Downloads/Ichioka Obsidian/09-開発/2_実装"
    pnpm dlx create-turbo@latest chat-organ-ai && mv "Chat Organ AI" chat-organ-ai/apps/web

Bootstrap the backend service:

    cd /Users/ichiokanaoto/chat-organ-ai
    npx @nestjs/cli new chat-organ-ai-server --package-manager pnpm

Provision local databases and search services (assuming Docker Compose yields Postgres, Redis, OpenSearch, MinIO, Temporal, pgvector):

    docker compose -f infra/docker-compose.dev.yml up -d

Generate Prisma/TypeORM migrations to create tables described in the ERD:

    cd chat-organ-ai/apps/server
    pnpm prisma migrate dev --name init_core_schema

Stand up Temporal workers and AI agents:

    pnpm --filter automation-worker dev
    pnpm --filter ai-agents dev

Launch the frontend and backend for manual testing:

    pnpm --filter web dev
    pnpm --filter chat-organ-ai-server start:dev

## Validation and Acceptance

Acceptance requires exercising the end-to-end workflow locally. Start the backend, workers, and frontend. Log in via SSO stub, create a workspace, invite at least one department, and open the Chat view. Post a message containing action items; verify AI inline suggestions appear and that accepting one creates a task visible in the Task board with reminder defaults (3/1/0.25 days). Upload an audio file; validate that the Minutes Agent transcription produces agendas/decisions/actions, that a user can approve them, and that reminders fire through Temporal timers (observable in logs). Ask a question in Knowledge; ensure the RAG response cites stored documents. Trigger an automation rule (e.g., weekly digest) and observe the resulting post in the appropriate channel plus analytics updates. Confirm GitHub PR links expand with metadata and that Actions runs can be dispatched and summarized. Run `pnpm lint`, `pnpm test`, `pnpm --filter web test:e2e`, and backend `pnpm test:e2e` suites; they must pass before declaring success.

## Idempotence and Recovery

Terraform and Docker Compose definitions must be written to allow repeated `apply` or `up` invocations without side effects; use immutable tagging for container images and wrap destructive migrations inside explicit confirmations. Database migrations should be resumable; keep snapshots before applying breaking changes. Temporal workflows are deterministic and can be restarted; provide scripts to reset stuck executions. Automation rules and AI operations must store last-run markers so reprocessing does not duplicate posts. Provide rollback procedures (e.g., `pnpm prisma migrate resolve --rolled-back`) and document how to disable agents or automations safely.

## Artifacts and Notes

Capture critical evidence during implementation, such as ERD exports, screenshot of the workspace, log excerpts proving AI grounding, and sample automation payloads. Store them under `artifacts/chat-organ-ai/` with concise readme files explaining what each artifact demonstrates. For illustration, keep a JSON example of Minutes Agent output (`artifacts/chat-organ-ai/minutes-sample.json`) and a GraphQL/REST transcript showing a task being created through AI suggestion.

## Interfaces and Dependencies

Frontend depends on Next.js 15, Tailwind, Radix UI, Supabase auth helpers, Socket.IO client, and the AI SDK packages already declared. Backend depends on NestJS, TypeORM/Prisma, PostgreSQL with pgvector extension, Redis, OpenSearch, S3-compatible storage, Temporal, Whisper-compatible STT, and GitHub/Google Calendar APIs. Core HTTP endpoints include `POST /messages`, `POST /tasks`, `POST /minutes`, `POST /automations/rules`, and `GET /analytics/engagement`. WebSocket channels stream `message.created`, `task.updated`, and `automation.executed` events. gRPC services expose `ai.MinutesService/SubmitTranscript` and `ai.AutomationService/ExecuteRule`. All interactions must enforce RBAC per Owner/Admin/Manager/Member/Guest definitions. External dependencies must be abstracted via provider interfaces (`server/src/integrations/github/github.service.ts`, `server/src/integrations/calendar/calendar.service.ts`) so they can be mocked during tests.

Change Record: 2025-02-14 – Initial ExecPlan authored from requirement definition to guide full-stack implementation.  
Change Record: 2025-02-14 – Requirements canon, ERD, and agent prompts committed to satisfy Step 1 foundations.  
Change Record: 2025-02-14 – Workspace UIをChat Organ AI仕様で再構築し、主要画面とデータスナップショットを実装。  
Change Record: 2025-02-14 – Next.js API層とモックDBを導入し、/api/messages,/tasks,/minutes,/automations/rules,/workspace エンドポイントでAI/Minutes/Automationフローをエミュレーション。  
Change Record: 2025-02-14 – プロジェクト一式を `2_実装/Chat Organ AI` 配下へ移し、以降の作業パスとREADMEを新ルールに合わせて更新。
