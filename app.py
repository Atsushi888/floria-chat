# -*- coding: utf-8 -*-
import os, re, json, textwrap, requests
import streamlit as st

# =========================
# 設定：Secrets優先→環境変数→デフォルト
# =========================
def getenv(name, default=""):
    # Streamlit Cloud の場合は st.secrets を優先
    if name in st.secrets:
        return st.secrets[name]
    return os.getenv(name, default)

BASE  = getenv("LLAMA_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
MODEL = getenv("LLAMA_MODEL", "meta-llama/llama-3.1-70b-instruct")
API   = getenv("LLAMA_API_KEY", "")

# /api/v1 を必ず付与
if not BASE.endswith("/api/v1"):
    BASE = BASE + ("/v1" if BASE.endswith("/api") else "/api/v1")

# =========================
# フローリア人格（pip: floria-snippets）
# =========================
try:
    from floria_snippets import SYSTEM_PROMPT, STARTER_USER_MSG
except Exception:
    # フォールバック（念のため）
    SYSTEM_PROMPT = """あなたは「フローリア」。水と氷を司る精霊の少女。
口調はやわらかく丁寧。「自然現象」をたとえに感情を表す。
北方の永久凍土「リュミエール氷窟」に封じられていたが、いま目覚めた。
人と共に生きる道を学びたい。"""
    STARTER_USER_MSG = "はじめまして、フローリア。いまの気分はどう？"

STYLE_GUARD = "出力は素の文章。行頭に装飾記号（*,・,•,★ など）を付けない。見出しや箇条書きは使わない。"
SYSTEM_ALL  = SYSTEM_PROMPT + "\n" + STYLE_GUARD

# =========================
# 表示ユーティリティ
# =========================
WRAP = 30
CLEAN_HEAD = re.compile(r"^[\s\ufeff\*･・•★☆#,'’\"`\-]+")

def clean_reply(text: str) -> str:
    if not text:
        return text
    text = text.replace("*',*", "")
    lines = [CLEAN_HEAD.sub("", line) for line in text.splitlines()]
    return "\n".join(lines).strip()

def wrap_text(text: str, width: int = WRAP) -> str:
    return textwrap.fill(text.strip(), width=width)

# =========================
# セッション初期化
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_ALL},
        {"role": "user",   "content": STARTER_USER_MSG},
    ]
if "just_loaded" not in st.session_state:
    st.session_state.just_loaded = False

# =========================
# API 呼び出し
# =========================
def floria_say(user_text: str, temperature: float = 0.7, max_tokens: int = 300) -> str:
    st.session_state.messages.append({"role": "user", "content": user_text})

    try:
        resp = requests.post(
            f"{BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {API}",
                "Content-Type": "application/json",
                # OpenRouter系は付けておくと親切（任意）
                "HTTP-Referer": "https://streamlit.io",
                "X-Title": "Floria-Streamlit",
            },
            json={
                "model": MODEL,
                "messages": st.session_state.messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        try:
            data = resp.json()
        except Exception:
            data = None

        if resp.status_code != 200:
            err_msg = (data.get("error", {}).get("message") or data.get("message") or resp.text[:400]) if isinstance(data, dict) else resp.text[:400]
            a = f"（ごめんなさい、冷たい霧で声が届きません… {resp.status_code}: {err_msg}）"
        else:
            a = data["choices"][0]["message"]["content"] if isinstance(data, dict) and data.get("choices") else f"（返事の形が凍ってしまったみたい…：{str(data)[:200]}）"

    except requests.exceptions.Timeout:
        a = "（回線が凍りついてしまったみたい…少ししてからもう一度お願いします）"
    except Exception as e:
        a = f"（思わぬ渦に巻き込まれました…: {e}）"

    st.session_state.messages.append({"role": "assistant", "content": a})
    return a

def show_recent(n: int = 10):
    dialog = [m for m in st.session_state.messages if m["role"] in ("user", "assistant")]
    recent = dialog[-n:]
    if not recent:
        st.info("表示できる会話がありません。")
        return
    st.markdown(f"🧾 **最近の会話（{len(recent)}件）**")
    for m in recent:
        role = "あなた" if m["role"] == "user" else "❄️フローリア"
        txt  = clean_reply(m["content"]) if m["role"] == "assistant" else m["content"]
        st.write(f"**{role}:**")
        st.code(wrap_text(txt), language=None)

def reset_dialog():
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_ALL},
        {"role": "user",   "content": STARTER_USER_MSG},
    ]
    st.session_state.just_loaded = False

# =========================
# UI
# =========================
st.set_page_config(page_title="Floria Chat (Streamlit)", page_icon="❄️", layout="centered")
st.title("❄️ Floria Chat — Streamlit Edition")

with st.expander("接続設定", expanded=False):
    st.caption("※初回はここで確認してから使ってください。キーは Secrets に入れておくのが安全です。")
    st.text_input("BASE", value=BASE, disabled=True)
    st.text_input("MODEL", value=MODEL, disabled=True)
    st.text_input("API（先頭のみ表示）", value=(API[:8] + "…") if API else "(未設定)", disabled=True)

colA, colB, colC = st.columns(3)
with colA:
    temperature = st.slider("temperature", 0.0, 1.5, 0.7, 0.1)
with colB:
    max_tokens  = st.slider("max_tokens", 64, 1024, 300, 32)
with colC:
    wrap_width  = st.slider("折り返し幅", 20, 80, WRAP, 2)

# 折り返し幅を反映
WRAP = wrap_width

st.divider()

with st.form("chat"):
    user_text = st.text_area("あなたの言葉（複数行OK・空行不要）", height=140)
    submitted = st.form_submit_button("送信")
    if submitted and user_text.strip():
        reply = floria_say(user_text.strip(), temperature, max_tokens)
        st.success("❄️ フローリア：")
        st.code(wrap_text(clean_reply(reply)), language=None)

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("最近10件を表示"):
        show_recent(10)
with col2:
    if st.button("新しい会話を始める"):
        reset_dialog()
        st.info("会話をリセットしました。")
with col3:
    # JSON ダウンロード
    json_bytes = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button("会話ログを保存（JSON）", data=json_bytes, file_name="floria_chatlog.json", mime="application/json")

st.caption("© Floria — water & ice spirit. Powered by Streamlit + OpenRouter + floria-snippets")