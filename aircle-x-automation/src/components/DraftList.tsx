'use client';

import { useState, useMemo, useEffect } from 'react';
import { DraftPost } from '@/types';
import DraftCard from './DraftCard';
import { 
  Grid3X3, 
  List,
  SlidersHorizontal,
  Search,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface DraftListProps {
  drafts: DraftPost[];
  onPost?: (draft: DraftPost) => void;
  onCopy?: (content: string) => void;
  onDelete?: (id: string) => void;
  onSchedule?: (draft: DraftPost) => void;
  loading?: boolean;
}

type ViewMode = 'grid' | 'list';
type SortField = 'createdAt' | 'status' | 'score' | 'template';
type SortOrder = 'asc' | 'desc';

export default function DraftList({ 
  drafts, 
  onPost, 
  onCopy, 
  onDelete,
  onSchedule,
  loading = false
}: DraftListProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('createdAt');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 9;

  // Filter and sort drafts
  const filteredDrafts = useMemo(() => {
    let result = [...drafts];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(draft =>
        draft.title.toLowerCase().includes(query) ||
        draft.content.toLowerCase().includes(query) ||
        draft.hashtags?.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      result = result.filter(draft => draft.status === statusFilter);
    }

    // Sort
    result.sort((a, b) => {
      let comparison = 0;
      switch (sortField) {
        case 'createdAt':
          comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
        case 'score':
          comparison = (a.score || 0) - (b.score || 0);
          break;
        case 'template':
          comparison = (a.template?.name || '').localeCompare(b.template?.name || '');
          break;
      }
      return sortOrder === 'desc' ? -comparison : comparison;
    });

    return result;
  }, [drafts, searchQuery, statusFilter, sortField, sortOrder]);

  // Pagination
  const totalPages = Math.ceil(filteredDrafts.length / itemsPerPage);
  const paginatedDrafts = filteredDrafts.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, statusFilter, sortField, sortOrder]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'posted': return 'text-green-400';
      case 'scheduled': return 'text-yellow-400';
      case 'draft': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 border-2 border-accent-blue border-t-transparent rounded-full animate-spin"></div>
          <span className="text-gray-400">読み込み中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-[#1a1a1a] p-4 rounded-xl border border-[#2a2a2a]">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="投稿案を検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-[#0d0d0d] border border-[#2a2a2a] rounded-lg focus:border-accent-blue focus:ring-1 focus:ring-accent-blue outline-none transition-colors text-sm"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-[#0d0d0d] border border-[#2a2a2a] rounded-lg focus:border-accent-blue outline-none text-sm"
          >
            <option value="all">すべてのステータス</option>
            <option value="draft">下書き</option>
            <option value="scheduled">予約済み</option>
            <option value="posted">投稿済み</option>
            <option value="archived">アーカイブ</option>
          </select>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <select
              value={sortField}
              onChange={(e) => setSortField(e.target.value as SortField)}
              className="px-3 py-2 bg-[#0d0d0d] border border-[#2a2a2a] rounded-lg focus:border-accent-blue outline-none text-sm"
            >
              <option value="createdAt">作成日</option>
              <option value="status">ステータス</option>
              <option value="score">スコア</option>
              <option value="template">テンプレート</option>
            </select>
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="px-3 py-2 bg-[#0d0d0d] border border-[#2a2a2a] rounded-lg hover:border-[#3a3a3a] transition-colors text-sm"
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center bg-[#0d0d0d] border border-[#2a2a2a] rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded transition-colors ${viewMode === 'grid' ? 'bg-[#2a2a2a] text-white' : 'text-gray-500 hover:text-white'}`}
            >
              <Grid3X3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded transition-colors ${viewMode === 'list' ? 'bg-[#2a2a2a] text-white' : 'text-gray-500 hover:text-white'}`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Results count */}
      <div className="text-sm text-gray-500 px-1">
        {filteredDrafts.length} 件の投稿案
        {searchQuery && `（"${searchQuery}" で検索）`}
      </div>

      {/* Drafts Grid/List */}
      {filteredDrafts.length > 0 ? (
        <>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {paginatedDrafts.map((draft) => (
                <DraftCard
                  key={draft.id}
                  draft={draft}
                  onPost={onPost}
                  onCopy={onCopy}
                  onDelete={onDelete}
                  onSchedule={onSchedule}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {paginatedDrafts.map((draft) => (
                <DraftCard
                  key={draft.id}
                  draft={draft}
                  onPost={onPost}
                  onCopy={onCopy}
                  onDelete={onDelete}
                  onSchedule={onSchedule}
                />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-6">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-2 rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] hover:border-[#3a3a3a] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              
              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                      currentPage === page
                        ? 'bg-accent-blue text-white'
                        : 'bg-[#1a1a1a] border border-[#2a2a2a] hover:border-[#3a3a3a]'
                    }`}
                  >
                    {page}
                  </button>
                ))}
              </div>
              
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-2 rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] hover:border-[#3a3a3a] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-16 bg-[#1a1a1a] rounded-xl border border-[#2a2a2a]">
          <div className="text-5xl mb-4">📝</div>
          <h3 className="text-lg font-semibold mb-2">投稿案がありません</h3>
          <p className="text-gray-500 mb-6">
            {searchQuery || statusFilter !== 'all' 
              ? 'フィルタ条件に一致する投稿案が見つかりません'
              : '新規生成から投稿案を作成してください'
            }
          </p>
          {(!searchQuery && statusFilter === 'all') && (
            <a 
              href="/generator"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-accent-blue hover:bg-[#1a8cd8] rounded-lg transition-colors"
            >
              <span>投稿案を生成</span>
            </a>
          )}
        </div>
      )}
    </div>
  );
}
