import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

import matplotlib.font_manager as fm
# 한글 폰트 설정 (시스템에 설치된 폰트 활용)
# Streamlit Cloud 환경이나 일반 Linux 환경에서 가장 흔히 사용되는 폰트들을 후보로 지정합니다.
font_list = ['NanumGothic', 'Malgun Gothic', 'AppleGothic', 'AppleGothic.ttf']

for font_name in font_list:
    try:
        plt.rcParams['font.family'] = font_name
        # 폰트가 적용되었는지 확인 (에러가 안 나면 성공)
        plt.title('테스트')
        break
    except:
        continue

# ----------------------------------------------------------------------
# 1. 페이지 기본 설정
# ----------------------------------------------------------------------
st.set_page_config(page_title="SKHynix 성장 파트너", page_icon="🚀", layout="wide")

# Matplotlib 한글 폰트 설정 (환경에 따라 'Malgun Gothic' 등 설정 필요)
plt.rcParams['font.family'] = 'sans-serif'

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
    
    # 세션 상태에 데이터 저장소 초기화
    if 'log_data' not in st.session_state:
        st.session_state.log_data = pd.DataFrame(columns=['날짜', '시간대', '컨디션', '성취도'])
    
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
    # 탭 1: 갓생 루틴 메이커
    # ---------------------------------------------------
    if mode == "⏱️ 갓생(God-생) 루틴 메이커":
        
        # 1. 24시간 타임블록 (0.5단위, 한글 라벨, (시간) 추가)
        st.subheader("📊 24시간 타임블록 설계")
        col_slider1, col_slider2, col_slider3 = st.columns(3)
        with col_slider1: sleep_h = st.slider("수면 시간", 0.0, 24.0, 7.0, 0.5)
        with col_slider2: work_h = st.slider("업무/학습", 0.0, 24.0, 9.0, 0.5)
        with col_slider3: study_h = st.slider("자기계발", 0.0, 24.0, 2.0, 0.5)
        rest_h = 24.0 - (sleep_h + work_h + study_h)
        
        if rest_h < 0:
            st.error("총합이 24시간을 초과했습니다! 슬라이더를 조절해주세요.")
        else:
            fig, ax = plt.subplots(figsize=(6, 3))
            labels = [f'수면({sleep_h}시간)', f'업무/학습({work_h}시간)', f'자기계발({study_h}시간)', f'휴식({rest_h:.1f}시간)']
            sizes = [sleep_h, work_h, study_h, rest_h]
            colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

        st.markdown("---")
        
        # 2. 감정-컨디션 상관관계 분석기 (하루 3회, 0~100점 선택)
        st.subheader("🧠 감정-성취도 상관관계 분석")
        
        time_slot = st.selectbox("시간대 선택", ["아침", "점심", "저녁"])
        cond_map = {"피곤해요": 0, "그저 그래요": 50, "최고예요": 100}
        cond_label = st.select_slider("컨디션 지수", options=["피곤해요", "그저 그래요", "최고예요"])
        achieve = st.slider("일일 성취도 (%)", 0, 100, 50)
        
        if st.button("기록 저장"):
            new_entry = pd.DataFrame({'날짜': [today], '시간대': [time_slot], '컨디션': [cond_map[cond_label]], '성취도': [achieve]})
            st.session_state.log_data = pd.concat([st.session_state.log_data, new_entry], ignore_index=True)
            st.success(f"{time_slot} 기록 완료!")

        # 분석 차트들
        if not st.session_state.log_data.empty:
            df = st.session_state.log_data
            
            # 하루 평균 컨디션 등 분석
            st.write("📊 분석 차트")
            st.line_chart(df[['컨디션', '성취도']])
            st.bar_chart(df.groupby('날짜')[['컨디션', '성취도']].mean())
            
            fig2, ax2 = plt.subplots()
            ax2.scatter(df['컨디션'], df['성취도'])
            ax2.set_xlabel("컨디션")
            ax2.set_ylabel("성취도")
            st.pyplot(fig2)

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
    
    if mode == "⏱️ 갓생(God-생) 루틴 메이커":
        sys_prompt = "너는 데이터 기반의 루틴 코치야. 기록된 컨디션과 성취도 데이터를 분석해줘."
        greeting = "안녕하세요! 컨디션과 성취도를 기록하고 분석을 요청해 보세요."
    else:
        sys_prompt = "너는 엄격한 재무 상담가야."
        greeting = "재무 상담가입니다. 지출 내역을 분석해 드릴까요?"

    if "current_mode" not in st.session_state or st.session_state.current_mode != mode:
        st.session_state.messages = [{"role": "assistant", "content": greeting}]
        st.session_state.current_mode = mode

    chat_container = st.container(height=550)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    if user_input := st.chat_input("AI 코치에게 질문하기..."):
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # AI 응답 로직
            prompt = f"{sys_prompt}\n\n데이터: {st.session_state.log_data.tail(5).to_string()}\n질문: {user_input}"
            with st.chat_message("assistant"):
                response = model.generate_content(prompt)
                st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
