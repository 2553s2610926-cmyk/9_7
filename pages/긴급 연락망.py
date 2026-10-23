import json
import re
import html
import streamlit as st
from datetime import datetime

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="안심연결 | 긴급 도움",
    page_icon="🆘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# 화면 디자인: 큰 글씨, 높은 명암 대비, 넓은 버튼
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F7F9FC;
        color: #172033;
    }
    .block-container {
        max-width: 850px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3, p, label, li {
        color: #172033;
    }
    h1 { font-size: 2.1rem !important; }
    h2 { font-size: 1.65rem !important; }
    h3 { font-size: 1.3rem !important; }
    p, label, li, .stMarkdown {
        font-size: 1.08rem;
        line-height: 1.65;
    }
    .stButton > button,
    .stDownloadButton > button {
        min-height: 52px;
        width: 100%;
        font-size: 1.05rem;
        font-weight: 700;
        border-radius: 12px;
        border: 2px solid #CBD5E1;
    }
    .emergency-card {
        padding: 20px;
        border-radius: 16px;
        margin: 8px 0;
        text-align: center;
        background: #FFFFFF;
        border: 2px solid #D6DCE5;
    }
    .emergency-card h2 {
        margin: 0 0 8px 0;
    }
    .emergency-card p {
        margin: 8px 0;
    }
    .call-link {
        display: block;
        padding: 15px 12px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.25rem;
        font-weight: 800;
        text-decoration: none !important;
        margin-top: 12px;
        border: 2px solid rgba(0,0,0,0.15);
    }
    .police {
        background: #B91C1C;
        color: #FFFFFF !important;
    }
    .ambulance {
        background: #075985;
        color: #FFFFFF !important;
    }
    .contact-card {
        background: #FFFFFF;
        border: 2px solid #D6DCE5;
        border-radius: 14px;
        padding: 16px;
        margin: 8px 0;
    }
    .notice {
        padding: 14px;
        border-radius: 12px;
        background: #FFF7D6;
        border: 2px solid #E5C45B;
        color: #422D00;
    }
    a:focus, button:focus, input:focus {
        outline: 3px solid #2563EB !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 세션 데이터 초기화
# --------------------------------------------------
if "contacts" not in st.session_state:
    st.session_state.contacts = []

if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": "",
        "address": "",
        "memo": "",
    }

if "saved_notice" not in st.session_state:
    st.session_state.saved_notice = ""


# --------------------------------------------------
# 보조 함수
# --------------------------------------------------
def clean_phone(phone):
    """전화번호에 허용된 문자만 있는지 검사하고 전화 연결용 번호를 만듭니다."""
    phone = phone.strip()

    if not phone:
        return None

    if not re.fullmatch(r"[0-9+()\- ]+", phone):
        return None

    digits = re.sub(r"\D", "", phone)

    if len(digits) < 2 or len(digits) > 15:
        return None

    # tel 링크에는 숫자와 맨 앞의 +만 사용합니다.
    if phone.count("+") > 1 or ("+" in phone and not phone.startswith("+")):
        return None

    return ("+" if phone.startswith("+") else "") + digits


def phone_button(number, label, css_class):
    """휴대전화에서 누를 수 있는 전화 링크를 표시합니다."""
    safe_number = html.escape(number, quote=True)
    safe_label = html.escape(label)

    st.markdown(
        f"""
        <a class="call-link {css_class}"
           href="tel:{safe_number}"
           aria-label="{safe_label}">
           {safe_label}
        </a>
        """,
        unsafe_allow_html=True,
    )


def show_notice(message, kind="info"):
    if kind == "error":
        st.error(message)
    elif kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.info(message)


# --------------------------------------------------
# 앱 제목
# --------------------------------------------------
st.title("🆘 안심연결")
st.subheader("위급할 때, 어렵게 생각하지 말고 여기부터 누르세요.")
st.write(
    "이 앱은 도움이 필요할 때 긴급전화와 가족·보호자 연락처를 "
    "쉽게 찾도록 도와줍니다."
)

st.markdown(
    """
    <div class="notice">
    <strong>지금 위험한 상황인가요?</strong><br>
    생명이 위험하거나 범죄가 진행 중이면 아래의 112 또는 119를 누르세요.
    전화 연결은 사용하는 기기와 브라우저에 따라 달라질 수 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 최우선 영역: 긴급 전화
# --------------------------------------------------
st.header("1. 긴급 도움 받기")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="emergency-card">
            <h2>🚔 경찰</h2>
            <p>범죄, 폭력, 위협을 당했을 때</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    phone_button("112", "📞 112 경찰에 전화", "police")

with col2:
    st.markdown(
        """
        <div class="emergency-card">
            <h2>🚑 소방·구급</h2>
            <p>다쳤거나 아프거나 화재가 났을 때</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    phone_button("119", "📞 119 구급·소방에 전화", "ambulance")

st.caption(
    "※ 위 버튼은 전화 앱을 열도록 요청하는 링크입니다. "
    "이 화면에서 실제 통화가 자동으로 시작되거나 연결을 보장하지는 않습니다."
)

with st.expander("전화가 어렵다면 이렇게 해보세요"):
    st.markdown(
        """
        1. 주변에 사람이 있다면 **“도와주세요. 112 또는 119에 전화해 주세요.”**라고 말하세요.
        2. 가능한 경우 현재 있는 장소와 무슨 일이 있었는지 알려주세요.
        3. 위험한 사람에게 다가가거나 위험한 장소로 돌아가지 마세요.
        4. 전화 연결이 되지 않으면 주변 사람에게 직접 도움을 요청하세요.
        """
    )

# --------------------------------------------------
# 상황별 도움말
# --------------------------------------------------
st.header("2. 어떤 도움이 필요하신가요?")

situations = [
    (
        "🤕 몸이 아프거나 다쳤어요",
        [
            "생명이 위험하거나 심하게 다쳤다면 119에 전화하세요.",
            "현재 있는 장소와 증상을 가능한 만큼 알려주세요.",
            "혼자 이동하기 어렵다면 주변 사람에게 도움을 요청하세요.",
        ],
    ),
    (
        "🚶 길을 잃었어요",
        [
            "안전한 가게나 안내소처럼 사람이 있는 곳으로 이동하세요.",
            "가족이나 보호자에게 현재 위치를 알려주세요.",
            "위험하거나 실종 등 긴급한 상황이면 112에 도움을 요청하세요.",
        ],
    ),
    (
        "📱 돈을 보내라고 해요",
        [
            "모르는 사람이 급하게 돈을 보내라고 하면 일단 멈추세요.",
            "비밀번호, 인증번호, 계좌 정보를 알려주지 마세요.",
            "가족에게 직접 전화해 사실인지 확인하세요.",
            "사기 피해가 진행 중이거나 범죄가 의심되면 112에 신고하세요.",
        ],
    ),
    (
        "😟 무섭거나 위협받고 있어요",
        [
            "가능하면 안전하고 사람이 있는 곳으로 이동하세요.",
            "위협이 진행 중이거나 위험하면 112에 전화하세요.",
            "믿을 수 있는 가족이나 보호자에게 도움을 요청하세요.",
        ],
    ),
    (
        "📲 휴대전화 사용이 어려워요",
        [
            "이 화면의 큰 전화 버튼을 눌러 보세요.",
            "화면을 누르기 어렵다면 가까운 사람에게 대신 눌러 달라고 요청하세요.",
            "평소에 보호자와 함께 긴급전화 사용법을 연습해 두세요.",
        ],
    ),
]

for title, steps in situations:
    with st.expander(title):
        for step in steps:
            st.markdown(f"- {step}")

# --------------------------------------------------
# 연락처 등록
# --------------------------------------------------
st.header("3. 나를 도와줄 사람 등록하기")
st.write(
    "가족, 보호자, 친구 또는 믿을 수 있는 이웃을 등록하세요. "
    "전화번호는 본인이 신뢰하는 사람의 번호만 입력하세요."
)

with st.form("add_contact_form", clear_on_submit=True):
    contact_name = st.text_input(
        "이름 또는 부르는 호칭",
        placeholder="예: 딸, 아들, 보호자",
        max_chars=50,
    )
    relationship = st.text_input(
        "관계 (선택)",
        placeholder="예: 가족, 이웃, 활동지원사",
        max_chars=50,
    )
    contact_phone = st.text_input(
        "전화번호",
        placeholder="예: 010-1234-5678",
        max_chars=25,
    )

    submitted = st.form_submit_button(
        "➕ 연락처 추가",
        use_container_width=True,
    )

if submitted:
    safe_name = contact_name.strip()
    safe_relationship = relationship.strip()
    valid_phone = clean_phone(contact_phone)

    if not safe_name:
        show_notice("이름 또는 부르는 호칭을 입력해 주세요.", "error")
    elif not valid_phone:
        show_notice(
            "전화번호를 확인해 주세요. 숫자와 +, -, 괄호만 사용할 수 있습니다.",
            "error",
        )
    elif len(st.session_state.contacts) >= 20:
        show_notice(
            "연락처는 최대 20명까지 등록할 수 있습니다.",
            "warning",
        )
    else:
        st.session_state.contacts.append(
            {
                "name": safe_name,
                "relationship": safe_relationship,
                "phone": valid_phone,
            }
        )
        st.session_state.saved_notice = f"{safe_name} 연락처를 추가했습니다."
        st.rerun()

if st.session_state.saved_notice:
    show_notice(st.session_state.saved_notice, "success")
    st.session_state.saved_notice = ""

# --------------------------------------------------
# 연락처 보기 및 삭제
# --------------------------------------------------
st.subheader("내 긴급 연락망")

if not st.session_state.contacts:
    st.info(
        "아직 등록한 연락처가 없습니다. 위에서 가족이나 보호자의 "
        "전화번호를 추가해 주세요."
    )
else:
    for index, contact in enumerate(st.session_state.contacts):
        with st.container(border=True):
            st.markdown(f"### 👤 {contact['name']}")

            if contact["relationship"]:
                st.write(f"관계: {contact['relationship']}")

            st.write(f"전화번호: {contact['phone']}")
            phone_button(
                contact["phone"],
                f"📞 {contact['name']}에게 전화",
                "ambulance",
            )

            if st.button(
                f"🗑️ {contact['name']} 연락처 삭제",
                key=f"delete_contact_{index}",
                use_container_width=True,
            ):
                st.session_state.contacts.pop(index)
                st.rerun()

# --------------------------------------------------
# 사용자 정보
# --------------------------------------------------
st.header("4. 내 정보와 도움 요청 문구")
st.write(
    "아래 정보는 필요한 경우 가족이나 구조대원에게 알려줄 수 있습니다. "
    "민감한 개인정보는 꼭 필요한 만큼만 입력하세요."
)

with st.form("user_info_form"):
    new_name = st.text_input(
        "내 이름 또는 부르는 호칭",
        value=st.session_state.user_info["name"],
        max_chars=50,
    )
    new_address = st.text_area(
        "자주 머무는 장소 또는 주소 (선택)",
        value=st.session_state.user_info["address"],
        max_chars=300,
        placeholder="예: 서울시 ○○구 ○○로 ...",
    )
    new_memo = st.text_area(
        "도움을 받을 때 알려줄 내용 (선택)",
        value=st.session_state.user_info["memo"],
        max_chars=500,
        placeholder="예: 현관 비밀번호는 말하지 않기, 보호자에게 연락하기",
    )

    info_submitted = st.form_submit_button(
        "내 정보 저장",
        use_container_width=True,
    )

if info_submitted:
    st.session_state.user_info = {
        "name": new_name.strip(),
        "address": new_address.strip(),
        "memo": new_memo.strip(),
    }
    show_notice("내 정보를 현재 세션에 저장했습니다.", "success")

if any(st.session_state.user_info.values()):
    with st.container(border=True):
        st.subheader("내가 알려줄 정보")

        if st.session_state.user_info["name"]:
            st.write(f"**이름:** {st.session_state.user_info['name']}")

        if st.session_state.user_info["address"]:
            st.write(f"**장소 또는 주소:** {st.session_state.user_info['address']}")

        if st.session_state.user_info["memo"]:
            st.write(f"**도움 요청 메모:** {st.session_state.user_info['memo']}")

        st.caption(
            "주소와 메모는 화면을 보는 다른 사람에게 노출될 수 있습니다."
        )

# --------------------------------------------------
# 도움 요청 문구
# --------------------------------------------------
st.subheader("말하기 어려울 때 보여줄 문장")

help_message = (
    "도움이 필요합니다. 제가 디지털기기 사용에 어려움이 있습니다. "
    "현재 상황을 확인하고 가족 또는 긴급기관에 연락하는 것을 도와주세요."
)

st.text_area(
    "아래 문장을 주변 사람에게 보여주세요.",
    value=help_message,
    height=110,
    disabled=True,
)

if st.button("📋 도움 요청 문구 복사용으로 보기", use_container_width=True):
    st.code(help_message, language=None)
    st.info("위 문장을 길게 눌러 복사하거나 화면을 다른 사람에게 보여주세요.")

# --------------------------------------------------
# 연락망 백업
# --------------------------------------------------
st.header("5. 연락망 백업하기")

backup_data = {
    "app": "안심연결",
    "backup_date": datetime.now().astimezone().isoformat(timespec="seconds"),
    "contacts": st.session_state.contacts,
    "user_info": st.session_state.user_info,
}

backup_json = json.dumps(
    backup_data,
    ensure_ascii=False,
    indent=2,
)

st.download_button(
    label="⬇️ 연락망 백업 파일 다운로드",
    data=backup_json.encode("utf-8"),
    file_name="ansimyeongyeol_backup.json",
    mime="application/json",
    use_container_width=True,
)

st.warning(
    "중요: 연락처와 내 정보는 현재 세션에만 보관됩니다. "
    "앱을 다시 시작하거나 세션이 종료되면 사라질 수 있습니다. "
    "백업 파일에는 전화번호와 주소 등 개인정보가 포함될 수 있으므로 "
    "안전한 장소에 보관하고 다른 사람과 공유하지 마세요."
)

# --------------------------------------------------
# 하단 안내
# --------------------------------------------------
st.divider()
st.caption("안심연결 | 디지털기기 사용이 어려운 사람을 위한 쉬운 긴급 연락망")
st.caption(
    "이 앱은 긴급기관을 대신하지 않습니다. "
    "위급할 때는 112 또는 119에 직접 연락하거나 주변 사람에게 도움을 요청하세요."
)
