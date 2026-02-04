#!/usr/bin/env node
/**
 * X Post Analyzer
 * Analyzes tweet structure and suggests improvements
 * Usage: node x-post-analyzer.js "tweet content"
 */

const content = process.argv[2];

if (!content) {
    console.log('Usage: node x-post-analyzer.js "tweet content"');
    process.exit(1);
}

// Analysis functions
function countChars(text) {
    return text.length;
}

function countLines(text) {
    return text.split('\n').length;
}

function detectElements(text) {
    const elements = [];
    
    // Emoji detection
    const emojiRegex = /[\u{1F300}-\u{1F9FF}]/gu;
    const emojis = text.match(emojiRegex) || [];
    if (emojis.length > 0) elements.push(`絵文字: ${emojis.length}個`);
    
    // Hashtag detection
    const hashtags = text.match(/#\w+/g) || [];
    if (hashtags.length > 0) elements.push(`ハッシュタグ: ${hashtags.join(', ')}`);
    
    // URL detection
    const urls = text.match(/https?:\/\/[^\s]+/g) || [];
    if (urls.length > 0) elements.push(`URL: ${urls.length}個`);
    
    // Bullet points
    const bullets = text.match(/^[\s]*[・•\-]/gm) || [];
    if (bullets.length > 0) elements.push(`箇条書き: ${bullets.length}項目`);
    
    // Numbers/steps
    const numbers = text.match(/^[\s]*[①②③④⑤⑥⑦⑧⑨⑩\d\.]/gm) || [];
    if (numbers.length > 0) elements.push(`ナンバリング: ${numbers.length}項目`);
    
    return elements;
}

function analyzeStructure(text) {
    const lines = text.split('\n').filter(l => l.trim());
    const structure = [];
    
    // First line as headline
    if (lines[0]) {
        if (lines[0].includes('【') || lines[0].includes('「')) {
            structure.push('✅ 強い見出しで開始');
        } else {
            structure.push('💡 【】や「」で見出しを強調すると効果的');
        }
    }
    
    // Check for problem/solution structure
    if (text.includes('でも') || text.includes('しかし') || text.includes('ただ')) {
        structure.push('✅ 転換点あり（ストーリー構造）');
    }
    
    // CTA check
    if (text.includes('👇') || text.includes('こちら') || text.includes('https')) {
        structure.push('✅ CTA（行動喚起）あり');
    } else {
        structure.push('💡 最後にCTAを追加すると反応率UP');
    }
    
    // Readability
    if (text.includes('\n\n')) {
        structure.push('✅ 適切な空白行あり（読みやすい）');
    } else {
        structure.push('💡 段落間に空白行を入れると読みやすい');
    }
    
    return structure;
}

function suggestImprovements(text) {
    const suggestions = [];
    const charCount = countChars(text);
    
    if (charCount < 100) {
        suggestions.push('📝 もう少し内容を追加すると良いかも（100文字以上推奨）');
    } else if (charCount > 280) {
        suggestions.push('⚠️ 280文字超過 - スレッド形式を検討');
    }
    
    if (!text.includes('。') && !text.includes('！') && !text.includes('？')) {
        suggestions.push('📝 句読点を追加すると読みやすくなります');
    }
    
    const emojiCount = (text.match(/[\u{1F300}-\u{1F9FF}]/gu) || []).length;
    if (emojiCount === 0) {
        suggestions.push('😀 絵文字を1-2個追加すると目を引きやすい');
    } else if (emojiCount > 5) {
        suggestions.push('⚠️ 絵文字が多すぎるかも（3-4個が適切）');
    }
    
    return suggestions;
}

// Main analysis
console.log('\n═══════════════════════════════════════════');
console.log('        📊 X投稿 分析レポート');
console.log('═══════════════════════════════════════════\n');

console.log('📝 投稿内容:');
console.log('─────────────────────────────────────────');
console.log(content);
console.log('─────────────────────────────────────────\n');

console.log('📈 基本情報:');
console.log(`  文字数: ${countChars(content)} / 280`);
console.log(`  行数: ${countLines(content)}`);
console.log('');

const elements = detectElements(content);
if (elements.length > 0) {
    console.log('🔍 検出された要素:');
    elements.forEach(e => console.log(`  ${e}`));
    console.log('');
}

console.log('📐 構造分析:');
const structure = analyzeStructure(content);
structure.forEach(s => console.log(`  ${s}`));
console.log('');

const suggestions = suggestImprovements(content);
if (suggestions.length > 0) {
    console.log('💡 改善提案:');
    suggestions.forEach(s => console.log(`  ${s}`));
    console.log('');
}

console.log('═══════════════════════════════════════════\n');
