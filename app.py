import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Matplotlib 한글 폰트 설정 (기본 폰트 사용 또는 환경에 맞춰 설정 필요)
plt.rcParams['font.family'] = 'sans-serif' 

st.set_page_config(page_title="SKHynix 성장 파트너", page_icon="🚀", layout="wide")

# API 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.5-flash')
except:
    st.error("API 키가 설정되지 않았습니다.")

# 날짜 로직
kst = pytz.timezone('Asia/Seoul')
today = datetime.now(kst).date()

# 사이드바
with st.sidebar:
    st.header("🏢 SKHynix 성장 파트너")
    mode = st.radio("메뉴 선택:", ["⏱️ 갓생 루틴 메이커", "💰 스마트 재무 관리"])

# 세션 상태 초기화 (데이터 저장용)
if 'log_data' not in st.session_state:
    st.session_state.log_data = pd.DataFrame(columns=['시간대', '컨디션', '성취도'])

# 메인 화면
st.title(f"{mode}")
col_visual, col_chat = st.columns([6, 4])

with col_visual:
    if mode == "⏱️ 갓생 루틴 메이커":
        st.subheader("📊 24시간 타임블록 설계")
        c1, c2, c3 = st.columns(3)
        with c1: s = st.slider("수면", 0.0, 24.0, 7.0, 0.5)
        with c2: w = st.slider("업무/학습", 0.0, 24.0, 9.0, 0.5)
        with c3: st_h = st.slider("자기계발", 0.0, 24.0, 2.0, 0.5)
        r = 24.0 - (s + w + st_h)
        
        fig, ax = plt.subplots(figsize=(5,3))
        ax.pie([s, w, st_h, r], labels=[f'수면({s}시간)', f'업무({w}시간)', f'자기계발({st_h}시간)', f'휴식({r}시간)'], autopct='%1.1f%%')
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("🧠 컨디션 및 성취도 기록")
        time_slot = st.selectbox("시간대", ["아침", "점심", "저녁"])
        cond = st.select_slider("컨디션(0=피곤, 50=보통, 100=최고)", options=range(0, 101, 10))
        achieve = st.slider("성취도(%)", 0, 100, 50)
        
        if st.button("기록 저장"):
            new_row = pd.DataFrame({'시간대': [time_slot], '컨디션': [cond], '성취도': [achieve]})
            st.session_state.log_data = pd.concat([st.session_state.log_data, new_row], ignore_index=True)

        if not st.session_state.log_data.empty:
            st.write("📈 분석 결과")
            df = st.session_state.log_data
            # 1. 하루 변화(라인)
            st.line_chart(df[['컨디션', '성취도']])
            # 2. 요일/시간별 평균(바)
            st.bar_chart(df.groupby('시간대')[['컨디션', '성취도']].mean())
            # 3. 상관관계(산점도)
            fig2, ax2 = plt.subplots()
            ax2.scatter(df['컨디션'], df['성취도'])
            st.pyplot(fig2)

    elif mode == "💰 스마트 재무 관리":
        st.subheader("📈 자산 시뮬레이터")
        ratio = st.slider("저축 비율(%)", 0, 100, 50)
        st.bar_chart(pd.DataFrame([ratio, 100-ratio], index=["저축", "소비"], columns=["비율"]))

with col_chat:
    st.subheader("💬 AI 1:1 맞춤 코칭")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 컨디션과 루틴 데이터를 기반으로 코칭해 드립니다."}]
    
    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
    
    if user_input := st.chat_input("질문을 입력하세요..."):
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            prompt = f"데이터: {st.session_state.log_data.tail(5).to_string()}\n질문: {user_input}"
            with st.chat_message("assistant"):
                response = model.generate_content(prompt)
                st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
