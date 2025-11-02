# app_multilang.py — Floria Chat (Streamlit Edition, wide & auto-clear, Multilingual)

import os, json, requests, html, time, streamlit as st

# ================== 多言語辞書 ==================
LANGS = {
    "日本語": {
        "APP_TITLE": "❄️ Floria Chat — Streamlit Edition",
        "ROLE_EXPANDER": "世界観とあなたの役割（ロール）",
        "ROLE_BODY": (
            "舞台：白霧の湖のほとり。水と氷の精霊フローリアは、封印の鎖に縛られている。\n"
            "あなた：旅の来訪者。観察者ではなく、語りかけ・問いかけ・提案で物語を動かす当事者。\n"
            "お願い：命令口調よりも、状況描写や気持ち・意図を添えて話しかけると、会話が豊かになります。"
        ),
        "HINT_CHECK": "入力ヒントを表示する",
        "CONNECT_EXPANDER": "接続設定",
        "SL_TEMPERATURE": "temperature",
        "SL_MAXTOKENS": "max_tokens（1レス上限）",
        "SL_WRAPWIDTH": "折り返し幅",
        "CB_AUTOCONT": "長文を自動で継ぎ足す",
        "SL_MAXCONT": "最大継ぎ足し回数",
        "CHAT_HEADER": "会話",
        "YOU": "あなた",
        "FLORIA": "フローリア",
        "BTN_SEND": "送信",
        "BTN_NEW": "新しい会話を始める",
        "BTN_RECENT": "最近10件を表示",
        "BTN_SAVE": "会話ログを保存（JSON）",
        "TXTAREA_LABEL": "あなたの言葉（複数行OK・空行不要）",
        "PLACEHOLDER": "……白い霧の向こうに気配がする。そこにいるのは誰？",
        "HINT_BUTTON": "ヒントを入力欄に挿入",
        "RECENT_INFO": "最近10件の会話を下に表示します。",
        "TEST_EXPANDER": "接続テスト（任意）",
        "TEST_BUTTON": "モデルへテストリクエスト",
        "TEST_ERROR": "接続エラー",
        "SAVE_HEADER": "会話ログの保存",
        "SAVE_DL": "JSON をダウンロード",
        "LOAD_HEADER": "会話ログの読み込み",
        "LOAD_FILE": "保存した JSON を選択",
        "LOAD_MODE": "読込モード",
        "LOAD_REPLACE": "置き換え",
        "LOAD_APPEND": "末尾に追記",
        "LOAD_PREVIEW": "内容をプレビュー",
        "LOAD_BUTTON": "読み込む",
        "LOAD_PREVIEW_CAP": "先頭5件プレビュー",
        "LOAD_INVALID": "JSON 形式が不正です。messages の配列（各要素に role と content）が必要です。",
        "LOAD_OK": "読込が完了しました。",
        "LOAD_FAIL": "JSON の読み込みに失敗しました",
        "DBG_CHECK": "デバッグを表示",
        "DBG_HEADER": "最後の呼び出し情報",
        "BTN_NEW_WARN": "新しい会話（履歴が消えます）",
        "RESET_WARN": "会話履歴がすべて消えます。続行しますか？",
        "RESET_YES": "はい、リセットする",
        "RESET_NO": "やめる",
        "PING": "ping",
        "PONGQ": "pong?",
        "AUTH_MISSING": "LLAMA_API_KEY が未設定です。Streamlit → Settings → Secrets で設定してください。",
        "SPINNER": "フローリアが考えています…",
        "ERR_AUTH": "（認証に失敗しました。LLAMA_API_KEY を確認してください）",
        "ERR_FROZEN": "（返事の形が凍ってしまったみたい…）",
        "ERR_DELIVERY": "（ごめんなさい、冷たい霧で声が届きません… {code}: {err}）",
        "ERR_EMPTY": "（返答の生成に失敗しました。少し内容を短くしてもう一度お試しください）",
        "SYSTEM_PROMPT": (
            "あなたは『フローリア』。水と氷の精霊の乙女。"
            "口調は穏やかで知的、ややツンデレ。描写は上品。"
            "出力は素の文章。行頭に装飾記号（*,・,•,★ など）を付けない。"
            "見出しや箇条書きは使わない。"
        ),
    },
    "English": {
        "APP_TITLE": "❄️ Floria Chat — Streamlit Edition",
        "ROLE_EXPANDER": "World & Your Role",
        "ROLE_BODY": (
            "Stage: On the shore of a misty white lake. Floria, a spirit of water and ice, is bound by sealing chains.\n"
            "You: A traveling visitor. Not a mere observer — speak, ask, suggest, and drive the story forward.\n"
            "Tip: Instead of commands, adding mood, intent, and description will enrich the dialogue."
        ),
        "HINT_CHECK": "Show starter hint",
        "CONNECT_EXPANDER": "Connection",
        "SL_TEMPERATURE": "temperature",
        "SL_MAXTOKENS": "max_tokens (per reply limit)",
        "SL_WRAPWIDTH": "wrap width",
        "CB_AUTOCONT": "auto-continue long replies",
        "SL_MAXCONT": "max continuations",
        "CHAT_HEADER": "Conversation",
        "YOU": "You",
        "FLORIA": "Floria",
        "BTN_SEND": "Send",
        "BTN_NEW": "Start New Conversation",
        "BTN_RECENT": "Show last 10 turns",
        "BTN_SAVE": "Save Log (JSON)",
        "TXTAREA_LABEL": "Your message (multiline OK)",
        "PLACEHOLDER": "…A presence in the white fog. Who is there?",
        "HINT_BUTTON": "Insert hint to input",
        "RECENT_INFO": "Showing the last 10 turns below.",
        "TEST_EXPANDER": "Connection Test (optional)",
        "TEST_BUTTON": "Send test request",
        "TEST_ERROR": "Connection error",
        "SAVE_HEADER": "Save Conversation Log",
        "SAVE_DL": "Download JSON",
        "LOAD_HEADER": "Load Conversation Log",
        "LOAD_FILE": "Choose saved JSON",
        "LOAD_MODE": "Load mode",
        "LOAD_REPLACE": "Replace",
        "LOAD_APPEND": "Append to tail",
        "LOAD_PREVIEW": "Preview content",
        "LOAD_BUTTON": "Load",
        "LOAD_PREVIEW_CAP": "Preview (first 5 items)",
        "LOAD_INVALID": "Invalid JSON format. Must be an array of messages with 'role' and 'content'.",
        "LOAD_OK": "Loaded successfully.",
        "LOAD_FAIL": "Failed to load JSON",
        "DBG_CHECK": "Show debug",
        "DBG_HEADER": "Last call meta",
        "BTN_NEW_WARN": "Start New Conversation (clears history)",
        "RESET_WARN": "This will erase the entire conversation history. Continue?",
        "RESET_YES": "Yes, reset",
        "RESET_NO": "Cancel",
        "PING": "ping",
        "PONGQ": "pong?",
        "AUTH_MISSING": "LLAMA_API_KEY is missing. Set it in Streamlit → Settings → Secrets.",
        "SPINNER": "Floria is thinking…",
        "ERR_AUTH": "(Authentication failed. Please check your LLAMA_API_KEY.)",
        "ERR_FROZEN": "(The reply seems frozen in ice…) ",
        "ERR_DELIVERY": "(Sorry, my voice can’t reach through the cold mist… {code}: {err})",
        "ERR_EMPTY": "(Failed to generate a reply. Try a shorter message and resend.)",
        "SYSTEM_PROMPT": (
            "You are “Floria”, a maiden spirit of water and ice. "
            "Tone: calm, intelligent, slightly tsundere. Descriptions are refined. "
            "Output plain prose (no leading decorative symbols like *,・,•,★). "
            "Do not use headings or bullet lists."
        ),
    },
}

# ================== 基本設定 ==================
AVAILABLE_LANGS = list(LANGS.keys())
DEFAULT_LANG = "日本語"

MAX_LOG = 500
DISPLAY_LIMIT = 20000  # 表示のみの上限（保存はフル）

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

# ================== 言語選択 ==================
lang = st.sidebar.radio("Language / 言語", AVAILABLE_LANGS, index=AVAILABLE_LANGS.index(DEFAULT_LANG))
L = LANGS[lang]

# 言語切替時に会話をリセット（任意：仕様どおり自動リセット）
if "lang" not in st.session_state:
    st.session_state["lang"] = lang
elif st.session_state["lang"] != lang:
    st.session_state["lang"] = lang
    # 会話リセット（SYSTEM_PROMPTを言語に合わせる）
    st.session_state["messages"] = [{"role": "system", "content": L["SYSTEM_PROMPT"]}]
    st.session_state["_pending_text"] = ""
    st.session_state["_do_send"] = False
    st.session_state["_busy"] = False
    st.session_state["_clear_input"] = False
    st.session_state["_do_reset"] = False
    st.session_state.pop("_last_call_meta", None)
    st.rerun()

SYSTEM_PROMPT = L["SYSTEM_PROMPT"]
STARTER_HINT = L["PLACEHOLDER"]

# ================== session_state 初期化 ==================
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""
if "show_hint" not in st.session_state:
    st.session_state["show_hint"] = False

DEFAULTS = {
    "_busy": False,
    "_do_send": False,
    "_pending_text": "",
    "_clear_input": False,
    "_do_reset": False,
    "_ask_reset": False,   # ← 追加
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- フラグ処理（UI描画前） ---
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
    st.error(L["AUTH_MISSING"])
    st.stop()

# ================== パラメータUI ==================
st.title(L["APP_TITLE"])
with st.expander(L["ROLE_EXPANDER"], expanded=False):
    st.markdown(L["ROLE_BODY"])
    st.checkbox(L["HINT_CHECK"], key="show_hint")

with st.expander(L["CONNECT_EXPANDER"], expanded=False):
    c1, c2, c3 = st.columns(3)
    temperature = c1.slider(L["SL_TEMPERATURE"], 0.0, 1.5, 0.70, 0.05)
    max_tokens  = c2.slider(L["SL_MAXTOKENS"], 64, 4096, 800, 16)
    wrap_width  = c3.slider(L["SL_WRAPWIDTH"], 20, 100, 80, 1)

    r1, r2 = st.columns(2)
    auto_continue = r1.checkbox(L["CB_AUTOCONT"], True)
    max_cont      = r2.slider(L["SL_MAXCONT"], 1, 6, 3)

st.markdown(f"<style>.chat-bubble {{ max-width: min(90vw, {wrap_width}ch); }}</style>", unsafe_allow_html=True)

# 任意：接続テスト
with st.expander(L["TEST_EXPANDER"], expanded=False):
    if st.button(L["TEST_BUTTON"]):
        headers = {
            "Authorization": f"Bearer {API}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "HTTP-Referer": "https://streamlit.io",
            "X-Title": "Floria-Streamlit/multilang",
        }
        payload = {
            "model": MODEL,
            "messages": [{"role": "system", "content": L["PING"]}, {"role": "user", "content": L["PONGQ"]}],
            "max_tokens": 8,
            "temperature": 0.0,
        }
        try:
            r = requests.post(f"{BASE}/chat/completions", headers=headers, json=payload, timeout=(10, 30))
            st.code(f"status={r.status_code}\nbody={r.text[:500]}", language="text")
        except Exception as e:
            st.error(f'{L["TEST_ERROR"]}: {e}')

# ================== HTTP（軽いリトライ） ==================
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
        if resp.status_code in (429, 502, 503):
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

    # ユーザー発言を履歴に追加
    st.session_state.messages.append({"role": "user", "content": user_text})

    # コンテキストを用意（大きめ→必要なら縮小）
    base = st.session_state.messages
    max_slice = 60
    min_slice = 20
    convo = [base[0]] + base[-max_slice:]

    headers = {
        "Authorization": f"Bearer {API}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Floria-Streamlit/multilang",
    }

    def _one_call(msgs):
        payload = {
            "model": MODEL,
            "messages": msgs,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
        }
        return _post_with_retry(f"{BASE}/chat/completions", headers, payload, timeout=(10, 60))

    def _call_with_shrink(msgs):
        nonlocal max_slice
        while True:
            resp = _one_call(msgs)
            if getattr(resp, "status_code", 599) == 200:
                return resp, msgs
            # コンテキスト超過らしきエラーを検知
            body_text = ""
            try:
                _j = resp.json()
                body_text = json.dumps(_j, ensure_ascii=False)[:800]
            except Exception:
                body_text = getattr(resp, "text", "")[:800]
            is_ctx_err = (getattr(resp, "status_code", 0) in (400, 413)) or ("context" in body_text.lower() and "length" in body_text.lower())
            if not is_ctx_err or max_slice <= min_slice:
                return resp, msgs
            max_slice = max(min_slice, max_slice // 2)
            msgs = [base[0]] + base[-max_slice:]

    parts = []
    reason = None

    def _need_more(reason, chunk: str):
        if reason not in ("length", "max_tokens"):
            return False
        return not chunk.rstrip().endswith(("。", "！", "？", ".", "!", "?", "」", "『", "』", "”", "\"", "…"))

    with st.spinner(L["SPINNER"]):
        for _ in range(1 + (max_cont if auto_continue else 0)):
            resp, used_convo = _call_with_shrink(convo)

            try:
                data = resp.json()
            except Exception:
                data = None

            if getattr(resp, "status_code", 599) != 200:
                code = getattr(resp, "status_code", 599)
                if code in (401, 403):
                    parts = [L["ERR_AUTH"]]
                else:
                    err = ""
                    if isinstance(data, dict):
                        err = data.get("error", {}).get("message") or data.get("message") or ""
                    if not err:
                        err = getattr(resp, "text", "")[:500]
                    parts = [L["ERR_DELIVERY"].format(code=code, err=err)]
                break

            chunk = ""
            reason = None
            if isinstance(data, dict) and data.get("choices"):
                ch = data["choices"][0]
                chunk = (ch.get("message", {}) or {}).get("content", "") or ""
                reason = ch.get("finish_reason") or ((ch.get("finish_details") or {}).get("type"))

            # デバッグ用メタ
            if isinstance(data, dict):
                st.session_state["_last_call_meta"] = {
                    "status": getattr(resp, "status_code", None),
                    "finish": reason,
                    "usage": data.get("usage", {}),
                    "len_messages_sent": len(used_convo),
                    "model": MODEL,
                }

            if not chunk:
                parts.append(L["ERR_FROZEN"])
                break

            parts.append(chunk)

            # 継ぎ足し判定
            if not (auto_continue and _need_more(reason, chunk)):
                break

            # 続き要求
            convo = used_convo + [
                {"role": "assistant", "content": chunk},
                {"role": "user", "content": "続きのみを、重複や言い直しなしで出力してください。" if lang == "日本語" else "Continue ONLY the remaining text, no repetition or rephrasing."},
            ]

    # まとめて追加
    a = "".join(parts).strip()
    if not a:
        a = L["ERR_EMPTY"]
    st.session_state.messages.append({"role": "assistant", "content": a})

# ================== 会話表示 ==================
st.subheader(L["CHAT_HEADER"])
dialog = [m for m in st.session_state.messages if m["role"] in ("user", "assistant")]

for m in dialog:
    role = m["role"]
    raw  = m["content"].strip()
    shown = raw if len(raw) <= DISPLAY_LIMIT else (raw[:DISPLAY_LIMIT] + " …[truncated]")
    txt   = html.escape(shown)

    if role == "user":
        st.markdown(f"<div class='chat-bubble user'><b>{L['YOU']}：</b><br>{txt}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble assistant'><b>{L['FLORIA']}：</b><br>{txt}</div>", unsafe_allow_html=True)

# ================== デバッグ情報表示（任意） ==================
show_dbg = st.checkbox(L["DBG_CHECK"], False)
if show_dbg and "_last_call_meta" in st.session_state:
    st.markdown("###### " + L["DBG_HEADER"])
    st.json(st.session_state["_last_call_meta"])

# ================== 入力欄 & ヒント ==================
hint_col, _ = st.columns([1, 3])
if hint_col.button(L["HINT_BUTTON"], disabled=st.session_state["_busy"]):
    st.session_state["user_input"] = STARTER_HINT

st.text_area(
    L["TXTAREA_LABEL"],
    key="user_input",
    height=160,
    placeholder=(STARTER_HINT if st.session_state.get("show_hint") else ""),
    label_visibility="visible",
)

# ================== ボタン群 ==================
c_send, c_new, c_show, c_dl = st.columns([1, 1, 1, 1])

if c_send.button(L["BTN_SEND"], type="primary", disabled=st.session_state["_busy"]):
    txt = st.session_state.get("user_input", "").strip()
    if txt:
        st.session_state["_pending_text"] = txt
        st.session_state["_do_send"] = True
        st.session_state["_clear_input"] = True
        st.rerun()

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

# 新しい会話（確認ダイアログ付き・多言語）
if st.session_state.get("_ask_reset", False):
    with st.container():
        st.warning(L["RESET_WARN"])
        cc1, cc2 = st.columns(2)
        confirm = cc1.button(L["RESET_YES"], use_container_width=True)
        cancel  = cc2.button(L["RESET_NO"],  use_container_width=True)
        if confirm:
            st.session_state["_do_reset"] = True
            st.session_state["_ask_reset"] = False
            st.rerun()
        elif cancel:
            st.session_state["_ask_reset"] = False
else:
    if c_new.button(L.get("BTN_NEW_WARN", L["BTN_NEW"]), use_container_width=True, disabled=st.session_state["_busy"]):
        st.session_state["_ask_reset"] = True
        st.rerun()

if c_show.button(L["BTN_RECENT"], use_container_width=True, disabled=st.session_state["_busy"]):
    st.info(L["RECENT_INFO"])
    recent = [m for m in st.session_state.messages if m["role"] in ("user", "assistant")][-10:]
    for m in recent:
        role = L["YOU"] if m["role"] == "user" else L["FLORIA"]
        st.write(f"**{role}**：{m['content'].strip()}")

# ================== 保存・読込 ==================
st.markdown("---")
st.subheader(L["SAVE_HEADER"])
st.download_button(
    L["SAVE_DL"],
    json.dumps(st.session_state.messages, ensure_ascii=False, indent=2),
    file_name="floria_chat_log.json",
    mime="application/json",
    use_container_width=True
)

st.subheader(L["LOAD_HEADER"])
up = st.file_uploader(L["LOAD_FILE"], type=["json"])
col_l, col_m, col_r = st.columns(3)
load_mode = col_l.radio(L["LOAD_MODE"], [L["LOAD_REPLACE"], L["LOAD_APPEND"]], horizontal=True)
show_preview = col_m.checkbox(L["LOAD_PREVIEW"], value=True)
do_load = col_r.button(L["LOAD_BUTTON"], use_container_width=True, disabled=(up is None or st.session_state.get("_busy", False)))

if up is not None:
    try:
        imported = json.load(up)
        ok = isinstance(imported, list) and all(isinstance(x, dict) and "role" in x and "content" in x for x in imported)
        if not ok:
            st.error(L["LOAD_INVALID"])
        else:
            if show_preview:
                st.caption(L["LOAD_PREVIEW_CAP"])
                st.json(imported[:5])
            if do_load:
                if not (len(imported) > 0 and imported[0].get("role") == "system"):
                    imported = [{"role": "system", "content": SYSTEM_PROMPT}] + imported

                if load_mode == L["LOAD_REPLACE"]:
                    st.session_state["messages"] = imported
                else:
                    base = st.session_state.get("messages", [{"role": "system", "content": SYSTEM_PROMPT}])
                    tail = imported[1:] if (len(imported) > 0 and imported[0].get("role") == "system") else imported
                    st.session_state["messages"] = base + tail

                st.session_state["_pending_text"] = ""
                st.session_state["_do_send"] = False
                st.session_state["_busy"] = False
                st.session_state["_clear_input"] = False
                st.session_state["_do_reset"] = False
                st.session_state.pop("_last_call_meta", None)

                st.success(L["LOAD_OK"])
                st.rerun()
    except Exception as e:
        st.error(f'{L["LOAD_FAIL"]}: {e}')
