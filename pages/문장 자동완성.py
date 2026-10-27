
import streamlit as st
import re
import json
from urllib.parse import quote

st.set_page_config(
    page_title="한마디 도우미",
    page_icon="💙",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# 하늘색 디자인
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #D9F0FF 0%, #F3FAFF 48%, #FFFFFF 100%);
}
.block-container {
    max-width: 650px;
    padding: 1.5rem 1rem 3rem;
}
h1, h2, h3 {
    color: #285D86 !important;
}
h1 {
    font-size: 2rem !important;
    text-align: center;
}
p, label, li {
    font-size: 1.05rem;
    line-height: 1.65;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.94);
    border: 1px solid #D6EAF8;
    border-radius: 22px;
    padding: 15px;
}
div.stButton > button,
div.stDownloadButton > button {
    min-height: 52px;
    width: 100%;
    border-radius: 15px;
    font-size: 1.05rem;
    font-weight: 650;
    border: 1px solid #B9DDF4;
    background: #E5F4FF;
    color: #285D86;
}
div.stButton > button:hover,
div.stDownloadButton > button:hover {
    background: #CDEAFF;
    border-color: #8CC8EF;
    color: #174B73;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: 12px;
    font-size: 1.05rem;
    background: #FAFDFF;
}
div[data-baseweb="select"] > div {
    border-radius: 12px;
    background: #FAFDFF;
}
div[data-testid="stAlert"] {
    border-radius: 14px;
}
hr {
    border-color: #D8EAF7;
}
.hero {
    background: linear-gradient(135deg, #BDE5FF, #EAF7FF);
    border: 1px solid #C8E7FA;
    border-radius: 25px;
    padding: 24px 18px;
    text-align: center;
    margin-bottom: 18px;
}
.hero-title {
    font-size: 29px;
    font-weight: 800;
    color: #285D86;
}
.hero-subtitle {
    color: #507895;
    font-size: 15px;
}
.section-label {
    color: #285D86;
    font-size: 20px;
    font-weight: 750;
    margin-bottom: 8px;
}
.small-note {
    color: #63839B;
    font-size: 13px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 문장 자료
# -----------------------------
SITUATIONS = {
    "👨‍👩‍👧 가족": {
        "안부": "{recipient}아, 잘 지내고 있니? 나는 잘 지내고 있어.",
        "전화 부탁": "{recipient}아, 시간이 될 때 나에게 전화해 줘.",
        "방문 부탁": "{recipient}아, 시간이 되면 우리 집에 한번 와 줘.",
        "감사": "{recipient}아, 항상 챙겨 줘서 고맙다.",
        "식사": "{recipient}아, 밥은 잘 먹고 다니니? 건강 잘 챙기렴.",
        "직접 작성": "{recipient}에게 연락하고 싶어.",
    },
    "🏥 병원": {
        "진료 예약": "{recipient}, 진료 예약을 하고 싶습니다.",
        "예약 변경": "{recipient}, 진료 예약 날짜를 변경하고 싶습니다.",
        "약 문의": "{recipient}, 약을 어떻게 먹어야 하는지 알려 주세요.",
        "도움 요청": "{recipient}, 도움이 필요합니다. 도와주세요.",
        "직접 작성": "{recipient}에게 문의하고 싶습니다.",
    },
    "🛒 일상": {
        "가격 문의": "{recipient}, 이 물건은 얼마인가요?",
        "길 묻기": "{recipient}, {keyword}에 어떻게 가나요?",
        "물건 찾기": "{recipient}, {keyword}를 찾고 있는데 도와주세요.",
        "약속": "{recipient}, {keyword}에서 만나요.",
        "감사": "{recipient}, 도와주셔서 감사합니다.",
        "부탁": "{recipient}, 잠시 도와주실 수 있나요?",
        "직접 작성": "{recipient}에게 {keyword}에 대해 이야기하고 싶습니다.",
    },
    "🚨 긴급 연락": {
        "도움 요청": "{recipient}, 지금 도움이 필요해요. 연락해 주세요.",
        "몸이 아픔": "{recipient}, 몸이 많이 아파요. 도와주세요.",
        "길을 잃음": "{recipient}, 길을 잃었어요. 연락해 주세요.",
        "위험한 상황": "{recipient}, 지금 위험한 상황이에요. 도움을 요청해 주세요.",
        "직접 작성": "{recipient}, 지금 도움이 필요합니다.",
    },
}

# -----------------------------
# 세션 데이터
# -----------------------------
if "contacts" not in st.session_state:
    st.session_state.contacts = {}

if "generated_sentence" not in st.session_state:
    st.session_state.generated_sentence = ""

if "edited_sentence" not in st.session_state:
    st.session_state.edited_sentence = ""

# -----------------------------
# 첫 화면
# -----------------------------
st.markdown("""
<div class="hero">
    <div style="font-size:36px;">💙</div>
    <div class="hero-title">한마디 도우미</div>
    <div class="hero-subtitle">
        소중한 사람에게 마음을 쉽게 전해 보세요
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📖 간단한 사용 방법"):
    st.markdown("""
    **1. 연락처 저장** — 이름과 전화번호를 입력해요.

    **2. 받을 사람 선택** — 저장한 연락처 중 한 명을 골라요.

    **3. 문장 만들기** — 상황과 전달할 내용을 선택해요.

    **4. 문장 수정** — 완성된 문장을 원하는 대로 고쳐요.

    **5. 문자 보내기** — 문자 앱을 열고 내용을 확인한 뒤 보내요.
    """)

st.caption("연락처는 현재 세션 동안 임시로 저장됩니다.")
st.divider()

# -----------------------------
# 연락처 관리
# -----------------------------
with st.container(border=True):
    st.markdown(
        '<div class="section-label">👤 나의 연락처</div>',
        unsafe_allow_html=True,
    )
    st.write("자주 연락하는 사람을 등록해 보세요.")

    with st.form("contact_form", clear_on_submit=True):
        name_input = st.text_input(
            "이름",
            placeholder="예: 우리 아들",
            max_chars=40,
        )
        phone_input = st.text_input(
            "전화번호",
            placeholder="예: 010-1234-5678",
            max_chars=20,
        )
        save_contact = st.form_submit_button(
            "＋ 연락처 저장",
            use_container_width=True,
        )

    if save_contact:
        name = name_input.strip()
        phone = re.sub(r"[\s()-]", "", phone_input.strip())

        if not name:
            st.warning("이름을 입력해 주세요.")
        elif not re.fullmatch(r"\+?\d{8,15}", phone):
            st.warning("전화번호를 다시 확인해 주세요.")
        elif name in st.session_state.contacts:
            st.warning("같은 이름이 있어요. 다른 이름을 입력해 주세요.")
        else:
            st.session_state.contacts[name] = phone
            st.success(f"{name} 연락처를 저장했어요!")
            st.rerun()

    if st.session_state.contacts:
        st.markdown("**저장된 연락처**")
        for person, number in list(st.session_state.contacts.items()):
            left, right = st.columns([3, 1])
            left.write(f"💙 {person}")
            left.caption(number)

            if right.button("삭제", key=f"del_{person}"):
                del st.session_state.contacts[person]
                st.rerun()

    with st.expander("📁 연락처 백업 및 복원"):
        if st.session_state.contacts:
            backup = json.dumps(
                st.session_state.contacts,
                ensure_ascii=False,
                indent=2,
            )
            st.download_button(
                "연락처 백업 파일 저장",
                data=backup,
                file_name="연락처_백업.json",
                mime="application/json",
                use_container_width=True,
            )

        uploaded = st.file_uploader(
            "백업 파일 선택",
            type=["json"],
            key="restore_contacts",
        )

        if uploaded is not None and st.button("연락처 불러오기"):
            try:
                data = json.load(uploaded)
                if not isinstance(data, dict) or len(data) > 200:
                    raise ValueError()

                valid = {}
                for person, number in data.items():
                    cleaned = re.sub(r"[\s()-]", "", str(number))
                    if (
                        isinstance(person, str)
                        and person.strip()
                        and len(person) <= 40
                        and re.fullmatch(r"\+?\d{8,15}", cleaned)
                    ):
                        valid[person.strip()] = cleaned

                if not valid:
                    raise ValueError()

                st.session_state.contacts.update(valid)
                st.success("연락처를 불러왔어요!")
                st.rerun()
            except Exception:
                st.error("파일을 읽을 수 없어요. 올바른 백업 파일인지 확인해 주세요.")

# -----------------------------
# 연락처 선택
# -----------------------------
if not st.session_state.contacts:
    st.info("먼저 연락처를 저장해 주세요. 그다음 문장을 만들 수 있어요.")
    st.stop()

st.divider()

with st.container(border=True):
    st.markdown(
        '<div class="section-label">💌 누구에게 보낼까요?</div>',
        unsafe_allow_html=True,
    )

    selected_name = st.selectbox(
        "문자 받을 사람",
        list(st.session_state.contacts.keys()),
    )
    selected_phone = st.session_state.contacts[selected_name]

    st.success(f"선택한 연락처: {selected_name}")
    st.caption(f"전화번호: {selected_phone}")

# -----------------------------
# 문장 만들기
# -----------------------------
st.divider()

with st.container(border=True):
    st.markdown(
        '<div class="section-label">✏️ 전하고 싶은 말</div>',
        unsafe_allow_html=True,
    )

    situation = st.selectbox(
        "상황을 선택하세요",
        list(SITUATIONS.keys()),
    )

    message_type = st.selectbox(
        "어떤 말을 하고 싶으세요?",
        list(SITUATIONS[situation].keys()),
    )

    keyword = st.text_input(
        "추가할 단어 (선택)",
        placeholder="예: 시장, 내일, 오후 3시",
        max_chars=100,
    )

    extra = st.text_input(
        "더 넣고 싶은 말 (선택)",
        placeholder="예: 조금 늦을 것 같아요",
        max_chars=100,
    )

    if st.button(
        "✨ 문장 만들기",
        type="primary",
        use_container_width=True,
    ):
        try:
            template = SITUATIONS[situation][message_type]
            sentence = template.format(
                recipient=selected_name,
                keyword=keyword.strip() or "그곳",
            )

            if extra.strip():
                sentence = sentence.rstrip(" .!?") + ". " + extra.strip()
                if sentence[-1] not in ".!?":
                    sentence += "."

            st.session_state.generated_sentence = sentence
            st.session_state.edited_sentence = sentence
            st.rerun()
        except Exception:
            st.error("문장을 만들지 못했어요. 다시 선택해 주세요.")

# -----------------------------
# 문장 수정 및 문자 연결
# -----------------------------
st.divider()

with st.container(border=True):
    st.markdown(
        '<div class="section-label">📨 문장 확인하기</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.generated_sentence:
        st.write("아래 문장을 눌러 자유롭게 수정할 수 있어요.")

        st.text_area(
            "완성된 문장",
            key="edited_sentence",
            height=160,
            max_chars=2000,
        )

        final_message = st.session_state.edited_sentence.strip()

        if final_message:
            st.markdown("**문자에 들어갈 내용**")
            st.code(final_message, language=None)

            encoded_message = quote(final_message, safe="")
            encoded_phone = quote(selected_phone, safe="")

            # Android와 iPhone의 문자 앱 연결 방식은 다를 수 있음
            android_link = (
                f"sms:{encoded_phone}?body={encoded_message}"
            )
            iphone_link = (
                f"sms:{encoded_phone}&body={encoded_message}"
            )

            st.markdown(
                f'<a href="{android_link}" target="_self" '
                'style="display:block;text-align:center;'
                'background:#79C7F2;color:#174B73;'
                'padding:16px;border-radius:16px;'
                'font-size:19px;font-weight:bold;'
                'text-decoration:none;margin:10px 0;">'
                '📩 문자 앱 열기 · 일반 방식</a>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<a href="{iphone_link}" target="_self" '
                'style="display:block;text-align:center;'
                'background:#D8F0FF;color:#174B73;'
                'padding:16px;border-radius:16px;'
                'font-size:19px;font-weight:bold;'
                'text-decoration:none;margin:10px 0;">'
                '📱 문자 앱 열기 · 아이폰 방식</a>',
                unsafe_allow_html=True,
            )

            st.caption(
                "문자 앱에서 받는 사람과 내용을 확인한 뒤 직접 전송하세요. "
                "기기나 브라우저에 따라 자동 입력이 되지 않을 수 있어요."
            )

            st.download_button(
                "📄 문장 파일로 저장",
                data=final_message,
                file_name="완성된_문장.txt",
                mime="text/plain",
                use_container_width=True,
            )

            if st.button("🔄 새 문장 만들기", use_container_width=True):
                st.session_state.generated_sentence = ""
                st.session_state.edited_sentence = ""
                st.rerun()
    else:
        st.info("위에서 문장을 만든 뒤 이곳에서 수정할 수 있어요.")

# -----------------------------
# 안내
# -----------------------------
st.markdown("""
<div class="hero">
    <div style="font-size:27px;">☁️ 💙 ☁️</div>
    <div style="font-size:18px;font-weight:bold;color:#285D86;">
        마음을 전하는 쉬운 방법
    </div>
    <div class="hero-subtitle">
        긴급한 상황에서는 주변 사람이나 119에 도움을 요청하세요.
    </div>
</div>
""", unsafe_allow_html=True)
