#!/usr/bin/env node
/**
 * Daily 15-Post Generator — AI-Powered with OpenClaw Memory Integration
 * 
 * Features:
 * - Analyzes user's OpenClaw memory for writing style and experiences
 * - Uses X Premium data if available
 * - Generates 15 posts using AI (Claude/OpenAI) with memory context
 * - First-hand experiences are incorporated into posts
 * - Saves to JSON and delivers via URL
 * 
 * Schedule: 7AM, 12PM, 6PM (3x daily)
 */

const fs   = require('fs');
const path = require('path');
const https = require('https');

// Core modules
const { analyzeUserFromMemory, generateMemoryContext } = require('../core/memory-analyzer');
const { generateDaily15: generateAI15 } = require('../core/ai-generator');
const { generatePost } = require('../core/generator'); // Fallback

const OUTPUT_DIR = path.join(__dirname, '../web/daily');
const LOG_PATH   = path.join(__dirname, '../logs/daily-15.jsonl');

// ─── Configuration ──────────────────────────────────────────────────────────

const CONFIG = {
  // AI Model preference
  aiModel: process.env.VPA_AI_MODEL || 'claude', // 'claude' or 'openai'
  
  // Whether to use memory analysis
  useMemory: process.env.VPA_USE_MEMORY !== 'false',
  
  // Whether to use X Premium data
  useXPremium: !!process.env.XPREMIUM_DATA_PATH,
  
  // News fetch (optional)
  fetchNews: process.env.VPA_FETCH_NEWS !== 'false',
  
  // Delivery
  webhookUrl: process.env.VPA_WEBHOOK_URL,
  baseUrl: process.env.VPA_BASE_URL || 'https://opclawx.vercel.app'
};

// ─── News Fetcher (Optional Enhancement) ─────────────────────────────────────

async function fetchNewsTopics(lang = 'ja') {
  if (!CONFIG.fetchNews) {
    return getDefaultTopics(lang);
  }
  
  // In production, this would fetch from RSS/API
  // For now, return trending AI topics
  const topics = {
    ja: [
      'Claude最新アップデート', 'GPT-5リリース予測', 'AI画像生成の進化',
      'Perplexity新機能', 'Cursor AI機能拡張', 'AIエージェント活用術',
      'LLMコスト削減', '自動化ツール比較', 'AI副業事例',
      'プロンプトエンジニアリング', 'AIセキュリティ対策', 'マルチモーダルAI',
      'Vibe Coding最新トレンド', 'AI会議ツール', '生成AI規制動向'
    ],
    en: [
      'Claude new features', 'GPT-5 release rumors', 'AI image generation',
      'Perplexity updates', 'Cursor AI expansion', 'AI agents tutorial',
      'LLM cost optimization', 'automation comparison', 'AI side hustle',
      'prompt engineering', 'AI security', 'multimodal AI',
      'Vibe Coding trends', 'AI meeting tools', 'AI regulation updates'
    ],
    cn: [
      'Claude最新功能', 'GPT-5发布预测', 'AI图像生成',
      'Perplexity更新', 'Cursor AI扩展', 'AI代理应用',
      'LLM成本优化', '自动化工具对比', 'AI副业案例',
      '提示工程技巧', 'AI安全', '多模态AI',
      'Vibe Coding趋势', 'AI会议工具', '生成AI监管'
    ]
  };
  
  return topics[lang] || topics.en;
}

function getDefaultTopics(lang) {
  const defaults = {
    ja: ['AI活用術', '効率化テクニック', '最新ツール紹介', '業界トレンド', '実践ガイド'],
    en: ['AI Tips', 'Productivity Hacks', 'New Tools', 'Industry Trends', 'How-To Guides'],
    cn: ['AI技巧', '效率提升', '新工具介绍', '行业趋势', '实践指南']
  };
  return defaults[lang] || defaults.en;
}

// ─── Main Generation Flow ────────────────────────────────────────────────────

async function generateDaily15Enhanced(options = {}) {
  const {
    lang = 'ja',
    timeSlot = 'morning', // 'morning', 'lunch', 'evening'
    customTopics = null
  } = options;
  
  console.log(`\n🚀 [daily-15] Starting generation for ${lang} (${timeSlot})`);
  console.log(`   Time: ${new Date().toLocaleString('ja-JP')}`);
  
  let memoryPatterns = null;
  
  // Step 1: Analyze user memory (if enabled)
  if (CONFIG.useMemory) {
    try {
      console.log('[daily-15] Analyzing OpenClaw memory...');
      memoryPatterns = await analyzeUserFromMemory();
      console.log(`   ✓ Found ${memoryPatterns.experiences.length} experiences, ${memoryPatterns.topics.length} topics`);
      console.log(`   ✓ Writing style: ${memoryPatterns.writingStyle.tone.join(', ') || 'balanced'}`);
    } catch (e) {
      console.warn('[daily-15] Memory analysis failed:', e.message);
    }
  }
  
  // Step 2: Fetch news topics
  let topics = customTopics;
  if (!topics) {
    topics = await fetchNewsTopics(lang);
  }
  
  // Step 3: Generate posts with AI
  console.log('[daily-15] Generating 15 posts with AI...');
  let posts;
  
  try {
    // Try AI-powered generation first
    posts = await generateAI15({
      lang,
      memoryPatterns,
      newsTopics: topics
    });
  } catch (e) {
    console.error('[daily-15] AI generation failed, falling back to templates:', e.message);
    // Fallback to template-based generation
    posts = await generateTemplateFallback(lang, topics);
  }
  
  // Step 4: Enhance posts with user's first-hand experiences
  if (memoryPatterns?.experiences?.length > 0) {
    console.log('[daily-15] Enhancing posts with personal experiences...');
    posts = enhanceWithExperiences(posts, memoryPatterns.experiences, lang);
  }
  
  // Step 5: Save and deliver
  const result = await saveAndDeliver(posts, lang, timeSlot);
  
  console.log(`\n✅ [daily-15] Complete! ${posts.length} posts generated.`);
  console.log(`   📁 File: ${result.filepath}`);
  console.log(`   🔗 URL: ${result.url}`);
  
  return { posts, ...result };
}

/**
 * Enhance posts with user's personal experiences
 */
function enhanceWithExperiences(posts, experiences, lang) {
  return posts.map((post, index) => {
    // For certain patterns, inject personal experience
    const experiencePatterns = ['07-first-impression', '13-storytelling', '05-honest-opinion'];
    
    if (experiencePatterns.includes(post.patternId) && experiences[index % experiences.length]) {
      const exp = experiences[index % experiences.length];
      // Add experience reference without making it too long
      const enhancedText = post.text.replace(
        /(👇|詳細|→)$/m,
        `（${exp.slice(0, 30)}...の経験から） $1`
      );
      return { ...post, text: enhancedText, hasExperience: true };
    }
    
    return post;
  });
}

/**
 * Template fallback if AI fails
 */
async function generateTemplateFallback(lang, topics) {
  const { VIRAL_PATTERNS } = require('../core/generator');
  const patterns = Object.keys(VIRAL_PATTERNS).sort();
  
  return topics.slice(0, 15).map((topic, i) => {
    const patternId = patterns[i % patterns.length];
    const post = generatePost(patternId, topic, lang);
    return {
      ...post,
      number: i + 1,
      patternName: VIRAL_PATTERNS[patternId]?.name[lang] || VIRAL_PATTERNS[patternId]?.name.en,
      model: 'fallback-template'
    };
  });
}

/**
 * Save posts and deliver
 */
async function saveAndDeliver(posts, lang, timeSlot) {
  const date = new Date().toISOString().split('T')[0];
  const filename = `${date}-${lang}-${timeSlot}.json`;
  const filepath = path.join(OUTPUT_DIR, filename);
  
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  
  const data = {
    date,
    lang,
    timeSlot,
    generatedAt: new Date().toISOString(),
    totalPosts: posts.length,
    aiModel: CONFIG.aiModel,
    hasMemoryContext: CONFIG.useMemory,
    posts
  };
  
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
  
  // Update latest
  const latestPath = path.join(OUTPUT_DIR, `latest-${lang}.json`);
  fs.writeFileSync(latestPath, JSON.stringify(data, null, 2));
  
  // Log
  fs.mkdirSync(path.dirname(LOG_PATH), { recursive: true });
  fs.appendFileSync(LOG_PATH, JSON.stringify({
    ts: new Date().toISOString(),
    lang,
    timeSlot,
    count: posts.length,
    model: CONFIG.aiModel
  }) + '\n');
  
  // Deliver to webhook if configured
  if (CONFIG.webhookUrl) {
    await deliverToWebhook(data);
  }
  
  return {
    filepath,
    filename,
    url: `${CONFIG.baseUrl}/daily.html?date=${date}&lang=${lang}&slot=${timeSlot}`
  };
}

/**
 * Deliver to Discord/Slack webhook
 */
async function deliverToWebhook(data) {
  const { date, lang, timeSlot, posts, url } = data;
  
  const slotNames = {
    morning: '🌅 朝7時',
    lunch: '🌞 昼12時',
    evening: '🌆 夕方18時'
  };
  
  const embed = {
    username: 'OpClawX Daily Posts',
    avatar_url: 'https://cdn-icons-png.flaticon.com/512/4712/4712109.png',
    embeds: [{
      title: `${slotNames[timeSlot] || timeSlot} — 15投稿生成完了`,
      description: `**${date}** — ${posts.length}個のバズ投稿案を生成しました！`,
      color: 0x5865F2,
      fields: [
        { name: '📝 言語', value: lang.toUpperCase(), inline: true },
        { name: '🤖 AIモデル', value: data.aiModel, inline: true },
        { name: '🧠 メモリ連携', value: data.hasMemoryContext ? 'ON' : 'OFF', inline: true },
        { name: '🔗 閲覧URL', value: url }
      ],
      footer: { text: 'OpClawX — AI-Powered Viral Post Generator' },
      timestamp: new Date().toISOString()
    }]
  };
  
  try {
    await new Promise((resolve, reject) => {
      const urlObj = new URL(CONFIG.webhookUrl);
      const body = JSON.stringify(embed);
      
      const req = https.request({
        hostname: urlObj.hostname,
        path: urlObj.pathname + urlObj.search,
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
      }, res => {
        if (res.statusCode >= 200 && res.statusCode < 300) resolve();
        else reject(new Error(`HTTP ${res.statusCode}`));
      });
      
      req.on('error', reject);
      req.write(body);
      req.end();
    });
    console.log('[daily-15] ✅ Delivered to webhook');
  } catch (e) {
    console.error('[daily-15] ❌ Webhook delivery failed:', e.message);
  }
}

// ─── CLI ─────────────────────────────────────────────────────────────────────

if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    console.log(`
OpClawX Daily 15-Post Generator — AI-Powered with Memory

Usage:
  node scheduler/daily-15.js [options]

Options:
  --lang [ja|en|cn]     Language (default: ja)
  --slot [morning|lunch|evening]  Time slot (default: morning)
  --topics "t1,t2,..."  Custom topics (comma-separated)
  --no-memory           Disable memory analysis
  --no-news             Disable news fetching
  --help                Show this help

Environment:
  OPENAI_API_KEY        OpenAI API key
  ANTHROPIC_API_KEY     Claude API key
  VPA_WEBHOOK_URL       Discord/Slack webhook URL
  VPA_USE_MEMORY        Enable memory analysis (true/false)
  XPREMIUM_DATA_PATH    Path to X Premium export

Examples:
  node scheduler/daily-15.js --lang ja --slot morning
  node scheduler/daily-15.js --lang en --topics "AI Tips,Productivity"
  node scheduler/daily-15.js --no-memory --no-news
    `);
    process.exit(0);
  }
  
  const getArg = (flag) => {
    const i = args.indexOf(flag);
    return i !== -1 ? args[i + 1] : null;
  };
  const hasArg = (flag) => args.includes(flag);
  
  const options = {
    lang: getArg('--lang') || 'ja',
    timeSlot: getArg('--slot') || 'morning',
    customTopics: getArg('--topics')?.split(',').map(t => t.trim()),
  };
  
  if (hasArg('--no-memory')) CONFIG.useMemory = false;
  if (hasArg('--no-news')) CONFIG.fetchNews = false;
  
  generateDaily15Enhanced(options).catch(err => {
    console.error('[daily-15] Fatal error:', err);
    process.exit(1);
  });
}

module.exports = { generateDaily15Enhanced, CONFIG };
