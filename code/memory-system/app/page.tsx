'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { MemoryEntry, GitHubConfig } from '@/lib/types';
import { GitHubSync } from '@/lib/github';
import { 
  getStoredMemories, 
  storeMemories, 
  addMemory, 
  updateMemory, 
  deleteMemory,
  searchMemories,
  getAllTags,
} from '@/lib/storage';
import { MemoryCard } from '@/components/memory-card';
import { SearchBar } from '@/components/search-bar';
import { MemoryFormDialog } from '@/components/memory-form-dialog';
import { GitHubConfigDialog } from '@/components/github-config-dialog';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Toaster } from '@/components/ui/sonner';
import { toast } from 'sonner';
import { 
  Plus, 
  Github, 
  RefreshCw, 
  Brain, 
  Settings,
  Upload,
  Download,
  Trash2,
  Moon,
  Sun,
  LayoutGrid,
  List
} from 'lucide-react';
import { cn } from '@/lib/utils';

type ViewMode = 'grid' | 'list';

export default function MemorySystem() {
  // State
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [query, setQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [formOpen, setFormOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState<MemoryEntry | null>(null);
  const [githubConfigOpen, setGithubConfigOpen] = useState(false);
  const [githubConfig, setGithubConfig] = useState<GitHubConfig | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [isLoaded, setIsLoaded] = useState(false);

  // Load initial data
  useEffect(() => {
    const loaded = getStoredMemories();
    setMemories(loaded);
    
    // Load GitHub config from localStorage
    const savedConfig = localStorage.getItem('github-config');
    if (savedConfig) {
      try {
        setGithubConfig(JSON.parse(savedConfig));
      } catch {
        console.error('Failed to parse GitHub config');
      }
    }

    // Load dark mode preference
    const savedDarkMode = localStorage.getItem('dark-mode');
    if (savedDarkMode) {
      setDarkMode(JSON.parse(savedDarkMode));
    } else {
      setDarkMode(window.matchMedia('(prefers-color-scheme: dark)').matches);
    }

    setIsLoaded(true);
  }, []);

  // Apply dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('dark-mode', JSON.stringify(darkMode));
  }, [darkMode]);

  // Filtered memories
  const filteredMemories = useMemo(() => {
    return searchMemories(memories, query, selectedCategory || undefined, selectedTags);
  }, [memories, query, selectedCategory, selectedTags]);

  // All available tags
  const allTags = useMemo(() => {
    return getAllTags(memories);
  }, [memories]);

  // Category counts
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { 'All': memories.length };
    memories.forEach(m => {
      counts[m.category] = (counts[m.category] || 0) + 1;
    });
    return counts;
  }, [memories]);

  // Handlers
  const handleAddMemory = useCallback((entry: Omit<MemoryEntry, 'id' | 'createdAt' | 'updatedAt'>) => {
    const newEntry = addMemory(entry);
    setMemories(getStoredMemories());
    toast.success('Memory added successfully');
  }, []);

  const handleEditMemory = useCallback((entry: Omit<MemoryEntry, 'id' | 'createdAt' | 'updatedAt'>) => {
    if (editingEntry) {
      updateMemory(editingEntry.id, entry);
      setMemories(getStoredMemories());
      setEditingEntry(null);
      toast.success('Memory updated successfully');
    }
  }, [editingEntry]);

  const handleDeleteMemory = useCallback((entry: MemoryEntry) => {
    if (confirm(`Are you sure you want to delete "${entry.title}"?`)) {
      deleteMemory(entry.id);
      setMemories(getStoredMemories());
      toast.success('Memory deleted successfully');
    }
  }, []);

  const openEditDialog = useCallback((entry: MemoryEntry) => {
    setEditingEntry(entry);
    setFormOpen(true);
  }, []);

  const openAddDialog = useCallback(() => {
    setEditingEntry(null);
    setFormOpen(true);
  }, []);

  const handleSaveGithubConfig = useCallback((config: GitHubConfig) => {
    setGithubConfig(config);
    localStorage.setItem('github-config', JSON.stringify(config));
    toast.success('GitHub configuration saved');
  }, []);

  const handlePullFromGitHub = useCallback(async () => {
    if (!githubConfig) {
      setGithubConfigOpen(true);
      return;
    }

    setIsSyncing(true);
    try {
      const sync = new GitHubSync(githubConfig);
      const remoteMemories = await sync.fetchMemoryFiles();
      
      // Merge with existing memories (avoid duplicates by title)
      const existingTitles = new Set(memories.map(m => m.title.toLowerCase()));
      const newMemories = remoteMemories.filter(m => !existingTitles.has(m.title.toLowerCase()));
      
      const merged = [...memories, ...newMemories];
      storeMemories(merged);
      setMemories(merged);
      
      toast.success(`Pulled ${newMemories.length} new memories from GitHub`);
    } catch (error) {
      toast.error('Failed to pull from GitHub: ' + (error as Error).message);
    } finally {
      setIsSyncing(false);
    }
  }, [githubConfig, memories]);

  const handlePushToGitHub = useCallback(async () => {
    if (!githubConfig) {
      setGithubConfigOpen(true);
      return;
    }

    setIsSyncing(true);
    try {
      const sync = new GitHubSync(githubConfig);
      
      // Push a few recent memories as examples
      const recentMemories = memories.slice(0, 5);
      for (const memory of recentMemories) {
        await sync.pushMemoryEntry(memory, `Update memory: ${memory.title}`);
      }
      
      toast.success(`Pushed ${recentMemories.length} memories to GitHub`);
    } catch (error) {
      toast.error('Failed to push to GitHub: ' + (error as Error).message);
    } finally {
      setIsSyncing(false);
    }
  }, [githubConfig, memories]);

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex items-center gap-2 text-red-500">
          <Brain className="h-6 w-6 animate-pulse" />
          <span className="text-lg font-medium">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Toaster position="top-right" richColors />
      
      {/* Header */}
      <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-500">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">Memory System</h1>
              <p className="text-xs text-muted-foreground">OpenClaw Workspace</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* View Mode Toggle */}
            <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as ViewMode)}>
              <TabsList className="h-8">
                <TabsTrigger value="grid" className="px-2">
                  <LayoutGrid className="h-4 w-4" />
                </TabsTrigger>
                <TabsTrigger value="list" className="px-2">
                  <List className="h-4 w-4" />
                </TabsTrigger>
              </TabsList>
            </Tabs>

            {/* Dark Mode Toggle */}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => setDarkMode(!darkMode)}
            >
              {darkMode ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>

            {/* GitHub Actions */}
            <Button
              variant="outline"
              size="sm"
              className="gap-2"
              onClick={handlePullFromGitHub}
              disabled={isSyncing}
            >
              <Download className={cn("h-4 w-4", isSyncing && "animate-bounce")} />
              Pull
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="gap-2"
              onClick={handlePushToGitHub}
              disabled={isSyncing}
            >
              <Upload className={cn("h-4 w-4", isSyncing && "animate-bounce")} />
              Push
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={cn("h-8 w-8", githubConfig && "text-green-500")}
              onClick={() => setGithubConfigOpen(true)}
            >
              <Github className="h-4 w-4" />
            </Button>

            <Separator orientation="vertical" className="h-6 mx-2" />

            {/* Add Memory */}
            <Button
              onClick={openAddDialog}
              className="gap-2 bg-red-500 hover:bg-red-600"
            >
              <Plus className="h-4 w-4" />
              Add Memory
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Search & Filters */}
        <div className="mb-8">
          <SearchBar
            query={query}
            onQueryChange={setQuery}
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            selectedTags={selectedTags}
            onTagsChange={setSelectedTags}
            availableTags={allTags}
            resultCount={filteredMemories.length}
          />
        </div>

        {/* Category Tabs */}
        <div className="mb-6">
          <ScrollArea className="w-full whitespace-nowrap">
            <div className="flex gap-2 pb-2">
              <Button
                variant={selectedCategory === null ? 'default' : 'outline'}
                size="sm"
                className={cn(
                  selectedCategory === null && "bg-red-500 hover:bg-red-600"
                )}
                onClick={() => setSelectedCategory(null)}
              >
                All
                <span className="ml-2 text-xs opacity-70">
                  {categoryCounts['All'] || 0}
                </span>
              </Button>
              {Object.entries(categoryCounts)
                .filter(([cat]) => cat !== 'All')
                .sort(([, a], [, b]) => b - a)
                .map(([cat, count]) => (
                  <Button
                    key={cat}
                    variant={selectedCategory === cat ? 'default' : 'outline'}
                    size="sm"
                    className={cn(
                      selectedCategory === cat && "bg-red-500 hover:bg-red-600"
                    )}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                    <span className="ml-2 text-xs opacity-70">{count}</span>
                  </Button>
                ))}
            </div>
          </ScrollArea>
        </div>

        {/* Memory Grid/List */}
        {filteredMemories.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <Brain className="h-16 w-16 text-muted-foreground/30 mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground">
              No memories found
            </h3>
            <p className="text-sm text-muted-foreground/70 mt-1">
              {query || selectedCategory || selectedTags.length > 0
                ? 'Try adjusting your search or filters'
                : 'Start by adding your first memory'}
            </p>
            {(query || selectedCategory || selectedTags.length > 0) && (
              <Button
                variant="outline"
                className="mt-4"
                onClick={() => {
                  setQuery('');
                  setSelectedCategory(null);
                  setSelectedTags([]);
                }}
              >
                Clear Filters
              </Button>
            )}
          </div>
        ) : (
          <div className={cn(
            "grid gap-4",
            viewMode === 'grid' 
              ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3" 
              : "grid-cols-1"
          )}>
            {filteredMemories.map((entry) => (
              <MemoryCard
                key={entry.id}
                entry={entry}
                onEdit={openEditDialog}
                onDelete={handleDeleteMemory}
              />
            ))}
          </div>
        )}
      </main>

      {/* Dialogs */}
      <MemoryFormDialog
        entry={editingEntry}
        open={formOpen}
        onOpenChange={setFormOpen}
        onSave={editingEntry ? handleEditMemory : handleAddMemory}
        availableTags={allTags}
      />

      <GitHubConfigDialog
        open={githubConfigOpen}
        onOpenChange={setGithubConfigOpen}
        config={githubConfig}
        onSave={handleSaveGithubConfig}
      />
    </div>
  );
}
