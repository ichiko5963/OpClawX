import { NextRequest, NextResponse } from 'next/server';
import { esVectorIndexer } from '@/src/mastra/tools/es-vector-indexer';
import { esVectorSearch } from '@/src/mastra/tools/es-vector-search';

// テスト用のESデータ
const testESData = [
  {
    id: "es_1",
    company: "マルハニチロ",
    industry: "メーカー",
    jobType: "総合職",
    question: "学生時代に力を入れた経験はなんですか？ガクチカはなんですか？",
    wordCount: 500,
    content: "獣害である猪の高付加価値食肉生産プロジェクトにおいて、銀座のミシュラン星付きの店に扱われるまでに価値を高められた事です。留学の際、研究成果を世に還元することの重要性を学びました。私も研究を世に役立てたいと想い、猪の被害で苦しんでいる農家の方を猪産業の活性化により解決できると考え、立ち上げました。私は、発起人として、研究成果の信頼性向上のため産学官の連携を図りました。",
    selectionPeriod: "インターンシップ、本選考",
    metadata: {}
  },
  {
    id: "es_2", 
    company: "ミツカン",
    industry: "メーカー",
    jobType: "総合職",
    question: "学生時代に力を入れた経験はなんですか？ガクチカはなんですか？",
    wordCount: 400,
    content: "猪肉の高付加価値食肉生産プロジェクトの立ち上げです。留学の際、研究成果を世に還元することの重要性を学び、私自身の食肉の研究も世に役立てたいと想いました。そこで、未だ体系化されていない猪産業に着目し、挑戦しました。心掛けたことは俯瞰し、最適な行動をとることです。当初は、発足の糸口を探すために関係者の元へ情報収集に奔走しました。",
    selectionPeriod: "インターンシップ、本選考",
    metadata: {}
  },
  {
    id: "es_3",
    company: "三井物産",
    industry: "総合商社",
    jobType: "総合職", 
    question: "学生時代に力を入れた経験はなんですか？ガクチカはなんですか？",
    wordCount: 400,
    content: "大学のプログラミングサークルでWebアプリケーション開発に取り組んだ経験です。チームリーダーとして、5人のメンバーをまとめながら、学生向けの課題管理システムを開発しました。特に困難だったのは、メンバー間の技術レベルの差と、開発スケジュールの管理でした。私は、定期的な勉強会の開催と、タスクの細分化により、全員が貢献できる環境を作り上げました。",
    selectionPeriod: "本選考",
    metadata: {}
  },
  {
    id: "es_4",
    company: "楽天",
    industry: "IT・通信",
    jobType: "エンジニア",
    question: "学生時代に力を入れた経験はなんですか？ガクチカはなんですか？",
    wordCount: 350,
    content: "機械学習を活用した株価予測システムの開発に取り組みました。研究室の個人プロジェクトとして、Pythonとscikit-learnを使用して、過去の株価データから翌日の価格変動を予測するモデルを構築しました。最初は精度が低く、何度も特徴量エンジニアリングやアルゴリズムの調整を行いました。最終的に70%の精度を達成し、学会での発表も行いました。",
    selectionPeriod: "インターンシップ、本選考",
    metadata: {}
  },
  {
    id: "es_5",
    company: "アクセンチュア",
    industry: "コンサルティング",
    jobType: "コンサルタント",
    question: "学生時代に力を入れた経験はなんですか？ガクチカはなんですか？",
    wordCount: 450,
    content: "学生団体での新入生向けキャリア支援イベントの企画・運営です。100名規模のイベントを一から企画し、企業との交渉、会場手配、参加者募集まで一貫して担当しました。特に苦労したのは、企業の協賛獲得で、30社以上にアプローチし、最終的に10社の協賛を得ることができました。イベント当日は参加者から高い評価を得て、翌年度以降も継続開催される基盤を作りました。",
    selectionPeriod: "本選考",
    metadata: {}
  }
];

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json();
    
    if (!query) {
      return NextResponse.json(
        { error: 'クエリが必要です' },
        { status: 400 }
      );
    }
    
    console.log('1. テスト用ESデータを準備中...');
    console.log(`テスト用に${testESData.length}件のドキュメントを使用`);
    
    console.log('2. ベクターインデックスを作成中...');
    // ベクターインデックスを作成
    const indexResult = await esVectorIndexer.execute({
      context: {
        documents: testESData,
        chunkSize: 512,
        chunkOverlap: 50,
        indexName: 'test_es_embeddings'
      }
    });
    
    console.log(`インデックス作成完了: ${indexResult.chunkCount}個のチャンク`);
    
    console.log('3. ベクター検索を実行中...');
    // ベクター検索を実行
    const searchResult = await esVectorSearch.execute({
      context: {
        query,
        topK: 3,
        indexName: 'test_es_embeddings'
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
      totalDocuments: testESData.length,
      chunks: indexResult.chunkCount,
      searchResults: searchResult.totalResults
    });
    
  } catch (error) {
    console.error('Test RAG API Error:', error);
    return NextResponse.json(
      { 
        error: 'Test RAG処理中にエラーが発生しました',
        details: error instanceof Error ? error.message : '不明なエラー',
        stack: error instanceof Error ? error.stack : undefined
      },
      { status: 500 }
    );
  }
}


