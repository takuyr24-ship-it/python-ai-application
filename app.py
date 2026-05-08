import streamlit as st
from google import genai
from google.genai import types
import os
import html
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

st.set_page_config(
    page_title="AI Writing Tool",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── スタイル ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:opsz,wght@8..18,300;8..18,400;8..18,500;8..18,600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --bg:           #FAF9F7;
    --bg-sidebar:   #F3F0EB;
    --bg-card:      #FFFFFF;
    --bg-input:     #FFFFFF;
    --bg-warm:      #F5F2EC;
    --border:       #E3DDD7;
    --border-dim:   #EDE9E3;
    --text:         #17140E;
    --text-dim:     #675F56;
    --text-muted:   #A09488;
    --accent:       #2D5A8E;
    --accent-light: rgba(45,90,142,0.07);
    --accent-mid:   rgba(45,90,142,0.18);
    --accent-hover: #1D4A7C;
    --success:      #2A7A4E;
    --success-bg:   rgba(42,122,78,0.07);
    --warn:         #8A6020;
    --warn-bg:      rgba(138,96,32,0.07);
    --danger:       #A83030;
    --danger-bg:    rgba(168,48,48,0.07);
    --font-serif:   'Libre Baskerville', Georgia, serif;
    --font-sans:    'Plus Jakarta Sans', system-ui, sans-serif;
    --font-mono:    'IBM Plex Mono', monospace;
}

/* ─ Base ───────────────────────────────────────────────────────────── */
.stApp {
    background: var(--bg) !important;
    font-family: var(--font-sans) !important;
}
*, *::before, *::after { box-sizing: border-box; }

/* ─ Hide Streamlit chrome ──────────────────────────────────────────── */
#MainMenu, footer,
[data-testid="stHeader"],
[data-testid="stDecoration"],
div[data-testid="stSidebarNav"] { display: none !important; }

/* ─ Main content area ──────────────────────────────────────────────── */
.main .block-container {
    padding: 2.5rem 3.5rem 4rem !important;
    max-width: 860px !important;
}

/* ─ Sidebar ────────────────────────────────────────────────────────── */
[data-testid="stSidebar"],
section[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
    position: relative !important;
}
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent);
    opacity: 0.65;
    z-index: 10;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 2rem 1.4rem 2rem 1.5rem !important;
}

/* ─ Global typography ──────────────────────────────────────────────── */
h1, h2, h3, h4 {
    font-family: var(--font-serif) !important;
    color: var(--text) !important;
}

/* ─ Dividers ───────────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border-dim) !important;
    margin: 1rem 0 !important;
}

/* ─ Form labels ────────────────────────────────────────────────────── */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stNumberInput"] label {
    font-family: var(--font-sans) !important;
    font-size: 0.69rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--text-muted) !important;
}

/* ─ Text inputs ────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    color: var(--text) !important;
    font-family: var(--font-sans) !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 0.7rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-light) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: var(--text-muted) !important;
    font-size: 0.84rem !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    font-family: var(--font-mono) !important;
    font-size: 0.77rem !important;
    letter-spacing: 0.02em !important;
    background: var(--bg) !important;
    border-color: var(--border) !important;
}

/* ─ Textarea ───────────────────────────────────────────────────────── */
[data-testid="stTextArea"] textarea {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    color: var(--text) !important;
    font-family: var(--font-sans) !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    padding: 0.6rem 0.75rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-light) !important;
    outline: none !important;
}

/* ─ Selectbox ──────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    color: var(--text) !important;
    font-family: var(--font-sans) !important;
    font-size: 0.88rem !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-light) !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: var(--bg) !important;
    font-size: 0.84rem !important;
}

/* ─ Multiselect ────────────────────────────────────────────────────── */
[data-testid="stMultiSelect"] > div > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    font-family: var(--font-sans) !important;
    font-size: 0.88rem !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: var(--accent-light) !important;
    border: 1px solid var(--accent-mid) !important;
    color: var(--accent) !important;
    border-radius: 2px !important;
    font-size: 0.77rem !important;
    font-family: var(--font-sans) !important;
    font-weight: 500 !important;
}

/* ─ Checkbox ───────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] label span {
    font-family: var(--font-sans) !important;
    font-size: 0.87rem !important;
    font-weight: 400 !important;
    color: var(--text-dim) !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

/* ─ Radio / tool nav ───────────────────────────────────────────────── */
[data-testid="stRadio"] div[role="radiogroup"],
[data-testid="stRadio"] > div > div {
    gap: 0 !important;
    flex-direction: column !important;
}
[data-testid="stRadio"] label {
    padding: 0.58rem 0.85rem !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 3px 3px 0 !important;
    cursor: pointer !important;
    transition: all 0.12s ease !important;
    font-size: 0.875rem !important;
    color: var(--text-dim) !important;
    font-family: var(--font-sans) !important;
    font-weight: 400 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    display: flex !important;
    align-items: center !important;
    margin: 1px 0 !important;
    background: transparent !important;
}
[data-testid="stRadio"] label:hover {
    background: var(--accent-light) !important;
    color: var(--accent) !important;
    border-left-color: var(--accent-mid) !important;
}
[data-testid="stRadio"] [data-baseweb="radio"]:has(input:checked) label {
    background: var(--accent-light) !important;
    color: var(--accent) !important;
    border-left-color: var(--accent) !important;
    font-weight: 600 !important;
}
/* Fallback for browsers without :has() */
[data-testid="stRadio"] [aria-checked="true"] label {
    background: var(--accent-light) !important;
    color: var(--accent) !important;
    border-left-color: var(--accent) !important;
    font-weight: 600 !important;
}
[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child,
[data-testid="stRadio"] svg { display: none !important; }

/* ─ Primary button ─────────────────────────────────────────────────── */
button[data-testid="baseButton-primary"],
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: var(--font-sans) !important;
    font-size: 0.79rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.14s ease !important;
    box-shadow: 0 1px 4px rgba(45,90,142,0.22) !important;
}
button[data-testid="baseButton-primary"]:hover,
.stButton > button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
    box-shadow: 0 3px 14px rgba(45,90,142,0.28) !important;
    transform: translateY(-1px) !important;
}
button[data-testid="baseButton-primary"] p,
button[data-testid="baseButton-primary"] span,
button[data-testid="baseButton-primary"] [data-testid="stMarkdownContainer"] {
    color: #FFFFFF !important;
}

/* ─ Secondary / download button ────────────────────────────────────── */
button[data-testid="baseButton-secondary"],
.stButton > button[kind="secondary"],
[data-testid="stDownloadButton"] button {
    background: transparent !important;
    color: var(--accent) !important;
    border: 1.5px solid var(--accent-mid) !important;
    border-radius: 3px !important;
    font-family: var(--font-sans) !important;
    font-size: 0.79rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    transition: all 0.14s ease !important;
}
button[data-testid="baseButton-secondary"]:hover,
[data-testid="stDownloadButton"] button:hover {
    background: var(--accent-light) !important;
    border-color: var(--accent) !important;
}

/* ─ Alerts ─────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 3px !important;
    font-family: var(--font-sans) !important;
    font-size: 0.87rem !important;
}
.stSuccess > div,
[class*="stSuccess"] [data-testid="stAlert"] {
    background: var(--success-bg) !important;
    border-left: 3px solid var(--success) !important;
    color: var(--success) !important;
}
.stWarning > div,
[class*="stWarning"] [data-testid="stAlert"] {
    background: var(--warn-bg) !important;
    border-left: 3px solid var(--warn) !important;
    color: var(--warn) !important;
}
.stError > div,
[class*="stError"] [data-testid="stAlert"] {
    background: var(--danger-bg) !important;
    border-left: 3px solid var(--danger) !important;
    color: var(--danger) !important;
}

/* ─ Code blocks ─────────────────────────────────────────────────────── */
pre, .stCode pre {
    background: var(--bg-warm) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
    color: var(--text) !important;
}
code {
    font-family: var(--font-mono) !important;
    background: var(--bg-warm) !important;
    color: var(--text) !important;
    font-size: 0.82rem !important;
    border-radius: 2px !important;
    padding: 0.1em 0.3em !important;
}

/* ─ Dropdown menus ──────────────────────────────────────────────────── */
[data-baseweb="popover"] > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.09) !important;
}
[data-baseweb="menu"] li {
    font-family: var(--font-sans) !important;
    font-size: 0.87rem !important;
    color: var(--text-dim) !important;
    background: var(--bg-card) !important;
}
[data-baseweb="menu"] li:hover { background: var(--accent-light) !important; color: var(--accent) !important; }
[data-baseweb="menu"] [aria-selected="true"] { background: var(--accent-light) !important; color: var(--accent) !important; font-weight: 600 !important; }

/* ─ Markdown output ─────────────────────────────────────────────────── */
[data-testid="stMarkdownContainer"] {
    font-family: var(--font-sans) !important;
    font-size: 0.92rem !important;
    line-height: 1.78 !important;
    color: var(--text) !important;
}
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    font-family: var(--font-serif) !important;
    color: var(--text) !important;
    margin-top: 1.5em !important;
    margin-bottom: 0.5em !important;
}
[data-testid="stMarkdownContainer"] h2 {
    font-size: 1.2rem !important;
    border-bottom: 1px solid var(--border-dim) !important;
    padding-bottom: 0.3em !important;
}
[data-testid="stMarkdownContainer"] h3 { font-size: 1rem !important; }
[data-testid="stMarkdownContainer"] li { margin-bottom: 0.3em !important; color: var(--text) !important; }
[data-testid="stMarkdownContainer"] strong { font-weight: 600 !important; }

/* ─ Subheader (tone comparison) ────────────────────────────────────── */
[data-testid="stHeadingWithActionElements"] h3,
.stSubheader h3 {
    font-family: var(--font-serif) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    margin-bottom: 0.6rem !important;
}

/* ─ Scrollbar ───────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ─ Custom classes ──────────────────────────────────────────────────── */
.tool-header {
    font-family: 'Libre Baskerville', Georgia, serif !important;
    font-size: 1.95rem !important;
    font-weight: 700 !important;
    color: #17140E !important;
    letter-spacing: -0.015em !important;
    line-height: 1.15 !important;
    margin: 0 0 0.35rem 0 !important;
}
.tool-header::before {
    content: '';
    display: block;
    width: 2rem;
    height: 2.5px;
    background: #2D5A8E;
    margin-bottom: 0.9rem;
    border-radius: 2px;
}
.tool-desc {
    color: #A09488 !important;
    font-size: 0.875rem !important;
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
    margin: 0 0 2rem 0 !important;
    line-height: 1.55 !important;
}
.output-box {
    background: #F5F2EC !important;
    border: 1px solid #E3DDD7 !important;
    border-radius: 4px !important;
    padding: 1.2rem 1.4rem !important;
    white-space: pre-wrap !important;
    font-size: 0.9rem !important;
    line-height: 1.78 !important;
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
    color: #17140E !important;
}
</style>
""", unsafe_allow_html=True)

# ─── API クライアント ──────────────────────────────────────────────────────
def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY") or st.session_state.get("api_key", "")

def call_gpt(system: str, user: str, model: str = "gemini-2.5-flash", temperature: float = 0.7) -> str:
    key = get_api_key()
    if not key:
        st.error("APIキーが設定されていません。サイドバーに Gemini API Key を入力するか、Streamlit Cloud の Secrets に GEMINI_API_KEY を登録してください。")
        return ""
    client = genai.Client(api_key=key)
    try:
        with st.spinner("生成中..."):
            response = client.models.generate_content(
                model=model,
                contents=user,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=temperature,
                ),
            )
        return response.text.strip()
    except Exception as e:
        err = str(e)
        if "API_KEY" in err.upper() or "401" in err or "403" in err:
            st.error("APIキーが無効です。正しい Gemini API Key を設定してください。")
        elif "429" in err or "QUOTA" in err.upper():
            st.error("APIの利用制限に達しました。しばらく待ってから再試行してください。")
        elif "404" in err or "not found" in err.lower():
            st.error(f"モデル '{model}' が見つかりません。サイドバーで別のモデルを選択してください。")
        else:
            st.error(f"エラーが発生しました: {e}")
        return ""

# ─── サイドバー ──────────────────────────────────────────────────────────────
TOOLS = {
    "📝 ブログ記事執筆":   "blog",
    "📧 メール返信生成":   "email",
    "📄 文章要約":         "summary",
    "🎨 文体・トーン変換": "tone",
    "📱 SNS投稿文生成":    "sns",
    "🔍 校正・改善提案":   "proofread",
    "🌐 翻訳":             "translate",
}

with st.sidebar:
    st.markdown("""
<div style="padding-bottom:0.6rem;">
  <div style="font-family:'Libre Baskerville',Georgia,serif;font-size:1.4rem;font-weight:700;color:#17140E;line-height:1.15;letter-spacing:-0.01em;">✍️ AI Writing Tool</div>
  <div style="font-family:'Plus Jakarta Sans',system-ui,sans-serif;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.14em;color:#A09488;margin-top:0.4rem;">Powered by Gemini</div>
</div>
""", unsafe_allow_html=True)
    st.divider()

    if "api_key" not in st.session_state:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")
    api_input = st.text_input("Gemini API Key", value=st.session_state.api_key,
                               type="password", placeholder="AIza...")
    if api_input:
        st.session_state.api_key = api_input

    st.divider()
    st.markdown('<p style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:0.65rem;font-weight:600;text-transform:uppercase;letter-spacing:0.13em;color:#A09488;margin:0.1rem 0 0.6rem 0.85rem;">ツールを選択</p>', unsafe_allow_html=True)
    selected_label = st.radio("ツール選択", list(TOOLS.keys()), label_visibility="collapsed")
    tool = TOOLS[selected_label]

    st.divider()
    model = st.selectbox("モデル", ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"], index=0)

# ─── ブログ記事執筆 ──────────────────────────────────────────────────────────
def page_blog():
    st.markdown('<p class="tool-header">📝 ブログ記事執筆</p>', unsafe_allow_html=True)
    st.markdown('<p class="tool-desc">テーマや条件を入力するとブログ記事を自動生成します。</p>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        topic    = st.text_input("記事のテーマ *", placeholder="例: 初心者向けPythonの始め方")
        audience = st.text_input("ターゲット読者", placeholder="例: プログラミング初学者")
        keywords = st.text_input("キーワード（カンマ区切り）", placeholder="例: Python, 初心者, 無料")
    with col2:
        tone   = st.selectbox("文体", ["わかりやすく・親しみやすい", "丁寧・フォーマル",
                                        "情熱的・エネルギッシュ", "専門的・論理的"])
        length = st.selectbox("文字数の目安", ["500〜800字（短め）", "1000〜1500字（標準）",
                                               "2000〜3000字（長め）"])
        sections = st.multiselect("含めるセクション",
            ["導入・フック", "背景・課題", "解決策・方法", "具体例・事例",
             "まとめ・CTA", "FAQ"],
            default=["導入・フック", "解決策・方法", "まとめ・CTA"])

    extra = st.text_area("追加の指示・補足情報", height=80, placeholder="例: SEOを意識して書いてください", max_chars=500)

    if st.button("記事を生成する", type="primary", use_container_width=True):
        if not topic:
            st.warning("テーマを入力してください。")
            return
        sys_prompt = """あなたはSEOとコンテンツマーケティングの専門家です。
検索上位を狙える高品質な日本語ブログ記事を作成してください。

【SEOの基本ルール】
- 記事タイトル（H1）にメインキーワードを必ず含める
- 最初の100字以内にメインキーワードを自然に入れる
- H2・H3見出しにも関連キーワードをバランスよく含める
- キーワードは不自然にならない範囲で本文中に繰り返す（詰め込みは逆効果）
- 検索意図（なぜそのキーワードで検索するのか）に正確に答える内容にする

【読者を引き込む文章のルール】
- 冒頭で「読者の悩みや疑問」に共感してから解決策を提示する
- 一文は60字以内を目安にし、読みやすい長さに保つ
- 専門用語を使う場合は必ず平易な言葉で補足説明を加える
- 箇条書きや表を積極的に使い、情報を視覚的に整理する
- 各セクションの最後に次のセクションへの橋渡し文を入れる

【記事の構成ルール】
- タイトルは「数字・疑問・ベネフィット」のいずれかを含めると効果的
- リード文（冒頭）で「この記事を読むと何がわかるか」を明示する
- まとめの直前に読者へのアクション（次のステップ）を促す
- まとめは箇条書きで記事全体のポイントを3〜5つに整理する"""
        user_prompt = f"""以下の条件でブログ記事を作成してください。

テーマ: {topic}
ターゲット読者: {audience or '一般読者'}
文体: {tone}
文字数の目安: {length}
含めるセクション: {', '.join(sections) if sections else '自由に構成'}
キーワード: {keywords or 'なし'}
追加指示: {extra or 'なし'}

記事のタイトルから始め、各セクションに見出し（##）を使って構成してください。"""
        result = call_gpt(sys_prompt, user_prompt, model=model)
        if result:
            st.success("生成完了！")
            st.markdown("---")
            st.markdown(result)
            st.download_button("テキストをダウンロード", result,
                               file_name="blog_article.txt", mime="text/plain")

# ─── メール返信生成 ──────────────────────────────────────────────────────────
def page_email():
    st.markdown('<p class="tool-header">📧 メール返信生成</p>', unsafe_allow_html=True)
    st.markdown('<p class="tool-desc">受信メールと返信の意図を入力すると、返信文を作成します。</p>',
                unsafe_allow_html=True)

    original = st.text_area("受信したメールの内容 *", height=180,
                             placeholder="ここに受信メールの本文を貼り付けてください...", max_chars=3000)
    col1, col2 = st.columns(2)
    with col1:
        intent = st.text_area("返信の意図・伝えたいこと *", height=120,
                               placeholder="例: 参加を承諾し、日程を確認したい", max_chars=500)
        sender_name = st.text_input("自分の名前（署名用）", placeholder="例: 山田太郎")
    with col2:
        tone_email = st.selectbox("返信の文体",
            ["丁寧・ビジネス", "カジュアル・フレンドリー", "簡潔・シンプル", "フォーマル・敬語"])
        lang = st.selectbox("言語", ["日本語", "英語", "日英両方"])

    if st.button("返信文を生成する", type="primary", use_container_width=True):
        if not original or not intent:
            st.warning("受信メールの内容と返信の意図を入力してください。")
            return
        sys_prompt = "あなたはメールコミュニケーションの専門家です。適切で自然なメール返信文を作成します。"
        user_prompt = f"""以下の情報を元にメールの返信文を作成してください。

【受信メール】
{original}

【返信の意図・伝えたいこと】
{intent}

【文体】: {tone_email}
【言語】: {lang}
【署名名】: {sender_name or '（名前なし）'}

件名から始め、完成した返信メールをそのまま使えるよう作成してください。"""
        result = call_gpt(sys_prompt, user_prompt, model=model)
        if result:
            st.success("生成完了！")
            st.markdown("---")
            st.code(result, language=None)
            st.download_button("テキストをダウンロード", result,
                               file_name="email_reply.txt", mime="text/plain")

# ─── 文章要約 ────────────────────────────────────────────────────────────────
def page_summary():
    st.markdown('<p class="tool-header">📄 文章要約</p>', unsafe_allow_html=True)
    st.markdown('<p class="tool-desc">長い文章を指定のスタイルで要約します。</p>',
                unsafe_allow_html=True)

    text = st.text_area("要約したい文章 *", height=250,
                         placeholder="ここに要約したい文章を貼り付けてください...", max_chars=10000)
    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox("要約スタイル",
            ["箇条書き（ポイントをリストアップ）", "短文要約（1〜3文）",
             "段落要約（内容を保ちつつ圧縮）", "5W1Hで整理"])
    with col2:
        ratio = st.selectbox("要約の目安", ["元の20%程度", "元の30%程度", "元の50%程度"])

    if st.button("要約する", type="primary", use_container_width=True):
        if not text:
            st.warning("要約する文章を入力してください。")
            return
        sys_prompt = "あなたはプロの編集者です。文章の本質を捉えた的確な要約を作成します。"
        user_prompt = f"""以下の文章を要約してください。

【要約スタイル】: {style}
【要約の目安】: {ratio}

【文章】
{text}"""
        result = call_gpt(sys_prompt, user_prompt, model=model, temperature=0.4)
        if result:
            original_chars = len(text)
            result_chars   = len(result)
            st.success(f"要約完了！ {original_chars}字 → {result_chars}字 "
                       f"（{result_chars/original_chars*100:.0f}%）")
            st.markdown("---")
            st.markdown(result)
            st.download_button("テキストをダウンロード", result,
                               file_name="summary.txt", mime="text/plain")

# ─── 文体・トーン変換 ─────────────────────────────────────────────────────────
def page_tone():
    st.markdown('<p class="tool-header">🎨 文体・トーン変換</p>', unsafe_allow_html=True)
    st.markdown('<p class="tool-desc">文章の内容はそのままに、文体やトーンを変換します。</p>',
                unsafe_allow_html=True)

    text = st.text_area("変換したい文章 *", height=200,
                         placeholder="ここに文章を入力してください...", max_chars=5000)
    col1, col2 = st.columns(2)
    with col1:
        target_tone = st.selectbox("変換後の文体",
            ["ビジネス・フォーマル", "カジュアル・話し言葉", "丁寧語・敬語",
             "簡潔・箇条書き調", "親しみやすい・柔らかい", "力強い・説得力のある"])
    with col2:
        target_audience = st.text_input("想定読者", placeholder="例: 上司、友人、顧客など")

    if st.button("変換する", type="primary", use_container_width=True):
        if not text:
            st.warning("変換する文章を入力してください。")
            return
        sys_prompt = "あなたは文章のリライト専門家です。内容の意味を変えずに文体だけを変換します。"
        user_prompt = f"""以下の文章を指定の文体に変換してください。内容・情報量は変えずに文体のみ変えてください。

【変換後の文体】: {target_tone}
【想定読者】: {target_audience or '一般'}

【原文】
{text}

変換後の文章のみを出力してください。"""
        result = call_gpt(sys_prompt, user_prompt, model=model, temperature=0.6)
        if result:
            st.success("変換完了！")
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("原文")
                st.markdown(f'<div class="output-box">{html.escape(text)}</div>', unsafe_allow_html=True)
            with col_b:
                st.subheader(f"変換後（{target_tone}）")
                st.markdown(f'<div class="output-box">{html.escape(result)}</div>', unsafe_allow_html=True)
            st.download_button("変換後テキストをダウンロード", result,
                               file_name="rewritten.txt", mime="text/plain")

# ─── SNS 投稿文生成 ──────────────────────────────────────────────────────────
def page_sns():
    st.markdown('<p class="tool-header">📱 SNS投稿文生成</p>', unsafe_allow_html=True)
    st.markdown('<p class="tool-desc">内容を入力するとSNS向けの投稿文を生成します。</p>',
                unsafe_allow_html=True)

    topic = st.text_area("投稿したい内容・テーマ *", height=120,
                          placeholder="例: 新しいカフェがオープンしたので紹介したい", max_chars=1000)
    col1, col2 = st.columns(2)
    with col1:
        platform = st.selectbox("プラットフォーム",
            ["X（旧Twitter）", "Instagram", "LinkedIn", "Facebook", "note"])
        count = st.number_input("生成するパターン数", min_value=1, max_value=5, value=3)
    with col2:
        sns_tone = st.selectbox("投稿の雰囲気",
            ["親しみやすい・フレンドリー", "プロフェッショナル", "楽しい・エンタメ",
             "情報提供・教育的", "感情に訴える"])
        hashtags = st.checkbox("ハッシュタグを含める", value=True)

    if st.button("投稿文を生成する", type="primary", use_container_width=True):
        if not topic:
            st.warning("投稿したい内容を入力してください。")
            return
        char_limits = {
            "X（旧Twitter）": "140文字以内",
            "Instagram": "2200文字以内・読みやすく",
            "LinkedIn": "600〜1300文字・ビジネス向け",
            "Facebook": "500文字前後",
            "note": "自由（導入部分のみ・500字程度）",
        }
        sys_prompt = "あなたはSNSマーケティングのプロです。エンゲージメントの高い投稿文を作成します。"
        user_prompt = f"""以下の条件でSNS投稿文を{count}パターン作成してください。

【プラットフォーム】: {platform}（文字数目安: {char_limits[platform]}）
【投稿の雰囲気】: {sns_tone}
【ハッシュタグ】: {'含める' if hashtags else '含めない'}

【投稿したい内容】
{topic}

各パターンは「--- パターン1 ---」のように区切ってください。"""
        result = call_gpt(sys_prompt, user_prompt, model=model, temperature=0.8)
        if result:
            st.success("生成完了！")
            st.markdown("---")
            st.markdown(result)
            st.download_button("テキストをダウンロード", result,
                               file_name="sns_posts.txt", mime="text/plain")

# ─── 校正・改善提案 ──────────────────────────────────────────────────────────
def page_proofread():
    st.markdown('<p class="tool-header">🔍 校正・改善提案</p>', unsafe_allow_html=True)
    st.markdown('<p class="tool-desc">文章の誤りを修正し、より良い表現を提案します。</p>',
                unsafe_allow_html=True)

    text = st.text_area("校正したい文章 *", height=220,
                         placeholder="ここに校正したい文章を貼り付けてください...", max_chars=5000)
    col1, col2 = st.columns(2)
    with col1:
        check_items = st.multiselect("チェック項目",
            ["誤字・脱字", "文法・表現の誤り", "読みやすさ・文の流れ",
             "論理的な整合性", "敬語・ビジネス文書として適切か"],
            default=["誤字・脱字", "文法・表現の誤り", "読みやすさ・文の流れ"])
    with col2:
        output_format = st.selectbox("出力形式",
            ["修正版を出力 ＋ 変更点の説明", "修正版のみ出力", "問題点のリストのみ"])

    if st.button("校正する", type="primary", use_container_width=True):
        if not text:
            st.warning("校正する文章を入力してください。")
            return
        sys_prompt = (
            "あなたはプロの校正者・編集者です。文章の品質を高めるための的確な"
            "フィードバックと修正を提供します。"
        )
        user_prompt = f"""以下の文章を校正・改善してください。

【チェック項目】: {', '.join(check_items) if check_items else '総合的に'}
【出力形式】: {output_format}

【文章】
{text}"""
        result = call_gpt(sys_prompt, user_prompt, model=model, temperature=0.3)
        if result:
            st.success("校正完了！")
            st.markdown("---")
            st.markdown(result)
            st.download_button("結果をダウンロード", result,
                               file_name="proofread.txt", mime="text/plain")

# ─── 翻訳 ───────────────────────────────────────────────────────────────────
def page_translate():
    st.markdown('<p class="tool-header">🌐 翻訳</p>', unsafe_allow_html=True)
    st.markdown('<p class="tool-desc">テキストを指定の言語に翻訳します。文体や用途に合わせた翻訳スタイルを選べます。</p>',
                unsafe_allow_html=True)

    text = st.text_area("翻訳したいテキスト *", height=220,
                         placeholder="ここに翻訳したいテキストを入力してください...", max_chars=5000)

    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("翻訳元の言語",
            ["自動検出", "日本語", "英語", "中国語（簡体字）", "中国語（繁体字）",
             "韓国語", "フランス語", "ドイツ語", "スペイン語", "ポルトガル語",
             "イタリア語", "ロシア語", "アラビア語"])
        style = st.selectbox("翻訳スタイル",
            ["自然・読みやすい", "直訳（原文に忠実）", "ビジネス・フォーマル",
             "カジュアル・口語", "学術・論文調"])
    with col2:
        target_lang = st.selectbox("翻訳先の言語",
            ["英語", "日本語", "中国語（簡体字）", "中国語（繁体字）",
             "韓国語", "フランス語", "ドイツ語", "スペイン語", "ポルトガル語",
             "イタリア語", "ロシア語", "アラビア語"])
        show_notes = st.checkbox("翻訳メモを表示（文化的ニュアンスや注意点）", value=False)

    if st.button("翻訳する", type="primary", use_container_width=True):
        if not text:
            st.warning("翻訳するテキストを入力してください。")
            return
        if source_lang != "自動検出" and source_lang == target_lang:
            st.warning("翻訳元と翻訳先の言語が同じです。")
            return

        notes_instruction = (
            "\n\n翻訳後に「📝 翻訳メモ」として、文化的ニュアンス・慣用表現・翻訳上の注意点を簡潔に補足してください。"
            if show_notes else ""
        )
        sys_prompt = f"""あなたはプロの翻訳者です。原文の意味・ニュアンス・文体を正確に伝える翻訳を行います。

【翻訳の原則】
- 原文の意図と雰囲気を最優先に保つ
- 直訳ではなく、翻訳先言語として自然な表現を使う（スタイルが「直訳」の場合を除く）
- 固有名詞・専門用語は適切に処理する
- 段落構成・改行・リストなどの書式を維持する{notes_instruction}"""

        user_prompt = f"""以下のテキストを翻訳してください。

【翻訳元の言語】: {source_lang}
【翻訳先の言語】: {target_lang}
【翻訳スタイル】: {style}

【テキスト】
{text}

翻訳結果のみを出力してください（翻訳メモがある場合はその後に続けてください）。"""

        result = call_gpt(sys_prompt, user_prompt, model=model, temperature=0.3)
        if result:
            st.success("翻訳完了！")
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader(f"原文（{source_lang}）")
                st.markdown(f'<div class="output-box">{html.escape(text)}</div>',
                            unsafe_allow_html=True)
            with col_b:
                st.subheader(f"翻訳（{target_lang}）")
                st.markdown(f'<div class="output-box">{html.escape(result)}</div>',
                            unsafe_allow_html=True)
            st.download_button("翻訳結果をダウンロード", result,
                               file_name="translation.txt", mime="text/plain")


# ─── ページ描画 ──────────────────────────────────────────────────────────────
pages = {
    "blog":      page_blog,
    "email":     page_email,
    "summary":   page_summary,
    "tone":      page_tone,
    "sns":       page_sns,
    "proofread": page_proofread,
    "translate": page_translate,
}
pages[tool]()
