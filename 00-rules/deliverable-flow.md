# 完成物→ナレッジ蓄積フロー

## 基本フロー

C-Suite（CMO/CTO/CSO/CFO/CHRO）が作業を完了したとき、以下の3段階で情報が蓄積される：

### Step 1: 保存（プロジェクト/事業に紐づく成果物）

成果物を該当する場所に保存：
- 事業の日常業務 → 事業フォルダ直下の適切な場所
- プロジェクトの成果物 → `projects/[名前]/deliverables/[role]/YYYY-MM-DD-[内容].md`

### Step 2: 蓄積（横断ナレッジへの追記）

その作業から得た**汎用的な学び・パターン**を蓄積：
- `02-business/c-suite/[role]/knowledge/` に追記
- 新しいスキル・手順を発見した場合は `skills/` にも追記

### Step 3: 反映（CEOメモリへの報告）

戦略レベルの決定事項があれば：
- `MEMORY.md` に重要事項を追記
- `c-suite/ceo/decisions.md` に意思決定ログを追記

## 具体例

### CMOがAirCleのX投稿を20件作成
1. 保存 → `02-business/株式会社PLai/自社/X運用/AirCle/投稿/YYYY-MM-DD-x投稿20件.md`
2. 蓄積 → `c-suite/cmo/knowledge/` に「この型がバズった」を追記
3. 反映 → バズ率が大きく変動した場合のみMEMORY.mdに記載

### CTOがOpClawXの新機能を開発
1. 保存 → 該当プロジェクトの `deliverables/cto/` に技術設計書
2. 蓄積 → `c-suite/cto/knowledge/` に実装パターンを追記
3. 反映 → リリース完了をMEMORY.mdに記載

### CFOが月次経費をまとめ
1. 保存 → `c-suite/cfo/knowledge/monthly/YYYY-MM.md`
2. 蓄積 → `c-suite/cfo/knowledge/expense-categories.md` 更新
3. 反映 → 大きな支出変動があればMEMORY.mdに記載

### CHROがMTGから新メンバーを検出
1. 保存 → 該当プロジェクトの `people.md` を更新
2. 蓄積 → `c-suite/chro/knowledge/all-members.md` に追加
3. 反映 → 組織変更があればMEMORY.mdに記載
