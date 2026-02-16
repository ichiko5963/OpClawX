# メモリ参照フロー完全図解

## 📍 現在の構成

```
/Users/ai-driven-work/Documents/OpenClaw-Workspace/
├── MEMORY.md                              ← OpenClawメインメモリ
├── memory/                                ← 日次メモリ
│   ├── 2026-02-16.md
│   ├── 2026-02-17.md
│   └── heartbeat-state.json
├── obsidian/
│   └── Ichioka Obsidian/                  ← ローカルObsidian Vault
│       ├── 00_System/
│       ├── 03_Projects/
│       ├── 10-私の周りの人/
│       └── 11-連携企業/
└── .git/                                  ← Gitリポジトリ
    └── [リモート: git@github.com:ichiko5963/ichioka-vault.git]
```

---

## 🔄 メモリ参照フロー（全体像）

### 1️⃣ **セッション起動時（自動読み込み）**

```
┌─────────────────────────────────────────────────┐
│ OpenClaw起動 (Telegram/Discordメッセージ受信)  │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ AGENTS.mdの指示に従って自動読み込み開始         │
│ "Every Session" セクションを実行                │
└─────────────────────────────────────────────────┘
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
┌──────────────┐        ┌──────────────┐
│ SOUL.md      │        │ USER.md      │
│ (ローカル)   │        │ (ローカル)   │
└──────────────┘        └──────────────┘
        ↓                       ↓
┌─────────────────────────────────────────────────┐
│ memory/YYYY-MM-DD.md (今日+昨日)                │
│ - memory/2026-02-17.md (ローカル)               │
│ - memory/2026-02-16.md (ローカル)               │
└─────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────┐
│ **メインセッション判定**                        │
│ - メイン(Telegram直接チャット) → MEMORY.md読む  │
│ - サブ/グループ → MEMORY.md読まない            │
└─────────────────────────────────────────────────┘
        ↓ (メインセッションの場合)
┌─────────────────────────────────────────────────┐
│ MEMORY.md (ローカル)                            │
│ - 長期記憶、重要な決定、進行中タスク            │
└─────────────────────────────────────────────────┘
```

**重要:** この時点ではすべて**ローカルファイル**から読み込み。
GitHubは関与しない。

---

### 2️⃣ **チャット中の検索（memory_searchツール）**

```
┌─────────────────────────────────────────────────┐
│ ユーザー: 「XXXについて覚えてる？」            │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ memory_search ツール実行                        │
│ query: "XXX"                                    │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ **検索対象（すべてローカル）**                  │
│                                                 │
│ 1. MEMORY.md                                    │
│ 2. memory/*.md                                  │
│ 3. obsidian/Ichioka Obsidian/** (設定済み)      │
│    - 00_System/                                 │
│    - 03_Projects/                               │
│    - 10-私の周りの人/                           │
│    - 11-連携企業/                               │
│                                                 │
│ ※OpenClaw設定で extraPaths に指定済み          │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ セマンティック検索実行 (ベクトル検索)           │
│ - ローカルの全ファイルをインデックス化          │
│ - クエリと類似度スコアでランキング              │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 検索結果を返す                                  │
│ - path + line number + snippet                  │
│ - 例: "MEMORY.md#45: プロジェクトXの決定事項"   │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ memory_get で該当行を取得                       │
│ memory_get(path="MEMORY.md", from=45, lines=10) │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ ローカルファイルから該当箇所を読み込み          │
│ → チャット応答に使用                            │
└─────────────────────────────────────────────────┘
```

**重要:** memory_searchも**100%ローカル**。GitHubは見ない。

---

### 3️⃣ **GitHubとの関係（現状の問題点）**

```
┌─────────────────────────────────────────────────┐
│ ローカルワークスペース                          │
│ /Users/ai-driven-work/Documents/                │
│   OpenClaw-Workspace/                           │
│                                                 │
│ ├── MEMORY.md          ← AI参照元（ローカル）   │
│ ├── memory/            ← AI参照元（ローカル）   │
│ └── obsidian/          ← AI参照元（ローカル）   │
└─────────────────────────────────────────────────┘
              ↓ (git push)
┌─────────────────────────────────────────────────┐
│ GitHub: ichiko5963/ichioka-vault                │
│                                                 │
│ ├── MEMORY.md          ← ❌ 空または古い        │
│ ├── memory/            ← ❌ 同期されてない      │
│ └── obsidian/          ← ❌ 同期されてない      │
└─────────────────────────────────────────────────┘
```

**問題:**
- OpenClawは**ローカルのみ参照**
- GitHubリポジトリには`git push`しないと反映されない
- 自動同期cronはあるが、最近pushされてない可能性

---

## 🔧 設定詳細（OpenClaw config）

```json
{
  "agents": {
    "defaults": {
      "workspace": "/Users/ai-driven-work/Documents/OpenClaw-Workspace",
      "memorySearch": {
        "sources": [
          "memory",      // memory/*.md
          "sessions"     // セッション履歴
        ],
        "extraPaths": [
          "/Users/ai-driven-work/Documents/OpenClaw-Workspace/obsidian/Ichioka Obsidian"
        ],
        "experimental": {
          "sessionMemory": true
        }
      }
    }
  }
}
```

**意味:**
1. `workspace` = ベースディレクトリ
2. `sources: ["memory"]` = `workspace/MEMORY.md` + `workspace/memory/*.md` を検索
3. `extraPaths` = Obsidian Vaultも追加で検索
4. すべて**ローカルファイルシステム**から検索

---

## ✅ Obsidianの参照元

```
質問: ObsidianはローカルからかGitHubからか？

答え: 100%ローカル

/Users/ai-driven-work/Documents/OpenClaw-Workspace/obsidian/Ichioka Obsidian/

↑ この実際のディレクトリをリアルタイムで読む。
GitHubにpushされたものは見ない。
```

---

## 🐛 問題の原因

### GitHubが空/古い理由

**可能性1: 手動pushしてない**
```bash
cd /Users/ai-driven-work/Documents/OpenClaw-Workspace
git status  # ← 変更が溜まってる
# mission-control/ が未コミット
```

**可能性2: 自動同期cronが止まってる**
- `git-auto-sync` cronジョブが実行されてない
- または実行されたがコンフリクトでスキップ

**可能性3: .gitignore で除外されてる**
- MEMORY.mdやobsidian/が除外設定されてる可能性

---

## 🔨 解決策

### 1. 現状確認
```bash
cd /Users/ai-driven-work/Documents/OpenClaw-Workspace
git status               # 未コミット確認
git log --oneline -5     # 最近のコミット確認
cat .gitignore           # 除外設定確認
```

### 2. 手動同期
```bash
cd /Users/ai-driven-work/Documents/OpenClaw-Workspace
git add MEMORY.md memory/ obsidian/
git commit -m "📝 メモリ同期 $(date +%Y-%m-%d)"
git push origin main
```

### 3. 自動同期の確認
```bash
cron action:list  # git-auto-sync の状態確認
```

---

## 📊 まとめ表

| 項目 | 参照元 | GitHub関与 |
|------|--------|-----------|
| **MEMORY.md** | ローカル | ❌ 読み込み時は無関係 |
| **memory/*.md** | ローカル | ❌ 読み込み時は無関係 |
| **obsidian/** | ローカル | ❌ 読み込み時は無関係 |
| **memory_search** | ローカル全体 | ❌ GitHubは見ない |
| **GitHub repo** | - | 📦 バックアップ/共有用のみ |

**結論:**
- AI（OpenClaw）は**100%ローカルファイル**のみ参照
- GitHubはバックアップ/共有用
- GitHubが空でもAI動作に影響なし
- ただし他デバイスで見たい場合は `git push` 必要

---

## 🚀 推奨アクション

1. **今すぐ手動push**
   ```bash
   cd ~/Documents/OpenClaw-Workspace
   git add .
   git commit -m "📝 完全同期"
   git push
   ```

2. **自動同期cronの復活確認**
   - `git-auto-sync` が毎時動いてるか確認
   - エラーログ確認

3. **GitHub確認**
   - https://github.com/ichiko5963/ichioka-vault
   - MEMORY.mdの中身が最新か確認
