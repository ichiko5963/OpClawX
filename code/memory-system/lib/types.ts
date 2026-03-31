export interface MemoryEntry {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  source: 'MEMORY.md' | string;
}

export interface GitHubConfig {
  owner: string;
  repo: string;
  branch: string;
  token: string;
}

export type MemoryCategory = 
  | '人物' 
  | 'プロジェクト' 
  | 'ワークスペース' 
  | '未解決課題'
  | '技術'
  | 'ニュース'
  | 'Other';

export const CATEGORIES: MemoryCategory[] = [
  '人物',
  'プロジェクト', 
  'ワークスペース',
  '未解決課題',
  '技術',
  'ニュース',
  'Other'
];
