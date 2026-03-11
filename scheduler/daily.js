/**
 * Daily Delivery System
 * Reads a schedule config → generates posts → delivers via webhook / Discord / email
 */

const fs   = require('fs');
const path = require('path');
const { generatePost, suggestPattern } = require('../core/generator');
const { analyzeData }                  = require('../core/analyzer');

const SCHEDULE_PATH = path.join(__dirname, '../config/schedule.json');
const LOG_PATH      = path.join(__dirname, '../logs/deliveries.jsonl');

// ─── Schedule helpers ────────────────────────────────────────────────────────

function loadSchedules() {
  if (!fs.existsSync(SCHEDULE_PATH)) return [];
  try { return JSON.parse(fs.readFileSync(SCHEDULE_PATH, 'utf8')); }
  catch { return []; }
}

function saveSchedules(schedules) {
  fs.mkdirSync(path.dirname(SCHEDULE_PATH), { recursive: true });
  fs.writeFileSync(SCHEDULE_PATH, JSON.stringify(schedules, null, 2));
}

function addSchedule(cfg) {
  const schedules = loadSchedules();
  const id = `sched_${Date.now()}`;
  schedules.push({ id, enabled: true, createdAt: new Date().toISOString(), ...cfg });
  saveSchedules(schedules);
  return id;
}

// ─── Delivery methods ─────────────────────────────────────────────────────────

async function deliverWebhook(url, payload) {
  try {
    const body = JSON.stringify(payload);
    // Use built-in https to avoid extra dependencies
    const { request } = require('https');
    const urlObj = new URL(url);

    return new Promise((resolve, reject) => {
      const req = request({
        hostname: urlObj.hostname,
        path:     urlObj.pathname + urlObj.search,
        method:   'POST',
        headers:  { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
      }, res => {
        let data = '';
        res.on('data', d => data += d);
        res.on('end', () => resolve({ status: res.statusCode, body: data }));
      });
      req.on('error', reject);
      req.write(body);
      req.end();
    });
  } catch (err) {
    throw new Error(`Webhook delivery failed: ${err.message}`);
  }
}

async function deliverDiscord(webhookUrl, post) {
  const embed = {
    title:       `📝 Daily Post — ${post.patternName}`,
    description: `**Topic:** ${post.topic}\n\n**Prompt ready:**\n\`\`\`\n${post.prompt.slice(0,1000)}\n\`\`\``,
    color:       0x5865F2,
    fields: [
      { name: '🔗 View Online', value: post.url, inline: true },
      { name: '🌍 Language',    value: post.lang, inline: true },
      { name: '📋 Pattern',     value: post.patternId, inline: true }
    ],
    footer: { text: 'Viral Post Automation • github.com/ichiko5963/OpClawX' },
    timestamp: new Date().toISOString()
  };
  return deliverWebhook(webhookUrl, { embeds: [embed] });
}

// ─── Log helper ──────────────────────────────────────────────────────────────

function logDelivery(scheduleId, post, result) {
  fs.mkdirSync(path.dirname(LOG_PATH), { recursive: true });
  const entry = JSON.stringify({
    ts: new Date().toISOString(),
    scheduleId,
    postId:    post.id,
    patternId: post.patternId,
    lang:      post.lang,
    url:       post.url,
    success:   result.success,
    error:     result.error || null
  });
  fs.appendFileSync(LOG_PATH, entry + '\n');
}

// ─── Core runner ─────────────────────────────────────────────────────────────

async function runSchedule(schedule) {
  console.log(`[scheduler] Running: ${schedule.id} | ${schedule.patternId || 'auto'} | lang:${schedule.lang}`);

  // Auto-select pattern from last analysis if configured
  let patternId = schedule.patternId;
  if (patternId === 'auto' || !patternId) {
    patternId = suggestPattern(schedule.topic || 'AI News', schedule.lang || 'en');
  }

  const post = generatePost(patternId, schedule.topic || 'AI News', schedule.lang || 'en', {
    baseUrl: schedule.delivery?.baseUrl || 'https://vpa.opclaw.app'
  });

  let deliveryResult = { success: false, error: null };

  if (schedule.delivery?.webhook) {
    try {
      const method = schedule.delivery.type === 'discord' ? deliverDiscord : deliverWebhook;
      const response = await method(schedule.delivery.webhook, post);
      deliveryResult = { success: true, status: response?.status };
      console.log(`[scheduler] ✅ Delivered to webhook. Post URL: ${post.url}`);
    } catch (err) {
      deliveryResult = { success: false, error: err.message };
      console.error(`[scheduler] ❌ Delivery error: ${err.message}`);
    }
  } else {
    // No webhook — just log the generated post
    console.log('\n' + '─'.repeat(60));
    console.log('GENERATED POST PROMPT:');
    console.log('─'.repeat(60));
    console.log(post.prompt);
    console.log('─'.repeat(60));
    console.log(`URL: ${post.url}`);
    deliveryResult = { success: true };
  }

  logDelivery(schedule.id, post, deliveryResult);
  return { post, ...deliveryResult };
}

async function runDue() {
  const now     = new Date();
  const hh      = String(now.getHours()).padStart(2,'0');
  const mm      = String(now.getMinutes()).padStart(2,'0');
  const current = `${hh}:${mm}`;

  const schedules = loadSchedules().filter(s => s.enabled && s.time === current);
  console.log(`[scheduler] ${current} — ${schedules.length} schedule(s) due`);

  for (const s of schedules) {
    await runSchedule(s).catch(err => console.error(`[scheduler] Error in ${s.id}:`, err));
  }
}

async function runAll() {
  const schedules = loadSchedules().filter(s => s.enabled);
  for (const s of schedules) {
    await runSchedule(s).catch(err => console.error(`[scheduler] Error in ${s.id}:`, err));
  }
}

// ─── CLI ─────────────────────────────────────────────────────────────────────

if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.includes('--add')) {
    const get = (flag) => { const i = args.indexOf(flag); return i !== -1 ? args[i+1] : null; };
    const id = addSchedule({
      time:      get('--time')    || '07:00',
      lang:      get('--lang')    || 'ja',
      patternId: get('--pattern') || 'auto',
      topic:     get('--topic')   || 'AI News',
      delivery: {
        type:    get('--type')    || 'discord',
        webhook: get('--webhook'),
        baseUrl: get('--base-url')|| 'https://vpa.opclaw.app'
      }
    });
    console.log(`✅ Schedule added: ${id}`);

  } else if (args.includes('--list')) {
    console.table(loadSchedules().map(s => ({
      id: s.id, enabled: s.enabled, time: s.time,
      lang: s.lang, pattern: s.patternId, topic: s.topic
    })));

  } else if (args.includes('--run-all')) {
    runAll().then(() => console.log('Done.'));

  } else if (args.includes('--run-due')) {
    runDue().then(() => console.log('Done.'));

  } else {
    console.log(`
Usage:
  node scheduler/daily.js --add --time 07:00 --lang ja --topic "AI News" --webhook <url>
  node scheduler/daily.js --list
  node scheduler/daily.js --run-due
  node scheduler/daily.js --run-all
    `);
  }
}

module.exports = { addSchedule, loadSchedules, runDue, runAll, runSchedule };
