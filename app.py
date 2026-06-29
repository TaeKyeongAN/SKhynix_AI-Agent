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

# ----------------------------------------------------------------------
# 5. 메인 화면 로직 (탭 기반 1기능-1채팅 레이아웃)
# ----------------------------------------------------------------------
st.title("🚀 SKHynix AI 성장 파트너 대시보드")

# 기능별로 탭 생성
tab1, tab2, tab3 = st.tabs(["⏱️ 24시간 타임블록 설계", "🧠 감정-성취도 분석", "💰 스마트 재무/소비 관리"])

# ==========================================
# 탭 1: 갓생 루틴 메이커 (타임블록)
# ==========================================
with tab1:
    col_vis1, col_chat1 = st.columns([6, 4])
    
    with col_vis1:
        st.subheader("📊 24시간 타임블록 설계")
        color_map = {'수면': '#3498db', '업무': '#e74c3c', '자기계발': '#f1c40f', '휴식': '#2ecc71'}
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### 📉 통계 분석")
            period = st.selectbox("기간 단위", ["요일별", "월별"], key="stat_period")
            if period == "요일별":
                options_display = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
                val = st.selectbox("항목 선택", options_display, key="stat_val")
                display_title = f"{val} 데이터"
                day_key = val[0] 
                base_data = {
                    "월": [7, 10, 2, 5], "화": [7, 9, 2, 6], "수": [7, 9, 2, 6], 
                    "목": [7, 9, 2, 6], "금": [7, 8, 2, 7], "토": [8, 2, 6, 8], "일": [9, 1, 6, 8]
                }
                data_values = base_data.get(day_key, [7, 8, 2, 7])
            else:
                options_display = [f"{i}월" for i in range(1, 13)]
                val = st.selectbox("항목 선택", options_display, key="stat_val2")
                display_title = f"{val} 데이터"
                month_num = int(val.replace("월", ""))
                if month_num in [6, 7, 8]: data_values = [7, 7, 3, 7]
                elif month_num == 12: data_values = [6, 11, 4, 3]
                else: data_values = [7, 9, 2, 6]
            
            df_stat = pd.DataFrame({'활동': ['수면', '업무', '자기계발', '휴식'], '시간': data_values})
            fig_stat = px.pie(df_stat, values='시간', names='활동', title=f"{display_title}", color='활동', color_discrete_map=color_map)
            fig_stat.update_layout(height=350, margin=dict(t=50, b=0, l=0, r=0))
            st.plotly_chart(fig_stat, use_container_width=True)

        with col_right:
            st.markdown("#### 📅 오늘의 계획")
            c1, c2, c3 = st.columns(3)
            with c1: sleep_h = st.slider("수면", 0.0, 24.0, 7.0, 0.5, key="sl1")
            with c2: work_h = st.slider("업무", 0.0, 24.0, 9.0, 0.5, key="wk1")
            with c3: study_h = st.slider("자기계발", 0.0, 24.0, 2.0, 0.5, key="st1")
            rest_h = 24.0 - (sleep_h + work_h + study_h)
            
            st.write("") 
            st.write("")
            st.write("")
            st.write("")
            st.write("")
                        
            if rest_h < 0:
                st.error("시간 합계 초과!")
            else:
                df_today = pd.DataFrame({'활동': ['수면', '업무', '자기계발', '휴식'], '시간': [sleep_h, work_h, study_h, rest_h]})
                fig_today = px.pie(df_today, values='시간', names='활동', title="현재 타임블록", color='활동', color_discrete_map=color_map)
                fig_today.update_layout(height=350, margin=dict(t=50, b=0, l=0, r=0))
                st.plotly_chart(fig_today, use_container_width=True)
                
    with col_chat1:
        st.subheader("💬 타임블록 맞춤 코칭")
        sys_prompt_1 = f"너는 엄격하고 다정한 루틴 코치야. 현재 상황: 컨디션 '{condition}', 오늘 시간 배분: 수면 {sleep_h}시간, 업무 {work_h}시간, 공부 {study_h}시간, 휴식 {rest_h}시간. 이 데이터를 바탕으로 팩트 폭격을 해주고 조언을 제안해."
        greeting_1 = f"안녕하세요 안태경 님! 오늘 '{condition}' 상태시군요. 좌측의 시간 배분 데이터를 분석해 드릴까요?"
        
        if "messages_1" not in st.session_state:
            st.session_state.messages_1 = [{"role": "assistant", "content": greeting_1}]
            
        chat_container_1 = st.container(height=550)
        with chat_container_1:
            for msg in st.session_state.messages_1:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
        user_input_1 = st.chat_input("타임블록에 대해 질문하기...", key="chat_in_1")
        if user_input_1:
            with chat_container_1:
                with st.chat_message("user"): st.write(user_input_1)
                st.session_state.messages_1.append({"role": "user", "content": user_input_1})
                with st.chat_message("assistant"):
                    response_1 = model.generate_content(f"{sys_prompt_1}\n\n사용자 질문: {user_input_1}")
                    st.write(response_1.text)
                st.session_state.messages_1.append({"role": "assistant", "content": response_1.text})

# ==========================================
# 탭 2: 감정-성취도 상관관계 분석
# ==========================================
with tab2:
    col_vis2, col_chat2 = st.columns([6, 4])
    
    with col_vis2:
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

    with col_chat2:
        st.subheader("💬 멘탈/성취도 맞춤 코칭")
        sys_prompt_2 = f"너는 직장인의 멘탈과 성취도를 관리해주는 따뜻한 상담가야. 사용자의 오늘 컨디션은 '{condition}'이야. 이를 바탕으로 멘탈 관리법이나 성취도 향상 팁을 제공해줘."
        greeting_2 = f"오늘 컨디션이 '{condition}'이시네요. 최근 2주간의 감정과 성취도 흐름에 대해 이야기 나눠볼까요?"
        
        if "messages_2" not in st.session_state:
            st.session_state.messages_2 = [{"role": "assistant", "content": greeting_2}]
            
        chat_container_2 = st.container(height=550)
        with chat_container_2:
            for msg in st.session_state.messages_2:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
        user_input_2 = st.chat_input("감정이나 성취도에 대해 질문하기...", key="chat_in_2")
        if user_input_2:
            with chat_container_2:
                with st.chat_message("user"): st.write(user_input_2)
                st.session_state.messages_2.append({"role": "user", "content": user_input_2})
                with st.chat_message("assistant"):
                    response_2 = model.generate_content(f"{sys_prompt_2}\n\n사용자 질문: {user_input_2}")
                    st.write(response_2.text)
                st.session_state.messages_2.append({"role": "assistant", "content": response_2.text})

# ==========================================
# 탭 3: 스마트 재무/소비 관리
# ==========================================
with tab3:
    col_vis3, col_chat3 = st.columns([6, 4])
    
    with col_vis3:
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
        edited_df = st.data_editor(df_expenses, num_rows="dynamic", key="expense_editor")
        st.bar_chart(edited_df.set_index("카테고리"))

    with col_chat3:
        st.subheader("💬 재무/소비 맞춤 코칭")
        max_expense = edited_df.loc[edited_df["금액"].idxmax()]["카테고리"]
        sys_prompt_3 = f"너는 엄격한 재무 상담가야. 사용자가 이번 주 '{max_expense}'에 가장 많은 돈을 썼고 저축률을 {save_ratio}%로 설정했어. 구체적인 절약 미션을 던져줘."
        greeting_3 = f"재무 상담가입니다. 현재 저축률을 {save_ratio}%로 설정하셨네요! 이번 주 지출 내역을 바탕으로 뼈 때리는 절약 미션을 받아보시겠어요?"
        
        if "messages_3" not in st.session_state:
            st.session_state.messages_3 = [{"role": "assistant", "content": greeting_3}]
            
        chat_container_3 = st.container(height=550)
        with chat_container_3:
            for msg in st.session_state.messages_3:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
        user_input_3 = st.chat_input("재무/지출 관리에 대해 질문하기...", key="chat_in_3")
        if user_input_3:
            with chat_container_3:
                with st.chat_message("user"): st.write(user_input_3)
                st.session_state.messages_3.append({"role": "user", "content": user_input_3})
                with st.chat_message("assistant"):
                    response_3 = model.generate_content(f"{sys_prompt_3}\n\n사용자 질문: {user_input_3}")
                    st.write(response_3.text)
                st.session_state.messages_3.append({"role": "assistant", "content": response_3.text})
