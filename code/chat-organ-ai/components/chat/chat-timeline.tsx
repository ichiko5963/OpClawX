import type { Message } from "@/lib/types/workspace";
import { TaskSuggestionCard } from "./task-suggestion-card";
import { MessageComposer } from "./message-composer";

type Props = {
  messages: Message[];
};

export function ChatTimeline({ messages }: Props) {
  return (
    <section className="flex flex-col gap-4 rounded-3xl border border-border/70 bg-card p-4 lg:p-6">
      <header className="flex flex-wrap items-center gap-3">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">
            会話／スレッド
          </p>
          <h3 className="text-xl font-semibold">#最新情報</h3>
        </div>
        <div className="ml-auto flex items-center gap-3 text-xs text-muted-foreground">
          <span>既読 42 / 48</span>
          <span>ゲスト閲覧 5</span>
          <span className="rounded-full border border-border px-2 py-0.5">
            プライベート
          </span>
        </div>
      </header>

      <div className="space-y-4 divide-y divide-border/60">
        {messages.map((message) => (
          <article key={message.id} className="space-y-3 pt-4 first:pt-0">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <p className="font-semibold text-sm">{message.author}</p>
              <span className="rounded-full bg-foreground/5 px-2 py-0.5 text-muted-foreground">
                {message.role}
              </span>
              <span className="text-muted-foreground">{message.timestamp}</span>
            </div>
            <p className="text-sm leading-relaxed">{message.content}</p>
            {message.attachments && (
              <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                {message.attachments.map((attachment) => (
                  <span
                    key={`${message.id}-${attachment.label}`}
                    className="rounded-full border border-border px-3 py-1"
                  >
                    {attachment.type === "audio" ? "🎙️" : "📎"} {attachment.label}
                  </span>
                ))}
              </div>
            )}
            {message.reactions && (
              <div className="flex gap-2 text-xs text-muted-foreground">
                {message.reactions.map((reaction) => (
                  <span
                    key={`${message.id}-${reaction.emoji}`}
                    className="rounded-full border border-border/80 px-2 py-0.5"
                  >
                    {reaction.emoji} {reaction.count}
                  </span>
                ))}
              </div>
            )}
            {message.suggestions && (
              <div className="space-y-2 rounded-2xl border border-dashed border-border/70 bg-foreground/[0.02] p-3">
                <p className="text-xs font-semibold text-muted-foreground">
                  AIタスク提案
                </p>
                <div className="space-y-3">
                  {message.suggestions.map((suggestion) => (
                    <TaskSuggestionCard key={suggestion.id} suggestion={suggestion} />
                  ))}
                </div>
              </div>
            )}
          </article>
        ))}
      </div>

      <MessageComposer />
    </section>
  );
}
