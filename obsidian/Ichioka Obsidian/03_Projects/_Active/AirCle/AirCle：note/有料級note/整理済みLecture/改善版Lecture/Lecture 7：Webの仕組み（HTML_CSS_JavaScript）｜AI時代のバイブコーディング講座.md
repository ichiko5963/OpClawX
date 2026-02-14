# Lecture 7：Webの仕組み（HTML/CSS/JavaScript）｜AI時代のバイブコーディング講座

## 初めに

こんにちはAirCleの運営です！

Webページはどうやって動いているの？

HTML、CSS、JavaScript。Web開発の3大要素、聞いたことありますか？

「HTMLって何？CSSって何？JavaScriptって何？」「それぞれ何が違うの？」「どうやって使うの？」という疑問、多いと思います。

そこで今回、AirCleで実際に「Webの仕組み」を徹底的に検証し、初心者が最短ルートでWebページの構造を理解する方法を詳しく調べてみました。

HTML、CSS、JavaScriptは、Webページを作るための3つの言語です。HTMLが骨組み、CSSが見た目、JavaScriptが動きを担当します。この3つを理解すれば、どんなWebページでも作れるようになります。

この講座では、2025年最新版の最短ルートでWebの仕組みを学びます。HTML/CSS/JavaScriptの役割から、ReactとNext.jsの基礎まで、初心者が絶対に挫折しないように、一つ一つ丁寧に解説していきます。

しかも今回は特別に、実際に手を動かしながら学べる実践演習と、よくあるエラーの解決法まで、余すことなくお届けします。

さらにそれだけではなく、「なぜそうなるのか？」という本質的な理解も詳しく解説し、「Webの仕組みを自在に使いこなして、どんなWebページでも理解できる」知識として落とし込みました。

つまり「実践 → 理解 → 応用」という  
3段階の学び方ができるようになっているんです。

内容としては：

- Webページの三位一体（HTML/CSS/JavaScript）
    
- HTML5の主要タグ
    
- CSSのFlexbox、Grid Layout
    
- JavaScriptのDOM操作、イベントリスナー
    
- ReactとNext.jsの基礎

僕自身もこの講座を通じて、Web開発の見え方がまるで変わりました。  
ただの「コードを書く作業」じゃなく、「ユーザー体験を設計する創造的な作業」としてやっと本当の価値が分かったんです。

もしあなたが  
「Webページがどう動いているか分からない」  
「HTML/CSS/JavaScriptの違いが分からない」  
と思っているなら、この記事は間違いなく最適解になるはずです。

---

## 【ここから本編スタート】

# 📘 Lecture 7: Webの仕組み（HTML/CSS/JavaScript）

学習時間: 4-5時間  
難易度: ★★☆☆☆（初級）  
目標: Web開発の3大要素（HTML/CSS/JavaScript）を理解し、動的なWebページを作成できる

---

## 🎯 この講座で達成できること

- Webページの三位一体（HTML/CSS/JavaScript）を理解する
- HTML5の主要タグを理解し、セマンティックなマークアップができる
- CSSのFlexbox、Grid Layoutでレスポンシブなレイアウトを作成
- JavaScriptでDOM操作、イベント処理を実装
- ReactとNext.jsの基礎を理解する

---

## 📚 セクション構成

### SECTION 01: Webページの三位一体（30分）

#### 1.1 Webサイトは3つの要素だけでできている

Webサイトは、実は3つの要素だけでできています。

HTML: 骨格（構造）
- 見出し、段落、ボタンなどの「部品」を配置する

CSS: 皮膚・服（見た目）
- 色、大きさ、レイアウトを決める

JavaScript: 筋肉・神経（動き）
- ボタンを押したら何か起きる、などの「動作」を制御する

#### 1.2 例えで理解

Webページの例え：

- HTML = 家の骨組み（柱、壁、屋根）
- CSS = 家の見た目（色、デザイン、内装）
- JavaScript = 家の機能（電気、水道、エアコン）

この3つが組み合わさって、動くWebページができます。

#### 1.3 実際の例

実際の例：

```html
<!-- HTML: 骨組み -->
<h1>タイトル</h1>
<button>クリック</button>
```

```css
/* CSS: 見た目 */
h1 {
    color: blue;
    font-size: 24px;
}
button {
    background: red;
    padding: 10px;
}
```

```javascript
// JavaScript: 動き
button.addEventListener('click', () => {
    alert('クリックされました！');
});
```

この3つが組み合わさって、動くWebページができます。

---

### SECTION 02: HTML5の基本とセマンティックタグ（40分）

#### 2.1 HTMLとは？構造を定義する言語

HTML（HyperText Markup Language）は、Webページの構造を定義する言語です。

HTMLの役割:
- ページの骨組みを作る
- 見出し、段落、リスト、画像などの要素を配置
- セマンティック（意味のある）タグで構造を明確にする

#### 2.2 基本的なHTMLの構造

基本的なHTMLの構造:
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ページのタイトル</title>
</head>
<body>
    <!-- ここにコンテンツを書く -->
</body>
</html>
```

各要素の意味：

- `<!DOCTYPE html>` = 「これはHTML5です」という宣言
- `<html lang="ja">` = 「このページは日本語です」という宣言
- `<head>` = ページの情報（タイトル、設定など）
- `<body>` = ページの内容（ここにコンテンツを書く）

全部覚える必要はありません。 AIが全部書いてくれます。

#### 2.3 主要タグ: div, section, article, header, footer, nav, aside

セマンティックタグは、意味を持ったタグです。これらを使うことで、検索エンジンやスクリーンリーダーがページの構造を理解しやすくなります。

主要なセマンティックタグ:

`<header>`
- 意味: ページのヘッダー
- 使用例: ロゴ、ナビゲーション
- 例え: 家の玄関

`<nav>`
- 意味: ナビゲーション
- 使用例: メニュー、リンク集
- 例え: 家の廊下

`<main>`
- 意味: メインコンテンツ
- 使用例: 記事本文
- 例え: 家のリビング

`<section>`
- 意味: セクション
- 使用例: 関連するコンテンツのグループ
- 例え: 家の部屋

`<article>`
- 意味: 記事
- 使用例: 独立したコンテンツ
- 例え: 家の書斎

`<aside>`
- 意味: サイドバー
- 使用例: 補足情報、広告
- 例え: 家の物置

`<footer>`
- 意味: フッター
- 使用例: 著作権情報、リンク
- 例え: 家の地下室

実例: セマンティックな構造:
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>ブログサイト</title>
</head>
<body>
    <header>
        <h1>私のブログ</h1>
        <nav>
            <ul>
                <li><a href="#home">ホーム</a></li>
                <li><a href="#about">について</a></li>
                <li><a href="#contact">お問い合わせ</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <article>
            <h2>記事タイトル</h2>
            <p>記事の本文...</p>
        </article>
    </main>
    
    <aside>
        <h3>関連記事</h3>
        <ul>
            <li>記事1</li>
            <li>記事2</li>
        </ul>
    </aside>
    
    <footer>
        <p>&copy; 2025 私のブログ</p>
    </footer>
</body>
</html>
```

なぜセマンティックタグを使うのか？

1. 検索エンジンが理解しやすい（SEOに有利）
2. スクリーンリーダーが理解しやすい（アクセシビリティ向上）
3. コードが読みやすい（他の人が見てもわかりやすい）

全部覚える必要はありません。 AIが全部書いてくれます。

---

### SECTION 03: CSSの基礎とFlexbox（40分）

#### 3.1 CSSとは？スタイルを定義する言語

CSS（Cascading Style Sheets）は、Webページの見た目を定義する言語です。

CSSの役割:
- 色、サイズ、レイアウトを指定
- レスポンシブデザイン（画面サイズに応じた表示）を実現
- アニメーションやトランジションを追加

#### 3.2 CSSの基本的な書き方

CSSの基本的な書き方:
```css
/* セレクタ { プロパティ: 値; } */
h1 {
    color: blue;
    font-size: 24px;
}
```

各要素の意味：

- `h1` = セレクタ（どの要素にスタイルを適用するか）
- `color: blue;` = プロパティと値（色を青にする）
- `font-size: 24px;` = プロパティと値（フォントサイズを24pxにする）

#### 3.3 セレクタ: class, id, 子孫セレクタ

セレクタは、どの要素にスタイルを適用するかを指定します。

主要なセレクタ:

```css
/* 要素セレクタ */
p { color: red; }

/* クラスセレクタ */
.button { background: blue; }

/* IDセレクタ */
#header { height: 100px; }

/* 子孫セレクタ */
.container p { color: green; }
```

HTMLでの使い方:
```html
<div class="container">
    <p>この段落は緑色</p>
    <button class="button">このボタンは青色</button>
</div>
```

全部覚える必要はありません。 AIが全部書いてくれます。

#### 3.4 Flexbox: 横並び・縦並びの自由自在なレイアウト

Flexboxは、柔軟なレイアウトを作るためのCSS機能です。

Flexboxの基本:
```css
.container {
    display: flex;
    flex-direction: row; /* 横並び（デフォルト） */
    justify-content: center; /* 横方向の配置 */
    align-items: center; /* 縦方向の配置 */
}
```

Flexboxの主要プロパティ:

`display: flex`
- 意味: Flexboxを有効化
- 値の例: -
- 例え: レイアウトモードをON

`flex-direction`
- 意味: 方向
- 値の例: `row`（横）、`column`（縦）
- 例え: 横並び or 縦並び

`justify-content`
- 意味: 横方向の配置
- 値の例: `center`、`space-between`
- 例え: 横方向の位置

`align-items`
- 意味: 縦方向の配置
- 値の例: `center`、`flex-start`
- 例え: 縦方向の位置

`flex-wrap`
- 意味: 折り返し
- 値の例: `wrap`、`nowrap`
- 例え: 折り返すかどうか

全部覚える必要はありません。 AIが全部書いてくれます。

---

### SECTION 04: JavaScriptの基礎（40分）

#### 4.1 JavaScriptとは？動きを制御する言語

JavaScript（ジャバスクリプト）は、Webページの動きを制御する言語です。

JavaScriptの役割:
- ボタンを押したら何か起きるなどの「動作」を制御
- フォームの入力チェック
- データの計算・処理

#### 4.2 変数: const, let

変数は、データを保存する箱です。

変数の宣言方法:
```javascript
// const: 再代入不可（推奨）
const name = "山田太郎";

// let: 再代入可能
let age = 20;
age = 21; // OK
```

なぜconstを使うのか？

- 間違えて値を変えることを防げる
- コードが読みやすい
- AIも推奨している

全部覚える必要はありません。 AIが全部書いてくれます。

#### 4.3 関数: アロー関数

関数は、処理をまとめたものです。

関数の書き方:
```javascript
// アロー関数（推奨）
const greet = (name) => {
    return `こんにちは、${name}さん！`;
};

// 1行で書ける場合
const greet2 = (name) => `こんにちは、${name}さん！`;
```

全部覚える必要はありません。 AIが全部書いてくれます。

#### 4.4 DOM操作: 要素の取得と操作

DOM（Document Object Model）は、HTMLをJavaScriptで操作するための仕組みです。

要素の取得方法:
```javascript
// IDで取得
const header = document.getElementById('header');

// クラスで取得（最初の1つ）
const button = document.querySelector('.button');

// クラスで取得（全て）
const buttons = document.querySelectorAll('.button');
```

要素の操作:
```javascript
// テキストを変更
element.textContent = "新しいテキスト";

// クラスを追加
element.classList.add('active');
```

全部覚える必要はありません。 AIが全部書いてくれます。

#### 4.5 イベント: click, input

イベントリスナーは、ユーザーの操作に反応する機能です。

```javascript
// クリックイベント
button.addEventListener('click', () => {
    alert('クリックされました！');
});
```

全部覚える必要はありません。 AIが全部書いてくれます。

---

### SECTION 05: ReactとNext.jsの基礎（30分）

#### 5.1 Reactとは？

でも、今のWebアプリはもっと複雑です。

そこで生まれたのが React（リアクト）。

Reactは、画面を小さな「部品（コンポーネント）」に分けて、組み合わせる技術です。

- 「ボタン部品」「ヘッダー部品」「カード部品」
- 部品を組み合わせるだけでアプリができる
- AIは、この「部品作り」がめちゃくちゃ得意

#### 5.2 Reactの例え

Reactの例え：

- HTML = レゴブロックの説明書
- React = レゴブロックの部品
- コンポーネント = 1つの部品（ボタン、カードなど）

部品を組み合わせるだけでアプリができます。

#### 5.3 Next.jsとは？

Next.js（ネクストジェイエス） は、Reactを使って「Webサイト全体」を作るためのフレームワークです。

Reactが「エンジン」なら、Next.jsは「車体」です。

Next.jsの特徴：
- ルーティング（ページ遷移）が簡単
- サーバーサイドレンダリング（高速表示）
- API Routes（バックエンド機能）

全部覚える必要はありません。 AIが全部書いてくれます。

---

## 📝 今日のまとめ

1. HTML → 骨組み（家の骨組み）
2. CSS → 見た目（家の見た目）
3. JavaScript → 動き（家の機能）
4. React → 部品を組み合わせる技術（レゴブロック）
5. Next.js → Reactの完全装備セット（車体）

---

## 📚 今日覚えた用語

HTML
  - 意味: Webページの骨組みを書く言語
  - 例え: 家の骨組み（柱、壁、屋根）

CSS
  - 意味: Webページの見た目（色・大きさ）を書く言語
  - 例え: 家の見た目（色、デザイン、内装）

JavaScript
  - 意味: Webページの動き（ボタンを押したら何か起きる）を書く言語
  - 例え: 家の機能（電気、水道、エアコン）

セマンティックタグ
  - 意味: 意味を持ったタグ（header, nav, mainなど）
  - 例え: 家の各部屋（玄関、リビング、書斎）

Flexbox
  - 意味: 柔軟なレイアウトを作るCSS機能
  - 例え: レイアウトモード

DOM
  - 意味: HTMLをJavaScriptで操作するための仕組み
  - 例え: HTMLとJavaScriptの橋渡し

React
  - 意味: 部品を組み合わせる技術
  - 例え: レゴブロック

Next.js
  - 意味: Reactの完全装備セット
  - 例え: 車体


---

## 🎯 宿題

1. 簡単なHTMLページを作ってみてください（AIに頼んでOK）
2. CSSで色を変えてみてください（AIに頼んでOK）
3. JavaScriptでボタンを追加してみてください（AIに頼んでOK）
4. ブラウザの開発者ツール（F12）を開いて、HTMLの構造を確認してみてください

次回は「AIにデザインを作らせる（v0）」を学びます！

---

## 🔗 次回への接続

次回（Lecture 8）では、AIにデザインを作らせる（v0）を学びます。

今日、HTML/CSS/JavaScriptの基礎を学びました。

でも、デザインが苦手だと、カッコいいUIが作れないですよね？

次回は、v0というAIツールを使って、言葉だけでプロ級のデザインを作ります。

なぜ次回でv0を学ぶのか？

デザインは、センスが必要だと思われがちです。

でも、v0を使えば、言葉だけでプロ級のデザインが作れます。

「カッコいい感じで」「モダンなデザインで」と言うだけで、AIが完璧なデザインを生成してくれます。

次回でこれを学べば、デザインのセンスがなくても、カッコいいUIが作れるようになります。

それでは、また次回！
