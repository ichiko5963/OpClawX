'use client';

import { useState } from 'react';
import Image from 'next/image';
import { X, Play, ZoomIn, Download, ExternalLink } from 'lucide-react';

interface MediaPreviewProps {
  mediaUrls: string[];
  isVideo?: boolean;
  videoUrl?: string;
  className?: string;
}

interface MediaModalProps {
  url: string;
  isVideo: boolean;
  onClose: () => void;
}

export default function MediaPreview({ 
  mediaUrls, 
  isVideo = false,
  videoUrl,
  className = ''
}: MediaPreviewProps) {
  const [selectedMedia, setSelectedMedia] = useState<string | null>(null);
  const [imageErrors, setImageErrors] = useState<Set<number>>(new Set());

  const handleImageError = (index: number) => {
    setImageErrors(prev => new Set(prev).add(index));
  };

  const getLayout = () => {
    const count = mediaUrls.length;
    if (count === 1) return 'grid-cols-1';
    if (count === 2) return 'grid-cols-2';
    if (count === 3) return 'grid-cols-2';
    return 'grid-cols-2';
  };

  const getItemStyle = (index: number, count: number) => {
    if (count === 3 && index === 0) return 'col-span-2 row-span-1';
    if (count === 1) return 'aspect-video';
    return 'aspect-square';
  };

  const normalizeVideoUrl = (url: string): string => {
    // Ensure URL ends with /video/1 for X videos
    if (url.includes('/video/')) {
      return url.replace(/\/video.*$/, '/video/1');
    }
    return url;
  };

  return (
    <>
      <div className={`grid ${getLayout()} gap-1 rounded-xl overflow-hidden ${className}`}>
        {mediaUrls.slice(0, 4).map((url, index) => {
          const isVideoItem = isVideo && index === 0;
          const displayUrl = isVideoItem ? normalizeVideoUrl(videoUrl || url) : url;
          const hasError = imageErrors.has(index);

          return (
            <div
              key={index}
              className={`relative group cursor-pointer overflow-hidden bg-[#1a1a1a] ${getItemStyle(index, mediaUrls.length)}`}
              onClick={() => setSelectedMedia(displayUrl)}
            >
              {hasError ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#2a2a2a]">
                  <span className="text-2xl mb-2">🖼️</span>
                  <span className="text-xs text-gray-500">画像を読み込めません</span>
                </div>
              ) : isVideoItem ? (
                <>
                  {/* Video Thumbnail */}
                  <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-12 h-12 bg-accent-blue/90 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Play className="w-6 h-6 text-white ml-1" fill="white" />
                    </div>
                  </div>
                  <div className="absolute bottom-2 left-2 right-2">
                    <span className="text-[10px] bg-black/70 px-2 py-0.5 rounded text-white">
                      動画
                    </span>
                  </div>
                  {/* Hover overlay */}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <ZoomIn className="w-6 h-6 text-white" />
                  </div>
                </>
              ) : (
                <>
                  {/* Image */}
                  <Image
                    src={url}
                    alt={`Media ${index + 1}`}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-300"
                    onError={() => handleImageError(index)}
                    unoptimized
                  />
                  {/* Hover overlay */}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <ZoomIn className="w-6 h-6 text-white" />
                  </div>
                </>
              )}

              {/* More indicator */}
              {mediaUrls.length > 4 && index === 3 && (
                <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                  <span className="text-xl font-bold text-white">+{mediaUrls.length - 4}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Modal */}
      {selectedMedia && (
        <MediaModal
          url={selectedMedia}
          isVideo={isVideo || selectedMedia.includes('/video/')}
          onClose={() => setSelectedMedia(null)}
        />
      )}
    </>
  );
}

function MediaModal({ url, isVideo, onClose }: MediaModalProps) {
  const handleDownload = async () => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `media-${Date.now()}.${isVideo ? 'mp4' : 'jpg'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handleOpenOriginal = () => {
    window.open(url, '_blank');
  };

  // Close on escape key
  if (typeof window !== 'undefined') {
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') onClose();
    });
  }

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm"
      onClick={onClose}
    >
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-2 bg-white/10 hover:bg-white/20 rounded-full text-white transition-colors z-10"
      >
        <X className="w-6 h-6" />
      </button>

      {/* Media container */}
      <div 
        className="relative max-w-4xl max-h-[85vh] w-full"
        onClick={(e) => e.stopPropagation()}
      >
        {isVideo ? (
          <div className="relative w-full aspect-video bg-black rounded-xl overflow-hidden">
            <video
              src={url}
              controls
              autoPlay
              className="w-full h-full"
              poster={url.replace('/video/1', '')}
            />
          </div>
        ) : (
          <div className="relative w-full max-h-[80vh]">
            <Image
              src={url}
              alt="Media preview"
              width={1200}
              height={800}
              className="object-contain w-full h-auto max-h-[80vh] rounded-xl"
              unoptimized
            />
          </div>
        )}

        {/* Action buttons */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-3 bg-black/70 px-4 py-2 rounded-full">
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 text-white hover:text-accent-blue transition-colors"
          >
            <Download className="w-5 h-5" />
            <span className="text-sm">ダウンロード</span>
          </button>
          <span className="text-gray-500">|</span>
          <button
            onClick={handleOpenOriginal}
            className="flex items-center gap-2 text-white hover:text-accent-blue transition-colors"
          >
            <ExternalLink className="w-5 h-5" />
            <span className="text-sm">元URLを開く</span>
          </button>
        </div>
      </div>
    </div>
  );
}

// Compact version for inline display
export function MediaPreviewCompact({ 
  mediaCount,
  isVideo,
  className = ''
}: {
  mediaCount: number;
  isVideo?: boolean;
  className?: string;
}) {
  if (mediaCount === 0) return null;

  return (
    <div className={`flex items-center gap-2 text-gray-400 text-sm ${className}`}>
      {isVideo ? (
        <div className="flex items-center gap-1 px-2 py-0.5 bg-blue-500/10 text-blue-400 rounded">
          <Play className="w-3 h-3" fill="currentColor" />
          <span className="text-xs">動画</span>
        </div>
      ) : (
        <div className="flex items-center gap-1 px-2 py-0.5 bg-purple-500/10 text-purple-400 rounded">
          <span className="text-xs">🖼️</span>
          <span className="text-xs">{mediaCount}枚</span>
        </div>
      )}
    </div>
  );
}

// URL preview component for X links
export function VideoUrlPreview({ url }: { url: string }) {
  const normalizedUrl = url.replace(/\/video.*$/, '/video/1');
  
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/20 rounded-lg">
      <Play className="w-4 h-4 text-blue-400" fill="currentColor" />
      <span className="text-sm text-blue-400 font-mono truncate max-w-[200px]">
        {normalizedUrl}
      </span>
      <button
        onClick={() => navigator.clipboard.writeText(normalizedUrl)}
        className="text-xs text-blue-400 hover:text-blue-300 ml-2"
      >
        コピー
      </button>
    </div>
  );
}
