"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { ThemeSwitcher } from "@/components/theme-switcher";

const navSections = [
  {
    title: "オペレーション",
    items: [
      { href: "/chat", label: "チャット", hint: "スレッド／タスク" },
      { href: "/minutes", label: "Minutes", hint: "音声要約と承認" },
      { href: "/tasks", label: "タスク", hint: "ガント・かんばん" },
      { href: "/knowledge", label: "ナレッジ", hint: "RAG検索" },
      { href: "/automations", label: "自動化", hint: "ルールビルダー" },
      { href: "/analytics", label: "アナリティクス", hint: "参加率" },
    ],
  },
  {
    title: "管理",
    items: [
      { href: "/admin", label: "部署／権限", hint: "ロールとチャンネル" },
      { href: "/settings", label: "設定", hint: "SSO・連携" },
    ],
  },
];

export function WorkspaceSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex w-72 shrink-0 flex-col border-r border-border/80 bg-background/40">
      <div className="px-5 py-6 border-b border-border/70">
        <p className="text-xs uppercase tracking-widest text-muted-foreground">
          Chat Organ AI
        </p>
        <h1 className="mt-1 text-xl font-semibold">Unified Ops Desk</h1>
        <p className="text-sm text-muted-foreground">
          会話・タスク・ナレッジ・自動化を一面で管理。
        </p>
        <button className="mt-4 w-full rounded-xl bg-foreground text-background py-2 text-sm font-semibold hover:opacity-90 transition">
          新規投稿 / ⌘K
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-8">
        {navSections.map((section) => (
          <div key={section.title} className="space-y-2">
            <p className="text-xs uppercase tracking-widest text-muted-foreground">
              {section.title}
            </p>
            <div className="space-y-1">
              {section.items.map((item) => {
                const active = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex flex-col rounded-xl border px-4 py-3 transition",
                      active
                        ? "border-foreground bg-foreground text-background shadow"
                        : "border-border/70 hover:border-foreground/60 hover:bg-foreground/5"
                    )}
                  >
                    <span className="text-sm font-medium">{item.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {item.hint}
                    </span>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="px-4 py-6 border-t border-border/60 space-y-3">
        <div className="rounded-xl border border-border/70 p-3">
          <p className="text-xs text-muted-foreground">オンライン中</p>
          <p className="text-sm font-semibold">23 Members / 4 Guests</p>
          <p className="text-xs text-muted-foreground">
            直近1時間のタスク返信速度: 12分
          </p>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">テーマ</span>
          <ThemeSwitcher />
        </div>
      </div>
    </aside>
  );
}
