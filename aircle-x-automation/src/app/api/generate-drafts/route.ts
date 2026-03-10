import { NextRequest, NextResponse } from 'next/server';
import { fetchBookmarkedPosts, searchPostsByKeywords } from '@/lib/x-api';
import { selectTemplate, generateDraft } from '@/lib/templates';
import { DraftPost, XPost } from '@/types';
import fs from 'fs';
import path from 'path';

const MONITORED_KEYWORDS = [
  'Claude Code', 'Opus', 'Antigravity', 'Gemini CLI', 
  'Codex', 'Cursor', 'Vercel', 'Supabase', 
  'Next.js', 'React', 'Vibe Coding', 'OpenClaw'
];

// Path to store drafts
const DATA_DIR = path.join(process.cwd(), 'public', 'data');
const DRAFTS_FILE = path.join(DATA_DIR, 'drafts.json');

// Ensure data directory exists
function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

// Load existing drafts
function loadDrafts(): DraftPost[] {
  ensureDataDir();
  if (fs.existsSync(DRAFTS_FILE)) {
    const data = fs.readFileSync(DRAFTS_FILE, 'utf-8');
    return JSON.parse(data);
  }
  return [];
}

// Save drafts
function saveDrafts(drafts: DraftPost[]) {
  ensureDataDir();
  fs.writeFileSync(DRAFTS_FILE, JSON.stringify(drafts, null, 2));
}

// Check if draft already exists
function isDuplicate(drafts: DraftPost[], originalPostId?: string, content?: string): boolean {
  if (!originalPostId && !content) return false;
  
  return drafts.some(draft => {
    // Check by original post ID
    if (originalPostId && draft.originalPostId === originalPostId) {
      return true;
    }
    // Check by content similarity (first 100 chars)
    if (content && draft.content) {
      const contentSnippet = content.substring(0, 100);
      const draftSnippet = draft.content.substring(0, 100);
      return contentSnippet === draftSnippet;
    }
    return false;
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { type, limit = 60, minLikes = 500 } = body;
    
    if (!type || !['bookmarks', 'keywords'].includes(type)) {
      return NextResponse.json(
        { error: 'Invalid generation type. Use "bookmarks" or "keywords"' }, 
        { status: 400 }
      );
    }
    
    // Load existing drafts
    const existingDrafts = loadDrafts();
    const newDrafts: DraftPost[] = [];

    if (type === 'bookmarks') {
      console.log('Generating drafts from bookmarks...');
      const posts = await fetchBookmarkedPosts();
      
      for (const post of posts.slice(0, limit)) {
        // Skip duplicates
        if (isDuplicate(existingDrafts, post.id)) {
          console.log(`Skipping duplicate: ${post.id}`);
          continue;
        }
        
        const template = selectTemplate(post.text, 'bookmark');
        const { content, hashtags } = generateDraft(
          template,
          {
            text: post.text,
            author: post.author,
            mediaUrls: post.mediaUrls,
            isVideo: post.isVideo,
            videoUrl: post.videoUrl,
          },
          post.text.match(/#\w+/g)?.map(t => t.slice(1)) || []
        );
        
        // Skip if content is too similar
        if (isDuplicate(existingDrafts, undefined, content)) {
          continue;
        }
        
        const draftId = `draft_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const now = new Date().toISOString();
        
        const draft: DraftPost = {
          id: draftId,
          originalPostId: post.id,
          template: { id: template, name: '', pattern: '', avgLikes: 0, avgRetweets: 0, description: '', isActive: true },
          title: content.split('\n')[0].substring(0, 50),
          content: content,
          hashtags: hashtags,
          mediaUrls: post.mediaUrls || [],
          isVideo: post.isVideo || false,
          videoUrl: post.videoUrl,
          status: 'draft',
          createdAt: now,
          updatedAt: now,
          score: post.publicMetrics?.likeCount || 0,
          keywords: [],
        };
        
        newDrafts.push(draft);
        existingDrafts.push(draft);
      }
      
      console.log(`Generated ${newDrafts.length} drafts from bookmarks`);
      
    } else if (type === 'keywords') {
      console.log('Generating drafts from keywords...');
      const results = await searchPostsByKeywords(MONITORED_KEYWORDS, minLikes, 24);
      
      for (const result of results) {
        for (const post of result.posts) {
          // Skip duplicates
          if (isDuplicate(existingDrafts, post.id)) {
            console.log(`Skipping duplicate: ${post.id}`);
            continue;
          }
          
          const template = selectTemplate(post.text, 'keyword');
          const { content, hashtags } = generateDraft(
            template,
            {
              text: post.text,
              author: post.author,
              mediaUrls: post.mediaUrls,
              isVideo: post.isVideo,
              videoUrl: post.videoUrl,
            },
            [result.keyword]
          );
          
          // Skip if content is too similar
          if (isDuplicate(existingDrafts, undefined, content)) {
            continue;
          }
          
          const draftId = `draft_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          const now = new Date().toISOString();
          
          const draft: DraftPost = {
            id: draftId,
            originalPostId: post.id,
            template: { id: template, name: '', pattern: '', avgLikes: 0, avgRetweets: 0, description: '', isActive: true },
            title: `[${result.keyword}] ${content.split('\n')[0].substring(0, 40)}`,
            content: content,
            hashtags: [...hashtags, `#${result.keyword.replace(/\s/g, '')}`],
            mediaUrls: post.mediaUrls || [],
            isVideo: post.isVideo || false,
            videoUrl: post.videoUrl,
            status: 'draft',
            createdAt: now,
            updatedAt: now,
            score: post.publicMetrics?.likeCount,
            keywords: [result.keyword],
          };
          
          newDrafts.push(draft);
          existingDrafts.push(draft);
        }
      }
      
      console.log(`Generated ${newDrafts.length} drafts from keywords`);
    }
    
    // Save all drafts
    saveDrafts(existingDrafts);
    
    return NextResponse.json({ 
      success: true, 
      count: newDrafts.length,
      total: existingDrafts.length,
      drafts: newDrafts,
    });
    
  } catch (error) {
    console.error('Generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate drafts', details: (error as Error).message }, 
      { status: 500 }
    );
  }
}

// GET: List all drafts
export async function GET() {
  try {
    const drafts = loadDrafts();
    return NextResponse.json({
      success: true,
      count: drafts.length,
      drafts: drafts.sort((a, b) => 
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      ),
    });
  } catch (error) {
    console.error('Failed to load drafts:', error);
    return NextResponse.json(
      { error: 'Failed to load drafts' },
      { status: 500 }
    );
  }
}
