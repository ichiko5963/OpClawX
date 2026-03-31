export type WorkspaceNavItem = {
  href: string;
  label: string;
  hint?: string;
};

export type MessageReaction = {
  emoji: string;
  count: number;
};

export type TaskSuggestion = {
  id: string;
  title: string;
  confidence: number;
  dueCandidates: string[];
  assigneeCandidates: string[];
};

export type Message = {
  id: string;
  author: string;
  role: string;
  department: string;
  timestamp: string;
  content: string;
  attachments?: { type: "audio" | "file"; label: string }[];
  reactions?: MessageReaction[];
  suggestions?: TaskSuggestion[];
};

export type TaskStatus = "todo" | "in_progress" | "review" | "done";
export type TaskPriority = "low" | "medium" | "high";

export type Task = {
  id: string;
  title: string;
  status: TaskStatus;
  priority: TaskPriority;
  dueAt: string;
  assignee: string;
  department: string;
  tags: string[];
  reminders: string[];
  relatedMessageId?: string;
};

export type KnowledgeDoc = {
  id: string;
  title: string;
  scope: string[];
  summary: string;
  updatedAt: string;
  confidence: number;
  source: string;
};

export type AutomationRule = {
  id: string;
  name: string;
  trigger: string;
  condition: string;
  action: string;
  status: "active" | "paused";
  lastRun: string;
};

export type AnalyticsMetric = {
  id: string;
  label: string;
  value: string;
  delta: string;
  trend: "up" | "down" | "flat";
};

export type DepartmentSummary = {
  id: string;
  name: string;
  members: number;
  mentions: number;
  privateRooms: number;
};

export type IntegrationStatus = {
  id: string;
  provider: string;
  status: "connected" | "action_required";
  scope: string;
  lastSynced: string;
};

export type SecurityControl = {
  id: string;
  title: string;
  description: string;
  status: "enabled" | "disabled" | "pending";
};

export type MinutesRecord = {
  id: string;
  meetingTitle: string;
  createdAt: string;
  transcriptUrl?: string;
  agenda: string[];
  decisions: string[];
  actions: {
    title: string;
    assigneeCandidates: string[];
    dueCandidates: string[];
  }[];
};

export type WorkspaceSnapshot = {
  messages: Message[];
  tasks: Task[];
  knowledgeDocs: KnowledgeDoc[];
  automationRules: AutomationRule[];
  analytics: AnalyticsMetric[];
  departments: DepartmentSummary[];
  integrations: IntegrationStatus[];
  securityControls: SecurityControl[];
  minutes: MinutesRecord[];
};
