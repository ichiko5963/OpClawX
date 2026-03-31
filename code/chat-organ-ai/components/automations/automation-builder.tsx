import type { AutomationRule } from "@/lib/types/workspace";

type Props = {
  rules: AutomationRule[];
};

export function AutomationBuilder({ rules }: Props) {
  return (
    <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-4">
      <header>
        <p className="text-xs uppercase tracking-widest text-muted-foreground">
          Automation Agent
        </p>
        <h3 className="text-xl font-semibold">GUIルールビルダー</h3>
        <p className="text-sm text-muted-foreground">
          トリガー / 条件 / フィルタ / アクションをドラッグして連結。Temporalで冪等実行。
        </p>
      </header>
      <div className="grid gap-3 md:grid-cols-2">
        {rules.map((rule) => (
          <article
            key={rule.id}
            className="rounded-2xl border border-border/80 bg-background/60 p-4 space-y-2"
          >
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span className="rounded-full border border-border px-2 py-0.5">
                {rule.status === "active" ? "Active" : "Paused"}
              </span>
              <span>Last run {rule.lastRun}</span>
            </div>
            <h4 className="text-sm font-semibold">{rule.name}</h4>
            <div className="text-xs text-muted-foreground space-y-1">
              <p>Trigger: {rule.trigger}</p>
              <p>Condition: {rule.condition}</p>
              <p>Action: {rule.action}</p>
            </div>
            <div className="flex flex-wrap gap-2 text-xs">
              <button className="rounded-full border border-border px-3 py-1 hover:border-foreground">
                実行
              </button>
              <button className="rounded-full border border-border px-3 py-1 hover:border-foreground">
                編集
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
