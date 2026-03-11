/**
 * i18n — UI strings for the web dashboard & CLI
 */

const STRINGS = {
  en: {
    // CLI
    analyzing:        'Analyzing your posts...',
    analysisComplete: 'Analysis complete!',
    totalPosts:       'Total posts analyzed',
    topPatterns:      'Top performing patterns',
    avgEngagement:    'Avg. engagement',
    used:             'used',
    times:            'times',
    savedTo:          'Results saved to',
    generatedPost:    'Generated post',
    pattern:          'Pattern',
    charCount:        'Char count',
    postUrl:          'Post URL',
    platformCompat:   'Platform compatibility',
    suggestedPattern: 'Suggested pattern for your topic',
    weight:           'Engagement multiplier',
    engagement:       'engagement',
    tryCommand:       'Try this command',
    usage:            'Usage',
    commands:         'Commands',
    examples:         'Examples',
    languages:        'Supported languages',
    scheduleAdded:    'Schedule created',
    scheduleRemoved:  'Schedule removed',
    schedules:        'Your schedules',
    // Web
    appTitle:         'Viral Post Automation',
    uploadPrompt:     'Upload your X/Twitter CSV data',
    dragDrop:         'Drag & drop your CSV here, or click to browse',
    selectPattern:    'Select a pattern',
    enterTopic:       'Enter a topic',
    selectLang:       'Language',
    generateBtn:      'Generate Post',
    copyBtn:          'Copy Prompt',
    copied:           'Copied!',
    setupSchedule:    'Setup Daily Delivery',
    webhookPlaceholder: 'Discord / Slack webhook URL',
    timeLabel:        'Delivery time (local)',
    saveSchedule:     'Save Schedule',
    historyTitle:     'Generation History',
    noHistory:        'No posts generated yet',
    patternNames: {
      '01-breaking-news':  'Breaking News',
      '02-save-for-later': 'Save for Later',
      '03-global-trend':   'Global Trend',
      '04-conclusion-first':'Conclusion First',
      '05-honest-opinion': 'Honest Opinion',
      '06-vs-battle':      'VS Battle',
      '07-first-impression':'First Impression',
      '08-by-numbers':     'By The Numbers',
      '09-insight':        'Insight',
      '10-freebie':        'Free Resource',
      '11-pro-tips':       'Pro Tips',
      '12-warning':        'Warning',
      '13-storytelling':   'Storytelling',
      '14-complete-guide': 'Complete Guide',
      '15-future-forecast':'Future Forecast'
    }
  },

  ja: {
    analyzing:        '投稿を分析中...',
    analysisComplete: '分析完了！',
    totalPosts:       '分析した投稿数',
    topPatterns:      '最も効果的なパターン',
    avgEngagement:    '平均エンゲージメント',
    used:             '使用回数',
    times:            '回',
    savedTo:          '結果を保存しました',
    generatedPost:    '生成された投稿',
    pattern:          'パターン',
    charCount:        '文字数',
    postUrl:          '投稿URL',
    platformCompat:   'プラットフォーム互換性',
    suggestedPattern: 'おすすめパターン',
    weight:           'エンゲージメント倍率',
    engagement:       'エンゲージメント',
    tryCommand:       'このコマンドを試す',
    usage:            '使い方',
    commands:         'コマンド',
    examples:         '例',
    languages:        '対応言語',
    scheduleAdded:    'スケジュールを作成しました',
    scheduleRemoved:  'スケジュールを削除しました',
    schedules:        'スケジュール一覧',
    appTitle:         'バズ投稿自動化',
    uploadPrompt:     'X/TwitterデータのCSVをアップロード',
    dragDrop:         'CSVをここにドロップ、またはクリックして選択',
    selectPattern:    'パターンを選ぶ',
    enterTopic:       'トピックを入力',
    selectLang:       '言語',
    generateBtn:      '投稿を生成',
    copyBtn:          'プロンプトをコピー',
    copied:           'コピーしました！',
    setupSchedule:    '毎日自動配信を設定',
    webhookPlaceholder: 'Discord / Slack の Webhook URL',
    timeLabel:        '配信時刻',
    saveSchedule:     '保存',
    historyTitle:     '生成履歴',
    noHistory:        'まだ投稿が生成されていません',
    patternNames: {
      '01-breaking-news':  '速報型',
      '02-save-for-later': '保存版型',
      '03-global-trend':   '海外バズ型',
      '04-conclusion-first':'結論型',
      '05-honest-opinion': '正直型',
      '06-vs-battle':      '比較型',
      '07-first-impression':'体験記型',
      '08-by-numbers':     '数字強調型',
      '09-insight':        '洞察型',
      '10-freebie':        '配布型',
      '11-pro-tips':       '裏技型',
      '12-warning':        '警告型',
      '13-storytelling':   'ストーリー型',
      '14-complete-guide': '完全解説型',
      '15-future-forecast':'予測型'
    }
  },

  cn: {
    analyzing: '正在分析您的帖子...',
    analysisComplete: '分析完成！',
    totalPosts: '分析帖子总数',
    topPatterns: '效果最佳的模式',
    avgEngagement: '平均参与度',
    appTitle: '病毒式帖子自动化',
    uploadPrompt: '上传您的 X/Twitter CSV 数据',
    dragDrop: '将 CSV 拖放到此处，或点击浏览',
    selectPattern: '选择模式',
    enterTopic: '输入主题',
    selectLang: '语言',
    generateBtn: '生成帖子',
    copyBtn: '复制提示词',
    copied: '已复制！',
    setupSchedule: '设置每日自动发送',
    webhookPlaceholder: 'Discord / Slack Webhook URL',
    patternNames: {
      '01-breaking-news':  '突发新闻',
      '02-save-for-later': '收藏版',
      '03-global-trend':   '全球趋势',
      '04-conclusion-first':'结论先行',
      '05-honest-opinion': '诚实观点',
      '06-vs-battle':      '对决',
      '07-first-impression':'第一印象',
      '08-by-numbers':     '数字强调',
      '09-insight':        '洞察',
      '10-freebie':        '免费资源',
      '11-pro-tips':       '专业技巧',
      '12-warning':        '警告',
      '13-storytelling':   '故事',
      '14-complete-guide': '完整指南',
      '15-future-forecast':'未来预测'
    }
  },

  ko: {
    analyzing: '게시물 분석 중...',
    analysisComplete: '분석 완료!',
    appTitle: '바이럴 게시물 자동화',
    patternNames: {
      '01-breaking-news':  '속보형',
      '02-save-for-later': '저장형',
      '03-global-trend':   '글로벌트렌드',
      '04-conclusion-first':'결론형',
      '05-honest-opinion': '솔직한의견',
      '06-vs-battle':      '비교형',
      '07-first-impression':'첫인상형',
      '08-by-numbers':     '숫자강조형',
      '09-insight':        '통찰형',
      '10-freebie':        '무료배포형',
      '11-pro-tips':       '프로팁형',
      '12-warning':        '경고형',
      '13-storytelling':   '스토리텔링형',
      '14-complete-guide': '완전가이드형',
      '15-future-forecast':'미래예측형'
    }
  },

  es: {
    analyzing: 'Analizando tus publicaciones...',
    analysisComplete: '¡Análisis completo!',
    appTitle: 'Automatización de Posts Virales',
    patternNames: {
      '01-breaking-news':  'Noticia de Última Hora',
      '02-save-for-later': 'Guardar para Después',
      '03-global-trend':   'Tendencia Global',
      '04-conclusion-first':'Conclusión Primero',
      '05-honest-opinion': 'Opinión Honesta',
      '06-vs-battle':      'VS Batalla',
      '07-first-impression':'Primera Impresión',
      '08-by-numbers':     'En Números',
      '09-insight':        'Perspectiva',
      '10-freebie':        'Recurso Gratuito',
      '11-pro-tips':       'Consejos Pro',
      '12-warning':        'Advertencia',
      '13-storytelling':   'Narrativa',
      '14-complete-guide': 'Guía Completa',
      '15-future-forecast':'Pronóstico Futuro'
    }
  }
};

const LANGS = [
  { code:'en', name:'English',  flag:'🇺🇸' },
  { code:'ja', name:'日本語',   flag:'🇯🇵' },
  { code:'cn', name:'中文',     flag:'🇨🇳' },
  { code:'ko', name:'한국어',   flag:'🇰🇷' },
  { code:'es', name:'Español',  flag:'🇪🇸' }
];

function t(lang, key) {
  const locale  = STRINGS[lang] || STRINGS.en;
  const fallback = STRINGS.en;
  const keys = key.split('.');
  let val = locale;
  for (const k of keys) val = val?.[k];
  if (val !== undefined) return val;
  let fb = fallback;
  for (const k of keys) fb = fb?.[k];
  return fb ?? key;
}

function detectLang(text = '') {
  if (/[\u3040-\u30FF]/.test(text)) return 'ja';
  if (/[\u4E00-\u9FFF]/.test(text) && !/[\u3040-\u30FF]/.test(text)) return 'cn';
  if (/[\uAC00-\uD7AF]/.test(text)) return 'ko';
  if (/[áéíóúñ¿¡]/.test(text))    return 'es';
  return 'en';
}

module.exports = { t, detectLang, STRINGS, LANGS };
