
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
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #F1FAFF !important;
    color: #000000 !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background: #DDF2FF !important;
    color: #000000 !important;
}

[data-testid="stSidebar"] * {
    color: #000000 !important;
}

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

html, body, p, label, span, li, small,
h1, h2, h3, h4, strong {
    color: #000000 !important;
}

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

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 800px;
}

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

input::placeholder,
textarea::placeholder {
    color: #777777 !important;
    opacity: 1 !important;
}

[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 2px solid #A9DDF5 !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    box-shadow: none !important;
}

[data-baseweb="select"] *,
[data-baseweb="select"] svg {
    color: #000000 !important;
    fill: #000000 !important;
    font-size: 17px !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="popover"] ul,
[data-baseweb="menu"] ul {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B9E5FA !important;
    box-shadow: none !important;
}

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

.stButton button *,
.stDownloadButton button * {
    color: #000000 !important;
    fill: #000000 !important;
    font-size: 17px !important;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background: #A9DFFF !important;
    color: #000000 !important;
    border-color: #8ED0F2 !important;
    box-shadow: none !important;
}

[data-testid="stAlert"] {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B9E5FA !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"],
details {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B9E5FA !important;
    border-radius: 12px !important;
}

[data-testid="stFileUploader"],
[data-testid="stFileUploader"] section {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B9E5FA !important;
    border-radius: 12px !important;
}

hr {
    border-color: #B9E5FA !important;
}

a {
    color: #000000 !important;
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

if "selected_keyword" not in st.session_state:
    st.session_state["selected_keyword"] = ""


def reset_sentence():
    st.session_state["generated_sentence"] = ""
    st.session_state["edited_sentence"] = ""
    st.session_state["selected_keyword"] = ""


def choose_keyword(keyword):
    st.session_state["selected_keyword"] = keyword


# -------------------------
# 문장 자동완성 데이터
# -------------------------
sentence_rules = {
    "가족에게 연락하기": [
        (["늦", "지각", "늦어"],
         "생각보다 늦어질 것 같아요. 조금만 기다려 주세요."),
        (["도착", "왔어요", "도착했"],
         "목적지에 잘 도착했어요. 걱정하지 마세요."),
        (["병원", "진료"],
         "병원에 도착했어요. 진료가 끝나면 다시 연락할게요."),
        (["식사", "밥", "먹"],
         "식사는 잘했어요. 걱정하지 않으셔도 돼요."),
        (["전화", "통화"],
         "지금은 통화하기 어려워요. 나중에 다시 전화할게요."),
        (["고마워", "감사"],
         "항상 신경 써 줘서 고마워요. 덕분에 큰 힘이 돼요."),
        (["사랑", "보고 싶"],
         "늘 고맙고 보고 싶어요. 조만간 만나요."),
        (["걱정"],
         "걱정하지 마세요. 저는 잘 지내고 있어요.")
    ],

    "병원 관련 연락": [
        (["예약", "진료 예약"],
         "진료 예약을 하고 싶습니다. 가능한 시간을 알려 주세요."),
        (["늦", "지각"],
         "예정된 시간보다 조금 늦을 것 같습니다. 양해 부탁드립니다."),
        (["아파", "통증", "아픈"],
         "현재 몸이 아프고 불편한 증상이 있습니다. 진료 상담을 받고 싶습니다."),
        (["약", "처방"],
         "처방받은 약에 대해 문의하고 싶습니다. 확인 부탁드립니다."),
        (["검사", "결과"],
         "검사 결과를 확인하고 싶습니다. 확인 방법을 안내해 주세요."),
        (["취소", "변경"],
         "예정된 진료 일정을 변경하거나 취소하고 싶습니다."),
        (["도착", "왔어요"],
         "병원에 도착했습니다. 어디로 가면 되는지 안내 부탁드립니다."),
        (["문의", "질문"],
         "진료와 관련하여 문의할 내용이 있습니다. 연락 부탁드립니다.")
    ],

    "일상적인 연락": [
        (["고마워", "감사"],
         "도와주셔서 정말 감사합니다. 덕분에 잘 해결했어요."),
        (["미안", "죄송"],
         "미리 말씀드리지 못해 죄송합니다. 양해 부탁드립니다."),
        (["약속", "만나"],
         "약속 시간과 장소를 다시 한번 확인하고 싶습니다."),
        (["늦", "지각"],
         "예정보다 조금 늦을 것 같습니다. 도착하면 연락드리겠습니다."),
        (["전화", "통화"],
         "지금은 통화하기 어렵습니다. 나중에 다시 연락드리겠습니다."),
        (["부탁", "도와"],
         "부탁드릴 일이 있습니다. 시간 괜찮으실 때 연락 부탁드립니다."),
        (["안부", "잘 지내"],
         "잘 지내고 계신가요? 안부가 궁금해서 연락드렸습니다."),
        (["확인", "알려"],
         "내용을 확인하고 싶습니다. 확인 후 답변 부탁드립니다.")
    ],

    "긴급한 연락": [
        (["도움", "도와줘", "도와주세요"],
         "지금 도움이 필요합니다. 가능한 한 빨리 연락해 주세요."),
        (["길", "길을 잃", "위치"],
         "현재 위치를 찾기 어렵습니다. 연락해 주시고 도움을 부탁드립니다."),
        (["아파", "다쳤", "몸이 안"],
         "몸이 좋지 않아 도움이 필요합니다. 가능한 한 빨리 연락해 주세요."),
        (["위험", "무서"],
         "현재 안전에 대한 걱정이 있습니다. 연락하여 도움을 부탁드립니다."),
        (["연락", "전화"],
         "급하게 전할 말이 있습니다. 확인하는 대로 연락 부탁드립니다."),
        (["병원", "응급"],
         "병원에 도움이 필요한 상황입니다. 가능한 한 빨리 연락해 주세요.")
    ]
}


# -------------------------
# 상황별 버튼 목록
# -------------------------
keyword_buttons = {
    "가족에게 연락하기": [
        "늦어요",
        "도착했어요",
        "병원",
        "식사",
        "전화",
        "고마워요",
        "보고 싶어요",
        "걱정하지 마세요"
    ],

    "병원 관련 연락": [
        "예약",
        "진료",
        "아파요",
        "약 문의",
        "검사 결과",
        "일정 변경",
        "도착했어요",
        "문의"
    ],

    "일상적인 연락": [
        "감사해요",
        "죄송해요",
        "약속",
        "늦어요",
        "전화",
        "부탁",
        "안부",
        "확인"
    ],

    "긴급한 연락": [
        "도움이 필요해요",
        "길을 잃었어요",
        "몸이 아파요",
        "위험해요",
        "급한 연락",
        "병원"
    ]
}


default_sentences = {
    "가족에게 연락하기":
        "안녕하세요. 잘 지내고 있어요. 시간 될 때 다시 연락할게요.",

    "병원 관련 연락":
        "안녕하세요. 병원 진료와 관련하여 문의드리고 싶습니다.",

    "일상적인 연락":
        "안녕하세요. 전할 말이 있어 연락드렸습니다.",

    "긴급한 연락":
        "지금 도움이 필요한 상황입니다. 확인하시면 연락 부탁드립니다."
}


# -------------------------
# 문장 생성 함수
# -------------------------
def make_sentence(situation, keyword, extra):
    keyword = keyword.strip()
    extra = extra.strip()

    if keyword:
        for words, sentence in sentence_rules[situation]:
            if any(word in keyword for word in words):
                result = sentence

                if extra:
                    result += " " + extra

                return result

    if keyword:
        if situation == "가족에게 연락하기":
            result = f"안녕하세요. {keyword}."

        elif situation == "병원 관련 연락":
            result = f"안녕하세요. {keyword}에 대해 문의드리고 싶습니다."

        elif situation == "일상적인 연락":
            result = f"안녕하세요. {keyword}."

        else:
            result = f"현재 {keyword}. 도움이 필요합니다."

    else:
        result = default_sentences[situation]

    if extra:
        result += " " + extra

    if not result.endswith((".", "!", "?")):
        result += "."

    return result


# -------------------------
# 제목
# -------------------------
st.title("💬 한마디 도우미")
st.write("필요한 말을 쉽고 간편하게 만들어 보세요!")

with st.expander("📌 사용 방법"):
    st.write("""
    1. 연락처를 등록합니다.
    2. 문자를 보낼 사람을 선택합니다.
    3. 상황을 선택합니다.
    4. 상황에 맞는 단어 버튼을 누릅니다.
    5. 문장을 만들고 필요하면 수정합니다.
    6. 문자 앱을 열어 직접 전송합니다.
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

st.write("**전달하고 싶은 내용을 선택해 주세요.**")

# 상황에 따라 다른 버튼 표시
buttons = keyword_buttons[situation]

for i in range(0, len(buttons), 2):
    col1, col2 = st.columns(2)

    with col1:
        word = buttons[i]

        st.button(
            word,
            key=f"keyword_{situation}_{i}",
            use_container_width=True,
            type="primary" if st.session_state["selected_keyword"] == word else "secondary",
            on_click=choose_keyword,
            args=(word,)
        )

    if i + 1 < len(buttons):
        with col2:
            word2 = buttons[i + 1]

            st.button(
                word2,
                key=f"keyword_{situation}_{i+1}",
                use_container_width=True,
                type="primary" if st.session_state["selected_keyword"] == word2 else "secondary",
                on_click=choose_keyword,
                args=(word2,)
            )

# 선택한 단어 표시
if st.session_state["selected_keyword"] in buttons:
    st.success(
        f"선택한 내용: {st.session_state['selected_keyword']}"
    )
else:
    st.info("위 버튼 중 하나를 선택해 주세요.")

# 추가 내용 입력
extra = st.text_input(
    "추가로 덧붙일 말 (선택)",
    placeholder="예: 오후 시간으로 부탁드려요",
    key="extra_input"
)

# 문장 생성
if st.button("✨ 문장 만들기", use_container_width=True):

    selected_keyword = st.session_state["selected_keyword"]

    sentence = make_sentence(
        situation,
        selected_keyword,
        extra
    )

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
    st.info("단어 버튼을 선택하고 '문장 만들기'를 눌러 주세요.")


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
