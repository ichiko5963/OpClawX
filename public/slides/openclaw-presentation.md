---
marp: true
---
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
:root {
  --color-background: #f8f8f4;
  --color-foreground: #3a3b5a;
  --color-heading: #4f86c6;
  --color-hr: #000000;
  --font-default: 'Noto Sans JP', sans-serif;
}
section {
  background-color: var(--color-background);
  color: var(--color-foreground);
  font-family: var(--font-default);
  font-weight: 400;
  box-sizing: border-box;
  border-bottom: 8px solid var(--color-hr);
  position: relative;
  line-height: 1.7;
  font-size: 22px;
  padding: 56px;
}
section:last-of-type { border-bottom: none; }
h1, h2, h3, h4, h5, h6 { font-weight: 700; color: var(--color-heading); margin: 0; padding: 0; }
h1 { font-size: 56px; line-height: 1.4; text-align: left; }
h2 { position: absolute; top: 40px; left: 56px; right: 56px; font-size: 40px; padding-top: 0; padding-bottom: 16px; }
h2::after { content: ''; position: absolute; left: 0; bottom: 8px; width: 60px; height: 2px; background-color: var(--color-hr); }
h2 + * { margin-top: 112px; }
h3 { color: var(--color-foreground); font-size: 28px; margin-top: 32px; margin-bottom: 12px; }
ul, ol { padding-left: 32px; }
li { margin-bottom: 10px; }
footer { font-size: 0; color: transparent; position: absolute; left: 56px; right: 56px; bottom: 40px; height: 8px; background-color: var(--color-heading); }
header { font-size: 0; color: transparent; background-image: url('ロゴ.png'); background-repeat: no-repeat; background-size: contain; background-position: top right; position: absolute; top: 40px; left: calc(100% - 180px - 56px); width: 180px; height: 50px; }
section.lead { border-bottom: 8px solid var(--color-hr); }
section.lead footer, section.lead header { display: none; }
section.lead h1 { margin-bottom: 24px; }
section.lead p { font-size: 24px; color: var(--color-foreground); }
</style>

# OpenClawを使いこなせない99%の原因

## たった1つの共通点

---

## はじめに

- いち（市岡直人）
- AirCle代表
- 大学生で事業をM&Aした経験あり

---

## 多くの人の误区

「OpenClaw入れたerset動いた」
↓
「でも Manson랑差不多？」

---

## 現実

OpenClawを使ってる人の**99%**が
まだ本領を発揮できていない

---

## 原因

### たった1つの共通点

**情報的一元管理ができてない**

---

## つまりこういうこと

M anusは「優秀な派遣社員」

OpenClawは「もう一人のは自分」

この差が出るのは
**情報的一元管理**やったときだけ

---

## マ二ス・Notion AIとの差

| | Manus | OpenClaw |
|---|---|---|
| 文脈把握 | 弱い | 強い（設定をしたら）|
| 自発的行動 | なし | あり |
| タスク実行 | ○ | ○ |

---

## 本来のOpenClaw

「3時間後のMTG、協業案3つ作っといたよ」

「昨天的X投稿パターン伸びそう 作っといた」

「それ非効率やわ〜自動化しといた」

---

## なぜ差が付くのか

全部GitHubで管理してるから

```
~/OpenClaw-Workspace/
├── MEMORY.md
├── memory/
├── obsidian/
├── scripts/
└── tools/
```

---

## GitHub Actionsで全自動化

- Gmail同步（毎時）
- Googleカレンダー同步（毎時）
- Google Tasks同步（1日4回）
- X投稿生成・Discord通知（毎朝7時）
- 経費自動記録

---

## Gmail同步

```yaml
name: Gmail Sync
on:
  schedule:
    - cron: '0 * * * *'
```

メールを取得→優先度分類（P0/P1/P2/P3）→markdown保存

---

## カレンダー同步

```yaml
name: Calendar Sync
on:
  schedule:
    - cron: '0 * * * *'
```

2時間以内にMTG→
参加者をObsidianから検索→
準備リスト自動生成

---

## X投稿自動化

```yaml
name: X Morning Posts
on:
  schedule:
    - cron: '0 22 * * *'
```

过去820件のデータから
パターン分析→
最新ニュース踏まえて投稿生成

---

## 経費自動記録

```yaml
name: Expense Tracker
on:
  schedule:
    - cron: '0 * * *'
```

Gmailから領収書を検知→
Google Sheetsに自動記録

---

## 一元管理の効果

OpenClawが知ることができる：
- プロジェクトの進捗
- 関係者の情報
- 過去の判断・失敗
- 定期的なイベント

---

## 「もう一人のは自分」になる瞬间

```
「明日の打ち合わせ準備しといて」
↓
「〇株式会社との定例ですね。
 前回の議事録見たけど、
 進捗報告とマイルストーンが議題です。
 協業案3つ作っといました」
```

---

## 設定はめどう感じる？

正直、最初は何日もかかる

でも**1回やれば毎日の作業が自動化**

---

## まとめ

- 信息散らばってたら Manusと同じ
- 一元管理やると OpenClawが化ける
- GitHubに全部集める が正解

---

## AirCle的活动

- OpenClaw Guild（LINEオープンチャット）
- 2/27 20:00〜 セミナー開催

---

## 最後に

「的全部自动化したい」
「每次零から説明するのはもうイヤ」
↓
GitHubから始めてみて

---

ご清聴ありがとう！

