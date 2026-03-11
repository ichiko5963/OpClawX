#!/usr/bin/env node
/**
 * Daily 15-Post Generator — cron版
 * Fetches latest news → generates 15 viral posts (one per pattern) → saves to JSON → delivers URL
 */

const fs   = require('fs');
const path = require('path');
const https = require('https');
const { generatePost, VIRAL_PATTERNS } = require('../core/generator');
const { t } = require('../i18n');

const OUTPUT_DIR = path.join(__dirname, '../web/daily');
const LOG_PATH   = path.join(__dirname, '../logs/daily-15.jsonl');

// ─── News Fetchers (multiple sources for redundancy) ──────────────────────────

async function fetchNews(lang = 'ja') {
  const sources = {
    ja: [
      { name: 'TechCrunch JP', url: 'https://techcrunch.jp/feed/' },
      { name: 'ITmedia', url: 'https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml' }
    ],
    en: [
      { name: 'TechCrunch', url: 'https://techcrunch.com/feed/' },
      { name: 'The Verge', url: 'https://www.theverge.com/rss/index.xml' }
    ],
    cn: [
      { name: '36kr', url: 'https://36kr.com/feed' }
    ]
  };
  
  // For now, return trending topics based on common AI themes
  // In production, you'd parse RSS feeds here
  const topics = {
    ja: [
      'Claude最新アップデート', 'GPT-5リリース予測', 'AI画像生成の進化',
      'Perplexity新機能', 'Midjourney V7', 'OpenAI新モデル',
      'Cursor AI機能拡張', 'AIエージェント活用術', 'LLMコスト削減',
      'AI作曲ツール最新', '自動化ツール比較', 'AI副業事例',
      'プロンプトエンジニアリング', 'AIセキュリティ対策', 'マルチモーダルAI'
    ],
    en: [
      'Claude new features', 'GPT-5 release rumors', 'AI image generation',
      'Perplexity updates', 'Midjourney V7', 'OpenAI latest model',
      'Cursor AI expansion', 'AI agents tutorial', 'LLM cost optimization',
      'AI music tools', 'automation comparison', 'AI side hustle cases',
      'prompt engineering tips', 'AI security best practices', 'multimodal AI'
    ],
    cn: [
      'Claude最新功能', 'GPT-5发布预测', 'AI图像生成',
      'Perplexity更新', 'Midjourney V7', 'OpenAI新模型',
      'Cursor AI扩展', 'AI代理应用', 'LLM成本优化'
    ]
  };
  
  const list = topics[lang] || topics.en;
  // Shuffle and pick 15
  return list.sort(() => 0.5 - Math.random()).slice(0, 15);
}

// ─── Generate 15 Posts (one per pattern) ──────────────────────────────────────

async function generateDaily15(lang = 'ja', customTopics = null) {
  console.log(`[daily-15] Generating 15 posts for ${lang}...`);
  
  // Get topics
  let topics = customTopics;
  if (!topics) {
    topics = await fetchNews(lang);
  }
  
  // Ensure we have 15 topics
  while (topics.length < 15) {
    topics.push(topics[topics.length % topics.length]); // repeat if needed
  }
  
  const patterns = Object.keys(VIRAL_PATTERNS).sort();
  const posts = [];
  
  for (let i = 0; i < 15; i++) {
    const patternId = patterns[i];
    const topic = topics[i];
    
    try {
      const post = generatePost(patternId, topic, lang, {
        baseUrl: process.env.VPA_BASE_URL || 'https://vpa.opclaw.app'
      });
      posts.push({
        ...post,
        number: i + 1,
        patternName: VIRAL_PATTERNS[patternId]?.name[lang] || VIRAL_PATTERNS[patternId]?.name.en
      });
    } catch (err) {
      console.error(`[daily-15] Error generating post ${i+1}:`, err.message);
    }
  }
  
  return posts;
}

// ─── Save to Web Directory ───────────────────────────────────────────────────

function saveDailyPage(posts, lang = 'ja') {
  const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const filename = `${today}-${lang}.json`;
  const filepath = path.join(OUTPUT_DIR, filename);
  
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  
  const data = {
    date: today,
    lang,
    generatedAt: new Date().toISOString(),
    totalPosts: posts.length,
    posts
  };
  
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
  
  // Also update latest.json symlink equivalent
  const latestPath = path.join(OUTPUT_DIR, `latest-${lang}.json`);
  fs.writeFileSync(latestPath, JSON.stringify(data, null, 2));
  
  console.log(`[daily-15] Saved to ${filepath}`);
  return { filepath, filename, url: `/daily/${filename}` };
}

// ─── Discord Delivery ────────────────────────────────────────────────────────

async function deliverToDiscord(webhookUrl, posts, lang = 'ja') {
  if (!webhookUrl) {
    console.log('[daily-15] No webhook configured, skipping delivery');
    return;
  }
  
  const today = new Date().toLocaleDateString(lang === 'ja' ? 'ja-JP' : lang === 'cn' ? 'zh-CN' : 'en-US');
  
  // Create summary embed
  const summary = {
    username: 'Viral Post Automation',
    avatar_url: 'https://cdn-icons-png.flaticon.com/512/4712/4712109.png',
    embeds: [{
      title: `📅 ${today} のバズ投稿15案 / 15 Viral Post Ideas`,
      description: `**全15型のバズる投稿案を生成しました！**\n**15 viral post patterns generated!**`,
      color: 0x5865F2,
      fields: posts.slice(0, 10).map(p => ({
        name: `${p.number}. ${p.patternName}`,
        value: `📝 ${p.topic}\n[View Prompt](${p.url})`,
        inline: true
      })),
      footer: { 
        text: `OpClawX • ${posts.length} patterns • ${lang.toUpperCase()}` 
      },
      timestamp: new Date().toISOString()
    }]
  };
  
  // Add remaining 5 as second embed if needed
  if (posts.length > 10) {
    summary.embeds.push({
      title: '続き / Continued',
      color: 0x57F287,
      fields: posts.slice(10).map(p => ({
        name: `${p.number}. ${p.patternName}`,
        value: `📝 ${p.topic}\n[View Prompt](${p.url})`,
        inline: true
      }))
    });
  }
  
  // Deliver
  try {
    const body = JSON.stringify(summary);
    const urlObj = new URL(webhookUrl);
    
    await new Promise((resolve, reject) => {
      const req = https.request({
        hostname: urlObj.hostname,
        path: urlObj.pathname + urlObj.search,
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
      }, res => {
        let data = '';
        res.on('data', d => data += d);
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            console.log(`[daily-15] ✅ Delivered to Discord`);
            resolve();
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${data}`));
          }
        });
      });
      req.on('error', reject);
      req.write(body);
      req.end();
    });
  } catch (err) {
    console.error('[daily-15] ❌ Discord delivery failed:', err.message);
  }
}

// ─── Log ─────────────────────────────────────────────────────────────────────

function logGeneration(posts, lang) {
  fs.mkdirSync(path.dirname(LOG_PATH), { recursive: true });
  const entry = {
    ts: new Date().toISOString(),
    lang,
    count: posts.length,
    patterns: posts.map(p => p.patternId)
  };
  fs.appendFileSync(LOG_PATH, JSON.stringify(entry) + '\n');
}

// ─── Main Runner ─────────────────────────────────────────────────────────────

async function run(options = {}) {
  const lang = options.lang || process.env.VPA_LANG || 'ja';
  const webhook = options.webhook || process.env.VPA_WEBHOOK_URL;
  const topics = options.topics || null; // Custom topics if provided
  
  console.log(`[daily-15] Starting generation for ${lang}...`);
  
  // Generate
  const posts = await generateDaily15(lang, topics);
  
  // Save
  const { filepath, url } = saveDailyPage(posts, lang);
  
  // Log
  logGeneration(posts, lang);
  
  // Deliver
  if (webhook) {
    await deliverToDiscord(webhook, posts, lang);
  }
  
  console.log(`[daily-15] ✅ Complete! ${posts.length} posts generated.`);
  console.log(`[daily-15] 📁 File: ${filepath}`);
  console.log(`[daily-15] 🔗 URL: ${url}`);
  
  return { posts, filepath, url };
}

// ─── CLI ─────────────────────────────────────────────────────────────────────

if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    console.log(`
Daily 15-Post Generator
Generates 15 viral posts (one per pattern) and saves to web/daily/

Usage:
  node scheduler/daily-15.js --lang ja --webhook <url>
  node scheduler/daily-15.js --topics "topic1,topic2,..."

Environment:
  VPA_LANG         Default language (ja/en/cn/ko/es)
  VPA_WEBHOOK_URL  Discord webhook for delivery
  VPA_BASE_URL     Base URL for generated links

Cron setup:
  crontab -e
  0 7 * * * cd /path/to/OpClawX && node scheduler/daily-15.js --lang ja
    `);
    process.exit(0);
  }
  
  const get = (flag) => {
    const i = args.indexOf(flag);
    return i !== -1 ? args[i + 1] : null;
  };
  
  const lang = get('--lang') || process.env.VPA_LANG || 'ja';
  const webhook = get('--webhook') || process.env.VPA_WEBHOOK_URL;
  const topicsStr = get('--topics');
  const topics = topicsStr ? topicsStr.split(',').map(t => t.trim()) : null;
  
  run({ lang, webhook, topics }).catch(err => {
    console.error('[daily-15] Fatal error:', err);
    process.exit(1);
  });
}

module.exports = { run, generateDaily15 };
