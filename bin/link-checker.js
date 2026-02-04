#!/usr/bin/env node
/**
 * Obsidian Link Checker
 * Finds broken internal links in Obsidian vault
 * Usage: node link-checker.js [folder]
 */

const fs = require('fs');
const path = require('path');

const VAULT_DIR = path.join(
    process.env.HOME,
    'Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian'
);

const targetFolder = process.argv[2] || '';
const searchDir = targetFolder ? path.join(VAULT_DIR, targetFolder) : VAULT_DIR;

// Collect all markdown files
function getAllMdFiles(dir, files = []) {
    try {
        const items = fs.readdirSync(dir);
        for (const item of items) {
            const fullPath = path.join(dir, item);
            const stat = fs.statSync(fullPath);
            if (stat.isDirectory() && !item.startsWith('.')) {
                getAllMdFiles(fullPath, files);
            } else if (item.endsWith('.md')) {
                files.push(fullPath);
            }
        }
    } catch (e) {
        // Skip inaccessible directories
    }
    return files;
}

// Extract links from markdown content
function extractLinks(content) {
    const links = [];
    
    // [[link]] format
    const wikiLinkRegex = /\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g;
    let match;
    while ((match = wikiLinkRegex.exec(content)) !== null) {
        links.push(match[1].trim());
    }
    
    return links;
}

// Check if a link target exists
function linkExists(link, allFiles) {
    // Remove anchor if present
    const cleanLink = link.split('#')[0].trim();
    if (!cleanLink) return true; // Header-only links are valid
    
    // Check if any file matches
    return allFiles.some(file => {
        const basename = path.basename(file, '.md');
        return basename === cleanLink || file.includes(cleanLink);
    });
}

console.log('');
console.log('═══════════════════════════════════════════');
console.log('      🔗 Obsidian リンクチェッカー');
console.log('═══════════════════════════════════════════');
console.log('');
console.log(`📁 検索パス: ${searchDir}`);
console.log('');

const allFiles = getAllMdFiles(searchDir);
console.log(`📄 ファイル数: ${allFiles.length}`);
console.log('');

let brokenLinks = [];
let totalLinks = 0;

for (const file of allFiles) {
    try {
        const content = fs.readFileSync(file, 'utf-8');
        const links = extractLinks(content);
        totalLinks += links.length;
        
        for (const link of links) {
            if (!linkExists(link, allFiles)) {
                brokenLinks.push({
                    file: path.relative(VAULT_DIR, file),
                    link: link
                });
            }
        }
    } catch (e) {
        // Skip unreadable files
    }
}

console.log(`🔗 総リンク数: ${totalLinks}`);
console.log('');

if (brokenLinks.length === 0) {
    console.log('✅ 壊れたリンクはありません！');
} else {
    console.log(`⚠️ 壊れたリンク: ${brokenLinks.length}個`);
    console.log('');
    console.log('─────────────────────────────────────────');
    
    // Group by file
    const byFile = {};
    for (const {file, link} of brokenLinks) {
        if (!byFile[file]) byFile[file] = [];
        byFile[file].push(link);
    }
    
    for (const [file, links] of Object.entries(byFile)) {
        console.log(`\n📄 ${file}`);
        for (const link of links) {
            console.log(`   ❌ [[${link}]]`);
        }
    }
}

console.log('');
console.log('═══════════════════════════════════════════');
