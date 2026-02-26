---
name: slides-generator
description: CanvaやGoogle Slidesを使ってプレゼンテーションを自動作成するスキル。テンプレートを使ってスライドを作成し、Google Driveに保存する。
---

# Slides Generator

CanvaやGoogle Slidesでプレゼンテーションを自動作成する。

## デフォルトMarpテンプレート

いちさん指定のMarpテンプレートを毎回使用:
```
---
marp: true
# ↓↓↓ これらの行はテンプレートが機能するために必要です ↓↓↓
header: ' '
footer: ' '
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
.bad-example { background-color: #fbe9e7; color: #c62828; padding: 8px 16px; border-radius: 4px; }
</style>
```
↑ 毎回このテンプレートをデフォルトで使用

## 必要な情報

- スlidesのタイトル
- スlidesの内容（テキスト、ポイント）
- 保存先（Google Driveのフォルダ）

## 作業フロー

### 1. MarpでMarkdown→HTML→PDF/画像変換
- 毎回↑のMarpテンプレートを使用
- タイトル、内容、マイルストーンなどをMarkdown形式で作成
- Marp CLIでPDF/画像に変換

### 2. Canva or Google Slidesにインポート
- 変換したPDF/画像をCanva or Google Slidesにアップロード
- 微調整が必要な場合は編集

### 3. 保存・共有
- Google Driveに適切なフォルダに保存
- 共有リンクを取得

### 4. ユーザーに結果を報告
- スlidesのリンクを報告
