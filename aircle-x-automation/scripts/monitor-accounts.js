const { TwitterApi } = require('twitter-api-v2');
const fs = require('fs');
const path = require('path');

const MONITORED_ACCOUNTS = [
  { username: 'cursor_ai', displayName: 'Cursor' },
  { username: 'vercel', displayName: 'Vercel' },
  { username: 'antigravity', displayName: 'Antigravity' },
  { username: 'AnthropicAI', displayName: 'Anthropic' },
  { username: 'geminicli', displayName: 'Gemini CLI' },
  { username: 'OpenAI', displayName: 'OpenAI' },
];

const DISCORD_WEBHOOK_URL = process.env.DISCORD_WEBHOOK_URL;
const STATE_FILE = path.join(__dirname, '..', '.monitor-state.json');
const DRAFTS_DIR = path.join(__dirname, '..', 'public', 'data');
const DRAFTS_FILE = path.join(DRAFTS_DIR, 'drafts.json');

// Ensure directories exist
function ensureDirectories() {
  if (!fs.existsSync(DRAFTS_DIR)) {
    fs.mkdirSync(DRAFTS_DIR, { recursive: true });
  }
}

// Load last seen tweet IDs
function loadState() {
  if (fs.existsSync(STATE_FILE)) {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  }
  return {};
}

// Save state
function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

// Load existing drafts
function loadDrafts() {
  if (fs.existsSync(DRAFTS_FILE)) {
    return JSON.parse(fs.readFileSync(DRAFTS_FILE, 'utf8'));
  }
  return [];
}

// Save draft
function saveDraft(draft) {
  ensureDirectories();
  const drafts = loadDrafts();
  
  // Check for duplicates
  const isDuplicate = drafts.some(d => 
    d.originalPostId === draft.originalPostId ||
    d.content.substring(0, 100) === draft.content.substring(0, 100)
  );
  
  if (!isDuplicate) {
    drafts.push(draft);
    fs.writeFileSync(DRAFTS_FILE, JSON.stringify(drafts, null, 2));
    return true;
  }
  return false;
}

// Normalize video URL
function normalizeVideoUrl(url) {
  if (!url) return url;
  let normalized = url.split('?')[0];
  normalized = normalized.replace(/\/+$/, '');
  normalized = normalized.replace(/\/video\/?1?$/, '/video/1');
  normalized = normalized.replace(/\/video\/video\//g, '/video/');
  return normalized;
}

// Detect buzz template
function detectBuzzTemplate(text) {
  const lower = text.toLowerCase();
  if (/\b(announc|launch|release|introduc|new|update)\b/.test(lower) &&
      /\b(new feature|available now|today)\b/.test(lower)) return '速報型';
  if (/\b(how to|tutorial|guide|build|create)\b/.test(lower)) return '配布型';
  if (/\b(thought|thinking|honest|opinion)\b/.test(lower)) return '正直型';
  if (/\b(viral|trending|popular|海外|米国)\b/.test(lower)) return '海外バズ型';
  return '結論型';
}

// Generate buzz-worthy Japanese post
function generateBuzzPost(originalText, originalUrl, isVideo, authorName) {
  const template = detectBuzzTemplate(originalText);
  
  // Extract key point (first sentence or first 100 chars)
  const keyPoint = originalText.substring(0, 100).split('\n')[0];
  
  let buzzContent = '';
  let hashtag = '';
  
  switch (template) {
    case '速報型':
      hashtag = '#速報';
      buzzContent = `【速報】${authorName}が発表\n\n${keyPoint}\n\nこれは見逃せない`;
      break;
    case '配布型':
      hashtag = '#配布';
      buzzContent = `🔥 ${authorName}の新機能\n\n${keyPoint}\n\n試す価値あり`;
      break;
    case '正直型':
      hashtag = '#正直';
      buzzContent = `正直、${keyPoint}\n\nこれは革命的`;
      break;
    case '海外バズ型':
      hashtag = '#海外トレンド';
      buzzContent = `【海外で話題】${keyPoint}\n\n日本でも広まる予感`;
      break;
    default:
      hashtag = '#結論';
      buzzContent = `【結論】${keyPoint}\n\nこれは覚えておくべき`;
  }
  
  // Add hashtags
  buzzContent += `\n\n${hashtag} #AI #開発 #エンジニア #AirCle`;
  
  // For videos, prepend the normalized URL at the beginning
  if (isVideo) {
    const normalizedUrl = normalizeVideoUrl(originalUrl);
    buzzContent = `${normalizedUrl}\n\n${buzzContent}`;
  } else {
    buzzContent += `\n\n${originalUrl}`;
  }
  
  return { buzzContent, template };
}

// Send Discord notification using Node.js native https
async function sendDiscordNotification(account, post, buzzContent, template) {
  if (!DISCORD_WEBHOOK_URL) {
    console.log('Discord webhook not configured, skipping notification');
    return;
  }

  const embed = {
    title: `🔔 ${account.displayName} の新規投稿`,
    description: buzzContent.substring(0, 4096),
    color: 0x1d9bf0,
    fields: [
      { name: '型', value: template, inline: true },
      { name: '動画', value: post.isVideo ? '✅ はい' : '❌ いいえ', inline: true },
      { name: 'いいね', value: post.publicMetrics.likeCount.toString(), inline: true },
      { name: '元投稿', value: post.originalUrl },
    ],
    timestamp: new Date().toISOString(),
    footer: { text: 'AirCle X Monitor' },
  };

  const payload = {
    content: `📢 **${account.displayName}** が投稿しました！\n元URL: ${post.originalUrl}\n\nこれ投稿しとこうか？ 👇`,
    embeds: [embed],
    components: [
      {
        type: 1,
        components: [
          {
            type: 2,
            label: '✅ 投稿する',
            style: 3,
            custom_id: `post_${account.username}_${Date.now()}`,
          },
          {
            type: 2,
            label: '❌ スキップ',
            style: 4,
            custom_id: `skip_${account.username}_${Date.now()}`,
          },
          {
            type: 2,
            label: '📋 コピー',
            style: 2,
            custom_id: `copy_${account.username}_${Date.now()}`,
          },
        ],
      },
    ],
    username: 'AirCle X Monitor',
    avatar_url: 'https://pbs.twimg.com/profile_images/1729618006259572736/Hb8dpjJt_400x400.jpg',
  };

  const url = new URL(DISCORD_WEBHOOK_URL);
  const https = require('https');
  
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname: url.hostname,
        path: url.pathname + url.search,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            console.log(`✅ Notification sent for ${account.username}`);
            resolve(data);
          } else {
            reject(new Error(`Discord API error: ${res.statusCode} - ${data}`));
          }
        });
      }
    );
    
    req.on('error', reject);
    req.write(JSON.stringify(payload));
    req.end();
  });
}

// Main monitoring function
async function monitorAccounts() {
  const bearerToken = process.env.X_BEARER_TOKEN;
  if (!bearerToken) {
    console.error('❌ X_BEARER_TOKEN not set');
    process.exit(1);
  }

  const client = new TwitterApi(bearerToken);
  const state = loadState();
  let newPostsFound = 0;
  let draftsSaved = 0;

  console.log('🔍 Starting account monitoring...\n');

  for (const account of MONITORED_ACCOUNTS) {
    try {
      console.log(`👀 Monitoring @${account.username}...`);

      const user = await client.v2.userByUsername(account.username);
      if (!user.data) {
        console.log(`   ⚠️ User not found: ${account.username}`);
        continue;
      }

      const tweets = await client.v2.userTimeline(user.data.id, {
        expansions: ['attachments.media_keys', 'author_id'],
        'tweet.fields': ['created_at', 'public_metrics'],
        'media.fields': ['url', 'preview_image_url', 'type', 'variants'],
        max_results: 5,
        since_id: state[account.username],
      });
      
      // Reverse to process oldest first
      const tweetsToProcess = [...tweets.tweets].reverse();

      for (const tweet of tweetsToProcess) {
        // Skip retweets and replies
        if (tweet.referenced_tweets?.some(ref =>
          ref.type === 'retweeted' || ref.type === 'replied_to'
        )) {
          console.log(`   ⏭️ Skipping RT/reply: ${tweet.id}`);
          continue;
        }

        // Get media from includes
        const tweetMedia = tweets.includes?.media || [];
        const mediaKeys = tweet.attachments?.media_keys || [];
        const media = tweetMedia.filter(m => mediaKeys.includes(m.media_key));
        const videoMedia = media.find(m => m.type === 'video');
        const isVideo = !!videoMedia;

        const post = {
          id: tweet.id,
          text: tweet.text,
          author: { name: user.data.name, username: user.data.username },
          createdAt: tweet.created_at,
          publicMetrics: {
            likeCount: tweet.public_metrics?.like_count || 0,
            retweetCount: tweet.public_metrics?.retweet_count || 0,
            replyCount: tweet.public_metrics?.reply_count || 0,
          },
          mediaUrls: media.map(m => m.url || m.preview_image_url).filter(Boolean),
          isVideo,
          videoUrl: videoMedia?.variants?.[0]?.url,
          originalUrl: `https://x.com/${account.username}/status/${tweet.id}`,
        };

        // Generate buzz content
        const { buzzContent, template } = generateBuzzPost(
          post.text,
          post.originalUrl,
          post.isVideo,
          account.displayName
        );

        // Create draft
        const draft = {
          id: `draft_monitor_${Date.now()}_${post.id}`,
          originalPostId: post.id,
          template: { id: template, name: template, pattern: '', avgLikes: 0, avgRetweets: 0, description: '', isActive: true },
          title: `${account.displayName} - ${template}`,
          content: buzzContent,
          hashtags: hashtagMatch(buzzContent),
          mediaUrls: post.mediaUrls,
          isVideo: post.isVideo,
          videoUrl: post.videoUrl,
          status: 'draft',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          score: post.publicMetrics.likeCount,
          keywords: [account.username],
        };

        // Save draft
        if (saveDraft(draft)) {
          draftsSaved++;
          console.log(`   💾 Draft saved`);
        }

        // Send to Discord
        try {
          await sendDiscordNotification(account, post, buzzContent, template);
          newPostsFound++;
          console.log(`   📨 Discord notified`);
        } catch (discordError) {
          console.error(`   ❌ Discord error: ${discordError.message}`);
        }

        console.log(`   ✅ New post: ${post.id.substring(0, 20)}... (${template})`);
      }

      // Update last seen tweet ID
      if (tweets.tweets.length > 0) {
        state[account.username] = tweets.tweets[0].id;
        console.log(`   📝 Updated last seen ID`);
      } else {
        console.log(`   ℹ️ No new tweets`);
      }

    } catch (error) {
      console.error(`   ❌ Error monitoring @${account.username}:`, error.message);
    }
    
    console.log('');
  }

  // Save state
  saveState(state);
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`📊 Monitoring complete`);
  console.log(`   • New posts found: ${newPostsFound}`);
  console.log(`   • Drafts saved: ${draftsSaved}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
}

// Extract hashtags from content
function hashtagMatch(content) {
  const matches = content.match(/#\w+/g);
  return matches || [];
}

// Run monitoring
monitorAccounts().catch(error => {
  console.error('❌ Monitoring failed:', error);
  process.exit(1);
});
