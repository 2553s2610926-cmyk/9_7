
import re
import hmac
import hashlib
import secrets
from datetime import datetime, timezone

import requests
import streamlit as st

st.set_page_config(
    page_title="마음 한마디",
    page_icon="💌",
    layout="centered",
)

st.markdown("""
<style>
.stApp { background-color: #FFF9F0; }
.block-container { max-width: 800px; padding-top: 1.5rem; }
h1, h2, h3 { color: #493522; }
div.stButton > button {
    min-height: 52px;
    width: 100%;
    white-space: normal;
    font-size: 1rem;
    border-radius: 12px;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    font-size: 1.05rem;
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

# 모든 상태는 위젯 생성 전에 초기화합니다.
defaults = {
    "contacts": [],
    "favorites": [],
    "keyword": "",
    "message_editor": "",
    "recipient_label": "",
    "notice": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def normalize_phone(phone):
    phone = re.sub(r"[\s\-()]", "", phone.strip())
    if not re.fullmatch(r"\+?[0-9]{8,15}", phone):
        raise ValueError("전화번호를 확인해 주세요. 예: 010-1234-5678")
    return phone


def find_sentences(keyword, category):
    keyword = keyword.strip().lower()
    results = []

    for group, keywords, message in SENTENCES:
        if category != "전체" and category != group:
            continue

        searchable = " ".join([group, message] + keywords).lower()
        terms = keyword.split()

        if not keyword or any(term in searchable for term in terms):
            results.append((group, message))

    return results


def send_sms(phone, message):
    # Secrets 누락도 친절한 오류로 처리합니다.
    try:
        api_key = st.secrets["SOLAPI_API_KEY"]
        api_secret = st.secrets["SOLAPI_API_SECRET"]
        from_number = st.secrets["SOLAPI_FROM_NUMBER"]
    except Exception as exc:
        raise RuntimeError(
            "문자 발송 설정이 없습니다. "
            "Streamlit Settings > Secrets에 SOLAPI 설정을 입력해 주세요."
        ) from exc

    phone = normalize_phone(phone)
    from_number = normalize_phone(from_number)
    message = message.strip()

    if not message:
        raise ValueError("보낼 문장을 입력해 주세요.")

    date_time = (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
    salt = secrets.token_hex(16)
    signature = hmac.new(
        str(api_secret).encode("utf-8"),
        (date_time + salt).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "Authorization": (
            f"HMAC-SHA256 apiKey={api_key}, date={date_time}, "
            f"salt={salt}, signature={signature}"
        ),
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [{
            "to": phone,
            "from": from_number,
            "text": message,
        }]
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
            "중복 발송 방지를 위해 발송 내역을 확인한 뒤 재시도하세요."
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(
            "문자 서비스에 연결하지 못했습니다. 인터넷 연결을 확인해 주세요."
        ) from exc

    try:
        result = response.json()
    except ValueError:
        result = {}

    if not response.ok:
        detail = (
            result.get("errorMessage")
            or result.get("message")
            or "문자 서비스에서 요청을 거부했습니다."
        )
        code = result.get("errorCode", "")
        raise RuntimeError(
            f"발송 실패 (HTTP {response.status_code}, {code}): {detail}"
        )

    failed = result.get("failedMessageList", [])
    if failed:
        item = failed[0]
        reason = (
            item.get("statusMessage")
            or item.get("errorMessage")
            or item.get("reason")
            or "발송에 실패했습니다."
        )
        raise RuntimeError(str(reason))

    return result


# --------------------------------------------------
# 1. 연락처 관리
# --------------------------------------------------
st.title("💌 마음 한마디")
st.write("받는 사람을 선택하고, 하고 싶은 말을 쉽게 문자로 보내세요.")

st.header("1. 📇 연락처")

with st.expander("새 연락처 등록", expanded=not st.session_state.contacts):
    with st.form("add_contact_form", clear_on_submit=True):
        name_input = st.text_input("이름", placeholder="예: 우리 딸")
        phone_input = st.text_input(
            "전화번호", placeholder="예: 010-1234-5678"
        )
        add_clicked = st.form_submit_button(
            "연락처 저장", use_container_width=True
        )

    if add_clicked:
        try:
            name = name_input.strip()
            phone = normalize_phone(phone_input)

            if not name:
                st.error("이름을 입력해 주세요.")
            elif any(
                c["phone"] == phone for c in st.session_state.contacts
            ):
                st.error("이미 저장된 전화번호입니다.")
            else:
                st.session_state.contacts.append({
                    "name": name,
                    "phone": phone,
                })
                st.session_state.notice = f"{name} 연락처를 저장했습니다."
                st.rerun()
        except ValueError as exc:
            st.error(str(exc))

if st.session_state.notice:
    st.success(st.session_state.notice)
    st.session_state.notice = ""

# 연락처 삭제 동작은 문장 입력창 생성 전에 처리합니다.
if st.session_state.contacts:
    st.subheader("저장된 연락처")

    for i, contact in enumerate(st.session_state.contacts):
        left, right = st.columns([4, 1])
        with left:
            st.write(f"**{contact['name']}** · {contact['phone']}")
        with right:
            if st.button("삭제", key=f"delete_contact_{i}"):
                st.session_state.contacts.pop(i)
                st.rerun()

    contact_labels = [
        f"{c['name']} ({c['phone']})"
        for c in st.session_state.contacts
    ]

    # 삭제된 연락처가 선택되어 있어도 안전하게 기본값을 선택합니다.
    if st.session_state.recipient_label not in contact_labels:
        st.session_state.recipient_label = contact_labels[0]

    selected_label = st.selectbox(
        "문자를 받을 사람",
        contact_labels,
        key="recipient_label",
    )
    recipient = st.session_state.contacts[contact_labels.index(selected_label)]
else:
    recipient = None
    st.info("문자를 보내려면 먼저 연락처를 등록해 주세요.")


# --------------------------------------------------
# 2. 키워드와 문장 선택
# --------------------------------------------------
st.divider()
st.header("2. ✏️ 문장 자동완성")

cols = st.columns(3)
for i, word in enumerate(QUICK_WORDS):
    with cols[i % 3]:
        if st.button(word, key=f"quick_{i}"):
            st.session_state.keyword = word
            st.rerun()

keyword = st.text_input(
    "주요 키워드",
    key="keyword",
    placeholder="예: 딸, 병원, 전화, 고마워",
)

categories = ["전체"] + list(dict.fromkeys(x[0] for x in SENTENCES))
category = st.selectbox("상황 선택", categories)

results = find_sentences(keyword, category)
if not results:
    st.info("일치하는 문장이 없습니다. 기본 문장을 보여 드립니다.")
    results = [
        ("안부", "잘 지내고 있니? 시간 될 때 연락해 줘."),
        ("부탁", "미안하지만 잠시 도와줄 수 있을까?"),
    ]

st.caption("마음에 드는 문장을 누르면 아래 입력창에 나타납니다.")

for i in range(0, min(len(results), 12), 2):
    cols = st.columns(2)

    for offset, col in enumerate(cols):
        idx = i + offset
        if idx >= min(len(results), 12):
            continue

        group, text = results[idx]
        with col:
            st.caption(group)
            if st.button(text, key=f"sentence_{idx}"):
                # 이 입력 위젯은 아직 생성되지 않았으므로 안전합니다.
                st.session_state.message_editor = text
                st.rerun()


# --------------------------------------------------
# 3. 즐겨찾기 선택: 입력 위젯 생성 전에 실행
# --------------------------------------------------
if st.session_state.favorites:
    with st.expander("⭐ 즐겨찾기 문장"):
        for i, favorite in enumerate(st.session_state.favorites):
            st.write(favorite)

            left, right = st.columns(2)
            with left:
                if st.button("이 문장 사용", key=f"use_favorite_{i}"):
                    st.session_state.message_editor = favorite
                    st.rerun()

            with right:
                if st.button("삭제", key=f"remove_favorite_{i}"):
                    st.session_state.favorites.pop(i)
                    st.rerun()


# --------------------------------------------------
# 4. 최종 문장 입력창
# 위쪽의 선택 동작이 모두 끝난 뒤 생성합니다.
# --------------------------------------------------
st.divider()
st.header("3. 📝 최종 문장 확인")

st.text_area(
    "보낼 문장을 확인하고 수정하세요.",
    key="message_editor",
    height=140,
    placeholder="위에서 문장을 선택하거나 직접 입력하세요.",
)

current_message = st.session_state.message_editor.strip()

if st.button("⭐ 현재 문장을 즐겨찾기에 저장", use_container_width=True):
    if current_message:
        if current_message not in st.session_state.favorites:
            st.session_state.favorites.append(current_message)
        st.success("즐겨찾기에 저장했습니다.")
    else:
        st.warning("먼저 문장을 선택하거나 입력해 주세요.")


# --------------------------------------------------
# 5. 실제 SMS 발송
# --------------------------------------------------
st.divider()
st.header("4. 📩 문자 보내기")

if recipient:
    st.write(f"**받는 사람:** {recipient['name']}")
    st.write(f"**전화번호:** {recipient['phone']}")
else:
    st.warning("먼저 연락처를 등록하고 선택해 주세요.")

st.warning("발송에는 문자 서비스 이용료가 발생할 수 있습니다.")

confirmed = st.checkbox(
    "받는 사람과 문장을 확인했고, 문자 발송에 동의합니다."
)

if st.button("📩 실제 문자 발송", type="primary", use_container_width=True):
    if not recipient:
        st.error("먼저 연락처를 등록해 주세요.")
    elif not current_message:
        st.error("보낼 문장을 선택하거나 입력해 주세요.")
    elif not confirmed:
        st.error("발송 확인란에 체크해 주세요.")
    else:
        try:
            with st.spinner("문자 발송 요청 중입니다..."):
                result = send_sms(
                    recipient["phone"],
                    current_message,
                )

            st.success(
                "문자 발송 요청이 접수되었습니다. "
                "최종 수신 여부는 문자 서비스의 발송 내역에서 확인해 주세요."
            )

            group_info = result.get("groupInfo", {})
            if group_info.get("groupId"):
                st.caption(f"발송 그룹 ID: {group_info['groupId']}")

        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
        except Exception as exc:
            # 원인을 파악할 수 있도록 오류 유형을 표시합니다.
            st.error(
                f"예상하지 못한 오류가 발생했습니다 ({type(exc).__name__}). "
                "앱 로그와 문자 서비스 발송 내역을 확인해 주세요."
            )

st.caption(
    "연락처와 즐겨찾기는 현재 세션에 저장됩니다. "
    "문자 발송 요청 접수가 실제 수신 완료를 의미하지는 않습니다."
)
