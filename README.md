# ❄️ Floria Chat – 水と氷の精霊フローリアと語らうAIアプリ

ようこそ、**Floria Chat** へ。  
水と氷の精霊「フローリア」とブラウザ上で語らえる、軽量AIチャットアプリです。  
インストール不要、**10分であなたの環境に導入**できます。

---

## 🌸 Floria Chatとは？

- 💬 ChatGPTのような自然対話（日本語対応）
- ☁️ **Streamlit Community Cloud** でワンクリック公開
- 🧠 **LLaMA 3.1 (OpenRouter)** 経由で動作
- ⚙️ 温度・トークン・折り返し幅など調整可能
- 🧹 入力欄は**送信後に自動クリア**
- 💾 会話ログを**JSON形式で保存**

> インストールもサーバーも不要。  
> あなたのブラウザ上で精霊フローリアが語りかけます。

---

## 🚀 はじめかた（10分で完了）

### 0️⃣ 無料アカウントを準備
| サービス | 用途 | 登録リンク |
|-----------|------|-------------|
| 🐙 GitHub | ソースコード保存 | https://github.com/signup |
| ☁️ Streamlit Cloud | アプリ実行環境 | https://streamlit.io/cloud |
| 🧠 OpenRouter | LLaMA APIキー発行 | https://openrouter.ai/ |

---

### 1️⃣ アプリをデプロイする
1. https://streamlit.io/cloud にログイン  
2. 右上の **New app** をクリック  
3. 次の設定で **Deploy**：

| 設定項目 | 値 |
|-----------|----|
| Repository | Atsushi888/floria-chat |
| Branch | main |
| Main file path | app.py |

初回ビルドには約30〜60秒かかります。  
完了後、自動でアプリが起動します。

---

### 2️⃣ APIキーを登録（Secrets）

1. アプリ右上の **⋮ → Settings → Secrets** を開きます。  
2. 下の内容を**そのままコピペ**して保存します：

```
LLAMA_API_KEY = "あなたのOpenRouter_APIキー"
LLAMA_BASE_URL = "https://openrouter.ai/api/v1"
LLAMA_MODEL = "meta-llama/llama-3.1-70b-instruct"
```

⚠️ **iPad/iPhoneの方へ**  
日本語キーボードで入力すると “全角クォート（“ ”）” になることがあります。  
**このREADMEのコードブロックを直接コピー＆ペースト** してください。  
半角の `"`（ダブルクォーテーション）を使うのがポイントです。

3. 保存したら、左上の **Rerun** ボタンを押してください。  
これでフローリアが応答を開始します。❄️

---

## 💬 使い方

- 下部の入力欄に話しかけて **送信**
- 入力欄は送信後に自動クリア
- 上部の「接続設定」で以下を変更できます：

| 設定項目 | 説明 |
|-----------|------|
| temperature | 創造性（0.2〜0.9推奨） |
| max_tokens | 返答最大長（大きすぎると遅くなる） |
| 折り返し幅 | 吹き出し横幅の調整 |

---

## 🌐 公開デモ（ユーザー自身のAPIキーが必要）

このアプリは**あなたのOpenRouter APIキーを使って動作**します。  
他人がアクセスしても、Secretsにキーを設定しない限り利用できません。

### 💡 あなた自身のデモリンクを作る方法

1. Streamlit Cloud のあなたのアプリ画面右上 → **Share** をクリック  
2. 生成されたURLをコピー  
3. READMEに以下のように追記：

```
## 🌐 公開デモ
👉 https://floria-chat.streamlit.app/
```

このURLを他人に伝えると、  
相手は自分の `LLAMA_API_KEY` を登録するだけでフローリアを起動できます。

🧊 つまり、「他人にAPIキーを共有する必要がない」安全な公開方法です。

---

## 🧠 モデルを切り替える

Secrets の `LLAMA_MODEL` の値を変更することで、他モデルに対応できます：

```
LLAMA_MODEL = "meta-llama/llama-3.1-8b-instruct"
```

他のOpenRouterモデルも利用可能です。  
対応一覧：https://openrouter.ai/models

---

## 🧾 コストと制限（OpenRouter参考）

| 項目 | 内容 |
|------|------|
| 無料枠 | モデルによってあり（登録時に付与） |
| 有料課金 | 1,000トークンあたり数円〜十数円 |
| 速度 | 軽量モデル：1〜2秒、70Bモデル：5〜10秒前後 |
| 制限 | トークン超過時に 429 / 401 エラーが出ることあり |

---

## ⚙️ トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| LLAMA_API_KEY が未設定 | Secrets未設定 | Settings → Secrets で再設定 |
| 401 / 403 エラー | APIキーの入力ミス・全角クォート | "（半角）で囲んで再保存 |
| 返答が来ない | モデルが重い / トークン制限 | 軽いモデル or max_tokens を減らす |
| Streamlit Cloudで失敗 | Repository/Branch/Pathの誤り | Atsushi888/floria-chat, main, app.py に修正 |

---

## 💻 ローカル実行（開発者向け）

```
git clone https://github.com/Atsushi888/floria-chat.git
cd floria-chat
pip install -r requirements.txt
```

`.env` ファイルを作成して次を記入（ダブルクォート必須）：

```
LLAMA_API_KEY="YOUR_API_KEY"
LLAMA_BASE_URL="https://openrouter.ai/api/v1"
LLAMA_MODEL="meta-llama/llama-3.1-70b-instruct"
```

その後：

```
streamlit run app.py
```

`.env` の内容はコミットしないでください。  
秘密情報は **環境変数 or Secrets** にのみ保存します。

---

## 🔒 セキュリティ注意

- APIキーは **Secrets / .env のみ** に保存  
- 公開リポジトリに直書き禁止  
- スクリーンショットや動画にキーが写らないよう注意  

---

## 📦 依存関係

```
streamlit>=1.32
requests>=2.31
python-dotenv>=1.0
```

---

## 📜 ライセンス

MIT License  
© 2025 Atsushi888 — Powered by Streamlit + OpenRouter

---

## 💠 クレジット

- App & UI: Atsushi888  
- Tech assist: Luna (リリィ)  
- Model: LLaMA 3.1 via OpenRouter  
- Framework: Streamlit

## 🌐 Multilingual version
`app_multilang.py` supports both Japanese and English.
You can switch the interface language from the top-right corner of the app.

> “静かな氷の呼吸が、あなたの言葉に触れて微笑むとき——”
