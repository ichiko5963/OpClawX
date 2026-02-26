#!/usr/bin/env python3
"""
X投稿テンプレートジェネレーター
フック型に基づいた投稿テンプレートを生成する

Usage:
    python3 x_post_template.py --hook 速報 --topic "Claude Code新機能"
    python3 x_post_template.py --all  # 全フック型のテンプレートを表示
"""

import argparse
import random

TEMPLATES = {
    "速報": {
        "opener": [
            "【速報】{topic}",
            "【速報】{topic}が発表された",
            "【速報】{topic}、ついにきた",
        ],
        "bridge": [
            "これ、何を意味するか👇",
            "これがヤバい理由👇",
            "ポイントは3つ👇",
        ],
        "body_format": "bullets",  # 箇条書き
        "closer": [
            "{conclusion}の時代に突入。",
            "もう{old_way}は通用しない。",
            "{new_era}すべき。",
        ],
        "rules": [
            "発表直後のニュースに使う",
            "ソースURLは必須",
            "数字を必ず入れる",
        ],
    },
    "海外バズ": {
        "opener": [
            "【海外で大バズ】{topic}",
            "【海外で話題】{topic}",
            "【海外で大バズ】{topic}が話題になっている",
        ],
        "bridge": [
            "これ、何を意味するか👇",
            "日本ではまだ知られてないけど👇",
            "海外の反応がすごい👇",
        ],
        "body_format": "bullets",
        "closer": [
            "{conclusion}の時代。",
            "日本も{action}すべき。",
            "これ知らないのはヤバい。",
        ],
        "rules": [
            "英語圏のニュース/ツイートがソース",
            "「日本ではまだ〜」の対比が効く",
            "具体的な数字・事例を入れる",
        ],
    },
    "結論型": {
        "opener": [
            "【結論から言います】{topic}",
            "【結論】{topic}",
            "結論から言います。{topic}",
        ],
        "bridge": [
            "理由は3つ👇",
            "根拠を説明する👇",
            "データが証明してる👇",
        ],
        "body_format": "numbered",  # 番号付き
        "closer": [
            "これが現実。{action}。",
            "{conclusion}。異論は認める。",
            "事実ベースで考えるとこうなる。",
        ],
        "rules": [
            "最初に結論を言い切る",
            "根拠を3つ以内で説明",
            "データ・数字が命",
        ],
    },
    "公式型": {
        "opener": [
            "【公式が答えを出してしまった】{topic}",
            "【公式が認めた】{topic}",
            "【公式発表】{topic}",
        ],
        "bridge": [
            "何が変わるか👇",
            "これまでの常識が覆る👇",
            "業界への影響👇",
        ],
        "body_format": "bullets",
        "closer": [
            "公式が認めた以上、もう{old_way}は終わり。",
            "{conclusion}。公式が言ってるんだから。",
        ],
        "rules": [
            "公式発表・公式ブログがソース",
            "「公式が認めた」のインパクト",
            "従来の常識との対比",
        ],
    },
    "正直型": {
        "opener": [
            "正直、{topic}",
            "正直に言う。{topic}",
            "正直なところ、{topic}",
        ],
        "bridge": [
            "理由を説明する👇",
            "なぜそう思うか👇",
            "",  # ブリッジなしで直接本文もOK
        ],
        "body_format": "prose",  # 散文
        "closer": [
            "これが本音。",
            "異論は認めるけど、データは嘘つかない。",
            "信じるか信じないかはあなた次第。でも数字は出てる。",
        ],
        "rules": [
            "個人の意見・本音がベース",
            "やや挑発的でもOK",
            "「正直」で始めて本音を言い切る",
        ],
    },
    "配布型": {
        "opener": [
            "{item}欲しい人いますか？",
            "{item}、無料で配ります",
            "{item}をまとめました。欲しい人はリプ/RT",
        ],
        "bridge": [
            "中身を紹介👇",
            "こんな内容です👇",
            "",
        ],
        "body_format": "list",
        "closer": [
            "欲しい人はリプかRTで🙌",
            "いいね+RTで配布します",
            "フォロー+RTしてくれた人に送ります",
        ],
        "rules": [
            "「配布します」は強いCTA",
            "実際に配布するものを用意してから",
            "リスト形式で中身を見せる",
            "エンゲージメント最大化型",
        ],
    },
}


def show_template(hook: str, topic: str = ""):
    """指定したフック型のテンプレートを表示"""
    if hook not in TEMPLATES:
        print(f"❌ 未知のフック型: {hook}")
        print(f"   利用可能: {', '.join(TEMPLATES.keys())}")
        return
    
    t = TEMPLATES[hook]
    topic_display = topic or "[トピック]"
    
    print(f"\n{'=' * 50}")
    print(f"🎣 フック型: {hook}")
    print(f"{'=' * 50}")
    
    print(f"\n📝 オープナー例:")
    for opener in t["opener"]:
        print(f"   {opener.format(topic=topic_display, item=topic_display)}")
    
    print(f"\n🌉 ブリッジ:")
    for bridge in t["bridge"]:
        if bridge:
            print(f"   {bridge}")
    
    print(f"\n📄 本文形式: {t['body_format']}")
    if t["body_format"] == "bullets":
        print("   • ポイント1")
        print("   • ポイント2")
        print("   • ポイント3")
    elif t["body_format"] == "numbered":
        print("   ①ポイント1")
        print("   ②ポイント2")
        print("   ③ポイント3")
    elif t["body_format"] == "list":
        print("   ✅ 項目1")
        print("   ✅ 項目2")
        print("   ✅ 項目3")
    else:
        print("   自由散文形式")
    
    print(f"\n🏁 クローザー例:")
    for closer in t["closer"]:
        print(f"   {closer.format(conclusion='[結論]', old_way='[旧手法]', new_era='[新時代]', action='[行動]')}")
    
    print(f"\n📌 ルール:")
    for rule in t["rules"]:
        print(f"   • {rule}")


def show_all():
    """全フック型のテンプレートを表示"""
    for hook in TEMPLATES:
        show_template(hook)


def generate_skeleton(hook: str, topic: str) -> str:
    """投稿のスケルトンを生成"""
    t = TEMPLATES.get(hook)
    if not t:
        return f"Unknown hook: {hook}"
    
    opener = random.choice(t["opener"]).format(topic=topic, item=topic)
    bridge = random.choice([b for b in t["bridge"] if b])
    closer = random.choice(t["closer"]).format(
        conclusion="[結論]", old_way="[旧手法]", 
        new_era="[新時代]", action="[行動]"
    )
    
    body = ""
    if t["body_format"] == "bullets":
        body = "\n• [ポイント1]\n• [ポイント2]\n• [ポイント3]\n• [ポイント4]\n• [ポイント5]"
    elif t["body_format"] == "numbered":
        body = "\n①[ポイント1]\n②[ポイント2]\n③[ポイント3]"
    elif t["body_format"] == "list":
        body = "\n✅ [項目1]\n✅ [項目2]\n✅ [項目3]"
    else:
        body = "\n[本文をここに書く]"
    
    return f"{opener}\n\n{bridge}\n{body}\n\n{closer}\n\n参考: [URL]"


def main():
    parser = argparse.ArgumentParser(description="X投稿テンプレートジェネレーター")
    parser.add_argument("--hook", help="フック型を指定")
    parser.add_argument("--topic", default="", help="トピック")
    parser.add_argument("--all", action="store_true", help="全フック型を表示")
    parser.add_argument("--skeleton", action="store_true", help="スケルトン生成")
    args = parser.parse_args()
    
    if args.all:
        show_all()
    elif args.hook:
        if args.skeleton and args.topic:
            print(generate_skeleton(args.hook, args.topic))
        else:
            show_template(args.hook, args.topic)
    else:
        print("📋 利用可能なフック型:")
        for hook, t in TEMPLATES.items():
            print(f"  🎣 {hook}: {t['rules'][0]}")
        print(f"\n使い方: python3 {__file__} --hook 速報 --topic 'Claude新機能'")
        print(f"         python3 {__file__} --all")


if __name__ == "__main__":
    main()
