export interface XPost {
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
    impressionCount?: number;
  };
  mediaKeys?: string[];
  mediaUrls?: string[];
  isVideo?: boolean;
  videoUrl?: string;
  referencedTweets?: Array<{
    type: 'retweeted' | 'quoted' | 'replied_to';
    id: string;
  }>;
}

export interface DraftPost {
  id: string;
  originalPostId?: string;
  template: PostTemplate;
  title: string;
  content: string;
  hashtags: string[];
  mediaUrls: string[];
  isVideo: boolean;
  videoUrl?: string;
  status: 'draft' | 'scheduled' | 'posted' | 'archived';
  createdAt: string;
  updatedAt: string;
  postedAt?: string;
  xPostId?: string;
  score?: number;
  keywords?: string[];
}

export interface PostTemplate {
  id: string;
  name: string;
  pattern: string;
  avgLikes: number;
  avgRetweets: number;
  description: string;
  example?: string;
  isActive: boolean;
}

export type TemplateType = 
  | 'conclusion'      // 結論型
  | 'breaking'        // 速報型
  | 'distribution'    // 配布型
  | 'honest'          // 正直型
  | 'viral'           // 海外バズ型
  | 'official';       // 公式型

export interface MonitoredKeyword {
  id: string;
  keyword: string;
  category: 'ai' | 'dev' | 'tool' | 'trend';
  isActive: boolean;
  lastCheckedAt?: string;
  minLikes: number;
}

export interface KeywordSearchResult {
  keyword: string;
  posts: XPost[];
  searchedAt: string;
}

export interface GeneratedDraft {
  id: string;
  title: string;
  content: string;
  template: TemplateType;
  sourcePost?: XPost;
  relevanceScore: number;
  mediaUrls: string[];
  isVideo: boolean;
  createdAt: string;
}

export interface DashboardStats {
  totalDrafts: number;
  postedDrafts: number;
  scheduledDrafts: number;
  avgEngagement: number;
  topTemplate: string;
  recentPosts: DraftPost[];
}

export interface GitHubActionRun {
  id: string;
  name: string;
  status: 'success' | 'failure' | 'in_progress' | 'queued';
  runAt: string;
  logs: string;
}