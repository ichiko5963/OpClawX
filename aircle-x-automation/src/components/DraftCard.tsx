'use client';

import { useState } from 'react';
import { DraftPost } from '@/types';
import { 
  CheckCircle, 
  Clock, 
  MessageSquare,
  ExternalLink,
  Copy,
  Trash2,
  Play,
  Image as ImageIcon
} from 'lucide-react';
import { TEMPLATES } from '@/lib/templates';
import { TemplateType } from '@/types';

interface DraftCardProps {
  draft: DraftPost;
  onPost?: (draft: DraftPost) => void;
  onCopy?: (content: string) => void;
  onDelete?: (id: string) => void;
  onSchedule?: (draft: DraftPost) => void;
}

export default function DraftCard({ 
  draft, 
  onPost, 
  onCopy, 
  onDelete,
  onSchedule 
}: DraftCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  const getTemplateName = (templateId: string) => {
    return TEMPLATES[templateId as TemplateType]?.name || templateId;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'posted': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'scheduled': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'draft': return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'posted': return <CheckCircle className="w-3.5 h-3.5" />;
      case 'scheduled': return <Clock className="w-3.5 h-3.5" />;
      case 'draft': return <MessageSquare className="w-3.5 h-3.5" />;
      default: return <MessageSquare className="w-3.5 h-3.5" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'posted': return '投稿済';
      case 'scheduled': return '予約';
      case 'draft': return '下書き';
      default: return status;
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(draft.content);
    setIsCopied(true);
    onCopy?.(draft.content);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handlePostToX = () => {
    // Xの投稿画面を開く（内容をコピー済み）
    const text = encodeURIComponent(draft.content);
    window.open(`https://x.com/compose/post?text=${text}`, '_blank');
    onPost?.(draft);
  };

  const formatContent = (content: string) => {
    // URLをリンク化
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return content.replace(urlRegex, (url) => {
      // video/1形式のURLは特別なスタイル
      if (url.includes('/video/1')) {
        return `<span class="text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded">${url}</span>`;
      }
      return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="text-accent-blue hover:underline">${url}</a>`;
    }).replace(/\n/g, '<br>');
  };

  return (
    <div className="bg-gradient-to-br from-[#1a1a1a] to-[#0d0d0d] rounded-xl overflow-hidden border border-[#2a2a2a] hover:border-[#3a3a3a] transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-black/20">
      {/* Header */}
      <div className="p-4 border-b border-[#2a2a2a]">
        <div className="flex items-start justify-between gap-3 mb-2">
          <h3 className="font-semibold text-white line-clamp-1 flex-1">{draft.title}</h3>
          <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${getStatusColor(draft.status)} whitespace-nowrap`}>
            {getStatusIcon(draft.status)}
            <span>{getStatusLabel(draft.status)}</span>
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="px-2 py-0.5 bg-[#2a2a2a] rounded text-gray-400">
            {getTemplateName(draft.template.id || draft.template.name)}
          </span>
          <span>•</span>
          <span>{new Date(draft.createdAt).toLocaleDateString('ja-JP')}</span>
          {draft.score && (
            <>
              <span>•</span>
              <span className="text-green-400">スコア: {draft.score}</span>
            </>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <div 
          className={`text-sm text-gray-300 whitespace-pre-wrap break-words ${isExpanded ? '' : 'line-clamp-4'}`}
          dangerouslySetInnerHTML={{ __html: formatContent(draft.content) }}
        />
        
        {!isExpanded && draft.content.length > 200 && (
          <button 
            onClick={() => setIsExpanded(true)}
            className="text-xs text-accent-blue hover:underline mt-2"
          >
            続きを表示
          </button>
        )}

        {/* Media Preview */}
        {draft.mediaUrls && draft.mediaUrls.length > 0 && (
          <div className="flex gap-2 mt-4">
            {draft.mediaUrls.slice(0, 4).map((url, i) => (
              <div 
                key={i} 
                className="w-14 h-14 bg-[#2a2a2a] rounded-lg flex items-center justify-center border border-[#3a3a3a]"
              >
                {draft.isVideo ? (
                  <div className="flex flex-col items-center">
                    <Play className="w-4 h-4 text-accent-blue" />
                    <span className="text-[10px] text-gray-500 mt-0.5">動画</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    <ImageIcon className="w-4 h-4 text-gray-400" />
                    <span className="text-[10px] text-gray-500 mt-0.5">画像</span>
                  </div>
                )}
              </div>
            ))}
            {draft.mediaUrls.length > 4 && (
              <div className="w-14 h-14 bg-[#2a2a2a] rounded-lg flex items-center justify-center border border-[#3a3a3a]">
                <span className="text-xs text-gray-400">+{draft.mediaUrls.length - 4}</span>
              </div>
            )}
          </div>
        )}

        {/* Hashtags */}
        {draft.hashtags && draft.hashtags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {draft.hashtags.slice(0, 5).map((tag, i) => (
              <span key={i} className="text-xs text-accent-blue bg-accent-blue/10 px-2 py-0.5 rounded">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-3 border-t border-[#2a2a2a] flex gap-2 bg-[#0d0d0d]/50">
        {draft.status === 'draft' && (
          <>
            <button
              onClick={handlePostToX}
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-[#1d9bf0] hover:bg-[#1a8cd8] text-white rounded-lg transition-colors text-sm font-medium"
            >
              <ExternalLink className="w-4 h-4" />
              <span>Xで投稿</span>
            </button>
            {onSchedule && (
              <button
                onClick={() => onSchedule(draft)}
                className="flex items-center justify-center gap-1.5 px-3 py-2 bg-[#2a2a2a] hover:bg-[#3a3a3a] text-white rounded-lg transition-colors text-sm"
              >
                <Clock className="w-4 h-4" />
              </button>
            )}
          </>
        )}
        
        <button
          onClick={handleCopy}
          className={`flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg transition-colors text-sm ${
            isCopied 
              ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
              : 'bg-[#2a2a2a] hover:bg-[#3a3a3a] text-white'
          }`}
          title="内容をコピー"
        >
          <Copy className="w-4 h-4" />
          {isCopied && <span className="text-xs">OK</span>}
        </button>
        
        {onDelete && (
          <button
            onClick={() => onDelete(draft.id)}
            className="flex items-center justify-center gap-1.5 px-3 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors text-sm"
            title="削除"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
