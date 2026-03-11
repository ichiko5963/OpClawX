# OpClawX Cron Setup Guide

## macOS / Linux

```bash
# Edit crontab
crontab -e

# Add this line for daily 7:00 AM execution
0 7 * * * cd /path/to/OpClawX && /usr/local/bin/node scheduler/daily-15.js --lang ja >> logs/cron.log 2>&1

# Or for multiple languages
0 7 * * * cd /path/to/OpClawX && /usr/local/bin/node scheduler/daily-15.js --lang ja
0 8 * * * cd /path/to/OpClawX && /usr/local/bin/node scheduler/daily-15.js --lang en
0 9 * * * cd /path/to/OpClawX && /usr/local/bin/node scheduler/daily-15.js --lang cn
```

## Environment Variables

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
export VPA_LANG="ja"
export VPA_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export VPA_BASE_URL="https://your-domain.com"
```

## Verify Cron is Working

```bash
# Check crontab
crontab -l

# Test run manually
cd /path/to/OpClawX && node scheduler/daily-15.js --lang ja

# Check logs
tail -f logs/cron.log
```

## OpenClaw Integration

```bash
# Let OpenClaw handle the cron via its built-in scheduler
openclaw run OpClawX --schedule-cron --time "07:00" --lang ja
```
