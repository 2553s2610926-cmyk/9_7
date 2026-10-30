
import streamlit as st
import re
import json
from urllib.parse import quote

# ==================================
# 기본 설정
# ==================================
st.set_page_config(
    page_title="한마디 도우미",
    page_icon="💙",
    layout="centered"
)

# ==================================
# 디자인
# ==================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#D8F0FF,#F3FAFF,#FFFFFF);
}
.block-container {
    max-width: 650px;
    padding-top: 2rem;
}
h1,h2,h3 {
    color: #285D86 !important;
}
.hero {
    background: #D5EDFF;
    padding: 25px 15px;
    border-radius: 25px;
    text-align: center;
}
div.stButton > button,
div.stDownloadButton > button {
    width: 100%;
    min-height: 50px;
    border-radius: 14px;
    background: #DDF1FF;
    color: #285D86;
    border: 1px solid #B9DDF4;
    font-size: 16px;
    font-weight: bold;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: 12px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ==================================
# 데이터 초기화
# 기존 contacts와 다른 이름 사용
# ==================================
if "contact_book" not in st.session_state:
    st.session_state["contact_book"] = {}

if not isinstance(st.session_state["contact_book"], dict):
    st.session_state["contact_book"] = {}

if "generated_sentence" not in st.session_state:
    st.session_state["generated_sentence"] = ""

if "edited_sentence" not in st.session_state:
    st.session_state["edited_sentence"] = ""

# ==================================
# 문장 자료
# ==================================
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

# ==================================
# 첫 화면
# ==================================
st.markdown("""
<div class="hero">
    <div style="font-size:40px;">💙</div>
    <div style="font-size:32px;font-weight:bold;color:#285D86;">
        한마디 도우미
    </div>
    <p style="color:#507895;">
        소중한 사람에게 마음을 쉽게 전해 보세요.
    </p>
</div>
""", unsafe_allow_html=True)

with st.expander("📖 간단한 사용 방법"):
    st.write("""
    1. 이름과 전화번호를 저장해요.
    2. 문자 받을 사람을 선택해요.
    3. 상황과 전달할 내용을 선택해요.
    4. 완성된 문장을 원하는 대로 수정해요.
    5. 문자 앱을 열어 직접 보내요.
    """)

st.divider()

# ==================================
# 1. 연락처 등록
# ==================================
st.header("👤 나의 연락처")
st.write("자주 연락하는 사람을 등록해 보세요.")

with st.form("contact_form", clear_on_submit=True):
    name = st.text_input(
        "이름",
        placeholder="예: 우리 아들"
    )

    phone = st.text_input(
        "전화번호",
        placeholder="예: 010-1234-5678"
    )

    save = st.form_submit_button(
        "＋ 연락처 저장",
        use_container_width=True
    )

if save:
    name = name.strip()
    phone = re.sub(r"[\s()-]", "", phone.strip())

    if not name:
        st.error("이름을 입력해 주세요.")

    elif not re.fullmatch(r"\+?\d{8,15}", phone):
        st.error("전화번호를 확인해 주세요. 예: 010-1234-5678")

    elif name in st.session_state["contact_book"]:
        st.warning("이미 저장된 이름이에요.")

    else:
        st.session_state["contact_book"][name] = phone
        st.success(f"{name} 연락처가 저장되었어요!")
        st.rerun()

# ==================================
# 2. 연락처 목록 및 삭제
# ==================================
st.subheader("📋 저장된 연락처")

contacts = st.session_state["contact_book"]

if contacts:
    for person, number in list(contacts.items()):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write("💙 " + person)
            st.caption(number)

        with col2:
            if st.button("삭제", key="del_" + person):
                del st.session_state["contact_book"][person]
                st.rerun()
else:
    st.info("저장된 연락처가 없어요.")

# ==================================
# 3. 연락처 백업 및 복원
# ==================================
with st.expander("📁 연락처 백업 및 복원"):
    if contacts:
        backup = json.dumps(
            contacts,
            ensure_ascii=False,
            indent=2
        )

        st.download_button(
            "📥 연락처 백업하기",
            data=backup,
            file_name="연락처_백업.json",
            mime="application/json",
            use_container_width=True
        )

    uploaded = st.file_uploader(
        "백업 파일 불러오기",
        type=["json"]
    )

    if uploaded is not None:
        if st.button("연락처 복원하기"):
            try:
                data = json.load(uploaded)

                if not isinstance(data, dict) or len(data) > 200:
                    raise ValueError()

                valid = {}

                for person, number in data.items():
                    cleaned = re.sub(
                        r"[\s()-]",
                        "",
                        str(number)
                    )

                    if (
                        isinstance(person, str)
                        and person.strip()
                        and len(person) <= 40
                        and re.fullmatch(r"\+?\d{8,15}", cleaned)
                    ):
                        valid[person.strip()] = cleaned

                if not valid:
                    raise ValueError()

                st.session_state["contact_book"].update(valid)
                st.success("연락처를 불러왔어요!")
                st.rerun()

            except Exception:
                st.error("백업 파일을 확인해 주세요.")

st.divider()

# ==================================
# 연락처가 없으면 여기서 중단
# ==================================
if not st.session_state["contact_book"]:
    st.info("먼저 연락처를 저장해 주세요.")
    st.stop()

# ==================================
# 4. 받을 사람 선택
# ==================================
st.header("💌 문자 받을 사람")

selected_name = st.selectbox(
    "누구에게 보낼까요?",
    list(st.session_state["contact_book"].keys())
)

selected_phone = st.session_state["contact_book"][selected_name]

st.success("선택한 사람: " + selected_name)
st.caption("전화번호: " + selected_phone)

st.divider()

# ==================================
# 5. 문장 만들기
# ==================================
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
    placeholder="예: 시장, 내일, 오후 3시",
    max_chars=100
)

extra = st.text_input(
    "더 넣고 싶은 말 (선택)",
    placeholder="예: 조금 늦을 것 같아요",
    max_chars=100
)

if st.button(
    "✨ 문장 만들기",
    type="primary",
    use_container_width=True
):
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

    except Exception:
        st.error("문장을 만드는 중 오류가 발생했어요.")

st.divider()

# ==================================
# 6. 문장 수정 및 문자 보내기
# ==================================
st.header("📝 완성된 문장")

if st.session_state["generated_sentence"]:

    st.success("문장이 완성되었어요!")

    st.text_area(
        "문장을 자유롭게 수정해 보세요.",
        key="edited_sentence",
        height=150,
        max_chars=2000
    )

    final_message = st.session_state["edited_sentence"].strip()

    if final_message:
        st.subheader("📩 문자 보내기")

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
            display:block;text-align:center;
            background:#79C7F2;color:#174B73;
            padding:16px;border-radius:15px;
            font-size:18px;font-weight:bold;
            text-decoration:none;margin:10px 0;">
            📩 문자 앱 열기
            </a>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <a href="{iphone_link}" target="_self"
            style="
            display:block;text-align:center;
            background:#D8F0FF;color:#174B73;
            padding:16px;border-radius:15px;
            font-size:18px;font-weight:bold;
            text-decoration:none;margin:10px 0;">
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

    if st.button("🔄 새 문장 만들기", use_container_width=True):
        st.session_state["generated_sentence"] = ""
        st.rerun()

else:
    st.info("위에서 문장 만들기를 눌러 주세요.")

# ==================================
# 마지막 안내
# ==================================
st.divider()

st.markdown("""
<div class="hero">
    <div style="font-size:30px;">☁️ 💙 ☁️</div>
    <b style="color:#285D86;font-size:18px;">
        누구나 쉽게 소통할 수 있도록
    </b>
    <p style="color:#507895;">한마디 도우미</p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "연락처는 현재 세션 동안만 저장됩니다. "
    "긴급 상황에서는 119 등 적절한 도움을 요청하세요."
)
