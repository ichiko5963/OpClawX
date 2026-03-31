import type {
  AnalyticsMetric,
  AutomationRule,
  DepartmentSummary,
  IntegrationStatus,
  KnowledgeDoc,
  Message,
  MinutesRecord,
  SecurityControl,
  Task,
  TaskStatus,
  WorkspaceSnapshot,
} from "../types/workspace";

type CreateMessageInput = {
  author: string;
  role: string;
  department: string;
  content: string;
  attachments?: Message["attachments"];
};

type UpdateTaskInput = Partial<
  Pick<Task, "status" | "priority" | "dueAt" | "assignee" | "reminders">
>;

type CreateMinutesInput = {
  meetingTitle: string;
  agenda: string[];
  decisions: string[];
  actions: {
    title: string;
    assigneeCandidates: string[];
    dueCandidates: string[];
  }[];
  transcriptUrl?: string;
};

const messages: Message[] = [
  {
    id: "msg-101",
    author: "松岡 彩 (営業部)",
    role: "Manager",
    department: "営業",
    timestamp: "2025-02-14T08:45:00+09:00",
    content:
      "昨日の大型案件Bの議事録をナレッジ化しました。フォロータスクの担当とリマインドを整理したいので、AI提案をレビューして承認お願いします。",
    attachments: [{ type: "file", label: "B社_定例_0213.pdf" }],
    reactions: [
      { emoji: "👍", count: 6 },
      { emoji: "🧠", count: 3 },
    ],
    suggestions: [
      {
        id: "sg-1",
        title: "B社アップセル提案書の初稿作成",
        confidence: 0.91,
        dueCandidates: ["2025-02-17", "2025-02-19"],
        assigneeCandidates: ["@営業部", "@加藤"],
      },
      {
        id: "sg-2",
        title: "定例共有テンプレをナレッジに登録",
        confidence: 0.81,
        dueCandidates: ["2025-02-18"],
        assigneeCandidates: ["@CS部"],
      },
    ],
  },
  {
    id: "msg-102",
    author: "小林 遥 (プロダクト)",
    role: "Member",
    department: "プロダクト",
    timestamp: "2025-02-14T09:05:00+09:00",
    content:
      "音声アップロード > Minutes Agent で抽出されたアクション3件を承認しました。Temporalから3日前/1日前/当日AMのリマインドを設定済みです。",
    attachments: [{ type: "audio", label: "0214_tactics.m4a" }],
    reactions: [{ emoji: "✅", count: 4 }],
  },
  {
    id: "msg-103",
    author: "DevOps Agent",
    role: "Automation",
    department: "Ops",
    timestamp: "2025-02-14T09:20:00+09:00",
    content:
      "GitHub Actions workflow `weekly-digest.yml` を実行し、結果を #最新情報 チャンネルへ投稿しました。失敗ゼロ、テナント別に平均7.2%参加率向上。",
    reactions: [{ emoji: "🚀", count: 5 }],
  },
];

const tasks: Task[] = [
  {
    id: "task-201",
    title: "B社アップセル提案書 初稿",
    status: "in_progress",
    priority: "high",
    dueAt: "2025-02-19",
    assignee: "加藤 玲",
    department: "営業",
    tags: ["B社", "資料制作"],
    reminders: ["3日前", "1日前", "当日AM"],
    relatedMessageId: "msg-101",
  },
  {
    id: "task-202",
    title: "定例テンプレをナレッジ登録",
    status: "todo",
    priority: "medium",
    dueAt: "2025-02-18",
    assignee: "CS部",
    department: "CS",
    tags: ["ナレッジ"],
    reminders: ["1日前"],
  },
  {
    id: "task-203",
    title: "自己紹介ダイジェスト 2月号",
    status: "review",
    priority: "low",
    dueAt: "2025-02-16",
    assignee: "Automation Agent",
    department: "Ops",
    tags: ["自動化"],
    reminders: ["当日8:00"],
  },
  {
    id: "task-204",
    title: "GitHub連携ポリシー更新",
    status: "done",
    priority: "medium",
    dueAt: "2025-02-12",
    assignee: "SecOps",
    department: "管理",
    tags: ["セキュリティ"],
    reminders: [],
  },
];

const knowledgeDocs: KnowledgeDoc[] = [
  {
    id: "kn-301",
    title: "営業: B社 アップセル勝ち筋",
    scope: ["営業", "B社"],
    summary:
      "B社向け追加AIエージェントの期待値と必要な根拠資料を整理。ROIとタイムラインを含む。",
    updatedAt: "2025-02-14T06:30:00+09:00",
    confidence: 0.92,
    source: "doc://knowledge/b-company",
  },
  {
    id: "kn-302",
    title: "自己紹介ダイジェスト テンプレ",
    scope: ["CS", "コミュニティ"],
    summary:
      "4日に1回の自己紹介まとめテンプレ。Automation Agent が参照し、未紹介者へのリマインド文面も含む。",
    updatedAt: "2025-02-13T15:00:00+09:00",
    confidence: 0.88,
    source: "doc://knowledge/intros",
  },
];

const automationRules: AutomationRule[] = [
  {
    id: "auto-401",
    name: "イベント自動告知",
    trigger: "イベント投稿時 + 3/1/0.25日前",
    condition: "参加登録が50%未満の場合は再通知",
    action: "#イベント情報 へ告知 / メンバーDM",
    status: "active",
    lastRun: "2025-02-13T10:00:00+09:00",
  },
  {
    id: "auto-402",
    name: "週次リアクションランキング",
    trigger: "毎週月曜 09:00",
    condition: "リアクション数 >= 10",
    action: "#最新情報 にランキング投稿",
    status: "active",
    lastRun: "2025-02-12T09:00:00+09:00",
  },
  {
    id: "auto-403",
    name: "相談部屋 呼びかけ",
    trigger: "5日に1回",
    condition: "未解決スレ > 0",
    action: "#相談部屋 にヘルプ投稿",
    status: "paused",
    lastRun: "2025-02-10T08:30:00+09:00",
  },
];

const analytics: AnalyticsMetric[] = [
  { id: "metric-1", label: "参加率", value: "86%", delta: "+5pt", trend: "up" },
  {
    id: "metric-2",
    label: "平均返信速度",
    value: "14m",
    delta: "-3m",
    trend: "down",
  },
  {
    id: "metric-3",
    label: "週次自動化",
    value: "42 runs",
    delta: "+7",
    trend: "up",
  },
  {
    id: "metric-4",
    label: "RAG解決率",
    value: "78%",
    delta: "+4pt",
    trend: "up",
  },
];

const departments: DepartmentSummary[] = [
  { id: "dept-1", name: "営業部", members: 14, mentions: 23, privateRooms: 6 },
  { id: "dept-2", name: "マーケ部", members: 11, mentions: 12, privateRooms: 4 },
  { id: "dept-3", name: "プロダクト部", members: 18, mentions: 17, privateRooms: 8 },
];

const integrations: IntegrationStatus[] = [
  {
    id: "int-1",
    provider: "GitHub",
    status: "connected",
    scope: "Actions, Issues",
    lastSynced: "5m ago",
  },
  {
    id: "int-2",
    provider: "Google Calendar",
    status: "connected",
    scope: "Events",
    lastSynced: "12m ago",
  },
  {
    id: "int-3",
    provider: "Drive",
    status: "action_required",
    scope: "Docs",
    lastSynced: "2d ago",
  },
];

const securityControls: SecurityControl[] = [
  {
    id: "sec-1",
    title: "SSO (OIDC)",
    description: "本番 / ステージング必須。MFA enforced。",
    status: "enabled",
  },
  {
    id: "sec-2",
    title: "RBACレビュー",
    description: "Owner/Admin 月次レビュー。",
    status: "enabled",
  },
  {
    id: "sec-3",
    title: "SCIMプロビジョニング",
    description: "β導入予定。",
    status: "pending",
  },
];

const minutesRecords: MinutesRecord[] = [
  {
    id: "minutes-1",
    meetingTitle: "プロダクト戦略定例",
    createdAt: "2025-02-14T08:00:00+09:00",
    transcriptUrl: "https://files.chat.organ/minutes/0214.mp3",
    agenda: ["MVP進捗", "GitHub連携拡張", "RAG品質"],
    decisions: ["GitHub Actions結果スレ化を先行提供", "RAGベクトルDBをpgvectorで開始"],
    actions: [
      {
        title: "Actionsの権限ロール設計",
        assigneeCandidates: ["@DevOps", "@SecOps"],
        dueCandidates: ["2025-02-17"],
      },
      {
        title: "RAG品質テストケース作成",
        assigneeCandidates: ["@プロダクト部"],
        dueCandidates: ["2025-02-16"],
      },
    ],
  },
];

export function getWorkspaceSnapshot(): WorkspaceSnapshot {
  return {
    messages,
    tasks,
    knowledgeDocs,
    automationRules,
    analytics,
    departments,
    integrations,
    securityControls,
    minutes: minutesRecords,
  };
}

export function listMessages(): Message[] {
  return [...messages].sort((a, b) =>
    a.timestamp > b.timestamp ? -1 : a.timestamp === b.timestamp ? 0 : 1
  );
}

export function createMessage(input: CreateMessageInput): Message {
  const timestamp = new Date().toISOString();
  const newMessage: Message = {
    id: `msg-${Date.now()}`,
    timestamp,
    content: input.content,
    author: input.author,
    department: input.department,
    role: input.role,
    attachments: input.attachments,
  };
  messages.unshift(newMessage);
  return newMessage;
}

export function listTasks(status?: TaskStatus): Task[] {
  if (!status) return [...tasks];
  return tasks.filter((task) => task.status === status);
}

export function updateTask(taskId: string, payload: UpdateTaskInput): Task | null {
  const task = tasks.find((item) => item.id === taskId);
  if (!task) {
    return null;
  }
  Object.assign(task, payload);
  return task;
}

export function addTask(task: Task): Task {
  tasks.push(task);
  return task;
}

export function listKnowledgeDocs(): KnowledgeDoc[] {
  return [...knowledgeDocs];
}

export function listAutomationRules(): AutomationRule[] {
  return [...automationRules];
}

export function recordMinutes(input: CreateMinutesInput): MinutesRecord {
  const record: MinutesRecord = {
    id: `minutes-${Date.now()}`,
    meetingTitle: input.meetingTitle,
    createdAt: new Date().toISOString(),
    transcriptUrl: input.transcriptUrl,
    agenda: input.agenda,
    decisions: input.decisions,
    actions: input.actions,
  };
  minutesRecords.unshift(record);
  return record;
}
