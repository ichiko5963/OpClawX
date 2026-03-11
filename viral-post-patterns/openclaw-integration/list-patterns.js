#!/usr/bin/env node
/**
 * List all available patterns
 */

const { loadPatterns } = require('./generate.js');

const patterns = loadPatterns();

console.log('\n📚 Viral Post Patterns - バズる投稿15型\n');
console.log('─'.repeat(60));

patterns.patterns.forEach((p, index) => {
  console.log(`\n${(index + 1).toString().padStart(2, '0')}. ${p.name} (${p.id})`);
  console.log(`    ${p.psychology}`);
  console.log(`    Keywords: ${p.trigger_keywords.join(', ')}`);
  console.log(`    Max Length: ${p.max_length} chars`);
});

console.log('\n' + '─'.repeat(60));
console.log(`\nTotal: ${patterns.patterns.length} patterns\n`);
console.log('Usage:');
console.log('  openclaw run viral-post-patterns --pattern <id> --theme <subject>');
console.log('  viral-post generate -p <id> -t <subject>\n');
