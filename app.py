import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import numpy as np
import plotly.express as px  # 폰트 깨짐 방지를 위해 matplotlib 대신 plotly 사용
import time

# ----------------------------------------------------------------------
# 1. 페이지 기본 설정
# ----------------------------------------------------------------------
st.set_page_config(page_title="SKHynix 성장 파트너", page_icon="🚀", layout="wide")

# ----------------------------------------------------------------------
# 2. API 키 설정
# ----------------------------------------------------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.5-flash')
except:
    st.error("API 키가 설정되지 않았습니다.")

# ----------------------------------------------------------------------
# 3. 날짜 및 D-Day 계산 로직
# ----------------------------------------------------------------------
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst)
today = now.date()

join_date = date(2026, 7, 1)
d_day_join = (join_date - today).days
join_str = f"D-{d_day_join}" if d_day_join > 0 else (f"D+{-d_day_join}" if d_day_join < 0 else "D-Day (입사일! 🎉)")

year, month = today.year, today.month
payday = date(year, month, 25)
if today > payday:
    month = month + 1 if month < 12 else 1
    year = year + 1 if month == 1 else year
    payday = date(year, month, 25)

if payday.weekday() == 5: payday -= timedelta(days=1)
elif payday.weekday() == 6: payday -= timedelta(days=2)
d_day_pay = (payday - today).days
pay_str = f"D-{d_day_pay}" if d_day_pay > 0 else "D-Day (월급날! 💸)"

# ----------------------------------------------------------------------
# 4. 사이드바 구성
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("🏢 SKHynix 성장 파트너")
    st.markdown("### 👤 Profile\n**Name:** 안태경\n\n**Team:** 양산기술")
    st.info(f"**입사일:** {join_str}\n\n**월급날:** {pay_str}")
    
    if 'log_data' not in st.session_state:
        st.session_state.log_data = pd.DataFrame(columns=['날짜', '시간대', '컨디션', '성취도'])
    
    mode = st.radio("이동할 탭을 선택하세요:", ["⏱️ 갓생(God-생) 루틴 메이커", "💰 스마트 재무/소비 관리"])

# ----------------------------------------------------------------------
# 5. 메인 화면 로직
# ----------------------------------------------------------------------
st.title(f"{mode}")
col_visual, col_chat = st.columns([6, 4])

with col_visual:
    if mode == "⏱️ 갓생(God-생) 루틴 메이커":
        st.subheader("📊 24시간 타임블록 설계")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1: s = st.slider("수면", 0.0, 24.0, 7.0, 0.5)
        with col_s2: w = st.slider("업무/학습", 0.0, 24.0, 9.0, 0.5)
        with col_s3: st_h = st.slider("자기계발", 0.0, 24.0, 2.0, 0.5)
        r = 24.0 - (s + w + st_h)
        
        # Plotly 파이 차트 (폰트 깨짐 없음)
        df_time = pd.DataFrame({
            '활동': [f'수면({s}시간)', f'업무/학습({w}시간)', f'자기계발({st_h}시간)', f'휴식({r:.1f}시간)'],
            '시간': [s, w, st_h, r]
        })
        fig = px.pie(df_time, values='시간', names='활동', title="일일 시간 배분")
        st.plotly_chart(fig)

        st.markdown("---")
        st.subheader("🧠 감정-성취도 기록 및 분석")
        ts = st.selectbox("시간대", ["아침", "점심", "저녁"])
        cond_map = {"피곤해요": 0, "그저 그래요": 50, "최고예요": 100}
        cond_val = st.select_slider("컨디션 지수", options=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        achieve = st.slider("성취도 (%)", 0, 100, 50)
        
        if st.button("기록 저장"):
            new_entry = pd.DataFrame({'날짜': [today], '시간대': [ts], '컨디션': [cond_val], '성취도': [achieve]})
            st.session_state.log_data = pd.concat([st.session_state.log_data, new_entry], ignore_index=True)

        if not st.session_state.log_data.empty:
            df = st.session_state.log_data
            st.line_chart(df[['컨디션', '성취도']])
            st.bar_chart(df.groupby('시간대')[['컨디션', '성취도']].mean())
            
    elif mode == "💰 스마트 재무/소비 관리":
        st.subheader("📈 첫 월급 황금비율 시뮬레이터")
        save_ratio = st.slider("첫 월급 저축 비율 (%)", 0, 100, 50)
        st.bar_chart(pd.DataFrame([save_ratio, 100-save_ratio], index=["저축", "소비"], columns=["비율"]))

# 채팅창은 기존 베이스 코드 유지
with col_chat:
    st.subheader("💬 AI 1:1 맞춤 코칭")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "분석할 데이터가 있으면 질문해 주세요!"}]
    chat_container = st.container(height=550)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
    if user_input := st.chat_input("AI 코치에게 질문하기..."):
        with chat_container:
            with st.chat_message("user"): st.write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("assistant"):
                prompt = f"데이터: {st.session_state.log_data.tail(5).to_string()}\n질문: {user_input}"
                response = model.generate_content(prompt)
                st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
