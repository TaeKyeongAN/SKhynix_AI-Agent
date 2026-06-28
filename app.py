import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# 1. 페이지 설정
st.set_page_config(page_title="SKHynix 성장 파트너", page_icon="🚀", layout="wide")

# 2. API 키 설정 (Streamlit Secrets 필요)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.5-flash')
except:
    st.error("API 키가 설정되지 않았습니다.")

# 3. 데이터 로직 (날짜/D-Day)
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst)
today = now.date()
join_date = date(2026, 7, 1)
d_day_join = (join_date - today).days

# 4. 사이드바 구성 (여기에 채팅창을 고정함)
with st.sidebar:
    st.header("💬 AI 1:1 맞춤 코칭")
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 궁금한 점을 물어보세요."}]
    
    # 채팅창 컨테이너 고정 (스크롤해도 따라옴)
    chat_container = st.container(height=500)
    
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
    user_input = st.chat_input("AI 코치에게 질문하기...")
    
    if user_input:
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.chat_message("assistant"):
                response = model.generate_content(user_input)
                st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    st.markdown("---")
    st.info(f"**입사까지 남은 시간:** D-{d_day_join}")

# 5. 메인 화면 (좌측 100% 활용)
st.title("⏱️ 갓생(God-생) 루틴 메이커")
st.subheader("📊 24시간 타임블록 설계")

col1, col2, col3 = st.columns(3)
with col1: sleep_h = st.slider("수면 시간", 0, 24, 7)
with col2: work_h = st.slider("업무/학습", 0, 24, 9)
with col3: study_h = st.slider("자기계발", 0, 24, 2)

rest_h = 24 - (sleep_h + work_h + study_h)

fig, ax = plt.subplots(figsize=(6, 3))
ax.pie([sleep_h, work_h, study_h, rest_h], labels=['Sleep', 'Work', 'Study', 'Rest'], autopct='%1.1f%%')
st.pyplot(fig)

st.subheader("📈 감정-성취도 상관관계")
df = pd.DataFrame(np.random.randn(20, 2), columns=['컨디션', '성취도'])
st.line_chart(df)

st.write("스크롤을 내려보세요! 오른쪽 채팅창(사이드바)은 항상 고정되어 있습니다.")
for i in range(10): st.write(f"테스트 데이터 {i}번: 대시보드 내용이 길어질 경우 여기 스크롤이 생깁니다.")
