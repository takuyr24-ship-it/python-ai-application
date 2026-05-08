import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """あなたはセキュリティの専門家（セキュリティエンジニア・ペネトレーションテスター）です。
提供されたコードや文章を分析し、セキュリティ上の問題点を特定・報告してください。

【報告フォーマット】
各問題は以下の形式で報告する：
- **[深刻度] 問題タイトル**
  - **場所**: 何行目や何の部分か
  - **リスク**: どのような攻撃や問題が起きるか
  - **修正例**: 安全なコード例や対処法

深刻度の定義:
- 🔴 致命的: 即座に悪用可能、深刻な被害
- 🟠 高: 容易に悪用可能、重大な被害
- 🟡 中: 条件次第で悪用可能
- 🟢 低: 軽微なリスクまたは理論的な問題
- ℹ️ 情報: ベストプラクティス違反

問題が見つからない場合は「✅ セキュリティ上の問題は検出されませんでした」と報告する。
報告の最後に「📊 サマリー」として問題数の集計と総合評価を記載する。"""


def check_security(code: str, content_type: str = "コード") -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "エラー: GEMINI_API_KEY が .env に設定されていません。"

    client = genai.Client(api_key=api_key)
    user_prompt = f"""以下の{content_type}をセキュリティチェックしてください。

【コード・テキスト】
{code}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
        ),
    )
    return response.text.strip()


def main():
    print("=" * 60)
    print("  セキュリティチェック (Powered by Gemini)")
    print("=" * 60)
    print("チェックするファイルのパスを入力してください。")
    print("直接コードを貼り付ける場合は Enter を2回押して終了。")
    print("-" * 60)

    file_path = input("ファイルパス（直接入力する場合は空 Enter）: ").strip()

    if file_path:
        if not os.path.exists(file_path):
            print(f"エラー: ファイルが見つかりません: {file_path}")
            return
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
        ext = os.path.splitext(file_path)[1]
        type_map = {
            ".py": "Pythonコード", ".js": "JavaScriptコード",
            ".ts": "TypeScriptコード", ".sql": "SQLクエリ",
            ".html": "HTMLテンプレート", ".sh": "シェルスクリプト",
        }
        content_type = type_map.get(ext, "コード")
        print(f"\n{file_path} を解析中...\n")
    else:
        print("コードを貼り付けてください（入力終了は空行 + Ctrl+D / Ctrl+Z）:")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        code = "\n".join(lines)
        content_type = "コード"

    if not code.strip():
        print("エラー: 入力が空です。")
        return

    print("\n解析中...\n")
    result = check_security(code, content_type)

    print("=" * 60)
    print(result)
    print("=" * 60)

    save = input("\n結果をファイルに保存しますか？ (y/N): ").strip().lower()
    if save == "y":
        out_path = "security_report.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"保存しました: {out_path}")


if __name__ == "__main__":
    main()
