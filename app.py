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

# 기능별로 4개의 탭 생성
tab1, tab2, tab3, tab4 = st.tabs([
    "⏱️ 24시간 타임블록 설계", 
    "🧠 감정-성취도 분석", 
    "📈 첫 월급 시뮬레이터", 
    "💸 소비 패턴 분석"
])

# ==========================================
# 탭 1: 갓생 루틴 메이커 (타임블록) - AI 자동 비교 코멘트 추가
# ==========================================
with tab1:
    col_vis1, col_chat1 = st.columns([6, 4])
    
    with col_vis1:
        st.subheader("📊 24시간 타임블록 설계")
        color_map = {'수면': '#3498db', '업무': '#e74c3c', '자기계발': '#f1c40f', '일상/휴식': '#2ecc71'}
        col_left, col_right = st.columns(2)
        
        # [왼쪽: 통계 분석]
        with col_left:
            st.markdown("#### 📉 통계 분석")
            period = st.selectbox("기간 단위", ["요일별", "월별"], key="stat_period")
            if period == "요일별":
                options_display = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
                val = st.selectbox("항목 선택", options_display, key="stat_val")
                display_title = f"{val} 평균 데이터"
                day_key = val[0] 
                base_data_day = {
                    "월": [6.8, 9.5, 1.2, 6.5], "화": [7.1, 9.2, 1.5, 6.2], 
                    "수": [6.9, 9.4, 1.8, 5.9], "목": [7.2, 8.8, 2.1, 5.9], 
                    "금": [6.5, 8.5, 1.0, 8.0], "토": [8.2, 2.5, 3.5, 9.8], 
                    "일": [8.5, 1.5, 3.0, 11.0]
                }
                data_values = base_data_day.get(day_key, [7.0, 9.0, 2.0, 6.0])
            else:
                options_display = [f"{i}월" for i in range(1, 13)]
                val = st.selectbox("항목 선택", options_display, key="stat_val2")
                display_title = f"{val} 평균 데이터"
                month_num = val.replace("월", "")
                base_data_month = {
                    "1": [7.3, 8.6, 2.4, 5.7], "2": [7.1, 8.9, 2.1, 5.9], 
                    "3": [6.9, 9.3, 1.8, 6.0], "4": [7.0, 9.1, 1.9, 6.0],
                    "5": [6.8, 8.8, 2.0, 6.4], "6": [6.9, 8.5, 2.1, 6.5],
                    "7": [7.2, 8.0, 1.8, 7.0], "8": [7.4, 7.8, 1.5, 7.3],
                    "9": [7.0, 8.7, 2.2, 6.1], "10": [7.1, 8.9, 2.5, 5.5],
                    "11": [6.8, 9.5, 2.3, 5.4], "12": [6.5, 8.5, 1.5, 7.5]
                }
                data_values = base_data_month.get(month_num, [7.0, 9.0, 2.0, 6.0])
            
            df_stat = pd.DataFrame({'활동': ['수면', '업무', '자기계발', '일상/휴식'], '시간': data_values})
            fig_stat = px.pie(df_stat, values='시간', names='활동', title=f"{display_title}", color='활동', color_discrete_map=color_map)
            fig_stat.update_layout(height=350, margin=dict(t=50, b=0, l=0, r=0))
            st.plotly_chart(fig_stat, use_container_width=True)

        # [오른쪽: 오늘의 계획]
        with col_right:
            st.markdown("#### 📅 오늘의 계획")
            weekday_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][today.weekday()]
            st.info(f"📅 **현재 날짜:** {today.strftime('%Y년 %m월 %d일')} ({weekday_kr})")
            
            c1, c2, c3 = st.columns(3)
            with c1: sleep_h = st.slider("수면", 0.0, 24.0, 7.0, 0.5, key="sl1")
            with c2: work_h = st.slider("업무", 0.0, 24.0, 9.0, 0.5, key="wk1")
            with c3: study_h = st.slider("자기계발", 0.0, 24.0, 2.0, 0.5, key="st1")
            rest_h = 24.0 - (sleep_h + work_h + study_h)
            
            st.write("") 
                        
            if rest_h < 0:
                st.error("시간 합계 초과!")
            else:
                df_today = pd.DataFrame({'활동': ['수면', '업무', '자기계발', '일상/휴식'], '시간': [sleep_h, work_h, study_h, rest_h]})
                fig_today = px.pie(df_today, values='시간', names='활동', title="현재 타임블록", color='활동', color_discrete_map=color_map)
                fig_today.update_layout(height=350, margin=dict(t=50, b=0, l=0, r=0))
                st.plotly_chart(fig_today, use_container_width=True)
        
        # [NEW: 로직 기반 패턴 비교 분석 영역]
        st.markdown("---")
        st.markdown("#### 📊 패턴 비교 분석")
        
        if st.button("✨ 평균 데이터 vs 오늘 계획 비교하기"):
            avg_sleep, avg_work, avg_study, avg_rest = data_values
            
            diff_sleep = sleep_h - avg_sleep
            diff_work = work_h - avg_work
            diff_study = study_h - avg_study
            
            comments = []
            
            # 수면 시간 분석
            if diff_sleep <= -1.0:
                comments.append("평소보다 **수면 시간이 부족**해 보여요. 컨디션 관리에 유의하세요! 🛌")
            elif diff_sleep >= 1.0:
                comments.append("오늘은 평소보다 **수면을 넉넉히** 챙기셨네요. 에너지 충전하기 딱 좋은 날입니다! 🔋")
                
            # 업무 및 자기계발(생산성) 분석
            if (diff_work + diff_study) >= 1.5:
                comments.append("평균보다 **업무와 자기계발에 투자하는 시간이 많습니다.** 열정도 좋지만 번아웃 조심하세요! 🔥")
            elif (diff_work + diff_study) <= -1.5:
                comments.append("오늘은 평소보다 일/공부 부담을 좀 덜어내셨네요. **여유를 즐기는 것도 루틴의 일부**죠! ☕")
                
            # 일상/휴식 분석
            if rest_h < 4.0:
                comments.append("식사나 이동을 제외하면 **온전한 휴식 시간이 꽤 부족**할 수 있어요. 짬 내서 꼭 스트레칭하세요! 🧘")
                
            # 밸런스가 좋은 경우
            if not comments:
                comments.append("평소 패턴과 비슷하게 **안정적이고 균형 잡힌 하루**를 계획하셨네요. 훌륭한 루틴 유지입니다! 👏")
            
            # 결과 출력
            final_comment = "\n\n".join(comments)
            st.success(final_comment)
                
    # [우측: 채팅 영역]
    with col_chat1:
        st.subheader("💬 타임블록 맞춤 코칭")
        sys_prompt_1 = f"""
        너는 직장인을 위한 현실적이고 다정한 루틴 코치야.
        현재 사용자의 컨디션은 '{condition}' 상태야.
        오늘 계획한 시간 배분: 수면 {sleep_h}시간, 업무 {work_h}시간, 자기계발 {study_h}시간, 일상/휴식 {rest_h:.1f}시간.
        
        [주의사항]
        여기서 '일상/휴식' 시간은 순수하게 노는 시간이 아니라 출퇴근, 식사, 가사 노동, 씻는 시간 등 필수적인 생활 시간이 모두 포함된 값이야.
        따라서 일상/휴식 시간이 길다고 해서 게으르다고 판단하거나 억지스러운 팩폭을 날려선 절대 안 돼.
        이 점을 충분히 감안해서, 현재 컨디션과 시간 배분의 밸런스가 좋은지 분석해주고, 현실적으로 실천 가능한 조언이나 따뜻한 격려를 해줘.
        """
        greeting_1 = f"안녕하세요 안태경 님! 오늘 '{condition}' 상태시군요. 출퇴근과 식사 시간 등을 고려했을 때, 오늘의 루틴 밸런스가 어떤지 점검해 드릴까요?"
        
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
# 탭 2: 감정-성취도 상관관계 분석 (로직 기반 자동 분석 코멘트 추가)
# ==========================================
with tab2:
    col_vis2, col_chat2 = st.columns([6, 4])
    
    with col_vis2:
        st.subheader("🧠 감정-성취도 상관관계 분석")
        
        # 1. 오늘의 데이터 입력 
        st.markdown("#### 📝 오늘의 기록")
        
        def format_cond(val):
            if val == 0: return "😥 0"
            elif val == 50: return "😐 50"
            elif val == 100: return "😀 100"
            return str(val)

        cond_help_text = "0(😥 피곤해요) ~ 50(😐 그저 그래요) ~ 100(😀 최고예요)"
        
        c1, c2, c3 = st.columns(3)
        with c1: cond_morning = st.select_slider("아침", options=range(0, 101, 10), value=50, format_func=format_cond, help=cond_help_text, key="cm")
        with c2: cond_afternoon = st.select_slider("점심", options=range(0, 101, 10), value=70, format_func=format_cond, help=cond_help_text, key="ca")
        with c3: cond_evening = st.select_slider("저녁", options=range(0, 101, 10), value=40, format_func=format_cond, help=cond_help_text, key="ce")
        
        st.write("")
        achieve_help_text = "💡 기준: 오늘 계획했던 핵심 루틴과 업무를 얼마나 달성했나요?"
        achievement_today = st.slider("🎯 오늘의 성취도 (%)", 0, 100, 70, 5, help=achieve_help_text, key="achieve")
        
        avg_cond_today = (cond_morning + cond_afternoon + cond_evening) / 3
        
        st.markdown("---")
        st.markdown("#### 📊 데이터 시각화 리포트")
        
        # 2. 가상 데이터 생성 
        dates = pd.date_range(end=today - timedelta(days=1), periods=13) 
        df_mock = pd.DataFrame({
            "날짜": dates,
            "아침": np.random.randint(30, 100, 13),
            "점심": np.random.randint(40, 100, 13),
            "저녁": np.random.randint(20, 90, 13),
            "성취도": np.random.randint(40, 100, 13)
        })
        df_mock["일일_평균"] = df_mock[["아침", "점심", "저녁"]].mean(axis=1)
        
        # 오늘 데이터를 통합
        df_today = pd.DataFrame({
            "날짜": [today], "아침": [cond_morning], "점심": [cond_afternoon], "저녁": [cond_evening],
            "성취도": [achievement_today], "일일_평균": [avg_cond_today]
        })
        df_history = pd.concat([df_mock, df_today], ignore_index=True)
        
        df_history["날짜"] = pd.to_datetime(df_history["날짜"])
        df_history["요일"] = df_history["날짜"].dt.strftime("%a")
        
        # 🎨 가독성을 높인 뚜렷한 대비 색상 (블루 & 레드)
        chart_colors = {"일일_평균": "#3498db", "성취도": "#e74c3c"}
        
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(["📈 종합 추이", "⏰ 시간대별 패턴", "📅 요일별 분석"])
        
        with chart_tab1:
            fig_trend = px.line(df_history, x="날짜", y=["일일_평균", "성취도"],
                                labels={"value": "점수", "variable": "지표"},
                                title="최근 2주 컨디션 vs 성취도 추이", markers=True,
                                color="variable", color_discrete_map=chart_colors)
            fig_trend.update_layout(height=320, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with chart_tab2:
            time_avg = {"아침": df_history["아침"].mean(), "점심": df_history["점심"].mean(), "저녁": df_history["저녁"].mean()}
            df_time = pd.DataFrame(list(time_avg.items()), columns=["시간대", "평균_컨디션"])
            fig_time = px.bar(df_time, x="시간대", y="평균_컨디션", title="시간대별 평균 컨디션", color="시간대", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_time.update_layout(height=320, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_time, use_container_width=True)
            
        with chart_tab3:
            day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            df_history['요일'] = pd.Categorical(df_history['요일'], categories=day_order, ordered=True)
            df_day = df_history.groupby("요일")[["일일_평균", "성취도"]].mean().reset_index()
            fig_day = px.bar(df_day, x="요일", y=["일일_평균", "성취도"], barmode="group", 
                             title="요일별 평균 비교", color="variable", color_discrete_map=chart_colors)
            fig_day.update_layout(height=320, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_day, use_container_width=True)
            
        # [NEW: 로직 기반 3종 데이터 인사이트 분석 영역]
        st.markdown("---")
        st.markdown("#### 💡 데이터 인사이트")
        
        if st.button("✨ 최근 2주 패턴 분석하기", key="analyze_tab2"):
            # 1. 종합 추이 분석 로직
            avg_cond_14d = df_history["일일_평균"].mean()
            avg_ach_14d = df_history["성취도"].mean()
            
            diff_cond = avg_cond_today - avg_cond_14d
            diff_ach = achievement_today - avg_ach_14d
            
            trend_msg = "**1. 종합 추이:** 최근 2주 평균 대비 오늘의 컨디션은 "
            if diff_cond >= 10: trend_msg += "좋은 편이고, "
            elif diff_cond <= -10: trend_msg += "아쉬운 편이고, "
            else: trend_msg += "비슷한 수준이며, "
            
            if diff_ach >= 10: trend_msg += "성취도는 훌륭합니다! 🌟"
            elif diff_ach <= -10: trend_msg += "성취도는 다소 낮습니다. 무리하지 마세요. ☕"
            else: trend_msg += "성취도도 안정적으로 유지 중입니다. 👍"
            
            # 2. 시간대별 분석 로직
            best_time = max(time_avg, key=time_avg.get)
            worst_time = min(time_avg, key=time_avg.get)
            time_msg = f"**2. 시간대별 패턴:** 주로 **'{best_time}'**에 에너지가 가장 높고, **'{worst_time}'**에 떨어지는 경향이 있습니다. 에너지가 필요한 중요한 업무는 가급적 {best_time}에 배치해 보세요! ⏰"
            
            # 3. 요일별 분석 로직
            best_day = df_day.loc[df_day["성취도"].idxmax()]["요일"]
            # 영어 요일을 한글로 변환
            day_kr_map = {"Mon": "월", "Tue": "화", "Wed": "수", "Thu": "목", "Fri": "금", "Sat": "토", "Sun": "일"}
            best_day_kr = day_kr_map.get(best_day, best_day)
            day_msg = f"**3. 요일별 분석:** 데이터를 보면 **{best_day_kr}요일**의 성취도가 가장 높게 나타납니다. {best_day_kr}요일의 좋은 루틴을 다른 날에도 적용해 보는 건 어떨까요? 📅"
            
            # 종합 코멘트 출력
            st.success(f"{trend_msg}\n\n{time_msg}\n\n{day_msg}")

    with col_chat2:
        st.subheader("💬 멘탈/성취도 맞춤 코칭")
        
        sys_prompt_2 = f"""
        너는 직장인의 멘탈과 성취도를 관리해주는 따뜻하고 예리한 상담가야.
        오늘 사용자의 데이터:
        - 아침 컨디션: {cond_morning}/100
        - 점심 컨디션: {cond_afternoon}/100
        - 저녁 컨디션: {cond_evening}/100
        - 하루 평균: {avg_cond_today:.1f}/100
        - 오늘의 달성률(성취도): {achievement_today}%
        
        이 데이터를 바탕으로 오늘 하루 감정의 기복이 어땠는지 캐치해주고(예: 저녁에 급격히 떨어짐 등), 
        달성률과 엮어서 내일을 위한 멘탈 케어 팁을 2~3문장으로 다정하게 제공해줘.
        """
        
        greeting_2 = f"감정의 흐름(아침 {cond_morning} ➡️ 점심 {cond_afternoon} ➡️ 저녁 {cond_evening})을 기록해주셨네요! 달성률 {achievement_today}%와 엮어서 오늘 하루를 리뷰해 드릴까요?"
        
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
# 탭 3: 월급 시뮬레이터 (원 단위 & 고정지출 상세 관리)
# ==========================================
with tab3:
    col_vis3, col_chat3 = st.columns([6, 4])
    
    with col_vis3:
        st.subheader("📈 월급 시뮬레이터")
        net_salary = 3750000 
        st.markdown(f"### 💵 예상 월 세후 실수령액: `3,750,000원`")
        
        st.markdown("---")
        st.markdown("#### 🛠️ 월 예산 설정 (원 단위)")
        
        # 1. 고정 지출 리스트 관리
        st.markdown("#### 🏠 고정 지출 상세 (정기 결제)")
        # 데이터프레임으로 고정 지출 관리
        fixed_expenses_data = pd.DataFrame([
            {"항목": "카카오톡", "금액": 6000},
            {"항목": "유튜브 프리미엄", "금액": 15000},
            {"항목": "티빙", "금액": 5000},
            {"항목": "휴대폰 요금", "금액": 105000},
            {"항목": "구글+제미나이", "금액": 29000}
        ])
        
        # 사용자가 리스트 수정 가능
        edited_fixed = st.data_editor(fixed_expenses_data, num_rows="dynamic", use_container_width=True)
        total_fixed = edited_fixed["금액"].sum()
        
        st.write("")
        # 2. 저축/투자 및 생활비 설정
        c1, c2 = st.columns(2)
        with c1:
            amt_save = st.number_input("💰 저축/투자 금액 (원)", min_value=0, max_value=net_salary, value=1500000, step=10000)
        with c2:
            ret_rate = st.slider("📊 연 기대 수익률 (%)", 0.0, 10.0, 4.0, 0.1)
            
        # 잔액 계산
        amt_flex = net_salary - total_fixed - amt_save
        
        st.write("")
        m1, m2, m3 = st.columns(3)
        m1.metric("저축/투자", f"{amt_save:,} 원")
        m2.metric("고정 지출", f"{total_fixed:,} 원")
        m3.metric("남은 생활비", f"{amt_flex:,} 원", delta_color="normal")
        
        if amt_flex < 0:
            st.error("⚠️ 설정한 예산이 월급을 초과했습니다! 지출이나 저축액을 조정하세요.")
            
        st.markdown("---")
        st.markdown("#### 📊 자산 성장 시뮬레이션")
        
        # 미래 자산 계산
        years = [1, 3, 5]
        accumulated = []
        for y in years:
            months = y * 12
            total = 0
            for m in range(months): total = (total + amt_save) * (1 + (ret_rate/100) / 12)
            accumulated.append(total)
            
        df_g = pd.DataFrame({"기간": ["1년 뒤", "3년 뒤", "5년 뒤"], "자산(원)": accumulated})
        fig_g = px.bar(df_g, x="기간", y="자산(원)", text_auto='.2s', title="저축 지속 시 목돈 마련 추이")
        st.plotly_chart(fig_g, use_container_width=True)

    with col_chat3:
        st.subheader("💬 재무 상담가 코멘트")
        sys_prompt_3 = f"""
        너는 재무 전문가야. 사용자의 월 세후 실수령액은 375만원이야.
        - 고정 지출 합계: {total_fixed}원
        - 저축액: {amt_save}원
        - 남은 생활비: {amt_flex}원
        - 기대 수익률: {ret_rate}%
        
        이 예산을 기반으로, 고정 지출 중 줄일 수 있는 부분은 없는지, 
        남은 생활비로 한 달을 버티기에 적절한지 냉정하게 평가하고 팩트 폭격형 조언을 해줘.
        """
        if "messages_3" not in st.session_state:
            st.session_state.messages_3 = [{"role": "assistant", "content": "세후 375만 원의 첫 월급, 고정 지출까지 꼼꼼히 반영해서 재무 설계를 시작해 볼까요?"}]
            
        chat_container_3 = st.container(height=550)
        with chat_container_3:
            for msg in st.session_state.messages_3:
                with st.chat_message(msg["role"]): st.write(msg["content"])
                    
        if user_input_3 := st.chat_input("재무 전략 상담...", key="chat_in_3"):
            with chat_container_3:
                with st.chat_message("user"): st.write(user_input_3)
                st.session_state.messages_3.append({"role": "user", "content": user_input_3})
                with st.chat_message("assistant"):
                    response_3 = model.generate_content(f"{sys_prompt_3}\n\n질문: {user_input_3}")
                    st.write(response_3.text)
                st.session_state.messages_3.append({"role": "assistant", "content": response_3.text})

# ==========================================
# 탭 4: 소비 패턴 분석 및 팩폭 컨설팅
# ==========================================
with tab4:
    col_vis4, col_chat4 = st.columns([6, 4])
    
    with col_vis4:
        st.subheader("💸 소비 패턴 분석 및 팩폭 컨설팅")
        df_expenses = pd.DataFrame([
            {"카테고리": "식비(배달 포함)", "금액": 150000},
            {"카테고리": "교통비", "금액": 30000},
            {"카테고리": "쇼핑/자기계발", "금액": 50000},
            {"카테고리": "기타", "금액": 20000}
        ])
        edited_df = st.data_editor(df_expenses, num_rows="dynamic", key="expense_editor")
        st.bar_chart(edited_df.set_index("카테고리"))

    with col_chat4:
        st.subheader("💬 지출 팩폭 상담가")
        max_expense = edited_df.loc[edited_df["금액"].idxmax()]["카테고리"]
        sys_prompt_4 = f"너는 지출 내역을 보고 팩트 폭격을 날려주는 깐깐한 상담가야. 사용자가 이번 주 '{max_expense}' 카테고리에 가장 많은 돈을 썼어. 정신 차리게 해주고 내일 당장 실천할 구체적인 절약 미션을 던져줘."
        greeting_4 = f"이번 주 '{max_expense}'에 지출이 가장 많으시네요. 팩트 폭격과 함께 절약 미션을 받아보시겠어요?"
        
        if "messages_4" not in st.session_state:
            st.session_state.messages_4 = [{"role": "assistant", "content": greeting_4}]
            
        chat_container_4 = st.container(height=550)
        with chat_container_4:
            for msg in st.session_state.messages_4:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
        user_input_4 = st.chat_input("지출 관리에 대해 질문하기...", key="chat_in_4")
        if user_input_4:
            with chat_container_4:
                with st.chat_message("user"): st.write(user_input_4)
                st.session_state.messages_4.append({"role": "user", "content": user_input_4})
                with st.chat_message("assistant"):
                    response_4 = model.generate_content(f"{sys_prompt_4}\n\n사용자 질문: {user_input_4}")
                    st.write(response_4.text)
                st.session_state.messages_4.append({"role": "assistant", "content": response_4.text})
