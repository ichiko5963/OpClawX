#!/usr/bin/env node
/**
 * Idea Capture Tool
 * Quick capture of ideas with automatic categorization
 * Usage: node idea-capture.js "your idea"
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = path.join(
    process.env.HOME,
    'Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared'
);
const IDEAS_FILE = path.join(WORKSPACE, 'ideas.json');
const VAULT_DIR = path.join(WORKSPACE, 'obsidian/Ichioka Obsidian');

const idea = process.argv.slice(2).join(' ');

if (!idea) {
    console.log('Usage: node idea-capture.js "your idea"');
    console.log('');
    console.log('Commands:');
    console.log('  node idea-capture.js "idea"     - Capture a new idea');
    console.log('  node idea-capture.js --list     - List all ideas');
    console.log('  node idea-capture.js --export   - Export to Obsidian');
    process.exit(1);
}

// Load existing ideas
function loadIdeas() {
    try {
        return JSON.parse(fs.readFileSync(IDEAS_FILE, 'utf-8'));
    } catch {
        return { ideas: [] };
    }
}

// Save ideas
function saveIdeas(data) {
    fs.writeFileSync(IDEAS_FILE, JSON.stringify(data, null, 2));
}

// Auto-categorize idea
function categorize(text) {
    const lower = text.toLowerCase();
    
    if (lower.includes('ai') || lower.includes('claude') || lower.includes('gpt') || lower.includes('cursor')) {
        return 'AI/ツール';
    }
    if (lower.includes('aircle') || lower.includes('コミュニティ') || lower.includes('セミナー')) {
        return 'AirCle';
    }
    if (lower.includes('x') || lower.includes('twitter') || lower.includes('投稿') || lower.includes('sns')) {
        return 'SNS/マーケティング';
    }
    if (lower.includes('obsidian') || lower.includes('ノート') || lower.includes('メモ')) {
        return 'Obsidian/知識管理';
    }
    if (lower.includes('コード') || lower.includes('開発') || lower.includes('実装')) {
        return '開発';
    }
    if (lower.includes('ビジネス') || lower.includes('収益') || lower.includes('マネタイズ')) {
        return 'ビジネス';
    }
    
    return 'その他';
}

// List command
if (idea === '--list') {
    const data = loadIdeas();
    console.log('');
    console.log('═══════════════════════════════════════════');
    console.log('      💡 アイデア一覧');
    console.log('═══════════════════════════════════════════');
    console.log('');
    
    if (data.ideas.length === 0) {
        console.log('まだアイデアがありません');
    } else {
        // Group by category
        const byCategory = {};
        for (const idea of data.ideas) {
            const cat = idea.category || 'その他';
            if (!byCategory[cat]) byCategory[cat] = [];
            byCategory[cat].push(idea);
        }
        
        for (const [category, ideas] of Object.entries(byCategory)) {
            console.log(`📁 ${category} (${ideas.length})`);
            for (const i of ideas) {
                const date = new Date(i.created).toLocaleDateString('ja-JP');
                console.log(`   • [${date}] ${i.text}`);
            }
            console.log('');
        }
    }
    
    console.log(`合計: ${data.ideas.length} アイデア`);
    console.log('');
    process.exit(0);
}

// Export command
if (idea === '--export') {
    const data = loadIdeas();
    const exportFile = path.join(VAULT_DIR, '01_Notes', `ideas-export-${new Date().toISOString().split('T')[0]}.md`);
    
    let content = '# アイデア集\n\n';
    content += `*エクスポート日時: ${new Date().toLocaleString('ja-JP')}*\n\n`;
    
    const byCategory = {};
    for (const idea of data.ideas) {
        const cat = idea.category || 'その他';
        if (!byCategory[cat]) byCategory[cat] = [];
        byCategory[cat].push(idea);
    }
    
    for (const [category, ideas] of Object.entries(byCategory)) {
        content += `## ${category}\n\n`;
        for (const i of ideas) {
            const date = new Date(i.created).toLocaleDateString('ja-JP');
            content += `- [${date}] ${i.text}\n`;
        }
        content += '\n';
    }
    
    fs.writeFileSync(exportFile, content);
    console.log(`✅ エクスポート完了: ${exportFile}`);
    process.exit(0);
}

// Add new idea
const data = loadIdeas();
const newIdea = {
    id: Date.now(),
    text: idea,
    category: categorize(idea),
    created: new Date().toISOString(),
    status: 'new'
};

data.ideas.push(newIdea);
saveIdeas(data);

console.log('');
console.log('═══════════════════════════════════════════');
console.log('      💡 アイデアをキャプチャしました！');
console.log('═══════════════════════════════════════════');
console.log('');
console.log(`📝 アイデア: ${idea}`);
console.log(`📁 カテゴリ: ${newIdea.category}`);
console.log(`⏰ 保存日時: ${new Date().toLocaleString('ja-JP')}`);
console.log('');
console.log(`現在のアイデア数: ${data.ideas.length}`);
console.log('');
