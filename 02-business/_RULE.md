# 02-business — 事業層ルール

## 構造

```
02-business/
├── 株式会社PLai/         ← AI全般の会社
│   ├── 自社/             ← 自社事業
│   │   ├── X運用/        ← X（Twitter）の運用事業
│   │   │   ├── AirCle/   ← @aircle_ai
│   │   │   └── いち-OpenClawガチ勢/ ← @ichiaimarketer
│   │   ├── Peatix-無料イベント運営/
│   │   ├── SlideBox/
│   │   ├── VideoPocket/
│   │   └── AI×X運用ブートキャンプ/
│   └── 他社/             ← クライアントワーク
│       ├── Genspark/
│       └── 外部案件・開発/
│
├── 株式会社ValueQ/       ← ポート株式会社からの引き継ぎ
│   ├── 自社/
│   │   └── ClimbBeyond/
│   └── 他社/
│       └── ポート株式会社/
│
├── c-suite/              ← C-Suite横断ナレッジ（プロジェクトを超えた蓄積）
└── mtg-inbox/            ← MTG文字起こしの受け入れ口
```

## 事業フォルダの標準構成

各事業フォルダは以下を持つ：
- `_RULE.md` — その事業固有のルール
- `overview.md` — 事業概要・目標・ステータス
- `mtg/` — 事業レベルのMTG議事録
- `projects/` — 金銭が発生するプロジェクト群

## プロジェクトフォルダの標準構成

`projects/[名前]/` は以下を持つ：
- `overview.md` — プロジェクト概要
- `backlog.md` — タスク一覧
- `people.md` — 関係者（CHRO管轄）
- `mtg/` — プロジェクト固有MTG
- `deliverables/` — 成果物（C-Suite役割ごとにサブフォルダ可）

## 検索のヒント

- 事業の知識を探す → まず該当事業フォルダを検索
- 横断的なノウハウ → `c-suite/[role]/knowledge/` を検索
- 見つからない → `c-suite/ceo/source-knowledge/` をフォールバック検索
