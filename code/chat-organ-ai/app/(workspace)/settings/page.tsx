import { SecurityPanel } from "@/components/settings/security-panel";
import { getWorkspaceSnapshot } from "@/lib/mock-data";

export default function SettingsPage() {
  const snapshot = getWorkspaceSnapshot();
  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs uppercase tracking-widest text-muted-foreground">
          設定 / セキュリティ
        </p>
        <h3 className="text-2xl font-semibold">SSO・RBAC・監査ログ</h3>
        <p className="text-sm text-muted-foreground">
          OIDC/OAuth2, SAML, SCIM, RBAC, 監査ログ、IP制限、暗号化設定をまとめて管理。GitHub Actions へのOIDCフェデレーションもここで設定します。
        </p>
      </div>

      <SecurityPanel controls={snapshot.securityControls} />

      <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-2 text-sm">
        <h4 className="font-semibold">監査ログエクスポート</h4>
        <p className="text-xs text-muted-foreground">
          期間とロールでフィルタし、OpenSearchからCSV/JSONをエクスポート。SCIM導入後はユーザ自動同期ログも対象。
        </p>
        <div className="flex flex-col gap-2 md:flex-row">
          <input
            className="flex-1 rounded-2xl border border-border/70 bg-background px-4 py-2 text-xs outline-none focus:border-foreground"
            placeholder="例: 2025-02-01 〜 2025-02-14 / Owner, Admin"
          />
          <button className="rounded-2xl border border-border px-4 py-2 text-xs font-semibold hover:border-foreground">
            エクスポート
          </button>
        </div>
      </section>
    </div>
  );
}
