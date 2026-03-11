#!/usr/bin/env node
/**
 * Viral Post Pattern Generator
 * OpenClaw Integration Script
 */

const fs = require('fs');
const path = require('path');

const PATTERNS_FILE = path.join(__dirname, '../patterns/patterns.json');
const PROMPTS_DIR = path.join(__dirname, '../prompts');

// パターンを読み込み
function loadPatterns() {
  const data = fs.readFileSync(PATTERNS_FILE, 'utf8');
  return JSON.parse(data);
}

// プロンプトテンプレートを読み込み
function loadPromptTemplate(patternId) {
  const promptFile = path.join(PROMPTS_DIR, `${patternId}.txt`);
  if (fs.existsSync(promptFile)) {
    return fs.readFileSync(promptFile, 'utf8');
  }
  return null;
}

// 投稿を生成
function generatePost(patternId, theme, platform = 'x-twitter') {
  const patterns = loadPatterns();
  const pattern = patterns.patterns.find(p => p.id === patternId);
  
  if (!pattern) {
    throw new Error(`Pattern ${patternId} not found`);
  }

  const template = loadPromptTemplate(patternId);
  if (!template) {
    throw new Error(`Prompt template for ${patternId} not found`);
  }

  // プロンプトにテーマを埋め込み
  const prompt = template.replace(/\{theme\}/g, theme);
  
  return {
    pattern: pattern,
    prompt: prompt,
    platform: platform,
    max_length: pattern.max_length
  };
}

// 最適なパターンを推奨
function suggestPattern(theme) {
  const patterns = loadPatterns();
  
  // テーマからキーワードを抽出して最適なパターンを選択
  const keywords = {
    '新': '01-breaking-news',
    '発表': '01-breaking-news',
    'まとめ': '02-save-for-later',
    '海外': '03-global-trend',
    '結論': '04-conclusion-first',
    '正直': '05-honest-opinion',
    '比較': '06-vs-battle',
    '体験': '07-first-impression',
    'データ': '08-by-numbers',
    '実は': '09-insight',
    '配布': '10-freebie',
    '裏技': '11-pro-tips',
    '注意': '12-warning',
    '話': '13-storytelling',
    '解説': '14-complete-guide',
    '未来': '15-future-forecast'
  };

  for (const [keyword, patternId] of Object.entries(keywords)) {
    if (theme.includes(keyword)) {
      return patterns.patterns.find(p => p.id === patternId);
    }
  }

  // デフォルトは結論型
  return patterns.patterns.find(p => p.id === '04-conclusion-first');
}

// CLI実行
if (require.main === module) {
  const args = process.argv.slice(2);
  const patternId = args.find(a => a.startsWith('--pattern='))?.split('=')[1];
  const theme = args.find(a => a.startsWith('--theme='))?.split('=')[1];
  const platform = args.find(a => a.startsWith('--platform='))?.split('=')[1] || 'x-twitter';
  const interactive = args.includes('--interactive');

  if (interactive) {
    console.log('🚀 Viral Post Pattern Generator - Interactive Mode\n');
    console.log('使用可能なパターン:');
    const patterns = loadPatterns();
    patterns.patterns.forEach(p => {
      console.log(`  ${p.id}: ${p.name}`);
    });
    console.log('\n使用例:');
    console.log('  openclaw run viral-post-patterns --pattern 01-breaking-news --theme "AI新機能"');
  } else if (patternId && theme) {
    try {
      const result = generatePost(patternId, theme, platform);
      console.log('📋 生成プロンプト:\n');
      console.log(result.prompt);
      console.log('\n---');
      console.log(`パターン: ${result.pattern.name}`);
      console.log(`推奨文字数: ${result.max_length}文字以内`);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  } else {
    console.log('Usage: generate.js --pattern=<id> --theme=<theme> [--platform=<platform>]');
    console.log('       generate.js --interactive');
  }
}

module.exports = { generatePost, suggestPattern, loadPatterns };
