import { NextRequest, NextResponse } from 'next/server';
import { fetchBookmarkedPosts, searchPostsByKeywords, normalizeVideoUrl } from '@/lib/x-api';
import { selectTemplate, generateDraft } from '@/lib/templates';
import { DraftPost } from '@/types';

const MONITORED_KEYWORDS = [
  'Claude Code', 'Opus', 'Antigravity', 'Gemini CLI', 
  'Codex', 'Cursor', 'Vercel', 'Supabase', 
  'Next.js', 'React', 'Vibe Coding', 'OpenClaw'
];

export async function POST(request: NextRequest) {
  try {
    const { type } = await request.json();
    
    if (type === 'bookmarks') {
      return await generateFromBookmarks();
    } else if (type === 'keywords') {
      return await generateFromKeywords();
    }
    
    return NextResponse.json({ error: 'Invalid generation type' }, { status: 400 });
  } catch (error) {
    console.error('Generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate drafts' }, 
      { status: 500 }
    );
  }
}

async function generateFromBookmarks() {
  const posts = await fetchBookmarkedPosts();
  const drafts: DraftPost[] = [];
  
  for (const post of posts.slice(0, 60)) {
    const template = selectTemplate(post.text, 'bookmark');
    const { content, hashtags } = generateDraft(
      template,
      post,
      post.text.match(/#\w+/g)?.map(t => t.slice(1)) || []
    );
    
    const draftId = `draft_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    drafts.push({
      id: draftId,
      originalPostId: post.id,
      template: template as any,
      title: content.split('\n')[0].substring(0, 50),
      content: content,
      hashtags: hashtags,
      mediaUrls: post.mediaUrls || [],
      isVideo: post.isVideo || false,
      status: 'draft',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });
  }
  
  return NextResponse.json({ 
    success: true, 
    count: drafts.length,
    drafts 
  });
}

async function generateFromKeywords() {
  const results = await searchPostsByKeywords(MONITORED_KEYWORDS, 500, 24);
  const drafts: DraftPost[] = [];
  
  for (const result of results) {
    for (const post of result.posts) {
      const template = selectTemplate(post.text, 'keyword');
      const { content, hashtags } = generateDraft(
        template,
        post,
        [result.keyword]
      );
      
      const draftId = `draft_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      drafts.push({
        id: draftId,
        originalPostId: post.id,
        template: template as any,
        title: `[${result.keyword}] ${content.split('\n')[0].substring(0, 40)}`,
        content: content,
        hashtags: [...hashtags, `#${result.keyword.replace(/\s/g, '')}`],
        mediaUrls: post.mediaUrls || [],
        isVideo: post.isVideo || false,
        status: 'draft',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    }
  }
  
  return NextResponse.json({ 
    success: true, 
    count: drafts.length,
    drafts 
  });
}
