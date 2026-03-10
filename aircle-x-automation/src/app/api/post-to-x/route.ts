import { NextRequest, NextResponse } from 'next/server';
import { TwitterApi } from 'twitter-api-v2';
import fs from 'fs';
import path from 'path';
import { DraftPost } from '@/types';

const DATA_DIR = path.join(process.cwd(), 'public', 'data');
const DRAFTS_FILE = path.join(DATA_DIR, 'drafts.json');

// Load drafts
function loadDrafts(): DraftPost[] {
  if (fs.existsSync(DRAFTS_FILE)) {
    const data = fs.readFileSync(DRAFTS_FILE, 'utf-8');
    return JSON.parse(data);
  }
  return [];
}

// Update draft status
function updateDraftStatus(draftId: string, status: string, xPostId?: string): boolean {
  const drafts = loadDrafts();
  const draftIndex = drafts.findIndex(d => d.id === draftId);
  
  if (draftIndex === -1) return false;
  
  drafts[draftIndex].status = status as 'draft' | 'scheduled' | 'posted' | 'archived';
  drafts[draftIndex].updatedAt = new Date().toISOString();
  
  if (status === 'posted') {
    drafts[draftIndex].postedAt = new Date().toISOString();
  }
  
  if (xPostId) {
    drafts[draftIndex].xPostId = xPostId;
  }
  
  fs.writeFileSync(DRAFTS_FILE, JSON.stringify(drafts, null, 2));
  return true;
}

// Initialize X API client
function initXApi() {
  const client = new TwitterApi({
    appKey: process.env.X_API_KEY || '',
    appSecret: process.env.X_API_SECRET || '',
    accessToken: process.env.X_ACCESS_TOKEN || '',
    accessSecret: process.env.X_ACCESS_SECRET || '',
  });
  return client;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      draftId, 
      content, 
      mediaUrls = [], 
      action = 'draft' // 'draft', 'post', 'schedule'
    } = body;

    if (!content) {
      return NextResponse.json(
        { error: 'Content is required' },
        { status: 400 }
      );
    }

    // Since X API doesn't support creating drafts through the public API,
    // we return the formatted content for manual posting
    if (action === 'draft' || action === 'prepare') {
      // Format content for X
      const formattedContent = formatContentForX(content, mediaUrls);
      
      // Update draft status if draftId provided
      if (draftId) {
        updateDraftStatus(draftId, 'draft');
      }
      
      return NextResponse.json({
        success: true,
        action: 'prepare',
        message: '投稿内容を準備しました。Xで貼り付けて投稿してください。',
        data: {
          content: formattedContent,
          characterCount: formattedContent.length,
          xComposeUrl: `https://x.com/compose/post?text=${encodeURIComponent(formattedContent)}`,
        }
      });
    }

    // For direct posting (requires write permissions)
    if (action === 'post') {
      try {
        const client = initXApi();
        
        // Upload media if URLs provided
        const mediaIds: string[] = [];
        if (mediaUrls.length > 0) {
          for (const mediaUrl of mediaUrls.slice(0, 4)) { // Max 4 media
            try {
              // Download and upload media
              const response = await fetch(mediaUrl);
              const buffer = Buffer.from(await response.arrayBuffer());
              const mimeType = response.headers.get('content-type') || 'image/jpeg';
              
              const mediaId = await client.v1.uploadMedia(buffer, { mimeType });
              mediaIds.push(mediaId);
            } catch (mediaError) {
              console.error('Failed to upload media:', mediaError);
            }
          }
        }
        
        // Post tweet
        const tweet = await client.v2.tweet(content, {
          media: mediaIds.length > 0 ? { media_ids: mediaIds as [string] } : undefined,
        });
        
        // Update draft status
        if (draftId) {
          updateDraftStatus(draftId, 'posted', tweet.data.id);
        }
        
        return NextResponse.json({
          success: true,
          action: 'posted',
          data: {
            id: tweet.data.id,
            url: `https://x.com/i/web/status/${tweet.data.id}`,
            text: tweet.data.text,
          }
        });
        
      } catch (postError) {
        console.error('Failed to post:', postError);
        return NextResponse.json(
          { 
            error: 'Failed to post to X',
            details: (postError as Error).message,
            fallback: {
              content: formatContentForX(content, mediaUrls),
              xComposeUrl: `https://x.com/compose/post?text=${encodeURIComponent(formatContentForX(content, mediaUrls))}`,
            }
          },
          { status: 500 }
        );
      }
    }

    // Schedule post (would require a job queue in production)
    if (action === 'schedule') {
      const { scheduledAt } = body;
      
      if (!scheduledAt) {
        return NextResponse.json(
          { error: 'scheduledAt is required for scheduling' },
          { status: 400 }
        );
      }
      
      // Update draft status
      if (draftId) {
        updateDraftStatus(draftId, 'scheduled');
      }
      
      // In production, this would add to a job queue
      return NextResponse.json({
        success: true,
        action: 'scheduled',
        message: `投稿を予約しました: ${scheduledAt}`,
        data: {
          draftId,
          scheduledAt,
          content: formatContentForX(content, mediaUrls),
        }
      });
    }

    return NextResponse.json(
      { error: 'Invalid action' },
      { status: 400 }
    );
    
  } catch (error) {
    console.error('Post to X error:', error);
    return NextResponse.json(
      { error: 'Failed to process request', details: (error as Error).message },
      { status: 500 }
    );
  }
}

// GET: Get posting stats
export async function GET() {
  try {
    const drafts = loadDrafts();
    const posted = drafts.filter(d => d.status === 'posted').length;
    const scheduled = drafts.filter(d => d.status === 'scheduled').length;
    const draft = drafts.filter(d => d.status === 'draft').length;
    
    return NextResponse.json({
      success: true,
      stats: {
        total: drafts.length,
        posted,
        scheduled,
        draft,
      }
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to get stats' },
      { status: 500 }
    );
  }
}

// Helper: Format content for X
function formatContentForX(content: string, mediaUrls: string[] = []): string {
  let formatted = content;
  
  // Ensure line breaks are preserved
  formatted = formatted.replace(/\\n/g, '\n');
  
  // Remove excess whitespace
  formatted = formatted.replace(/\n{3,}/g, '\n\n');
  
  // Ensure content is within X's character limit
  if (formatted.length > 280) {
    // X allows longer tweets now, but we warn if it exceeds traditional limit
    console.warn(`Content is ${formatted.length} characters (limit: 280 for basic tweets, 4000 for X Premium)`);
  }
  
  return formatted.trim();
}

// PUT: Update draft status
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { draftId, status, xPostId } = body;
    
    if (!draftId || !status) {
      return NextResponse.json(
        { error: 'draftId and status are required' },
        { status: 400 }
      );
    }
    
    const success = updateDraftStatus(draftId, status, xPostId);
    
    if (!success) {
      return NextResponse.json(
        { error: 'Draft not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json({
      success: true,
      message: `Draft status updated to ${status}`,
    });
    
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to update draft' },
      { status: 500 }
    );
  }
}
