import { AdminPanels } from "@/components/admin/admin-panels";
import { getWorkspaceSnapshot } from "@/lib/mock-data";

export default function AdminPage() {
  const snapshot = getWorkspaceSnapshot();
  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs uppercase tracking-widest text-muted-foreground">
          管理者ビュー
        </p>
        <h3 className="text-2xl font-semibold">部署・ロール・統合管理</h3>
        <p className="text-sm text-muted-foreground">
          ワークスペース初期設定（事業 or スクール）、部署メンション、プライベートチャンネル自動生成、GitHub等の連携をここで管理します。
        </p>
      </div>

      <AdminPanels
        departments={snapshot.departments}
        integrations={snapshot.integrations}
      />
    </div>
  );
}
