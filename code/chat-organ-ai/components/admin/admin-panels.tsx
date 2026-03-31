import type {
  DepartmentSummary,
  IntegrationStatus,
} from "@/lib/types/workspace";

type Props = {
  departments: DepartmentSummary[];
  integrations: IntegrationStatus[];
};

export function AdminPanels({ departments, integrations }: Props) {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-3">
        <header>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">
            部署 / メンション管理
          </p>
          <h3 className="text-xl font-semibold">部署メンションとプラベ自動生成</h3>
        </header>
        {departments.map((dept) => (
          <article
            key={dept.id}
            className="rounded-2xl border border-border/80 bg-background/60 p-3 space-y-1 text-sm"
          >
            <div className="flex items-center justify-between">
              <p className="font-semibold">{dept.name}</p>
              <span className="text-xs text-muted-foreground">
                @{dept.name}
              </span>
            </div>
            <p className="text-xs text-muted-foreground">
              {dept.members}名 / プライベート {dept.privateRooms}部屋 / メンション {dept.mentions}回
            </p>
            <button className="rounded-full border border-border px-3 py-1 text-xs hover:border-foreground">
              自動提案を確認
            </button>
          </article>
        ))}
      </section>

      <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-3">
        <header>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">
            インテグレーション
          </p>
          <h3 className="text-xl font-semibold">GitHub / カレンダー / ストレージ</h3>
        </header>
        {integrations.map((integration) => (
          <article
            key={integration.id}
            className="rounded-2xl border border-border/80 bg-background/60 p-3 space-y-1 text-sm"
          >
            <div className="flex items-center justify-between">
              <p className="font-semibold">{integration.provider}</p>
              <span
                className={`text-xs font-semibold ${
                  integration.status === "connected"
                    ? "text-emerald-500"
                    : "text-amber-500"
                }`}
              >
                {integration.status === "connected" ? "Connected" : "Action Required"}
              </span>
            </div>
            <p className="text-xs text-muted-foreground">
              スコープ: {integration.scope} / 最終同期 {integration.lastSynced}
            </p>
            <button className="rounded-full border border-border px-3 py-1 text-xs hover:border-foreground">
              設定を開く
            </button>
          </article>
        ))}
      </section>
    </div>
  );
}
