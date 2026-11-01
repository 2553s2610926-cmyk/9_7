
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
# 전체 화면 디자인
# -------------------------
st.markdown("""
<style>

/* 전체 화면 */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #F1FAFF !important;
    color: #000000 !important;
}

/* 왼쪽 사이드바 */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background: #DDF2FF !important;
    color: #000000 !important;
}

/* 사이드바 내부 */
[data-testid="stSidebar"] * {
    color: #000000 !important;
}

/* 페이지 메뉴 */
[data-testid="stSidebarNav"] {
    background: #DDF2FF !important;
}

[data-testid="stSidebarNav"] a {
    background: #EFF9FF !important;
    color: #000000 !important;
    border-radius: 12px !important;
    margin: 5px 0 !important;
    padding: 12px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
}

[data-testid="stSidebarNav"] a:hover {
    background: #BDE8FF !important;
}

/* 기본 글자 */
html, body, p, label, span, li, small,
h1, h2, h3, h4, strong, div {
    color: #000000 !important;
}

/* 글자 크기 */
p, label, li {
    font-size: 17px !important;
}

h1 {
    font-size: 34px !important;
    font-weight: 800 !important;
}

h2 {
    font-size: 27px !important;
    font-weight: 700 !important;
}

h3 {
    font-size: 22px !important;
    font-weight: 700 !important;
}

/* 본문 영역 */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 800px;
}

/* 입력창 */
.stTextInput input,
.stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 2px solid #A9DDF5 !important;
    border-radius: 12px !important;
    font-size: 17px !important;
    box-shadow: none !important;
}

/* 입력창 안내 문구 */
input::placeholder,
textarea::placeholder {
    color: #777777 !important;
    opacity: 1 !important;
}

/* 선택창 */
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 2px solid #A9DDF5 !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    box-shadow: none !important;
}

/* 선택창 글자 */
[data-baseweb="select"] *,
[data-baseweb="select"] svg {
    color: #000000 !important;
    fill: #000000 !important;
    font-size: 17px !important;
}

/* 선택 목록 */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="popover"] ul,
[data-baseweb="menu"] ul {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B9E5FA !important;
    box-shadow: none !important;
}

/* 선택 목록 항목 */
[role="option"] {
    background: #FFFFFF !important;
    color: #000000 !important;
    font-size: 17px !important;
    padding: 12px !important;
}

[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background: #DDF2FF !important;
    color: #000000 !important;
}

/* 버튼 */
.stButton button,
.stDownloadButton button,
button[kind] {
    background: #BDE8FF !important;
    background-image: none !important;
    color: #000000 !important;
    border: 2px solid #A5DCF7 !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}

/* 버튼 내부 */
.stButton button *,
.stDownloadButton button * {
    color: #000000 !important;
    fill: #000000 !important;
    font-size: 17px !important;
}

/* 버튼 마우스 올림 */
.stButton button:hover,
.stDownloadButton button:hover {
    background: #A9DFFF !important;
    color: #000000 !important;
    border-color: #8ED0F2 !important;
    box-shadow: none !important;
}

/* 버튼 포커스 */
.stButton button:focus,
.stDownloadButton button:focus {
    background: #A9DFFF !important;
    color: #000000 !important;
    outline: 2px solid #A9DFFF !important;
    box-shadow: none !important;
}

/* 안내창 */
[data-testid="stAlert"] {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B9E5FA !important;
    border-radius: 12px !important;
}

/* 펼치기 메뉴 */
[data-testid="stExpander"],
details {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B9E5FA !important;
    border-radius: 12px !important;
}

/* 파일 업로드 */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] section {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B9E5FA !important;
    border-radius: 12px !important;
}

/* 구분선 */
hr {
    border-color: #B9E5FA !important;
}

/* 표 */
[data-testid="stTable"],
[data-testid="stDataFrame"] {
    background: #FFFFFF !important;
    color: #000000 !important;
}

/* 체크박스와 라디오 */
[data-testid="stCheckbox"],
[data-testid="stRadio"] {
    color: #000000 !important;
    font-size: 17px !important;
}

/* 링크 */
a {
    color: #000000 !important;
}

/* 하단 여백 */
footer {
    background: transparent !important;
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# 세션 데이터 초기화
# -------------------------
if "contact_book" not in st.session_state:
    st.session_state["contact_book"] = {}

if not isinstance(st.session_state["contact_book"], dict):
    st.session_state["contact_book"] = {}

if "generated_sentence" not in st.session_state:
    st.session_state["generated_sentence"] = ""

if "edited_sentence" not in st.session_state:
    st.session_state["edited_sentence"] = ""


# 새 문장 버튼을 위한 초기화 함수
def reset_sentence():
    st.session_state["generated_sentence"] = ""
    st.session_state["edited_sentence"] = ""


# -------------------------
# 제목
# -------------------------
st.title("💬 한마디 도우미")
st.write("필요한 말을 쉽고 간편하게 만들어 보세요!")

with st.expander("📌 사용 방법"):
    st.write("""
    1. 연락처를 등록합니다.
    2. 문자를 보낼 사람을 선택합니다.
    3. 전달하고 싶은 상황을 선택합니다.
    4. 필요한 내용을 입력하고 문장을 만듭니다.
    5. 완성된 문장을 확인하고 문자 앱으로 연결합니다.
    """)

st.divider()


# -------------------------
# 연락처 관리
# -------------------------
st.header("📱 연락처 관리")

with st.form("contact_form", clear_on_submit=True):
    contact_name = st.text_input(
        "이름",
        placeholder="예: 딸"
    )

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
    st.subheader("저장된 연락처")

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
# 문자 받을 사람 선택
# -------------------------
st.header("👤 문자 받을 사람")

selected_name = None
selected_phone = None

if st.session_state["contact_book"]:

    selected_name = st.selectbox(
        "누구에게 문자를 보낼까요?",
        options=list(st.session_state["contact_book"].keys()),
        key="recipient_select"
    )

    selected_phone = st.session_state["contact_book"][selected_name]

else:
    st.info("문자를 보내려면 먼저 연락처를 등록해 주세요.")

st.divider()


# -------------------------
# 문장 만들기
# -------------------------
st.header("✏️ 문장 만들기")

situation = st.selectbox(
    "어떤 상황인가요?",
    [
        "가족에게 연락하기",
        "병원 관련 연락",
        "일상적인 연락",
        "긴급한 연락"
    ],
    key="situation_select"
)

templates = {
    "가족에게 연락하기": "안녕하세요. 지금 ",
    "병원 관련 연락": "안녕하세요. 병원 관련해서 ",
    "일상적인 연락": "안녕하세요. ",
    "긴급한 연락": "도움이 필요합니다. 지금 "
}

keyword = st.text_input(
    "전달하고 싶은 내용",
    placeholder="예: 집에 도착했어요",
    key="keyword_input"
)

extra = st.text_input(
    "추가로 덧붙일 말 (선택)",
    placeholder="예: 걱정하지 마세요",
    key="extra_input"
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
# 완성된 문장
# -------------------------
st.header("📝 완성된 문장")

if st.session_state["generated_sentence"]:

    st.text_area(
        "필요하다면 문장을 직접 수정할 수 있어요.",
        key="edited_sentence",
        height=160
    )

    st.caption("문장을 확인한 뒤 아래 버튼을 눌러 주세요.")

    # 문자 앱 연결
    if selected_phone:

        message = urllib.parse.quote(
            st.session_state["edited_sentence"]
        )

        sms_link = f"sms:{selected_phone}?body={message}"

        st.markdown(
            f'''
            <a href="{sms_link}" target="_blank"
            style="
                display:block;
                text-align:center;
                background-color:#BDE8FF;
                color:#000000;
                padding:15px;
                border:2px solid #A5DCF7;
                border-radius:12px;
                text-decoration:none;
                font-size:18px;
                font-weight:bold;
            ">
            📨 {selected_name}에게 문자 보내기
            </a>
            ''',
            unsafe_allow_html=True
        )

    else:
        st.info("문자를 보내려면 연락처를 먼저 등록해 주세요.")

    st.download_button(
        "📥 문장 파일로 저장하기",
        data=st.session_state["edited_sentence"],
        file_name="완성된_문장.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.button(
        "🔄 새 문장 만들기",
        use_container_width=True,
        on_click=reset_sentence
    )

else:
    st.info("내용을 입력하고 '문장 만들기'를 눌러 주세요.")


# -------------------------
# 연락처 백업 및 복원
# -------------------------
st.divider()
st.header("💾 연락처 백업 및 복원")

st.write("저장한 연락처를 파일로 보관하거나 다시 불러올 수 있습니다.")

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
