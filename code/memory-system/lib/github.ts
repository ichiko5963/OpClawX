import { Octokit } from 'octokit';
import matter from 'gray-matter';
import { MemoryEntry, GitHubConfig } from './types';

export class GitHubSync {
  private octokit: Octokit;
  private config: GitHubConfig;

  constructor(config: GitHubConfig) {
    this.octokit = new Octokit({ auth: config.token });
    this.config = config;
  }

  async fetchMemoryFiles(): Promise<MemoryEntry[]> {
    const entries: MemoryEntry[] = [];
    
    try {
      // Fetch MEMORY.md
      const mainMemory = await this.fetchFile('MEMORY.md');
      if (mainMemory) {
        entries.push(...this.parseMemoryContent(mainMemory, 'MEMORY.md'));
      }

      // Fetch memory/ folder files
      const memoryFiles = await this.listDirectoryFiles('memory');
      for (const file of memoryFiles) {
        if (file.endsWith('.md')) {
          const content = await this.fetchFile(file);
          if (content) {
            entries.push(...this.parseMemoryContent(content, file));
          }
        }
      }
    } catch (error) {
      console.error('Error fetching from GitHub:', error);
      throw error;
    }

    return entries;
  }

  private async fetchFile(path: string): Promise<string | null> {
    try {
      const response = await this.octokit.rest.repos.getContent({
        owner: this.config.owner,
        repo: this.config.repo,
        path,
        ref: this.config.branch,
      });

      if ('content' in response.data) {
        return Buffer.from(response.data.content, 'base64').toString('utf-8');
      }
      return null;
    } catch (error) {
      console.warn(`Could not fetch ${path}:`, error);
      return null;
    }
  }

  private async listDirectoryFiles(path: string): Promise<string[]> {
    try {
      const response = await this.octokit.rest.repos.getContent({
        owner: this.config.owner,
        repo: this.config.repo,
        path,
        ref: this.config.branch,
      });

      if (Array.isArray(response.data)) {
        return response.data
          .filter(item => item.type === 'file')
          .map(item => `${path}/${item.name}`);
      }
      return [];
    } catch (error) {
      console.warn(`Could not list directory ${path}:`, error);
      return [];
    }
  }

  private parseMemoryContent(content: string, source: string): MemoryEntry[] {
    const entries: MemoryEntry[] = [];
    
    // Try to parse frontmatter first
    const parsed = matter(content);
    if (parsed.data.title || parsed.data.category) {
      entries.push({
        id: this.generateId(),
        title: parsed.data.title || 'Untitled',
        content: parsed.content,
        category: parsed.data.category || 'Other',
        tags: parsed.data.tags || [],
        createdAt: parsed.data.createdAt || new Date().toISOString(),
        updatedAt: parsed.data.updatedAt || new Date().toISOString(),
        source,
      });
    } else {
      // Parse sections as individual entries
      const sections = this.parseSections(content);
      sections.forEach(section => {
        entries.push({
          id: this.generateId(),
          title: section.title,
          content: section.content,
          category: this.inferCategory(section.title, section.content),
          tags: this.extractTags(section.content),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          source,
        });
      });
    }

    return entries;
  }

  private parseSections(content: string): { title: string; content: string }[] {
    const sections: { title: string; content: string }[] = [];
    const lines = content.split('\n');
    
    let currentTitle = '';
    let currentContent: string[] = [];

    for (const line of lines) {
      if (line.startsWith('## ')) {
        if (currentTitle) {
          sections.push({
            title: currentTitle.replace('## ', '').trim(),
            content: currentContent.join('\n').trim(),
          });
        }
        currentTitle = line;
        currentContent = [];
      } else if (currentTitle) {
        currentContent.push(line);
      }
    }

    // Add last section
    if (currentTitle) {
      sections.push({
        title: currentTitle.replace('## ', '').trim(),
        content: currentContent.join('\n').trim(),
      });
    }

    // If no sections found, treat entire content as one entry
    if (sections.length === 0 && content.trim()) {
      sections.push({
        title: 'General Notes',
        content: content.trim(),
      });
    }

    return sections;
  }

  private inferCategory(title: string, content: string): string {
    const lowerTitle = title.toLowerCase();
    const lowerContent = content.toLowerCase();

    if (lowerTitle.includes('人物') || lowerTitle.includes('person') || lowerTitle.includes('owner')) 
      return '人物';
    if (lowerTitle.includes('プロジェクト') || lowerTitle.includes('project')) 
      return 'プロジェクト';
    if (lowerTitle.includes('ワークスペース') || lowerTitle.includes('workspace') || lowerTitle.includes('structure')) 
      return 'ワークスペース';
    if (lowerTitle.includes('未解決') || lowerTitle.includes('backlog') || lowerTitle.includes('issue')) 
      return '未解決課題';
    if (lowerTitle.includes('技術') || lowerTitle.includes('tool') || lowerTitle.includes('tech') || lowerTitle.includes('stack')) 
      return '技術';
    if (lowerTitle.includes('ニュース') || lowerTitle.includes('news')) 
      return 'ニュース';
    
    return 'Other';
  }

  private extractTags(content: string): string[] {
    const tags: string[] = [];
    const tagRegex = /#(\w+)/g;
    let match;
    while ((match = tagRegex.exec(content)) !== null) {
      tags.push(match[1]);
    }
    return tags;
  }

  private generateId(): string {
    return `mem-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  async pushMemoryEntry(entry: MemoryEntry, message: string): Promise<void> {
    const content = this.formatMemoryEntry(entry);
    const path = entry.source === 'MEMORY.md' ? 'MEMORY.md' : `memory/${entry.id}.md`;
    
    // Get current file SHA if it exists
    let sha: string | undefined;
    try {
      const response = await this.octokit.rest.repos.getContent({
        owner: this.config.owner,
        repo: this.config.repo,
        path,
        ref: this.config.branch,
      });
      if ('sha' in response.data) {
        sha = response.data.sha;
      }
    } catch {
      // File doesn't exist
    }

    await this.octokit.rest.repos.createOrUpdateFileContents({
      owner: this.config.owner,
      repo: this.config.repo,
      path,
      message,
      content: Buffer.from(content).toString('base64'),
      branch: this.config.branch,
      sha,
    });
  }

  private formatMemoryEntry(entry: MemoryEntry): string {
    const frontmatter = {
      title: entry.title,
      category: entry.category,
      tags: entry.tags,
      createdAt: entry.createdAt,
      updatedAt: new Date().toISOString(),
    };

    return `---
${Object.entries(frontmatter)
  .map(([key, value]) => `${key}: ${Array.isArray(value) ? `[${value.join(', ')}]` : value}`)
  .join('\n')}
---

${entry.content}
`;
  }

  async deleteMemoryEntry(entry: MemoryEntry, message: string): Promise<void> {
    const path = entry.source === 'MEMORY.md' ? 'MEMORY.md' : `memory/${entry.id}.md`;
    
    try {
      const response = await this.octokit.rest.repos.getContent({
        owner: this.config.owner,
        repo: this.config.repo,
        path,
        ref: this.config.branch,
      });

      if ('sha' in response.data) {
        await this.octokit.rest.repos.deleteFile({
          owner: this.config.owner,
          repo: this.config.repo,
          path,
          message,
          sha: response.data.sha,
          branch: this.config.branch,
        });
      }
    } catch (error) {
      console.warn(`Could not delete ${path}:`, error);
      throw error;
    }
  }
}
