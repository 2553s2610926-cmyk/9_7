import streamlit as st
import google.generativeai as genai
import datetime
import uuid
import json

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="스마트 AI 민원 접수창",
    page_icon="🏛️",
    layout="wide"
)

# 2. Gemini API 설정
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 API 키가 설정되지 않았습니다. Streamlit Secrets에 `GEMINI_API_KEY`를 등록해 주세요.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
except Exception as e:
    st.error(f"API 초기화 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 세션 상태(임시 DB 역할) 초기화
if "complaints" not in st.session_state:
    st.session_state.complaints = []

# AI 분석 함수
def analyze_complaint(title, content):
    prompt = f"""
    당신은 지자체 민원 분석 전문가입니다. 아래 민원 내용을 분석하여 반드시 지정된 JSON 형식으로만 응답해 주세요.

    [민원 제목]: {title}
    [민원 내용]: {content}

    [응답 JSON 양식]:
    {{
        "category": "교통/도로, 환경/위생, 시설/건설, 복지/보건, 기타 중 하나 선택",
        "urgency": "상, 중, 하 중 하나 선택",
        "department": "추천 담당 부서명 (예: 도로교통과, 청소행정과 등)",
        "summary": "민원 내용 핵심 1문장 요약",
        "draft_reply": "민원인에게 전달할 친절하고 정중한 공식 답변 초안 (3문장 이내)"
    }}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # 마크다운 코드 블록 제거
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        result = json.loads(text.strip())
        return result
    except Exception as e:
        # AI 예외 처리 시 기본값 반환
        return {
            "category": "기타",
            "urgency": "중",
            "department": "일반민원과",
            "summary": "민원 내용 분석 중 오류가 발생했습니다.",
            "draft_reply": "접수해주신 민원은 담당 부서 확인 후 처리될 예정입니다."
        }

# 4. 앱 헤더
st.title("🏛️ 스마트 AI 민원 접수창")
st.caption("시민의 소리를 AI가 빠르게 분석하여 정확하고 신속한 해결을 돕습니다.")

# 5. 탭 구성
tab1, tab2, tab3 = st.tabs(["📝 민원 접수하기", "🔍 민원 조회하기", "🏢 [관리자] 민원 처리"])

# ==========================================
# TAB 1: 민원 접수하기
# ==========================================
with tab1:
    st.subheader("새로운 민원을 작성해 주세요")
    
    with st.form("complaint_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("작성자 성명 *", placeholder="홍길동")
            contact = st.text_input("연락처 *", placeholder="010-1234-5678")
        with col2:
            region = st.selectbox("소속 지역구", ["중구", "동구", "서구", "남구", "북구", "기타"])
            is_private = st.checkbox("비공개 민원으로 신청")

        title = st.text_input("민원 제목 *", placeholder="예: OO동 사거리 신호등 고장 수리 요청")
        content = st.text_area("민원 상세 내용 *", placeholder="민원 발생 장소, 상황, 요구 사항 등을 자세히 작성해 주세요.", height=200)
        
        submit_button = st.form_submit_button("🚀 민원 접수하기", type="primary")

    if submit_button:
        if not name.strip() or not contact.strip() or not title.strip() or not content.strip():
            st.warning("⚠️ 모든 필수 항목(*)을 작성해 주세요.")
        else:
            with st.spinner("AI가 민원 내용을 분석 및 분류하고 있습니다..."):
                analysis = analyze_complaint(title, content)
                
                complaint_id = f"CIV-{datetime.datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                
                new_complaint = {
                    "id": complaint_id,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "name": name,
                    "contact": contact,
                    "region": region,
                    "title": title,
                    "content": content,
                    "is_private": is_private,
                    "category": analysis.get("category", "기타"),
                    "urgency": analysis.get("urgency", "중"),
                    "department": analysis.get("department", "일반민원과"),
                    "summary": analysis.get("summary", ""),
                    "draft_reply": analysis.get("draft_reply", ""),
                    "status": "접수 완료",
                    "final_reply": ""
                }
                
                st.session_state.complaints.append(new_complaint)
                
                st.success("✅ 민원이 정상적으로 접수되었습니다!")
                st.info(f"📌 **접수 번호:** `{complaint_id}` (이 번호로 민원 처리 현황을 조회할 수 있습니다.)")
                
                with st.expander("🤖 AI 자동 분석 결과 확인", expanded=True):
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("분류 카테고리", new_complaint["category"])
                    col_b.metric("처리 긴급도", new_complaint["urgency"])
                    col_c.metric("추천 담당부서", new_complaint["department"])
                    st.write(f"**AI 요약:** {new_complaint['summary']}")

# ==========================================
# TAB 2: 민원 조회하기
# ==========================================
with tab2:
    st.subheader("민원 처리 현황 조회")
    
    search_id = st.text_input("접수 번호를 입력하세요", placeholder="예: CIV-20261016-A1B2")
    
    if st.button("조회하기"):
        if not search_id.strip():
            st.warning("접수 번호를 입력해 주세요.")
        else:
            found = [c for c in st.session_state.complaints if c["id"] == search_id.strip()]
            if found:
                item = found[0]
                st.success(f"민원을 찾았습니다. [현재 상태: **{item['status']}**]")
                
                st.markdown(f"**접수 일시:** {item['date']}")
                st.markdown(f"**민원 제목:** {item['title']}")
                st.markdown(f"**민원 내용:**\n{item['content']}")
                
                st.divider()
                st.markdown(f"**담당 부서:** {item['department']}")
                
                if item["final_reply"]:
                    st.info(f"💬 **답변 내용:**\n\n{item['final_reply']}")
                else:
                    st.warning("⌛ 담당 부서에서 민원을 검토 중입니다. 빠른 시일 내에 답변드리겠습니다.")
            else:
                st.error("해당 접수 번호로 등록된 민원을 찾을 수 없습니다.")

# ==========================================
# TAB 3: [관리자] 민원 처리
# ==========================================
with tab3:
    st.subheader("🏢 담당자 민원 관리 대시보드")
    
    if not st.session_state.complaints:
        st.info("현재 접수된 민원이 없습니다.")
    else:
        # 필터링 옵션
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            status_filter = st.selectbox("상태 필터", ["전체", "접수 완료", "처리 중", "답변 완료"])
        with col_f2:
            urgency_filter = st.selectbox("긴급도 필터", ["전체", "상", "중", "하"])
            
        filtered_list = st.session_state.complaints
        if status_filter != "전체":
            filtered_list = [c for c in filtered_list if c["status"] == status_filter]
        if urgency_filter != "전체":
            filtered_list = [c for c in filtered_list if c["urgency"] == urgency_filter]
            
        st.write(f"총 **{len(filtered_list)}**건의 민원이 검색되었습니다.")
        
        for idx, item in enumerate(filtered_list):
            badge_color = "🔴" if item["urgency"] == "상" else ("🟡" if item["urgency"] == "중" else "🟢")
            
            with st.expander(f"{badge_color} [{item['id']}] {item['title']} ({item['category']} | {item['status']})"):
                st.write(f"**신청자:** {item['name']} ({item['contact']}) | **지역:** {item['region']}")
                st.write(f"**접수일:** {item['date']} | **담당부서:** {item['department']}")
                st.markdown(f"**내용:** {item['content']}")
                st.info(f"🤖 **AI 핵심 요약:** {item['summary']}")
                
                st.divider()
                st.subheader("답변 등록 및 상태 업데이트")
                
                # AI 답변 초안 활용
                reply_text = st.text_area(
                    "답변 내용 입력 (AI 초안 수정 가능)",
                    value=item["final_reply"] if item["final_reply"] else item["draft_reply"],
                    key=f"reply_{item['id']}"
                )
                
                new_status = st.selectbox(
                    "처리 상태 변경",
                    ["접수 완료", "처리 중", "답변 완료"],
                    index=["접수 완료", "처리 중", "답변 완료"].index(item["status"]),
                    key=f"status_{item['id']}"
                )
                
                if st.button("답변 저장하기", key=f"btn_{item['id']}"):
                    item["final_reply"] = reply_text
                    item["status"] = new_status
                    st.success("민원 처리 내역이 업데이트되었습니다")
pip install streamlit
python-3.11
