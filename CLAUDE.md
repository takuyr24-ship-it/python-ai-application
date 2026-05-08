# CLAUDE.md

このファイルは、Claude Code がこのリポジトリで作業する際に参照する説明書です。

## よく使うコマンド

```bash
# 依存パッケージのインストール
pip3 install -r requirements.txt

# アプリの起動（ブラウザが自動で開く）
streamlit run app.py

# ポートを指定して起動したい場合
streamlit run app.py --server.port 8502
```

## プロジェクト概要

個人用のAIライティングツール。Python + Streamlit + Gemini API で構築。
データベースや認証機能はなし。

## ファイル構成

```
app.py            # アプリ本体（全ツール・UIを1ファイルに集約）
requirements.txt  # 依存パッケージ（streamlit, openai, python-dotenv）
.env              # APIキー（gitで管理しない）
.env.example      # .envのテンプレート
CLAUDE.md         # このファイル
```

## コードの構造

すべてのコードは `app.py` 1ファイルに収まっている。

**画面の流れ：**
サイドバーでツールを選択 → `TOOLS` dict でキー名に変換 → `pages` dict で対応する `page_*()` 関数を呼び出し → `call_gpt()` でOpenAI APIを叩いて結果を表示する。

**APIキーの読み込み順：**
1. `.env` ファイルの `GEMINI_API_KEY`
2. サイドバーの入力欄（`st.session_state.api_key`）

この解決は `get_api_key()` 関数が担っている。APIキーは `call_gpt()` 内で `genai.Client(api_key=key)` に渡す。

## ツールの追加方法

新しいライティングツールを追加する場合は以下の3ステップ：

1. `page_xxx()` 関数を定義する
2. `TOOLS` dict に `"絵文字 ラベル名": "キー名"` を追加する
3. `pages` dict に `"キー名": page_xxx` を追加する

## `page_*()` 関数の実装パターン

各ツールページは以下の構成で統一している：

```python
def page_xxx():
    # 1. ヘッダー表示（tool-header / tool-desc クラスを使う）
    st.markdown('<p class="tool-header">アイコン タイトル</p>', unsafe_allow_html=True)
    st.markdown('<p class="tool-desc">説明文</p>', unsafe_allow_html=True)

    # 2. 入力フォーム（st.columns で2カラムに分けることが多い）

    # 3. 生成ボタン（type="primary", use_container_width=True で統一）
    if st.button("生成する", type="primary", use_container_width=True):
        # 4. バリデーション（必須項目が空なら st.warning で返す）
        # 5. call_gpt() を呼んで結果を表示
        # 6. st.download_button でダウンロードボタンを表示
```

## カスタムCSSクラス

`app.py` 冒頭の `st.markdown` で定義しているクラス：

| クラス名 | 用途 |
|---|---|
| `.tool-header` | 各ツールページのタイトル（大きめフォント・太字） |
| `.tool-desc` | タイトル直下のグレー説明文 |
| `.output-box` | 原文と変換後を並べて表示するときのボックス（文体変換ツールで使用） |

## モデルの選択肢と使い分け

サイドバーで選択できるモデル：

| モデル | 特徴 |
|---|---|
| gemini-2.5-flash | デフォルト。最新・高精度・高速 |
| gemini-2.0-flash | 安定版。高速・無料枠あり |
| gemini-1.5-pro | 長文・複雑な指示に向く |

## temperature の設定値

`call_gpt()` の `temperature` はツールの性質に合わせて調整している：

| ツール | temperature | 理由 |
|---|---|---|
| 校正・改善提案 | 0.3 | 正確さ重視 |
| 文章要約 | 0.4 | 忠実な要約 |
| 文体・トーン変換 | 0.6 | ある程度の柔軟性 |
| ブログ・メール | 0.7 | バランス型 |
| SNS投稿文 | 0.8 | 多様なパターン生成 |

## 注意事項

- `.env` は絶対に git にコミットしない（`.gitignore` に追加すること）
- `unsafe_allow_html=True` はカスタムCSSクラスの適用のためだけに使用しており、ユーザー入力を直接HTMLに埋め込んではいけない
- Streamlit はボタンを押すたびにスクリプト全体が再実行される。ユーザー入力の保持が必要な場合は `st.session_state` を使う
