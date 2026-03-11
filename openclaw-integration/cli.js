#!/usr/bin/env node
/**
 * Main CLI for Viral Post Automation / メインCLI
 */

const { analyzeData } = require('../core/analyzer');
const { generatePost, suggestPattern } = require('../core/generator');
const { Scheduler } = require('../scheduler/daily');
const { t, getLanguages } = require('../i18n');
const fs = require('fs');

const args = process.argv.slice(2);
const command = args[0];

function showHelp(lang = 'en') {
  console.log(`
🚀 Viral Post Automation / バズ投稿自動化

${t(lang, 'usage')}:
  vpa <command> [options]

${t(lang, 'commands')}:
  analyze, a      ${t(lang, 'analyzeData')}
  generate, g     ${t(lang, 'generatePost')}
  schedule, s     ${t(lang, 'dailySchedule')}
  list, l         ${t(lang, 'listSchedules')}
  suggest         ${t(lang, 'suggestPattern')}
  help, h         Show help

${t(lang, 'examples')}:
  vpa analyze ./posts.csv --lang ja
  vpa generate -p 01-breaking-news -t "AI News" --lang en
  vpa schedule --time "07:00" --webhook https://discord.com/api/webhooks/...
  vpa suggest -t "product comparison"

${t(lang, 'languages')}:
  ${getLanguages().map(l => `${l.code} (${l.name})`).join(', ')}
`);
}

async function handleAnalyze() {
  const fileIdx = args.findIndex(a => a === '--file' || a === '-f');
  const langIdx = args.findIndex(a => a === '--lang' || a === '-l');
  const outputIdx = args.findIndex(a => a === '--output' || a === '-o');
  
  const file = fileIdx !== -1 ? args[fileIdx + 1] : args[1];
  const lang = langIdx !== -1 ? args[langIdx + 1] : 'en';
  const output = outputIdx !== -1 ? args[outputIdx + 1] : null;
  
  if (!file) {
    console.error('Error: Please provide a file path');
    console.log('Usage: vpa analyze ./posts.csv');
    process.exit(1);
  }
  
  console.log(t(lang, 'analyzing'));
  
  try {
    const analysis = analyzeData(file, lang);
    
    console.log('\n' + '═'.repeat(60));
    console.log(t(lang, 'analysisComplete'));
    console.log('═'.repeat(60));
    
    console.log(`\n📊 ${t(lang, 'totalPosts')}: ${analysis.totalPosts}`);
    
    console.log(`\n🏆 ${t(lang, 'topPatterns')}:`);
    analysis.bestPerforming.forEach((p, i) => {
      console.log(`  ${i + 1}. ${p.patternInfo.name[lang]} (${p.id})`);
      console.log(`     ${t(lang, 'avgEngagement')}: ${Math.round(p.avgEngagement)}`);
      console.log(`     ${t(lang, 'used')}: ${p.count} ${t(lang, 'times')}`);
    });
    
    if (output) {
      fs.writeFileSync(output, JSON.stringify(analysis, null, 2));
      console.log(`\n💾 ${t(lang, 'savedTo')}: ${output}`);
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

async function handleGenerate() {
  const patternIdx = args.findIndex(a => a === '--pattern' || a === '-p');
  const topicIdx = args.findIndex(a => a === '--topic' || a === '-t');
  const langIdx = args.findIndex(a => a === '--lang' || a === '-l');
  const platformIdx = args.findIndex(a => a === '--platform');
  
  const patternId = patternIdx !== -1 ? args[patternIdx + 1] : null;
  const topic = topicIdx !== -1 ? args[topicIdx + 1] : null;
  const lang = langIdx !== -1 ? args[langIdx + 1] : 'en';
  const platform = platformIdx !== -1 ? args[platformIdx + 1] : 'x-twitter';
  
  if (!patternId || !topic) {
    console.error('Error: --pattern and --topic are required');
    console.log('Usage: vpa generate -p 01-breaking-news -t "Topic"');
    process.exit(1);
  }
  
  try {
    const post = generatePost(patternId, topic, lang, { platform });
    
    console.log('\n' + '═'.repeat(60));
    console.log(`✨ ${t(lang, 'generatedPost')}`);
    console.log('═'.repeat(60));
    console.log('\n' + post.content);
    console.log('─'.repeat(60));
    console.log(`\n📋 ${t(lang, 'pattern')}: ${post.patternName}`);
    console.log(`📊 ${t(lang, 'charCount')}: ${post.stats.charCount}`);
    console.log(`🔗 ${t(lang, 'postUrl')}: ${post.url}`);
    console.log(`\n📱 ${t(lang, 'platformCompatibility')}:`);
    Object.entries(post.platforms).forEach(([plat, info]) => {
      const status = info.compatible ? '✅' : '❌';
      console.log(`  ${status} ${plat}: ${info.maxLength} chars`);
    });
    
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

async function handleSchedule() {
  const scheduler = new Scheduler();
  
  if (args.includes('--add')) {
    const timeIdx = args.findIndex(a => a === '--time');
    const webhookIdx = args.findIndex(a => a === '--webhook');
    const patternIdx = args.findIndex(a => a === '--pattern');
    const topicIdx = args.findIndex(a => a === '--topic');
    const langIdx = args.findIndex(a => a === '--lang');
    
    const id = scheduler.addSchedule({
      time: timeIdx !== -1 ? args[timeIdx + 1] : '07:00',
      timezone: 'Asia/Tokyo',
      pattern: patternIdx !== -1 ? args[patternIdx + 1] : '04-conclusion-first',
      topic: topicIdx !== -1 ? args[topicIdx + 1] : 'Daily AI News',
      language: langIdx !== -1 ? args[langIdx + 1] : 'ja',
      delivery: {
        method: 'webhook',
        url: webhookIdx !== -1 ? args[webhookIdx + 1] : null,
        baseUrl: 'https://vpa.opclaw.app'
      }
    });
    
    console.log(`✅ Schedule created: ${id}`);
    console.log('Your daily posts will be generated and sent automatically!');
    
  } else if (args.includes('--list')) {
    const schedules = scheduler.listSchedules();
    console.log('\n📅 Scheduled Jobs:');
    schedules.forEach(s => {
      console.log(`  ${s.id}`);
      console.log(`    Time: ${s.time} (${s.timezone})`);
      console.log(`    Pattern: ${s.pattern}`);
      console.log(`    Topic: ${s.topic}`);
      console.log(`    Status: ${s.enabled ? '✅ Active' : '⏸️ Paused'}`);
      console.log('');
    });
    
  } else if (args.includes('--run')) {
    console.log('Running scheduled jobs...');
    await scheduler.run();
    console.log('Done!');
    
  } else {
    console.log('Usage:');
    console.log('  vpa schedule --add --time "07:00" --webhook <url>');
    console.log('  vpa schedule --list');
    console.log('  vpa schedule --run');
  }
}

async function handleSuggest() {
  const topicIdx = args.findIndex(a => a === '--topic' || a === '-t');
  const langIdx = args.findIndex(a => a === '--lang' || a === '-l');
  
  const topic = topicIdx !== -1 ? args[topicIdx + 1] : args[1];
  const lang = langIdx !== -1 ? args[langIdx + 1] : 'en';
  
  if (!topic) {
    console.error('Error: Please provide a topic');
    console.log('Usage: vpa suggest -t "your topic"');
    process.exit(1);
  }
  
  const patternId = suggestPattern(topic, lang);
  const { VIRAL_PATTERNS } = require('../core/analyzer');
  const pattern = VIRAL_PATTERNS[patternId];
  
  console.log('\n' + '═'.repeat(60));
  console.log(`💡 ${t(lang, 'suggestedPattern')}`);
  console.log('═'.repeat(60));
  console.log(`\n${t(lang, 'pattern')}: ${pattern.name[lang]} (${patternId})`);
  console.log(`${t(lang, 'weight')}: ${pattern.weight}x ${t(lang, 'engagement')}`);
  console.log(`\n${t(lang, 'tryCommand')}:`);
  console.log(`  vpa generate -p ${patternId} -t "${topic}" --lang ${lang}`);
}

function handleList() {
  const typeIdx = args.findIndex(a => a === '--type' || a === '-t');
  const type = typeIdx !== -1 ? args[typeIdx + 1] : 'patterns';
  
  if (type === 'patterns') {
    const { VIRAL_PATTERNS } = require('../core/analyzer');
    console.log('\n📚 15 Viral Patterns / 15のバズ型:\n');
    Object.values(VIRAL_PATTERNS).forEach(p => {
      console.log(`  ${p.id}`);
      console.log(`    EN: ${p.name.en}`);
      console.log(`    JP: ${p.name.ja}`);
      console.log(`    CN: ${p.name.cn}`);
      console.log(`    Weight: ${p.weight}x`);
      console.log('');
    });
  }
}

// Main / メイン
(async () => {
  switch (command) {
    case 'analyze':
    case 'a':
      await handleAnalyze();
      break;
    case 'generate':
    case 'g':
      await handleGenerate();
      break;
    case 'schedule':
    case 's':
      await handleSchedule();
      break;
    case 'suggest':
      await handleSuggest();
      break;
    case 'list':
    case 'l':
      handleList();
      break;
    case 'help':
    case 'h':
    default:
      showHelp();
      break;
  }
})();
