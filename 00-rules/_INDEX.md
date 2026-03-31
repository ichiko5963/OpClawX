# 00-rules — ルール層インデックス

このフォルダはAIエージェントの全行動規範を定義する。セッション開始時にMEMORY.mdから参照される。

## ファイル一覧

| ファイル | 内容 |
|----------|------|
| `memory-structure.md` | メモリ全体の構造ルール・命名規則・P0/P1/P2運用 |
| `project-lifecycle.md` | プロジェクト自動生成・更新・アーカイブのルール |
| `deliverable-flow.md` | 完成物→ナレッジ→メモリの蓄積フロー定義 |
| `skill-creation.md` | スキルの作成方法・ナレッジ参照ルール |
| `ceo.md` | CEO（市岡）の意思決定ルール |
| `cmo.md` | CMO：マーケ全般（X投稿・記事・Peatix・画像生成） |
| `cto.md` | CTO：開発・コード・自動化・技術ルール |
| `cso.md` | CSO：営業・クライアント・提携 |
| `cfo.md` | CFO：Gmail連携・領収書・売上・スプシ |
| `chro.md` | CHRO：プロジェクト人員・メンバー管理・特性分析 |

## 読み方

1. タスク実行時、該当する役割の `.md` を読む
2. 成果物が出たら `deliverable-flow.md` に従う
3. 新プロジェクト検出時は `project-lifecycle.md` に従う
4. 新スキル作成時は `skill-creation.md` に従う
