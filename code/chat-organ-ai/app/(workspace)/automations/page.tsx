import { AutomationBuilder } from "@/components/automations/automation-builder";
import { getWorkspaceSnapshot } from "@/lib/mock-data";

export default function AutomationsPage() {
  const snapshot = getWorkspaceSnapshot();
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">
            Automation Agent
          </p>
          <h3 className="text-2xl font-semibold">仕組み化ルールの編成</h3>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          <button className="rounded-full border border-border px-4 py-1.5 font-semibold hover:border-foreground">
            Temporalを開く
          </button>
          <button className="rounded-full border border-border px-4 py-1.5 font-semibold hover:border-foreground">
            週次テンプレを適用
          </button>
        </div>
      </div>

      <AutomationBuilder rules={snapshot.automationRules} />
    </div>
  );
}
