# Projects

> プロジェクト管理の中心

## 構造

```
03_Projects/
├── _Active/           # アクティブなプロジェクト
│   ├── AirCle/
│   ├── ClimbBeyond/
│   ├── SlideBox/
│   ├── ClientWork/
│   └── Genspark/
└── _Old/              # 完了・休止プロジェクト
    └── VideoPocket/
```

## プロジェクト標準構成

各プロジェクトには以下のファイル/フォルダを配置：

| ファイル | 用途 |
|---------|------|
| MEMORY.md | 確定事実の蓄積（正本） |
| STATUS.md | 現在の状態・次のアクション |
| DECISIONS.md | 意思決定ログ |
| MTG/ | ミーティング議事録 |
| INBOX/ | 未整理の素材 |

## ルール

1. **議事録はプロジェクト配下へ** — 人物フォルダに置かない
2. **MEMORY.md は短く** — 確定事実のみ、詳細はMTG/へ
3. **20プロジェクト以内** — 超えたら統合または_Oldへ移管
4. **新規プロジェクトはPROJECT_REGISTRYに登録**

## 関連
- [[00_System/PROJECT_REGISTRY|プロジェクトレジストリ]]
- [[00_System/TEMPLATES/TEMPLATE_PROJECT_MEMORY|MEMORY.mdテンプレート]]
