import { TwitterApi } from 'twitter-api-v2';
import { XPost, DraftPost, PostTemplate, MonitoredKeyword, KeywordSearchResult, TemplateType } from '@/types';

// X API Client
let client: TwitterApi | null = null;
let bearerClient: TwitterApi | null = null;

export function initXApi() {
  if (!client) {
    client = new TwitterApi({
      appKey: process.env.X_API_KEY || '',
      appSecret: process.env.X_API_SECRET || '',
      accessToken: process.env.X_ACCESS_TOKEN || '',
      accessSecret: process.env.X_ACCESS_SECRET || '',
    });
  }
  if (!bearerClient) {
    bearerClient = new TwitterApi(process.env.X_BEARER_TOKEN || '');
  }
  return { client, bearerClient };
}

// Fetch bookmarked posts using X API v2
// Note: Requires OAuth 2.0 authentication for the authenticated user
export async function fetchBookmarkedPosts(): Promise<XPost[]> {
  try {
    const { client } = initXApi();
    if (!client) throw new Error('X API not initialized with user authentication');

    // User context is required for bookmarks
    const bookmarks = await client.v2.bookmarks({
      expansions: ['attachments.media_keys', 'author_id', 'referenced_tweets.id'],
      'tweet.fields': ['created_at', 'public_metrics', 'entities'],
      'user.fields': ['username', 'profile_image_url', 'name'],
      'media.fields': ['url', 'preview_image_url', 'type', 'variants'],
      max_results: 100,
    });

    return bookmarks.tweets.map((tweet: any) => ({
      id: tweet.id,
      text: tweet.text,
      author: {
        name: tweet.author?.name || '',
        username: tweet.author?.username || '',
        profileImageUrl: tweet.author?.profile_image_url,
      },
      createdAt: tweet.created_at,
      publicMetrics: {
        likeCount: tweet.public_metrics?.like_count || 0,
        retweetCount: tweet.public_metrics?.retweet_count || 0,
        replyCount: tweet.public_metrics?.reply_count || 0,
        impressionCount: tweet.public_metrics?.impression_count || 0,
      },
      mediaKeys: tweet.attachments?.media_keys,
      mediaUrls: tweet.media?.map((m: any) => m.url || m.preview_image_url),
      isVideo: tweet.media?.some((m: any) => m.type === 'video'),
      videoUrl: tweet.media?.find((m: any) => m.type === 'video')?.variants?.[0]?.url,
      referencedTweets: tweet.referenced_tweets,
    }));
  } catch (error) {
    console.error('Error fetching bookmarks:', error);
    return [];
  }
}

// Search posts by keywords
export async function searchPostsByKeywords(
  keywords: string[],
  minLikes: number = 500,
  hoursAgo: number = 24
): Promise<KeywordSearchResult[]> {
  try {
    const { bearerClient } = initXApi();
    if (!bearerClient) throw new Error('X API not initialized');

    const sinceDate = new Date();
    sinceDate.setHours(sinceDate.getHours() - hoursAgo);
    const since = sinceDate.toISOString().split('T')[0];

    const results: KeywordSearchResult[] = [];

    for (const keyword of keywords) {
      const search = await bearerClient.v2.search(keyword, {
        expansions: ['attachments.media_keys', 'author_id', 'referenced_tweets.id'],
        'tweet.fields': ['created_at', 'public_metrics', 'entities', 'context_annotations'],
        'user.fields': ['username', 'profile_image_url', 'name'],
        'media.fields': ['url', 'preview_image_url', 'type', 'variants'],
        start_time: since,
        max_results: 50,
      });

      const posts: XPost[] = search.tweets
        .filter((tweet: any) => (tweet.public_metrics?.like_count || 0) >= minLikes)
        .map((tweet: any) => {
          // Get media from includes
          const searchMedia = search.includes?.media || [];
          const mediaKeys = tweet.attachments?.media_keys || [];
          const media = searchMedia.filter((m: any) => mediaKeys.includes(m.media_key));
          const videoMedia = media.find((m: any) => m.type === 'video');
          
          return {
            id: tweet.id,
            text: tweet.text,
            author: {
              name: tweet.author?.name || '',
              username: tweet.author?.username || '',
              profileImageUrl: tweet.author?.profile_image_url,
            },
            createdAt: tweet.created_at,
            publicMetrics: {
              likeCount: tweet.public_metrics?.like_count || 0,
              retweetCount: tweet.public_metrics?.retweet_count || 0,
              replyCount: tweet.public_metrics?.reply_count || 0,
            },
            mediaKeys: tweet.attachments?.media_keys,
            mediaUrls: media.map((m: any) => m.url || m.preview_image_url),
            isVideo: !!videoMedia,
            videoUrl: videoMedia?.variants?.[0]?.url,
            referencedTweets: tweet.referenced_tweets,
          };
        });

      results.push({
        keyword,
        posts,
        searchedAt: new Date().toISOString(),
      });
    }

    return results;
  } catch (error) {
    console.error('Error searching posts:', error);
    return [];
  }
}

// Fetch user timeline (for monitoring)
export async function fetchUserTimeline(
  username: string,
  sinceId?: string
): Promise<XPost[]> {
  try {
    const { bearerClient } = initXApi();
    if (!bearerClient) throw new Error('X API not initialized');

    const user = await bearerClient.v2.userByUsername(username);
    if (!user.data) return [];

    const tweets = await bearerClient.v2.userTimeline(user.data.id, {
      expansions: ['attachments.media_keys', 'author_id', 'referenced_tweets.id'],
      'tweet.fields': ['created_at', 'public_metrics', 'entities'],
      'media.fields': ['url', 'preview_image_url', 'type', 'variants'],
      since_id: sinceId,
      max_results: 20,
    });

    return tweets.tweets
      .filter((tweet: any) => !tweet.referenced_tweets) // Exclude RTs
      .map((tweet: any) => {
        // Get media from includes
        const timelineMedia = tweets.includes?.media || [];
        const mediaKeys = tweet.attachments?.media_keys || [];
        const media = timelineMedia.filter((m: any) => mediaKeys.includes(m.media_key));
        const videoMedia = media.find((m: any) => m.type === 'video');
        
        return {
          id: tweet.id,
          text: tweet.text,
          author: {
            name: user.data.name,
            username: user.data.username,
            profileImageUrl: user.data.profile_image_url,
          },
          createdAt: tweet.created_at,
          publicMetrics: {
            likeCount: tweet.public_metrics?.like_count || 0,
            retweetCount: tweet.public_metrics?.retweet_count || 0,
            replyCount: tweet.public_metrics?.reply_count || 0,
          },
          mediaKeys: tweet.attachments?.media_keys,
          mediaUrls: media.map((m: any) => m.url || m.preview_image_url),
          isVideo: !!videoMedia,
          videoUrl: videoMedia?.variants?.[0]?.url,
        };
      });
  } catch (error) {
    console.error(`Error fetching timeline for ${username}:`, error);
    return [];
  }
}

// Normalize video URL
export function normalizeVideoUrl(url: string): string {
  // Remove query parameters
  let normalized = url.split('?')[0];
  // Remove trailing slash
  normalized = normalized.replace(/\/$/, '');
  // Convert /video1 or /video/1 to /video/1
  normalized = normalized.replace(/\/video\/?1?$/, '/video/1');
  // Remove double video paths
  normalized = normalized.replace(/\/video\/video\//g, '/video/');
  return normalized;
}

// Create draft post
export async function createDraftPost(content: string, mediaUrls: string[] = []): Promise<{ id: string }> {
  try {
    const { client } = initXApi();
    if (!client) throw new Error('X API not initialized');

    const limitedMedia = mediaUrls.slice(0, 4);
    const result = await client.v2.tweet(content, {
      media: limitedMedia.length > 0 ? { 
        media_ids: limitedMedia as [string] | [string, string] | [string, string, string] | [string, string, string, string]
      } : undefined,
    });

    return { id: result.data.id };
  } catch (error) {
    console.error('Error creating draft:', error);
    throw error;
  }
}

// Post to X
export async function postToX(
  content: string,
  mediaUrls: string[] = [],
  replyToId?: string
): Promise<{ id: string; url: string }> {
  try {
    const { client } = initXApi();
    if (!client) throw new Error('X API not initialized');

    const limitedMedia = mediaUrls.slice(0, 4);
    const result = await client.v2.tweet(content, {
      media: limitedMedia.length > 0 ? { 
        media_ids: limitedMedia as [string] | [string, string] | [string, string, string] | [string, string, string, string]
      } : undefined,
      reply: replyToId ? { in_reply_to_tweet_id: replyToId } : undefined,
    });

    return {
      id: result.data.id,
      url: `https://x.com/i/web/status/${result.data.id}`,
    };
  } catch (error) {
    console.error('Error posting to X:', error);
    throw error;
  }
}