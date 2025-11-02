# Floria Chat — Streamlit Edition

水と氷の精霊フローリアと語らう、軽量なチャットアプリです。  
OpenRouter 経由で Llama（等のモデル）に接続して動作します。

> **注意**: 初回起動時、**入力欄にヒントは表示されません**（仕様）。  
> 画面左の「世界観とあなたの役割」→「入力ヒントを表示する」にチェックを入れるか、下部の「ヒントを入力欄に挿入」ボタンを押すとヒントを出せます。

---

# はじめかた（Streamlit Cloud 版・iPad対応詳解）

> 事前に：OpenRouter（Llamaの中継サービス）でアカウント作成＆クレジット追加が必要です。  
> ダッシュボードでAPIキーを発行しておきましょう。

## 1) アプリをデプロイする

1. **Streamlit Cloud にログイン** → 上部タブの **My apps** を開く。  
2. 右上の **Create app** をタップ。  
3. 「What would you like to do?」で**左のカード**  
   **“Deploy a public app from GitHub”** を選ぶ。  
4. **Deploy an app** 画面で次を入力：
   - **Repository**：`Atsushi888/floria-chat`（あなたのフォーク名に読み替え可）
   - **Branch**：`main`
   - **Main file path**：`app_multilang.py`（多言語版）  
     ※ベーシック版で出すなら `app.py`
   - （任意）**App URL**：好きなサブドメイン名
5. そのまま **Deploy**。ビルド〜起動が走ります（数分）。

## 2) シークレット（APIキー）をセットする

起動後に画面右下 **Manage app** → **Settings** → **Secrets** を開き、下の3行を**丸ごとコピペ**して保存。  
（**必ず**ダブルクォーテーション `"` を含めてください。スマート引用符 “ ” は不可）

```ini
LLAMA_API_KEY="sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
LLAMA_BASE_URL="https://openrouter.ai/api/v1"
LLAMA_MODEL="meta-llama/llama-3.1-70b-instruct"
```

- `LLAMA_API_KEY` は OpenRouter で発行した **あなたのAPIキー** に置き換え。
- iPadで `"` が打ちにくい場合は、**このブロックをコピーして x を置換**してください（引用符はそのまま）。

保存したら、画面上部の **↻ Rerun**（またはページ再読み込み）でアプリを再起動します。

## 3) 使い方

- 左サイドバーの **Language / 言語** で **日本語 / English** を切り替え可能。  
- 「接続テスト（任意）」のボタンで 200 が返れば接続OK。  
- テキストエリアに台詞や地の文を入れて **送信**。長文は自動継ぎ足し可。  
- **新しい会話** は確認ダイアログ付き（履歴を消去）。

## よくあるエラーと対処

- 画面に赤いバナーで  
  **「LLAMA_API_KEY が未設定です」**  
  → **Secretsに3行を正確に貼れていない**可能性。`"` が “ ” になっていないか、空白や改行が増えていないか確認。
- **401 / 403**  
  → APIキーの打ち間違い／OpenRouter側のクレジット不足。OpenRouterのダッシュボードで残高を確認。
- **英語切替で落ちる**  
  → 古いキャッシュの可能性。ブラウザをリロード or **Rerun**。それでも出る場合は `Main file path` が `app_multilang.py` になっているか確認。

---

## ライセンス

MIT License（同梱の `LICENSE` を参照）
