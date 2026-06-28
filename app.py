import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import numpy as np
import plotly.express as px
import time

# ----------------------------------------------------------------------
# 1. 페이지 기본 설정
# ----------------------------------------------------------------------
st.set_page_config(page_title="SKHynix 성장 파트너", page_icon="🚀", layout="wide")

# ----------------------------------------------------------------------
# 2. API 키 설정 (Streamlit Secrets)
# ----------------------------------------------------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.5-flash')
except:
    st.error("API 키가 설정되지 않았습니다. Streamlit Secrets를 확인해주세요.")

# ----------------------------------------------------------------------
# 3. 날짜 및 D-Day 계산 로직 (KST 기준)
# ----------------------------------------------------------------------
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst)
today = now.date()

# [입사일 D-Day 계산] - 2026년 7월 1일
join_date = date(2026, 7, 1)
d_day_join = (join_date - today).days
join_str = f"D-{d_day_join}" if d_day_join > 0 else (f"D+{-d_day_join}" if d_day_join < 0 else "D-Day (입사일! 🎉)")

# [월급날 D-Day 계산] - 매달 25일 (주말 보정)
year, month = today.year, today.month
payday = date(year, month, 25)

if today > payday:
    month = month + 1 if month < 12 else 1
    year = year + 1 if month == 1 else year
    payday = date(year, month, 25)

if payday.weekday() == 5: # 토요일
    payday -= timedelta(days=1)
elif payday.weekday() == 6: # 일요일
    payday -= timedelta(days=2)

d_day_pay = (payday - today).days
pay_str = f"D-{d_day_pay}" if d_day_pay > 0 else "D-Day (월급날! 💸)"

# ----------------------------------------------------------------------
# 4. 사이드바 구성 (프로필 및 전역 데이터)
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("🏢 SKHynix 성장 파트너")
    st.markdown("---")
    st.markdown("### 👤 Profile\n**Name:** 안태경\n\n**Team:** 양산기술")
    st.markdown("---")
    st.markdown("### ⏳ D-Day\n")
    st.info(f"**입사일:** {join_str}\n\n**월급날:** {pay_str}")
    st.markdown("---")
    
    st.markdown("### 🌡️ 오늘의 컨디션")
    condition = st.radio("현재 기분이 어떠신가요?", ["😀 최고예요!", "😐 그저 그래요", "😥 피곤해요"], horizontal=True)
    
    st.markdown("---")
    st.markdown("### 🎯 메뉴 선택")
    mode = st.radio("이동할 탭을 선택하세요:", 
                    ["⏱️ 갓생(God-생) 루틴 메이커", 
                     "💰 스마트 재무/소비 관리"])

# ----------------------------------------------------------------------
# 5. 메인 화면 로직 (2분할 레이아웃 적용)
# ----------------------------------------------------------------------
st.title(f"{mode}")
col_visual, col_chat = st.columns([6, 4])

# ==========================================
# [왼쪽 영역] 탭별 데이터 시각화 및 대시보드
# ==========================================
with col_visual:
    # ---------------------------------------------------
    # 탭 1: 갓생 루틴 메이커 (레이아웃 높이 최종 정렬)
    # ---------------------------------------------------
    if mode == "⏱️ 갓생(God-생) 루틴 메이커":
        st.subheader("📊 24시간 타임블록 설계")
        
        # 1. 차트 영역 (좌우 2열 배치)
        col_left, col_right = st.columns(2)
        
        # [왼쪽: 통계 분석]
        with col_left:
            st.markdown("#### 📉 통계 분석")
            period = st.selectbox("기간 단위", ["요일별", "월별"], key="stat_period")
            val = st.selectbox("항목 선택", ["월", "화", "수", "목", "금", "토", "일"] if period == "요일별" else range(1, 13), key="stat_val")
            
            data = [6.5, 9.5, 2.5, 5.5]
            fig_stat = px.pie(values=data, names=['수면', '업무', '자기계발', '휴식'], title="평균 데이터")
            fig_stat.update_layout(height=350, margin=dict(t=50, b=0, l=0, r=0))
            st.plotly_chart(fig_stat, use_container_width=True)

        # [오른쪽: 오늘의 계획]
        with col_right:
            st.markdown("#### 📅 오늘의 계획")
            
            # 슬라이더 영역 (오른쪽 차트 바로 위)
            c1, c2, c3 = st.columns(3)
            with c1: sleep_h = st.slider("수면", 0.0, 24.0, 7.0, 0.5)
            with c2: work_h = st.slider("업무", 0.0, 24.0, 9.0, 0.5)
            with c3: study_h = st.slider("자기계발", 0.0, 24.0, 2.0, 0.5)
            rest_h = 24.0 - (sleep_h + work_h + study_h)
            
            # 왼쪽의 셀렉트박스 2개(약 120px) 높이만큼 여백 확보
            st.write("") 
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            
            if rest_h < 0:
                st.error("시간 합계 초과!")
            else:
                df_today = pd.DataFrame({'활동': ['수면', '업무', '자기계발', '휴식'], '시간': [sleep_h, work_h, study_h, rest_h]})
                fig_today = px.pie(df_today, values='시간', names='활동', title="현재 타임블록")
                fig_today.update_layout(height=350, margin=dict(t=50, b=0, l=0, r=0))
                st.plotly_chart(fig_today, use_container_width=True)
        
        st.markdown("---")

        # 2. 감정-컨디션 상관관계 분석기 (Plotly 사용)
        st.subheader("🧠 감정-성취도 상관관계 분석")
        st.write(f"오늘 안태경 님의 컨디션은 **'{condition}'** 입니다.")
        
        dates = pd.date_range(end=today, periods=14)
        condition_scores = np.random.randint(1, 4, size=14)
        achievement = condition_scores * 25 + np.random.randint(-10, 10, size=14) 
        
        df_insight = pd.DataFrame({
            "날짜": dates,
            "컨디션": condition_scores * 30,
            "성취도": achievement
        })
        st.line_chart(df_insight.set_index("날짜"))
        
        st.markdown("---")

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

    chat_container = st.container(height=550)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # # 뽀모도로 완료 버튼을 눌렀을 때 자동 채팅 트리거
    # user_input = st.chat_input("AI 코치에게 질문하기...")
    
    # if getattr(st.session_state, 'pomodoro_done', False):
    #     user_input = "나 방금 뽀모도로 25분 집중 완료했어! 성취도 리포트랑 다정한 칭찬 멘트, 그리고 다음 스텝 추천해 줘."
    #     st.session_state.pomodoro_done = False # 한 번 실행 후 초기화

    # if user_input:
    #     with chat_container:
    #         with st.chat_message("user"):
    #             st.write(user_input)
    #         st.session_state.messages.append({"role": "user", "content": user_input})
            
    #         with st.chat_message("assistant"):
    #             prompt = f"{sys_prompt}\n\n사용자 질문: {user_input}"
    #             response = model.generate_content(prompt)
    #             st.write(response.text)
    #         st.session_state.messages.append({"role": "assistant", "content": response.text})
