# Floria Chat — Streamlit Edition

A minimal Streamlit chat app to talk with **Floria**.  
It uses **Meta Llama 3.1 via OpenRouter** (paid, prepaid credits).

> **Important**: The app **does not run for free**.  
> You must add credits on OpenRouter and set your API key.

---

## 1) Llama (OpenRouter) & Billing

- Floria Chat calls **Meta Llama 3.1** through **OpenRouter**.
- Usage is **paid and credit-based** (prepaid).
- Typical cost: a few cents (JPY) per exchange depending on length.
- With no balance, you’ll see `401` / `403` or no response.

**Steps**
1. Sign up at [OpenRouter](https://openrouter.ai/)  
2. Open **Billing** and add credits  
3. Open **API Keys** and generate a key (`sk-or-...`)

---

## 2) Required Secrets (Streamlit Secrets)

Paste the following 3 lines into Streamlit Cloud **Secrets** (use **straight ASCII double quotes `"`**):

```toml
LLAMA_API_KEY = "sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
LLAMA_BASE_URL = "https://openrouter.ai/api/v1"
LLAMA_MODEL = "meta-llama/llama-3.1-70b-instruct"
```

> **For iPad users**: If typing `"` is tricky,  
> **copy & paste** the block above and only replace `sk-or-...` with your key.

---

## 3) Getting Started (Streamlit Cloud)

> This repository documents **Streamlit Cloud only**.

1. **Fork** (or Import) this repo on GitHub  
2. Log in to [streamlit.io](https://streamlit.io) → **Deploy an app**  
3. Set **Repository / Branch / Main file path**  
   - Example:  
     - Repository: `yourname/floria-chat`  
     - Branch: `main`  
     - Main file path: `app.py` (Japanese) or `app_multilang.py` (Japanese/English)
4. Before deploying, open **Advanced settings → Secrets** and paste:
   ```toml
   LLAMA_API_KEY = "sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   LLAMA_BASE_URL = "https://openrouter.ai/api/v1"
   LLAMA_MODEL = "meta-llama/llama-3.1-70b-instruct"
   ```
5. Click **Deploy** to start the app (auto-opening behavior may vary by environment).

> Note: Some environments won’t show a starter hint automatically.  
> Just type in the input box and send to start chatting.

---

## 4) Usage Tips

- Type your message and click **Send**.  
- For long replies, enable **Auto-continue**.  
- **“Start New Conversation”** clears history; a confirmation dialog is included.

---

## 5) Troubleshooting

- `401 / 403`:  
  - Missing/invalid `LLAMA_API_KEY`, or **no OpenRouter credits**.  
  - Refill credits and double-check your Secrets.
- `429`: Rate limited — wait and retry.  
- `502 / 503`: Upstream temporary issue — retry later.  
- Truncated/no output: `max_tokens` too small or context overflow.  
- Still failing: Ensure your Secrets use **straight ASCII double quotes**.

---

## 6) Main Files

- `app.py` — Japanese version (with reset confirmation)  
- `app_multilang.py` — Multilingual (Japanese/English) version (with reset confirmation)

---

## 7) License

MIT License
