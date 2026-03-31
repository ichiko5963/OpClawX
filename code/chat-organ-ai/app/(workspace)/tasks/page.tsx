import { TaskBoard } from "@/components/tasks/task-board";
import { TaskStats } from "@/components/tasks/task-stats";
import { getWorkspaceSnapshot } from "@/lib/mock-data";

export default function TasksPage() {
  const snapshot = getWorkspaceSnapshot();
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">
            タスク管理
          </p>
          <h3 className="text-2xl font-semibold">部署横断タスクビュー</h3>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          <button className="rounded-full border border-border px-4 py-1.5 font-semibold hover:border-foreground">
            承認フロー設定
          </button>
          <button className="rounded-full border border-border px-4 py-1.5 font-semibold hover:border-foreground">
            リマインドテンプレ
          </button>
        </div>
      </div>

      <TaskStats tasks={snapshot.tasks} />
      <TaskBoard tasks={snapshot.tasks} />
    </div>
  );
}
