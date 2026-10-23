import streamlit as st
import random

# Page config
st.set_page_config(
    page_title="메신저 기호 사전",
    page_icon="💬",
    layout="centered"
)

# Custom CSS for large text and high-contrast senior-friendly UI
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem !important;
        font-weight: 800;
        color: #1E1E1E;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.2rem !important;
        color: #555555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .icon-card {
        background-color: #F8F9FA;
        border: 2px solid #E9ECEF;
        border-radius: 15px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .icon-large {
        font-size: 4rem !important;
        text-align: center;
        margin-bottom: 10px;
    }
    .meaning-title {
        font-size: 1.6rem !important;
        font-weight: bold;
        color: #2B8A3E;
        margin-bottom: 10px;
    }
    .metaphor-box {
        background-color: #E6FCF5;
        border-left: 5px solid #20C997;
        padding: 12px 15px;
        font-size: 1.2rem !important;
        border-radius: 5px;
        margin: 10px 0;
    }
    .desc-text {
        font-size: 1.15rem !important;
        line-height: 1.6;
        color: #333333;
    }
    .stButton>button {
        font-size: 1.1rem !important;
        font-weight: bold !important;
        padding: 10px 15px !important;
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Definition (Symbols Dictionary) - Updated with actual KakaoTalk icons
# ---------------------------------------------------------
SYMBOLS_DATA = {
    "🔍 돋보기": {
        "icon": "🔍",
        "name": "돋보기 (검색)",
        "metaphor": "💡 '찾기 안경'이에요!",
        "meaning": "원하는 대화 내용, 사람 이름, 또는 사진을 찾아줄 때 누르는 기호입니다.",
        "example": "카카오톡 상단에서 '홍길동'을 입력하면 홍길동님과의 대화방을 바로 찾아줍니다."
    },
    "📎 클립": {
        "icon": "📎",
        "name": "종이클립 (파일 첨부)",
        "metaphor": "💡 '서류 묶는 핀'이에요!",
        "meaning": "사진, 동영상, 또는 문서를 상대방에게 보내고 싶을 때 누르는 기호입니다.",
        "example": "글자 입력창 옆 클립을 누르면 내 폰에 저장된 앨범 사진을 골라서 전송할 수 있습니다."
    },
    "⚙️ 톱니바퀴": {
        "icon": "⚙️",
        "name": "톱니바퀴 (설정)",
        "metaphor": "💡 '시계 뒤태 (기계 조정)'예요!",
        "meaning": "앱의 글자 크기를 바꾸거나, 소리를 끄는 등 모양과 기능을 바꿀 때 씁니다.",
        "example": "글씨가 너무 작을 때 톱니바퀴를 눌러 '글자 크기'를 크게 변경할 수 있습니다."
    },
    "🔔 종": {
        "icon": "🔔",
        "name": "종 (알림)",
        "metaphor": "💡 '대문 벨소리'예요!",
        "meaning": "메시지가 왔을 때 소리나 진동으로 알려주는 기능을 켜고 끄는 기호입니다.",
        "example": "종에 빗금이 그려져 있다면(🔕) 메시지가 와도 소리가 나지 않는 '무음 상태'입니다."
    },
    "➕ 더하기": {
        "icon": "➕",
        "name": "더하기 (메뉴/추가)",
        "metaphor": "💡 '보물상자 열기'예요!",
        "meaning": "숨겨진 다른 기능들(지도 보내기, 송금, 사진 보내기 등)을 더 보여줍니다.",
        "example": "대화창 왼쪽 아래 ➕를 누르면 카메라, 송금, 지도 등의 추가 메뉴가 나옵니다."
    },
    "🔒 자물쇠": {
        "icon": "🔒",
        "name": "자물쇠 (보안/비밀)",
        "metaphor": "💡 '우리만의 비밀방'이에요!",
        "meaning": "나와 상대방 외에는 아무도 대화 내용을 볼 수 없게 암호화되어 있다는 표시입니다.",
        "example": "보안 대화방이나 개인정보 입력 화면에 자주 등장합니다."
    },
    "📌 핀": {
        "icon": "📌",
        "name": "압정 (고정)",
        "metaphor": "💡 '게시판에 메모 고정하기'예요!",
        "meaning": "자주 만나는 중요한 대화방을 맨 위에 올려서 찾기 쉽게 만들어줍니다.",
        "example": "가족 대화방을 압정으로 고정해 두면 대화 목록 맨 위에 항상 위치합니다."
    },
    "🔊 스피커": {
        "icon": "🔊",
        "name": "스피커 (음성/소리)",
        "metaphor": "💡 '확성기'예요!",
        "meaning": "소리를 켜거나, 음성 메시지를 듣거나, 보이스톡(전화)을 할 때 쓰입니다.",
        "example": "상대방이 보낸 목소리 메시지를 들으려면 스피커 모양을 터치하세요."
    },
    "🎙️ 음성메시지": {
        "icon": "🎙️",
        "name": "음성메시지 (목소리 녹음)",
        "metaphor": "💡 '말하는 녹음기'예요!",
        "meaning": "글자를 자판으로 치기 힘들 때 내 목소리를 직접 녹음해서 전달할 때 씁니다.",
        "example": "버튼을 누르고 말을 한 뒤 손을 떼면 내 목소리가 메시지로 상대방에게 전송됩니다."
    },
    "🟡 송금": {
        "icon": "🟡",
        "name": "송금 (원화 ₩ 표시)",
        "metaphor": "💡 '모바일 용돈 봉투'예요!",
        "meaning": "은행 앱을 따로 켜지 않고 메신저 대화방에서 바로 돈을 보낼 때 쓰는 아이콘입니다.",
        "example": "경조사비나 밥값을 정산할 때 대화방 안에서 노란색 '송금' 버튼을 눌러 전달합니다."
    },
    "📍 지도": {
        "icon": "📍",
        "name": "지도 (위치 핀)",
        "metaphor": "💡 '우리 동네 나침반'이에요!",
        "meaning": "내가 지금 있는 장소나 약속 장소의 지도를 상대방에게 전달해줄 때 누릅니다.",
        "example": "모임 장소를 말로 설명하기 어려울 때 '지도' 아이콘을 눌러 위치를 찍어 보내주세요."
    },
    "📂 파일": {
        "icon": "📂",
        "name": "파일 (문서 서류철)",
        "metaphor": "💡 '종이 서류철'이에요!",
        "meaning": "한글 문서(HWP), PDF, 엑셀 파일 등 폰이나 컴퓨터에 있는 문서를 전달할 때 씁니다.",
        "example": "대화창 ➕ 메뉴에서 '파일'을 누르면 저장된 문서나 안내장을 상대방에게 공유할 수 있습니다."
    }
}

# ---------------------------------------------------------
# App Header
# ---------------------------------------------------------
st.markdown("<div class='main-title'>💬 스마트폰 메신저 기호 사전</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>알쏭달쏭한 스마트폰 모양, 터치해서 궁금증을 풀어보세요!</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📖 기호 사전", "🧩 퀴즈 풀기", "💡 쉬운 팁"])

# ---------------------------------------------------------
# Tab 1: Dictionary (Learning)
# ---------------------------------------------------------
with tab1:
    st.subheader("👇 궁금한 기호를 눌러보세요")
    
    keys = list(SYMBOLS_DATA.keys())
    cols = st.columns(4)
    
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = keys[0]
        
    for idx, key in enumerate(keys):
        with cols[idx % 4]:
            if st.button(key, key=f"btn_{idx}", use_container_width=True):
                st.session_state.selected_symbol = key

    selected_data = SYMBOLS_DATA[st.session_state.selected_symbol]
    
    st.markdown("---")
    st.markdown(f"""
        <div class='icon-card'>
            <div class='icon-large'>{selected_data['icon']}</div>
            <div class='meaning-title'>{selected_data['name']}</div>
            <div class='metaphor-box'>{selected_data['metaphor']}</div>
            <p class='desc-text'><b>무슨 뜻인가요?</b><br>{selected_data['meaning']}</p>
            <p class='desc-text'><b>언제 쓰나요?</b><br>{selected_data['example']}</p>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Tab 2: Quiz
# ---------------------------------------------------------
with tab2:
    st.subheader("🧩 오늘 배운 기호 퀴즈")
    st.write("기호의 의미를 맞혀보며 잊지 않도록 복습해 보세요.")

    if "quiz_index" not in st.session_state:
        st.session_state.quiz_index = 0
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "quiz_list" not in st.session_state:
        items = list(SYMBOLS_DATA.values())
        random.shuffle(items)
        st.session_state.quiz_list = items

    quiz_list = st.session_state.quiz_list
    current_idx = st.session_state.quiz_index

    if current_idx < len(quiz_list):
        current_q = quiz_list[current_idx]
        
        st.info(f"문제 {current_idx + 1} / {len(quiz_list)}")
        st.markdown(f"<h1 style='text-align: center;'>{current_q['icon']}</h1>", unsafe_allow_html=True)
        st.markdown(f"### 이 기호의 역할은 무엇일까요?")

        correct_answer = current_q['name']
        
        if f"options_{current_idx}" not in st.session_state:
            wrong_answers = [v['name'] for v in SYMBOLS_DATA.values() if v['name'] != correct_answer]
            selected_wrongs = random.sample(wrong_answers, 3)
            options = selected_wrongs + [correct_answer]
            random.shuffle(options)
            st.session_state[f"options_{current_idx}"] = options
        else:
            options = st.session_state[f"options_{current_idx}"]

        user_choice = st.radio("정답을 선택하세요:", options, key=f"radio_{current_idx}")

        if st.button("정답 확인하기", type="primary"):
            if user_choice == correct_answer:
                st.success("🎉 정답입니다! 참 잘하셨어요.")
            else:
                st.error(f"아쉬워요! 정답은 **[{correct_answer}]** 입니다.")
                
                wrong_symbol = None
                for v in SYMBOLS_DATA.values():
                    if v['name'] == user_choice:
                        wrong_symbol = v
                        break
                
                if wrong_symbol:
                    st.warning(f"""
                    💡 **골라주신 [{wrong_symbol['name']}]은 어떤 아이콘일까요?**
                    * **비유:** {wrong_symbol['metaphor']}
                    * **원래 용도:** {wrong_symbol['meaning']}
                    """)

            if st.button("다음 문제로 ➡️"):
                if user_choice == correct_answer:
                    st.session_state.score += 1
                st.session_state.quiz_index += 1
                st.rerun()

    else:
        st.balloons()
        st.success(f"🎊 퀴즈 완료! 총 {len(quiz_list)}문제 중 {st.session_state.score}문제를 맞히셨습니다!")
        
        if st.button("🔄 퀴즈 다시 풀기"):
            st.session_state.quiz_index = 0
            st.session_state.score = 0
            items = list(SYMBOLS_DATA.values())
            random.shuffle(items)
            st.session_state.quiz_list = items
            st.rerun()

# ---------------------------------------------------------
# Tab 3: Easy Tips
# ---------------------------------------------------------
with tab3:
    st.subheader("💡 초보자를 위한 스마트폰 안심 사용법")
    
    st.markdown("""
    * **1. 잘 모르겠을 때는?**
      * 화면의 **'← (뒤로 가기)'** 화살표를 누르면 이전 화면으로 안전하게 돌아갑니다.
    * **2. 잘못 터치했을 때는?**
      * 당황하지 말고 화면의 빈 곳을 누르거나, 앱을 종료했다가 다시 켜면 원상복구 됩니다.
    * **3. 글자가 잘 안 보일 때는?**
      * 기호 사전의 **⚙️ 톱니바퀴(설정)** 아이콘을 찾으신 후, **[디스플레이] -> [글자 크기]**에서 글씨를 크게 키울 수 있습니다.
    """)
