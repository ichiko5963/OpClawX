### S058｜Claude Code Channels とは

**スライドに載せる文言**

```
Claude Code Channels とは？

Discord／Telegram を、Claude Code の「リモコン」にできる機能（概念）

スマホ → Discord Bot → PC上の Claude Code → 生成・GitHub 等

※ Research Preview／仕様変更に注意
```

---

### S059｜仕組み図

**スライドに載せる文言**

```
仕組み（概念図）

スマホ（Discord）
  ↓
Discord Bot
  ↓
Claude Code plugin
  ↓
PCで作業
```

---

### S060｜できること（例）

**スライドに載せる文言**

```
できること（例）

・コード生成・修正
・ログ解析
・GitHub操作（Push／PR 等）
・エージェント系タスク
・リサーチ依頼

「PCの前にいなくても次の一手を投げられる」
```

---

### S061｜用意するもの（表）

**スライドに載せる文言**

```
用意するもの

| 必要なもの | メモ |
| --- | --- |
| Claude Code | バージョン要件あり |
| Discord | アカウント・サーバー |
| Bun | plugin 実行に必要（ハマりどころ） |
```

---

### S062｜ステップ1：バージョン確認

**スライドに載せる文言**

```
claude --version

・要件を満たす版以上（古いと「全部動かない」になりやすい）
・ claude update（環境による）
```

---

### S063｜ステップ2：Discord Bot（流れ）

**スライドに載せる文言**

```
Developer Portal で Bot 作成

・New Application → Bot 追加
・Token 取得（外部公開禁止）

※ UIは変わるので最新手順は公式／記事へ
```

---

### S064｜落とし穴：Message Content Intent

**スライドに載せる文言**

```
Privileged Gateway Intents

Message Content Intent を含め、必要な Intent を ON

OFFのままだと本文が取れず「反応しない」になりがち
```

---

### S065｜ステップ3：Bun とは

**スライドに載せる文言**

```
Bun（バン）

・高速 JavaScript ランタイム
・Discord plugin が Bun 上で動く、と説明されることがある

bun --version で確認。無ければインストール
```

---

### S066｜ステップ4：plugin インストール

**スライドに載せる文言**

```
/plugin install discord@claude-plugins-official
/reload-plugins

※ コマンド体系はアップデートで変わる可能性
```

---

### S067｜トークン：環境変数で渡す

**スライドに載せる文言**

```
export DISCORD_BOT_TOKEN="（Botトークン）"

スラッシュコマンドが Unknown になる等の差分対策として記事で紹介
```

---

### S068｜起動：Channels モード

**スライドに載せる文言**

```
claude --channels plugin:discord@claude-plugins-official

ターミナルを閉じると止まる前提（後で常駐）
```

---

### S069｜ペアリングと allowlist（必須）

**スライドに載せる文言**

```
DM → pairing code → /discord:access pair

必須：
/discord:access policy allowlist

やらないと「誰でも操作できる」リスク
```

---

### S070｜サーバーチャンネルで使う

**スライドに載せる文言**

```
チャンネルIDを取得 → 登録

/discord:access channel add チャンネルID

メンションなしで反応、等の調整も可能（記事参照）
```

---

### S071｜トラブルシュート（よくある）

**スライドに載せる文言**

```
よくある原因

・Claude Code 停止
・Intent OFF
・Bun 未インストール
・ペアリング未完
```

---

### S072｜OpenClaw Bot と同居するとき

**スライドに載せる文言**

```
同一チャンネルで複数Botが反応することがある

対策：チャンネルを分ける
#openclaw / #claudecode など

権限設計＝安全
```

---

### S073｜常時起動の選択肢

**スライドに載せる文言**

```
・tmux 等でセッション維持
・自宅の常駐マシン（例：Mac mini）
・VPS（ポリシー・コスト注意）
```

---

### S074｜Telegram でも可能

**スライドに載せる文言**

```
/plugin install telegram@claude-plugins-official

起動も Channels 形式（詳細は公式・記事）
```

---

### S075｜Discord編まとめ（6ステップ）

**スライドに載せる文言**

```
やること（型）

1. バージョン確認
2. Bun
3. Bot＋Intents
4. トークンを環境変数
5. ペアリング
6. allowlist

細部は記事・noteで追う
```

---

### S076｜Channels単体 vs OpenClaw×Channels

**スライドに載せる文言**

```
Channels 単体：便利、でも毎回ゼロから指示になりがち

OpenClaw × Channels：永続メモリ側に文脈があると短い指示で回る

※ 今日は地図。手順は宿題でOK
```
