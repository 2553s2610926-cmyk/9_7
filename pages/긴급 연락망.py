
import html
import re
import streamlit as st

st.set_page_config(
    page_title="쉬운 긴급 연락망",
    page_icon="🆘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# 화면 디자인: 검은 배경 + 고대비
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    [data-testid="stHeader"] {
        background-color: #000000;
    }
    [data-testid="stSidebar"] {
        background-color: #111111;
    }
    .block-container {
        max-width: 800px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    html, body, [class*="st-"], p, label {
        color: #FFFFFF;
    }
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }
    p, label, li {
        font-size: 18px;
        line-height: 1.65;
    }
    div.stButton > button,
    div.stFormSubmitButton > button {
        min-height: 58px;
        width: 100%;
        border-radius: 12px;
        border: 2px solid #FFFFFF;
        background-color: #202020;
        color: #FFFFFF;
        font-size: 19px;
        font-weight: 700;
    }
    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background-color: #383838;
        color: #FFFFFF;
        border-color: #FFFF00;
    }
    input, textarea {
        background-color: #171717 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stAlert"] {
        background-color: #161616;
    }
    a {
        color: #FFFF00 !important;
        font-weight: 700;
    }
    .contact-card {
        background: #151515;
        border: 2px solid #555555;
        border-radius: 14px;
        padding: 18px;
        margin: 12px 0;
    }
    .phone-link {
        display: block;
        text-align: center;
        background: #176B35;
        color: #FFFFFF !important;
        font-size: 22px;
        font-weight: 800;
        padding: 17px;
        border-radius: 12px;
        border: 2px solid #FFFFFF;
        text-decoration: none !important;
        margin: 12px 0;
    }
    .emergency-link {
        background: #B91C1C;
    }
    .subtext {
        color: #DDDDDD;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 세션 상태 초기화
# 연락처는 현재 세션에서만 유지됩니다.
# -----------------------------
if "contacts" not in st.session_state:
    st.session_state.contacts = []

if "large_text" not in st.session_state:
    st.session_state.large_text = True

if "help_message" not in st.session_state:
    st.session_state.help_message = (
        "지금 도움이 필요해요. "
        "저에게 전화해 주세요."
    )

# -----------------------------
# 도우미 함수
# -----------------------------
def safe_phone(raw_phone):
    """전화번호에 숫자와 맨 앞의 +만 허용합니다."""
    value = raw_phone.strip()
    if not value:
        return None

    cleaned = re.sub(r"[\s\-().]", "", value)

    if not re.fullmatch(r"\+?\d{2,15}", cleaned):
        return None

    return cleaned


def phone_link(phone):
    """전화 링크를 만듭니다."""
    return f"tel:{phone}"


def render_call_button(label, phone, emergency=False):
    """기기의 전화 앱을 열 수 있는 링크를 표시합니다."""
    css_class = "phone-link"
    if emergency:
        css_class += " emergency-link"

    safe_label = html.escape(label)
    safe_number = html.escape(phone)

    st.markdown(
        f'<a class="{css_class}" href="{phone_link(safe_number)}">'
        f'☎️ {safe_label}<br>{safe_number}</a>',
        unsafe_allow_html=True,
    )


# -----------------------------
# 메인 화면
# -----------------------------
st.title("🆘 쉬운 긴급 연락망")
st.markdown(
    "어려운 설정 없이, 필요한 연락처를 쉽게 찾아보세요."
)
st.markdown("---")

# 글씨 크기 설정
with st.expander("⚙️ 화면 글씨 설정"):
    st.session_state.large_text = st.checkbox(
        "글씨를 더 크게 보기",
        value=st.session_state.large_text,
    )
    st.caption(
        "화면이 작게 보이면 기기의 확대 기능도 이용해 주세요."
    )

if st.session_state.large_text:
    st.markdown(
        """
        <style>
        p, label, li, .subtext {
            font-size: 22px !important;
            line-height: 1.7 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# 긴급 전화
st.header("🚨 지금 긴급한 상황인가요?")
st.warning(
    "생명이나 신체가 위험하면 즉시 긴급 전화로 연락하세요. "
    "전화 연결 후 상황과 위치를 알려주세요."
)

render_call_button("112 경찰", "112", emergency=True)
render_call_button("119 소방·구급", "119", emergency=True)

st.caption(
    "버튼을 누르면 기기에 따라 전화 앱이 열립니다. "
    "화면에 표시되는 통화 버튼을 추가로 눌러야 할 수 있습니다."
)

st.markdown("---")

# 가족 및 보호자 연락처
st.header("👨‍👩‍👧 가족 · 보호자 연락처")
st.write("믿을 수 있는 사람의 이름과 전화번호를 등록하세요.")

with st.form("add_contact_form", clear_on_submit=True):
    contact_name = st.text_input(
        "이름 또는 관계",
        placeholder="예: 딸, 아들, 보호자, 이웃",
        max_chars=40,
    )
    contact_phone = st.text_input(
        "전화번호",
        placeholder="예: 010-1234-5678",
        max_chars=25,
    )
    submitted = st.form_submit_button("＋ 연락처 추가")

    if submitted:
        name = contact_name.strip()
        number = safe_phone(contact_phone)

        if not name:
            st.error("이름 또는 관계를 입력해 주세요.")
        elif number is None:
            st.error(
                "전화번호를 확인해 주세요. "
                "숫자와 국가번호 앞의 + 기호만 사용할 수 있습니다."
            )
        elif len(st.session_state.contacts) >= 30:
            st.error("연락처는 최대 30개까지 등록할 수 있습니다.")
        else:
            st.session_state.contacts.append(
                {"name": name, "phone": number}
            )
            st.success(f"{name} 연락처를 추가했습니다.")

if not st.session_state.contacts:
    st.info(
        "아직 등록된 연락처가 없습니다. "
        "위에서 가족이나 보호자를 추가해 주세요."
    )
else:
    for index, contact in enumerate(
        st.session_state.contacts
    ):
        st.markdown('<div class="contact-card">', unsafe_allow_html=True)
        st.subheader(f"👤 {contact['name']}")
        st.write(contact["phone"])
        render_call_button(
            f"{contact['name']}에게 전화하기",
            contact["phone"],
        )

        if st.button(
            f"🗑️ {contact['name']} 연락처 삭제",
            key=f"delete_contact_{index}",
        ):
            st.session_state.contacts.pop(index)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# 도움 요청 메시지
st.header("💬 도움 요청 메시지")
st.write(
    "말로 설명하기 어려울 때 사용할 문구를 선택하세요. "
    "아래 문구를 복사해 문자나 메신저에 붙여 넣을 수 있습니다."
)

message_options = {
    "도움이 필요해요": "지금 도움이 필요해요. 저에게 전화해 주세요.",
    "몸이 아파요": "몸이 아파서 도움이 필요해요. 저에게 연락해 주세요.",
    "집에 혼자 있어요": "지금 집에 혼자 있어요. 확인을 위해 전화해 주세요.",
    "위치를 알려 드릴게요": "도움이 필요해요. 제 위치를 확인해 주세요.",
}

selected_message = st.selectbox(
    "상황을 선택하세요",
    options=list(message_options.keys()),
)

st.session_state.help_message = message_options[selected_message]

st.text_area(
    "복사할 메시지",
    value=st.session_state.help_message,
    height=110,
    help="코드 블록 또는 텍스트 영역의 내용을 선택해 복사할 수 있습니다.",
    key="message_preview",
)

st.code(st.session_state.help_message, language=None)

st.caption(
    "복사 방법: 위 문구를 길게 누르거나 마우스로 선택한 뒤 "
    "복사를 선택하세요. 복사한 문구를 문자나 메신저에 붙여 넣으세요."
)

# 등록된 보호자에게 메시지 전송용 안내
if st.session_state.contacts:
    contact_names = [
        item["name"] for item in st.session_state.contacts
    ]
    st.write("연락할 사람: " + ", ".join(contact_names))
    st.info(
        "이 앱은 메시지를 자동으로 보내지 않습니다. "
        "복사한 문구를 휴대전화의 문자나 메신저에 붙여 넣어 보내세요."
    )

st.markdown("---")

# 쉬운 사용 안내
st.header("ℹ️ 사용 방법")
st.markdown(
    """
    1. 긴급하면 빨간색 전화 버튼을 누르세요.
    2. 평소 자주 연락하는 가족이나 보호자를 등록하세요.
    3. 도움이 필요하면 상황에 맞는 메시지를 골라 복사하세요.
    4. 전화나 메시지가 작동하지 않으면 기기의 기본 전화 앱을 사용하세요.
    """
)

with st.expander("🔒 개인정보 안내"):
    st.write(
        "이 앱은 등록한 연락처를 별도의 서버나 데이터베이스에 저장하지 않습니다. "
        "현재 실행 세션의 메모리에만 보관하며, 새 세션이 시작되거나 "
        "서버가 다시 시작되면 연락처가 사라질 수 있습니다. "
        "실제 전화 연결 및 문자 전송은 사용자의 기기와 통신 서비스에 따라 달라집니다."
    )

st.caption(
    "쉬운 긴급 연락망 · 한국 기준 · 긴급 번호는 지역별로 다를 수 있습니다."
)
