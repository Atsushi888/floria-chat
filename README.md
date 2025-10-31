# Floria Chat — Streamlit & Colab Edition

水と氷の精霊 **フローリア** と会話できる、超軽量のAIチャット。  
Pythonが分からなくても、**ブラウザだけ**で体験できます（無料枠あり）。

- UI: **Streamlit**（ブラウザで動くPythonアプリ）
- モデル呼び出し: **OpenRouter** 経由の **Llama 3.1**（または対応モデル）
- 人格定義: **PyPI パッケージ `floria-snippets`**（外部化で再利用しやすい）

---

## 0. これは何をするもの？

- ブラウザでアクセス → **フローリアと会話**できます  
- 会話はページ内で整形表示、**ログをJSONダウンロード**可能  
- Colab でも **同じ人格・同じコード**で動きます

---

## 1. はじめての方向けの最短ルート（Streamlit で公開）

> GitHub アカウントがあれば、**無料で常時公開**できます。

### 1-1. このリポジトリを自分のGitHubに用意
- GitHubで新規リポジトリを作成（例：`floria-streamlit`）
- 下の3ファイルを置きます：
  - `app.py`（このリポジトリのものをそのまま）
  - `requirements.txt`
  - `README.md`（この文章。任意）
- コミット＆プッシュ

### 1-2. OpenRouter のAPIキーを取得（Llama導入）
1. OpenRouter にGoogle/Twitter等でサインイン  
   → ダッシュボードで **API Key** を発行  
2. **モデル選択**：`meta-llama/llama-3.1-70b-instruct` を推奨  
3. 単価はモデルごとに表示されます（従量制）  
   ※無料枠は時期により変動。必要に応じて課金手段を設定

### 1-3. Streamlit Community Cloud で公開
1. https://streamlit.io/cloud にアクセス→ログイン  
2. **New app** → 1-1で作成したGitHubリポジトリを選択  
3. **Main file** に `app.py` を指定  
4. **Advanced settings → Secrets** に以下をコピペして保存：

```
LLAMA_BASE_URL = "https://openrouter.ai/api/v1"
LLAMA_MODEL    = "meta-llama/llama-3.1-70b-instruct"
LLAMA_API_KEY  = "sk-ここにあなたのAPIキー"
```

5. **Deploy** を押す → 数十秒でURLが発行されます  
   例）`https://<your-app-name>.streamlit.app/`

> これで、**誰でもブラウザからフローリアと会話**できます（OS不問）。

---

## 2. いますぐ試したい（Colab で体験）

> Colab は“自分で遊ぶ用”。無料〜少額でOK。GPU不要。

1. Colab を開く → 新しいノートブック  
2. 1セル目（依存インストール）：
   ```bash
   !pip install -q requests python-dotenv floria-snippets
   ```
3. 2セル目（`.env` を作る。**自分のキーに書き換えて**）：
   ```bash
   %%writefile secret.env
   LLAMA_BASE_URL=https://openrouter.ai/api/v1
   LLAMA_MODEL=meta-llama/llama-3.1-70b-instruct
   LLAMA_API_KEY=sk-あなたのAPIキー
   ```
4. 3セル目（`chat_floria.py` 本体の中身をペーストして実行）  
   → 画面に「🧊 フローリアと会話を始めます」と出たら成功  
   - 複数行入力可、**空行で送信**  
   - コマンド：`/save`, `/load`, `/recent 10`, `/clear`, `/retry`, `/bye`

> 既に `chat_floria.py` を持っている人は、Colabの左側（ファイル）にアップして  
> `!python chat_floria.py` でもOK。

---

## 3. ローカルPC（Windows/macOS/Linux）で動かす

1. Python 3.9+ を用意  
2. 依存インストール：
   ```bash
   pip install requests python-dotenv floria-snippets
   ```
3. プロジェクト直下に `.env` を作成：
   ```
   LLAMA_BASE_URL=https://openrouter.ai/api/v1
   LLAMA_MODEL=meta-llama/llama-3.1-70b-instruct
   LLAMA_API_KEY=sk-あなたのAPIキー
   ```
4. 実行：
   ```bash
   python chat_floria.py
   ```

> ログ保存先は `./chat_logs` を推奨（Colabの `/content/drive/...` は使わない）。

---

## 4. iPad（Pythonista）で動かす（任意）

1. Pythonista をインストール（有料アプリ）  
2. 付属の StaSh を導入 → ライブラリをインストール  
   ```
   pip install requests
   pip install python-dotenv
   pip install floria-snippets
   ```
3. `~/Documents/` に `chat_floria.py` と `secret.env` を置く  
   - `load_dotenv(os.path.expanduser("~/Documents/secret.env"))`
   - `LOG_DIR = os.path.expanduser("~/Documents/chat_logs")`
4. `chat_floria.py` を開いて ▶ で実行

---

## 5. セキュリティと運用の注意

- **APIキーは絶対にGitHubにコミットしない**  
  - Streamlit は **Secrets**、ローカルやColabは `.env` で管理  
- Colabはセッション切れあり → `/save` で会話ログをDriveへ  
- モデル代は**従量課金**：`max_tokens` を 200–400 程度に抑えると安定  
- 公開デモ（Streamlit）は**軽量UI**が基本。音声や画像は後から拡張でOK

---

## 6. よくある質問（FAQ）

**Q1. Llama（LlimaじゃなくてLlama）って何？**  
A. Metaの大規模言語モデルです。本リポジトリは **OpenRouter** 経由でLlama 3.1などを呼び出します。  
BASE/MODEL/API を差し替えれば他モデルにも対応できます。

**Q2. 無料で使える？**  
A. アプリ公開は無料（Streamlit Community Cloud）。ただし**モデル推論は従量課金**。OpenRouterの料金表を確認してください。

**Q3. ブラウザだけで使える？**  
A. はい。Streamlit で公開すれば、ユーザーはURLを開くだけで使えます。OSや機種は問いません。

**Q4. 会話は保存できる？**  
A. はい。Streamlit版は**JSONとしてダウンロード**可能。Colab/ローカル版は `/save` で保存、`/load` で復元できます（直近10件のプレビュー付き）。

---

## 7. 参考：環境変数の一覧

| 変数名 | 例 | 説明 |
|---|---|---|
| `LLAMA_BASE_URL` | `https://openrouter.ai/api/v1` | モデル提供APIのベースURL |
| `LLAMA_MODEL` | `meta-llama/llama-3.1-70b-instruct` | 使用モデルID |
| `LLAMA_API_KEY` | `sk-xxxx` | APIキー（**秘密にする**） |

---

## 8. ライセンスとクレジット

- 人格定義: `floria-snippets`（MIT）  
- このリポジトリ: MIT License  
- Model: Meta Llama / via OpenRouter

---

## 9. 問題が起きたら（トラブルシュート）

- **応答が返らない**：APIキー・モデルID・BASE URL を再確認。`/api/v1` が付いているか？  
- **エラー `401/403`**：APIキー無効 or 権限不足（OpenRouterの鍵・課金設定を確認）  
- **Streamlit で環境変数が読めない**：**Secrets** に入れたか？（`st.secrets`が優先）  
- **Colab でDriveに保存できない**：`drive.mount('/content/drive')` 済みか？

---

### 付録：`requirements.txt`
```txt
streamlit>=1.36
requests>=2.31
python-dotenv>=1.0
floria-snippets>=0.0.1
```

---

“インストールから起動まで”を、**OpenRouter（Llama）導入込みで**一気通貫にしました。  
これで初見さんでも迷わず始められるはず。
