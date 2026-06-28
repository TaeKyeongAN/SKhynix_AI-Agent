import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# ----------------------------------------------------------------------
# 1. 페이지 기본 설정
# ----------------------------------------------------------------------
st.set_page_config(page_title="SKHynix 갓생 매니저", page_icon="🚀", layout="wide")

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
    st.header("🏢 SKHynix 갓생 매니저")
    st.markdown("---")
    st.markdown("### 👤 Profile\n**Name:** 안태경\n\n**Team:** 양산기술")
    st.markdown("---")
    st.markdown("### ⏳ D-Day\n")
    st.info(f"**입사일:** {join_str}\n\n**월급날:** {pay_str}")
    st.markdown("---")
    
    # 💡 탭 3(인사이트)에서 활용될 핵심 전역 데이터
    st.markdown("### 🌡️ 오늘의 컨디션")
    condition = st.radio("현재 기분이 어떠신가요?", ["😀 최고예요!", "😐 그저 그래요", "😥 피곤해요"], horizontal=True)
    
    st.markdown("---")
    st.markdown("### 🎯 메뉴 선택")
    mode = st.radio("이동할 탭을 선택하세요:", 
                    ["⏱️ 타임블록 & 뽀모도로", 
                     "💰 첫 월급 & 소비 분석", 
                     "📊 멘탈-달성률 대시보드"])

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
    # 탭 1: 시간 관리
    # ---------------------------------------------------
    if mode == "⏱️ 타임블록 & 뽀모도로":
        st.subheader("📊 24시간 타임블록 설계")
        
        # 시간 입력 슬라이더
        sleep_h = st.slider("수면 시간 (시간)", 0, 24, 7)
        work_h = st.slider("업무/학습 시간 (시간)", 0, 24, 9)
        study_h = st.slider("자기계발 시간 (시간)", 0, 24, 2)
        rest_h = 24 - (sleep_h + work_h + study_h)
        
        if rest_h < 0:
            st.error("총합이 24시간을 초과했습니다! 슬라이더를 조절해주세요.")
        else:
            # 파이 차트 시각화 (matplotlib)
            fig, ax = plt.subplots(figsize=(6, 3))
            labels = ['Sleep', 'Work/Study', 'Self-Dev', 'Rest']
            sizes = [sleep_h, work_h, study_h, rest_h]
            colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
            
        st.markdown("---")
        st.subheader("🍅 뽀모도로 집중 타이머")
        if st.button("25분 집중 시작하기!"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            # 시연을 위해 1초를 1분처럼 작동하게 세팅 (실제론 25*60)
            for i in range(100):
                time.sleep(0.05) # 시연용 (빠르게 슉 지나감)
                progress_bar.progress(i + 1)
                status_text.text(f"집중 중... {i+1}% 완료")
            st.success("🎉 25분 집중 완료! AI 코치에게 칭찬을 요구해보세요.")

    # ---------------------------------------------------
    # 탭 2: 재무 관리
    # ---------------------------------------------------
    elif mode == "💰 첫 월급 & 소비 분석":
        st.subheader("📈 미래 자산 시뮬레이터")
        save_ratio = st.slider("첫 월급 저축 비율 (%)", 0, 100, 50)
        
        # 복리 계산 (가상: 월급 300만 원, 연이율 5% 가정)
        base_salary = 3000000
        monthly_save = base_salary * (save_ratio / 100)
        years = [1, 3, 5]
        assets = [monthly_save * 12 * y * 1.05 for y in years]
        
        chart_data = pd.DataFrame({"예상 자산(원)": assets}, index=["1년 뒤", "3년 뒤", "5년 뒤"])
        st.bar_chart(chart_data)
        
        st.markdown("---")
        st.subheader("💸 이번 주 소비 내역 입력")
        # 편집 가능한 데이터프레임
        df_expenses = pd.DataFrame([
            {"카테고리": "식비(배달 포함)", "금액": 150000},
            {"카테고리": "교통비", "금액": 30000},
            {"카테고리": "쇼핑/자기계발", "금액": 50000},
            {"카테고리": "기타", "금액": 20000}
        ])
        edited_df = st.data_editor(df_expenses, num_rows="dynamic")
        
        # 소비 데이터 차트화
        st.write("카테고리별 지출 비율")
        st.bar_chart(edited_df.set_index("카테고리"))

    # ---------------------------------------------------
    # 탭 3: 통합 인사이트 (컨디션+달성률)
    # ---------------------------------------------------
    elif mode == "📊 멘탈-달성률 대시보드":
        st.subheader("🧠 컨디션 기반 퍼포먼스 분석")
        st.write(f"오늘 안태경 님의 컨디션은 **'{condition}'** 입니다.")
        
        # 한 달 치 가상 더미 데이터 생성
        dates = pd.date_range(end=today, periods=14)
        # 컨디션(1~3)과 목표달성률(%)의 상관관계를 보여주는 가상 데이터
        condition_scores = np.random.randint(1, 4, size=14)
        achievement = condition_scores * 25 + np.random.randint(-10, 10, size=14) 
        
        df_insight = pd.DataFrame({
            "날짜": dates,
            "컨디션 지수 (높을수록 좋음)": condition_scores * 30, # 스케일 맞추기
            "루틴 달성률 (%)": achievement
        }).set_index("날짜")
        
        st.line_chart(df_insight)
        st.info("💡 과거 데이터를 보면, 컨디션 지수가 떨어지는 날 목표 달성률도 급격히 하락하는 패턴이 있습니다.")

# ==========================================
# [오른쪽 영역] AI 에이전트 채팅
# ==========================================
with col_chat:
    st.subheader("💬 맞춤형 AI 코칭")
    
    # 탭별 프롬프트 및 환영 메시지 동적 생성
    if mode == "⏱️ 타임블록 & 뽀모도로":
        sys_prompt = f"너는 팩트폭격을 하는 루틴 코치야. 사용자의 오늘 계획은 수면 {sleep_h}시간, 업무 {work_h}시간, 공부 {study_h}시간이야. 이 밸런스를 평가하고 뼈때리는 조언을 해줘."
        greeting = f"안태경님, 오늘 남은 휴식 시간은 {rest_h}시간이군요. 이대로 괜찮은지 밸런스를 점검해 드릴까요?"
    elif mode == "💰 첫 월급 & 소비 분석":
        max_expense = edited_df.loc[edited_df["금액"].idxmax()]["카테고리"]
        sys_prompt = f"너는 엄격한 재무 상담가야. 사용자가 이번 주 '{max_expense}'에 가장 많은 돈을 썼어. 내일 당장 실천할 구체적인 절약 미션을 줘."
        greeting = f"재무 상담가입니다. 현재 저축률을 {save_ratio}%로 설정하셨네요! 이번 주 지출을 바탕으로 절약 미션을 받아보시겠어요?"
    else:
        sys_prompt = f"너는 심리와 데이터를 종합 분석하는 코치야. 사용자의 현재 컨디션은 '{condition}'야. 이 컨디션일 때 발생할 수 있는 리스크를 막기 위한 조언 3가지를 정리해 줘."
        greeting = f"수석 분석 코치입니다. 오늘 컨디션이 '{condition}' 상태시군요. 이런 날을 위한 맞춤형 루틴 방어 전략을 세워드릴까요?"

    # 모드 변경 시 채팅 초기화 및 환영 메시지 삽입
    if "current_mode" not in st.session_state or st.session_state.current_mode != mode:
        st.session_state.messages = [{"role": "assistant", "content": greeting}]
        st.session_state.current_mode = mode

    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # 채팅 입력 및 AI 응답
    if user_input := st.chat_input("AI 코치에게 질문하기..."):
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.chat_message("assistant"):
                prompt = f"{sys_prompt}\n\n사용자 질문: {user_input}"
                response = model.generate_content(prompt)
                st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
