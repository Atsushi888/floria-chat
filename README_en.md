# Floria Chat — Streamlit Edition (English)

Chat freely with **Floria**, the maiden spirit of water and ice.  
This app connects to **OpenRouter (Llama or other models)** to generate dialogue.

> **Note**: The first launch may show an empty input box.  
> You can enable the hint from the sidebar under *World & Role → Show input hint*, or click *Insert hint* under the text box.

---

# Getting Started (Streamlit Cloud)

> Before you begin: Create an **OpenRouter** account, add credits, and generate an API key.

## 1) Deploy the app

1. Log into **Streamlit Cloud** → open **My apps**.  
2. Click **Create app** (top-right).  
3. On “What would you like to do?”, choose the **left card**  
   **“Deploy a public app from GitHub.”**  
4. Fill **Deploy an app**:
   - **Repository**: `Atsushi888/floria-chat` (or your fork)
   - **Branch**: `main`
   - **Main file path**: `app_multilang.py` (or `app.py` for basic version)
   - **App URL**: optional
5. Click **Deploy**. It will build and start automatically.

## 2) Set Secrets (API keys)

After the app launches, open **Manage app → Settings → Secrets**, and paste the following exactly (keep the quotes `" "`!):

```ini
LLAMA_API_KEY="sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
LLAMA_BASE_URL="https://openrouter.ai/api/v1"
LLAMA_MODEL="meta-llama/llama-3.1-70b-instruct"
```

- Replace the API key with your **OpenRouter key**.  
- On iPad, please **copy this block and replace the x’s** to avoid smart quotes (“ ”).  
- Then click **↻ Rerun** or reload the page.

## 3) Usage

- Switch **Language** (Japanese / English) in the sidebar.  
- Use **Connection Test** to confirm HTTP 200.  
- Type your lines and click **Send**. Long messages can auto-continue.  
- **Start New Conversation** shows a confirmation dialog before clearing.

## Troubleshooting

- Red banner: **LLAMA_API_KEY missing** → check your Secrets. Ensure straight quotes `"` and no extra spaces.  
- **401 / 403** → invalid key or insufficient OpenRouter credits.  
- Language switch crash → try reload / rerun, or check `Main file path` = `app_multilang.py`.

---

## License

MIT License (see `LICENSE`)
