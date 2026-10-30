
import streamlit as st
import re
import json
import html
from urllib.parse import quote

st.set_page_config(
    page_title="한마디 도우미",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# 디자인
# -----------------------------
st.markdown("""
<style>
.stApp { background-color: #F4F8FC; }
h1, h2, h3 { color: #174A7E; }
p, label, li { font-size: 1.1rem; line-height: 1.6; }
div.stButton > button, div.stDownloadButton > button {
    min-height: 50px;
    width: 100%;
    font-size: 1.05rem;
    font-weight: bold;
    border-radius: 12px;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    font-size: 1.1rem;
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
# 세션 데이터 초기화
# -----------------------------
if "contacts" not in st.session_state:
    st.session_state.contacts = {}

if "generated_sentence" not in st.session_state:
    st.session_state.generated_sentence = ""

if "edited_sentence" not in st.session_state:
    st.session_state.edited_sentence = ""

# -----------------------------
# 제목 및 사용법
# -----------------------------
st.title("💬 한마디 도우미")
st.subheader("하고 싶은 말을 쉽게 만들고 전해요!")

with st.expander("📖 간단한 조작법 보기", expanded=False):
    st.markdown("""
    1. 연락처에서 이름과 전화번호를 저장합니다.
    2. 문자 받을 사람을 선택합니다.
    3. 상황과 전달할 내용을 선택합니다.
    4. 문장을 만들고 원하는 대로 수정합니다.
    5. 문자 앱 열기를 눌러 내용을 확인하고 전송합니다.
    """)

st.info(
    "연락처는 현재 앱을 사용하는 동안 임시로 저장됩니다. "
    "앱을 새로 열거나 세션이 끝나면 사라질 수 있습니다."
)

# -----------------------------
# 연락처 관리
# -----------------------------
st.header("1. 연락처 저장하기")

with st.form("add_contact_form", clear_on_submit=True):
    new_name = st.text_input(
        "이름",
        placeholder="예: 우리 아들",
        max_chars=40,
    )
    new_phone = st.text_input(
        "전화번호",
        placeholder="예: 010-1234-5678",
        max_chars=20,
    )
    add_contact = st.form_submit_button(
        "➕ 연락처 저장",
        use_container_width=True,
    )

if add_contact:
    name = new_name.strip()
    phone = new_phone.strip()
    normalized_phone = re.sub(r"[\s()-]", "", phone)

    if not name:
        st.warning("이름을 입력해 주세요.")
    elif not re.fullmatch(r"\+?\d{8,15}", normalized_phone):
        st.warning("전화번호를 확인해 주세요. 숫자와 국가번호를 입력할 수 있어요.")
    elif name in st.session_state.contacts:
        st.warning("같은 이름의 연락처가 이미 있어요. 다른 이름을 사용해 주세요.")
    else:
        st.session_state.contacts[name] = normalized_phone
        st.success(f"{name} 연락처를 저장했어요!")
        st.rerun()

# 연락처 파일 백업 및 복원
with st.expander("📁 연락처 백업 및 복원"):
    st.caption(
        "연락처를 파일로 백업해 두면 나중에 다시 불러올 수 있어요. "
        "전화번호가 포함되므로 파일을 안전하게 보관하세요."
    )

    if st.session_state.contacts:
        backup_json = json.dumps(
            st.session_state.contacts,
            ensure_ascii=False,
            indent=2,
        )
        st.download_button(
            "📥 연락처 백업 파일 저장",
            data=backup_json,
            file_name="연락처_백업.json",
            mime="application/json",
            use_container_width=True,
        )

    uploaded_contacts = st.file_uploader(
        "기존 연락처 백업 파일 불러오기",
        type=["json"],
        key="contacts_upload",
    )

    if uploaded_contacts is not None:
        if st.button("백업 연락처 불러오기", use_container_width=True):
            try:
                loaded = json.load(uploaded_contacts)
                if not isinstance(loaded, dict) or len(loaded) > 200:
                    raise ValueError("파일 형식이 올바르지 않습니다.")

                valid_contacts = {}
                for person, number in loaded.items():
                    cleaned_number = re.sub(
                        r"[\s()-]", "", str(number)
                    )
                    if (
                        isinstance(person, str)
                        and person.strip()
                        and len(person) <= 40
                        and re.fullmatch(r"\+?\d{8,15}", cleaned_number)
                    ):
                        valid_contacts[person.strip()] = cleaned_number

                if not valid_contacts:
                    raise ValueError("유효한 연락처가 없습니다.")

                st.session_state.contacts.update(valid_contacts)
                st.success("연락처를 불러왔어요!")
                st.rerun()
            except (ValueError, json.JSONDecodeError, OSError):
                st.error("백업 파일을 읽을 수 없어요. 올바른 JSON 파일인지 확인해 주세요.")
            except Exception:
                st.error("파일을 처리하지 못했어요. 다시 시도해 주세요.")

if st.session_state.contacts:
    st.markdown("**저장된 연락처**")
    for contact_name, contact_phone in list(st.session_state.contacts.items()):
        col1, col2 = st.columns([3, 1])
        col1.write(f"👤 **{contact_name}**")
        col1.caption(contact_phone)

        if col2.button("삭제", key=f"delete_{contact_name}"):
            del st.session_state.contacts[contact_name]
            st.rerun()
else:
    st.caption("저장된 연락처가 없어요. 위에서 먼저 연락처를 등록해 주세요.")

st.divider()

# -----------------------------
# 받는 사람 선택
# -----------------------------
st.header("2. 문자 받을 사람 선택")

if not st.session_state.contacts:
    st.warning("문자를 보내려면 먼저 연락처를 저장해 주세요.")
    st.stop()

contact_names = list(st.session_state.contacts.keys())
selected_name = st.selectbox(
    "누구에게 문자를 보낼까요?",
    contact_names,
)

selected_phone = st.session_state.contacts[selected_name]
st.success(f"선택한 사람: {selected_name}")
st.caption(f"전화번호: {selected_phone}")

# -----------------------------
# 문장 입력
# -----------------------------
st.header("3. 문장 만들기")

situation = st.selectbox(
    "어떤 상황인가요?",
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

if st.button("✨ 문장 만들기", type="primary", use_container_width=True):
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
    except (KeyError, ValueError, AttributeError):
        st.error("문장을 만드는 중 문제가 생겼어요. 다시 선택해 주세요.")
    except Exception:
        st.error("일시적인 오류가 발생했어요. 다시 시도해 주세요.")

# -----------------------------
# 수정 및 문자 보내기
# -----------------------------
st.divider()
st.header("4. 문장 확인하고 문자 보내기")

if st.session_state.generated_sentence:
    st.success("문장이 완성되었어요. 보내기 전에 확인해 주세요.")

    # 새로 생성된 문장을 편집할 수 있는 입력창
    st.text_area(
        "완성된 문장 (직접 수정 가능)",
        key="edited_sentence",
        height=180,
        max_chars=2000,
        help="문장 안을 눌러 글자를 추가하거나 삭제할 수 있어요.",
    )

    final_message = st.session_state.edited_sentence.strip()

    if final_message:
        st.markdown("**문자 앱으로 보낼 내용 미리보기**")
        st.code(final_message, language=None)

        encoded_message = quote(final_message, safe="")
        safe_phone = html.escape(selected_phone, quote=True)

        # 문자 앱 호환 방식은 기기마다 다를 수 있어 두 링크 제공
        android_sms_uri = (
            f"sms:{safe_phone}?body={encoded_message}"
        )
        ios_sms_uri = (
            f"sms:{safe_phone}&body={encoded_message}"
        )

        st.markdown(
            f'<a href="{android_sms_uri}" '
            'style="display:block;text-align:center;'
            'background:#1769AA;color:white;padding:16px;'
            'border-radius:12px;font-size:20px;font-weight:bold;'
            'text-decoration:none;margin:8px 0;" '
            'target="_self">📩 문자 앱 열기 (일반 방식)</a>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<a href="{ios_sms_uri}" '
            'style="display:block;text-align:center;'
            'background:#287A58;color:white;padding:16px;'
            'border-radius:12px;font-size:20px;font-weight:bold;'
            'text-decoration:none;margin:8px 0;" '
            'target="_self">📱 문자 앱 열기 (아이폰 방식)</a>',
            unsafe_allow_html=True,
        )

        st.caption(
            "문자 앱이 열리지 않거나 내용이 자동 입력되지 않으면 "
            "아래 문장을 복사해 문자 앱에 붙여넣으세요."
        )

        st.code(final_message, language=None)

        st.download_button(
            "📄 완성된 문장 저장하기",
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
        st.warning("문장을 입력해 주세요.")
else:
    st.info("위에서 문장을 만든 후 여기에서 수정하고 보낼 수 있어요.")

st.divider()
st.markdown("""
### 💙 꼭 기억해 주세요
- 문자는 자동으로 전송되지 않아요. 문자 앱에서 내용을 확인하고 직접 보내세요.
- 문자 앱 연결은 휴대전화와 브라우저에 따라 작동 방식이 다를 수 있어요.
- 긴급한 상황에서는 문자 앱만 기다리지 말고 주변 사람이나 119에 도움을 요청하세요.
""")
st.caption("한마디 도우미 | 누구나 쉽게 소통할 수 있도록")
