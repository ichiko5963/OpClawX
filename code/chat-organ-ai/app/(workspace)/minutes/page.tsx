import { MinutesList } from "@/components/minutes/minutes-list";
import { MinutesUploader } from "@/components/minutes/minutes-uploader";
import { getWorkspaceSnapshot } from "@/lib/mock-data";

export default function MinutesPage() {
  const snapshot = getWorkspaceSnapshot();
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(320px,1fr)]">
      <MinutesList minutes={snapshot.minutes} />
      <div className="space-y-4">
        <MinutesUploader />
        <section className="rounded-3xl border border-border/70 bg-card p-4 text-sm">
          <h4 className="text-sm font-semibold">Minutes APIの使い方</h4>
          <p className="text-xs text-muted-foreground">
            音声をアップロードすると、Minutes Agent が `POST /api/minutes` に JSON を送信し、
            承認待ちタスクを生成します。Temporal導入後は `minutes.workflow` から自動的に
            3/1/0.25日前のリマインドを設定できます。
          </p>
        </section>
      </div>
    </div>
  );
}
