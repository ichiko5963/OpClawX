'use client';

import { useState, useEffect } from 'react';
import { TEMPLATES, selectTemplate, generateDraft } from '@/lib/templates';
import { DraftPost, TemplateType } from '@/types';
import DraftCard from '@/components/DraftCard';
import { 
  Sparkles, 
  Bookmark, 
  Search, 
  ArrowLeft,
  RefreshCw,
  Check,
  Zap,
  TrendingUp,
  AlertCircle
} from 'lucide-react';

interface GenerateResult {
  success: boolean;
  count: number;
  total: number;
  drafts: DraftPost[];
  error?: string;
}

export default function Generator() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDrafts, setGeneratedDrafts] = useState<DraftPost[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateType | 'auto'>('auto');
  const [source, setSource] = useState<'bookmarks' | 'keywords'>('bookmarks');
  const [limit, setLimit] = useState(10);
  const [error, setError] = useState<string | null>(null);
  const [savedCount, setSavedCount] = useState(0);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    setGeneratedDrafts([]);
    
    try {
      const response = await fetch('/api/generate-drafts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: source,
          limit: limit,
          minLikes: source === 'keywords' ? 100 : undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || '生成に失敗しました');
      }

      const data: GenerateResult = await response.json();
      
      if (data.success) {
        setGeneratedDrafts(data.drafts);
        setSavedCount(data.total);
        
        // Also save to localStorage for backup
        const existing = localStorage.getItem('aircle_drafts');
        const existingDrafts: DraftPost[] = existing ? JSON.parse(existing) : [];
        const merged = [...existingDrafts, ...data.drafts];
        localStorage.setItem('aircle_drafts', JSON.stringify(merged));
        
        // Notify parent window/dashboard
        window.dispatchEvent(new CustomEvent('draftsUpdated'));
      } else {
        setError(data.error || '生成に失敗しました');
      }
    } catch (err) {
      console.error('Generation error:', err);
      setError(err instanceof Error ? err.message : '予期しないエラーが発生しました');
      
      // Fallback: generate sample drafts for testing
      if (process.env.NODE_ENV === 'development') {
        generateSampleDrafts();
      }
    } finally {
      setIsGenerating(false);
    }
  };

  // Generate sample drafts for testing
  const generateSampleDrafts = () => {
    const templates = Object.values(TEMPLATES).filter(t => t.isActive);
    const sampleDrafts: DraftPost[] = [];

    const sampleContents = [
      {
        title: 'Claude Codeの革命性について',
        content: '【結論から言います】\nClaude Codeはエンジニアの仕事を変える\n\n・自然言語でコード生成\n・30分で3日分の作業が完了\n・ハルシネーションも大幅減少\n\nこれは絶対に覚えるべきスキル\n\n#AI #ClaudeCode #エンジニア #AirCle',
      },
      {
        title: '速報：Cursorの新機能',
        content: '【速報】Cursorが新機能「Agent Mode」を発表\n\n・AIが自動でタスク実行\n・ファイル編集からコマンド実行まで\n・人間の確認ステップも設定可能\n\nコードエディターの概念が変わる\n\n#Cursor #AI #エンジニア #AirCle',
      },
      {
        title: 'Vibe Codingとは？',
        content: '【海外で大バズ】\nVibe Codingという新潮流\n\n・「雰囲気」でコードを書く\n・AIが文脈を理解して補完\n・非エンジニアも開発可能に\n\n米国で50万いいね突破\n日本でも広まりそう\n\n#VibeCoding #AI #海外トレンド #AirCle',
      },
    ];

    for (let i = 0; i < 3; i++) {
      const template = templates[i % templates.length];
      const sample = sampleContents[i % sampleContents.length];
      const now = new Date().toISOString();

      sampleDrafts.push({
        id: `draft_sample_${Date.now()}_${i}`,
        template: template,
        title: sample.title,
        content: sample.content,
        hashtags: ['#AI', '#AirCle', '#エンジニア'],
        mediaUrls: [],
        isVideo: false,
        status: 'draft',
        createdAt: now,
        updatedAt: now,
        score: Math.floor(Math.random() * 500) + 100,
      });
    }

    setGeneratedDrafts(sampleDrafts);
    
    // Save to localStorage
    const existing = localStorage.getItem('aircle_drafts');
    const existingDrafts: DraftPost[] = existing ? JSON.parse(existing) : [];
    const merged = [...existingDrafts, ...sampleDrafts];
    localStorage.setItem('aircle_drafts', JSON.stringify(merged));
  };

  const handleSaveDraft = (draft: DraftPost) => {
    const existing = localStorage.getItem('aircle_drafts');
    const existingDrafts: DraftPost[] = existing ? JSON.parse(existing) : [];
    
    // Check if already exists
    if (existingDrafts.some(d => d.id === draft.id)) {
      alert('既に保存済みです');
      return;
    }
    
    existingDrafts.push(draft);
    localStorage.setItem('aircle_drafts', JSON.stringify(existingDrafts));
    alert('保存しました！');
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#0a0a0a]/95 backdrop-blur border-b border-[#1a1a1a]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center gap-4">
            <a 
              href="/" 
              className="p-2 bg-[#1a1a1a] hover:bg-[#2a2a2a] rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400" />
            </a>
            <div>
              <h1 className="text-xl font-bold text-white">投稿案生成</h1>
              <p className="text-xs text-gray-500">AIによる投稿案の自動生成</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-400 font-medium">エラーが発生しました</p>
              <p className="text-sm text-red-300/70">{error}</p>
              <p className="text-xs text-gray-500 mt-2">
                X APIの設定を確認してください。環境変数が正しく設定されているか確認してください。
              </p>
            </div>
          </div>
        )}

        {/* Source Selection */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
            <Sparkles className="w-5 h-5 text-[#1d9bf0]" />
            生成ソースを選択
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => setSource('bookmarks')}
              className={`p-6 rounded-xl border-2 transition-all text-left ${
                source === 'bookmarks'
                  ? 'border-[#1d9bf0] bg-[#1d9bf0]/10'
                  : 'border-[#2a2a2a] bg-[#1a1a1a] hover:border-[#3a3a3a]'
              }`}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={`p-2 rounded-lg ${source === 'bookmarks' ? 'bg-[#1d9bf0]/20' : 'bg-[#2a2a2a]'}`}>
                  <Bookmark className={`w-5 h-5 ${source === 'bookmarks' ? 'text-[#1d9bf0]' : 'text-gray-400'}`} />
                </div>
                <h3 className="font-semibold text-white">Xの保存投稿</h3>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed">
                保存した投稿を元に、バズる型を参考に新しい投稿案を自動生成します。
              </p>
            </button>

            <button
              onClick={() => setSource('keywords')}
              className={`p-6 rounded-xl border-2 transition-all text-left ${
                source === 'keywords'
                  ? 'border-[#1d9bf0] bg-[#1d9bf0]/10'
                  : 'border-[#2a2a2a] bg-[#1a1a1a] hover:border-[#3a3a3a]'
              }`}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={`p-2 rounded-lg ${source === 'keywords' ? 'bg-[#1d9bf0]/20' : 'bg-[#2a2a2a]'}`}>
                  <Search className={`w-5 h-5 ${source === 'keywords' ? 'text-[#1d9bf0]' : 'text-gray-400'}`} />
                </div>
                <h3 className="font-semibold text-white">キーワード監視</h3>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed">
                Claude Code, Cursor, Vercelなどの注目キーワードから人気投稿を検索・再構成します。
              </p>
            </button>
          </div>
        </section>

        {/* Options */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-4 text-white">生成オプション</h2>
          <div className="bg-[#1a1a1a] rounded-xl border border-[#2a2a2a] p-4 space-y-4">
            {/* Limit */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                生成数: <span className="text-white font-medium">{limit}件</span>
              </label>
              <input
                type="range"
                min="1"
                max="60"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="w-full accent-[#1d9bf0]"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>1件</span>
                <span>60件</span>
              </div>
            </div>
          </div>
        </section>

        {/* Template Info */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-4 text-white">使用されるテンプレート</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {Object.values(TEMPLATES).filter(t => t.isActive).map((template) => (
              <div key={template.id} className="bg-[#1a1a1a] border border-[#2a2a2a] p-4 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-white">{template.name}</span>
                  <span className="text-xs text-green-400 bg-green-400/10 px-2 py-1 rounded">
                    平均 {template.avgLikes} いいね
                  </span>
                </div>
                <p className="text-sm text-gray-500">{template.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Generate Button */}
        <section className="mb-10">
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="w-full py-4 bg-gradient-to-r from-[#1d9bf0] to-blue-600 rounded-xl font-semibold text-lg flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-[#1d9bf0]/20"
          >
            {isGenerating ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>AIが投稿案を生成中...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>投稿案を生成</span>
              </>
            )}
          </button>
          
          {savedCount > 0 && (
            <p className="text-center text-sm text-gray-500 mt-3">
              これまでに <span className="text-[#1d9bf0] font-medium">{savedCount}件</span> の投稿案を生成しました
            </p>
          )}
        </section>

        {/* Generated Drafts */}
        {generatedDrafts.length > 0 && (
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">
                生成された投稿案 
                <span className="ml-2 text-sm text-gray-500">({generatedDrafts.length}件)</span>
              </h2>
              <a 
                href="/"
                className="text-sm text-[#1d9bf0] hover:underline"
              >
                ダッシュボードで確認 →
              </a>
            </div>
            
            <div className="space-y-4">
              {generatedDrafts.map((draft) => (
                <DraftCard
                  key={draft.id}
                  draft={draft}
                  onCopy={() => {}}
                />
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
