import type { MinutesRecord } from "@/lib/types/workspace";

type Props = {
  minutes: MinutesRecord[];
};

export function MinutesList({ minutes }: Props) {
  return (
    <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-4">
      <header>
        <p className="text-xs uppercase tracking-widest text-muted-foreground">
          Minutes Agent
        </p>
        <h3 className="text-xl font-semibold">議事録とアクション</h3>
        <p className="text-sm text-muted-foreground">
          音声→要約→アクション抽出→タスク化をワンクリックで承認。
        </p>
      </header>
      <div className="space-y-3">
        {minutes.map((record) => (
          <article
            key={record.id}
            className="rounded-2xl border border-border/80 bg-background/60 p-4 space-y-2"
          >
            <div className="flex flex-wrap items-center justify-between text-xs text-muted-foreground">
              <span>{record.meetingTitle}</span>
              <span>{record.createdAt}</span>
            </div>
            {record.transcriptUrl && (
              <a
                href={record.transcriptUrl}
                className="text-xs text-blue-500 underline underline-offset-4"
              >
                transcript
              </a>
            )}
            <div className="text-xs text-muted-foreground space-y-1">
              <p>議題: {record.agenda.join(" / ")}</p>
              <p>決定事項: {record.decisions.join(" / ")}</p>
            </div>
            <div className="space-y-2">
              {record.actions.map((action, index) => (
                <div
                  key={`${record.id}-${index}`}
                  className="rounded-xl border border-dashed border-border px-3 py-2 text-xs"
                >
                  <p className="font-semibold text-foreground">{action.title}</p>
                  <p className="text-muted-foreground">
                    候補担当: {action.assigneeCandidates.join(", ") || "未割当"}
                  </p>
                  <p className="text-muted-foreground">
                    期日候補: {action.dueCandidates.join(" / ") || "未設定"}
                  </p>
                  <div className="mt-2 flex gap-2 text-[11px]">
                    <button className="rounded-full bg-foreground px-3 py-1 font-semibold text-background">
                      承認してタスク化
                    </button>
                    <button className="rounded-full border border-border px-3 py-1">
                      修正
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
