# Cron Setup Guide — OpClawX

## 1日3回自動配信（朝7時・昼12時・夕方18時）

## macOS / Linux

```bash
# Edit crontab
crontab -e

# Add these lines for 3 daily deliveries
# 朝7時（モーニング投稿）
0 7 * * * cd /path/to/OpClawX && /usr/local/bin/node scheduler/daily-15.js --lang ja >> logs/cron-07.log 2>&1

# 昼12時（ランチタイム投稿）
0 12 * * * cd /path/to/OpClawX && /usr/local/bin/node scheduler/daily-15.js --lang ja >> logs/cron-12.log 2>&1

# 夕方18時（イブニング投稿）
0 18 * * * cd /path/to/OpClawX && /usr/local/bin/node scheduler/daily-15.js --lang ja >> logs/cron-18.log 2>&1
```

## 多言語対応（例：日本語・英語・中国語）

```bash
# 日本語 — 朝7時
0 7 * * * cd /path/to/OpClawX && node scheduler/daily-15.js --lang ja

# 英語 — 昼12時
0 12 * * * cd /path/to/OpClawX && node scheduler/daily-15.js --lang en

# 中国語 — 夕方18時
0 18 * * * cd /path/to/OpClawX && node scheduler/daily-15.js --lang cn
```

## Environment Setup

```bash
# Add to ~/.zshrc or ~/.bashrc
export VPA_LANG="ja"
export VPA_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export VPA_BASE_URL="https://your-domain.com"
```

## Verify Cron Jobs

```bash
# List all cron jobs
crontab -l

# Check cron logs
tail -f logs/cron-07.log
tail -f logs/cron-12.log
tail -f logs/cron-18.log
```

## Manual Test

```bash
# Simulate each run
cd /path/to/OpClawX && node scheduler/daily-15.js --lang ja
```
