import os

import streamlit as st
from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)

load_dotenv()

LANGUAGES = {"영어": "English", "일본어": "Japanese", "베트남어": "Vietnamese"}
MAX_CHARS = 5000
DEFAULT_MODEL = "gpt-6-astra"
SYSTEM_PROMPT = (
    "You are a professional translator. Translate the user's text into {target_language}. "
    "Output only the translated text, with no explanations or quotes. "
    "Preserve line breaks and tone."
)


class TranslationError(Exception):
    """사용자에게 그대로 보여줄 수 있는 메시지를 담은 예외."""


def translate(text: str, target_language: str) -> str:
    """text를 target_language(영문 언어명)로 번역해 반환한다."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise TranslationError(
            "OPENAI_API_KEY가 설정되지 않았습니다. 프로젝트 폴더의 `.env` 파일에 "
            "`OPENAI_API_KEY=...` 를 추가한 뒤 앱을 다시 실행해 주세요."
        )
    model = os.getenv("OPENAI_MODEL", "").strip() or DEFAULT_MODEL
    client = OpenAI(api_key=api_key, timeout=60.0)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(target_language=target_language)},
        {"role": "user", "content": text},
    ]
    try:
        try:
            resp = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
        except BadRequestError as e:
            # 일부 모델은 temperature 지정을 허용하지 않으므로 한 번 더 시도
            if "temperature" not in str(e).lower():
                raise
            resp = client.chat.completions.create(model=model, messages=messages)
    except AuthenticationError:
        raise TranslationError("API 키가 올바르지 않습니다. `.env`의 OPENAI_API_KEY를 확인해 주세요.")
    except PermissionDeniedError:
        raise TranslationError(f"모델 `{model}`에 접근할 권한이 없습니다. 계정 권한과 OPENAI_MODEL을 확인해 주세요.")
    except NotFoundError:
        raise TranslationError(f"모델 `{model}`을(를) 찾을 수 없습니다. `.env`의 OPENAI_MODEL 값을 확인해 주세요.")
    except RateLimitError:
        raise TranslationError("요청 한도를 초과했거나 사용 가능한 크레딧이 부족합니다. 잠시 후 다시 시도해 주세요.")
    except (APIConnectionError, APITimeoutError):
        raise TranslationError("OpenAI 서버에 연결하지 못했습니다. 네트워크 상태를 확인하고 다시 시도해 주세요.")
    except BadRequestError:
        raise TranslationError("요청이 거부되었습니다. 입력 내용이나 OPENAI_MODEL 설정을 확인해 주세요.")
    except APIStatusError as e:
        raise TranslationError(f"OpenAI API 오류가 발생했습니다. (상태 코드 {e.status_code})")
    content = resp.choices[0].message.content if resp.choices else None
    if not content or not content.strip():
        raise TranslationError("번역 결과가 비어 있습니다. 다시 시도해 주세요.")
    return content.strip()


st.set_page_config(page_title="다국어 번역기", page_icon="🌐", layout="centered")

st.markdown(
    """
<style>
.block-container { max-width: 760px; padding-top: 2.5rem; padding-bottom: 3rem; }
header[data-testid="stHeader"] { background: transparent; }
.app-title { font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin: 0; line-height: 1.2; }
.app-sub { opacity: .65; margin: .25rem 0 1.5rem; font-size: .98rem; }
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px; border-color: rgba(128,128,128,.28);
    box-shadow: 0 2px 14px rgba(79,70,229,.07);
}
div[data-testid="stTextArea"] textarea { font-size: 1.02rem; line-height: 1.6; border-radius: 12px; }
.char-count { text-align: right; font-size: .82rem; opacity: .6; margin-top: -.4rem; }
.char-count.over { color: #dc2626; opacity: 1; font-weight: 600; }
div[data-testid="stButton"] button {
    border-radius: 12px; font-weight: 600; padding: .65rem 0; border: 1px solid rgba(79,70,229,.45);
    transition: transform .08s ease, box-shadow .15s ease, background .15s ease;
}
div[data-testid="stButton"] button:hover {
    border-color: #4f46e5; color: #4f46e5; transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(79,70,229,.2);
}
div[data-testid="stButton"] button:active { transform: translateY(0); }
.result-head { display: flex; align-items: center; gap: .6rem; margin-bottom: .6rem; font-weight: 700; font-size: 1.05rem; }
.badge { background: rgba(79,70,229,.14); color: #4f46e5; border-radius: 999px; padding: .15rem .7rem; font-size: .82rem; font-weight: 700; }
.placeholder { opacity: .55; padding: 1.2rem 0; text-align: center; }
div[data-testid="stCode"] pre { white-space: pre-wrap !important; word-break: break-word; font-size: 1rem; line-height: 1.65; }
@media (prefers-color-scheme: dark) {
    .badge { background: rgba(129,140,248,.2); color: #c7d2fe; }
    div[data-testid="stButton"] button { border-color: rgba(129,140,248,.5); }
    div[data-testid="stButton"] button:hover { border-color: #818cf8; color: #c7d2fe; }
}
@media (max-width: 640px) {
    .block-container { padding: 1.5rem 1rem 2rem; }
    .app-title { font-size: 1.55rem; }
    div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: .5rem; }
    div[data-testid="stHorizontalBlock"] > div { min-width: 0 !important; flex: 1 1 0 !important; }
    div[data-testid="stButton"] button { font-size: .88rem; padding: .6rem 0; }
}
</style>
<p class="app-title">🌐 다국어 번역기</p>
<p class="app-sub">글을 입력하고 번역할 언어 버튼을 눌러 보세요.</p>
""",
    unsafe_allow_html=True,
)

with st.container(border=True):
    text = st.text_area(
        "번역할 글을 입력하세요",
        height=180,
        key="input_text",
        placeholder="여기에 번역할 글을 입력하세요...",
    )
    over = len(text) > MAX_CHARS
    st.markdown(
        f'<div class="char-count{" over" if over else ""}">{len(text):,} / {MAX_CHARS:,}자</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(len(LANGUAGES))
    clicked = None
    for col, label in zip(cols, LANGUAGES):
        if col.button(label, use_container_width=True, key=f"btn_{label}"):
            clicked = label

result_slot = st.empty()

if clicked:
    st.session_state.pop("result", None)
    st.session_state.pop("error", None)
    st.session_state.pop("warning", None)
    if not text.strip():
        st.session_state["warning"] = "번역할 글을 입력해 주세요."
    elif len(text) > MAX_CHARS:
        st.session_state["warning"] = (
            f"글자 수 제한({MAX_CHARS:,}자)을 초과했습니다. 현재 {len(text):,}자입니다."
        )
    else:
        try:
            with result_slot.container(border=True):
                with st.spinner(f"{clicked}로 번역하는 중..."):
                    result = translate(text, LANGUAGES[clicked])
            st.session_state["result"] = (clicked, result)
        except TranslationError as e:
            st.session_state["error"] = str(e)
        except Exception:
            st.session_state["error"] = "예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

with result_slot.container(border=True):
    if "warning" in st.session_state:
        st.warning(st.session_state["warning"])
    elif "error" in st.session_state:
        st.error(st.session_state["error"])
    elif "result" in st.session_state:
        label, result = st.session_state["result"]
        st.markdown(
            f'<div class="result-head">번역 결과 <span class="badge">{LANGUAGES[label]}</span></div>',
            unsafe_allow_html=True,
        )
        st.code(result, language=None, wrap_lines=True)
    else:
        st.markdown(
            '<div class="placeholder">언어 버튼을 누르면 여기에 번역 결과가 표시됩니다.</div>',
            unsafe_allow_html=True,
        )
