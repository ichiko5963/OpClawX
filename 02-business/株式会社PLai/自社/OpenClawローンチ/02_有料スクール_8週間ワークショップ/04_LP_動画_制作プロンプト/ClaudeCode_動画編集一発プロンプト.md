# Claude Code 用：ローンチ動画のポストプロダクション（一発プロンプト）

以下を **Claude Code にそのまま貼り付け**て使う。  
前提：`INPUT_VIDEO`（録画した mp4）と、任意で `ASSETS_DIR`（ロゴ・BGM）がある。

---

## コピペ用プロンプト（本文）

```
あなたは動画ポストプロダクション用のエンジニアです。次を満たすスクリプト一式を、このリポジトリ内に生成してください。OSは macOS を想定。依存は ffmpeg（必須）と、任意で Python 3。

## ゴール
1. 入力 MP4 から「無音区間」を自動カットし、尺を短縮した MP4 を出力する。
2. 冒頭 2 秒に「ロゴ画像」をフェードインで重ねる（ロゴが無ければスキップ可）。
3. 必要なら末尾 1 秒に簡易エンドカード（テキスト or 画像）を付与。
4. 設定は YAML か JSON で一元管理（閾値・ロゴパス・マージン秒・解像度）。

## 無音カット仕様
- ffmpeg の silencedetect で無音区間を検出。
- 無音とみなす閾値: noise=-40dB（設定で変更可）
- 最小無音継続: 0.5 秒以上をカット候補。ただし「連続発話の間の自然な間」は残すため、カット後に最短 0.12 秒の無音を必ず挿入する（機械的な詰まり感を防ぐ）。
- 冒頭 0.3 秒・末尾 0.5 秒はトリムしない（ノイズ対策）。

## ロゴ
- デフォルトパス: ./assets/logo.png（存在しなければロゴ処理をスキップして警告のみ）。
- ロゴが無い場合: README に「公式 OpenClaw ロゴは利用規約に従い各自で取得し assets に配置」と書く。
- ロゴは右上、幅は動画幅の 12%、余白 24px、フェード 0.4s。

## 出力
- ./out/final_YYYYMMDD_HHMM.mp4
- ./out/cuts.json にカット区間のログ（デバッグ用）

## ファイル構成（必ず作成）
- scripts/detect_silence.sh … silencedetect 実行し区間をパース
- scripts/build_timeline.py … カットリストから ffmpeg filter_complex 用の trim + concat を生成
- scripts/render.sh … 入力1ファイルから最終 mp4 まで一発実行
- config/edit.yaml … 上記パラメータすべて
- README.md … Homebrew で ffmpeg 入れる手順、使い方3行

## 実行例
./scripts/render.sh ./raw/launch_take1.mp4

## 制約
- 有料素材の自動ダウンロードはしない。ロゴはローカルファイルのみ。
- 長尺でもメモリ破綻しないよう、ffmpeg は segment + concat 方式で実装。

まず README と config、次にスクリプトを書き、最後に dry-run（ffmpeg -t 10 で先頭10秒だけテスト）用のオプションも render.sh に追加してください。
```

---

## 使い方（人間側）

1. 新規フォルダ（例 `video-post`）を作り、Claude Code でそのフォルダを開く。
2. 上記プロンプトを貼り、生成された `README.md` に従って `ffmpeg` を入れる。
3. `assets/logo.png` に **AirCle ロゴ**または**自作エンドカード**を置く（OpenClaw 公式ロゴは各公式の利用条件を確認）。
4. `config/edit.yaml` で無音感度を調整（声が小さい収録は `noise=-35dB` などに）。
5. `./scripts/render.sh ./raw/自分の録画.mp4` を実行。

---

## 追加でやりたい場合（第2プロンプト例）

「テロップ用の SRT を、同じリポジトリの `台本.md` からタイムコードなしで章見出しだけ抽出して `chapters.srt` を生成する Python を追加して」など、**1タスク1プロンプト**で足すと壊れにくい。

---

## 注意

- **ロゴをネットから自動取得**させるプロンプトは、ライセンス事故の原因になるので入れていない。必ず**自分で権利の通った画像**を `assets/` に置くこと。
- 無音カットだけで満足できない場合は、**Descript / Premiere** 等との併用を推奨。ffmpeg は「フィラー削り」の下処理に強い。
