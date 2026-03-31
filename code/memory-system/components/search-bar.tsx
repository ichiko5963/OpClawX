'use client';

import { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Search, X, Filter, Tag } from 'lucide-react';
import { CATEGORIES } from '@/lib/types';
import { cn } from '@/lib/utils';

interface SearchBarProps {
  query: string;
  onQueryChange: (query: string) => void;
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
  selectedTags: string[];
  onTagsChange: (tags: string[]) => void;
  availableTags: string[];
  resultCount: number;
  className?: string;
}

export function SearchBar({
  query,
  onQueryChange,
  selectedCategory,
  onCategoryChange,
  selectedTags,
  onTagsChange,
  availableTags,
  resultCount,
  className,
}: SearchBarProps) {
  const [showFilters, setShowFilters] = useState(false);

  const hasActiveFilters = selectedCategory || selectedTags.length > 0;

  const toggleTag = (tag: string) => {
    if (selectedTags.includes(tag)) {
      onTagsChange(selectedTags.filter(t => t !== tag));
    } else {
      onTagsChange([...selectedTags, tag]);
    }
  };

  const clearFilters = () => {
    onCategoryChange(null);
    onTagsChange([]);
    onQueryChange('');
  };

  return (
    <div className={cn("space-y-4", className)}>
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Search memories..."
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          className="pl-10 pr-20 h-11 bg-background/50 backdrop-blur-sm border-muted-foreground/20 focus:border-red-500/50"
        />
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {query && (
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-muted-foreground hover:text-foreground"
              onClick={() => onQueryChange('')}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "h-7 px-2 text-xs gap-1",
              showFilters && "bg-red-500/10 text-red-500"
            )}
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="h-3 w-3" />
            Filter
          </Button>
        </div>
      </div>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="flex items-center gap-2 text-sm">
          <span className="text-muted-foreground">Active filters:</span>
          {selectedCategory && (
            <Badge 
              variant="secondary" 
              className="gap-1 cursor-pointer hover:bg-destructive/10"
              onClick={() => onCategoryChange(null)}
            >
              {selectedCategory}
              <X className="h-3 w-3" />
            </Badge>
          )}
          {selectedTags.map(tag => (
            <Badge 
              key={tag}
              variant="secondary" 
              className="gap-1 cursor-pointer hover:bg-destructive/10"
              onClick={() => toggleTag(tag)}
            >
              #{tag}
              <X className="h-3 w-3" />
            </Badge>
          ))}
          <Button
            variant="ghost"
            size="sm"
            className="h-6 text-xs text-muted-foreground"
            onClick={clearFilters}
          >
            Clear all
          </Button>
        </div>
      )}

      {/* Expanded Filters */}
      {showFilters && (
        <div className="space-y-4 p-4 rounded-lg bg-muted/30 border border-muted">
          {/* Categories */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Category</label>
            <div className="flex flex-wrap gap-2">
              <Button
                variant={selectedCategory === null ? 'default' : 'outline'}
                size="sm"
                className={cn(
                  "text-xs",
                  selectedCategory === null && "bg-red-500 hover:bg-red-600"
                )}
                onClick={() => onCategoryChange(null)}
              >
                All
              </Button>
              {CATEGORIES.map((cat) => (
                <Button
                  key={cat}
                  variant={selectedCategory === cat ? 'default' : 'outline'}
                  size="sm"
                  className={cn(
                    "text-xs",
                    selectedCategory === cat && "bg-red-500 hover:bg-red-600"
                  )}
                  onClick={() => onCategoryChange(cat)}
                >
                  {cat}
                </Button>
              ))}
            </div>
          </div>

          {/* Tags */}
          {availableTags.length > 0 && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                <Tag className="h-3 w-3" />
                Tags
              </label>
              <ScrollArea className="h-24">
                <div className="flex flex-wrap gap-2">
                  {availableTags.map((tag) => (
                    <Badge
                      key={tag}
                      variant={selectedTags.includes(tag) ? 'default' : 'outline'}
                      className={cn(
                        "cursor-pointer text-xs",
                        selectedTags.includes(tag) 
                          ? "bg-red-500 hover:bg-red-600" 
                          : "hover:bg-muted"
                      )}
                      onClick={() => toggleTag(tag)}
                    >
                      #{tag}
                    </Badge>
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}
        </div>
      )}

      {/* Result Count */}
      <div className="text-sm text-muted-foreground">
        {resultCount} {resultCount === 1 ? 'memory' : 'memories'} found
      </div>
    </div>
  );
}
