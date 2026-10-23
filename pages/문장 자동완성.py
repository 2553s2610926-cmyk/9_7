
import streamlit as st
import requests
import re
import hmac
import hashlib
import secrets
from datetime import datetime, timezone

st.set_page_config(
    page_title="마음 한마디",
    page_icon="💌",
    layout="centered",
)

st.markdown("""
<style>
.stApp { background: #FFF9F0; }
.block-container { max-width: 800px; padding-top: 1.5rem; }
h1, h2, h3 { color: #493522; }
div.stButton > button {
    min-height: 55px;
    width: 100%;
    white-space: normal;
    font-size: 1.05rem;
    border-radius: 12px;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 문장 데이터
# --------------------------------------------------
SENTENCES = [
    ("가족", ["딸", "아들", "손주", "보고싶", "보고 싶"],
     "잘 지내고 있니? 보고 싶구나. 시간 될 때 전화해 줘."),
    ("가족", ["사랑", "고마워", "가족"],
     "항상 고맙고 사랑한다. 건강하게 잘 지내자."),
    ("전화", ["전화", "통화", "연락"],
     "시간 괜찮을 때 전화 한 통 해 주면 좋겠어."),
    ("병원", ["병원", "진료", "의사", "아파"],
     "오늘 병원에 다녀오려고 해. 끝나면 다시 연락할게."),
    ("약", ["약", "처방", "약국"],
     "약을 먹어야 하는데 복용 방법을 다시 알려 줄 수 있니?"),
    ("부탁", ["장보기", "마트", "시장", "부탁", "사다"],
     "미안하지만 필요한 물건을 사다 줄 수 있을까?"),
    ("외출", ["외출", "늦", "귀가"],
     "지금 외출 중이야. 조금 늦을 수 있으니 걱정하지 마."),
    ("식사", ["밥", "식사", "먹", "점심", "저녁"],
     "밥은 먹었니? 끼니 잘 챙겨 먹고 건강하렴."),
    ("감사", ["고마워", "감사", "도움", "덕분"],
     "도와줘서 정말 고마워. 덕분에 큰 도움이 되었어."),
    ("안부", ["안녕", "안부", "건강"],
     "잘 지내고 있니? 건강 조심하고 시간 될 때 연락해 줘."),
    ("사과", ["미안", "죄송", "사과"],
     "내가 말을 잘못했다면 미안해. 너를 생각하는 마음은 같아."),
    ("도움", ["도움", "급해", "위험"],
     "지금 도움이 필요해. 가능하면 빨리 연락해 줘."),
    ("인사", ["잘 자", "밤", "잠"],
     "오늘도 수고 많았어. 편안한 밤 보내고 푹 쉬렴."),
    ("인사", ["아침", "좋은 하루"],
     "좋은 아침이야. 오늘도 건강하고 행복한 하루 보내렴."),
]

QUICK_WORDS = ["딸", "전화", "병원", "고마워", "밥", "도움"]

# --------------------------------------------------
# 세션 상태
# --------------------------------------------------
if "contacts" not in st.session_state:
    st.session_state.contacts = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "message_editor" not in st.session_state:
    st.session_state.message_editor = ""

if "keyword" not in st.session_state:
    st.session_state.keyword = ""

# --------------------------------------------------
# 전화번호 및 API 처리
# --------------------------------------------------
def normalize_phone(phone):
    """공백, 하이픈, 괄호를 제거하고 전화번호를 검증합니다."""
    cleaned = re.sub(r"[\s\-()]", "", phone.strip())
    if not re.fullmatch(r"\+?[0-9]{8,15}", cleaned):
        raise ValueError("전화번호 형식을 확인해 주세요.")
    return cleaned


def create_auth_header(api_key, api_secret):
    """SOLAPI HMAC-SHA256 인증 헤더를 생성합니다."""
    date_time = (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
    salt = secrets.token_hex(16)
    signature = hmac.new(
        api_secret.encode("utf-8"),
        (date_time + salt).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return (
        f"HMAC-SHA256 apiKey={api_key}, "
        f"date={date_time}, salt={salt}, signature={signature}"
    )


def send_sms(to_number, message):
    """SOLAPI에 SMS/LMS 발송을 요청합니다."""
    api_key = st.secrets.get("SOLAPI_API_KEY", "")
    api_secret = st.secrets.get("SOLAPI_API_SECRET", "")
    from_number = st.secrets.get("SOLAPI_FROM_NUMBER", "")

    if not api_key or not api_secret or not from_number:
        raise RuntimeError(
            "문자 발송 설정이 없습니다. "
            "Streamlit Secrets에 API Key, API Secret, 발신번호를 등록해 주세요."
        )

    to_number = normalize_phone(to_number)
    from_number = normalize_phone(from_number)

    if not message.strip():
        raise ValueError("보낼 문장을 입력해 주세요.")

    # SOLAPI의 자동 타입 판별에 따라 SMS 또는 LMS로 발송됩니다.
    payload = {
        "messages": [
            {
                "to": to_number,
                "from": from_number,
                "text": message.strip(),
            }
        ]
    }

    headers = {
        "Authorization": create_auth_header(api_key, api_secret),
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://api.solapi.com/messages/v4/send-many/detail",
            json=payload,
            headers=headers,
            timeout=20,
        )
    except requests.Timeout as exc:
        raise RuntimeError(
            "발송 요청 시간이 초과되었습니다. "
            "중복 발송을 막기 위해 발송 내역을 먼저 확인해 주세요."
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(
            "문자 서비스에 연결할 수 없습니다. 인터넷 연결을 확인해 주세요."
        ) from exc

    try:
        result = response.json()
    except ValueError:
        result = {}

    if not response.ok:
        code = result.get("errorCode", "")
        detail = result.get("errorMessage", "")
        if not detail:
            detail = "문자 서비스에서 오류 응답을 반환했습니다."
        raise RuntimeError(f"발송 실패 (HTTP {response.status_code}, {code}): {detail}")

    failed = result.get("failedMessageList", [])
    if failed:
        first = failed[0]
        reason = (
            first.get("statusMessage")
            or first.get("errorMessage")
            or first.get("reason")
            or "발송 요청이 거부되었습니다."
        )
        raise RuntimeError(f"발송 실패: {reason}")

    return result


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


# --------------------------------------------------
# 앱 화면
# --------------------------------------------------
st.title("💌 마음 한마디")
st.write(
    "받는 사람을 선택하고, 문장을 골라 수정한 뒤 실제 문자 발송을 요청할 수 있어요."
)

st.header("1. 📇 연락처")

with st.expander("새 연락처 등록", expanded=not st.session_state.contacts):
    with st.form("contact_form", clear_on_submit=True):
        name_input = st.text_input("이름", placeholder="예: 우리 딸")
        phone_input = st.text_input(
            "전화번호", placeholder="예: 010-1234-5678"
        )
        add_contact = st.form_submit_button(
            "연락처 저장", use_container_width=True
        )

        if add_contact:
            try:
                name = name_input.strip()
                phone = normalize_phone(phone_input)

                if not name:
                    st.error("이름을 입력해 주세요.")
                elif any(
                    c["phone"] == phone for c in st.session_state.contacts
                ):
                    st.error("이미 등록된 전화번호입니다.")
                else:
                    st.session_state.contacts.append(
                        {"name": name, "phone": phone}
                    )
                    st.rerun()
            except ValueError as exc:
                st.error(str(exc))

if st.session_state.contacts:
    for i, contact in enumerate(st.session_state.contacts):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{contact['name']}** · {contact['phone']}")
        with col2:
            if st.button("삭제", key=f"contact_del_{i}"):
                st.session_state.contacts.pop(i)
                st.rerun()

    options = {
        f"{c['name']} ({c['phone']})": c
        for c in st.session_state.contacts
    }
    recipient_label = st.selectbox(
        "문자를 보낼 사람", list(options.keys())
    )
    recipient = options[recipient_label]
else:
    recipient = None
    st.info("먼저 연락처를 등록해 주세요.")

st.divider()
st.header("2. ✏️ 문장 자동완성")

quick_cols = st.columns(3)
for i, word in enumerate(QUICK_WORDS):
    with quick_cols[i % 3]:
        if st.button(word, key=f"quick_{i}"):
            st.session_state.keyword = word
            st.rerun()

keyword = st.text_input(
    "키워드",
    key="keyword",
    placeholder="예: 딸, 병원, 전화, 고마워",
)

category = st.selectbox(
    "상황",
    ["전체"] + list(dict.fromkeys(item[0] for item in SENTENCES)),
)

try:
    results = find_sentences(keyword, category)
    if not results:
        st.info("일치하는 문장이 없어 기본 문장을 보여 드립니다.")
        results = [
            ("안부", "잘 지내고 있니? 시간 될 때 연락해 줘."),
            ("부탁", "미안하지만 잠시 도와줄 수 있을까?"),
        ]

    results = results[:12]

    for i in range(0, len(results), 2):
        cols = st.columns(2)
        for offset, col in enumerate(cols):
            idx = i + offset
            if idx >= len(results):
                continue

            group, text = results[idx]
            with col:
                st.caption(group)
                if st.button(text, key=f"sentence_{idx}"):
                    st.session_state.message_editor = text
                    st.rerun()

except Exception:
    st.error("문장 추천 중 오류가 발생했습니다. 다시 시도해 주세요.")

st.header("3. 📝 최종 문장 확인")
message = st.text_area(
    "이 문장을 보냅니다. 필요하면 수정하세요.",
    key="message_editor",
    height=140,
    placeholder="문장 카드를 선택하거나 직접 입력하세요.",
)

if st.session_state.favorites:
    with st.expander("⭐ 즐겨찾기"):
        for i, favorite in enumerate(st.session_state.favorites):
            st.write(favorite)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("사용", key=f"fav_use_{i}"):
                    st.session_state.message_editor = favorite
                    st.rerun()
            with col2:
                if st.button("삭제", key=f"fav_del_{i}"):
                    st.session_state.favorites.pop(i)
                    st.rerun()

if st.button("⭐ 현재 문장 즐겨찾기 저장", use_container_width=True):
    current = st.session_state.message_editor.strip()
    if current:
        if current not in st.session_state.favorites:
            st.session_state.favorites.append(current)
        st.success("즐겨찾기에 저장했습니다.")
    else:
        st.warning("먼저 문장을 입력해 주세요.")

st.divider()
st.header("4. 📩 실제 문자 보내기")

if recipient:
    st.write(f"**받는 사람:** {recipient['name']}")
    st.write(f"**전화번호:** {recipient['phone']}")
else:
    st.warning("먼저 연락처를 등록하고 수신자를 선택해 주세요.")

st.warning(
    "문자 발송에는 서비스 이용료가 발생할 수 있습니다. "
    "번호와 내용을 반드시 확인하세요."
)

confirmed = st.checkbox(
    "받는 사람과 문장 내용을 확인했습니다. 문자 발송에 동의합니다."
)

if st.button("📩 실제 문자 발송", type="primary", use_container_width=True):
    if not recipient:
        st.error("먼저 연락처를 등록하고 선택해 주세요.")
    elif not st.session_state.message_editor.strip():
        st.error("보낼 문장을 입력해 주세요.")
    elif not confirmed:
        st.error("발송 전 확인 항목에 체크해 주세요.")
    else:
        with st.spinner("문자 발송 요청 중입니다..."):
            try:
                result = send_sms(
                    recipient["phone"],
                    st.session_state.message_editor,
                )
                st.success(
                    "문자 발송 요청이 접수되었습니다. "
                    "실제 수신 여부는 발송 내역에서 확인해 주세요."
                )

                group_info = result.get("groupInfo", {})
                if group_info.get("groupId"):
                    st.caption(
                        f"발송 그룹 ID: {group_info['groupId']}"
                    )

            except (ValueError, RuntimeError) as exc:
                st.error(str(exc))
            except Exception:
                st.error(
                    "예상하지 못한 오류가 발생했습니다. "
                    "문자 발송 내역을 확인한 뒤 다시 시도해 주세요."
                )

st.caption(
    "안내: 연락처와 즐겨찾기는 현재 세션에 보관됩니다. "
    "이 앱은 문자 발송 요청 결과를 보여 주며, "
    "요청 접수가 실제 수신 완료를 의미하지는 않습니다."
)
