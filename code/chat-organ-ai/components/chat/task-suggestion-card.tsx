import type { TaskSuggestion } from "@/lib/types/workspace";

type Props = {
  suggestion: TaskSuggestion;
};

export function TaskSuggestionCard({ suggestion }: Props) {
  return (
    <div className="rounded-2xl border border-dashed border-foreground/40 p-4 space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold">{suggestion.title}</p>
        <span className="text-xs text-muted-foreground">
          信頼度 {(suggestion.confidence * 100).toFixed(0)}%
        </span>
      </div>
      <div className="text-xs text-muted-foreground space-y-1">
        <p>期日候補: {suggestion.dueCandidates.join(" / ")}</p>
        <p>担当候補: {suggestion.assigneeCandidates.join(", ")}</p>
      </div>
      <div className="flex flex-wrap gap-2 text-xs">
        <button className="rounded-full bg-foreground px-3 py-1 font-semibold text-background hover:opacity-90">
          承認してタスク化
        </button>
        <button className="rounded-full border border-border px-3 py-1 text-muted-foreground hover:text-foreground">
          拒否
        </button>
      </div>
    </div>
  );
}
