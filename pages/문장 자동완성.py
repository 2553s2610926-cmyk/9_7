
import streamlit as st
import re
from urllib.parse import quote

# =====================================
# 기본 설정
# =====================================
st.set_page_config(
    page_title="한마디 도우미",
    page_icon="💙",
    layout="centered"
)

# =====================================
# 디자인
# =====================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #D8F0FF, #F3FAFF, #FFFFFF);
}
.block-container {
    max-width: 650px;
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #285D86 !important;
}
.hero {
    background: #D5EDFF;
    padding: 28px 15px;
    border-radius: 25px;
    text-align: center;
    margin-bottom: 20px;
}
.hero h1 {
    font-size: 32px;
}
.hero p {
    color: #507895;
}
div.stButton > button,
div.stDownloadButton > button {
    width: 100%;
    min-height: 50px;
    border-radius: 14px;
    background-color: #DDF1FF;
    color: #285D86;
    border: 1px solid #B9DDF4;
    font-size: 17px;
    font-weight: bold;
}
div.stButton > button:hover {
    background-color: #C5E7FC;
    color: #174B73;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: 12px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# 데이터 초기화
# =====================================
if "contacts" not in st.session_state:
    st.session_state["contacts"] = {}

if "generated_sentence" not in st.session_state:
    st.session_state["generated_sentence"] = ""

if "edited_sentence" not in st.session_state:
    st.session_state["edited_sentence"] = ""

# =====================================
# 문장 자료
# =====================================
SITUATIONS = {
    "👨‍👩‍👧 가족": {
        "안부": "{recipient}아, 잘 지내고 있니? 나는 잘 지내고 있어.",
        "전화 부탁": "{recipient}아, 시간이 될 때 나에게 전화해 줘.",
        "방문 부탁": "{recipient}아, 시간이 되면 우리 집에 한번 와 줘.",
        "감사": "{recipient}아, 항상 챙겨 줘서 고맙다.",
        "식사": "{recipient}아, 밥은 잘 먹고 다니니? 건강 잘 챙기렴.",
        "직접 작성": "{recipient}에게 연락하고 싶어."
    },
    "🏥 병원": {
        "진료 예약": "{recipient}, 진료 예약을 하고 싶습니다.",
        "예약 변경": "{recipient}, 진료 예약 날짜를 변경하고 싶습니다.",
        "약 문의": "{recipient}, 약을 어떻게 먹어야 하는지 알려 주세요.",
        "도움 요청": "{recipient}, 도움이 필요합니다. 도와주세요.",
        "직접 작성": "{recipient}에게 문의하고 싶습니다."
    },
    "🛒 일상": {
        "가격 문의": "{recipient}, 이 물건은 얼마인가요?",
        "길 묻기": "{recipient}, {keyword}에 어떻게 가나요?",
        "물건 찾기": "{recipient}, {keyword}를 찾고 있는데 도와주세요.",
        "약속": "{recipient}, {keyword}에서 만나요.",
        "감사": "{recipient}, 도와주셔서 감사합니다.",
        "부탁": "{recipient}, 잠시 도와주실 수 있나요?",
        "직접 작성": "{recipient}에게 {keyword}에 대해 이야기하고 싶습니다."
    },
    "🚨 긴급 연락": {
        "도움 요청": "{recipient}, 지금 도움이 필요해요. 연락해 주세요.",
        "몸이 아픔": "{recipient}, 몸이 많이 아파요. 도와주세요.",
        "길을 잃음": "{recipient}, 길을 잃었어요. 연락해 주세요.",
        "위험한 상황": "{recipient}, 지금 위험한 상황이에요. 도움을 요청해 주세요.",
        "직접 작성": "{recipient}, 지금 도움이 필요합니다."
    }
}

# =====================================
# 제목
# =====================================
st.markdown("""
<div class="hero">
    <div style="font-size:40px;">💙</div>
    <h1>한마디 도우미</h1>
    <p>소중한 사람에게 마음을 쉽게 전해 보세요.</p>
</div>
""", unsafe_allow_html=True)

with st.expander("📖 사용 방법"):
    st.write("""
    1. 연락처와 전화번호를 저장합니다.
    2. 문자 받을 사람을 선택합니다.
    3. 상황과 전달할 내용을 선택합니다.
    4. 완성된 문장을 수정합니다.
    5. 문자 앱을 열어 직접 전송합니다.
    """)

# =====================================
# 1. 연락처 저장
# =====================================
st.header("👤 나의 연락처")
st.write("자주 연락하는 사람을 등록해 보세요.")

with st.form("save_contact_form"):
    input_name = st.text_input(
        "이름",
        placeholder="예: 우리 아들"
    )

    input_phone = st.text_input(
        "전화번호",
        placeholder="예: 010-1234-5678"
    )

    save_button = st.form_submit_button(
        "＋ 연락처 저장",
        use_container_width=True
    )

if save_button:
    name = input_name.strip()
    phone = input_phone.strip()

    # 숫자와 +만 남겨 전화번호 검사
    cleaned_phone = re.sub(r"[\s()-]", "", phone)

    if not name:
        st.error("이름을 입력해 주세요.")

    elif not re.fullmatch(r"\+?\d{8,15}", cleaned_phone):
        st.error("전화번호를 확인해 주세요. 예: 010-1234-5678")

    elif name in st.session_state["contacts"]:
        st.warning("이미 저장된 이름이에요.")

    else:
        try:
            st.session_state["contacts"][name] = cleaned_phone
            st.success(name + " 연락처가 저장되었어요!")
            st.rerun()

        except Exception as e:
            st.error("저장 중 문제가 발생했어요: " + str(e))

# =====================================
# 2. 저장된 연락처 목록
# =====================================
st.subheader("📋 저장된 연락처")

contacts = st.session_state["contacts"]

if contacts:
    for person, number in list(contacts.items()):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write("💙 " + person)
            st.caption(number)

        with col2:
            if st.button("삭제", key="delete_" + person):
                del st.session_state["contacts"][person]
                st.rerun()
else:
    st.info("아직 저장된 연락처가 없어요.")

st.divider()

# 연락처가 없으면 이후 단계 진행 중단
if not st.session_state["contacts"]:
    st.info("연락처를 먼저 저장해 주세요.")
    st.stop()

# =====================================
# 3. 문자 받을 사람 선택
# =====================================
st.header("💌 문자 받을 사람")

contact_names = list(st.session_state["contacts"].keys())

selected_name = st.selectbox(
    "누구에게 보낼까요?",
    contact_names
)

selected_phone = st.session_state["contacts"][selected_name]

st.success("선택한 사람: " + selected_name)
st.caption("전화번호: " + selected_phone)

st.divider()

# =====================================
# 4. 문장 만들기
# =====================================
st.header("✏️ 전하고 싶은 말")

situation = st.selectbox(
    "상황 선택",
    list(SITUATIONS.keys())
)

message_type = st.selectbox(
    "전달할 내용",
    list(SITUATIONS[situation].keys())
)

keyword = st.text_input(
    "추가할 단어 (선택)",
    placeholder="예: 시장, 내일, 오후 3시"
)

extra = st.text_input(
    "더 넣고 싶은 말 (선택)",
    placeholder="예: 조금 늦을 것 같아요"
)

if st.button("✨ 문장 만들기", type="primary",
             use_container_width=True):

    try:
        template = SITUATIONS[situation][message_type]

        sentence = template.format(
            recipient=selected_name,
            keyword=keyword.strip() or "그곳"
        )

        if extra.strip():
            sentence = sentence.rstrip(" .!?") + ". " + extra.strip()
            if sentence[-1] not in ".!?":
                sentence += "."

        st.session_state["generated_sentence"] = sentence
        st.session_state["edited_sentence"] = sentence

        st.rerun()

    except Exception as e:
        st.error("문장 생성 오류: " + str(e))

st.divider()

# =====================================
# 5. 완성된 문장 수정
# =====================================
st.header("📝 완성된 문장")

if st.session_state["generated_sentence"]:

    st.success("문장이 완성되었어요!")

    # 직접 수정 가능한 문장 입력창
    edited = st.text_area(
        "원하는 대로 수정해 보세요.",
        key="edited_sentence",
        height=160,
        max_chars=2000
    )

    final_message = edited.strip()

    # =================================
    # 6. 문자 앱 연결
    # =================================
    st.subheader("📩 문자 보내기")

    if final_message:

        st.write("최종 전송 내용")
        st.code(final_message, language=None)

        encoded_message = quote(final_message, safe="")
        encoded_phone = quote(selected_phone, safe="")

        android_link = (
            f"sms:{encoded_phone}?body={encoded_message}"
        )

        iphone_link = (
            f"sms:{encoded_phone}&body={encoded_message}"
        )

        st.markdown(
            f"""
            <a href="{android_link}" target="_self"
            style="
            display:block;
            text-align:center;
            background:#79C7F2;
            color:#174B73;
            padding:16px;
            border-radius:15px;
            font-size:18px;
            font-weight:bold;
            text-decoration:none;
            margin:10px 0;">
            📩 문자 앱 열기
            </a>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <a href="{iphone_link}" target="_self"
            style="
            display:block;
            text-align:center;
            background:#D8F0FF;
            color:#174B73;
            padding:16px;
            border-radius:15px;
            font-size:18px;
            font-weight:bold;
            text-decoration:none;
            margin:10px 0;">
            📱 아이폰 문자 앱 열기
            </a>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "문자 앱에서 받는 사람과 내용을 확인한 뒤 직접 보내세요. "
            "기기와 브라우저에 따라 자동 입력이 지원되지 않을 수 있어요."
        )

        st.download_button(
            "📄 문장 파일 저장",
            data=final_message,
            file_name="완성된_문장.txt",
            mime="text/plain",
            use_container_width=True
        )

    else:
        st.warning("문장을 입력해 주세요.")

    if st.button("🔄 새 문장 만들기",
                 use_container_width=True):
        st.session_state["generated_sentence"] = ""
        st.session_state["edited_sentence"] = ""
        st.rerun()

else:
    st.info("위에서 문장 만들기를 눌러 주세요.")

# =====================================
# 마지막 안내
# =====================================
st.divider()

st.markdown("""
<div class="hero">
    <div style="font-size:30px;">☁️ 💙 ☁️</div>
    <b style="color:#285D86;font-size:18px;">
        누구나 쉽게 소통할 수 있도록
    </b>
    <p>한마디 도우미</p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "연락처는 현재 세션 동안만 저장됩니다. "
    "긴급 상황에서는 119 등 적절한 도움을 요청하세요."
)
