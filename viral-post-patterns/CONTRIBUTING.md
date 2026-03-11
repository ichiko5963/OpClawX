# Contributing to Viral Post Patterns

AirCleへの貢献に興味を持っていただき、ありがとうございます！

## 貢献の方法

### 1. 新しいパターンの提案

新しいバズ投稿パターンを発見した場合：

1. Issueを作成し、パターンの概要を説明
2. 以下を含めてください：
   - パターン名
   - 定義（バズる心理メカニズム）
   - 構文の骨格
   - 代表投稿例（最低3つ）
   - 効果データ（可能であれば）

### 2. 既存パターンの改善

- より良いプロンプトの提案
- 新しい例の追加
- 分析データの更新

### 3. コード貢献

バグ修正や機能追加：

1. リポジトリをFork
2. ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにPush (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## パターン追加のガイドライン

新しいパターンを追加する場合：

### 必須項目

```yaml
id: 16-new-pattern  # 連番で付与
name: 新パターン名
name_en: English Name
trigger_keywords: ["キーワード1", "キーワード2"]
psychology: バズる心理メカニズムの説明
engagement_type: 期待されるエンゲージメント
max_length: 280  # 推奨最大文字数
structure:
  hook: 書き出しの構造
  body: 本文の構造  
  cta: 締めの構造
```

### ファイル作成

1. `patterns/16-new-pattern.md` - 詳細ドキュメント
2. `prompts/16-new-pattern.txt` - 生成プロンプト
3. `patterns/patterns.json` - JSONデータへの追加
4. `examples/16-new-pattern.md` - 実例集

## コーディング規約

- JavaScript: StandardJSスタイル
- Markdown: Markdownlint準拠
- JSON: JSON Schema準拠

## レビュープロセス

1. Pull Requestが作成される
2. メンテナーがレビュー
3. 必要に応じて修正依頼
4. 承認後にマージ

## コミュニティ

- Issueでのディスカッション歓迎
- 新しいアイデアの提案歓迎
- 質問はDiscussionsへ

## ライセンス

貢献した内容はMITライセンスの下で公開されます。
