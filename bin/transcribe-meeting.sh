#!/bin/bash
# Meeting Transcription Script
# 会議音声ファイルを文字起こしして議事録を作成

AUDIO_FILE="$1"
PROJECT="$2"
MEETING_NAME="$3"

if [ -z "$AUDIO_FILE" ]; then
    echo "使い方: $0 <音声ファイル> [プロジェクト名] [会議名]"
    echo ""
    echo "例:"
    echo "  $0 meeting.mp3 AirCle 定例MTG"
    exit 1
fi

if [ ! -f "$AUDIO_FILE" ]; then
    echo "エラー: ファイルが見つかりません: $AUDIO_FILE"
    exit 1
fi

# デフォルト値
PROJECT=${PROJECT:-"General"}
MEETING_NAME=${MEETING_NAME:-"会議"}
DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/pi/inbox"
OUTPUT_FILE="$OUTPUT_DIR/meeting_${DATE}_${MEETING_NAME}.md"

echo "🎙️ 会議文字起こしを開始します..."
echo "  ファイル: $AUDIO_FILE"
echo "  プロジェクト: $PROJECT"
echo "  会議名: $MEETING_NAME"
echo ""

# Whisper APIで文字起こし
echo "📝 文字起こし中..."

TRANSCRIPT=$(curl -s https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@$AUDIO_FILE" \
  -F model="whisper-1" \
  -F language="ja" \
  | jq -r '.text')

if [ -z "$TRANSCRIPT" ] || [ "$TRANSCRIPT" == "null" ]; then
    echo "エラー: 文字起こしに失敗しました"
    exit 1
fi

# 議事録フォーマットで保存
cat > "$OUTPUT_FILE" << EOF
# 議事録: $MEETING_NAME

## 基本情報
- **日付**: $DATE
- **会議名**: $MEETING_NAME
- **プロジェクト**: $PROJECT
- **音声ファイル**: $(basename "$AUDIO_FILE")

## 文字起こし

$TRANSCRIPT

---

## アクションアイテム
（Piが自動抽出予定）

---

*作成: $(date +%Y-%m-%d\ %H:%M)*
*このファイルは自動生成されました。Piが整理して適切な場所に移動します。*
EOF

echo "✅ 完了！"
echo "  出力: $OUTPUT_FILE"
echo ""
echo "Piが深夜セッションで議事録を整理します。"
