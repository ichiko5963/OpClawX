import { ChatTimeline } from "@/components/chat/chat-timeline";
import { getWorkspaceSnapshot } from "@/lib/mock-data";

export default function ChatPage() {
  const snapshot = getWorkspaceSnapshot();
  const reminders = snapshot.tasks
    .filter((task) => task.status !== "done")
    .map((task) => ({
      id: task.id,
      title: task.title,
      dueAt: task.dueAt,
      assignee: task.assignee,
      reminders: task.reminders,
    }))
    .slice(0, 3);

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(300px,1fr)]">
      <ChatTimeline messages={snapshot.messages} />

      <aside className="space-y-4">
        <section className="rounded-3xl border border-border/70 bg-card p-4">
          <h3 className="text-sm font-semibold">Minutes Agent / 音声要約</h3>
          <p className="mt-1 text-xs text-muted-foreground">
            直近の会議音声 3件を要約済み。アクションは承認済みでタスク化されました。
          </p>
          <ul className="mt-3 space-y-2 text-xs text-muted-foreground">
            <li>• プロダクト戦略定例 → 3アクション、2タスク承認待ち</li>
            <li>• B社営業定例 → 2アクション、全部承認済み</li>
            <li>• 週次全社会 → Minutes Agent が草案を投稿</li>
          </ul>
        </section>

        <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-3">
          <h3 className="text-sm font-semibold">リマインド予定 (Temporal)</h3>
          {reminders.map((reminder) => (
            <article
              key={reminder.id}
              className="rounded-2xl border border-border/80 bg-background/60 p-3 text-xs"
            >
              <p className="font-semibold">{reminder.title}</p>
              <p className="text-muted-foreground">
                {reminder.assignee} / 期日 {reminder.dueAt}
              </p>
              <p className="text-muted-foreground">
                リマインド: {reminder.reminders.join(" / ") || "未設定"}
              </p>
              <button className="mt-2 rounded-full border border-border px-3 py-1 text-[11px] hover:border-foreground">
                カスタム通知を追加
              </button>
            </article>
          ))}
        </section>

        <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-2">
          <h3 className="text-sm font-semibold">自動化の健康状態</h3>
          <p className="text-xs text-muted-foreground">
            Automation Agent: 42ルール稼働 / 失敗 0 / GitHub Actions 2件待機。
          </p>
          <button className="rounded-full border border-border px-3 py-1 text-xs hover:border-foreground">
            ルールログを開く
          </button>
        </section>
      </aside>
    </div>
  );
}
