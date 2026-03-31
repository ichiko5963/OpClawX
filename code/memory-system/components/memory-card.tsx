'use client';

import { MemoryEntry } from '@/lib/types';
import { Card, CardContent, CardHeader, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Pencil, Trash2, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MemoryCardProps {
  entry: MemoryEntry;
  onEdit?: (entry: MemoryEntry) => void;
  onDelete?: (entry: MemoryEntry) => void;
  className?: string;
}

const categoryColors: Record<string, string> = {
  '人物': 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  'プロジェクト': 'bg-purple-500/10 text-purple-500 border-purple-500/20',
  'ワークスペース': 'bg-green-500/10 text-green-500 border-green-500/20',
  '未解決課題': 'bg-red-500/10 text-red-500 border-red-500/20',
  '技術': 'bg-cyan-500/10 text-cyan-500 border-cyan-500/20',
  'ニュース': 'bg-amber-500/10 text-amber-500 border-amber-500/20',
  'Other': 'bg-gray-500/10 text-gray-500 border-gray-500/20',
};

export function MemoryCard({ entry, onEdit, onDelete, className }: MemoryCardProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const truncateContent = (content: string, maxLength: number = 150) => {
    if (content.length <= maxLength) return content;
    return content.slice(0, maxLength) + '...';
  };

  return (
    <Card className={cn(
      "group transition-all duration-200 hover:shadow-lg hover:border-red-500/30",
      "bg-card/50 backdrop-blur-sm",
      className
    )}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-lg leading-tight truncate text-foreground">
              {entry.title}
            </h3>
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
              <Badge 
                variant="outline" 
                className={cn(
                  "text-xs font-medium",
                  categoryColors[entry.category] || categoryColors['Other']
                )}
              >
                {entry.category}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {formatDate(entry.updatedAt)}
              </span>
            </div>
          </div>
          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {onEdit && (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => onEdit(entry)}
              >
                <Pencil className="h-4 w-4" />
              </Button>
            )}
            {onDelete && (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-red-500 hover:text-red-600 hover:bg-red-500/10"
                onClick={() => onDelete(entry)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pb-3">
        <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
          {truncateContent(entry.content)}
        </p>
      </CardContent>

      <CardFooter className="pt-0">
        <div className="flex flex-wrap gap-1.5">
          {entry.tags.map((tag) => (
            <Badge 
              key={tag} 
              variant="secondary"
              className="text-xs bg-red-500/5 text-red-600/80 hover:bg-red-500/10"
            >
              #{tag}
            </Badge>
          ))}
        </div>
      </CardFooter>
    </Card>
  );
}
