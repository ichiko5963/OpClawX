/**
 * Core Analyzer — 15 Viral Pattern Detection Engine + Custom Patterns + X Premium Support
 * Numbers/CSV/JSON/X Premium → pattern analysis → engagement scoring
 */

const fs = require('fs');
const path = require('path');

// ─── Load custom patterns if exist ────────────────────────────────────────────

const CUSTOM_PATTERNS_PATH = path.join(__dirname, '../config/patterns.json');
let CUSTOM_PATTERNS = {};

function loadCustomPatterns() {
  if (fs.existsSync(CUSTOM_PATTERNS_PATH)) {
    try {
      const raw = JSON.parse(fs.readFileSync(CUSTOM_PATTERNS_PATH, 'utf8'));
      // Remove metadata fields
      const cleaned = {};
      Object.entries(raw).forEach(([k, v]) => {
        if (!k.startsWith('_')) cleaned[k] = v;
      });
      console.log(`[analyzer] Loaded ${Object.keys(cleaned).length} custom patterns from config/patterns.json`);
      return cleaned;
    } catch(e) {
      console.warn('[analyzer] Failed to load custom patterns:', e.message);
    }
  }
  return {};
}

// ─── Built-in 15 Viral Patterns ──────────────────────────────────────────────

const BUILTIN_PATTERNS = {
  '01-breaking-news': {
    id: '01-breaking-news',
    name: { en: 'Breaking News', ja: '速報型', cn: '突发新闻', ko: '속보형', es: 'Noticia Urgente' },
    indicators: ['【速報】','【Breaking】','ついに','Finally','速報','Breaking'],
    keywords: {
      en: ['breaking','released','launched','finally','just announced','new'],
      ja: ['速報','ついに','登場','リリース','発表','新しい'],
      cn: ['突发','终于','发布','推出','最新'],
      ko: ['속보','드디어','출시','발표'],
      es: ['último minuto','finalmente','lanzado','anunciado']
    },
    structure: '【Hook】Topic + Finally/ついに/终于 🔥\n・Point 1\n・Point 2\n・Point 3\nCTA 👇',
    weight: 1.8
  },
  '02-save-for-later': {
    id: '02-save-for-later',
    name: { en: 'Save for Later', ja: '保存版型', cn: '收藏版', ko: '저장형', es: 'Guardar para Después' },
    indicators: ['【保存版】','📌','Save this','Bookmark','保存推奨'],
    keywords: {
      en: ['save','bookmark','complete guide','ultimate','checklist'],
      ja: ['保存版','まとめ','完全','チェックリスト','保存推奨'],
      cn: ['收藏','完整指南','清单','建议保存'],
      ko: ['저장','완전가이드','체크리스트'],
      es: ['guardar','guía completa','lista de verificación']
    },
    structure: '【保存版/Save】Topic Guide 📌\n・Step/Point 1\n・Step/Point 2\n・Step/Point 3\nCTA 👇',
    weight: 2.5
  },
  '03-global-trend': {
    id: '03-global-trend',
    name: { en: 'Global Trend', ja: '海外バズ型', cn: '全球趋势', ko: '글로벌트렌드', es: 'Tendencia Global' },
    indicators: ['【海外で話題】','Trending worldwide','海外バズ','🌎'],
    keywords: {
      en: ['trending','worldwide','global','overseas','buzz','viral'],
      ja: ['海外で話題','海外バズ','グローバル','世界が注目','海外で注目'],
      cn: ['海外热议','全球趋势','国际上','全世界'],
      ko: ['해외에서화제','글로벌','세계적'],
      es: ['tendencia global','mundial','internacional']
    },
    structure: '【海外で話題/Trending】Topic 🌎\n海外の反応/Reaction👇\n・Use case 1\n・Use case 2\nCTA 👇',
    weight: 1.5
  },
  '04-conclusion-first': {
    id: '04-conclusion-first',
    name: { en: 'Conclusion First', ja: '結論型', cn: '结论先行', ko: '결론형', es: 'Conclusión Primero' },
    indicators: ['【結論】','Conclusion:','結論','TL;DR','要するに'],
    keywords: {
      en: ['conclusion','summary','bottom line','result','answer'],
      ja: ['結論','要するに','まとめると','つまり','答え'],
      cn: ['结论','总结','简而言之','答案'],
      ko: ['결론','요약','정리'],
      es: ['conclusión','en resumen','resultado']
    },
    structure: '【結論/Conclusion】Statement 💡\n理由/Reasons👇\n・Reason 1\n・Reason 2\n・Reason 3\nCTA 👇',
    weight: 2.0
  },
  '05-honest-opinion': {
    id: '05-honest-opinion',
    name: { en: 'Honest Opinion', ja: '正直型', cn: '诚实观点', ko: '솔직한의견', es: 'Opinión Honesta' },
    indicators: ['正直','Honestly','Real talk','本音','ぶっちゃけ'],
    keywords: {
      en: ['honestly','truth','real talk','confession','candid'],
      ja: ['正直','本音','リアル','ぶっちゃけ','実際のところ'],
      cn: ['老实说','说实话','真心话','坦白说'],
      ko: ['솔직히','진심으로','사실은'],
      es: ['honestamente','la verdad','siendo sincero']
    },
    structure: '正直/Honestly, Statement...\n理由/Because👇\n・Context\n・Why it matters\nConclusion 👇',
    weight: 1.4
  },
  '06-vs-battle': {
    id: '06-vs-battle',
    name: { en: 'VS Battle', ja: '比較型', cn: '对决', ko: '비교형', es: 'VS Batalla' },
    indicators: [' vs ',' VS ','⚔️','【頂上決戦】','徹底比較'],
    keywords: {
      en: ['vs','versus','comparison','battle','which is better'],
      ja: ['vs','比較','どっち','対決','頂上決戦'],
      cn: ['对比','vs','哪个','对决','比较'],
      ko: ['vs','비교','어느쪽','대결'],
      es: ['vs','versus','comparación','batalla']
    },
    structure: '【VS/頂上決戦】A vs B ⚔️\nA strengths:\n・Point 1\nB strengths:\n・Point 1\n結論/Verdict👇',
    weight: 1.5
  },
  '07-first-impression': {
    id: '07-first-impression',
    name: { en: 'First Impression', ja: '体験記型', cn: '第一印象', ko: '첫인상형', es: 'Primera Impresión' },
    indicators: ['使ってみた','Tried','I tested','体験','First look'],
    keywords: {
      en: ['tried','tested','review','used it','first look','impression'],
      ja: ['使ってみた','体験','レビュー','感想','試した'],
      cn: ['试用','体验','测评','使用感受'],
      ko: ['사용해봤다','체험','리뷰','써봤어'],
      es: ['probé','reseña','primera impresión','experiencia']
    },
    structure: '【体験/Tried】Topic using Tool\n期待/Expected vs 実際/Reality👇\n・Point 1\n・Surprise\n総評/Verdict👇',
    weight: 1.3
  },
  '08-by-numbers': {
    id: '08-by-numbers',
    name: { en: 'By The Numbers', ja: '数字強調型', cn: '数字强调', ko: '숫자강조형', es: 'En Números' },
    indicators: ['📊','%','倍','×','x faster','x more'],
    keywords: {
      en: ['percent','times faster','increased','decreased','statistics','data'],
      ja: ['倍','パーセント','データ','統計','向上','削減'],
      cn: ['倍','百分比','数据','统计','提升','减少'],
      ko: ['배','퍼센트','데이터','통계','향상'],
      es: ['por ciento','veces más','datos','estadísticas']
    },
    structure: '【数字/Numbers】Topic — shocking data📊\n・Stat 1: XX%\n・Stat 2: XXx\n・Stat 3: XX min\n意味/Meaning👇',
    weight: 1.6
  },
  '09-insight': {
    id: '09-insight',
    name: { en: 'Insight', ja: '洞察型', cn: '洞察', ko: '통찰형', es: 'Perspectiva' },
    indicators: ['実は','Actually','The truth is','秘密','Secret'],
    keywords: {
      en: ['actually','secret','truth','real reason','behind the scenes'],
      ja: ['実は','裏話','真実','本質','知られていない'],
      cn: ['其实','真相','背后','秘密','鲜为人知'],
      ko: ['사실은','비밀','진실','숨겨진'],
      es: ['en realidad','la verdad','detrás de escenas','secreto']
    },
    structure: '実は/Actually, [Common belief] is wrong.\n本当は/The truth👇\n・Real point 1\n・Real point 2\nImplication👇',
    weight: 1.5
  },
  '10-freebie': {
    id: '10-freebie',
    name: { en: 'Free Resource', ja: '配布型', cn: '免费资源', ko: '무료배포형', es: 'Recurso Gratuito' },
    indicators: ['【配布】','Free','🎁','Giveaway','欲しい人','無料'],
    keywords: {
      en: ['free','giveaway','template','download','grab','get'],
      ja: ['配布','無料','プレゼント','テンプレート','欲しい人'],
      cn: ['免费','赠品','模板','下载','获取'],
      ko: ['무료','배포','템플릿','다운로드'],
      es: ['gratis','plantilla','descarga','obtén']
    },
    structure: '【配布/Free】Resource name — want it?🎁\n中身/Contents:\n・Item 1\n・Item 2\n入手方法/How to get 👇',
    weight: 3.0
  },
  '11-pro-tips': {
    id: '11-pro-tips',
    name: { en: 'Pro Tips', ja: '裏技型', cn: '专业技巧', ko: '프로팁형', es: 'Consejos Pro' },
    indicators: ['裏技','Tips','💎','Pro tip','知ってると差がつく'],
    keywords: {
      en: ['tip','hack','trick','pro','advanced','level up'],
      ja: ['裏技','コツ','知ってると差','プロ技','上級'],
      cn: ['技巧','窍门','高手','进阶'],
      ko: ['팁','비법','프로','고급'],
      es: ['consejo','truco','avanzado','pro']
    },
    structure: '知ってると差がつく/Pro tip: Topic💎\n手順/Steps👇\n① Step 1\n② Step 2\n③ Step 3\n効果/Result👇',
    weight: 1.4
  },
  '12-warning': {
    id: '12-warning',
    name: { en: 'Warning', ja: '警告型', cn: '警告', ko: '경고형', es: 'Advertencia' },
    indicators: ['⚠️','【注意】','Warning','危険','注意'],
    keywords: {
      en: ['warning','caution','watch out','danger','alert','avoid'],
      ja: ['注意','警告','危険','気をつけて','要注意'],
      cn: ['警告','注意','危险','小心','避免'],
      ko: ['경고','주의','위험','조심'],
      es: ['advertencia','cuidado','peligro','evitar']
    },
    structure: '⚠️ Warning: Topic\n問題/Problem👇\n・Risk 1\n・Risk 2\n対策/Solution👇',
    weight: 1.7
  },
  '13-storytelling': {
    id: '13-storytelling',
    name: { en: 'Storytelling', ja: 'ストーリー型', cn: '故事型', ko: '스토리텔링형', es: 'Narrativa' },
    indicators: ['だった私が','I used to','From zero','から始まった','Journey'],
    keywords: {
      en: ['story','journey','used to','became','transformed','went from'],
      ja: ['だった','から','変わった','なった','経験','話'],
      cn: ['曾经','变成','故事','经历','从零到'],
      ko: ['이었던내가','변했어','스토리','경험'],
      es: ['solía','me convertí','historia','transformé']
    },
    structure: '[状況/Was]: X.\n[変化/Then]: Y happened.\n[今/Now]: Z.\n学び/Lesson👇',
    weight: 1.2
  },
  '14-complete-guide': {
    id: '14-complete-guide',
    name: { en: 'Complete Guide', ja: '完全解説型', cn: '完整指南', ko: '완전가이드형', es: 'Guía Completa' },
    indicators: ['完全','Complete guide','Ultimate','これだけ読めば','徹底解説'],
    keywords: {
      en: ['complete','ultimate','everything you need','master','comprehensive'],
      ja: ['完全','徹底','これだけ','マスター','全て'],
      cn: ['完整','终极','掌握','全面','一站式'],
      ko: ['완전','마스터','모든것','종합'],
      es: ['completo','definitivo','todo lo que necesitas','domina']
    },
    structure: '【Complete/完全】Topic — everything in one thread📚\n① Basics\n② Intermediate\n③ Advanced\n読むべき理由/Why read 👇',
    weight: 1.8
  },
  '15-future-forecast': {
    id: '15-future-forecast',
    name: { en: 'Future Forecast', ja: '予測型', cn: '未来预测', ko: '미래예측형', es: 'Pronóstico Futuro' },
    indicators: ['年後','In X years','Future','予測','Coming soon'],
    keywords: {
      en: ['future','predict','will be','years from now','coming','trend'],
      ja: ['未来','予測','年後','なる','来る','変わる'],
      cn: ['未来','预测','年后','将来','即将'],
      ko: ['미래','예측','년후','될것','다가오는'],
      es: ['futuro','predicción','años desde ahora','será','tendencia']
    },
    structure: 'X年後/years from now, Topic will [change].\n根拠/Evidence👇\n・Sign 1\n・Sign 2\n今すぐやること/Act now👇',
    weight: 1.4
  }
};

// ─── CSV/JSON loading ────────────────────────────────────────────────────────

function loadFile(filePath) {
  if (!fs.existsSync(filePath)) throw new Error(`File not found: ${filePath}`);
  const ext = path.extname(filePath).toLowerCase();
  if (ext === '.json') return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  if (ext === '.csv')  return fs.readFileSync(filePath, 'utf8');
  throw new Error(`Unsupported format: ${ext}. Use .csv or .json`);
}

// ─── X Premium / Standard column name mapping ─────────────────────────────────

const COLUMN_ALIASES = {
  // X Premium standard names
  'tweet_text': 'text',
  'tweet_created_at': 'date',
  'impressions': 'impressions',
  'engagements': 'engagements',
  'likes': 'likes',
  'retweets': 'retweets',
  'replies': 'replies',
  'bookmarks': 'bookmarks',
  'quotes': 'quotes',
  // Alternative names
  'content': 'text',
  'post': 'text',
  'created_at': 'date',
  'posted_at': 'date',
  'favorites': 'likes',
  'favs': 'likes',
  'rts': 'retweets',
  'shares': 'retweets',
  'comments': 'replies',
  'saves': 'bookmarks',
  'views': 'impressions'
};

function normalizeColumnName(h) {
  const clean = h.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
  return COLUMN_ALIASES[clean] || clean;
}

function parseCSV(raw) {
  const lines = raw.trim().split('\n').filter(Boolean);
  if (lines.length < 2) throw new Error('CSV must have a header row + at least one data row');
  
  // Handle quoted fields
  const parseRow = (line) => {
    const fields = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      if (line[i] === '"') { inQuotes = !inQuotes; continue; }
      if (line[i] === ',' && !inQuotes) { fields.push(current.trim()); current = ''; continue; }
      current += line[i];
    }
    fields.push(current.trim());
    return fields;
  };

  const headers = parseRow(lines[0]).map(h => normalizeColumnName(h));
  
  // Detect if this is X Premium format
  const isXPremium = headers.includes('impressions') && headers.includes('engagements');
  if (isXPremium) {
    console.log('[analyzer] Detected X Premium analytics format');
  }

  return lines.slice(1).map(line => {
    const vals = parseRow(line);
    const obj = {};
    headers.forEach((h, i) => {
      const v = vals[i] || '';
      // Numeric fields
      if (['likes','retweets','replies','shares','comments','impressions','bookmarks','engagements','quotes']
        .includes(h)) {
        obj[h] = parseInt(v.replace(/,/g, '')) || 0;
      } else {
        obj[h] = v;
      }
    });
    return obj;
  }).filter(p => p.text && p.text.length > 0);
}

// ─── Pattern detection ───────────────────────────────────────────────────────

function getAllPatterns() {
  // Merge built-in and custom patterns at runtime
  return { ...BUILTIN_PATTERNS, ...CUSTOM_PATTERNS };
}

function detectPatterns(text, lang = 'en') {
  const detected = [];
  if (!text) return detected;

  const allPatterns = getAllPatterns();
  Object.values(allPatterns).forEach(pattern => {
    // Indicator match (strong signal)
    const indicatorHit = pattern.indicators.some(ind =>
      text.toLowerCase().includes(ind.toLowerCase())
    );

    // Keyword match (weak signal, need 2+)
    const keys = pattern.keywords[lang] || pattern.keywords.en;
    const kwHits = keys.filter(k => text.toLowerCase().includes(k.toLowerCase())).length;

    if (indicatorHit || kwHits >= 2) detected.push(pattern.id);
  });

  return detected;
}

function calcEngagement(post) {
  // X Premium analytics: use engagements if available, otherwise calculate
  if (post.engagements) {
    return post.engagements;
  }
  // Weighted: reply > retweet > like > impression
  return (
    (post.likes      || 0) * 1   +
    (post.retweets   || post.shares || 0) * 2 +
    (post.replies    || post.comments || 0) * 3 +
    (post.bookmarks  || 0) * 2   +
    (post.quotes     || 0) * 2   +
    (post.impressions|| 0) * 0.01
  );
}

function autoDetectLang(posts) {
  const sample = posts.slice(0, 20).map(p => p.text || '').join(' ');
  if (/[\u3040-\u30FF]/.test(sample)) return 'ja';
  if (/[\u4E00-\u9FFF]/.test(sample) && !(/[\u3040-\u30FF]/.test(sample))) return 'cn';
  if (/[\uAC00-\uD7AF]/.test(sample)) return 'ko';
  if (/[áéíóúñ]/.test(sample)) return 'es';
  return 'en';
}

// ─── Main analysis ───────────────────────────────────────────────────────────

function analyzeData(filePath, lang = 'auto') {
  const raw   = loadFile(filePath);
  const posts = Array.isArray(raw) ? raw : parseCSV(raw);

  if (lang === 'auto') lang = autoDetectLang(posts);

  const patternStats = {};
  const topPostsByPattern = {};

  posts.forEach(post => {
    const eng      = calcEngagement(post);
    const patterns = detectPatterns(post.text, lang);

    patterns.forEach(pid => {
      if (!patternStats[pid]) {
        patternStats[pid] = { count: 0, totalEng: 0, posts: [] };
      }
      patternStats[pid].count++;
      patternStats[pid].totalEng += eng;
      if (patternStats[pid].posts.length < 5) {
        patternStats[pid].posts.push({ text: post.text, eng, date: post.date || '' });
      }
    });
  });

  // Build ranked result
  const allPatterns = getAllPatterns();
  const ranked = Object.entries(patternStats)
    .map(([pid, s]) => ({
      id: pid,
      name: allPatterns[pid]?.name || {},
      count: s.count,
      avgEng: Math.round(s.totalEng / s.count),
      topPosts: s.posts.sort((a,b) => b.eng - a.eng).slice(0, 3)
    }))
    .sort((a, b) => b.avgEng - a.avgEng);

  return {
    lang,
    totalPosts: posts.length,
    detectedPosts: posts.filter(p => detectPatterns(p.text, lang).length > 0).length,
    ranked,
    topPattern: ranked[0] || null,
    timestamp: new Date().toISOString()
  };
}

// ─── Export with custom pattern merge ────────────────────────────────────────

// Load custom patterns and merge with built-in
CUSTOM_PATTERNS = loadCustomPatterns();
const ALL_PATTERNS = { ...BUILTIN_PATTERNS, ...CUSTOM_PATTERNS };

// Ensure all patterns have ID field
Object.keys(ALL_PATTERNS).forEach(k => {
  ALL_PATTERNS[k].id = k;
});

module.exports = { analyzeData, detectPatterns, calcEngagement, VIRAL_PATTERNS: ALL_PATTERNS };
