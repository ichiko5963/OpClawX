# SlideBox Landing Page Implementation Plan

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

Reference: `09-開発/0_参考資料/PLANS.md.md`

## Purpose / Big Picture

AIスライド再構成ツール「SlideBox」のランディングページ（LP）を作成します。
このLPは、シンプルかつスタイリッシュ、洗練されたプロフェッショナルな世界観（Notion/Appleのようなミニマルデザイン）で構築され、ユーザーが「スライドをアップロードして編集可能なブロックに再構成する」というコア体験を直感的に理解できるようにします。

ユーザーに見える挙動：
- ブラウザでHTMLファイルを開くと、SlideBoxの機能、メリット、デモ、ユースケース、将来のビジョン、価格、CTAを含むフルLPが表示される。
- 白・黒・グレーを基調とし、青・紫をアクセントにしたモダンなSaaSデザインが適用されている。
- 複雑なビルド手順なしで、HTMLファイル単体で即座にプレビュー可能。

## Progress

- [ ] **Milestone 1: セットアップと基盤構築**
  - プロジェクトディレクトリ `09-開発/2_実装/SlideBox/` を作成。
  - Tailwind CDNと基本スタイル（Interフォント、カスタムカラー）を含む `index.html` の骨子を作成。
- [ ] **Milestone 2: ヒーローセクションとコア価値の訴求**
  - ヘッダー/ナビゲーションの実装。
  - ヒーローセクションの実装（コピー、CTA、UIモックアップのプレースホルダー）。
  - 「なぜSlideBoxなのか」（課題と解決策）の実装。
- [ ] **Milestone 3: 機能と仕組み**
  - 「SlideBoxの仕組み（How it works）」の4ステップ実装。
  - 「核となる3つの機能」グリッドの実装。
  - 「Before/After」比較セクションの実装。
- [ ] **Milestone 4: 社会的証明とビジョン**
  - ターゲット層/ユースケースの実装。
  - 未来のビジョン（ロードマップ）の実装。
  - 営業資料自動最適化機能の紹介。
  - 料金プランと最終CTAの実装。
  - フッターの実装。
- [ ] **Milestone 5: アセットと納品**
  - 画像生成用プロンプトをまとめた `prompts.md` を作成。
  - モバイルレスポンシブ対応と余白の最終調整。

## Surprises & Discoveries

*(実装中に発見した事項があればここに追記)*

## Decision Log

- Decision: 特定のフレームワーク（Next.js等）ではなく、HTML + Tailwind CDN を採用する。
  Rationale: ユーザーが「フル生成」かつ「プレビューできる状態」を求めているため。単一のHTMLファイルであれば、ブラウザで開くだけで即座に確認でき、ビルド不要で修正も容易。将来的にReactコンポーネントへの移植も簡単に行える。
  Date/Author: 2025-11-22 / AI Assistant

## Outcomes & Retrospective

*(完了時に記入)*

## Context and Orientation

- **Target Directory**: `09-開発/2_実装/SlideBox/`
- **Main File**: `index.html`
- **Design Reference**: ミニマルSaaS（白背景、黒テキスト、アクセント：青 #2D6DF6 / 紫 #6A5BF6）。Notion/Linear/Appleの中間のような質感。
- **Content Source**: ユーザープロンプトで提供された構成案（1〜10）に従う。

## Plan of Work

1.  **Setup**: ディレクトリ作成と `index.html` の用意。Tailwind CDNスクリプトを配置し、カスタムカラー（`#2D6DF6`, `#6A5BF6`）を設定に追加。
2.  **Structure**: 要件定義（1〜10のセクション）に従ってHTML構造をコーディングする。
3.  **Styling**: Tailwindのユーティリティクラスを使用し、余白（`py-24`等）を十分に取り、タイポグラフィを調整。
4.  **Components**:
    -   **ボタン**: 黒背景・白文字、角丸（rounded-full または rounded-md）。
    -   **カード**: 白背景、微細なボーダー、薄いシャドウ。
    -   **ビジュアル**: CSSで「ブロック」や「UI構造」を模したプレースホルダーを作成し、画像が必要な箇所を明確にする。
5.  **Output**: `prompts.md` に各セクションで必要な画像の生成プロンプトを出力する。

## Concrete Steps

1.  `mkdir -p "09-開発/2_実装/SlideBox"` を実行。
2.  `09-開発/2_実装/SlideBox/index.html` を作成し、LPの全コードを記述。
3.  `09-開発/2_実装/SlideBox/prompts.md` を作成し、画像プロンプトを記述。
4.  ブラウザで `index.html` を開き、表示崩れがないか確認する。

## Validation and Acceptance

-   **Visual Check**: `09-開発/2_実装/SlideBox/index.html` をブラウザで開いて確認。
-   **Criteria**:
    -   「ミニマルSaaS」デザイン（クリーン、余白、指定色）が再現されているか。
    -   要件にある全10セクションが含まれているか。
    -   テキストが提供された内容と一致しているか。
    -   レスポンシブ対応（スマホ・PC）ができているか。
    -   画像生成用のプロンプトが `prompts.md` にあるか。

## Idempotence and Recovery

-   HTMLファイルは何度でも上書き可能。
-   外部依存やDB変更はないため、リスクなし。

## Interfaces and Dependencies

-   **Tailwind CSS**: CDN経由で読み込み (`<script src="https://cdn.tailwindcss.com"></script>`)。
-   **Google Fonts**: Inter (`<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">`)。
