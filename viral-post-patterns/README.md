# Viral Post Patterns 🚀

SNSでバズる投稿の15の型を体系化したオープンソースライブラリ。
X(Twitter)、Instagram、LinkedIn、NoteなどあらゆるSNSで使える、バイラルコンテンツの生成パターンを提供します。

## 🎯 コンセプト

> 「バズる投稿には型がある」

数千のバズ投稿を分析し、「読者の感情を動かす構造・メカニズム」から15の型を抽出。
テーマを変えれば即使える、汎用性の高い生成プロンプトを提供します。

## 📦 インストール

```bash
# リポジトリをクローン
git clone https://github.com/Aircle-Japan/viral-post-patterns.git
cd viral-post-patterns

# OpenClawスキルとして使用する場合
openclaw skills install ./openclaw-integration
```

## 🎨 15のバズ投稿型

| No | 型名 | 特徴 | 向いている内容 |
|---|---|---|---|
| 01 | [速報型](./patterns/01-breaking-news.md) | 「ついに登場」の報道スタイル | 新製品・新機能発表 |
| 02 | [保存版型](./patterns/02-save-for-later.md) | 「後で絶対使う」価値提示 | 役立つ情報・チュートリアル |
| 03 | [海外バズ型](./patterns/03-global-trend.md) | 「世界が注目」の先行紹介 | 海外トレンド・未上陸情報 |
| 04 | [結論型](./patterns/04-conclusion-first.md) | 「結論から言うと」逆説法 | 分析・考察・レビュー |
| 05 | [正直型](./patterns/05-honest-opinion.md) | 「正直、○○」本音共有 | 体験談・失敗談・裏話 |
| 06 | [比較型](./patterns/06-vs-battle.md) | 「○○ vs △△」対決 | 製品比較・選択肢提示 |
| 07 | [体験記型](./patterns/07-first-impression.md) | 「実際に使ってみた」検証 | レビュー・体験レポート |
| 08 | [数字強調型](./patterns/08-by-numbers.md) | 「○○%向上」データ重視 | 成果報告・分析結果 |
| 09 | [批判・論評型](./patterns/09-insight.md) | 「実は○○」新解釈 | 考察・反論・新視点 |
| 10 | [リソース配布型](./patterns/10-freebie.md) | 「欲しい人いますか？」 | テンプレート配布・無料リソース |
| 11 | [裏技・Tips型](./patterns/11-pro-tips.md) | 「知ってると差がつく」 | 裏技・ショートカット |
| 12 | [警告・アラート型](./patterns/12-warning.md) | 「注意が必要」リスク警告 | 変更点・リスク・注意喚起 |
| 13 | [ストーリー型](./patterns/13-storytelling.md) | 「○○だった私が」変化譚 | 成功談・変化レポート |
| 14 | [完全解説型](./patterns/14-complete-guide.md) | 「これだけ読めばOK」総括 | 入門ガイド・総まとめ |
| 15 | [予測・展望型](./patterns/15-future-forecast.md) | 「○○年後には」未来予測 | トレンド予測・将来展望 |

## 🛠 OpenClaw連携

このリポジトリはOpenClawスキルとして直接使用可能です。

```bash
# パターンを使用して投稿を生成
openclaw run viral-post-patterns --pattern 01-breaking-news --theme "AIツール新機能"

# 対話式で生成
openclaw run viral-post-patterns --interactive
```

### スキル設定

`openclaw-integration/config.yaml`でデフォルト設定をカスタマイズできます：

```yaml
defaults:
  platform: x-twitter  # x-twitter, instagram, linkedin, note
  language: ja
  max_length: 280
  tone: professional
```

## 📖 使い方

### 1. パターンファイルを直接参照

各型のMarkdownファイルには以下が含まれています：
- 定義（バズる心理メカニズム）
- 構文の骨格
- 生成プロンプト（コピペで使用可能）
- 代表投稿例

### 2. JSON APIとして使用

```javascript
const patterns = require('./patterns/patterns.json');

// 特定の型を取得
const breakingNews = patterns.find(p => p.id === '01-breaking-news');

// プロンプトを生成
const prompt = breakingNews.prompt_template.replace('{theme}', 'ChatGPT新機能');
```

### 3. CLIツールとして使用

```bash
# 指定した型で投稿を生成
./bin/generate.js --pattern 01-breaking-news --theme "AI革命" --output post.txt

# 全型を一覧表示
./bin/list-patterns.js
```

## 🎓 分析メソドロジー

この15型は以下のプロセスで抽出されました：

1. **データ収集**: いいね100件以上の投稿を数千件収集
2. **構造分析**: 「話題」ではなく「感情を動かすメカニズム」で分類
3. **パターン抽出**: 重複のない明確な定義を持つ15型に集約
4. **検証**: 異なるテーマで再現性を確認

## 🤝 コントリビューション

新しいパターンの提案・改善は大歓迎です！

1. Issueで提案
2. Forkしてブランチ作成 (`git checkout -b feature/amazing-pattern`)
3. Commit (`git commit -m 'Add amazing pattern'`)
4. Push (`git push origin feature/amazing-pattern`)
5. Pull Request作成

[コントリビューションガイドライン](./CONTRIBUTING.md)を参照してください。

## 📄 ライセンス

MIT License - 商用・非商用問わず自由に使用できます。
詳細は[LICENSE](./LICENSE)ファイルを参照してください。

## 🙏 クレジット

分析・作成: [AirCle](https://x.com/AiAircle34052)  
リポジトリ管理: [いち@Aircle代表](https://x.com/ichi0965)

## 🔗 関連リンク

- [OpenClaw公式](https://openclaw.ai)
- [AirCle](https://x.com/AiAircle34052)
- [分析レポート詳細](./docs/analysis-report.md)

---

**⚠️ 免責事項**: これらのパターンは分析結果に基づくものです。すべての投稿がバズることを保証するものではありません。コンテンツの質とタイミングも重要です。
