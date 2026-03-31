import type { KnowledgeDoc } from "@/lib/types/workspace";

type Props = {
  docs: KnowledgeDoc[];
};

export function KnowledgePanel({ docs }: Props) {
  return (
    <section className="space-y-4 rounded-3xl border border-border/70 bg-card p-4">
      <header className="space-y-1">
        <p className="text-xs uppercase tracking-widest text-muted-foreground">
          RAGメモリ
        </p>
        <h3 className="text-xl font-semibold">ナレッジ回答と根拠</h3>
      </header>
      <div className="space-y-3">
        {docs.map((doc) => (
          <article
            key={doc.id}
            className="rounded-2xl border border-border/80 p-4 space-y-2"
          >
            <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <span className="rounded-full border border-border px-2 py-0.5">
                {doc.scope.join(" / ")}
              </span>
              <span>最終更新 {doc.updatedAt}</span>
              <span>信頼度 {(doc.confidence * 100).toFixed(0)}%</span>
            </div>
            <h4 className="text-sm font-semibold">{doc.title}</h4>
            <p className="text-sm text-muted-foreground">{doc.summary}</p>
            <p className="text-xs text-blue-500 underline underline-offset-4">
              {doc.source}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
