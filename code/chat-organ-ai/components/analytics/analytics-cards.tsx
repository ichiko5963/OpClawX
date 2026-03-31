import type { AnalyticsMetric } from "@/lib/types/workspace";

type Props = {
  metrics: AnalyticsMetric[];
};

export function AnalyticsCards({ metrics }: Props) {
  return (
    <section className="rounded-3xl border border-border/70 bg-card p-4">
      <header className="space-y-1">
        <p className="text-xs uppercase tracking-widest text-muted-foreground">
          参加状況 / 反応 / 投稿傾向
        </p>
        <h3 className="text-xl font-semibold">アナリティクス スナップショット</h3>
      </header>
      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <article
            key={metric.id}
            className="rounded-2xl border border-border/70 bg-background/60 p-4 space-y-2"
          >
            <p className="text-sm text-muted-foreground">{metric.label}</p>
            <p className="text-2xl font-semibold">{metric.value}</p>
            <p
              className={`text-xs font-semibold ${
                metric.trend === "down"
                  ? "text-rose-500"
                  : metric.trend === "up"
                  ? "text-emerald-500"
                  : "text-muted-foreground"
              }`}
            >
              {metric.delta}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
