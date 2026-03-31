import { NextRequest, NextResponse } from 'next/server';
import { mastra } from '@/src/mastra';

export async function POST(request: NextRequest) {
  try {
    const { query, filePath, indexName, action } = await request.json();
    
    if (!query) {
      return NextResponse.json(
        { error: 'クエリが必要です' },
        { status: 400 }
      );
    }
    
    // RAG Analysisエージェントを取得
    const agent = mastra.getAgent('ragAnalysisAgent');
    
    if (!agent) {
      return NextResponse.json(
        { error: 'RAG Analysisエージェントが見つかりません' },
        { status: 500 }
      );
    }
    
    let prompt = '';
    
    if (action === 'process') {
      // ファイル処理
      if (!filePath || !indexName) {
        return NextResponse.json(
          { error: 'ファイル処理にはfilePathとindexNameが必要です' },
          { status: 400 }
        );
      }
      prompt = `ファイル "${filePath}" を処理してベクトル化してください。インデックス名: ${indexName}`;
    } else if (action === 'search') {
      // ベクトル検索
      if (!indexName) {
        return NextResponse.json(
          { error: '検索にはindexNameが必要です' },
          { status: 400 }
        );
      }
      prompt = `インデックス "${indexName}" からクエリ "${query}" に関連する情報を検索してください。`;
    } else {
      // デフォルトは検索
      prompt = `クエリ "${query}" に関連する情報を検索してください。`;
    }
    
    // エージェントにクエリを送信
    console.log('RAGエージェントにクエリを送信中...');
    const response = await agent.generate(prompt);
    console.log('RAGエージェントの応答:', response.text);
    
    return NextResponse.json({
      success: true,
      result: response.text,
      query,
      filePath,
      indexName,
      action,
    });
    
  } catch (error) {
    console.error('RAG API Error:', error);
    return NextResponse.json(
      { 
        error: 'RAG処理中にエラーが発生しました',
        details: error instanceof Error ? error.message : '不明なエラー',
        stack: error instanceof Error ? error.stack : undefined
      },
      { status: 500 }
    );
  }
}