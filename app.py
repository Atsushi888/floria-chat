# app.py — Floria Chat (Streamlit Edition, wide & auto-clear)

import os
import json
import requests
import streamlit as st

# --- session state init ---
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""
if "show_hint" not in st.session_state:
    st.session_state["show_hint"] = False  # 入力ヒントの表示可否

# ============ ページ設定（横幅ひろびろ） ============
st.set_page_config(page_title="Floria Chat", layout="wide")

st.markdown("""
<style>
.block-container { max-width: 1100px; padding-left: 2rem; padding-right: 2rem; }

/* 吹き出しの見やすさ */
.chat-bubble {
  white-space: pre-wrap;      /* 改行を保持して折り返す */
  overflow-wrap: anywhere;    /* 長い語も折り返す */
  word-break: break-word;
  line-height: 1.7;
  padding: .8rem 1rem;
  border-radius: .7rem;
  margin: .35rem 0;
}
.chat-bubble.user { background: #f4f6fb; }
.chat-bubble.assistant { background: #eaf7ff; }
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
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

# ============ パラメータ ============
st.title("❄️ Floria Chat — Streamlit Edition")
with st.expander("世界観とあなたの役割（ロール）", expanded=False):
    st.markdown("""
**舞台**：白霧の湖のほとり。水と氷の精霊フローリアは、封印の鎖に縛られている。  
**あなた**：旅の来訪者。観察者ではなく、語りかけ・問いかけ・提案で物語を動かす当事者。  
**お願い**：命令口調よりも、状況描写や気持ち・意図を添えて話しかけると、会話が豊かになります。
""")
    st.checkbox("入力ヒントを表示する", key="show_hint")

with st.expander("接続設定", expanded=False):
    c1, c2, c3 = st.columns(3)
    temperature = c1.slider("temperature", 0.0, 1.5, 0.70, 0.05)
    max_tokens  = c2.slider("max_tokens", 64, 2048, 300, 16)
    wrap_width  = c3.slider("折り返し幅", 20, 100, 80, 1)
# スライダーの値でチャット幅を動的反映（文字数基準）
st.markdown(
    f"<style>.chat-bubble {{ max-width: {wrap_width}ch; }}</style>",
    unsafe_allow_html=True
)

# ============ 送信関数 ============
def floria_say(user_text: str):
    # ユーザー発言を履歴に追加
    st.session_state.messages.append({"role": "user", "content": user_text})

    # 直近だけを送る（system は先頭に残す）
    base = st.session_state.messages
    to_send = [base[0]] + base[-40:]

    try:
        with st.spinner("フローリアが考えています…"):
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
                    "messages": to_send,
                    "temperature": float(temperature),
                    "max_tokens": int(max_tokens),
                },
                timeout=(10, 60)
            )

        # できるだけ安全にパース
        try:
            data = resp.json()
        except Exception:
            data = None

        if resp.status_code != 200:
            if isinstance(data, dict):
                err = data.get("error", {}).get("message") or data.get("message") or str(data)
            else:
                err = resp.text[:500]
            a = f"（ごめんなさい、冷たい霧で声が届きません… {resp.status_code}: {err}）"
        else:
            a = ""
            if isinstance(data, dict) and data.get("choices"):
                a = data["choices"][0].get("message", {}).get("content", "") or ""
            if not a:
                a = f"（返事の形が凍ってしまったみたい…：{str(data)[:200]}）"

    except requests.exceptions.Timeout:
        a = "（回線が凍りついてしまったみたい…少ししてからもう一度お願いします）"
    except Exception as e:
        a = f"（思わぬ渦に巻き込まれました…: {e}）"

    # アシスタント発言を履歴に追加
    st.session_state.messages.append({"role": "assistant", "content": a})
    
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
# 1) 先にヒント文字列
STARTER_HINT = "……白い霧の向こうに気配がする。そこにいるのは誰？"

# 2) ヒント挿入フラグ
if "_insert_hint" not in st.session_state:
    st.session_state["_insert_hint"] = False

def ask_insert_hint():
    st.session_state["_insert_hint"] = True

# 3) 入力欄（そのまま）
st.text_area(
    "あなたの言葉（複数行OK・空行不要）",
    key="user_input",
    height=160,
    placeholder=(STARTER_HINT if st.session_state.get("show_hint") else ""),
    label_visibility="visible",
)

# 4) ボタン：on_click ではフラグだけ立てる
hint_col, _ = st.columns([1,3])
hint_col.button("ヒントを入力欄に挿入", on_click=ask_insert_hint)

# 5) コールバック外で反映
if st.session_state["_insert_hint"]:
    st.session_state["_insert_hint"] = False
    st.session_state["user_input"] = STARTER_HINT
    st.rerun()

# ▼ 送信・その他ボタンの行
c_send, c_new, c_show, c_dl = st.columns([1, 1, 1, 1])

# 送信制御フラグの初期化
if "_do_send" not in st.session_state:
    st.session_state["_do_send"] = False
if "_busy" not in st.session_state:
    st.session_state["_busy"] = False

# 送信ボタン（実行はメインループ側で）
if c_send.button("送信", type="primary", disabled=st.session_state["_busy"]):
    st.session_state["_do_send"] = True

# ここで送信処理を安全に実行（コールバック外）
if st.session_state["_do_send"] and not st.session_state["_busy"]:
    st.session_state["_do_send"] = False
    st.session_state["_busy"] = True
    try:
        user_text = st.session_state.get("user_input", "").strip()
        if user_text:
            floria_say(user_text)
        # 入力欄をクリア
        st.session_state["user_input"] = ""
    finally:
        st.session_state["_busy"] = False
        st.rerun()  # 古い環境なら st.experimental_rerun() でもOK

# 🌀 新しい会話を始める
if c_new.button("新しい会話を始める", use_container_width=True, disabled=st.session_state["_busy"]):
    base_sys = st.session_state.messages[0]  # system は維持
    st.session_state.messages = [base_sys]
    st.session_state["user_input"] = ""
    st.rerun()

# 📜 最近10件を表示
if c_show.button("最近10件を表示", use_container_width=True, disabled=st.session_state["_busy"]):
    st.info("最近10件の会話を下に表示します。")
    recent = [m for m in st.session_state.messages if m["role"] in ("user", "assistant")][-10:]
    for m in recent:
        role = "あなた" if m["role"] == "user" else "フローリア"
        st.write(f"**{role}**：{m['content'].strip()}")

# 💾 JSON保存
if c_dl.button("会話ログを保存（JSON）", use_container_width=True, disabled=st.session_state["_busy"]):
    js = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    st.download_button("JSON をダウンロード", js, file_name="floria_chat_log.json", mime="application/json")
