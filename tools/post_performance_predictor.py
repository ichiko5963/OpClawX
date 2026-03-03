#!/usr/bin/env python3
"""
Post Performance Predictor v1.0
X投稿のパフォーマンスを予測するツール。
過去のバズパターン分析に基づき、各投稿のバズ可能性をスコアリング。

Usage:
  python3 tools/post_performance_predictor.py <posts.md>
  python3 tools/post_performance_predictor.py <posts.md> --verbose
  python3 tools/post_performance_predictor.py <posts.md> --top 5
"""

import sys
import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

WORKSPACE = Path("/Users/ai-driven-work/Documents/OpenClaw-Workspace")

# バズパターン定義（過去分析結果: 820件ベース）
BUZZ_PATTERNS = {
    "結論型": {
        "triggers": ["結論から", "結論です", "結論を言います", "答えを出す", "答え出した"],
        "avg_likes": 306.7,
        "weight": 1.5,
    },
    "速報型": {
        "triggers": ["【速報】", "速報", "ついに", "公開された", "リリース"],
        "avg_likes": 173.2,
        "weight": 1.3,
    },
    "海外バズ型": {
        "triggers": ["海外で大バズ", "海外で話題", "海外バズ", "世界で話題"],
        "avg_likes": 150.0,
        "weight": 1.4,
    },
    "配布型": {
        "triggers": ["欲しい人", "配布", "無料で", "プレゼント", "あげます"],
        "avg_likes": 120.0,
        "weight": 1.2,
    },
    "正直型": {
        "triggers": ["正直、", "正直に言うと", "本音を言うと"],
        "avg_likes": 140.0,
        "weight": 1.2,
    },
    "公式型": {
        "triggers": ["公式が", "公式発表", "公式が答え"],
        "avg_likes": 160.0,
        "weight": 1.3,
    },
}

# エンゲージメント要素
ENGAGEMENT_FACTORS = {
    "箇条書き": {"pattern": r'[・\-①②③④⑤]', "score": 10, "desc": "箇条書きで読みやすい"},
    "数字インパクト": {"pattern": r'[\$¥]?\d+[万億千百%BbMm]', "score": 15, "desc": "具体的な数字"},
    "問いかけ": {"pattern": r'[？?]', "score": 8, "desc": "問いかけでリプ誘導"},
    "CTA": {"pattern": r'すべき|の時代|必見|知らないと|やらないと', "score": 12, "desc": "行動喚起"},
    "対比構造": {"pattern": r'(だけど|一方|しかし|なのに|vs|比較)', "score": 8, "desc": "対比で興味喚起"},
    "具体ツール名": {"pattern": r'(Claude|Cursor|GPT|Notion|GitHub|Copilot|Vercel|OpenAI|Anthropic|Stripe|Devin|Windsurf)', "score": 10, "desc": "具体的なツール名"},
    "衝撃表現": {"pattern": r'(ヤバい|やばい|衝撃|驚き|信じられない|とんでもない|破壊)', "score": 7, "desc": "感情的インパクト"},
    "👇導線": {"pattern": r'👇', "score": 5, "desc": "スレッド/箇条書き導線"},
}

# ペナルティ要素
PENALTIES = {
    "長すぎ": {"check": lambda t: len(t) > 600, "penalty": -10, "desc": "600文字超え"},
    "短すぎ": {"check": lambda t: len(t) < 50, "penalty": -15, "desc": "50文字未満"},
    "禁止絵文字": {"check": lambda t: bool(re.search(r'[📱📅🔗📰🚨📊💼]', t)), "penalty": -10, "desc": "禁止絵文字使用"},
    "絵文字過多": {"check": lambda t: len(re.findall(r'[\U0001F300-\U0001F9FF]', t)) > 5, "penalty": -8, "desc": "絵文字5個超え"},
    "番号リスト多用": {"check": lambda t: len(re.findall(r'[①②③④⑤⑥⑦⑧⑨⑩]', t)) > 5, "penalty": -5, "desc": "番号リスト多用"},
    "URLなし": {"check": lambda t: 'http' not in t and '🔥' not in t and '👇' not in t, "penalty": -3, "desc": "導線要素なし"},
}

# 最適投稿時間帯
OPTIMAL_HOURS = [0, 8, 12, 16, 20]


@dataclass
class PostScore:
    index: int
    title: str
    content: str
    base_score: int = 50
    pattern_score: int = 0
    engagement_score: int = 0
    penalty_score: int = 0
    total_score: int = 0
    pattern_name: str = ""
    factors: list = field(default_factory=list)
    penalties_hit: list = field(default_factory=list)
    buzz_prediction: str = ""
    char_count: int = 0


def parse_posts(filepath: str) -> list:
    """MDファイルから投稿を解析"""
    content = Path(filepath).read_text(encoding="utf-8")
    posts = []
    
    # ## 投稿N: タイトル パターンで分割
    sections = re.split(r'^## 投稿\d+[：:]?\s*', content, flags=re.MULTILINE)
    
    for i, section in enumerate(sections[1:], 1):
        lines = section.strip().split('\n')
        title = lines[0].strip() if lines else f"投稿{i}"
        # セパレーター(---)で分割してコンテンツ取得
        body_parts = section.split('---')
        body = body_parts[0].strip() if body_parts else section.strip()
        # タイトル行を除去
        body_lines = body.split('\n')[1:]
        body = '\n'.join(line for line in body_lines if line.strip())
        
        posts.append({"index": i, "title": title, "content": body})
    
    return posts


def score_post(post: dict) -> PostScore:
    """投稿をスコアリング"""
    result = PostScore(
        index=post["index"],
        title=post["title"],
        content=post["content"],
        char_count=len(post["content"]),
    )
    
    full_text = f"{post['title']}\n{post['content']}"
    
    # 1. バズパターン検出
    best_pattern = ""
    best_weight = 1.0
    for name, config in BUZZ_PATTERNS.items():
        for trigger in config["triggers"]:
            if trigger in full_text:
                if config["weight"] > best_weight:
                    best_pattern = name
                    best_weight = config["weight"]
                break
    
    if best_pattern:
        result.pattern_name = best_pattern
        result.pattern_score = int(20 * best_weight)
    
    # 2. エンゲージメント要素
    for name, config in ENGAGEMENT_FACTORS.items():
        if re.search(config["pattern"], full_text):
            result.engagement_score += config["score"]
            result.factors.append(f"✅ {name}: {config['desc']}")
    
    # 3. ペナルティ
    for name, config in PENALTIES.items():
        if config["check"](post["content"]):
            result.penalty_score += config["penalty"]
            result.penalties_hit.append(f"⚠️ {name}: {config['desc']}")
    
    # 4. 長さボーナス（100-400文字が最適）
    length = len(post["content"])
    if 100 <= length <= 400:
        result.engagement_score += 10
        result.factors.append("✅ 最適な文字数 (100-400)")
    elif 400 < length <= 600:
        result.engagement_score += 5
        result.factors.append("✅ やや長めだが許容範囲")
    
    # 5. 改行による読みやすさ
    line_count = len([l for l in post["content"].split('\n') if l.strip()])
    if line_count >= 5:
        result.engagement_score += 5
        result.factors.append("✅ 適切な改行で読みやすい")
    
    # トータル計算
    result.total_score = max(0, min(100, 
        result.base_score + result.pattern_score + result.engagement_score + result.penalty_score))
    
    # バズ予測
    if result.total_score >= 85:
        result.buzz_prediction = "🔥🔥🔥 高確率バズ"
    elif result.total_score >= 70:
        result.buzz_prediction = "🔥🔥 バズ期待大"
    elif result.total_score >= 55:
        result.buzz_prediction = "🔥 まあまあ"
    elif result.total_score >= 40:
        result.buzz_prediction = "😐 普通"
    else:
        result.buzz_prediction = "❄️ 改善必要"
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 post_performance_predictor.py <posts.md> [--verbose] [--top N]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    verbose = "--verbose" in sys.argv
    top_n = None
    if "--top" in sys.argv:
        idx = sys.argv.index("--top")
        if idx + 1 < len(sys.argv):
            top_n = int(sys.argv[idx + 1])
    
    posts = parse_posts(filepath)
    if not posts:
        print("❌ 投稿が見つかりませんでした")
        sys.exit(1)
    
    results = [score_post(p) for p in posts]
    results.sort(key=lambda r: r.total_score, reverse=True)
    
    # サマリー
    avg_score = sum(r.total_score for r in results) / len(results)
    print(f"\n{'='*60}")
    print(f"📊 パフォーマンス予測レポート")
    print(f"{'='*60}")
    print(f"📁 ファイル: {filepath}")
    print(f"📝 投稿数: {len(results)}")
    print(f"📈 平均スコア: {avg_score:.1f}/100")
    print(f"🏆 最高: {results[0].total_score}/100 (投稿{results[0].index})")
    print(f"📉 最低: {results[-1].total_score}/100 (投稿{results[-1].index})")
    
    # パターン分布
    patterns = {}
    for r in results:
        p = r.pattern_name or "パターンなし"
        patterns[p] = patterns.get(p, 0) + 1
    print(f"\n📋 バズパターン分布:")
    for p, count in sorted(patterns.items(), key=lambda x: -x[1]):
        print(f"  {p}: {count}件")
    
    # スコア分布
    tiers = {"🔥🔥🔥 (85+)": 0, "🔥🔥 (70-84)": 0, "🔥 (55-69)": 0, "😐 (40-54)": 0, "❄️ (<40)": 0}
    for r in results:
        if r.total_score >= 85: tiers["🔥🔥🔥 (85+)"] += 1
        elif r.total_score >= 70: tiers["🔥🔥 (70-84)"] += 1
        elif r.total_score >= 55: tiers["🔥 (55-69)"] += 1
        elif r.total_score >= 40: tiers["😐 (40-54)"] += 1
        else: tiers["❄️ (<40)"] += 1
    
    print(f"\n📊 スコア分布:")
    for tier, count in tiers.items():
        bar = "█" * count
        print(f"  {tier}: {bar} ({count}件)")
    
    # 詳細表示
    display = results[:top_n] if top_n else results
    print(f"\n{'='*60}")
    print(f"📝 投稿詳細 {'(上位' + str(top_n) + '件)' if top_n else ''}")
    print(f"{'='*60}")
    
    for r in display:
        print(f"\n{'─'*50}")
        print(f"📌 投稿{r.index}: {r.title[:50]}...")
        print(f"   スコア: {r.total_score}/100 {r.buzz_prediction}")
        print(f"   文字数: {r.char_count}")
        if r.pattern_name:
            print(f"   パターン: {r.pattern_name} (+{r.pattern_score})")
        
        if verbose:
            if r.factors:
                print(f"   要素:")
                for f in r.factors:
                    print(f"     {f}")
            if r.penalties_hit:
                print(f"   ペナルティ:")
                for p in r.penalties_hit:
                    print(f"     {p}")
    
    print(f"\n{'='*60}")
    
    # JSON出力
    output = {
        "file": filepath,
        "total_posts": len(results),
        "avg_score": round(avg_score, 1),
        "top_score": results[0].total_score,
        "bottom_score": results[-1].total_score,
        "scores": [{"index": r.index, "score": r.total_score, "pattern": r.pattern_name} for r in results],
    }
    
    json_path = Path(filepath).with_suffix('.scores.json')
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"💾 スコアデータ保存: {json_path}")


if __name__ == "__main__":
    main()
