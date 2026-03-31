import { NextRequest, NextResponse } from 'next/server';
import { mastra } from '@/src/mastra';

export async function POST(request: NextRequest) {
  try {
    const { query, filePath, indexName, action, sheetName } = await request.json();

    if (!action) {
      return NextResponse.json(
        { error: 'アクション (process または search) が必要です' },
        { status: 400 }
      );
    }

    const agent = mastra.getAgent('ragAnalysisAgent');

    if (!agent) {
      return NextResponse.json(
        { error: 'RAG Analysis エージェントが見つかりません' },
        { status: 500 }
      );
    }

    let agentQuery = '';
    if (action === 'process') {
      if (!filePath || !indexName) {
        return NextResponse.json(
          { error: 'ファイルパスとインデックス名が必要です' },
          { status: 400 }
        );
      }
      
      // Excelファイルの場合はexcelProcessorToolを使用
      if (filePath.endsWith('.xlsx') || filePath.endsWith('.xls')) {
        agentQuery = `Excelファイル "${filePath}" を処理し、インデックス名 "${indexName}" でベクトルストアに保存してください。${sheetName ? `シート名は "${sheetName}" を使用してください。` : ''}`;
      } else {
        agentQuery = `ファイル "${filePath}" を処理し、インデックス名 "${indexName}" でベクトルストアに保存してください。`;
      }
    } else if (action === 'search') {
      if (!query || !indexName) {
        return NextResponse.json(
          { error: '検索クエリとインデックス名が必要です' },
          { status: 400 }
        );
      }
      agentQuery = `インデックス名 "${indexName}" からクエリ "${query}" に関連する情報を検索してください。`;
    } else {
      return NextResponse.json(
        { error: '無効なアクションです。process または search を指定してください。' },
        { status: 400 }
      );
    }

    console.log('RAGエージェントにクエリを送信中...');
    const response = await agent.generate(agentQuery);
    console.log('RAGエージェントの応答:', response.text);

    return NextResponse.json({
      success: true,
      result: response.text,
      query,
      filePath,
      indexName,
      action,
      sheetName,
    });

  } catch (error) {
    console.error('RAG API Error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '不明なAPIエラーが発生しました' },
      { status: 500 }
    );
  }
}


