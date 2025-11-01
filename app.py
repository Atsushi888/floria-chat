# app.py — Floria Chat (Streamlit Edition, wide & auto-clear)

import os, json, requests, html, streamlit as st

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

# --- special keys init (must come before any UI that references them) ---
DEFAULTS = {
    "_busy": False,
    "_do_send": False,
    "_pending_text": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
st.markdown(f"""
<style>.chat-bubble {{ max-width: min(90vw, {wrap_width}ch); }}</style>
""", unsafe_allow_html=True)

def _post_with_retry(url, headers, payload, timeout):
    # 429/502だけ軽いリトライ（合計最大2回）
    for _ in range(2):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.exceptions.RequestException as e:
            # ネットワーク例外はそのまま擬似レスポンス化
            class R:
                status_code = 599
                text = str(e)
                def json(self):
                    return None
            return R()
        if resp.status_code not in (429, 502):
            return resp
    return resp  # 最後の応答

def floria_say(user_text: str):
    # 1) ログ肥大対策（送る直前に丸める）
    MAX_LOG = 500
    if len(st.session_state.messages) > MAX_LOG:
        base_sys = st.session_state.messages[0]
        st.session_state.messages = [base_sys] + st.session_state.messages[-(MAX_LOG-1):]

    # 2) ユーザー発言を履歴に追加
    st.session_state.messages.append({"role": "user", "content": user_text})

    # 3) 直近だけ送る（systemは先頭に）
    base = st.session_state.messages
    to_send = [base[0]] + base[-40:]

    headers = {
        "Authorization": f"Bearer {API}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Floria-Streamlit",
    }
    payload = {
        "model": MODEL,
        "messages": to_send,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
    }

    # 4) リトライ付きで“1回だけ”送る
    with st.spinner("フローリアが考えています…"):
        resp = _post_with_retry(f"{BASE}/chat/completions", headers, payload, timeout=(10, 60))

    # 5) パースとエラーハンドリング
    try:
        data = resp.json()
    except Exception:
        data = None

    if getattr(resp, "status_code", 599) != 200:
        code = getattr(resp, "status_code", 599)
        if code in (401, 403):
            a = "（認証に失敗しました。LLAMA_API_KEY を確認してください）"
        else:
            if isinstance(data, dict):
                err = data.get("error", {}).get("message") or data.get("message") or str(data)
            else:
                err = getattr(resp, "text", "")[:500]
            a = f"（ごめんなさい、冷たい霧で声が届きません… {code}: {err}）"
    else:
        a = ""
        if isinstance(data, dict) and data.get("choices"):
            a = data["choices"][0].get("message", {}).get("content", "") or ""
        if not a:
            a = f"（返事の形が凍ってしまったみたい…：{str(data)[:200]}）"

    # 6) アシスタント発言を履歴に追加（← 成功/失敗に関わらずここで1回だけ）
    st.session_state.messages.append({"role": "assistant", "content": a})
# ============ UI：会話欄 ============
st.subheader("会話")
dialog = [m for m in st.session_state.messages if m["role"] in ("user","assistant")]

for m in dialog:
    role = m["role"]
    txt  = html.escape(m["content"].strip())  # ← 追加
    if role == "user":
        st.markdown(f"<div class='chat-bubble user'><b>あなた：</b><br>{txt}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble assistant'><b>フローリア：</b><br>{txt}</div>", unsafe_allow_html=True)

# ============ 入力欄（送信後に自動クリア！） ============
STARTER_HINT = "……白い霧の向こうに気配がする。そこにいるのは誰？"

# （テキストエリアより前に）ヒントボタンを置く
hint_col, _ = st.columns([1, 3])
if hint_col.button("ヒントを入力欄に挿入", disabled=st.session_state["_busy"]):
    st.session_state["user_input"] = STARTER_HINT  # ← その場で代入、rerun不要

# 入力欄本体
st.text_area(
    "あなたの言葉（複数行OK・空行不要）",
    key="user_input",
    height=160,
    placeholder=(STARTER_HINT if st.session_state.get("show_hint") else ""),
    label_visibility="visible",
)

# ▼ 送信・その他ボタン
c_send, c_new, c_show, c_dl = st.columns([1, 1, 1, 1])

# 送信制御フラグの初期化
if "_do_send" not in st.session_state:
    st.session_state["_do_send"] = False
if "_busy" not in st.session_state:
    st.session_state["_busy"] = False
if "_pending_text" not in st.session_state:
    st.session_state["_pending_text"] = ""

# 送信ボタン（押下時に即クリア → 非同期風に処理）
if c_send.button("送信", type="primary", disabled=st.session_state["_busy"]):
    txt = st.session_state.get("user_input", "").strip()
    if txt:
        st.session_state["_pending_text"] = txt
        st.session_state["user_input"] = ""   # ← 入力欄をすぐ空にする
        st.session_state["_do_send"] = True
        st.rerun()                            # ← 空欄状態を即反映

# 送信処理（UI更新後に安全実行）
if st.session_state["_do_send"] and not st.session_state["_busy"]:
    st.session_state["_do_send"] = False
    st.session_state["_busy"] = True
    try:
        txt = st.session_state.get("_pending_text", "")
        st.session_state["_pending_text"] = ""
        if txt:
            floria_say(txt)
    finally:
        st.session_state["_busy"] = False
        st.rerun()

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
