/**
 * Memory Analyzer — Extract user patterns and experiences from OpenClaw memory
 * Learns writing style, topics, and first-hand experiences
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const MEMORY_DIR = process.env.VPA_MEMORY_DIR || path.join(__dirname, '../memory');
const OPENCLAW_WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME, 'Documents/OpenClaw-Workspace');

/**
 * Search OpenClaw memory for user's writing patterns
 */
async function analyzeUserFromMemory(userId = 'default') {
  console.log('[memory-analyzer] Analyzing user patterns from memory...');
  
  const patterns = {
    writingStyle: {
      tone: [], // casual, formal, humorous, serious
      commonPhrases: [],
      emojiUsage: [],
      sentenceLength: 'medium',
      questionFrequency: 0
    },
    topics: [], // frequently discussed topics
    experiences: [], // first-hand experiences to draw from
    postingTimes: [], // when user usually posts
    engagementPatterns: {
      highPerformingTypes: [],
      commonHooks: []
    }
  };
  
  // 1. Read recent memory files
  const memoryFiles = getRecentMemoryFiles(30); // last 30 days
  
  for (const file of memoryFiles) {
    try {
      const content = fs.readFileSync(file, 'utf8');
      
      // Extract writing patterns
      extractWritingStyle(content, patterns.writingStyle);
      
      // Extract topics
      extractTopics(content, patterns.topics);
      
      // Extract first-hand experiences
      extractExperiences(content, patterns.experiences);
      
    } catch (e) {
      console.warn(`[memory-analyzer] Error reading ${file}:`, e.message);
    }
  }
  
  // 2. If X Premium data exists, merge with memory analysis
  const xpremiumData = await loadXPremiumData();
  if (xpremiumData) {
    mergeXPremiumPatterns(patterns, xpremiumData);
  }
  
  console.log(`[memory-analyzer] Found ${patterns.experiences.length} experiences, ${patterns.topics.length} topics`);
  
  return patterns;
}

/**
 * Get recent memory files from OpenClaw workspace
 */
function getRecentMemoryFiles(days = 30) {
  const files = [];
  const today = new Date();
  
  for (let i = 0; i < days; i++) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    
    const memoryFile = path.join(MEMORY_DIR, `${dateStr}.md`);
    if (fs.existsSync(memoryFile)) {
      files.push(memoryFile);
    }
  }
  
  // Also check main MEMORY.md
  const mainMemory = path.join(OPENCLAW_WORKSPACE, 'MEMORY.md');
  if (fs.existsSync(mainMemory)) {
    files.push(mainMemory);
  }
  
  return files;
}

/**
 * Extract writing style characteristics
 */
function extractWritingStyle(content, style) {
  // Detect tone
  if (/！|🎉|🔥|✨|💡/.test(content)) style.tone.push('energetic');
  if (/です|ます|ますか|でしょう/.test(content)) style.tone.push('formal');
  if (/だね|だよ|かな|わかる/.test(content)) style.tone.push('casual');
  if (/【|】|◎|★/.test(content)) style.tone.push('structured');
  
  // Extract common phrases (2-4 word phrases that appear multiple times)
  const phrases = content.match(/[あ-ん]{2,8}/g) || [];
  const phraseCounts = {};
  phrases.forEach(p => {
    phraseCounts[p] = (phraseCounts[p] || 0) + 1;
    if (phraseCounts[p] >= 2 && !style.commonPhrases.includes(p)) {
      style.commonPhrases.push(p);
    }
  });
  
  // Emoji usage
  const emojis = content.match(/[\u{1F300}-\u{1F9FF}]/gu) || [];
  emojis.forEach(e => {
    if (!style.emojiUsage.includes(e)) style.emojiUsage.push(e);
  });
  
  // Sentence length estimation
  const sentences = content.split(/[。！？\n]/).filter(s => s.trim().length > 5);
  const avgLength = sentences.reduce((sum, s) => sum + s.length, 0) / sentences.length;
  if (avgLength < 30) style.sentenceLength = 'short';
  else if (avgLength > 60) style.sentenceLength = 'long';
  else style.sentenceLength = 'medium';
}

/**
 * Extract frequently discussed topics
 */
function extractTopics(content, topics) {
  // Tech/AI keywords
  const techKeywords = [
    'Claude', 'ChatGPT', 'GPT', 'AI', 'OpenAI', 'Gemini', 'Cursor',
    'Vibe Coding', 'バイブコーディング', 'LLM', '生成AI'
  ];
  
  // Business/marketing keywords
  const businessKeywords = [
    'マーケティング', '集客', '売上', 'コンセプト', 'ブランド',
    'SNS', 'X投稿', 'バズる', 'エンゲージメント'
  ];
  
  // Check for keywords
  [...techKeywords, ...businessKeywords].forEach(keyword => {
    if (content.includes(keyword) && !topics.includes(keyword)) {
      topics.push(keyword);
    }
  });
  
  // Extract hashtags
  const hashtags = content.match(/#[\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+/g) || [];
  hashtags.forEach(tag => {
    const cleanTag = tag.slice(1); // Remove #
    if (!topics.includes(cleanTag)) topics.push(cleanTag);
  });
}

/**
 * Extract first-hand experiences (体験記・実体験)
 */
function extractExperiences(content, experiences) {
  // Patterns indicating personal experience
  const experiencePatterns = [
    /使ってみた|試してみた|やってみた|検証してみた/g,
    /結果は|感想は|結論は/g,
    /気づいた|学んだ|分かった/g,
    /から始めた|から変わった/g
  ];
  
  // Split into paragraphs and find experience sections
  const paragraphs = content.split(/\n\n/);
  
  paragraphs.forEach(para => {
    // Check if paragraph contains experience indicators
    const hasExperience = experiencePatterns.some(pattern => pattern.test(para));
    const hasPersonalPronoun = /私は|僕は|自分は|うちは/.test(para);
    
    if (hasExperience && hasPersonalPronoun && para.length > 50 && para.length < 500) {
      // Clean up and add
      const cleanExperience = para.trim().replace(/\n/g, ' ');
      if (!experiences.some(e => e.includes(cleanExperience.slice(0, 30)))) {
        experiences.push(cleanExperience);
      }
    }
  });
}

/**
 * Load X Premium analytics data if available
 */
async function loadXPremiumData() {
  const xpremiumPath = process.env.XPREMIUM_DATA_PATH;
  if (!xpremiumPath || !fs.existsSync(xpremiumPath)) {
    return null;
  }
  
  try {
    const data = JSON.parse(fs.readFileSync(xpremiumPath, 'utf8'));
    return data;
  } catch (e) {
    console.warn('[memory-analyzer] Failed to load X Premium data:', e.message);
    return null;
  }
}

/**
 * Merge X Premium patterns with memory analysis
 */
function mergeXPremiumPatterns(patterns, xpremiumData) {
  if (xpremiumData.highPerformingPosts) {
    patterns.engagementPatterns.highPerformingTypes = 
      xpremiumData.highPerformingPosts.map(p => p.pattern || 'unknown');
  }
  
  if (xpremiumData.topics) {
    xpremiumData.topics.forEach(t => {
      if (!patterns.topics.includes(t)) patterns.topics.push(t);
    });
  }
}

/**
 * Generate AI context from memory patterns
 */
function generateMemoryContext(patterns) {
  const context = {
    systemPrompt: `You are an expert social media copywriter who specializes in creating viral X/Twitter posts.

USER PROFILE:
- Writing Style: ${patterns.writingStyle.tone.join(', ') || 'balanced'}
- Sentence Length: ${patterns.writingStyle.sentenceLength}
- Common Phrases: ${patterns.writingStyle.commonPhrases.slice(0, 5).join(', ')}
- Preferred Emojis: ${patterns.writingStyle.emojiUsage.slice(0, 5).join(' ')}

EXPERTISE TOPICS:
${patterns.topics.slice(0, 10).map(t => `- ${t}`).join('\n')}

${patterns.experiences.length > 0 ? `
FIRST-HAND EXPERIENCES (draw from these for authentic content):
${patterns.experiences.slice(0, 3).map((e, i) => `${i + 1}. ${e.slice(0, 100)}...`).join('\n')}
` : ''}

INSTRUCTIONS:
1. Write in the user's natural style (not generic AI text)
2. Use their common phrases and emoji patterns
3. Reference real experiences when relevant
4. Keep posts under 280 characters
5. Make it engaging and shareable`,

    userContext: patterns
  };
  
  return context;
}

module.exports = {
  analyzeUserFromMemory,
  generateMemoryContext,
  getRecentMemoryFiles
};
