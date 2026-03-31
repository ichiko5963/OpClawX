import { NextRequest, NextResponse } from 'next/server';
import { mastra } from '@/src/mastra';

export async function POST(request: NextRequest) {
  try {
    const { query, filePath, sheetName } = await request.json();
    
    if (!query || !filePath) {
      return NextResponse.json(
        { error: 'クエリとファイルパスが必要です' },
        { status: 400 }
      );
    }
    
    // ファイルの存在確認
    const fs = require('fs');
    if (!fs.existsSync(filePath)) {
      return NextResponse.json(
        { error: `ファイルが見つかりません: ${filePath}` },
        { status: 400 }
      );
    }
    
    // Advanced ES RAGエージェントを取得
    const agent = mastra.getAgent('advancedEsRagAgent');
    
    if (!agent) {
      return NextResponse.json(
        { error: 'Advanced ES RAGエージェントが見つかりません' },
        { status: 500 }
      );
    }
    
    // エージェントにクエリを送信
    console.log('エージェントにクエリを送信中...');
    const response = await agent.generate(
      `Excelファイル "${filePath}" からESデータを読み込み、ベクター検索を使用してクエリ "${query}" に基づいて類似性の高い3つのESを検索してください。${sheetName ? `シート名: ${sheetName}` : ''}`
    );
    console.log('エージェントの応答:', response.text);
    
    return NextResponse.json({
      success: true,
      result: response.text,
      query,
      filePath,
      sheetName,
    });
    
  } catch (error) {
    console.error('Advanced RAG API Error:', error);
    return NextResponse.json(
      { 
        error: 'Advanced RAG処理中にエラーが発生しました',
        details: error instanceof Error ? error.message : '不明なエラー',
        stack: error instanceof Error ? error.stack : undefined
      },
      { status: 500 }
    );
  }
}
