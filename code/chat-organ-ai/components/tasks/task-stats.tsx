import type { Task } from "@/lib/types/workspace";

type Props = {
  tasks: Task[];
};

const statusLabels: Record<string, string> = {
  todo: "未着手",
  in_progress: "進行中",
  review: "レビュー",
  done: "完了",
};

export function TaskStats({ tasks }: Props) {
  const total = tasks.length || 1;
  const segments = Object.entries(statusLabels).map(([status, label]) => {
    const count = tasks.filter((task) => task.status === status).length;
    const percentage = Math.round((count / total) * 100);
    return { label, count, percentage };
  });

  return (
    <section className="rounded-3xl border border-border/70 bg-card p-4">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">
            進捗サマリ
          </p>
          <h3 className="text-lg font-semibold">部署横断ビュー</h3>
        </div>
        <button className="rounded-full border border-border px-4 py-1 text-xs font-semibold hover:border-foreground">
          CSVエクスポート
        </button>
      </header>
      <div className="mt-4 grid gap-3 text-sm">
        {segments.map((segment) => (
          <div key={segment.label} className="space-y-1">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>{segment.label}</span>
              <span>
                {segment.count}件 ({segment.percentage}%)
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-foreground/5">
              <div
                className="h-2 rounded-full bg-foreground"
                style={{ width: `${segment.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
