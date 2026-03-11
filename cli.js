#!/usr/bin/env node
'use strict';
/**
 * Viral Post Automation — unified CLI
 * vpa analyze | generate | schedule | suggest | list | help
 */

const { analyzeData, VIRAL_PATTERNS } = require('./core/analyzer');
const { generatePost, suggestPattern }  = require('./core/generator');
const { addSchedule, loadSchedules, runAll, runDue } = require('./scheduler/daily');
const { t, LANGS }                      = require('./i18n');

const args    = process.argv.slice(2);
const command = args[0] || 'help';

const get = (flag) => {
  const i = args.indexOf(flag);
  return i !== -1 ? args[i + 1] : null;
};
const has = (flag) => args.includes(flag);

const lang = get('--lang') || get('-l') || 'en';

// ─── Help ────────────────────────────────────────────────────────────────────

function showHelp() {
  console.log(`
 ██╗   ██╗██████╗  █████╗     
 ██║   ██║██╔══██╗██╔══██╗    
 ██║   ██║██████╔╝███████║    
 ╚██╗ ██╔╝██╔═══╝ ██╔══██║    
  ╚████╔╝ ██║     ██║  ██║    
   ╚═══╝  ╚═╝     ╚═╝  ╚═╝   
  Viral Post Automation v2.0
  github.com/ichiko5963/OpClawX

Usage:
  vpa <command> [options]

Commands:
  analyze   -f <file.csv> [--lang ja]     Analyze your post data (CSV/JSON)
  generate  -p <pattern>  -t <topic>      Generate a post prompt
  schedule  --add --time 07:00 --topic X  Set up daily delivery
  schedule  --list                         View your schedules
  schedule  --run-due                      Run schedules due right now
  suggest   -t <topic>                    Get the best pattern for a topic
  list      --patterns | --schedules       List patterns or schedules
  help                                     Show this message

Flags:
  --lang, -l   Language: en ja cn ko es    (default: en, auto-detects from data)
  --pattern,-p Pattern ID (01-breaking-news … 15-future-forecast)
  --topic, -t  Your topic / theme
  --file, -f   Path to CSV or JSON file
  --webhook    Discord/Slack webhook URL
  --time       HH:MM for daily schedule
  --output,-o  Save analysis JSON to file

Examples:
  vpa analyze -f posts.csv --lang ja
  vpa generate -p 04-conclusion-first -t "AI is replacing jobs" --lang en
  vpa schedule --add --time 07:00 --lang ja --topic "AIニュース" --webhook https://…
  vpa suggest -t "product comparison"

Languages: ${LANGS.map(l => `${l.flag} ${l.code}(${l.name})`).join('  ')}
`);
}

// ─── Analyze ─────────────────────────────────────────────────────────────────

function cmdAnalyze() {
  const file   = get('-f') || get('--file') || args[1];
  const output = get('-o') || get('--output');

  if (!file) {
    console.error('❌  Please provide a file: vpa analyze -f posts.csv');
    process.exit(1);
  }

  console.log(`\n🔍  ${t(lang, 'analyzing')}\n`);

  try {
    const result = analyzeData(file, lang === 'auto' ? 'auto' : lang);

    console.log('═'.repeat(60));
    console.log(`✅  ${t(result.lang, 'analysisComplete')}`);
    console.log('═'.repeat(60));
    console.log(`\n📊  ${t(result.lang,'totalPosts')}: ${result.totalPosts}`);
    console.log(`🔎  Posts with detected patterns: ${result.detectedPosts}\n`);

    if (result.ranked.length === 0) {
      console.log('⚠️  No patterns detected. Try a different --lang or check your CSV format.');
    } else {
      console.log(`🏆  ${t(result.lang,'topPatterns')}:\n`);
      result.ranked.slice(0, 7).forEach((p, i) => {
        const name = p.name[result.lang] || p.name.en;
        console.log(`  ${i+1}. ${name.padEnd(22)} avg eng: ${String(p.avgEng).padStart(5)}  (${p.count} posts)`);
        if (p.topPosts[0]) {
          console.log(`     └── "${p.topPosts[0].text.slice(0, 70)}…"`);
        }
      });

      if (result.topPattern) {
        const top = result.topPattern;
        const name = top.name[result.lang] || top.name.en;
        console.log(`\n💡  Recommendation: Use the "${name}" pattern more often.`);
        console.log(`    Try: vpa generate -p ${top.id} -t "Your topic" --lang ${result.lang}`);
      }
    }

    if (output) {
      require('fs').writeFileSync(output, JSON.stringify(result, null, 2));
      console.log(`\n💾  ${t(result.lang,'savedTo')}: ${output}`);
    }

  } catch (err) {
    console.error(`❌  ${err.message}`);
    process.exit(1);
  }
}

// ─── Generate ────────────────────────────────────────────────────────────────

function cmdGenerate() {
  const patternId = get('-p') || get('--pattern');
  const topic     = get('-t') || get('--topic');

  if (!patternId || !topic) {
    console.error('❌  Usage: vpa generate -p <pattern-id> -t <topic>');
    console.log('    Example: vpa generate -p 04-conclusion-first -t "AI is replacing jobs" --lang en');
    process.exit(1);
  }

  try {
    const post = generatePost(patternId, topic, lang);

    console.log('\n' + '═'.repeat(60));
    console.log(`✨  ${t(lang,'generatedPost')}: ${post.patternName}`);
    console.log('═'.repeat(60));
    console.log('\n📋  PROMPT (paste into ChatGPT / Claude / Gemini):\n');
    console.log('┌' + '─'.repeat(58) + '┐');
    post.prompt.split('\n').forEach(l => console.log('│ ' + l.padEnd(57) + '│'));
    console.log('└' + '─'.repeat(58) + '┘');
    console.log(`\n🔗  ${t(lang,'postUrl')}: ${post.url}`);
    console.log(`📋  ${t(lang,'pattern')}: ${post.patternId}`);
    console.log(`🌍  Lang: ${post.lang}`);

  } catch (err) {
    console.error(`❌  ${err.message}`);
    process.exit(1);
  }
}

// ─── Schedule ────────────────────────────────────────────────────────────────

async function cmdSchedule() {
  if (has('--add')) {
    const id = addSchedule({
      time:      get('--time')    || '07:00',
      lang:      get('--lang') || get('-l') || 'ja',
      patternId: get('--pattern') || get('-p') || 'auto',
      topic:     get('--topic')   || get('-t') || 'AI News',
      delivery: {
        type:    get('--type')    || 'discord',
        webhook: get('--webhook'),
        baseUrl: get('--base-url')|| 'https://vpa.opclaw.app'
      }
    });
    console.log(`✅  ${t(lang,'scheduleAdded')}: ${id}`);
    console.log(`    Daily post will be delivered at ${get('--time')||'07:00'} every day.`);

  } else if (has('--list')) {
    const list = loadSchedules();
    if (list.length === 0) { console.log('No schedules yet.'); return; }
    console.log(`\n📅  ${t(lang,'schedules')}:\n`);
    list.forEach(s => {
      console.log(`  ${s.enabled ? '✅' : '⏸️ '} ${s.id}`);
      console.log(`     Time: ${s.time}  Lang: ${s.lang}  Pattern: ${s.patternId}`);
      console.log(`     Topic: ${s.topic}`);
      console.log(`     Webhook: ${s.delivery?.webhook || '(none)'}`);
      console.log('');
    });

  } else if (has('--run-due')) {
    await runDue();
  } else if (has('--run-all')) {
    await runAll();
  } else {
    console.log('Usage:\n  vpa schedule --add --time 07:00 --webhook <url>\n  vpa schedule --list\n  vpa schedule --run-due');
  }
}

// ─── Suggest ─────────────────────────────────────────────────────────────────

function cmdSuggest() {
  const topic = get('-t') || get('--topic') || args[1];
  if (!topic) { console.error('❌  Usage: vpa suggest -t "topic"'); process.exit(1); }

  const id      = suggestPattern(topic, lang);
  const pattern = VIRAL_PATTERNS[id];
  const name    = pattern.name[lang] || pattern.name.en;

  console.log(`\n💡  Best pattern for "${topic}":`);
  console.log(`    ${name} (${id})`);
  console.log(`    Engagement multiplier: ${pattern.weight}x`);
  console.log(`\n    Try:\n    vpa generate -p ${id} -t "${topic}" --lang ${lang}\n`);
}

// ─── List ────────────────────────────────────────────────────────────────────

function cmdList() {
  const type = get('--type') || get('-t') || 'patterns';

  if (type === 'patterns') {
    console.log('\n📚  15 Viral Patterns\n');
    Object.values(VIRAL_PATTERNS).forEach(p => {
      console.log(`  ${p.id}`);
      const names = LANGS.map(l => `${l.flag} ${p.name[l.code] || p.name.en}`).join('  ');
      console.log(`    ${names}`);
      console.log('');
    });
  } else if (type === 'schedules') {
    const list = loadSchedules();
    if (list.length === 0) { console.log('No schedules.'); return; }
    console.table(list.map(s => ({ id:s.id, enabled:s.enabled, time:s.time, lang:s.lang, topic:s.topic })));
  }
}

// ─── Router ──────────────────────────────────────────────────────────────────

(async () => {
  switch (command) {
    case 'analyze':
    case 'a':
      cmdAnalyze();
      break;
    case 'generate':
    case 'g':
      cmdGenerate();
      break;
    case 'schedule':
    case 's':
      await cmdSchedule();
      break;
    case 'suggest':
      cmdSuggest();
      break;
    case 'list':
    case 'l':
      cmdList();
      break;
    default:
      showHelp();
  }
})();
