#!/usr/bin/env node
/**
 * Viral Post Patterns - CLI Tool
 */

const { generatePost, suggestPattern, loadPatterns } = require('../openclaw-integration/generate.js');

const args = process.argv.slice(2);
const command = args[0];

function showHelp() {
  console.log(`
🚀 Viral Post Patterns - CLI

Usage:
  viral-post <command> [options]

Commands:
  generate, g    Generate a post using a pattern
  list, l        List all available patterns
  suggest, s     Suggest a pattern for your theme
  help, h        Show this help message

Options for generate:
  --pattern, -p   Pattern ID (e.g., 01-breaking-news)
  --theme, -t     Post theme/subject
  --platform      Target platform (x-twitter, instagram, linkedin, note)

Examples:
  viral-post generate -p 01-breaking-news -t "AI新機能"
  viral-post suggest -t "製品比較"
  viral-post list
`);
}

function handleGenerate() {
  const patternIdx = args.findIndex(a => a === '--pattern' || a === '-p');
  const themeIdx = args.findIndex(a => a === '--theme' || a === '-t');
  const platformIdx = args.findIndex(a => a === '--platform');
  
  const patternId = patternIdx !== -1 ? args[patternIdx + 1] : null;
  const theme = themeIdx !== -1 ? args[themeIdx + 1] : null;
  const platform = platformIdx !== -1 ? args[platformIdx + 1] : 'x-twitter';

  if (!patternId || !theme) {
    console.error('Error: --pattern and --theme are required');
    console.log('Usage: viral-post generate -p <pattern> -t <theme>');
    process.exit(1);
  }

  try {
    const result = generatePost(patternId, theme, platform);
    console.log('\n📝 Generated Prompt:\n');
    console.log('─'.repeat(50));
    console.log(result.prompt);
    console.log('─'.repeat(50));
    console.log(`\n📊 Pattern: ${result.pattern.name}`);
    console.log(`📱 Platform: ${platform}`);
    console.log(`📝 Max Length: ${result.max_length} chars`);
    console.log(`\n💡 Tips: Use 🔥 for emphasis, 👇 for CTA`);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

function handleList() {
  const patterns = loadPatterns();
  console.log('\n📚 Available Patterns:\n');
  patterns.patterns.forEach(p => {
    console.log(`  ${p.id.padEnd(20)} ${p.name}`);
    console.log(`                      ${p.psychology.substring(0, 40)}...`);
    console.log('');
  });
}

function handleSuggest() {
  const themeIdx = args.findIndex(a => a === '--theme' || a === '-t');
  const theme = themeIdx !== -1 ? args[themeIdx + 1] : null;

  if (!theme) {
    console.error('Error: --theme is required');
    console.log('Usage: viral-post suggest -t <theme>');
    process.exit(1);
  }

  const pattern = suggestPattern(theme);
  console.log(`\n💡 Suggested Pattern for "${theme}":`);
  console.log(`   ${pattern.id}: ${pattern.name}`);
  console.log(`   ${pattern.psychology}`);
  console.log(`\n   Try: viral-post generate -p ${pattern.id} -t "${theme}"`);
}

// Main
switch (command) {
  case 'generate':
  case 'g':
    handleGenerate();
    break;
  case 'list':
  case 'l':
    handleList();
    break;
  case 'suggest':
  case 's':
    handleSuggest();
    break;
  case 'help':
  case 'h':
  default:
    showHelp();
    break;
}
