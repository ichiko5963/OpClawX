import { TwitterApi } from 'twitter-api-v2';

export interface MonitoredAccountConfig {
  username: string;
  displayName: string;
  priority: 'high' | 'medium' | 'low';
  keywords?: string[];
}

export interface MonitoredPost {
  id: string;
  text: string;
  author: {
    name: string;
    username: string;
    profileImageUrl?: string;
  };
  createdAt: string;
  publicMetrics: {
    likeCount: number;
    retweetCount: number;
    replyCount: number;
  };
  mediaUrls: string[];
  isVideo: boolean;
  videoUrl?: string;
  originalUrl: string;
}

export interface MonitoringAlert {
  id: string;
  accountUsername: string;
  post: MonitoredPost;
  translatedText: string;
  generatedDraft: string;
  buzzTemplate: string;
  timestamp: string;
  status: 'pending' | 'approved' | 'rejected';
}

export const MONITORED_ACCOUNTS: MonitoredAccountConfig[] = [
  { username: 'cursor_ai', displayName: 'Cursor', priority: 'high', keywords: ['VS Code', 'AI', 'Editor'] },
  { username: 'vercel', displayName: 'Vercel', priority: 'high', keywords: ['Next.js', 'Deploy'] },
  { username: 'antigravity', displayName: 'Antigravity', priority: 'high' },
  { username: 'AnthropicAI', displayName: 'Anthropic', priority: 'high', keywords: ['Claude', 'Claude Code'] },
  { username: 'geminicli', displayName: 'Gemini CLI', priority: 'medium' },
  { username: 'OpenAI', displayName: 'OpenAI', priority: 'high', keywords: ['GPT', 'API'] },
];

// Fetch new posts from monitored accounts
export async function fetchNewPosts(
  bearerToken: string,
  sinceIds: Record<string, string> = {}
): Promise<MonitoredPost[]> {
  const client = new TwitterApi(bearerToken);
  const newPosts: MonitoredPost[] = [];

  for (const account of MONITORED_ACCOUNTS) {
    try {
      const user = await client.v2.userByUsername(account.username);
      if (!user.data) continue;

      const tweets = await client.v2.userTimeline(user.data.id, {
        expansions: ['attachments.media_keys', 'author_id'],
        'tweet.fields': ['created_at', 'public_metrics', 'entities'],
        'media.fields': ['url', 'preview_image_url', 'type', 'variants'],
        max_results: 5,
        since_id: sinceIds[account.username],
      });

      for (const tweet of tweets.tweets) {
        // Skip retweets and replies
        if (tweet.referenced_tweets?.some(ref => 
          ref.type === 'retweeted' || ref.type === 'replied_to'
        )) {
          continue;
        }

        // Get media from includes
        const tweetMedia = tweets.includes?.media || [];
        const mediaKeys = tweet.attachments?.media_keys || [];
        const media = tweetMedia.filter((m: any) => mediaKeys.includes(m.media_key));
        const videoMedia = media.find((m: any) => m.type === 'video');

        newPosts.push({
          id: tweet.id,
          text: tweet.text,
          author: {
            name: user.data.name,
            username: user.data.username,
            profileImageUrl: user.data.profile_image_url,
          },
          createdAt: tweet.created_at || new Date().toISOString(),
          publicMetrics: {
            likeCount: tweet.public_metrics?.like_count || 0,
            retweetCount: tweet.public_metrics?.retweet_count || 0,
            replyCount: tweet.public_metrics?.reply_count || 0,
          },
          mediaUrls: media.map((m: any) => m.url || m.preview_image_url).filter((url: string | undefined): url is string => !!url),
          isVideo: !!videoMedia,
          videoUrl: videoMedia?.variants?.[0]?.url,
          originalUrl: `https://x.com/${account.username}/status/${tweet.id}`,
        });
      }
    } catch (error) {
      console.error(`Error fetching posts for ${account.username}:`, error);
    }
  }

  return newPosts;
}

// Normalize video URL for X post
export function normalizeVideoUrl(url: string): string {
  // Remove query parameters
  let normalized = url.split('?')[0];
  // Remove trailing slash
  normalized = normalized.replace(/\/$/, '');
  // Convert /video1 to /video/1
  normalized = normalized.replace(/\/video\/?1?$/, '/video/1');
  // Remove double video paths
  normalized = normalized.replace(/\/video\/video\//g, '/video/');
  // Ensure proper format
  if (!normalized.includes('/video/')) {
    normalized = normalized.replace(/\/video$/, '/video/1');
  }
  return normalized;
}

// Detect buzz template based on content
export function detectBuzzTemplate(text: string): string {
  const lower = text.toLowerCase();
  
  if (/\b(announc|launch|release|introduc|new|update)\b/.test(lower) && 
      /\b(new feature|available now|today)\b/.test(lower)) {
    return 'breaking';
  }
  if (/\b(how to|tutorial|guide|build|create)\b/.test(lower)) {
    return 'distribution';
  }
  if (/\b(thought|thinking|honest|opinion)\b/.test(lower)) {
    return 'honest';
  }
  if (/\b(viral|trending|popular|海外|米国)\b/.test(lower)) {
    return 'viral';
  }
  
  return 'conclusion'; // Default strongest template
}

// Translate text (simplified version - would use actual translation API)
export function translateToJapanese(text: string): string {
  // In production, this would call Google Translate API or similar
  // For now, return placeholder text indicating it's a translation
  return text; // Placeholder
}

// Generate buzz-worthy Japanese post
export function generateBuzzPost(
  originalText: string,
  originalUrl: string,
  isVideo: boolean,
  authorName: string
): string {
  const template = detectBuzzTemplate(originalText);
  const translated = translateToJapanese(originalText);
  
  // Extract key point (first sentence or first 100 chars)
  const keyPoint = translated.split('.')[0].substring(0, 100);
  
  let buzzContent = '';
  
  switch (template) {
    case 'breaking':
      buzzContent = `【速報】${authorName}が発表\n\n${keyPoint}\n\nこれは見逃せない`;
      break;
    case 'distribution':
      buzzContent = `🔥 ${authorName}の新機能\n\n${keyPoint}\n\n試す価値あり`;
      break;
    case 'honest':
      buzzContent = `正直、${keyPoint}\n\nこれは革命的`;
      break;
    case 'viral':
      buzzContent = `【海外で話題】${keyPoint}\n\n日本でも広まる予感`;
      break;
    default:
      buzzContent = `【結論】${keyPoint}\n\nこれは覚えておくべき`;
  }
  
  // Add hashtags
  buzzContent += '\n\n#AI #開発 #エンジニア #AirCle';
  
  // For videos, prepend the normalized URL at the beginning
  if (isVideo) {
    const normalizedUrl = normalizeVideoUrl(originalUrl);
    buzzContent = `${normalizedUrl}\n\n${buzzContent}`;
  } else {
    buzzContent += `\n\n${originalUrl}`;
  }
  
  return buzzContent;
}
