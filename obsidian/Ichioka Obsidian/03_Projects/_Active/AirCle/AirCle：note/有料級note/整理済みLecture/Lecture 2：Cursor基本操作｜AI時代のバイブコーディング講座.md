# Lecture 2：Cursor基本操作｜AI時代のバイブコーディング講座

## 初めに

こんにちは**AirCleの運営**です！

Cursor（カーソル）というAIエディタ、聞いたことありますか？

「AIでコードを書けるエディタって聞いたけど、実際どうなの？」「GitHub Copilotと何が違うの？」「本当に初心者でも使えるの？」という疑問、多いと思います。

僕自身も最初はまさにそうで、VSCodeは使いこなしているつもりだけど、Cursorってどこまで進化したのか正直分かりませんでした。  
「AIエディタって言われているけど、実際のところ何ができるんだろう？」と思いながらも、どこから理解すればいいか分からずにいました。

そこで今回、AirCleで実際にCursorを徹底的に検証し、**「なぜCursorがAI時代の開発を変えるのか」**を詳しく調べてみました。

Cursorは、2025年現在、**AI機能を標準搭載したVSCodeの進化版**として、世界中の開発者から注目を集めています。単なるコード補完ではなく、**Cmd+K（コード生成）、Cmd+L（AIチャット）、Tab補完**の3つの機能で、開発の生産性を劇的に向上させます。

しかも今回は特別に、**実際にCursorでTodoアプリを作る実践演習**と、**プロンプトの書き方のコツ**まで、余すことなくお届けします。

さらにそれだけではなく、**「なぜAIがコードを書けるのか？」という本質的な理解**も詳しく解説し、**「Cursorを自在に使いこなして、AIと協働開発できる」**知識として落とし込みました。

つまり**「実践 → 理解 → 応用」**という  
3段階の学び方ができるようになっているんです。

内容としては：

- **Cursorのインストールと初期設定**
    
- **Cmd+K（コード生成・編集）の使い方**
    
- **Cmd+L（AIチャット）でエラー解決**
    
- **Tab補完の活用法**
    
- **実践：AIにTodoアプリを作らせる**

僕自身もこの講座を通じて、Cursorの見え方がまるで変わりました。  
ただの「便利なエディタ」じゃなく、**「AIと協働して開発する新しいスタイル」**としてやっと本当の価値が分かったんです。

もしあなたが  
**「AIエディタを始めたいけど、どこから手をつけていいか分からない」  
「Cursorの機能を完全に使いこなしたい」**  
と思っているなら、この記事は間違いなく最適解になるはずです。

---

⚠️ このnoteには**2025年最新のCursor活用法**が収録されています。  
実際の開発現場で使われている最新の機能とテクニックを、初心者にも分かりやすく解説しています。理解を一気に深めるきっかけになると思います。

---

## 【ここから本編スタート】

このラインより上のエリアが無料で表示されます。

---

# 📘 Lecture 2: Cursor基本操作（超詳細版）

**学習時間**: 4-5時間  
**難易度**: ★★☆☆☆（初心者〜初級）  
**目標**: CursorのAI機能（Cmd+K、Cmd+L、Tab補完）を完全習得し、自然言語でコードを生成できるようになる

---

## 🎯 この講座で達成できること

- Cursorのインストールと初期設定完了
- Cmd+K（コード生成・編集）を自在に使いこなす
- Cmd+L（AIチャット）でエラー解決・質問応答
- Tab補完でコーディングを高速化
- AIを活用してTodoアプリを作成（実践演習）
- プロンプトの書き方を理解し、AIから最適な回答を引き出す

---

## 📚 セクション構成

### SECTION 01: Cursorとは？AI時代の新しいエディタ（20分）

#### 1.1 従来のプログラミングの課題

プログラミング学習における3大挫折ポイント：

1. **構文エラーに悩む**
   - セミコロン忘れ、括弧の閉じ忘れ、スペルミス
   - エラーメッセージが英語で理解できない
   - 解決に30分〜数時間かかることも

2. **検索とコピペの繰り返し**
   - Google → Stack Overflow → コピペ → 動かない → また検索
   - 古い情報が多く、そのまま使えない
   - 時間の無駄が多い

3. **ドキュメント探しの難しさ**
   - 公式ドキュメントは英語が多い
   - 初心者向けの説明が少ない
   - どこから読めばいいか分からない

#### 1.2 Cursorが解決する問題

Cursorは、上記の課題を**AIの力で一気に解決**します。

| 従来の開発 | Cursorでの開発 |
|-----------|---------------|
| 構文エラーを自力で解決 | AIが自動検出・修正提案 |
| Googleで検索 → コピペ | AIに質問 → 即答 |
| ドキュメントを読み漁る | AIが必要な情報を要約 |
| コードを1行ずつ書く | 自然言語で指示 → 自動生成 |
| 学習期間: 数ヶ月 | 学習期間: 数週間 |

**実例**:
```
【従来】
Reactでボタンを作る方法をGoogle検索
→ 記事を読む
→ コードをコピペ
→ 動かない
→ また検索
→ 30分経過

【Cursor】
Cmd+K → 「Reactでボタンを作って、クリックしたらアラートを表示」
→ 5秒でコード生成
→ 完成
```

#### 1.3 CursorとGitHub Copilotの違い

**GitHub Copilot（月$10）**:
- VSCodeの拡張機能として動作
- コード補完に特化
- コンテキスト理解が限定的

**Cursor（無料版あり / Pro版$20/月）**:
- エディタ自体がAI統合型
- Cmd+K（編集）、Cmd+L（チャット）、Tab補完の3機能
- プロジェクト全体を理解した上で提案
- GPT-4o、Claude 3.5 Sonnetなど、複数のAIモデルを選択可能

---

### SECTION 02: Cursorのインストールと初期設定（25分）

#### 2.1 公式サイトからのダウンロード

**手順**:
1. https://cursor.sh にアクセス
2. 「Download for Free」をクリック
3. Windows/Mac/Linuxから選択
4. インストーラーをダウンロード
5. 指示に従ってインストール

**初回起動時の設定**:
1. 言語設定（日本語化可能）
2. VSCodeからの設定インポート（既にVSCodeを使っている場合）
3. AIモデルの選択（デフォルトはGPT-4o）

#### 2.2 無料プランとProプランの違い

| 項目 | 無料プラン | Proプラン |
|------|-----------|-----------|
| **月額料金** | $0 | $20 |
| **Cmd+K（コード生成）** | 月50回 | 無制限 |
| **Cmd+L（AIチャット）** | 月200メッセージ | 無制限 |
| **Tab補完** | 制限あり | 無制限 |
| **AIモデル** | GPT-4o mini | GPT-4o、Claude 3.5 Sonnet |
| **優先サポート** | なし | あり |

**初心者へのおすすめ**:
- **最初は無料プランで十分**
- 使い切った場合は翌月まで待つか、Proにアップグレード
- 学習用途なら無料プランで問題なし

#### 2.3 おすすめの初期設定

**AIモデルの選択**:
- **GPT-4o**: 最も賢いが、やや遅い（推奨）
- **Claude 3.5 Sonnet**: コード生成に強い
- **GPT-4o mini**: 高速だが、やや精度が落ちる

**ショートカットキーの確認**:
- **Mac**: `Cmd+K`（編集）、`Cmd+L`（チャット）
- **Windows**: `Ctrl+K`（編集）、`Ctrl+L`（チャット）
- **Tab**: 補完の確定

**その他の便利設定**:
- **Auto Save**: ファイルの自動保存を有効化
- **Format On Save**: 保存時にコードを自動整形
- **Prettier**: コードフォーマッター（VSCodeと同様に使える）

---

### SECTION 03: Cmd+K（コード生成・編集）の使い方（30分）

#### 3.1 基本的な使い方

**Cmd+K**は、**コードを生成・編集するための機能**です。

**使用例1: 新規コード生成**
1. HTMLファイルを開く
2. `Cmd+K`（Windows: `Ctrl+K`）を押す
3. 以下のように指示を入力:
```
ボタンを作成して、クリックしたら"Hello, Cursor!"とアラート表示
```
4. Enterを押す
5. 数秒でコードが生成される

**生成されるコード例**:
```html
<button onclick="alert('Hello, Cursor!')">クリック</button>
```

#### 3.2 既存コードの編集

**使用例2: 既存コードの修正**
1. 以下のコードを選択:
```html
<button>ボタン</button>
```
2. `Cmd+K`を押して指示:
```
このボタンを青色にして、クリックしたらアラートを表示
```
3. 自動的に以下に変換される:
```html
<button style="background-color: blue; color: white; padding: 10px; border: none; border-radius: 5px;" onclick="alert('ボタンがクリックされました！')">ボタン</button>
```

#### 3.3 実践：AIにHTMLページを作らせる

**課題**: 自己紹介ページを作成

**手順**:
1. 新規HTMLファイル`profile.html`を作成
2. `Cmd+K`で以下を指示:
```
自己紹介ページを作成。
- タイトル「私のプロフィール」
- 名前の見出し
- 自己紹介文
- 趣味のリスト（3つ）
- CSSでスタイリング（中央揃え、背景色を薄い青）
```
3. 生成されたコードを確認
4. localhost上で表示

**期待される出力**:
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>私のプロフィール</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #e3f2fd;
            text-align: center;
            padding: 50px;
        }
        h1 { color: #1976d2; }
        p { font-size: 18px; line-height: 1.6; }
        ul { list-style: none; padding: 0; }
        li { background: white; margin: 10px auto; padding: 10px; width: 200px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>山田太郎</h1>
    <p>東京在住の大学生です。AIとプログラミングに興味があります。</p>
    <h2>趣味</h2>
    <ul>
        <li>読書</li>
        <li>映画鑑賞</li>
        <li>カフェ巡り</li>
    </ul>
</body>
</html>
```

---

### SECTION 04: Cmd+L（AIチャット）の使い方（25分）

#### 4.1 エラー解決に使う

**Cmd+L**は、**AIと会話形式で質問・相談できる機能**です。

**使用例: エラーの原因を聞く**
1. 以下のコードでエラーが出たとする:
```javascript
const button = document.getElementById('myButton');
button.addEventListener('click', function() {
    alert('Hello!');
}
```
2. エラーメッセージ:
```
Uncaught SyntaxError: missing ) after argument list
```
3. `Cmd+L`を押して質問:
```
このエラーの原因は？
```
4. AIの回答:
```
閉じ括弧が不足しています。正しくは：
button.addEventListener('click', function() {
    alert('Hello!');
});
```

#### 4.2 コードの説明を聞く

**使用例: 複雑なコードの意味を理解する**
1. 以下のコードを選択:
```javascript
const fetchData = async () => {
    const response = await fetch('https://api.example.com/data');
    const data = await response.json();
    return data;
};
```
2. `Cmd+L`で質問:
```
このコードを初心者向けに説明して
```
3. AIの回答:
```
このコードは、非同期処理（async/await）を使って、外部APIからデータを取得しています。

- `async`: この関数は非同期（時間がかかる処理）であることを示す
- `await fetch(...)`: APIにリクエストを送り、レスポンスを待つ
- `await response.json()`: レスポンスをJSONデータに変換
- `return data`: 取得したデータを返す

非同期処理を使うことで、データ取得中も他の処理を止めずに実行できます。
```

#### 4.3 最適なコードを提案してもらう

**使用例: リファクタリング**
1. 以下の冗長なコードを選択:
```javascript
let total = 0;
total = total + 10;
total = total + 20;
total = total + 30;
console.log(total);
```
2. `Cmd+L`で質問:
```
このコードをもっと短く書ける？
```
3. AIの回答:
```javascript
const total = [10, 20, 30].reduce((sum, num) => sum + num, 0);
console.log(total); // 60
```

---

### SECTION 05: Tab補完の活用（20分）

#### 5.1 Tab補完とは？

**Tab補完**は、AIがコードの続きを予測し、**Tabキーで確定する機能**です。

**例**:
1. 以下のように入力途中で：
```javascript
const handleClick = 
```
2. Cursorが自動で続きを提案：
```javascript
const handleClick = () => {
    alert('Button clicked!');
};
```
3. **Tabキー**を押すと、提案が確定される

#### 5.2 効率的なコーディング例

**例1: React Componentの作成**
```javascript
const Button = 
// Tabを押すと自動補完
const Button = ({ onClick, children }) => (
    <button onClick={onClick}>
        {children}
    </button>
);
```

**例2: CSS Flexboxの記述**
```css
.container {
    display: flex;
    /* Tabで自動補完 */
    justify-content: center;
    align-items: center;
    flex-direction: column;
}
```

---

### SECTION 06: 実践演習：AIにTodoアプリを作らせる（40分）

#### 6.1 課題の概要

**目標**: Cursorを使って、完全に動くTodoアプリを作成

**要件**:
- タスクを入力するフォーム
- 追加ボタン
- タスクリスト（動的に表示）
- 削除ボタン（各タスクに）
- シンプルなCSS（見やすいデザイン）

#### 6.2 実装手順（AIに指示するプロンプト）

**ステップ1: 基本構造を作成**
1. `todo.html`を作成
2. `Cmd+K`で指示:
```
Todoアプリを作成。
- 入力フォーム（タスク名を入力）
- 追加ボタン
- タスクリスト（ul/li）
- 削除ボタン（各タスクの横）
- JavaScriptで動的に追加・削除
- CSSで少しデザイン（中央揃え、パステルカラー）
```

**生成されるコード例**:
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Todoアプリ</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            width: 400px;
        }
        input { width: 70%; padding: 10px; border: 1px solid #ddd; }
        button { padding: 10px 20px; background: #667eea; color: white; border: none; cursor: pointer; }
        ul { list-style: none; padding: 0; }
        li { background: #f9f9f9; margin: 10px 0; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; }
        .delete { background: #e74c3c; color: white; border: none; padding: 5px 10px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 Todo List</h1>
        <input type="text" id="taskInput" placeholder="タスクを入力">
        <button onclick="addTask()">追加</button>
        <ul id="taskList"></ul>
    </div>

    <script>
        function addTask() {
            const input = document.getElementById('taskInput');
            const taskText = input.value.trim();
            if (taskText === '') return;

            const li = document.createElement('li');
            li.innerHTML = `
                <span>${taskText}</span>
                <button class="delete" onclick="deleteTask(this)">削除</button>
            `;
            document.getElementById('taskList').appendChild(li);
            input.value = '';
        }

        function deleteTask(button) {
            button.parentElement.remove();
        }

        // Enterキーで追加
        document.getElementById('taskInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') addTask();
        });
    </script>
</body>
</html>
```

**ステップ2: 機能追加**
`Cmd+K`で以下を指示:
```
- タスク完了時に打ち消し線を追加（クリックでトグル）
- LocalStorageに保存して、リロードしても残る
```

**生成されるコード（追加部分）**:
```javascript
// LocalStorageに保存
function saveTasks() {
    const tasks = [];
    document.querySelectorAll('#taskList li span').forEach(span => {
        tasks.push({
            text: span.textContent,
            completed: span.style.textDecoration === 'line-through'
        });
    });
    localStorage.setItem('tasks', JSON.stringify(tasks));
}

// 読み込み時に復元
window.onload = function() {
    const tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
    tasks.forEach(task => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span style="text-decoration: ${task.completed ? 'line-through' : 'none'}" onclick="toggleTask(this)">${task.text}</span>
            <button class="delete" onclick="deleteTask(this)">削除</button>
        `;
        document.getElementById('taskList').appendChild(li);
    });
};

function toggleTask(span) {
    span.style.textDecoration = span.style.textDecoration === 'line-through' ? 'none' : 'line-through';
    saveTasks();
}
```

---

### SECTION 07: プロンプトの書き方のコツ（25分）

#### 7.1 具体的に指示する

**悪い例**:
```
ボタンを作って
```
→ どんなボタン？色は？サイズは？クリックしたら何が起こる？

**良い例**:
```
青色のボタンを作成。
- テキスト: "送信"
- サイズ: 幅200px、高さ50px
- クリックしたら"送信しました"とアラート表示
```

#### 7.2 段階的に指示する

**悪い例**:
```
Todoアプリを作って、完了機能、編集機能、LocalStorage保存、ダークモード対応、アニメーション付きで
```
→ 一度に複雑すぎる指示は、AIが混乱する

**良い例**:
```
ステップ1: 基本的なTodoアプリ（追加・削除のみ）
→ 完成を確認
ステップ2: 完了機能（チェックボックス）を追加
→ 確認
ステップ3: LocalStorageに保存
→ 確認
```

#### 7.3 エラーが出たらそのまま貼り付ける

**効果的な質問方法**:
```
以下のエラーが出ました。原因と解決法を教えて。

Uncaught TypeError: Cannot read properties of null (reading 'addEventListener')
    at script.js:10
```

AIは、エラーメッセージから問題箇所を特定し、解決策を提示してくれます。

---

### SECTION 08: 動画で学ぶ：Cursor実践ガイド（YouTube厳選5本）（60分視聴）

#### 動画1: 【衝撃】CursorでAI開発が変わる！完全ガイド
- **URL**: https://www.youtube.com/watch?v=jSAy06X7KFs
- **再生回数**: 15万回
- **内容**: Cursorの全機能を実演で解説
- **ポイント**: Cmd+K、Cmd+Lの実践的な使い方

#### 動画2: 【実践】Cursorで爆速開発！AI機能の使い方完全版
- **URL**: https://www.youtube.com/watch?v=LWqIWPU1QAY
- **再生回数**: 22万回
- **内容**: 実際にWebアプリを作りながら解説
- **ポイント**: プロンプトの書き方、エラー解決法

#### 動画3: Cursorで作るTodoアプリ（初心者向け）
- **URL**: https://www.youtube.com/watch?v=xxxxx
- **内容**: Todoアプリを0から作成
- **ポイント**: LocalStorage、動的DOM操作

#### 動画4: 【比較】GitHub Copilot vs Cursor、どっちが優秀？
- **URL**: https://www.youtube.com/watch?v=yyyyy
- **内容**: 両者の違いを実演比較
- **ポイント**: コンテキスト理解の違い、料金比較

#### 動画5: Cursorの設定を最適化！プロの開発環境
- **URL**: https://www.youtube.com/watch?v=zzzzz
- **内容**: Cursorのおすすめ設定、拡張機能
- **ポイント**: ショートカットカスタマイズ、テーマ設定

---

### SECTION 09: まとめと次回予告（10分）

#### この講座で学んだこと

✅ Cursorのインストールと初期設定  
✅ Cmd+K（コード生成・編集）の使い方  
✅ Cmd+L（AIチャット）でエラー解決  
✅ Tab補完の活用法  
✅ AIにTodoアプリを作らせる実践演習  
✅ プロンプトの書き方のコツ

#### 次回（Lecture 3）の内容

**Lecture 3: HTML/CSS/JavaScript基礎**
- HTML5の主要タグ（div, section, article, header, footerなど）
- CSSのFlexbox、Grid Layout
- JavaScriptのDOM操作、イベントリスナー
- 実践：レスポンシブなランディングページ作成

**事前準備**:
- CursorでHTMLファイルを自由に作成してみる
- 公式ドキュメント（MDN Web Docs）を軽く眺めておく

---

### 📝 Lecture 2 チェックリスト

**完了したらチェック✅**:
- [ ] Cursorをインストールし、起動できた
- [ ] AIモデル（GPT-4o推奨）を選択した
- [ ] Cmd+K（Ctrl+K）でコードを生成できた
- [ ] Cmd+L（Ctrl+L）でAIに質問できた
- [ ] Tab補完の仕組みを理解した
- [ ] Todoアプリを作成し、localhost上で動作確認した
- [ ] LocalStorageに保存する機能を追加できた
- [ ] プロンプトの書き方のコツを理解した

**全てチェックできたら、Lecture 3へ進みましょう！🚀**

---

それでは、また次回お会いしましょう。
