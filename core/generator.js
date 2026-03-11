/**
 * Post Generator — build viral posts from 15 pattern templates
 */

const { VIRAL_PATTERNS } = require('./analyzer');

// Per-pattern prompt templates in 5 languages
const PROMPT_TEMPLATES = {
  '01-breaking-news': {
    en: `Generate a Breaking News style X/Twitter post about: "{topic}"

Rules:
- Start with 【Breaking】or a 🔥 hook  
- Use "finally" / "just dropped" / "announced"
- 3 bullet points: key features or facts
- End with a CTA using 👇
- Max 280 chars, max 2 emojis (🔥 and 👇 only)
- NO numbered lists like ①②③

Output ONLY the post text, nothing else.`,

    ja: `以下のトピックで【速報型】のX投稿を作成してください: "{topic}"

ルール:
- 【速報】から始める
- 「ついに」「登場」「リリース」を使う
- 核心ポイントを3つ箇条書き（・を使う）
- 👇と🔥のみ使用（他の絵文字禁止）
- 番号リスト（①②③）は使わない
- 280文字以内

投稿テキストのみ出力。説明は不要。`,

    cn: `请以以下主题生成【突发新闻】风格的 X/Twitter 帖子: "{topic}"

规则:
- 以【突发】或「终于来了」开头
- 使用"终于""发布""推出"
- 3个要点（用・）
- 只使用 🔥 和 👇
- 不超过280字符

只输出帖子文本，不需要解释。`,

    ko: `다음 주제로 【속보형】 X/Twitter 게시물을 작성하세요: "{topic}"

규칙:
- 【속보】로 시작
- "드디어", "출시", "발표" 사용
- 핵심 포인트 3개 (・사용)
- 🔥와 👇만 사용
- 280자 이내

게시물 텍스트만 출력하세요.`,

    es: `Genera un post estilo Noticia de Última Hora para X/Twitter sobre: "{topic}"

Reglas:
- Empieza con 【Último Momento】o con 🔥
- Usa "finalmente" / "acaba de lanzarse"
- 3 puntos clave (usa ・)
- Solo emoji 🔥 y 👇
- Máx 280 caracteres

Escribe SOLO el texto del post.`
  },

  '02-save-for-later': {
    en: `Generate a Save for Later style X/Twitter post about: "{topic}"

Rules:
- Start with 【Save This】or 【Bookmark】
- Frame as a "complete reference"
- 3-5 actionable steps or facts
- Include 📌 and 👇 (max 2 emojis)
- Max 280 chars

Output ONLY the post text.`,

    ja: `以下のトピックで【保存版型】のX投稿を作成してください: "{topic}"

ルール:
- 【保存版】から始める
- 「後で見返す」「保存推奨」を入れる
- 実践的なステップを3〜5個（・で箇条書き）
- 📌と👇のみ使用
- 280文字以内

投稿テキストのみ出力。`
  },

  '03-global-trend': {
    en: `Generate a Global Trend style X post about: "{topic}"

Rules:
- Start with 【Trending】or 【Global Buzz】
- Mention "worldwide" or "overseas"
- Real use cases (2-3 bullets)
- 🌎 and 👇 only
- Max 280 chars

Output ONLY the post text.`,

    ja: `以下のトピックで【海外バズ型】のX投稿を作成してください: "{topic}"

ルール:
- 【海外で話題】から始める
- 海外の具体的な評価・反応を入れる
- 活用事例を2〜3個
- 🌎と👇のみ使用
- 280文字以内

投稿テキストのみ出力。`
  },

  '04-conclusion-first': {
    en: `Generate a Conclusion First style X post about: "{topic}"

Rules:
- Start with 【Conclusion】or a strong declarative statement
- State the CONCLUSION in line 1
- Give 3 short reasons (bullets with ・)
- End with implication + 👇
- 💡 and 👇 only
- Max 280 chars

Output ONLY the post text.`,

    ja: `以下のトピックで【結論型】のX投稿を作成してください: "{topic}"

ルール:
- 【結論】から始める、または結論を1文目に置く
- 理由を3つ箇条書き（・で）
- 「これが意味すること」で締める
- 💡と👇のみ使用
- 280文字以内

投稿テキストのみ出力。`
  },

  '05-honest-opinion': {
    en: `Generate an Honest Opinion style X post about: "{topic}"

Rules:
- Start with "Honestly," or "Real talk:"
- Share a contrarian or candid view
- Back it with 2 reasons
- Personal tone, no jargon
- Max 1 emoji (😅 or nothing)
- Max 280 chars

Output ONLY the post text.`,

    ja: `以下のトピックで【正直型】のX投稿を作成してください: "{topic}"

ルール:
- 「正直、」または「本音を言うと、」から始める
- 一般的な意見に反する視点を提示
- 2つの理由で裏付け
- 個人的なトーン
- 絵文字は😅か使わないかのどちらか
- 280文字以内

投稿テキストのみ出力。`
  },

  '06-vs-battle': {
    en: `Generate a VS Battle style X post comparing: "{topic}"

Rules:
- Use 【Battle】or A vs B in title
- List 2-3 pros for each side
- Give a clear verdict at the end
- ⚔️ and 👇 only
- Max 280 chars

Output ONLY the post text.`,

    ja: `以下の比較で【比較型】のX投稿を作成してください: "{topic}"

ルール:
- 【頂上決戦】またはA vs Bをタイトルに使う
- それぞれ2〜3つの強みを列挙
- 最後に明確な結論を出す
- ⚔️と👇のみ使用
- 280文字以内

投稿テキストのみ出力。`
  },

  '10-freebie': {
    en: `Generate a Free Resource giveaway style X post about: "{topic}"

Rules:
- Start with 【Free】or 【Giveaway】
- Include "want it?" or similar
- List 3 items/contents with ・
- Clear acquisition method (follow+RT / DM / link)
- 🎁 and 👇 only
- Max 280 chars

Output ONLY the post text.`,

    ja: `以下のリソースで【配布型】のX投稿を作成してください: "{topic}"

ルール:
- 【配布】から始める
- 「欲しい人いますか？」を入れる
- 中身を3つ箇条書き（・で）
- 入手方法を明確に（フォロー+RT / DM）
- 🎁と👇のみ使用
- 280文字以内

投稿テキストのみ出力。`
  }
};

// Fill missing languages with English fallback
Object.keys(PROMPT_TEMPLATES).forEach(id => {
  ['cn','ko','es','ja'].forEach(lang => {
    if (!PROMPT_TEMPLATES[id][lang]) {
      PROMPT_TEMPLATES[id][lang] = PROMPT_TEMPLATES[id].en;
    }
  });
});
// Fill remaining patterns with a generic template
Object.keys(VIRAL_PATTERNS).forEach(id => {
  if (!PROMPT_TEMPLATES[id]) {
    PROMPT_TEMPLATES[id] = {
      en: `Generate a ${VIRAL_PATTERNS[id].name.en} style X/Twitter post about: "{topic}"\n\nStructure:\n${VIRAL_PATTERNS[id].structure}\n\nMax 280 chars. Output ONLY the post text.`,
      ja: `"{topic}"について【${VIRAL_PATTERNS[id].name.ja}】のX投稿を作成。\n\n構造:\n${VIRAL_PATTERNS[id].structure}\n\n280文字以内。投稿テキストのみ出力。`,
      cn: `以"{topic}"为主题生成【${VIRAL_PATTERNS[id].name.cn}】风格帖子。\n\n结构:\n${VIRAL_PATTERNS[id].structure}\n\n不超过280字。只输出帖子。`,
      ko: `"{topic}"에 대해 【${VIRAL_PATTERNS[id].name.ko}】 스타일 게시물 작성.\n\n구조:\n${VIRAL_PATTERNS[id].structure}\n\n280자 이내. 게시물만 출력.`,
      es: `Genera un post estilo 【${VIRAL_PATTERNS[id].name.es}】 sobre: "{topic}".\n\nEstructura:\n${VIRAL_PATTERNS[id].structure}\n\nMáx 280 chars. Solo el texto del post.`
    };
  }
});

/**
 * Build the prompt string for a given pattern + language
 */
function buildPrompt(patternId, topic, lang = 'en') {
  const tmpl = PROMPT_TEMPLATES[patternId];
  if (!tmpl) throw new Error(`Unknown pattern: ${patternId}`);
  const base = tmpl[lang] || tmpl.en;
  return base.replace(/\{topic\}/g, topic);
}

/**
 * Suggest best pattern for a topic string
 */
function suggestPattern(topic, lang = 'en') {
  const lc = topic.toLowerCase();
  const triggers = {
    '10-freebie':          [/free|配布|無料|免费|무료/],
    '01-breaking-news':    [/new|release|launch|速報|発表|突发|새출시/],
    '06-vs-battle':        [/ vs | versus |比較|比较|비교/],
    '02-save-for-later':   [/guide|tutorial|保存|指南|가이드/],
    '03-global-trend':     [/海外|global|trend|全球|해외/],
    '04-conclusion-first': [/conclusion|result|結論|结论|결론/],
    '08-by-numbers':       [/\d+%|\d+x |倍|数字/],
    '12-warning':          [/warn|注意|danger|警告|경고/],
    '13-storytelling':     [/story|journey|経験|故事|경험/],
    '15-future-forecast':  [/future|predict|未来|将来|미래/]
  };
  for (const [pid, regexps] of Object.entries(triggers)) {
    if (regexps.some(r => r.test(lc))) return pid;
  }
  return '04-conclusion-first';
}

/**
 * Generate a complete post object (prompt + metadata)
 * Call an LLM externally with result.prompt to get actual post text
 */
function generatePost(patternId, topic, lang = 'en', options = {}) {
  const pattern = VIRAL_PATTERNS[patternId];
  if (!pattern) throw new Error(`Unknown pattern: ${patternId}`);

  const prompt    = buildPrompt(patternId, topic, lang);
  const uid       = Buffer.from(`${patternId}:${topic}:${Date.now()}`).toString('base64').slice(0,10);
  const baseUrl   = options.baseUrl || 'https://vpa.opclaw.app';

  return {
    id:          uid,
    url:         `${baseUrl}/p/${uid}`,
    patternId,
    patternName: pattern.name[lang] || pattern.name.en,
    lang,
    topic,
    prompt,      // ← pass this to any LLM (OpenAI, Claude, etc.)
    structure:   pattern.structure,
    metadata: {
      maxLength:   options.maxLength || 280,
      platform:    options.platform  || 'x-twitter',
      generatedAt: new Date().toISOString()
    }
  };
}

module.exports = { generatePost, suggestPattern, buildPrompt, PROMPT_TEMPLATES, VIRAL_PATTERNS };
