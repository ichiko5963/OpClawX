import { NextRequest, NextResponse } from 'next/server';
import { esDocumentProcessor } from '@/src/mastra/tools/es-document-processor';
import { esVectorIndexer } from '@/src/mastra/tools/es-vector-indexer';
import { esVectorSearch } from '@/src/mastra/tools/es-vector-search';

export async function POST(request: NextRequest) {
  try {
    const { query, filePath, sheetName } = await request.json();
    
    if (!query || !filePath) {
      return NextResponse.json(
        { error: 'クエリとファイルパスが必要です' },
        { status: 400 }
      );
    }
    
    console.log('1. ESドキュメントを読み込み中...');
    // 1. ESドキュメントを読み込み
    const docResult = await esDocumentProcessor.execute({
      context: {
        filePath,
        sheetName
      }
    });
    
    console.log(`読み込まれたドキュメント数: ${docResult.totalCount}`);
    
    // 処理速度のため最初の50件のみを使用
    const testDocs = docResult.documents.slice(0, 50);
    console.log(`処理用に${testDocs.length}件のドキュメントを使用`);
    
    console.log('2. ベクターインデックスを作成中...');
    // 2. ベクターインデックスを作成
    const indexResult = await esVectorIndexer.execute({
      context: {
        documents: testDocs,
        chunkSize: 512,
        chunkOverlap: 50,
        indexName: 'direct_es_embeddings'
      }
    });
    
    console.log(`インデックス作成完了: ${indexResult.chunkCount}個のチャンク`);
    
    console.log('3. ベクター検索を実行中...');
    // 3. ベクター検索を実行
    const searchResult = await esVectorSearch.execute({
      context: {
        query,
        topK: 3,
        indexName: 'direct_es_embeddings'
      }
    });
    
    // 結果をフォーマット
    const formattedResults = searchResult.results.map((result, index) => {
      return `【ES ${index + 1}】類似度: ${result.score.toFixed(4)}
企業名: ${result.metadata.company}
業界: ${result.metadata.industry}
職種: ${result.metadata.jobType}
設問内容: ${result.metadata.question}
文字数: ${result.metadata.wordCount}
ES内容: ${result.text}
選考時期: ${result.metadata.selectionPeriod}`;
    }).join('\n\n');
    
    return NextResponse.json({
      success: true,
      result: formattedResults,
      query,
      filePath,
      sheetName,
      totalDocuments: docResult.totalCount,
      processedDocuments: testDocs.length,
      chunks: indexResult.chunkCount,
      searchResults: searchResult.totalResults
    });
    
  } catch (error) {
    console.error('Direct RAG API Error:', error);
    return NextResponse.json(
      { 
        error: 'Direct RAG処理中にエラーが発生しました',
        details: error instanceof Error ? error.message : '不明なエラー',
        stack: error instanceof Error ? error.stack : undefined
      },
      { status: 500 }
    );
  }
}


