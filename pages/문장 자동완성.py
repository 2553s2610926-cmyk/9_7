
import streamlit as st

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="한마디 도우미",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# 화면 디자인
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F5F8FC;
    }
    html, body, [class*="css"] {
        font-family: sans-serif;
    }
    h1 {
        color: #174A7E;
        font-size: 2.2rem !important;
    }
    h2, h3 {
        color: #174A7E;
    }
    p, label, li {
        font-size: 1.15rem !important;
        line-height: 1.7 !important;
    }
    div.stButton > button,
    div.stDownloadButton > button {
        min-height: 52px;
        width: 100%;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 12px;
    }
    div[data-baseweb="select"] {
        font-size: 1.1rem;
    }
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        font-size: 1.15rem;
    }
    .info-card {
        background: white;
        border: 2px solid #D8E5F3;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 문장 제작 자료
# -----------------------------
SITUATIONS = {
    "👨‍👩‍👧 가족에게 연락": {
        "recipient": ["아들", "딸", "손주", "가족", "직접 입력"],
        "templates": {
            "안부": "{recipient}아, 잘 지내고 있니? 나는 잘 지내고 있어.",
            "전화": "{recipient}아, 시간이 될 때 나에게 전화해 줘.",
            "방문": "{recipient}아, 시간이 되면 우리 집에 한번 와 줘.",
            "감사": "{recipient}아, 항상 챙겨 줘서 고맙다.",
            "부탁": "{recipient}아, 부탁할 일이 있는데 연락해 줘.",
            "식사": "{recipient}아, 밥은 잘 먹고 다니니? 건강 잘 챙기렴.",
            "직접 만들기": "{recipient}에게 연락하고 싶어.",
        },
    },
    "🏥 병원 이용": {
        "recipient": ["의사 선생님", "간호사 선생님", "병원 직원", "직접 입력"],
        "templates": {
            "진료 예약": "{recipient}, 진료 예약을 하고 싶습니다.",
            "예약 변경": "{recipient}, 진료 예약 날짜를 변경하고 싶습니다.",
            "증상 설명": "{recipient}, 몸이 불편해서 진료를 받고 싶습니다.",
            "약 문의": "{recipient}, 약을 어떻게 먹어야 하는지 알려 주세요.",
            "길 안내": "{recipient}, 진료실이 어디에 있는지 알려 주세요.",
            "도움 요청": "{recipient}, 도움이 필요합니다. 도와주세요.",
            "직접 만들기": "{recipient}에게 문의하고 싶습니다.",
        },
    },
    "🛒 일상생활": {
        "recipient": ["가게 직원", "이웃", "지인", "직접 입력"],
        "templates": {
            "가격 문의": "{recipient}, 이 물건은 얼마인가요?",
            "길 묻기": "{recipient}, {keyword}에 어떻게 가나요?",
            "물건 찾기": "{recipient}, {keyword}를 찾고 있는데 도와주세요.",
            "약속": "{recipient}, {keyword}에서 만나요.",
            "감사": "{recipient}, 도와주셔서 감사합니다.",
            "부탁": "{recipient}, 잠시 도와주실 수 있나요?",
            "직접 만들기": "{recipient}에게 {keyword}에 대해 이야기하고 싶습니다.",
        },
    },
    "🚨 긴급 연락": {
        "recipient": ["가족", "주변 사람", "직접 입력"],
        "templates": {
            "도움 요청": "{recipient}, 지금 도움이 필요해요. 연락해 주세요.",
            "몸이 아픔": "{recipient}, 몸이 많이 아파요. 도와주세요.",
            "길을 잃음": "{recipient}, 길을 잃었어요. 제 위치를 확인하고 연락해 주세요.",
            "위험한 상황": "{recipient}, 지금 위험한 상황이에요. 도움을 요청해 주세요.",
            "직접 만들기": "{recipient}, 지금 도움이 필요합니다.",
        },
    },
}

# -----------------------------
# 제목과 사용 안내
# -----------------------------
st.title("💬 한마디 도우미")
st.markdown("### 하고 싶은 말을 쉽고 간단하게 만들어요!")
st.info(
    "사용 방법: ① 상황 선택 → ② 상대방과 단어 선택 "
    "→ ③ 문장 만들기 → ④ 완성된 문장 복사하기"
)

with st.expander("📖 처음 사용하시나요? 조작 방법 보기"):
    st.markdown(
        """
        1. **상황 선택**에서 가족, 병원, 일상, 긴급 연락 중 하나를 고릅니다.
        2. **누구에게 보낼까요?**에서 상대방을 선택합니다.
        3. **어떤 말을 하고 싶으세요?**에서 전달할 내용을 고릅니다.
        4. **문장 만들기**를 누르면 문장이 완성됩니다.
        5. 완성된 문장을 확인하고 필요하면 직접 고칩니다.
        6. 아래 문장 복사 안내를 따라 메시지에 붙여넣습니다.
        """
    )

st.divider()

# -----------------------------
# 입력 화면
# -----------------------------
st.header("1. 어떤 상황인가요?")

situation = st.selectbox(
    "상황을 선택하세요",
    list(SITUATIONS.keys()),
    key="situation",
)

data = SITUATIONS[situation]

st.header("2. 누구에게, 어떤 말을 할까요?")

recipient_option = st.selectbox(
    "누구에게 보낼까요?",
    data["recipient"],
    key="recipient_option",
)

recipient = recipient_option
if recipient_option == "직접 입력":
    recipient = st.text_input(
        "상대방을 입력하세요",
        placeholder="예: 관리사무소 직원",
        max_chars=40,
    ).strip()

st.markdown("**어떤 말을 하고 싶으세요?**")

message_type = st.selectbox(
    "전달할 내용 선택",
    list(data["templates"].keys()),
    key="message_type",
)

keyword = ""
if situation == "🛒 일상생활" or message_type == "직접 만들기":
    keyword = st.text_input(
        "추가할 단어 (선택)",
        placeholder="예: 시장, 내일, 전화",
        max_chars=80,
    ).strip()

extra = st.text_input(
    "더 넣고 싶은 말 (선택)",
    placeholder="예: 오후에, 조금 늦게",
    max_chars=100,
)

st.caption("입력하지 않아도 기본 문장을 만들 수 있어요.")

# -----------------------------
# 문장 생성
# -----------------------------
def make_sentence(situation, recipient, message_type, keyword, extra):
    """선택한 상황에 맞는 문장을 안전하게 생성합니다."""
    data = SITUATIONS.get(situation)
    if not data:
        raise ValueError("상황을 찾을 수 없습니다.")

    template = data["templates"].get(message_type)
    if not template:
        raise ValueError("문장 유형을 찾을 수 없습니다.")

    safe_recipient = recipient.strip() if recipient else ""
    if not safe_recipient:
        safe_recipient = "상대방"

    sentence = template.format(
        recipient=safe_recipient,
        keyword=keyword.strip() if keyword else "그곳",
    )

    if extra.strip():
        sentence = sentence.rstrip("。.!? ") + ". " + extra.strip()
        if sentence[-1] not in ".!?":
            sentence += "."

    return sentence


if "generated_sentence" not in st.session_state:
    st.session_state.generated_sentence = ""

if st.button("✨ 문장 만들기", type="primary", use_container_width=True):
    if recipient_option == "직접 입력" and not recipient:
        st.warning("상대방을 입력해 주세요.")
    else:
        try:
            st.session_state.generated_sentence = make_sentence(
                situation, recipient, message_type, keyword, extra
            )
            st.rerun()
        except (ValueError, KeyError, AttributeError):
            st.error("문장을 만드는 중 문제가 발생했어요. 다시 선택해 주세요.")
        except Exception:
            st.error("일시적인 오류가 발생했어요. 다시 시도해 주세요.")

# -----------------------------
# 완성된 문장
# -----------------------------
st.divider()
st.header("3. 완성된 문장")

if st.session_state.generated_sentence:
    st.success("문장이 완성되었어요! 아래 내용을 확인하세요.")

    edited_sentence = st.text_area(
        "필요하면 문장을 직접 수정하세요.",
        value=st.session_state.generated_sentence,
        height=150,
        key="edited_sentence",
        help="글자를 누르고 수정할 수 있어요.",
    )

    st.markdown("**📋 복사할 문장**")
    st.code(edited_sentence, language=None)

    st.caption(
        "복사 방법: 위 문장 상자의 오른쪽 위에 있는 복사 아이콘을 누르세요. "
        "그다음 카카오톡 등의 입력창을 길게 누르고 '붙여넣기'를 선택하세요."
    )

    st.download_button(
        label="📄 문장을 파일로 저장하기",
        data=edited_sentence,
        file_name="완성된_문장.txt",
        mime="text/plain",
        use_container_width=True,
    )

    if st.button("🔄 처음부터 다시 만들기", use_container_width=True):
        st.session_state.generated_sentence = ""
        st.rerun()
else:
    st.markdown(
        """
        <div class="info-card">
        <p>아직 완성된 문장이 없어요.</p>
        <p>위에서 상황과 전달할 내용을 선택한 다음
        <b>문장 만들기</b> 버튼을 눌러 주세요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

st.markdown(
    """
    <div class="info-card">
    <h3>💙 기억해 주세요</h3>
    <p>급하게 도움이 필요한 경우에는 이 앱만 사용하지 말고
    주변 사람이나 119 등 적절한 긴급 도움을 요청하세요.</p>
    <p>이 앱은 사용자가 선택한 내용으로 문장을 만드는 도구입니다.
    실제 메시지는 직접 확인한 뒤 전송하세요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("한마디 도우미 | 누구나 쉽게 소통할 수 있도록")
