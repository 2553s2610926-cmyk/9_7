
import re
import json
import streamlit as st
from urllib.parse import quote

st.set_page_config(
    page_title="마음 한마디",
    page_icon="💌",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp { background: #FFF9F0; }
.block-container { max-width: 820px; padding-top: 1.5rem; }
h1, h2, h3 { color: #493522; }
h1 { font-size: 2.2rem !important; }
div.stButton > button {
    min-height: 58px;
    width: 100%;
    white-space: normal;
    border-radius: 14px;
    border: 2px solid #D8C5AA;
    background: white;
    color: #493522;
    font-size: 1.05rem;
    font-weight: 600;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

SENTENCES = [
    ("가족", ["딸", "아들", "손주", "보고싶", "보고 싶"],
     "잘 지내고 있니? 보고 싶구나. 시간 될 때 전화해 줘."),
    ("가족", ["사랑", "고마워", "가족"],
     "항상 고맙고 사랑한다. 건강하게 잘 지내자."),
    ("전화", ["전화", "통화", "연락"],
     "시간 괜찮을 때 전화 한 통 해 주면 좋겠어."),
    ("병원", ["병원", "진료", "의사", "아파", "아픔"],
     "오늘 병원에 다녀오려고 해. 끝나면 다시 연락할게."),
    ("약", ["약", "처방", "약국"],
     "약을 먹어야 하는데 복용 방법을 다시 알려 줄 수 있니?"),
    ("부탁", ["장보기", "마트", "시장", "부탁", "사다"],
     "미안하지만 필요한 물건을 사다 줄 수 있을까?"),
    ("외출", ["외출", "늦", "귀가", "어디"],
     "지금 외출 중이야. 조금 늦을 수 있으니 걱정하지 마."),
    ("식사", ["밥", "식사", "먹", "점심", "저녁"],
     "밥은 먹었니? 끼니 잘 챙겨 먹고 건강하렴."),
    ("감사", ["고마워", "감사", "도움", "덕분"],
     "도와줘서 정말 고마워. 덕분에 큰 도움이 되었어."),
    ("안부", ["안녕", "안부", "잘 지내", "건강"],
     "잘 지내고 있니? 날씨가 변덕스러우니 건강 조심하렴."),
    ("사과", ["미안", "죄송", "사과", "잘못"],
     "내가 말을 잘못했다면 미안해. 너를 생각하는 마음은 같아."),
    ("도움 요청", ["도움", "급해", "위급", "위험"],
     "지금 도움이 필요해. 가능하면 빨리 연락해 줘."),
    ("인사", ["잘 자", "밤", "잠"],
     "오늘도 수고 많았어. 편안한 밤 보내고 푹 쉬렴."),
    ("인사", ["아침", "좋은 하루", "인사"],
     "좋은 아침이야. 오늘도 건강하고 행복한 하루 보내렴."),
]

QUICK_WORDS = ["딸", "전화", "병원", "고마워", "밥", "도움"]

if "contacts" not in st.session_state:
    st.session_state.contacts = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "message_editor" not in st.session_state:
    st.session_state.message_editor = ""
if "keyword" not in st.session_state:
    st.session_state.keyword = ""
if "notice" not in st.session_state:
    st.session_state.notice = ""

def valid_phone(phone):
    """한국 전화번호 형식의 기본 검증."""
    cleaned = re.sub(r"[\s\-()]", "", phone)
    return bool(re.fullmatch(r"\+?[0-9]{8,15}", cleaned))

def find_sentences(keyword, category):
    keyword = keyword.strip().lower()
    found = []
    for group, keywords, message in SENTENCES:
        if category != "전체" and group != category:
            continue
        searchable = " ".join([group, message] + keywords).lower()
        terms = keyword.split()
        if not keyword or any(term in searchable for term in terms):
            found.append((group, message))
    return found

st.title("💌 마음 한마디")
st.markdown("""
내 마음을 쉽게 전해 보세요.
먼저 받는 사람을 고르고, 문장을 선택한 뒤 문자 보내기를 누르세요.
""")

# 연락처 등록
st.header("1. 📇 연락처 목록")
with st.expander("연락처 추가하기", expanded=not st.session_state.contacts):
    with st.form("add_contact_form", clear_on_submit=True):
        person_name = st.text_input("이름", placeholder="예: 우리 딸")
        person_phone = st.text_input(
            "전화번호",
            placeholder="예: 010-1234-5678",
            help="국가번호를 사용하는 번호도 입력할 수 있습니다.",
        )
        submitted = st.form_submit_button("연락처 저장", use_container_width=True)

        if submitted:
            name = person_name.strip()
            phone = re.sub(r"[\s\-()]", "", person_phone.strip())
            if not name:
                st.error("이름을 입력해 주세요.")
            elif not valid_phone(phone):
                st.error("전화번호를 확인해 주세요. 숫자와 선택적인 + 기호를 입력할 수 있습니다.")
            elif any(c["phone"] == phone for c in st.session_state.contacts):
                st.error("이미 등록된 전화번호입니다.")
            else:
                st.session_state.contacts.append({
                    "name": name,
                    "phone": phone,
                })
                st.session_state.notice = f"{name} 연락처를 저장했어요."
                st.rerun()

if st.session_state.notice:
    st.success(st.session_state.notice)
    st.session_state.notice = ""

if st.session_state.contacts:
    for i, contact in enumerate(st.session_state.contacts):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{contact['name']}**")
                st.write(contact["phone"])
            with col2:
                if st.button("삭제", key=f"del_contact_{i}"):
                    st.session_state.contacts.pop(i)
                    st.rerun()

    contact_options = {
        f"{c['name']} ({c['phone']})": c
        for c in st.session_state.contacts
    }
    selected_label = st.selectbox(
        "문자를 보낼 사람을 선택하세요",
        list(contact_options.keys()),
        key="recipient",
    )
    recipient = contact_options[selected_label]
else:
    recipient = None
    st.info("먼저 연락처를 등록해 주세요. 연락처는 현재 세션에 저장됩니다.")

st.divider()
st.header("2. ✏️ 보낼 문장 만들기")

for start in range(0, len(QUICK_WORDS), 3):
    cols = st.columns(3)
    for offset, col in enumerate(cols):
        idx = start + offset
        if idx < len(QUICK_WORDS):
            word = QUICK_WORDS[idx]
            with col:
                if st.button(word, key=f"quick_{idx}"):
                    st.session_state.keyword = word
                    st.rerun()

keyword = st.text_input(
    "주요 키워드",
    key="keyword",
    placeholder="예: 딸, 병원, 전화, 고마워",
)

categories = ["전체"] + list(dict.fromkeys(row[0] for row in SENTENCES))
category = st.selectbox("상황", categories)

st.caption("아래 문장을 누르면 수정할 문장에 바로 나타납니다.")

try:
    results = find_sentences(keyword, category)
    if not results:
        results = [
            ("안부", "잘 지내고 있니? 시간 될 때 연락해 줘."),
            ("부탁", "미안하지만 잠시 도와줄 수 있을까?"),
        ]
        st.info("일치하는 문장이 없어 기본 문장을 보여 드립니다.")

    for i in range(0, min(len(results), 12), 2):
        cols = st.columns(2)
        for offset, col in enumerate(cols):
            idx = i + offset
            if idx >= min(len(results), 12):
                continue
            group, message = results[idx]
            with col:
                st.caption(group)
                if st.button(message, key=f"pick_{idx}"):
                    # 입력 위젯이 생성되기 전에 상태를 설정합니다.
                    st.session_state.message_editor = message
                    st.rerun()
except Exception:
    st.error("문장 추천 중 문제가 발생했습니다. 다시 시도해 주세요.")

st.subheader("3. 완성된 문장")
message = st.text_area(
    "보낼 내용을 확인하고 수정하세요",
    key="message_editor",
    height=140,
    placeholder="위 문장 카드를 누르면 여기에 표시됩니다.",
)

current_message = st.session_state.message_editor.strip()

col1, col2 = st.columns(2)
with col1:
    if st.button("⭐ 즐겨찾기 저장", use_container_width=True):
        if current_message:
            if current_message not in st.session_state.favorites:
                st.session_state.favorites.append(current_message)
            st.success("즐겨찾기에 저장했어요.")
        else:
            st.warning("먼저 문장을 선택하거나 입력해 주세요.")

with col2:
    if st.button("문장 비우기", use_container_width=True):
        st.session_state.message_editor = ""
        st.rerun()

if st.session_state.favorites:
    with st.expander("⭐ 즐겨찾기 문장"):
        for i, favorite in enumerate(st.session_state.favorites):
            st.write(favorite)
            a, b = st.columns(2)
            with a:
                if st.button("사용", key=f"use_fav_{i}"):
                    st.session_state.message_editor = favorite
                    st.rerun()
            with b:
                if st.button("삭제", key=f"del_fav_{i}"):
                    st.session_state.favorites.pop(i)
                    st.rerun()

st.divider()
st.header("4. 📩 문자 보내기")

if not recipient:
    st.info("문자를 보내려면 먼저 연락처를 등록하고 선택하세요.")
elif not current_message:
    st.info("먼저 보낼 문장을 선택하거나 직접 입력하세요.")
else:
    st.markdown(f"**받는 사람:** {recipient['name']} ({recipient['phone']})")
    sms_url = (
        f"sms:{quote(recipient['phone'], safe='+')}"
        f"?body={quote(current_message, safe='')}"
    )

    st.markdown(
        f"""
        <a href="{sms_url}"
           style="
             display:block;
             text-align:center;
             padding:16px;
             margin:8px 0;
             background:#287D50;
             color:white;
             text-decoration:none;
             border-radius:14px;
             font-size:20px;
             font-weight:bold;
           ">
           📩 문자 작성 화면 열기
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "휴대전화와 브라우저가 문자 연결을 지원하면 문자 작성 화면이 열립니다. "
        "번호와 문장이 자동 입력되지 않는 기기에서는 직접 붙여넣어 주세요. "
        "실제 전송은 문자 앱에서 확인 후 완료해야 합니다."
    )

    st.code(current_message, language=None)
    st.caption("위 문장의 복사 아이콘을 눌러 복사할 수도 있습니다.")

st.divider()
st.caption(
    "개인정보 안내: 연락처는 이 앱의 현재 세션 메모리에만 보관됩니다. "
    "세션 종료 또는 재시작 시 사라질 수 있습니다. "
    "이 앱은 문자를 자동 발송하지 않습니다."
)
