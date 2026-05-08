# Python・Streamlit・Gemini API で作る AIライティングツール｜コード完全解説

> この記事では、AIライティングツールのコード（app.py）を  
> **プログラミング初心者でもわかるように**、一行ずつ丁寧に解説します。

---

## そもそもこのアプリは何をするもの？

ブラウザで動く「AI文章作成ツール」です。  
左のメニューからツールを選んで、情報を入力してボタンを押すと、AIが文章を自動で書いてくれます。

使えるツールは全部で6種類：

- 📝 ブログ記事を書いてくれる
- 📧 メールの返信文を考えてくれる
- 📄 長い文章を要約してくれる
- 🎨 文体・トーンを変換してくれる
- 📱 SNSの投稿文を作ってくれる
- 🔍 文章の誤りを校正してくれる

---

## 使っている技術は3つだけ

| 技術 | 一言で言うと |
|---|---|
| **Python** | プログラムを書く言語。今回のアプリはPythonで書かれている |
| **Streamlit** | Pythonだけでブラウザの画面（ボタンや入力欄）を作れる便利な道具 |
| **Gemini API** | GoogleのAI（Gemini）をプログラムから呼び出すための仕組み |

---

## コードの全体像

`app.py` は1つのファイルだけで完結しています。  
上から順に読んでいくと、こんな流れになっています。

```
① 道具を揃える（ライブラリの読み込み）
② 画面の見た目を設定する
③ AIと話す仕組みを作る  ← アプリの心臓部
④ 左メニュー（サイドバー）を作る
⑤ 各ツールのページを作る（6種類）
⑥ 選ばれたページを表示する
```

では、一つずつ見ていきましょう。

---

## ① 道具を揃える（1〜7行目）

```python
import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
```

`import` は「この道具を使いますよ」という宣言です。  
料理を始める前に「包丁・まな板・鍋を用意する」のと同じイメージです。

| コード | 意味 |
|---|---|
| `import streamlit as st` | 画面を作る道具を「st」という短い名前で使う |
| `from google import genai` | GeminiのAIを呼び出す道具を用意する |
| `import os` | パソコンのファイルを読む道具を用意する |
| `load_dotenv()` | `.env` ファイルに書いたAPIキーを読み込む |

`.env` ファイルとは、APIキーなどの秘密情報を書いておくファイルです。  
`load_dotenv()` を最初に呼ぶことで、プログラムの中でAPIキーが使えるようになります。

---

## ② 画面の見た目を設定する（8〜32行目）

```python
st.set_page_config(
    page_title="AI Writing Tool",
    page_icon="✍️",
    layout="wide",
)
```

これはブラウザのタブに表示される情報を設定しています。

- `page_title` → タブに表示されるタイトル
- `page_icon` → タブに表示されるアイコン
- `layout="wide"` → 画面を横幅いっぱいに広げる

---

続いてCSSという「見た目の設定」が書かれています。

```css
.tool-header { font-size: 1.6rem; font-weight: 700; }
```

CSSはHTMLの見た目を整えるための言語で、「文字を大きくする」「色を変える」などを指定できます。  
ここでは各ツールのタイトルや説明文のデザインを定義しています。

---

## ③ AIと話す仕組みを作る（35〜53行目）

ここがアプリで一番大切な部分です。  
「関数」という概念が登場しますが、**関数とは「ひとまとまりの処理に名前をつけたもの」**です。  
料理レシピに例えると、「カレーの作り方」という名前をつけた手順書のようなものです。

---

### 関数①：`get_api_key()` ─ APIキーを探してくる

```python
def get_api_key():
    return os.getenv("GEMINI_API_KEY") or st.session_state.get("api_key", "")
```

**APIキー**とは、GeminiのAIを使うための「合言葉」のようなものです。  
この関数は2つの場所を順番に探します：

1. まず `.env` ファイルの中を見る
2. なければ、サイドバーの入力欄に入力された値を使う

---

### 関数②：`call_gpt()` ─ AIに質問して答えをもらう

```python
def call_gpt(system, user, model="gemini-2.5-flash", temperature=0.7):
    key = get_api_key()
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model=model,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
        ),
    )
    return response.text.strip()
```

この関数が実際にGeminiのAIと会話する処理です。  
4つの設定（引数）を受け取ります：

| 設定名 | 意味 | 具体例 |
|---|---|---|
| `system` | AIへの役割指示 | 「あなたはプロのブログライターです」 |
| `user` | ユーザーのお願い内容 | 「Pythonについての記事を書いて」 |
| `model` | 使うAIの種類 | `gemini-2.5-flash`（高性能・高速） |
| `temperature` | 回答のランダム度（0〜1） | 0に近いほど正確、1に近いほど自由 |

`system` と `user` の違いを料理で例えると：
- `system`＝「和食の料理人として振る舞って」（役割の設定）
- `user`＝「肉じゃがを作って」（具体的なお願い）

`temperature` は創造性のツマミです。  
校正（正確さが必要）は `0.3`、SNS投稿（バラエティが欲しい）は `0.8` と、ツールごとに調整しています。

---

## ④ 左メニュー（サイドバー）を作る（56〜82行目）

```python
TOOLS = {
    "📝 ブログ記事執筆": "blog",
    "📧 メール返信生成": "email",
    "📄 文章要約":       "summary",
    "🎨 文体・トーン変換": "tone",
    "📱 SNS投稿文生成":  "sns",
    "🔍 校正・改善提案": "proofread",
}
```

`TOOLS` は**辞書（dict）**というデータの入れ物です。  
左側が「画面に表示する名前」、右側が「プログラム内部で使う短い名前」です。

辞書は現実の辞書と同じで「単語（キー）→ 意味（値）」の対応表です。  
ここでは「📝 ブログ記事執筆 → blog」という対応を6つ登録しています。

```python
selected_label = st.radio("", list(TOOLS.keys()))
tool = TOOLS[selected_label]
```

`st.radio` でラジオボタンを画面に表示します。  
ユーザーが選んだラベル（例：「📝 ブログ記事執筆」）から、対応するキー（`"blog"`）を取り出します。

---

## ⑤ 各ツールのページを作る（85〜348行目）

6つのツールはすべて同じパターンで作られています。  
`page_blog()` を例に見てみましょう。

### ステップ1：タイトルと説明を表示する

```python
st.markdown('<p class="tool-header">📝 ブログ記事執筆</p>', unsafe_allow_html=True)
st.markdown('<p class="tool-desc">テーマや条件を入力するとブログ記事を自動生成します。</p>', unsafe_allow_html=True)
```

`st.markdown` はMarkdown（見出しや太字などが使えるテキスト形式）を表示する命令です。

---

### ステップ2：入力フォームを並べる

```python
col1, col2 = st.columns(2)
with col1:
    topic = st.text_input("記事のテーマ *")
with col2:
    tone = st.selectbox("文体", ["わかりやすく・親しみやすい", ...])
```

`st.columns(2)` で画面を左右2列に分割しています。  
`with col1:` の中に書いたパーツは左側に、`with col2:` は右側に配置されます。

| 命令 | 表示されるもの |
|---|---|
| `st.text_input()` | 1行テキスト入力欄 |
| `st.text_area()` | 複数行テキスト入力欄 |
| `st.selectbox()` | ドロップダウン選択 |
| `st.multiselect()` | 複数選択できるリスト |
| `st.checkbox()` | チェックボックス |

---

### ステップ3：ボタンを押したら動く

```python
if st.button("記事を生成する", type="primary", use_container_width=True):
    if not topic:
        st.warning("テーマを入力してください。")
        return

    sys_prompt = "あなたはプロのブログライターです..."
    user_prompt = f"テーマ: {topic}, 文体: {tone}..."

    result = call_gpt(sys_prompt, user_prompt)

    st.success("生成完了！")
    st.markdown(result)
    st.download_button("テキストをダウンロード", result, file_name="blog_article.txt")
```

`if st.button(...)` は「ボタンが押されたとき」という条件です。  
Streamlitは**ボタンを押すたびにプログラム全体が最初から再実行されます**。  
そのため `if st.button(...)` の中に書くことで「ボタンが押されたときだけ動く」処理を実現しています。

`f"テーマ: {topic}..."` の `f` は**f文字列**といい、`{}` の中に変数を埋め込める便利な書き方です。  
ユーザーが入力した内容をそのままAIへのお願い文に組み込んでいます。

---

## ⑥ 選ばれたページを表示する（351〜359行目）

```python
pages = {
    "blog":      page_blog,
    "email":     page_email,
    "summary":   page_summary,
    "tone":      page_tone,
    "sns":       page_sns,
    "proofread": page_proofread,
}

pages[tool]()
```

`pages` も辞書です。キーが `"blog"` なら `page_blog` 関数、`"email"` なら `page_email` 関数という対応を登録しています。

最後の `pages[tool]()` がページを切り替える核心です。  
サイドバーで選ばれた `tool`（例：`"blog"`）をキーにして対応する関数を呼び出します。

`page_blog` と `page_blog()` の違いに注目してください：
- `page_blog` → 関数そのもの（レシピを手に持っているだけ）
- `page_blog()` → 関数を実行する（実際に料理を作り始める）

`()` をつけることで「今すぐ実行」の意味になります。

---

## まとめ：アプリ全体のデータの流れ

```
【ユーザー】サイドバーでツールを選ぶ
               ↓
【TOOLS辞書】"📝 ブログ記事執筆" → "blog" に変換
               ↓
【pages辞書】"blog" → page_blog() を呼び出す
               ↓
【ユーザー】フォームに入力してボタンを押す
               ↓
【call_gpt()】役割指示＋お願い内容をGeminiに送る
               ↓
【Gemini API】AIが文章を生成して返す
               ↓
【画面】結果を表示＋ダウンロードボタン
```

---

## 新しいツールを追加するには？

このパターンさえ覚えれば、自分でツールを追加できます。

**手順1：** `page_xxx()` 関数を新しく書く  
**手順2：** `TOOLS` 辞書に1行追加する  
**手順3：** `pages` 辞書に1行追加する

たったこれだけです。あとはStreamlitが自動でメニューに表示してくれます。
