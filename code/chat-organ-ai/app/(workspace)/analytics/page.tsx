import { AnalyticsCards } from "@/components/analytics/analytics-cards";
import { getWorkspaceSnapshot } from "@/lib/mock-data";

export default function AnalyticsPage() {
  const snapshot = getWorkspaceSnapshot();
  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs uppercase tracking-widest text-muted-foreground">
          参加状況・反応・投稿傾向
        </p>
        <h3 className="text-2xl font-semibold">アナリティクス</h3>
        <p className="text-sm text-muted-foreground">
          週次レポート / 反応ランキング / 未回答質問の検知。GitHub連携による開発メトリクスも統合予定。
        </p>
      </div>

      <AnalyticsCards metrics={snapshot.analytics} />

      <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-3">
        <h4 className="text-sm font-semibold">未回答スレッド</h4>
        <p className="text-xs text-muted-foreground">
          Automation Agent が48時間以上返信のないスレを抽出し、相談部屋でヘルプを呼びかけます。
        </p>
        <div className="grid gap-2 text-xs">
          <div className="rounded-2xl border border-border px-3 py-2">
            #相談部屋 / AI導入相談 → 最終返信 52h前
          </div>
          <div className="rounded-2xl border border-border px-3 py-2">
            #イベント情報 / 3月カンファレンス → 最終返信 60h前
          </div>
        </div>
      </section>
    </div>
  );
}
