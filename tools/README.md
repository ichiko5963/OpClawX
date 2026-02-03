# 🛠️ OpenClaw ワークフローツール

ワークフロー改善のためのPythonツール集。

## ツール一覧

### 📱 x_scheduler.py
X投稿のスケジューリング支援ツール。

```bash
python3 tools/x_scheduler.py
```

**機能:**
- 投稿ファイルから投稿を抽出
- 最適な投稿時間を提案（7:00, 12:00, 18:00, 21:00）
- ランダムに投稿を選択してスケジュール生成

---

### 🏥 workspace_health.py
ワークスペースの健全性をチェック。

```bash
python3 tools/workspace_health.py
```

**チェック項目:**
- Inbox: 未処理ファイルの有無
- Memory: 日次ログの存在、古いファイル
- Projects: X投稿ファイルの更新状況
- Git: 未コミットの変更
- Obsidian: Inboxの整理状況

---

### 📊 daily_summary.py
デイリーサマリーを生成。

```bash
python3 tools/daily_summary.py           # 今日
python3 tools/daily_summary.py 2026-02-03  # 指定日
```

**出力内容:**
- 完了タスク一覧
- 残りのタスク一覧
- 更新ファイル数
- X投稿準備状況

---

### 📁 project_status.py
Obsidianプロジェクトのステータス確認。

```bash
python3 tools/project_status.py
```

**出力内容:**
- アクティブプロジェクト一覧
- 各プロジェクトのフェーズ、関係者、議事録数
- 次のアクション、ブロッカー
- アーカイブ済みプロジェクト

---

### 📈 session_analysis.py
過去7日間のセッションを分析。

```bash
python3 tools/session_analysis.py
```

**出力内容:**
- 完了タスク数の推移
- よく使われた技術キーワード
- 生産性の振り返りポイント

---

### ☀️ morning_brief.py
モーニングブリーフィング生成。朝起きたときに確認すべき情報をまとめて表示。

```bash
python3 tools/morning_brief.py
```

**出力内容:**
- 昨日の振り返り（完了・残りタスク）
- X投稿準備状況
- プロジェクト次のアクション
- 今日のログ状況

---

### 🔍 viral_analyzer.py
X投稿のバイラル度を分析し、改善ポイントを提案。

```bash
python3 tools/viral_analyzer.py
```

**チェック項目:**
- フック（【速報】【衝撃】など）
- 具体的な数字
- 効果的な絵文字
- 読みやすい構造
- CTA（行動喚起）
- 対比構造

---

## 使い方

すべてのツールはワークスペースから実行：

```bash
cd /Users/ai-driven-work/Library/Mobile\ Documents/com~apple~CloudDocs/OpenClaw-Shared
python3 tools/<ツール名>.py
```

## 拡張

新しいツールを追加する場合：
1. `tools/` ディレクトリに `.py` ファイルを作成
2. `if __name__ == '__main__':` でエントリポイントを定義
3. このREADMEにドキュメントを追加
