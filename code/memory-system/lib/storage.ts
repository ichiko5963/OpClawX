import { MemoryEntry } from './types';

// Sample data based on the existing MEMORY.md
export const sampleMemoryEntries: MemoryEntry[] = [
  {
    id: 'mem-1',
    title: 'ichiko',
    content: `ワークスペースオーナー。AIx マーケティング、バイブコーディング、プロダクト開発が軸。
Xアカウント2つ運用: @aircle_ai (AirCle / 学生AI団体) と @ichiaimarketer (いち@AIxマケ)
OpClawX プロジェクト（バイラル投稿自動化ツール）を開発中`,
    category: '人物',
    tags: ['owner', 'ai-marketing', 'vibe-coding'],
    createdAt: '2026-03-15T00:00:00Z',
    updatedAt: '2026-03-15T00:00:00Z',
    source: 'MEMORY.md',
  },
  {
    id: 'mem-2',
    title: 'OpClawX',
    content: `Your Knowledge, Automated — 経験×AIでバイラル投稿を自動生成。5言語対応、1日3回配信、15パターン生成。`,
    category: 'プロジェクト',
    tags: ['automation', 'viral', 'x-posts'],
    createdAt: '2026-03-15T00:00:00Z',
    updatedAt: '2026-03-15T00:00:00Z',
    source: 'MEMORY.md',
  },
  {
    id: 'mem-3',
    title: 'AirCle',
    content: `日本最大級の学生AI団体。バイブコーディング講義、note無料配布などで急成長。`,
    category: 'プロジェクト',
    tags: ['student', 'ai', 'community'],
    createdAt: '2026-03-15T00:00:00Z',
    updatedAt: '2026-03-15T00:00:00Z',
    source: 'MEMORY.md',
  },
  {
    id: 'mem-4',
    title: 'ワークスペース構造',
    content: `projects/ — X投稿ファイル等
scripts/ — 自動化スクリプト（daily_digest.py, x_posts_to_csv.py, meeting_prep_reminder.py）
bin/ — git-auto-sync.sh
reports/ — 日次レポート
memory/ — 日次メモリ
aircle-x-automation/ — AirCleのX自動化（Next.js）
viral-post-automation/ — バイラル投稿生成
mission-control/ — ミッションコントロール
x-posts/ — X投稿管理`,
    category: 'ワークスペース',
    tags: ['structure', 'folders'],
    createdAt: '2026-03-15T00:00:00Z',
    updatedAt: '2026-03-15T00:00:00Z',
    source: 'MEMORY.md',
  },
  {
    id: 'mem-5',
    title: '未解決課題 (BACKLOG)',
    content: `• Google API認証が切れている（2/24〜）→ Gmail/Calendar/Drive全滅
• cronジョブ用スクリプト多数不足
• viral-posts-daily-generatorのDiscord配信未設定`,
    category: '未解決課題',
    tags: ['google-api', 'cron', 'discord'],
    createdAt: '2026-03-15T00:00:00Z',
    updatedAt: '2026-03-15T00:00:00Z',
    source: 'MEMORY.md',
  },
  {
    id: 'mem-6',
    title: 'AirCle X投稿の傾向',
    content: `• バズりやすい型: 【速報】系、【無料配布】系、AIツール紹介
• 最高いいね: 5,347（「日本最大級の学生AI団体が最速で作成した」）
• 次点: 3,871（速報系ノート投稿）
• エンゲージメント高い投稿: 150〜300文字のノート投稿が最適
• 【速報】【結論から言います】【海外で大バズ】がフック文として強い`,
    category: 'プロジェクト',
    tags: ['analytics', 'engagement', 'trends'],
    createdAt: '2026-03-15T00:00:00Z',
    updatedAt: '2026-03-15T00:00:00Z',
    source: 'MEMORY.md',
  },
  {
    id: 'mem-7',
    title: 'ツール・技術スタック',
    content: `• Claude Code, Cursor, Antigravity (Google), OpenClaw
• Next.js, Vercel, Supabase
• v0 by Vercel（UI生成）
• ElevenLabs TTS (sag)`,
    category: '技術',
    tags: ['tools', 'stack', 'ai'],
    createdAt: '2026-03-15T00:00:00Z',
    updatedAt: '2026-03-15T00:00:00Z',
    source: 'MEMORY.md',
  },
  {
    id: 'mem-8',
    title: '最新ニュース（2026年3月中旬）',
    content: `• Cursor: $500億評価額で資金調達交渉中（Bloomberg 3/12）
• Lovable: ARR $400M、1ヶ月で$100M増、社員146人
• Replit: $90億評価額
• Anthropic: 1Mコンテキスト標準価格化（3/13）、Code Review + Security発表（3/9）
• Base44: ソロ開発者が創業6ヶ月でWixに$80M買収される
• Cognition: OpenAIが失敗したWindsurf買収を成功
• バイブコーディング: Collins辞典 2025 Word of the Year、エンタープライズ変革文脈でForbes特集`,
    category: 'ニュース',
    tags: ['startup', 'funding', 'ai-tools', 'trends'],
    createdAt: '2026-03-15T00:00:00Z',
    updatedAt: '2026-03-15T00:00:00Z',
    source: 'MEMORY.md',
  },
];

export function getStoredMemories(): MemoryEntry[] {
  if (typeof window === 'undefined') return sampleMemoryEntries;
  
  const stored = localStorage.getItem('memory-entries');
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      return sampleMemoryEntries;
    }
  }
  return sampleMemoryEntries;
}

export function storeMemories(entries: MemoryEntry[]): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('memory-entries', JSON.stringify(entries));
}

export function addMemory(entry: Omit<MemoryEntry, 'id' | 'createdAt' | 'updatedAt'>): MemoryEntry {
  const newEntry: MemoryEntry = {
    ...entry,
    id: `mem-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  
  const memories = getStoredMemories();
  memories.push(newEntry);
  storeMemories(memories);
  
  return newEntry;
}

export function updateMemory(id: string, updates: Partial<MemoryEntry>): MemoryEntry | null {
  const memories = getStoredMemories();
  const index = memories.findIndex(m => m.id === id);
  
  if (index === -1) return null;
  
  memories[index] = {
    ...memories[index],
    ...updates,
    updatedAt: new Date().toISOString(),
  };
  
  storeMemories(memories);
  return memories[index];
}

export function deleteMemory(id: string): boolean {
  const memories = getStoredMemories();
  const filtered = memories.filter(m => m.id !== id);
  
  if (filtered.length === memories.length) return false;
  
  storeMemories(filtered);
  return true;
}

export function searchMemories(
  entries: MemoryEntry[],
  query: string,
  category?: string,
  tags?: string[]
): MemoryEntry[] {
  return entries.filter(entry => {
    const matchesQuery = !query || 
      entry.title.toLowerCase().includes(query.toLowerCase()) ||
      entry.content.toLowerCase().includes(query.toLowerCase());
    
    const matchesCategory = !category || entry.category === category;
    
    const matchesTags = !tags || tags.length === 0 || 
      tags.some(tag => entry.tags.includes(tag));
    
    return matchesQuery && matchesCategory && matchesTags;
  });
}

export function getAllTags(entries: MemoryEntry[]): string[] {
  const tagSet = new Set<string>();
  entries.forEach(entry => {
    entry.tags.forEach(tag => tagSet.add(tag));
  });
  return Array.from(tagSet).sort();
}

export function getCategoryCounts(entries: MemoryEntry[]): Record<string, number> {
  const counts: Record<string, number> = {};
  entries.forEach(entry => {
    counts[entry.category] = (counts[entry.category] || 0) + 1;
  });
  return counts;
}
