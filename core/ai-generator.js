/**
 * AI Generator — Generate posts using OpenAI/Claude with memory context
 * Creates authentic content based on user's style and experiences
 */

const https = require('https');
const { generateMemoryContext } = require('./memory-analyzer');

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

/**
 * Generate a viral post using AI with memory context
 */
async function generateAIPost(options = {}) {
  const {
    patternId,
    topic,
    lang = 'ja',
    memoryPatterns = null,
    newsContext = null,
    model = 'claude' // 'claude' or 'openai'
  } = options;
  
  // Build context
  const context = memoryPatterns ? generateMemoryContext(memoryPatterns) : getDefaultContext(lang);
  
  // Build prompt
  const prompt = buildAIPrompt(patternId, topic, lang, context, newsContext);
  
  // Call AI API
  let post;
  if (model === 'claude' && ANTHROPIC_API_KEY) {
    post = await callClaude(prompt, context.systemPrompt);
  } else if (OPENAI_API_KEY) {
    post = await callOpenAI(prompt, context.systemPrompt);
  } else {
    // Fallback to template if no API keys
    post = generateTemplatePost(patternId, topic, lang);
  }
  
  return {
    text: post,
    patternId,
    topic,
    lang,
    generatedAt: new Date().toISOString(),
    model: model,
    hasMemoryContext: !!memoryPatterns
  };
}

/**
 * Build AI prompt with context
 */
function buildAIPrompt(patternId, topic, lang, context, newsContext) {
  const patternNames = {
    ja: {
      '01-breaking-news': '速報型',
      '02-save-for-later': '保存版型',
      '03-global-trend': '海外バズ型',
      '04-conclusion-first': '結論型',
      '05-honest-opinion': '正直型',
      '06-vs-battle': '比較型',
      '07-first-impression': '体験記型',
      '08-by-numbers': '数字強調型',
      '09-insight': '洞察型',
      '10-freebie': '配布型',
      '11-pro-tips': '裏技型',
      '12-warning': '警告型',
      '13-storytelling': 'ストーリー型',
      '14-complete-guide': '完全解説型',
      '15-future-forecast': '予測型'
    }
  };
  
  const patternName = patternNames[lang]?.[patternId] || patternId;
  
  let userPrompt = '';
  
  if (lang === 'ja') {
    userPrompt = `以下の条件で、X（Twitter）のバズる投稿を1つ作成してください：

【投稿タイプ】: ${patternName}
【トピック】: ${topic}
${newsContext ? `【最新情報】: ${newsContext}` : ''}

必要条件:
- 280文字以内
- ユーザーの文体（${context.userContext?.writingStyle?.tone?.join(', ') || 'カジュアル'}）で書く
- 絵文字を適度に使用（${context.userContext?.writingStyle?.emojiUsage?.slice(0, 3).join('') || '🔥👇'}）
- 具体的で実用的な内容
- 「AIが書いた」感を出さない、人間らしい表現
${context.userContext?.experiences?.length > 0 ? '- 可能であれば、過去の経験を反映させる' : ''}

投稿文のみを出力してください。説明は不要です。`;
  } else {
    userPrompt = `Create a viral X/Twitter post with the following:

Pattern: ${patternName}
Topic: ${topic}
${newsContext ? `Latest Context: ${newsContext}` : ''}

Requirements:
- Under 280 characters
- Write in the user's natural style
- Use appropriate emojis
- Be specific and practical
- Sound human, not AI-generated

Output ONLY the post text.`;
  }
  
  return userPrompt;
}

/**
 * Call Claude API
 */
async function callClaude(userPrompt, systemPrompt) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'claude-3-sonnet-20240229',
      max_tokens: 500,
      system: systemPrompt,
      messages: [{ role: 'user', content: userPrompt }]
    });
    
    const options = {
      hostname: 'api.anthropic.com',
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      }
    };
    
    const req = https.request(options, (res) => {
      let responseData = '';
      res.on('data', chunk => responseData += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(responseData);
          if (parsed.content && parsed.content[0]) {
            resolve(parsed.content[0].text.trim());
          } else {
            reject(new Error('Invalid Claude response'));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * Call OpenAI API
 */
async function callOpenAI(userPrompt, systemPrompt) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      max_tokens: 300,
      temperature: 0.8
    });
    
    const options = {
      hostname: 'api.openai.com',
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`
      }
    };
    
    const req = https.request(options, (res) => {
      let responseData = '';
      res.on('data', chunk => responseData += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(responseData);
          if (parsed.choices && parsed.choices[0]) {
            resolve(parsed.choices[0].message.content.trim());
          } else {
            reject(new Error('Invalid OpenAI response'));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * Fallback template generation
 */
function generateTemplatePost(patternId, topic, lang) {
  const templates = {
    ja: {
      '01-breaking-news': `【速報】${topic}がついに登場！🔥

・ポイント1
・ポイント2
・ポイント3

詳細👇`,
      '04-conclusion-first': `【結論】${topic}はこう使うと効果的

理由:
・理由1
・理由2
・理由3

実践してみて👇`,
      '07-first-impression': `${topic}使ってみた！

期待: ○○
実際: ○○

感想:
・ポイント1
・ポイント2

試してみて👇`,
      '10-freebie': `【配布】${topic}のテンプレート🎁

中身:
・資料1
・資料2
・資料3

欲しい人はRT+フォロー👇`
    }
  };
  
  return templates[lang]?.[patternId] || `${topic}についての投稿です。

・ポイント1
・ポイント2
・ポイント3

詳細👇`;
}

/**
 * Generate 15 posts with AI and memory
 */
async function generateDaily15(options = {}) {
  const { lang = 'ja', memoryPatterns = null, newsTopics = [] } = options;
  
  console.log('[ai-generator] Generating 15 posts with AI...');
  
  const patterns = [
    '01-breaking-news', '02-save-for-later', '03-global-trend',
    '04-conclusion-first', '05-honest-opinion', '06-vs-battle',
    '07-first-impression', '08-by-numbers', '09-insight',
    '10-freebie', '11-pro-tips', '12-warning',
    '13-storytelling', '14-complete-guide', '15-future-forecast'
  ];
  
  const posts = [];
  
  for (let i = 0; i < 15; i++) {
    const patternId = patterns[i];
    
    // Get topic from news or memory
    let topic;
    if (newsTopics[i]) {
      topic = newsTopics[i];
    } else if (memoryPatterns?.topics?.length > 0) {
      topic = memoryPatterns.topics[i % memoryPatterns.topics.length];
    } else {
      topic = getDefaultTopic(i, lang);
    }
    
    try {
      const post = await generateAIPost({
        patternId,
        topic,
        lang,
        memoryPatterns,
        model: ANTHROPIC_API_KEY ? 'claude' : 'openai'
      });
      
      posts.push({
        number: i + 1,
        ...post
      });
      
      // Small delay to avoid rate limits
      await new Promise(r => setTimeout(r, 500));
      
    } catch (e) {
      console.error(`[ai-generator] Error generating post ${i + 1}:`, e.message);
      // Fallback to template
      posts.push({
        number: i + 1,
        patternId,
        topic,
        text: generateTemplatePost(patternId, topic, lang),
        lang,
        generatedAt: new Date().toISOString(),
        model: 'fallback',
        hasMemoryContext: !!memoryPatterns
      });
    }
  }
  
  return posts;
}

function getDefaultTopic(index, lang) {
  const defaults = {
    ja: [
      'AI最新機能', '効率化ツール', '業界トレンド', '実践テクニック',
      '初心者向けガイド', '比較レビュー', '使い方解説', '導入事例',
      'コスト削減', '時短術', '自動化術', '注意点',
      '成功事例', '完全ガイド', '未来予測'
    ]
  };
  
  return defaults[lang]?.[index] || 'AI活用術';
}

function getDefaultContext(lang) {
  return {
    systemPrompt: `You are an expert social media copywriter specializing in viral X/Twitter posts. Write in a natural, engaging style.`,
    userContext: { writingStyle: { tone: ['casual'] }, topics: [], experiences: [] }
  };
}

module.exports = {
  generateAIPost,
  generateDaily15,
  generateTemplatePost
};
