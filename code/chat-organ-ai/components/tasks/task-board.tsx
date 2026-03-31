import type { Task, TaskStatus } from "@/lib/types/workspace";

const columns: { status: TaskStatus; label: string; accent: string }[] = [
  { status: "todo", label: "To Do", accent: "border-dashed" },
  { status: "in_progress", label: "In Flight", accent: "border-sky-400" },
  { status: "review", label: "Review", accent: "border-amber-400" },
  { status: "done", label: "Done", accent: "border-emerald-400" },
];

type Props = {
  tasks: Task[];
};

export function TaskBoard({ tasks }: Props) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {columns.map((column) => (
        <section
          key={column.status}
          className="rounded-3xl border border-border/70 bg-card p-4"
        >
          <header className="flex items-center justify-between text-sm font-semibold">
            <span>{column.label}</span>
            <span className="text-muted-foreground">
              {tasks.filter((task) => task.status === column.status).length}
            </span>
          </header>
          <div className="mt-3 space-y-3">
            {tasks
              .filter((task) => task.status === column.status)
              .map((task) => (
                <article
                  key={task.id}
                  className={`rounded-2xl border ${column.accent} border-border/80 bg-background/60 p-3 space-y-2`}
                >
                  <div className="flex items-center justify-between text-xs uppercase tracking-widest text-muted-foreground">
                    <span>{task.department}</span>
                    <span>{task.priority.toUpperCase()}</span>
                  </div>
                  <p className="text-sm font-semibold">{task.title}</p>
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p>担当: {task.assignee}</p>
                    <p>期日: {task.dueAt}</p>
                    {task.relatedMessageId && (
                      <p className="underline underline-offset-2">
                        元投稿: #{task.relatedMessageId}
                      </p>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-1 text-[11px] text-muted-foreground">
                    {task.tags.map((tag) => (
                      <span
                        key={`${task.id}-${tag}`}
                        className="rounded-full border border-border px-2 py-0.5"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </article>
              ))}
          </div>
        </section>
      ))}
    </div>
  );
}
