
import streamlit as st
import urllib.parse
import json
import re

st.set_page_config(
    page_title="한마디 도우미",
    page_icon="💬",
    layout="centered"
)

# -------------------------
# 화면 디자인
# -------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #e8f7ff,
        #d4efff,
        #f3fbff
    );
    color: #000000;
}

header[data-testid="stHeader"] {
    background: transparent;
}

h1, h2, h3, p, label, span, div {
    color: #000000;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 750px;
}

/* 입력창 */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #a9ddf5 !important;
    border-radius: 12px !important;
}

/* 버튼 */
.stButton button,
.stDownloadButton button {
    background-color: #b9e7ff !important;
    color: #000000 !important;
    border: 1px solid #a1d9f5 !important;
    border-radius: 12px !important;
    font-weight: 600;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background-color: #9edcff !important;
    border-color: #83ccef !important;
}

/* 안내 상자 */
div[data-testid="stAlert"] {
    background-color: #ffffff !important;
    border: 1px solid #b9e7ff !important;
    border-radius: 12px;
}

/* 구분선 */
hr {
    border-color: #b9e7ff !important;
}

/* 펼치기 메뉴 */
details {
    background-color: #ffffff;
    border: 1px solid #b9e7ff;
    border-radius: 12px;
    padding: 10px;
}

/* 파일 업로드 영역 */
div[data-testid="stFileUploader"] {
    background-color: #ffffff;
    border: 1px solid #b9e7ff;
    border-radius: 12px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)


# -------------------------
# 연락처 초기화
# -------------------------
if "contact_book" not in st.session_state:
    st.session_state["contact_book"] = {}

if not isinstance(st.session_state["contact_book"], dict):
    st.session_state["contact_book"] = {}

if "edited_sentence" not in st.session_state:
    st.session_state["edited_sentence"] = ""

if "generated_sentence" not in st.session_state:
    st.session_state["generated_sentence"] = ""


# -------------------------
# 제목
# -------------------------
st.title("💬 한마디 도우미")
st.write("필요한 말을 쉽고 간편하게 만들어 보세요!")

with st.expander("📌 사용 방법"):
    st.write("""
    1. 연락처를 등록합니다.
    2. 전달하고 싶은 상황을 선택합니다.
    3. 필요한 단어나 추가 내용을 입력합니다.
    4. 자동으로 만들어진 문장을 확인하고 수정합니다.
    5. 문자 앱을 열어 내용을 전송합니다.
    """)

st.divider()


# -------------------------
# 연락처 등록
# -------------------------
st.subheader("📱 연락처 관리")

with st.form("contact_form", clear_on_submit=True):
    contact_name = st.text_input("이름", placeholder="예: 딸")
    contact_phone = st.text_input(
        "전화번호",
        placeholder="예: 01012345678"
    )

    save_contact = st.form_submit_button(
        "연락처 저장",
        use_container_width=True
    )

    if save_contact:
        name = contact_name.strip()
        phone = re.sub(r"[\s()-]", "", contact_phone.strip())

        if not name or not phone:
            st.warning("이름과 전화번호를 모두 입력해 주세요.")
        elif not re.fullmatch(r"\+?\d{8,15}", phone):
            st.warning("전화번호를 올바르게 입력해 주세요.")
        elif name in st.session_state["contact_book"]:
            st.warning("이미 등록된 이름입니다.")
        else:
            st.session_state["contact_book"][name] = phone
            st.success(f"{name} 연락처가 저장되었습니다!")

# 연락처 목록
if st.session_state["contact_book"]:
    st.write("**저장된 연락처**")

    for name, phone in list(st.session_state["contact_book"].items()):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"👤 {name} : {phone}")

        with col2:
            if st.button("삭제", key=f"delete_{name}"):
                del st.session_state["contact_book"][name]
                st.rerun()
else:
    st.info("아직 저장된 연락처가 없습니다.")

st.divider()


# -------------------------
# 상황 선택
# -------------------------
st.subheader("✏️ 문장 만들기")

situation = st.selectbox(
    "어떤 상황인가요?",
    [
        "가족에게 연락하기",
        "병원 관련 연락",
        "일상적인 연락",
        "긴급한 연락"
    ]
)

templates = {
    "가족에게 연락하기": "안녕하세요. 지금 ",
    "병원 관련 연락": "안녕하세요. 병원 관련해서 ",
    "일상적인 연락": "안녕하세요. ",
    "긴급한 연락": "도움이 필요합니다. 지금 "
}

keyword = st.text_input(
    "전달하고 싶은 내용",
    placeholder="예: 집에 도착했어요"
)

extra = st.text_input(
    "추가로 덧붙일 말 (선택)",
    placeholder="예: 걱정하지 마세요"
)

if st.button("✨ 문장 만들기", use_container_width=True):
    sentence = templates[situation]

    if keyword.strip():
        sentence += keyword.strip()
    else:
        sentence += "연락드립니다."

    if extra.strip():
        sentence += " " + extra.strip()

    if not sentence.endswith((".", "!", "?")):
        sentence += "."

    st.session_state["generated_sentence"] = sentence
    st.session_state["edited_sentence"] = sentence

st.divider()


# -------------------------
# 문장 수정
# -------------------------
st.subheader("📝 완성된 문장")

if st.session_state["generated_sentence"]:
    st.text_area(
        "필요하다면 문장을 직접 수정할 수 있어요.",
        key="edited_sentence",
        height=150
    )

    st.caption("아래 버튼을 누르면 문자 앱으로 연결됩니다.")

    # 연락처 선택
    if st.session_state["contact_book"]:
        selected_name = st.selectbox(
            "문자를 보낼 사람",
            list(st.session_state["contact_book"].keys())
        )

        phone = st.session_state["contact_book"][selected_name]

        message = urllib.parse.quote(
            st.session_state["edited_sentence"]
        )

        sms_link = f"sms:{phone}?body={message}"

        st.markdown(
            f'<a href="{sms_link}" target="_blank" '
            f'style="display:block; text-align:center; '
            f'background-color:#b9e7ff; color:#000000; '
            f'padding:12px; border-radius:12px; '
            f'text-decoration:none; font-weight:bold;">'
            f'📨 문자 앱 열기</a>',
            unsafe_allow_html=True
        )
    else:
        st.info("문자를 보내려면 먼저 연락처를 등록해 주세요.")

    st.download_button(
        "📥 문장 파일로 저장하기",
        data=st.session_state["edited_sentence"],
        file_name="완성된_문장.txt",
        mime="text/plain",
        use_container_width=True
    )

    if st.button("🔄 새 문장 만들기", use_container_width=True):
        st.session_state["generated_sentence"] = ""
        st.session_state["edited_sentence"] = ""
        st.rerun()

else:
    st.info("위에서 내용을 입력하고 '문장 만들기'를 눌러 주세요.")


# -------------------------
# 연락처 백업 및 복원
# -------------------------
st.divider()
st.subheader("💾 연락처 백업 및 복원")

st.caption("저장한 연락처를 파일로 백업하거나 다시 불러올 수 있습니다.")

backup_data = json.dumps(
    st.session_state["contact_book"],
    ensure_ascii=False,
    indent=4
)

st.download_button(
    "📥 연락처 백업하기",
    data=backup_data,
    file_name="연락처_백업.json",
    mime="application/json",
    use_container_width=True
)

uploaded_file = st.file_uploader(
    "백업한 연락처 파일 불러오기",
    type=["json"]
)

if uploaded_file is not None:
    try:
        restored = json.load(uploaded_file)

        if not isinstance(restored, dict):
            st.error("올바른 연락처 백업 파일이 아닙니다.")
        else:
            valid_contacts = {}

            for name, phone in restored.items():
                if (
                    isinstance(name, str)
                    and isinstance(phone, str)
                    and name.strip()
                    and re.fullmatch(r"\+?\d{8,15}", phone)
                ):
                    valid_contacts[name.strip()] = phone

            if st.button("연락처 복원하기"):
                st.session_state["contact_book"].update(valid_contacts)
                st.success("연락처를 복원했습니다!")
                st.rerun()

    except Exception:
        st.error("파일을 읽을 수 없습니다. 백업 파일을 확인해 주세요.")


st.divider()
st.caption("한마디 도우미 | 쉽고 편리한 소통을 위한 앱")
