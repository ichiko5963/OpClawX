import { KnowledgePanel } from "@/components/knowledge/knowledge-panel";
import { getWorkspaceSnapshot } from "@/lib/mock-data";

export default function KnowledgePage() {
  const snapshot = getWorkspaceSnapshot();
  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-3">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">
            ナレッジ検索
          </p>
          <h3 className="text-2xl font-semibold">
            スコープ自動推定 + 根拠提示つきRAG
          </h3>
        </div>
        <div className="flex flex-col gap-3 md:flex-row">
          <input
            className="flex-1 rounded-2xl border border-border/70 bg-background px-4 py-2 text-sm outline-none focus:border-foreground"
            placeholder="例: B社・営業資料テンプレ / 自己紹介ダイジェスト"
          />
          <button className="rounded-2xl bg-foreground px-6 py-2 text-sm font-semibold text-background">
            質問する
          </button>
        </div>
        <p className="text-xs text-muted-foreground">
          メモリ階層: 個人トーン / チームナレッジ / 部署 / プロジェクト / 機密。RAGの根拠はDocIDと引用箇所を表示。
        </p>
      </section>

      <KnowledgePanel docs={snapshot.knowledgeDocs} />
    </div>
  );
}
