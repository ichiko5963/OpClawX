'use client';

import { useState } from 'react';
import { DraftPost, TemplateType } from '@/types';
import { TEMPLATES } from '@/lib/templates';
import { 
  ExternalLink, 
  Check, 
  Copy, 
  Calendar,
  Clock,
  Send,
  X
} from 'lucide-react';

interface PostButtonProps {
  draft: DraftPost;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  onPost?: (draft: DraftPost) => void;
  showSchedule?: boolean;
}

export default function PostButton({ 
  draft, 
  variant = 'primary',
  size = 'md',
  onPost,
  showSchedule = false
}: PostButtonProps) {
  const [isPosted, setIsPosted] = useState(false);
  const [isCopied, setIsCopied] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [scheduledDate, setScheduledDate] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');

  const getSizeClasses = () => {
    switch (size) {
      case 'sm': return 'px-3 py-1.5 text-xs';
      case 'lg': return 'px-6 py-3 text-base';
      default: return 'px-4 py-2 text-sm';
    }
  };

  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'bg-[#1d9bf0] hover:bg-[#1a8cd8] text-white';
      case 'secondary':
        return 'bg-[#2a2a2a] hover:bg-[#3a3a3a] text-white';
      case 'outline':
        return 'bg-transparent border border-[#1d9bf0] text-[#1d9bf0] hover:bg-[#1d9bf0]/10';
      default:
        return 'bg-[#1d9bf0] hover:bg-[#1a8cd8] text-white';
    }
  };

  const handlePost = () => {
    // Pre-fill X compose
    const formattedContent = formatPostContent(draft);
    const encodedText = encodeURIComponent(formattedContent);
    window.open(`https://x.com/compose/post?text=${encodedText}`, '_blank');
    setIsPosted(true);
    onPost?.(draft);
    setTimeout(() => setIsPosted(false), 3000);
  };

  const handleCopy = async () => {
    const formattedContent = formatPostContent(draft);
    await navigator.clipboard.writeText(formattedContent);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const formatPostContent = (draft: DraftPost): string => {
    let content = draft.content;
    
    // Add hashtags if not already included
    if (draft.hashtags && draft.hashtags.length > 0) {
      const hashtagStr = draft.hashtags.join(' ');
      if (!content.includes(hashtagStr)) {
        content += '\n\n' + hashtagStr;
      }
    }

    // For videos, add normalized URL if not at beginning
    if (draft.isVideo && draft.videoUrl) {
      const normalizedUrl = normalizeVideoUrl(draft.videoUrl);
      if (!content.startsWith(normalizedUrl)) {
        content = `${normalizedUrl}\n\n${content}`;
      }
    }

    return content;
  };

  const normalizeVideoUrl = (url: string): string => {
    let normalized = url.split('?')[0];
    normalized = normalized.replace(/\/+$/, '');
    normalized = normalized.replace(/\/video\/?1?$/, '/video/1');
    normalized = normalized.replace(/\/video\/video\//g, '/video/');
    return normalized;
  };

  const handleSchedule = () => {
    // In a real implementation, this would save to a job queue
    // For now, just close the modal
    setShowScheduleModal(false);
    alert(`予約しました: ${scheduledDate} ${scheduledTime}`);
  };

  // Get template emoji hint
  const getTemplateEmoji = () => {
    const templateId = draft.template?.id || 'conclusion';
    switch (templateId) {
      case 'conclusion': return '💡';
      case 'breaking': return '⚡';
      case 'distribution': return '🎁';
      case 'honest': return '💭';
      case 'viral': return '🌐';
      case 'official': return '📢';
      default: return '📝';
    }
  };

  return (
    <>
      {/* Button Group */}
      <div className="flex items-center gap-2">
        <button
          onClick={handlePost}
          className={`flex items-center gap-2 rounded-lg font-medium transition-all duration-200 ${getSizeClasses()} ${getVariantClasses()}`}
        >
          {isPosted ? (
            <>
              <Check className="w-4 h-4" />
              <span>投稿済</span>
            </>
          ) : (
            <>
              <ExternalLink className="w-4 h-4" />
              <span>Xで投稿</span>
              <span className="text-xs opacity-70">{getTemplateEmoji()}</span>
            </>
          )}
        </button>

        <button
          onClick={handleCopy}
          className={`flex items-center gap-2 rounded-lg font-medium transition-all duration-200 px-3 py-2 text-sm ${
            isCopied 
              ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
              : 'bg-[#2a2a2a] hover:bg-[#3a3a3a] text-white'
          }`}
          title="内容をコピー"
        >
          {isCopied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
        </button>

        {showSchedule && (
          <button
            onClick={() => setShowScheduleModal(true)}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-[#2a2a2a] hover:bg-[#3a3a3a] text-white rounded-lg transition-colors"
            title="予約投稿"
          >
            <Calendar className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Schedule Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">予約投稿</h3>
              <button 
                onClick={() => setShowScheduleModal(false)}
                className="p-1 hover:bg-[#2a2a2a] rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">日付</label>
                <input
                  type="date"
                  value={scheduledDate}
                  onChange={(e) => setScheduledDate(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0d0d0d] border border-[#2a2a2a] rounded-lg focus:border-accent-blue outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">時間</label>
                <input
                  type="time"
                  value={scheduledTime}
                  onChange={(e) => setScheduledTime(e.target.value)}
                  className="w-full px-4 py-2 bg-[#0d0d0d] border border-[#2a2a2a] rounded-lg focus:border-accent-blue outline-none"
                />
              </div>
              <div className="bg-[#0d0d0d] p-3 rounded-lg">
                <p className="text-xs text-gray-500 mb-1">投稿内容プレビュー:</p>
                <p className="text-sm text-gray-300 line-clamp-3">{draft.content}</p>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowScheduleModal(false)}
                className="flex-1 px-4 py-2 bg-[#2a2a2a] hover:bg-[#3a3a3a] text-white rounded-lg transition-colors"
              >
                キャンセル
              </button>
              <button
                onClick={handleSchedule}
                disabled={!scheduledDate || !scheduledTime}
                className="flex-1 px-4 py-2 bg-accent-blue hover:bg-[#1a8cd8] text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                予約する
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// Standalone component for quick actions
export function PostButtonGroup({ 
  draft,
  onPost 
}: { 
  draft: DraftPost;
  onPost?: () => void;
}) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(draft.content);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleOpenX = () => {
    const encodedText = encodeURIComponent(draft.content);
    window.open(`https://x.com/compose/post?text=${encodedText}`, '_blank');
    onPost?.();
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleOpenX}
        className="flex items-center gap-2 px-4 py-2 bg-[#1d9bf0] hover:bg-[#1a8cd8] text-white rounded-lg transition-colors font-medium"
      >
        <Send className="w-4 h-4" />
        <span>投稿</span>
      </button>
      <button
        onClick={handleCopy}
        className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
          isCopied 
            ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
            : 'bg-[#2a2a2a] hover:bg-[#3a3a3a] text-white'
        }`}
      >
        {isCopied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
      </button>
    </div>
  );
}
