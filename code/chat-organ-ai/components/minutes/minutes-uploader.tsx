"use client";

import { FormEvent, useState } from "react";

export function MinutesUploader() {
  const [meetingTitle, setMeetingTitle] = useState("定例ミーティング");
  const [agenda, setAgenda] = useState("タスク進捗, RAG品質確認");
  const [decisions, setDecisions] = useState("アップセル資料化, Temporal導入延伸");
  const [actions, setActions] = useState(
    "Actions権限設計:@DevOps;2025-02-17|RAGテストケース:@プロダクト;2025-02-16"
  );
  const [status, setStatus] = useState<"idle" | "submitting" | "done" | "error">(
    "idle"
  );
  const [message, setMessage] = useState("");

  function resetForm() {
    setMeetingTitle("");
    setAgenda("");
    setDecisions("");
    setActions("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("submitting");
    setMessage("");
    try {
      const payload = {
        meetingTitle,
        agenda: agenda.split(",").map((item) => item.trim()),
        decisions: decisions.split(",").map((item) => item.trim()),
        actions: actions.split("|").map((item) => {
          const [titlePart, assigneePart] = item.split(":");
          const [assignees, due] = assigneePart?.split(";") ?? [];
          return {
            title: titlePart?.trim() ?? "",
            assigneeCandidates: assignees
              ?.split(",")
              .map((candidate) => candidate.trim()) ?? [],
            dueCandidates: due ? [due.trim()] : [],
          };
        }),
      };

      const response = await fetch("/api/minutes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data?.error ?? "Minutes登録に失敗しました");
      }

      setStatus("done");
      setMessage("Minutesを登録し、アクションからタスクを生成しました。");
      resetForm();
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "予期しないエラーです");
    }
  }

  return (
    <section className="rounded-3xl border border-border/70 bg-card p-4 space-y-3">
      <header>
        <p className="text-xs uppercase tracking-widest text-muted-foreground">
          Minutes Agent Input
        </p>
        <h3 className="text-xl font-semibold">議事録アップロード</h3>
        <p className="text-xs text-muted-foreground">
          音声URLと議事録プロンプトを送ると、Minutes Agent が JSON を返却し /api/minutes に投稿します。
        </p>
      </header>
      <form onSubmit={handleSubmit} className="space-y-2 text-sm">
        <label className="space-y-1">
          <span className="text-xs text-muted-foreground">タイトル</span>
          <input
            value={meetingTitle}
            onChange={(event) => setMeetingTitle(event.target.value)}
            className="w-full rounded-xl border border-border/70 bg-background px-3 py-2 text-sm outline-none focus:border-foreground"
            required
          />
        </label>
        <label className="space-y-1">
          <span className="text-xs text-muted-foreground">議題（カンマ区切り）</span>
          <input
            value={agenda}
            onChange={(event) => setAgenda(event.target.value)}
            className="w-full rounded-xl border border-border/70 bg-background px-3 py-2 text-sm outline-none focus:border-foreground"
          />
        </label>
        <label className="space-y-1">
          <span className="text-xs text-muted-foreground">決定事項（カンマ区切り）</span>
          <input
            value={decisions}
            onChange={(event) => setDecisions(event.target.value)}
            className="w-full rounded-xl border border-border/70 bg-background px-3 py-2 text-sm outline-none focus:border-foreground"
          />
        </label>
        <label className="space-y-1">
          <span className="text-xs text-muted-foreground">
            アクション（タイトル:担当,担当;期日 | ...)
          </span>
          <textarea
            value={actions}
            onChange={(event) => setActions(event.target.value)}
            rows={3}
            className="w-full rounded-xl border border-border/70 bg-background px-3 py-2 text-sm outline-none focus:border-foreground"
          />
        </label>
        <button
          type="submit"
          className="w-full rounded-2xl bg-foreground py-2 text-sm font-semibold text-background"
          disabled={status === "submitting"}
        >
          {status === "submitting" ? "送信中..." : "Minutesを登録"}
        </button>
        {message && (
          <p
            className={`text-xs ${
              status === "error" ? "text-rose-500" : "text-emerald-500"
            }`}
          >
            {message}
          </p>
        )}
      </form>
    </section>
  );
}
