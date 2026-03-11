/**
 * Basic smoke tests
 */

const { analyzeData, detectPatterns, VIRAL_PATTERNS } = require('../core/analyzer');
const { generatePost, suggestPattern }                 = require('../core/generator');
const { t, detectLang }                                = require('../i18n');
const fs   = require('fs');
const path = require('path');

let passed = 0;
let failed = 0;

function assert(desc, fn) {
  try {
    fn();
    console.log(`  ✅  ${desc}`);
    passed++;
  } catch(e) {
    console.log(`  ❌  ${desc}: ${e.message}`);
    failed++;
  }
}

function assertEqual(a, b) {
  if (a !== b) throw new Error(`Expected "${b}", got "${a}"`);
}

function assertContains(arr, val) {
  if (!arr.includes(val)) throw new Error(`Expected array to contain "${val}", got [${arr.join(', ')}]`);
}

// ─── Tests ───────────────────────────────────────────────────────────────────

console.log('\n🧪  Viral Post Automation — Tests\n');

console.log('[ VIRAL_PATTERNS ]');
assert('Has 15 patterns', () => {
  if (Object.keys(VIRAL_PATTERNS).length !== 15)
    throw new Error(`Expected 15, got ${Object.keys(VIRAL_PATTERNS).length}`);
});
assert('Each pattern has 5 language names', () => {
  Object.values(VIRAL_PATTERNS).forEach(p => {
    ['en','ja','cn','ko','es'].forEach(l => {
      if (!p.name[l]) throw new Error(`${p.id} missing name.${l}`);
    });
  });
});

console.log('\n[ detectPatterns ]');
assert('Detects breaking-news in Japanese', () => {
  const r = detectPatterns('【速報】ChatGPTがついに登場！', 'ja');
  assertContains(r, '01-breaking-news');
});
assert('Detects freebie in English', () => {
  const r = detectPatterns('【Free】Templates — want them? 🎁 Follow+RT', 'en');
  assertContains(r, '10-freebie');
});
assert('Detects conclusion in English', () => {
  const r = detectPatterns('Conclusion: AI tools will replace repetitive jobs.', 'en');
  assertContains(r, '04-conclusion-first');
});

console.log('\n[ generatePost ]');
assert('Returns object with prompt', () => {
  const p = generatePost('01-breaking-news', 'ChatGPT Update', 'en');
  if (!p.prompt || p.prompt.length < 10) throw new Error('Empty prompt');
});
assert('Prompt contains topic', () => {
  const topic = 'AI Revolution 2026';
  const p = generatePost('04-conclusion-first', topic, 'ja');
  if (!p.prompt.includes(topic)) throw new Error('Topic not in prompt');
});
assert('Has url and id', () => {
  const p = generatePost('10-freebie', 'Templates', 'en');
  if (!p.url.startsWith('https://')) throw new Error('No URL');
  if (!p.id) throw new Error('No ID');
});

console.log('\n[ suggestPattern ]');
assert('Suggests freebie for "free templates"', () => assertEqual(suggestPattern('free templates'), '10-freebie'));
assert('Suggests vs-battle for "A vs B"', () => assertEqual(suggestPattern('ChatGPT vs Claude'), '06-vs-battle'));
assert('Suggests breaking-news for "new release"', () => assertEqual(suggestPattern('new release today'), '01-breaking-news'));

console.log('\n[ i18n ]');
assert('t() returns Japanese string', () => {
  const name = t('ja', 'patternNames.01-breaking-news');
  assertEqual(name, '速報型');
});
assert('detectLang detects Japanese', () => assertEqual(detectLang('これはテストです'), 'ja'));
assert('detectLang detects Chinese', () => assertEqual(detectLang('这是一个测试'), 'cn'));
assert('detectLang defaults to English', () => assertEqual(detectLang('This is a test'), 'en'));

console.log('\n[ analyzeData — CSV ]');
const SAMPLE_CSV = 'text,likes,retweets,replies,date\n' +
  '"【速報】AIついに登場！",200,80,30,"2026-01-01"\n' +
  '"【保存版】まとめ📌",150,60,20,"2026-01-02"\n' +
  '"正直、これは難しい",80,20,15,"2026-01-03"';
const tmpFile = path.join(__dirname, '.tmp_test.csv');
fs.writeFileSync(tmpFile, SAMPLE_CSV);
assert('Analyzes CSV correctly', async () => {
  const r = await analyzeData(tmpFile, 'ja');
  if (r.totalPosts !== 3) throw new Error(`Expected 3 posts, got ${r.totalPosts}`);
  if (!r.ranked.length) throw new Error('No patterns detected');
});
fs.unlinkSync(tmpFile);

// ─── Summary ──────────────────────────────────────────────────────────────────

console.log(`\n${'─'.repeat(40)}`);
console.log(`Total: ${passed+failed}  ✅ ${passed}  ❌ ${failed}`);
if (failed > 0) process.exit(1);
