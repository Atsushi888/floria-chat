# app.py — Floria Chat (Streamlit Edition, wide & auto-clear)

import os
import json
import requests
import streamlit as st

# --- session state init ---
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# ============ ページ設定（横幅ひろびろ） ============
st.set_page_config(page_title="Floria Chat", layout="wide")

st.markdown("""
<style>
/* 本文の最大幅を拡げる */
.block-container { max-width: 1100px; padding-left: 2rem; padding-right: 2rem; }
/* チャット気泡の横幅も拡張（任意） */
.chat-bubble { max-width: 900px; }
</style>
""", unsafe_allow_html=True)

# ============ シークレット読み込み ============
API  = st.secrets.get("LLAMA_API_KEY", os.getenv("LLAMA_API_KEY", ""))
BASE = st.secrets.get("LLAMA_BASE_URL", os.getenv("LLAMA_BASE_URL", "https://openrouter.ai/api/v1")).rstrip("/")
MODEL= st.secrets.get("LLAMA_MODEL",  os.getenv("LLAMA_MODEL",  "meta-llama/llama-3.1-70b-instruct"))

# /api/v1 が末尾に無ければ補完
if not BASE.endswith("/api/v1"):
    BASE = BASE + ("/v1" if BASE.endswith("/api") else "/api/v1")

if not API:
    st.error("LLAMA_API_KEY が未設定です。Streamlit → Settings → Secrets で設定してください。")
    st.stop()

# ============ 会話状態 ============
if "messages" not in st.session_state:
    SYSTEM_PROMPT = (
        "あなたは『フローリア』。水と氷の精霊の乙女。"
        "口調は穏やかで知的、ややツンデレ。描写は上品。"
        "出力は素の文章。行頭に装飾記号（*,・,•,★ など）を付けない。"
        "見出しや箇条書きは使わない。"
    )
    STARTER_USER_MSG = "はじめまして、フローリア。いま話せるかな？"
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": STARTER_USER_MSG},
    ]

# ============ パラメータ ============
st.title("❄️ Floria Chat — Streamlit Edition")

with st.expander("接続設定", expanded=False):
    c1, c2, c3 = st.columns(3)
    temperature = c1.slider("temperature", 0.0, 1.5, 0.70, 0.05)
    max_tokens  = c2.slider("max_tokens", 64, 2048, 300, 16)
    wrap_width  = c3.slider("折り返し幅", 20, 100, 80, 1)

# ============ 送信関数 ============
def floria_say(user_text: str):
    st.session_state.messages.append({"role":"user","content": user_text})
    try:
        resp = requests.post(
            f"{BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {API}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://streamlit.io",
                "X-Title": "Floria-Streamlit",
            },
            json={
                "model": MODEL,
                "messages": st.session_state.messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=60
        )
        try:
            data = resp.json()
        except Exception:
            data = None

        if resp.status_code != 200:
            err = (data.get("error", {}).get("message") or data.get("message") or resp.text[:500]) if isinstance(data, dict) else resp.text[:500]
            a = f"（ごめんなさい、冷たい霧で声が届きません… {resp.status_code}: {err}）"
        else:
            if isinstance(data, dict) and data.get("choices"):
                a = data["choices"][0]["message"]["content"]
            else:
                a = f"（返事の形が凍ってしまったみたい…：{str(data)[:200]}）"

    except requests.exceptions.Timeout:
        a = "（回線が凍りついてしまったみたい…少ししてからもう一度お願いします）"
    except Exception as e:
        a = f"（思わぬ渦に巻き込まれました…: {e}）"

    st.session_state.messages.append({"role":"assistant","content": a})

# ============ UI：会話欄 ============
st.subheader("会話")
dialog = [m for m in st.session_state.messages if m["role"] in ("user","assistant")]

for m in dialog:
    role = m["role"]
    txt  = m["content"].strip()
    if role == "user":
        st.markdown(f"<div class='chat-bubble user'><b>あなた：</b><br>{txt}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble assistant'><b>フローリア：</b><br>{txt}</div>", unsafe_allow_html=True)

# ============ 入力欄（送信後に自動クリア！） ============
st.markdown("---")
user_input = st.text_area(
    "あなたの言葉（複数行OK・空行不要）",
    key="user_input",
    height=160,
    label_visibility="visible",
)

c_send, c_new, c_show, c_dl = st.columns([1,1,1,1])

if c_send.button("送信", type="primary"):
    user_text = st.session_state["user_input"].strip()
    if user_text:
        floria_say(user_text)
        st.session_state["user_input"] = ""  # 入力欄を空に
        st.rerun()

# 便利ボタン
if c_new.button("新しい会話を始める", use_container_width=True):
    base_sys = st.session_state.messages[0]  # system は維持
    st.session_state.messages = [base_sys]
    st.session_state.messages.append({"role":"user", "content": "はじめまして、フローリア。いま話せるかな？"})
    st.session_state["user_input"] = ""
    st.rerun()

if c_show.button("最近10件を表示", use_container_width=True):
    st.info("最近10件の会話を下に表示します。")
    recent = dialog[-10:]
    for m in recent:
        role = "あなた" if m["role"]=="user" else "フローリア"
        st.write(f"**{role}**：{m['content'].strip()}")

if c_dl.button("会話ログを保存（JSON）", use_container_width=True):
    js = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    st.download_button("JSON をダウンロード", js, file_name="floria_chat_log.json", mime="application/json")

st.caption("© Floria — water & ice spirit. Powered by Streamlit + OpenRouter + floria-snippets")
