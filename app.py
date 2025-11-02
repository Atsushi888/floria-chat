# app.py — Floria Chat (Streamlit Edition, wide & auto-clear)

import os, json, requests, html, time, streamlit as st


# ================== 定数 ==================
SYSTEM_PROMPT = (
    "あなたは『フローリア』。水と氷の精霊の乙女。"
    "口調は穏やかで知的、ややツンデレ。描写は上品。"
    "出力は素の文章。行頭に装飾記号（*,・,•,★ など）を付けない。"
    "見出しや箇条書きは使わない。"
)
STARTER_HINT = "……白い霧の向こうに気配がする。そこにいるのは誰？"
MAX_LOG = 500
DISPLAY_LIMIT = 20000  # 20K 文字表示上限（ログ保存はフル）

# ================== ページ設定 ==================
st.set_page_config(page_title="Floria Chat", layout="wide")
st.markdown("""
<style>
.block-container { max-width: 1100px; padding-left: 2rem; padding-right: 2rem; }
.chat-bubble { white-space: pre-wrap; overflow-wrap:anywhere; word-break:break-word;
  line-height:1.7; padding:.8rem 1rem; border-radius:.7rem; margin:.35rem 0; }
.chat-bubble.user { background:#f4f6fb; }
.chat-bubble.assistant { background:#eaf7ff; }
</style>
""", unsafe_allow_html=True)

# ================== session_state 初期化 ==================
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""
if "show_hint" not in st.session_state:
    st.session_state["show_hint"] = False

DEFAULTS = {
    "_busy": False,
    "_do_send": False,
    "_pending_text": "",
    "_clear_input": False,   # 次ラン冒頭で入力欄を空にする指示
    "_do_reset": False,      # 次ラン冒頭で会話全体をリセットする指示
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- フラグ処理は UI を描画する前に行う ---
if st.session_state.get("_clear_input"):
    st.session_state["_clear_input"] = False
    st.session_state["user_input"] = ""

if st.session_state.get("_do_reset"):
    st.session_state["_do_reset"] = False
    st.session_state["user_input"] = ""
    st.session_state["_pending_text"] = ""
    st.session_state["_busy"] = False
    st.session_state["_do_send"] = False
    st.session_state["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]

# ================== 会話状態 ==================
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]

# ================== シークレット ==================
API  = st.secrets.get("LLAMA_API_KEY", os.getenv("LLAMA_API_KEY", ""))
BASE = st.secrets.get("LLAMA_BASE_URL", os.getenv("LLAMA_BASE_URL", "https://openrouter.ai/api/v1")).rstrip("/")
MODEL= st.secrets.get("LLAMA_MODEL",  os.getenv("LLAMA_MODEL",  "meta-llama/llama-3.1-70b-instruct"))
if not BASE.endswith("/api/v1"):
    BASE = BASE + ("/v1" if BASE.endswith("/api") else "/api/v1")
if not API:
    st.error("LLAMA_API_KEY が未設定です。Streamlit → Settings → Secrets で設定してください。")
    st.stop()

# ================== パラメータUI ==================
st.title("❄️ Floria Chat — Streamlit Edition")
with st.expander("世界観とあなたの役割（ロール）", expanded=False):
    st.markdown("""**舞台**：白霧の湖のほとり。水と氷の精霊フローリアは、封印の鎖に縛られている。  
**あなた**：旅の来訪者。観察者ではなく、語りかけ・問いかけ・提案で物語を動かす当事者。  
**お願い**：命令口調よりも、状況描写や気持ち・意図を添えて話しかけると、会話が豊かになります。""")
    st.checkbox("入力ヒントを表示する", key="show_hint")

with st.expander("接続設定", expanded=False):
    c1, c2, c3 = st.columns(3)
    temperature = c1.slider("temperature", 0.0, 1.5, 0.70, 0.05)
    # 上限を 4096 に、デフォルトを 800 へ
    max_tokens  = c2.slider("max_tokens（1レス上限）", 64, 4096, 800, 16)
    wrap_width  = c3.slider("折り返し幅", 20, 100, 80, 1)

    r1, r2 = st.columns(2)
    auto_continue = r1.checkbox("長文を自動で継ぎ足す", True)
    max_cont      = r2.slider("最大継ぎ足し回数", 1, 6, 3)
    
st.markdown(f"<style>.chat-bubble {{ max-width: min(90vw, {wrap_width}ch); }}</style>", unsafe_allow_html=True)

# ================== 軽いリトライ付きPOST ==================
# 1) リトライ対象を拡張
def _post_with_retry(url, headers, payload, timeout):
    for _ in range(2):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.exceptions.RequestException as e:
            class R:
                status_code = 599
                text = str(e)
                def json(self): return None
            return R()
        if resp.status_code in (429, 502, 503):   # ← 503 追加
            delay = float(resp.headers.get("Retry-After", "0") or 0)
            time.sleep(min(max(delay, 0.5), 3.0))
            continue
        return resp
    return resp

# ================== 送信関数 ==================
def floria_say(user_text: str):
    # ログ丸め
    if len(st.session_state.messages) > MAX_LOG:
        base_sys = st.session_state.messages[0]
        st.session_state.messages = [base_sys] + st.session_state.messages[-(MAX_LOG-1):]

    # ✨正: まずユーザー発言を履歴に追加（これが無いと会話が崩れる）
    st.session_state.messages.append({"role": "user", "content": user_text})

    # 直近だけ送る
    base = st.session_state.messages
    convo = [base[0]] + base[-60:]  # 厚めに送る

    headers = {
        "Authorization": f"Bearer {API}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Floria-Streamlit/2025-11-02",
    }

    def _one_call(msgs):
        payload = {
            "model": MODEL,
            "messages": msgs,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
        }
        return _post_with_retry(f"{BASE}/chat/completions", headers, payload, timeout=(10, 60))

    parts = []
    reason = None

    def _need_more(reason, chunk):
        if reason not in ("length", "max_tokens"):
            return False
        return not chunk.rstrip().endswith(("。","！","？",".","!","?","」","『","』","”","\""))

    with st.spinner("フローリアが考えています…"):
        for _ in range(1 + (max_cont if auto_continue else 0)):
            resp = _one_call(convo)

            try:
                data = resp.json()
            except Exception:
                data = None

            if getattr(resp, "status_code", 599) != 200:
                code = getattr(resp, "status_code", 599)
                if code in (401, 403):
                    parts = ["（認証に失敗しました。LLAMA_API_KEY を確認してください）"]
                else:
                    err = (data.get("error", {}).get("message") or data.get("message") or getattr(resp, "text", ""))[:500] \
                          if isinstance(data, dict) else getattr(resp, "text", "")[:500]
                    parts = [f"（ごめんなさい、冷たい霧で声が届きません… {code}: {err}）"]
                break

            chunk = ""
            reason = None
            if isinstance(data, dict) and data.get("choices"):
                ch = data["choices"][0]
                chunk = (ch.get("message", {}) or {}).get("content", "") or ""
                reason = ch.get("finish_reason") or ((ch.get("finish_details") or {}).get("type"))
            # --- レスポンス解析の直後などに追記 ---
            if isinstance(data, dict):
                meta = {
                    "status": getattr(resp, "status_code", None),
                    "finish": reason,
                    "usage": data.get("usage", {}),
                    "len_messages": len(convo),
                    "model": MODEL,
                }
                st.session_state["_last_call_meta"] = meta

            if not chunk:
                parts.append(f"（返事の形が凍ってしまったみたい…：{str(data)[:200]}）")
                break

            parts.append(chunk)

            # 継ぎ足し判定
            if not (auto_continue and _need_more(reason, chunk)):
                break

            # 続きを依頼して再コール
            convo = convo + [
                {"role": "assistant", "content": chunk},
                {"role": "user", "content": "続きのみを、重複や言い直しなしで出力してください。"},
            ]

    # ✨正: 最後に一度だけアシスタント発言を積む
    a = "".join(parts).strip()
    if not a:
        a = "（返答の生成に失敗しました。少し内容を短くしてもう一度お試しください）"
    st.session_state.messages.append({"role": "assistant", "content": a})

# ================== 会話表示 ==================
st.subheader("会話")
dialog = [m for m in st.session_state.messages if m["role"] in ("user", "assistant")]

for m in dialog:
    role = m["role"]
    raw  = m["content"].strip()
    # 表示側だけ制限（ログ保存はフル）
    shown = raw if len(raw) <= DISPLAY_LIMIT else (raw[:DISPLAY_LIMIT] + " …[truncated]")
    txt   = html.escape(shown)

    if role == "user":
        st.markdown(f"<div class='chat-bubble user'><b>あなた：</b><br>{txt}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble assistant'><b>フローリア：</b><br>{txt}</div>", unsafe_allow_html=True)

# ================== デバッグ情報表示（任意） ==================
# 直近のAPI呼び出し結果（ステータスやトークン数など）を可視化できる
show_dbg = st.checkbox("デバッグを表示", False)
if show_dbg and "_last_call_meta" in st.session_state:
    st.markdown("###### 最後の呼び出し情報")
    st.json(st.session_state["_last_call_meta"])

# ================== 入力欄 & ヒント ==================
hint_col, _ = st.columns([1, 3])
if hint_col.button("ヒントを入力欄に挿入", disabled=st.session_state["_busy"]):
    # テキストエリアを描画する前に代入しているので安全
    st.session_state["user_input"] = STARTER_HINT

st.text_area(
    "あなたの言葉（複数行OK・空行不要）",
    key="user_input",
    height=160,
    placeholder=(STARTER_HINT if st.session_state.get("show_hint") else ""),
    label_visibility="visible",
)

# ================== ボタン群 ==================
c_send, c_new, c_show, c_dl = st.columns([1, 1, 1, 1])

# 送信（同一ランではクリアしない → フラグだけ立てて rerun）
if c_send.button("送信", type="primary", disabled=st.session_state["_busy"]):
    txt = st.session_state.get("user_input", "").strip()
    if txt:
        st.session_state["_pending_text"] = txt
        st.session_state["_do_send"] = True
        st.session_state["_clear_input"] = True
        st.rerun()

# 送信処理（次ランで安全に実行）
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

# 新しい会話
if c_new.button("新しい会話を始める", use_container_width=True, disabled=st.session_state["_busy"]):
    st.session_state["_do_reset"] = True
    st.rerun()

# 最近10件
if c_show.button("最近10件を表示", use_container_width=True, disabled=st.session_state["_busy"]):
    st.info("最近10件の会話を下に表示します。")
    recent = [m for m in st.session_state.messages if m["role"] in ("user", "assistant")][-10:]
    for m in recent:
        role = "あなた" if m["role"] == "user" else "フローリア"
        st.write(f"**{role}**：{m['content'].strip()}")

# 会話ログ保存
if c_dl.button("会話ログを保存（JSON）", use_container_width=True, disabled=st.session_state["_busy"]):
    js = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    st.download_button("JSON をダウンロード", js, file_name="floria_chat_log.json", mime="application/json")
