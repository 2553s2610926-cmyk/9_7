
import streamlit as st
import re

st.set_page_config(
    page_title="마음 한마디",
    page_icon="💌",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# 기본 스타일
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFF9F0;
    }
    .block-container {
        max-width: 850px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3, p, label, div, span {
        line-height: 1.65;
    }
    h1 {
        color: #493522;
        font-size: 2.25rem !important;
    }
    h2, h3 {
        color: #493522;
    }
    .intro {
        background: #FFFFFF;
        border: 2px solid #E8D9C5;
        border-radius: 18px;
        padding: 18px;
        font-size: 1.15rem;
        color: #493522;
        margin-bottom: 16px;
    }
    div.stButton > button {
        min-height: 58px;
        width: 100%;
        border-radius: 14px;
        border: 2px solid #D8C5AA;
        background-color: #FFFFFF;
        color: #493522;
        font-size: 1.08rem;
        font-weight: 600;
        white-space: normal;
    }
    div.stButton > button:hover {
        border-color: #8A5A35;
        color: #493522;
        background-color: #FFF0D9;
    }
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        font-size: 1.15rem;
        border-radius: 12px;
    }
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 자주 사용하는 문장 데이터
# -----------------------------
SENTENCES = [
    {
        "category": "👨‍👩‍👧 가족",
        "keywords": ["딸", "아들", "가족", "손주", "보고싶", "보고 싶", "그리워"],
        "text": "잘 지내고 있니? 보고 싶구나. 시간 될 때 전화해 줘.",
    },
    {
        "category": "👨‍👩‍👧 가족",
        "keywords": ["사랑", "고마워", "감사", "가족"],
        "text": "항상 고맙고 사랑한다. 건강하게 잘 지내자.",
    },
    {
        "category": "📞 전화",
        "keywords": ["전화", "통화", "연락", "전화해"],
        "text": "시간 괜찮을 때 전화 한 통 해 주면 좋겠어.",
    },
    {
        "category": "🏥 병원",
        "keywords": ["병원", "진료", "의사", "아파", "아픔"],
        "text": "오늘 병원에 다녀오려고 해. 끝나면 다시 연락할게.",
    },
    {
        "category": "🏥 병원",
        "keywords": ["약", "처방", "약국"],
        "text": "약을 먹어야 하는데 복용 방법을 다시 알려 줄 수 있니?",
    },
    {
        "category": "🛒 부탁",
        "keywords": ["장보기", "마트", "시장", "물건", "부탁", "사다"],
        "text": "미안하지만 필요한 물건을 사다 줄 수 있을까?",
    },
    {
        "category": "🚶 외출",
        "keywords": ["외출", "나가", "늦", "귀가", "어디"],
        "text": "지금 외출 중이야. 조금 늦을 수 있으니 걱정하지 마.",
    },
    {
        "category": "🍚 식사",
        "keywords": ["밥", "식사", "먹", "점심", "저녁"],
        "text": "밥은 먹었니? 끼니 잘 챙겨 먹고 건강하렴.",
    },
    {
        "category": "🙏 감사",
        "keywords": ["고마워", "감사", "도움", "덕분"],
        "text": "도와줘서 정말 고마워. 덕분에 큰 도움이 되었어.",
    },
    {
        "category": "💗 안부",
        "keywords": ["안녕", "안부", "잘 지내", "건강"],
        "text": "잘 지내고 있니? 날씨가 변덕스러우니 건강 조심하렴.",
    },
    {
        "category": "🙇 사과",
        "keywords": ["미안", "죄송", "사과", "잘못"],
        "text": "내가 말을 잘못했다면 미안해. 너를 생각하는 마음은 같아.",
    },
    {
        "category": "🆘 도움",
        "keywords": ["도움", "급해", "위급", "위험"],
        "text": "지금 도움이 필요해. 가능하면 빨리 연락해 줘.",
    },
    {
        "category": "🌙 인사",
        "keywords": ["잘 자", "굿나잇", "밤", "잠"],
        "text": "오늘도 수고 많았어. 편안한 밤 보내고 푹 쉬렴.",
    },
    {
        "category": "☀️ 인사",
        "keywords": ["아침", "좋은 하루", "인사"],
        "text": "좋은 아침이야. 오늘도 건강하고 행복한 하루 보내렴.",
    },
]

QUICK_KEYWORDS = [
    "딸에게",
    "전화",
    "병원",
    "고마워",
    "밥",
    "도움이 필요해",
]

# -----------------------------
# 세션 상태
# -----------------------------
if "selected_message" not in st.session_state:
    st.session_state.selected_message = ""

if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "keyword" not in st.session_state:
    st.session_state.keyword = ""

# -----------------------------
# 추천 함수
# -----------------------------
def find_sentences(keyword, category):
    """키워드와 상황을 바탕으로 추천 문장을 찾습니다."""
    results = []
    normalized = keyword.strip().lower()

    for item in SENTENCES:
        if category != "전체" and item["category"] != category:
            continue

        if not normalized:
            results.append(item)
            continue

        searchable = " ".join(
            [item["text"], item["category"]] + item["keywords"]
        ).lower()

        # 입력한 단어 또는 입력 단어의 일부가 포함된 문장을 추천합니다.
        terms = [word for word in re.split(r"\s+", normalized) if word]
        if any(term in searchable for term in terms):
            results.append(item)

    return results


def select_message(message):
    st.session_state.selected_message = message


# -----------------------------
# 화면
# -----------------------------
st.title("💌 마음 한마디")
st.markdown(
    """
    <div class="intro">
    <b>하고 싶은 말을 쉽게 전해 보세요.</b><br>
    단어를 입력하거나 아래 버튼을 눌러 보세요.
    마음에 드는 문장을 누르면 완성됩니다.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("1. 어떤 말을 하고 싶으세요?")

for start in range(0, len(QUICK_KEYWORDS), 3):
    cols = st.columns(3)
    for offset, col in enumerate(cols):
        index = start + offset
        if index < len(QUICK_KEYWORDS):
            word = QUICK_KEYWORDS[index]
            with col:
                if st.button(word, key=f"quick_{index}"):
                    st.session_state.keyword = word
                    st.session_state.selected_message = ""

keyword = st.text_input(
    "떠오르는 단어를 입력하세요",
    key="keyword",
    placeholder="예: 딸, 병원, 전화, 고마워",
    help="짧은 단어 하나만 입력해도 괜찮습니다.",
)

categories = ["전체"] + list(dict.fromkeys(
    item["category"] for item in SENTENCES
))

category = st.selectbox(
    "상황 선택 (선택 사항)",
    categories,
    index=0,
)

st.subheader("2. 마음에 드는 문장을 눌러 보세요")

try:
    results = find_sentences(keyword, category)

    if not results:
        st.info(
            "딱 맞는 문장을 찾지 못했어요. "
            "상황을 바꾸거나 아래 기본 문장을 골라 보세요."
        )
        results = [
            {
                "category": "💗 안부",
                "keywords": [],
                "text": "잘 지내고 있니? 시간 될 때 연락해 줘.",
            },
            {
                "category": "🙏 부탁",
                "keywords": [],
                "text": "미안하지만 잠시 도와줄 수 있을까?",
            },
        ]

    # 지나치게 많은 선택지를 보여 주지 않습니다.
    results = results[:12]

    for i in range(0, len(results), 2):
        cols = st.columns(2)
        for offset, col in enumerate(cols):
            idx = i + offset
            if idx >= len(results):
                continue

            item = results[idx]
            with col:
                st.caption(item["category"])
                if st.button(
                    item["text"],
                    key=f"sentence_{idx}",
                    use_container_width=True,
                ):
                    select_message(item["text"])

except Exception:
    st.error("문장을 불러오는 중 문제가 생겼어요. 다시 시도해 주세요.")

st.divider()
st.subheader("3. 보낼 문장을 확인하세요")

edited_message = st.text_area(
    "완성된 문장 (필요하면 수정하세요)",
    key="message_editor",
    value=st.session_state.selected_message,
    height=130,
    placeholder="위에서 문장을 선택하면 여기에 나타납니다.",
)

# text_area의 key는 세션 상태와 연결되므로 현재 편집 내용을 사용합니다.
current_message = st.session_state.get("message_editor", "")

left, right = st.columns(2)

with left:
    if st.button("⭐ 즐겨찾기에 저장", use_container_width=True):
        if current_message.strip():
            if current_message not in st.session_state.favorites:
                st.session_state.favorites.append(current_message)
            st.success("즐겨찾기에 저장했어요.")
        else:
            st.warning("먼저 문장을 선택하거나 입력해 주세요.")

with right:
    if st.button("🗑️ 문장 비우기", use_container_width=True):
        st.session_state.selected_message = ""
        st.session_state.message_editor = ""
        st.rerun()

if current_message.strip():
    st.markdown("### 📋 완성된 문장")
    st.code(current_message, language=None)
    st.caption(
        "문장 상자의 복사 아이콘을 누르면 문장을 복사할 수 있어요."
    )
    st.markdown(
        """
        **문자나 카카오톡으로 보내는 방법**
        1. 위 문장을 복사하세요.
        2. 문자 또는 카카오톡을 여세요.
        3. 상대방의 대화창에 붙여넣고 전송하세요.
        """
    )
else:
    st.info("문장을 선택하면 여기에 보낼 내용이 나타납니다.")

if st.session_state.favorites:
    st.divider()
    st.subheader("⭐ 내가 좋아하는 문장")

    for i, favorite in enumerate(st.session_state.favorites):
        with st.container(border=True):
            st.write(favorite)
            a, b = st.columns(2)

            with a:
                if st.button(
                    "이 문장 사용",
                    key=f"use_fav_{i}",
                    use_container_width=True,
                ):
                    st.session_state.selected_message = favorite
                    st.session_state.message_editor = favorite
                    st.rerun()

            with b:
                if st.button(
                    "삭제",
                    key=f"delete_fav_{i}",
                    use_container_width=True,
                ):
                    st.session_state.favorites.pop(i)
                    st.rerun()

st.divider()
st.caption(
    "마음 한마디는 입력한 문장을 이 화면에서 추천합니다. "
    "즐겨찾기는 현재 실행 중인 세션에서만 유지됩니다."
)
