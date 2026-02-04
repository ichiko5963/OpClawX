#!/usr/bin/env node
/**
 * Smart Reminder System
 * Creates reminders via OpenClaw cron jobs
 * Usage: node smart-reminder.js "message" "time"
 * 
 * Time formats:
 *   "10m" - in 10 minutes
 *   "2h" - in 2 hours
 *   "tomorrow 9:00" - tomorrow at 9:00
 *   "2025-02-05 14:00" - specific date/time
 */

const { execSync } = require('child_process');

const message = process.argv[2];
const timeSpec = process.argv[3] || "1h";

if (!message) {
    console.log('Usage: node smart-reminder.js "message" "time"');
    console.log('');
    console.log('Time formats:');
    console.log('  10m              - in 10 minutes');
    console.log('  2h               - in 2 hours');
    console.log('  tomorrow 9:00    - tomorrow at 9:00');
    console.log('  2025-02-05 14:00 - specific date/time');
    process.exit(1);
}

function parseTime(spec) {
    const now = new Date();
    
    // "10m" - minutes
    const minMatch = spec.match(/^(\d+)m$/);
    if (minMatch) {
        return new Date(now.getTime() + parseInt(minMatch[1]) * 60 * 1000);
    }
    
    // "2h" - hours
    const hourMatch = spec.match(/^(\d+)h$/);
    if (hourMatch) {
        return new Date(now.getTime() + parseInt(hourMatch[1]) * 60 * 60 * 1000);
    }
    
    // "1d" - days
    const dayMatch = spec.match(/^(\d+)d$/);
    if (dayMatch) {
        return new Date(now.getTime() + parseInt(dayMatch[1]) * 24 * 60 * 60 * 1000);
    }
    
    // "tomorrow 9:00"
    if (spec.startsWith('tomorrow')) {
        const timeMatch = spec.match(/(\d{1,2}):(\d{2})/);
        const target = new Date(now);
        target.setDate(target.getDate() + 1);
        if (timeMatch) {
            target.setHours(parseInt(timeMatch[1]), parseInt(timeMatch[2]), 0, 0);
        } else {
            target.setHours(9, 0, 0, 0);
        }
        return target;
    }
    
    // "YYYY-MM-DD HH:MM"
    const dateTimeMatch = spec.match(/(\d{4}-\d{2}-\d{2})\s+(\d{1,2}):(\d{2})/);
    if (dateTimeMatch) {
        const [_, dateStr, hour, minute] = dateTimeMatch;
        const target = new Date(dateStr);
        target.setHours(parseInt(hour), parseInt(minute), 0, 0);
        return target;
    }
    
    // Default: 1 hour from now
    return new Date(now.getTime() + 60 * 60 * 1000);
}

function formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}日${hours % 24}時間後`;
    if (hours > 0) return `${hours}時間${minutes % 60}分後`;
    if (minutes > 0) return `${minutes}分後`;
    return `${seconds}秒後`;
}

const targetTime = parseTime(timeSpec);
const targetMs = targetTime.getTime();
const durationMs = targetMs - Date.now();

if (durationMs < 0) {
    console.log('❌ 過去の時間は指定できません');
    process.exit(1);
}

console.log('');
console.log('═══════════════════════════════════════════');
console.log('        ⏰ リマインダー設定');
console.log('═══════════════════════════════════════════');
console.log('');
console.log(`📝 メッセージ: ${message}`);
console.log(`⏰ 時間: ${targetTime.toLocaleString('ja-JP')}`);
console.log(`⏳ 残り: ${formatDuration(durationMs)}`);
console.log('');

// Create cron job via OpenClaw
const cronPayload = {
    name: `reminder-${Date.now()}`,
    schedule: {
        kind: "at",
        atMs: targetMs
    },
    payload: {
        kind: "systemEvent",
        text: `⏰ リマインダー: ${message}`
    },
    sessionTarget: "main"
};

console.log('📋 OpenClaw cronジョブを作成中...');
console.log('');
console.log('以下のコマンドでOpenClawにリマインダーを設定:');
console.log('');
console.log(`openclaw cron add '${JSON.stringify(cronPayload)}'`);
console.log('');
console.log('═══════════════════════════════════════════');
