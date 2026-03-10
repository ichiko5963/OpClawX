'use client';

import { useState, useEffect, useCallback } from 'react';
import { DraftPost, DashboardStats } from '@/types';
import DraftList from '@/components/DraftList';
import { 
  Plus, 
  RefreshCw,
  Zap,
  TrendingUp,
  FileText,
  CheckCircle2,
  Clock,
  ArrowUpRight,
  Sparkles
} from 'lucide-react';

export default function Dashboard() {
  const [drafts, setDrafts] = useState<DraftPost[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalDrafts: 0,
    postedDrafts: 0,
    scheduledDrafts: 0,
    avgEngagement: 0,
    topTemplate: '',
    recentPosts: [],
  });
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'bookmarks' | 'keywords'>('all');

  // Load drafts from API
  const loadDrafts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/generate-drafts');
      if (response.ok) {
        const data = await response.json();
        setDrafts(data.drafts || []);
        calculateStats(data.drafts || []);
      } else {
        // Fallback: try to load from localStorage
        const localDrafts = localStorage.getItem('aircle_drafts');
        if (localDrafts) {
          const parsed = JSON.parse(localDrafts);
          setDrafts(parsed);
          calculateStats(parsed);
        }
      }
    } catch (error) {
      console.error('Failed to load drafts:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Calculate stats
  const calculateStats = (draftList: DraftPost[]) => {
    const posted = draftList.filter(d => d.status === 'posted').length;
    const scheduled = draftList.filter(d => d.status === 'scheduled').length;
    const total = draftList.length;
    
    // Calculate top template
    const templateCounts: Record<string, number> = {};
    draftList.forEach(d => {
      const name = d.template?.name || '不明';
      templateCounts[name] = (templateCounts[name] || 0) + 1;
    });
    const topTemplate = Object.entries(templateCounts)
      .sort((a, b) => b[1] - a[1])[0]?.[0] || '-';
    
    // Recent posts (last 7 days)
    const recentPosts = draftList
      .filter(d => d.status === 'posted')
      .sort((a, b) => new Date(b.postedAt || b.createdAt).getTime() - new Date(a.postedAt || a.createdAt).getTime())
      .slice(0, 5);
    
    setStats({
      totalDrafts: total,
      postedDrafts: posted,
      scheduledDrafts: scheduled,
      avgEngagement: posted > 0 ? Math.round(posted / total * 100) : 0,
      topTemplate,
      recentPosts,
    });
  };

  // Generate drafts from bookmarks
  const generateFromBookmarks = async () => {
    setGenerating(true);
    try {
      const response = await fetch('/api/generate-drafts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'bookmarks', limit: 10 }),
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`${data.count}件の投稿案を生成しました！`);
        loadDrafts();
      } else {
        throw new Error('Generation failed');
      }
    } catch (error) {
      console.error('Generation error:', error);
      alert('生成に失敗しました。APIの設定を確認してください。');
    } finally {
      setGenerating(false);
    }
  };

  // Generate drafts from keywords
  const generateFromKeywords = async () => {
    setGenerating(true);
    try {
      const response = await fetch('/api/generate-drafts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'keywords', minLikes: 100 }),
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`${data.count}件の投稿案を生成しました！`);
        loadDrafts();
      } else {
        throw new Error('Generation failed');
      }
    } catch (error) {
      console.error('Generation error:', error);
      alert('生成に失敗しました。APIの設定を確認してください。');
    } finally {
      setGenerating(false);
    }
  };

  // Handle post action
  const handlePost = async (draft: DraftPost) => {
    try {
      const response = await fetch('/api/post-to-x', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draftId: draft.id, status: 'posted' }),
      });
      
      if (response.ok) {
        loadDrafts();
      }
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  // Handle delete
  const handleDelete = async (id: string) => {
    if (!confirm('削除しますか？')) return;
    
    const updatedDrafts = drafts.filter(d => d.id !== id);
    setDrafts(updatedDrafts);
    localStorage.setItem('aircle_drafts', JSON.stringify(updatedDrafts));
    calculateStats(updatedDrafts);
  };

  // Handle copy
  const handleCopy = (content: string) => {
    // Copy feedback is handled by DraftCard
  };

  useEffect(() => {
    loadDrafts();
  }, [loadDrafts]);

  // Filter drafts by tab
  const filteredDrafts = drafts.filter(draft => {
    if (activeTab === 'all') return true;
    if (activeTab === 'bookmarks') return !draft.keywords || draft.keywords.length === 0;
    if (activeTab === 'keywords') return draft.keywords && draft.keywords.length > 0;
    return true;
  });

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#0a0a0a]/95 backdrop-blur border-b border-[#1a1a1a]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#1d9bf0] to-blue-600 rounded-xl flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" fill="white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">AirCle X Automation</h1>
                <p className="text-xs text-gray-500">X投稿自動化システム</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={generateFromBookmarks}
                disabled={generating}
                className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] hover:bg-[#2a2a2a] border border-[#2a2a2a] rounded-lg transition-colors text-sm"
              >
                {generating ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4 text-purple-400" />
                )}
                <span className="hidden sm:inline">ブックマークから生成</span>
                <span className="sm:hidden">生成</span>
              </button>
              
              <button
                onClick={generateFromKeywords}
                disabled={generating}
                className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] hover:bg-[#2a2a2a] border border-[#2a2a2a] rounded-lg transition-colors text-sm"
              >
                {generating ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <TrendingUp className="w-4 h-4 text-green-400" />
                )}
                <span className="hidden sm:inline">キーワードから生成</span>
              </button>
              
              <a 
                href="/generator"
                className="flex items-center gap-2 px-4 py-2 bg-[#1d9bf0] hover:bg-[#1a8cd8] text-white rounded-lg transition-colors text-sm font-medium"
              >
                <Plus className="w-4 h-4" />
                <span>新規生成</span>
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-[#1a1a1a] to-[#0d0d0d] p-4 rounded-xl border border-[#2a2a2a]">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-gray-500" />
              <span className="text-gray-400 text-sm">総投稿案</span>
            </div>
            <div className="text-2xl font-bold text-white">{stats.totalDrafts}</div>
          </div>
          
          <div className="bg-gradient-to-br from-[#1a1a1a] to-[#0d0d0d] p-4 rounded-xl border border-[#2a2a2a]">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span className="text-gray-400 text-sm">投稿済み</span>
            </div>
            <div className="text-2xl font-bold text-green-400">{stats.postedDrafts}</div>
          </div>
          
          <div className="bg-gradient-to-br from-[#1a1a1a] to-[#0d0d0d] p-4 rounded-xl border border-[#2a2a2a]">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-yellow-500" />
              <span className="text-gray-400 text-sm">予約済み</span>
            </div>
            <div className="text-2xl font-bold text-yellow-400">{stats.scheduledDrafts}</div>
          </div>
          
          <div className="bg-gradient-to-br from-[#1a1a1a] to-[#0d0d0d] p-4 rounded-xl border border-[#2a2a2a]">
            <div className="flex items-center gap-2 mb-2">
              <ArrowUpRight className="w-4 h-4 text-blue-500" />
              <span className="text-gray-400 text-sm">使用率</span>
            </div>
            <div className="text-2xl font-bold text-blue-400">{stats.avgEngagement}%</div>
          </div>
        </div>
      </section>

      {/* Tabs & Content */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pb-12">
        {/* Tabs */}
        <div className="flex items-center gap-1 bg-[#1a1a1a] p-1 rounded-xl mb-6 inline-flex">
          {(['all', 'bookmarks', 'keywords'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab 
                  ? 'bg-[#2a2a2a] text-white' 
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {tab === 'all' && 'すべて'}
              {tab === 'bookmarks' && 'ブックマーク'}
              {tab === 'keywords' && 'キーワード'}
            </button>
          ))}
        </div>

        {/* Draft List */}
        <DraftList
          drafts={filteredDrafts}
          onPost={handlePost}
          onCopy={handleCopy}
          onDelete={handleDelete}
          loading={loading}
        />
      </section>

      {/* Quick Action FAB (Mobile) */}
      <div className="fixed bottom-6 right-6 sm:hidden">
        <a
          href="/generator"
          className="flex items-center justify-center w-14 h-14 bg-[#1d9bf0] rounded-full shadow-lg shadow-[#1d9bf0]/30"
        >
          <Plus className="w-6 h-6 text-white" />
        </a>
      </div>
    </div>
  );
}
