import { PostTemplate, TemplateType } from '@/types';

export const TEMPLATES: Record<TemplateType, PostTemplate> = {
  conclusion: {
    id: 'conclusion',
    name: '結論型',
    pattern: '【結論から言います】\n{content}\n\n{details}\n\n{action}',
    avgLikes: 306.7,
    avgRetweets: 45.2,
    description: '結論を先に述べ、続いて詳細を説明する構成。最もバズりやすい型。',
    example: '【結論から言います】\nAIエージェントは2024年に必須スキルになる\n\n①Cursorが月額$20でコーディング代行\n②Claude Codeが自然言語で開発\n③GPT-4が画像生成までこなす\n\nこれは絶対覚えるべき',
    isActive: true,
  },
  breaking: {
    id: 'breaking',
    name: '速報型',
    pattern: '【速報】{announcement}\n\n{details}\n\n{source}',
    avgLikes: 173.2,
    avgRetweets: 32.1,
    description: 'ニュース速報スタイル。最新情報を素早く届ける。',
    example: '【速報】Cursorが新機能「Composer」を発表\n\n・自然言語でアプリ構築\n・自動で環境構築\n・ワンクリックでデプロイ\n\n詳細はこちら👇',
    isActive: true,
  },
  distribution: {
    id: 'distribution',
    name: '配布型',
    pattern: '{emoji}{item}欲しい人いますか？\n\n{description}\n\n{condition}\n{action}',
    avgLikes: 85.3,
    avgRetweets: 35.1,
    description: '無料配布や特典を活用した構成。RT率が高い。',
    example: '🔥 AIツールリスト欲しい人いますか？\n\n・画像生成AI 10選\n・コーディングAI 8選\n・音声AI 5選\n\n計23個まとめました\n\n✅ フォロー必須\n✅ RTで全員にDM\n\n期限：24時間',
    isActive: true,
  },
  honest: {
    id: 'honest',
    name: '正直型',
    pattern: '正直、{honest_statement}\n\n{explanation}\n\n{conclusion}',
    avgLikes: 127.5,
    avgRetweets: 18.3,
    description: '率直な感想や意見から始める。親近感が出せる。',
    example: '正直、Claude Code最強すぎて怖い\n\n昨日試したら30分で完成した\n手動でやったら3日かかる作業が\n\n「自然言語指示だけで動く」\n\nこのままプログラマいらなくなるんじゃ',
    isActive: true,
  },
  viral: {
    id: 'viral',
    name: '海外バズ型',
    pattern: '【海外で大バズ】{trend}\n\n{details}\n\n{implication}',
    avgLikes: 142.8,
    avgRetweets: 28.7,
    description: '海外トレンドを紹介するスタイル。先取り感がある。',
    example: '【海外で大バズ】Vibe Codingという新潮流\n\n・英語指示だけでコード生成\n・非エンジニアがアプリ開発\n・Cursorが中心に\n\n米国で50万いいね突破\n日本まではあと数週間',
    isActive: true,
  },
  official: {
    id: 'official',
    name: '公式型',
    pattern: '【{company}が答えを出した】\n\n{announcement}\n\n{impact}',
    avgLikes: 98.4,
    avgRetweets: 22.1,
    description: '企業の公式発表を取り上げる。信頼性が高い。',
    example: '【OpenAIが答えを出した】\n\nGPT-5は「推論能力」特化\n\n・数学的推論が大幅向上\n・コーディング精度UP\n・ハルシネーション減少\n\nAIの"正確さ"が基準になる時代へ',
    isActive: true,
  },
};

// Template selector based on content
export function selectTemplate(content: string, source: 'bookmark' | 'keyword' | 'monitored'): TemplateType {
  const lowerContent = content.toLowerCase();
  
  // Check for breaking news indicators
  if (/\b(発表|発表|リリース|新機能|新サービス|アップデート)\b/.test(content)) {
    return 'breaking';
  }
  
  // Check for official announcements
  if (/\b(公式|企業|社|株式会社|Inc|Corp|OpenAI|Anthropic|Google|Microsoft)\b/.test(content)) {
    return 'official';
  }
  
  // Check for distribution/incentive content
  if (/\b(配布|プレゼント|プレゼント|無料|テンプレート|資料|リスト)\b/.test(content)) {
    return 'distribution';
  }
  
  // Check for honest opinions
  if (/\b(正直|思う|考え|感想|レビュー)\b/.test(content)) {
    return 'honest';
  }
  
  // Check for viral/overseas trends
  if (/\b(海外|米国|世界|バズ|話題|トレンド)\b/.test(content)) {
    return 'viral';
  }
  
  // Default to conclusion (strongest performer)
  return 'conclusion';
}

// Generate draft content based on template
export function generateDraft(
  templateType: TemplateType,
  sourcePost: {
    text: string;
    author: { name: string; username: string };
    mediaUrls?: string[];
    isVideo?: boolean;
    videoUrl?: string;
  },
  keywords: string[] = []
): { content: string; hashtags: string[] } {
  const template = TEMPLATES[templateType];
  
  // Extract key information
  const lines = sourcePost.text.split('\n').filter(l => l.trim());
  const mainPoint = lines[0]?.substring(0, 100) || sourcePost.text.substring(0, 100);
  const details = lines.slice(1, 4).map(l => `・${l.substring(0, 80)}`).join('\n');
  
  // Generate hashtags
  const baseHashtags = ['#AI', '#AirCle', '#エンジニア', '#プログラミング'];
  const keywordHashtags = keywords.slice(0, 3).map(k => `#${k.replace(/\s/g, '')}`);
  const uniqueHashtags = Array.from(new Set([...baseHashtags, ...keywordHashtags]));
  const hashtags = uniqueHashtags.slice(0, 5);
  
  let content = '';
  
  switch (templateType) {
    case 'conclusion':
      content = template.pattern
        .replace('{content}', mainPoint)
        .replace('{details}', details || '詳細はスレッドで👇')
        .replace('{action}', `これは見逃せない\n\n${hashtags.join(' ')}`);
      break;
      
    case 'breaking':
      content = template.pattern
        .replace('{announcement}', mainPoint)
        .replace('{details}', details || '続報を待つ')
        .replace('{source}', `via @${sourcePost.author.username}\n\n${hashtags.join(' ')}`);
      break;
      
    case 'distribution':
      content = template.pattern
        .replace('{emoji}', '🔥')
        .replace('{item}', mainPoint)
        .replace('{description}', details || '気になる人はフォロー必須')
        .replace('{condition}', '✅ RTで通知')
        .replace('{action}', `\n${hashtags.join(' ')}`);
      break;
      
    case 'honest':
      content = template.pattern
        .replace('{honest_statement}', mainPoint)
        .replace('{explanation}', details || '試してみて実感した')
        .replace('{conclusion}', `みんなも試してみて\n\n${hashtags.join(' ')}`);
      break;
      
    case 'viral':
      content = template.pattern
        .replace('{trend}', mainPoint)
        .replace('{details}', details || '世界中で注目されている')
        .replace('{implication}', `日本でも広まる予感\n\n${hashtags.join(' ')}`);
      break;
      
    case 'official':
      content = template.pattern
        .replace('{company}', sourcePost.author.name)
        .replace('{announcement}', mainPoint)
        .replace('{impact}', `これは業界を変える\n\n${hashtags.join(' ')}`);
      break;
  }
  
  return { content: content.replace(/\n{3,}/g, '\n\n'), hashtags };
}

// Get template stats for dashboard
export function getTemplateStats(): { name: string; avgLikes: number; usage: number }[] {
  return Object.values(TEMPLATES).map(t => ({
    name: t.name,
    avgLikes: t.avgLikes,
    usage: Math.floor(Math.random() * 30) + 10, // Placeholder, would come from DB
  }));
}
