import type { SecurityControl } from "@/lib/types/workspace";

type Props = {
  controls: SecurityControl[];
};

export function SecurityPanel({ controls }: Props) {
  return (
    <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-3">
      <header>
        <p className="text-xs uppercase tracking-widest text-muted-foreground">
          SSO / RBAC / 監査
        </p>
        <h3 className="text-xl font-semibold">セキュリティ統制の状態</h3>
        <p className="text-sm text-muted-foreground">
          OIDC, SAML, SCIM, 監査ログ, テナント分離の稼働状況を一覧化。
        </p>
      </header>
      {controls.map((control) => (
        <article
          key={control.id}
          className="rounded-2xl border border-border/80 bg-background/60 p-3 space-y-1 text-sm"
        >
          <div className="flex items-center justify-between">
            <p className="font-semibold">{control.title}</p>
            <span
              className={`text-xs font-semibold ${
                control.status === "enabled"
                  ? "text-emerald-500"
                  : control.status === "pending"
                  ? "text-amber-500"
                  : "text-rose-500"
              }`}
            >
              {control.status.toUpperCase()}
            </span>
          </div>
          <p className="text-xs text-muted-foreground">{control.description}</p>
          <button className="rounded-full border border-border px-3 py-1 text-xs hover:border-foreground">
            詳細 / 監査ログ
          </button>
        </article>
      ))}
    </section>
  );
}
