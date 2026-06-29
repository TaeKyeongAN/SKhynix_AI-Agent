import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------------------------------------------------
# 1. 페이지 기본 설정 및 초기화
# ----------------------------------------------------------------------
st.set_page_config(page_title="SKHynix 성장 파트너", page_icon="🚀", layout="wide")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.5-flash')
except:
    st.error("API 키가 설정되지 않았습니다.")

# ----------------------------------------------------------------------
# 2. 유틸리티 로직 (D-Day 등)
# ----------------------------------------------------------------------
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst)
today = now.date()

# [입사일/월급날 계산 생략 - 베이스 코드 유지]
join_date = date(2026, 7, 1)
d_day_join = (join_date - today).days
join_str = f"D-{d_day_join}" if d_day_join > 0 else (f"D+{-d_day_join}" if d_day_join < 0 else "D-Day (입사일! 🎉)")

# ----------------------------------------------------------------------
# 3. 사이드바 및 메인 구성
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("🏢 SKHynix 성장 파트너")
    condition = st.radio("오늘의 컨디션:", ["😀 최고예요!", "😐 그저 그래요", "😥 피곤해요"])
    mode = st.radio("메뉴 선택:", ["⏱️ 갓생(God-생) 루틴 메이커", "💰 스마트 재무/소비 관리"])

st.title(f"{mode}")

# ----------------------------------------------------------------------
# 4. 메인 탭 로직 (통합)
# ----------------------------------------------------------------------
if mode == "⏱️ 갓생(God-생) 루틴 메이커":
    # 색상 맵핑
    color_map = {'수면': '#3498db', '업무': '#e74c3c', '자기계발': '#f1c40f', '휴식': '#2ecc71'}
    
    # [섹션 1: 타임블록]
    st.subheader("📊 24시간 타임블록 설계")
    col1, col2 = st.columns([7, 3])
    with col1:
        # 기존 통계/타임블록 차트 코드 유지
        c_left, c_right = st.columns(2)
        with c_left:
            period = st.selectbox("기간 단위", ["요일별", "월별"], key="sp")
            val = st.selectbox("항목 선택", ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"] if period=="요일별" else [f"{i}월" for i in range(1,13)], key="sv")
            # [여기에 기존 데이터 매핑 로직 유지]
            st.plotly_chart(px.pie(pd.DataFrame({'a':['수면','업무','휴식','자기계발'],'b':[7,9,6,2]}), values='b', names='a', color='a', color_discrete_map=color_map), use_container_width=True)
    with col2:
        st.subheader("💬 루틴 AI")
        if "chat1" not in st.session_state: st.session_state.chat1 = []
        for m in st.session_state.chat1: st.chat_message(m["role"]).write(m["content"])
        if p1 := st.chat_input("타임블록 상담", key="ci1"):
            st.session_state.chat1.append({"role":"user", "content":p1})
            res = model.generate_content(p1)
            st.session_state.chat1.append({"role":"assistant", "content":res.text})
            st.rerun()

    st.markdown("---")

    # [섹션 2: 감정-성취도]
    st.subheader("🧠 감정-성취도 상관관계 분석")
    col3, col4 = st.columns([7, 3])
    with col3:
        # 기존 line_chart 코드 유지
        st.line_chart(pd.DataFrame(np.random.randint(30, 100, (14, 2)), columns=["성취도", "컨디션"]))
    with col4:
        st.subheader("💬 감정 분석 AI")
        if "chat2" not in st.session_state: st.session_state.chat2 = []
        for m in st.session_state.chat2: st.chat_message(m["role"]).write(m["content"])
        if p2 := st.chat_input("감정 공유", key="ci2"):
            st.session_state.chat2.append({"role":"user", "content":p2})
            res = model.generate_content(p2)
            st.session_state.chat2.append({"role":"assistant", "content":res.text})
            st.rerun()

    # ---------------------------------------------------
    # 탭 2: 스마트 재무 관리
    # ---------------------------------------------------
    elif mode == "💰 스마트 재무/소비 관리":
        st.subheader("📈 첫 월급 황금비율 시뮬레이터")
        save_ratio = st.slider("첫 월급 저축 비율 (%)", 0, 100, 50)
        
        base_salary = 3000000
        monthly_save = base_salary * (save_ratio / 100)
        years = [1, 3, 5]
        assets = [monthly_save * 12 * y * 1.05 for y in years]
        
        chart_data = pd.DataFrame({"예상 자산(원)": assets}, index=["1년 뒤", "3년 뒤", "5년 뒤"])
        st.bar_chart(chart_data)
        
        st.markdown("---")
        st.subheader("💸 소비 패턴 분석 및 팩폭 컨설팅")
        df_expenses = pd.DataFrame([
            {"카테고리": "식비(배달 포함)", "금액": 150000},
            {"카테고리": "교통비", "금액": 30000},
            {"카테고리": "쇼핑/자기계발", "금액": 50000},
            {"카테고리": "기타", "금액": 20000}
        ])
        edited_df = st.data_editor(df_expenses, num_rows="dynamic")
        st.bar_chart(edited_df.set_index("카테고리"))

# ==========================================
# [오른쪽 영역] AI 에이전트 채팅
# ==========================================
with col_chat:
    st.subheader("💬 AI 1:1 맞춤 코칭")
    
    # 탭별 프롬프트 세팅
    if mode == "⏱️ 갓생(God-생) 루틴 메이커":
        sys_prompt = f"""
        너는 데이터 기반으로 팩트 폭격을 하는 엄격하고 다정한 루틴 코치야. 
        사용자의 현재 상황:
        - 오늘의 컨디션: {condition}
        - 오늘 시간 배분: 수면 {sleep_h}시간, 업무 {work_h}시간, 공부 {study_h}시간, 휴식 {rest_h}시간.
        
        이 데이터를 바탕으로 수면 시간이 불규칙한지, 컨디션 저하 패턴이 있는지 팩트 폭격을 해주고, 휴식이나 다음 학습 스텝을 제안해 줘.
        """
        greeting = f"안녕하세요 안태경 님! 오늘 컨디션은 '{condition}' 상태시군요. 좌측에 입력하신 시간 배분과 과거 성취도 데이터를 분석해 드릴까요?"
    else:
        max_expense = edited_df.loc[edited_df["금액"].idxmax()]["카테고리"]
        sys_prompt = f"너는 엄격한 재무 상담가야. 사용자가 이번 주 '{max_expense}'에 가장 많은 돈을 썼어. 내일 당장 실천할 구체적인 절약 미션을 던져줘."
        greeting = f"재무 상담가입니다. 현재 저축률을 {save_ratio}%로 설정하셨네요! 이번 주 지출 내역을 바탕으로 뼈 때리는 절약 미션을 받아보시겠어요?"

    # 모드 변경 시 채팅 초기화
    if "current_mode" not in st.session_state or st.session_state.current_mode != mode:
        st.session_state.messages = [{"role": "assistant", "content": greeting}]
        st.session_state.current_mode = mode

    # 채팅 메시지 출력
    chat_container = st.container(height=550)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # 채팅 입력창 (누락되었던 부분)
    user_input = st.chat_input("AI 코치에게 질문하기...")
    
    if user_input:
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.chat_message("assistant"):
                prompt = f"{sys_prompt}\n\n사용자 질문: {user_input}"
                response = model.generate_content(prompt)
                st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
