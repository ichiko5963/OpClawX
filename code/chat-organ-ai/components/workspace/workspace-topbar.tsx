"use client";

import { useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";

const statusBadges = [
  { label: "SLO", value: "99.9%", tone: "text-emerald-500" },
  { label: "LLM稼働", value: "正常", tone: "text-sky-500" },
  { label: "Temporal", value: "132 workflows", tone: "text-amber-500" },
];

export function WorkspaceTopbar() {
  const [search, setSearch] = useState("");

  return (
    <header className="border-b border-border/70 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/70">
      <div className="flex flex-col gap-4 px-4 py-4 md:px-8 md:py-5">
        <div className="flex flex-wrap items-center gap-3">
          <div>
            <p className="text-xs uppercase tracking-widest text-muted-foreground">
              Workspace
            </p>
            <h2 className="text-2xl font-semibold">Chat Organ AI / 事業運営</h2>
          </div>
          <div className="flex flex-wrap items-center gap-2 ml-auto">
            {statusBadges.map((badge) => (
              <span
                key={badge.label}
                className={cn(
                  "rounded-full border border-border px-3 py-1 text-xs font-semibold tracking-wide",
                  badge.tone
                )}
              >
                {badge.label}: {badge.value}
              </span>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <div className="flex-1 flex items-center gap-3">
            <div className="relative flex-1">
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="メッセージ / タスク / ナレッジを横断検索"
                className="w-full rounded-2xl border border-border/70 bg-background px-4 py-2 text-sm outline-none focus:border-foreground"
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] uppercase tracking-widest text-muted-foreground">
                ⌘ /
              </span>
            </div>
            <button className="hidden md:inline-flex items-center gap-2 rounded-2xl border border-border px-4 py-2 text-sm font-semibold hover:border-foreground">
              音声アップロード
            </button>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Link className="underline-offset-4 hover:underline" href="/admin">
              ロール管理
            </Link>
            <span>•</span>
            <Link className="underline-offset-4 hover:underline" href="/settings">
              SSO/監査
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
