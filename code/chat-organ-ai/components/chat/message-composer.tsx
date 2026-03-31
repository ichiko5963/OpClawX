"use client";

import { FormEvent, useState, useTransition } from "react";

export function MessageComposer() {
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!message.trim()) return;
    setError(null);
    setUploading(true);
    startTransition(async () => {
      try {
        const response = await fetch("/api/messages", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            content: message,
            author: "あなた (Owner)",
            role: "Owner",
            department: "運営",
          }),
        });
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data?.error ?? "送信に失敗しました");
        }
        setMessage("");
      } catch (err) {
        setError(err instanceof Error ? err.message : "送信に失敗しました");
      } finally {
        setUploading(false);
      }
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-border/70 bg-background/70 p-4 space-y-3"
    >
      <textarea
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        placeholder="メンションや音声URLを貼り付け → AIにタスク化や要約を依頼"
        className="w-full resize-none rounded-xl border border-border/60 bg-transparent p-3 text-sm outline-none focus:border-foreground"
        rows={3}
      />
      <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
        <label className="flex cursor-pointer items-center gap-2 rounded-full border border-dashed border-border px-3 py-1 hover:border-foreground">
          音声ファイル
          <input
            type="file"
            accept="audio/*"
            className="hidden"
            onChange={() => setUploading(true)}
          />
        </label>
        <button
          type="button"
          className="rounded-full border border-dashed border-border px-3 py-1 hover:border-foreground"
        >
          タスク候補を抽出
        </button>
        <span className="ml-auto text-[11px] tracking-widest">
          ショートカット: ⌘ + Enter
        </span>
        <button
          type="submit"
          className="rounded-full bg-foreground px-4 py-1.5 text-xs font-semibold text-background hover:opacity-90"
          disabled={uploading || isPending}
        >
          {uploading || isPending ? "送信中..." : "送信"}
        </button>
      </div>
      {error && <p className="text-xs text-rose-500">{error}</p>}
    </form>
  );
}
