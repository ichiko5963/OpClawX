/**
 * Feedback Collector — Learn from user preferences to improve future posts
 * Asks "Which posts did you like?" and uses that data to refine prompts
 */

const fs = require('fs');
const path = require('path');

const FEEDBACK_DIR = path.join(__dirname, '../data/feedback');
const PREFERENCES_FILE = path.join(__dirname, '../data/user-preferences.json');

/**
 * Initialize feedback system
 */
function initFeedbackSystem() {
  fs.mkdirSync(FEEDBACK_DIR, { recursive: true });
  if (!fs.existsSync(PREFERENCES_FILE)) {
    fs.writeFileSync(PREFERENCES_FILE, JSON.stringify({
      likedPatterns: {},
      likedTopics: {},
      dislikedPatterns: {},
      engagementHistory: [],
      lastUpdated: new Date().toISOString()
    }, null, 2));
  }
}

/**
 * Collect feedback for a daily batch of posts
 */
async function collectFeedback(date, lang, posts) {
  initFeedbackSystem();
  
  const feedbackData = {
    date,
    lang,
    timestamp: new Date().toISOString(),
    posts: posts.map(p => ({
      id: p.id || `${p.patternId}-${date}`,
      patternId: p.patternId,
      patternName: p.patternName,
      topic: p.topic,
      preview: p.text?.slice(0, 100) + '...'
    })),
    feedbackUrl: generateFeedbackUrl(date, lang)
  };
  
  const feedbackPath = path.join(FEEDBACK_DIR, `${date}-${lang}.json`);
  fs.writeFileSync(feedbackPath, JSON.stringify(feedbackData, null, 2));
  
  return feedbackData;
}

/**
 * Generate a unique URL for feedback collection
 */
function generateFeedbackUrl(date, lang) {
  const baseUrl = process.env.VPA_BASE_URL || 'https://opclawx.vercel.app';
  return `${baseUrl}/feedback.html?date=${date}&lang=${lang}`;
}

/**
 * Record user feedback (which posts they liked)
 */
function recordFeedback(date, lang, likedPostIds, comments = '') {
  initFeedbackSystem();
  
  const preferences = JSON.parse(fs.readFileSync(PREFERENCES_FILE, 'utf8'));
  
  // Load the day's posts to get full details
  const feedbackPath = path.join(FEEDBACK_DIR, `${date}-${lang}.json`);
  if (!fs.existsSync(feedbackPath)) {
    console.warn(`[feedback] No data found for ${date}`);
    return;
  }
  
  const dayData = JSON.parse(fs.readFileSync(feedbackPath, 'utf8'));
  
  // Update preferences based on likes
  likedPostIds.forEach(postId => {
    const post = dayData.posts.find(p => p.id === postId);
    if (post) {
      // Track liked patterns
      preferences.likedPatterns[post.patternId] = 
        (preferences.likedPatterns[post.patternId] || 0) + 1;
      
      // Track liked topics
      preferences.likedTopics[post.topic] = 
        (preferences.likedTopics[post.topic] || 0) + 1;
    }
  });
  
  // Record engagement
  preferences.engagementHistory.push({
    date,
    lang,
    likedCount: likedPostIds.length,
    totalPosts: dayData.posts.length,
    comments,
    timestamp: new Date().toISOString()
  });
  
  // Keep only last 90 days
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 90);
  preferences.engagementHistory = preferences.engagementHistory.filter(
    h => new Date(h.date) > cutoff
  );
  
  preferences.lastUpdated = new Date().toISOString();
  
  fs.writeFileSync(PREFERENCES_FILE, JSON.stringify(preferences, null, 2));
  
  console.log(`[feedback] Recorded ${likedPostIds.length} likes for ${date}`);
}

/**
 * Get user preferences for improving future posts
 */
function getUserPreferences() {
  initFeedbackSystem();
  
  if (!fs.existsSync(PREFERENCES_FILE)) {
    return null;
  }
  
  const prefs = JSON.parse(fs.readFileSync(PREFERENCES_FILE, 'utf8'));
  
  // Calculate top preferences
  const topPatterns = Object.entries(prefs.likedPatterns)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([id, count]) => ({ patternId: id, count }));
  
  const topTopics = Object.entries(prefs.likedTopics)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([topic, count]) => ({ topic, count }));
  
  return {
    ...prefs,
    topPatterns,
    topTopics,
    totalFeedbackSessions: prefs.engagementHistory.length,
    averageLikesPerSession: prefs.engagementHistory.length > 0
      ? prefs.engagementHistory.reduce((sum, h) => sum + h.likedCount, 0) / prefs.engagementHistory.length
      : 0
  };
}

/**
 * Generate improved prompts based on feedback
 */
function generateImprovedContext(baseContext, userPreferences) {
  if (!userPreferences || !userPreferences.topPatterns.length) {
    return baseContext;
  }
  
  const improved = { ...baseContext };
  
  // Add preference hints to system prompt
  const likedPatterns = userPreferences.topPatterns
    .map(p => p.patternId)
    .join(', ');
  
  const likedTopics = userPreferences.topTopics
    .map(t => t.topic)
    .join(', ');
  
  improved.systemPrompt += `

USER PREFERENCE DATA (from past feedback):
- Preferred post patterns: ${likedPatterns}
- Preferred topics: ${likedTopics}
- Average engagement: ${userPreferences.averageLikesPerSession.toFixed(1)} likes per session

Use this data to prioritize similar patterns and topics in future posts.`;
  
  return improved;
}

/**
 * Create feedback prompt for Discord/webhook
 */
function createFeedbackPrompt(feedbackData) {
  return {
    text: `📊 Daily Posts Generated — Feedback Request`,
    embeds: [{
      title: `Which posts did you like?`,
      description: `15 posts generated for ${feedbackData.date}. Click the link below to select your favorites and help me improve!`,
      color: 0x5865F2,
      fields: [
        { 
          name: '📝 Posts', 
          value: feedbackData.posts.map((p, i) => `${i+1}. ${p.patternName}`).join('\n'),
          inline: false 
        },
        { 
          name: '👍 Give Feedback', 
          value: `[Click here to select favorites](${feedbackData.feedbackUrl})`,
          inline: false 
        }
      ],
      footer: { text: 'The more you use it, the smarter it gets!' }
    }]
  };
}

module.exports = {
  initFeedbackSystem,
  collectFeedback,
  recordFeedback,
  getUserPreferences,
  generateImprovedContext,
  createFeedbackPrompt,
  generateFeedbackUrl
};
