import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

# ----------------------------------------------------------------------
# 1. 페이지 기본 설정 (Hy-Life Manager 반영)
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Hy-Life Manager | 직장인 라이프 매니저", 
    page_icon="🌱", 
    layout="wide"
)

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
# 4. 사이드바 구성 (Company, 성장 로그 및 Quick Links 추가)
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 👤 Profile\n**Name:** 안태경\n\n**Company:** SK하이닉스\n\n**Team:** 양산기술")
    st.markdown("---")
    st.markdown("### ⏳ D-Day\n")
    st.info(f"**입사일:** {join_str}\n\n**월급날:** {pay_str}")
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown("- 🌐 [SK하이닉스 공식 홈페이지](https://www.skhynix.com/)")
    st.markdown("- 📰 [SK하이닉스 뉴스룸](https://news.skhynix.co.kr/)")

# ----------------------------------------------------------------------
# 5. 메인 화면 로직 (탭 기반 1기능-1채팅 레이아웃)
# ----------------------------------------------------------------------
st.title("🌱 Hy-Life Manager")

# 기능별로 4개의 탭 생성
tab1, tab2, tab3, tab4 = st.tabs([
    "🧩 24시간 타임블록 설계", 
    "💓 컨디션-성취도 분석", 
    "🧮 월급 시뮬레이터", 
    "💸 소비 패턴 분석"
])

# ==========================================
# 탭 1: 갓생 루틴 메이커 (타임블록) 
# ==========================================
with tab1:
    col_vis1, col_chat1 = st.columns([6, 4])
    
    with col_vis1:
        st.subheader("🧩 24시간 타임블록 설계")
        color_map = {'수면': '#3498db', '업무': '#e74c3c', '자기계발': '#f1c40f', '일상/휴식': '#2ecc71'}
        col_left, col_right = st.columns(2)
        
        # [왼쪽: 통계 분석]
        with col_left:
            st.markdown("#### 🗂️ 통계 분석")
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
            st.info(f"**현재 날짜:** {today.strftime('%Y년 %m월 %d일')} ({weekday_kr})")
            
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
        
        # [로직 기반 패턴 비교 분석 영역]
        st.markdown("---")
        st.markdown("#### 🔍 패턴 비교 분석")
        
        if st.button("✨ 평균 데이터 vs 오늘 계획 비교하기"):
            avg_sleep, avg_work, avg_study, avg_rest = data_values
            
            diff_sleep = sleep_h - avg_sleep
            diff_work = work_h - avg_work
            diff_study = study_h - avg_study
            
            comments = []
            
            if diff_sleep <= -1.0:
                comments.append("평소보다 **수면 시간이 부족**해 보여요. 컨디션 관리에 유의하세요! 🛌")
            elif diff_sleep >= 1.0:
                comments.append("오늘은 평소보다 **수면을 넉넉히** 챙기셨네요. 에너지 충전하기 딱 좋은 날입니다! 🔋")
                
            if (diff_work + diff_study) >= 1.5:
                comments.append("평균보다 **업무와 자기계발에 투자하는 시간이 많습니다.** 열정도 좋지만 번아웃 조심하세요! 🔥")
            elif (diff_work + diff_study) <= -1.5:
                comments.append("오늘은 평소보다 일/공부 부담을 좀 덜어내셨네요. **여유를 즐기는 것도 루틴의 일부**죠! ☕")
                
            if rest_h < 4.0:
                comments.append("식사나 이동을 제외하면 **온전한 휴식 시간이 꽤 부족**할 수 있어요. 짬 내서 꼭 스트레칭하세요! 🧘")
                
            if not comments:
                comments.append("평소 패턴과 비슷하게 **안정적이고 균형 잡힌 하루**를 계획하셨네요. 훌륭한 루틴 유지입니다! 👏")
            
            final_comment = "\n\n".join(comments)
            st.success(final_comment)
                
    # [우측: 채팅 영역 - 스마트 라이프 코치 페르소나 적용]
    with col_chat1:
        st.subheader("💬 타임블록 맞춤 코칭")
        sys_prompt_1 = f"""
        너는 직장인의 효율적인 시간 관리를 돕는 스마트 라이프 코치야.
        오늘 계획한 시간 배분(수면 {sleep_h}시간, 업무 {work_h}시간, 자기계발 {study_h}시간, 일상/휴식 {rest_h:.1f}시간)을 바탕으로 하루의 밸런스를 분석해 줘.
        무조건 열심히 하라는 압박보다는, 일과 휴식의 조화를 통해 '지속 가능한 루틴'을 만들 수 있도록 현실적이고 따뜻한 피드백을 제공하는 것이 핵심이야.
        """
        greeting_1 = "안녕하세요 안태경 님! 오늘 계획하신 타임블록을 확인했습니다. 일과 휴식의 밸런스가 잘 맞는지, 지속 가능한 루틴을 위한 피드백을 받아보시겠어요?"
        
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
# 탭 2: 컨디션-성취도 상관관계 분석 
# ==========================================
with tab2:
    col_vis2, col_chat2 = st.columns([6, 4])
    
    with col_vis2:
        st.subheader("💓 컨디션-성취도 분석")
        
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
        
        dates = pd.date_range(end=today - timedelta(days=1), periods=13) 
        df_mock = pd.DataFrame({
            "날짜": dates,
            "아침": np.random.randint(30, 100, 13),
            "점심": np.random.randint(40, 100, 13),
            "저녁": np.random.randint(20, 90, 13),
            "성취도": np.random.randint(40, 100, 13)
        })
        df_mock["일일_평균"] = df_mock[["아침", "점심", "저녁"]].mean(axis=1)
        
        df_today = pd.DataFrame({
            "날짜": [today], "아침": [cond_morning], "점심": [cond_afternoon], "저녁": [cond_evening],
            "성취도": [achievement_today], "일일_평균": [avg_cond_today]
        })
        df_history = pd.concat([df_mock, df_today], ignore_index=True)
        
        df_history["날짜"] = pd.to_datetime(df_history["날짜"])
        df_history["요일"] = df_history["날짜"].dt.strftime("%a")
        
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
            
        st.markdown("---")
        st.markdown("#### 💡 데이터 인사이트")
        
        if st.button("✨ 최근 2주 패턴 분석하기", key="analyze_tab2"):
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
            
            best_time = max(time_avg, key=time_avg.get)
            worst_time = min(time_avg, key=time_avg.get)
            time_msg = f"**2. 시간대별 패턴:** 주로 **'{best_time}'**에 에너지가 가장 높고, **'{worst_time}'**에 떨어지는 경향이 있습니다. 에너지가 필요한 중요한 업무는 가급적 {best_time}에 배치해 보세요! ⏰"
            
            best_day = df_day.loc[df_day["성취도"].idxmax()]["요일"]
            day_kr_map = {"Mon": "월", "Tue": "화", "Wed": "수", "Thu": "목", "Fri": "금", "Sat": "토", "Sun": "일"}
            best_day_kr = day_kr_map.get(best_day, best_day)
            day_msg = f"**3. 요일별 분석:** 데이터를 보면 **{best_day_kr}요일**의 성취도가 가장 높게 나타납니다. {best_day_kr}요일의 좋은 루틴을 다른 날에도 적용해 보는 건 어떨까요? 📅"
            
            st.success(f"{trend_msg}\n\n{time_msg}\n\n{day_msg}")

    # [우측: 채팅 영역 - 마인드케어 파트너 페르소나 적용]
    with col_chat2:
        st.subheader("💬 멘탈/성취도 맞춤 코칭")
        
        sys_prompt_2 = f"""
        너는 직장인의 멘탈 케어와 성취도를 함께 고민해 주는 다정한 파트너야.
        오늘의 감정 흐름(아침 {cond_morning}/100, 점심 {cond_afternoon}/100, 저녁 {cond_evening}/100)과 하루 성취도({achievement_today}%) 데이터를 바탕으로 오늘 하루를 객관적이면서도 따뜻하게 리뷰해 줘.
        무리하지 않고 내일 더 나은 컨디션을 유지할 수 있는 실질적인 마인드 케어 팁을 2~3문장으로 제안해 줘.
        """
        
        greeting_2 = "오늘 하루의 감정 흐름과 성취도를 모두 기록해 주셨군요! 데이터를 바탕으로 오늘 하루를 객관적으로 리뷰하고, 내일을 위한 마인드 케어 팁을 확인해 볼까요?"
        
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
# 탭 3: 월급 시뮬레이터 
# ==========================================
with tab3:
    col_vis3, col_chat3 = st.columns([6, 4])
    
    with col_vis3:
        st.markdown("### 🧮 월급 시뮬레이터")
        st.info("ℹ️ 하단 시뮬레이션은 예상 월 실수령액 **3,750,000원**을 기준으로 계산됩니다.")
        
        net_salary = 3750000 
        
        with st.expander("🏠 고정 지출 상세 내역 (정기 결제 항목 보기/편집)", expanded=False):
            fixed_expenses_data = pd.DataFrame([
                {"항목": "휴대폰 기기 + 통신", "금액": 105000}, {"항목": "구글 AI Pro", "금액": 29000},
                {"항목": "유튜브 프리미엄", "금액": 15000}, {"항목": "넷플릭스", "금액": 13500},
                {"항목": "카카오톡", "금액": 6000}, {"항목": "티빙", "금액": 5500}
            ])
            edited_fixed = st.data_editor(fixed_expenses_data, num_rows="dynamic", use_container_width=True)
        
        total_fixed = edited_fixed["금액"].sum()
        
        c1, c2 = st.columns(2)
        with c1:
            amt_save = st.number_input("💰 저축/투자 금액 (원)", min_value=0, max_value=net_salary, value=1500000, step=100000, key="num_save_3")
        with c2:
            rate_options = [round(x * 0.5, 1) for x in range(-40, 41)]
            ret_rate = st.select_slider("📈 수익률 시뮬레이션", options=rate_options, value=4.0, key="slide_rate_3")
        
        amt_flex = net_salary - total_fixed - amt_save
        
        m1, m2, m3 = st.columns(3)
        m1.metric("월 저축/투자액", f"{amt_save:,} 원")
        m2.metric("고정 지출 합계", f"{total_fixed:,} 원")
        m3.metric("남은 생활비", f"{amt_flex:,} 원")
        
        if amt_flex < 0:
            st.error("⚠️ 설정한 예산이 월급을 초과했습니다!")
        
        tab_basic, tab_bonus = st.tabs(["🗺️ 5개년 자산 로드맵", "🪙 성과급 시뮬레이션 (체험판)"])
        
        def format_kr_won(val):
            sign = "-" if val < 0 else ""
            val = abs(val)
            if val >= 100000000:
                uk = int(val // 100000000)
                man = int((val % 100000000) // 10000)
                return f"{sign}{uk}억{man}만" if man > 0 else f"{sign}{uk}억"
            return f"{sign}{int(val // 10000)}만"

        with tab_basic:
            with st.popover("ℹ️ 손익 계산 방식 보기"):
                st.write("**[계산 로직]**")
                st.caption("매월 투자액이 월 복리로 계산됩니다.")
                st.caption("- 원금: 월 투자액 × 누적 개월 수")
                st.caption("- 손익: 미래가치(FV) - 원금")
                st.caption("- 매달 적립되는 금액은 운용 기간에 따라 이자가 다르게 적용됩니다.")
            
            years = np.arange(1, 6) 
            results = []
            for y in years:
                months = y * 12
                fv = 0
                for m in range(months): fv = (fv + amt_save) * (1 + (ret_rate/100)/12)
                results.append({"년차": f"{y}년차", "원금": amt_save * months, "손익": fv - (amt_save * months)})
            
            df_melt = pd.DataFrame(results).melt(id_vars="년차", value_vars=["원금", "손익"], var_name="구분", value_name="금액")
            df_melt["금액_텍스트"] = df_melt["금액"].apply(format_kr_won)
            
            fig_g = px.bar(df_melt, x="년차", y=df_melt["금액"]/10000, color="구분",
                           title=f"연 기대 수익률 {ret_rate}% 반영 5개년 자산 로드맵",
                           barmode="relative", text="금액_텍스트",
                           color_discrete_map={"원금": "#7f8c8d", "손익": ("#e74c3c" if ret_rate > 0 else "#3498db")})
            fig_g.update_traces(textposition='auto', insidetextanchor='middle')
            fig_g.update_layout(height=450, uniformtext_minsize=11, uniformtext_mode='show')
            st.plotly_chart(fig_g, use_container_width=True)

        with tab_bonus:
            with st.popover("ℹ️ 성과급 계산 방식 보기"):
                st.write("**[예상 성과급 시스템 가정]**")
                st.caption("- 기본급: 연봉(월 실수령액 375만×12) / 20")
                st.caption("- PI(생산성 격려금): 기본급의 200% (연간)")
                st.caption("- PS(초과이익 성과급): 기본급의 1000% 가정")
                st.caption("- 세후 반영: 추정 세율 38% 공제 후 적용")
            
            results_b = []
            annual_base = net_salary * 12
            total_bonus_before_tax = (annual_base / 20) * 12 
            tax_rate = 0.38 
            total_bonus_after_tax = total_bonus_before_tax * (1 - tax_rate)
            
            for y in years:
                months = y * 12
                fv = 0
                for m in range(months): fv = (fv + amt_save) * (1 + (ret_rate/100)/12)
                fv += total_bonus_after_tax * y 
                
                results_b.append({
                    "년차": f"{y}년차", 
                    "원금": amt_save * months, 
                    "성과급": total_bonus_after_tax * y, 
                    "손익": fv - (amt_save * months + total_bonus_after_tax * y)
                })
            
            df_b = pd.DataFrame(results_b).melt(id_vars="년차", value_vars=["원금", "성과급", "손익"], var_name="구분", value_name="금액")
            df_b["금액_텍스트"] = df_b["금액"].apply(format_kr_won)
            
            fig_b = px.bar(df_b, x="년차", y=df_b["금액"]/10000, color="구분",
                           title=f"예상 성과급 반영 5개년 자산 로드맵",
                           barmode="relative", text="금액_텍스트",
                           color_discrete_map={"원금": "#7f8c8d", "성과급": "#ffcc99", "손익": ("#e74c3c" if ret_rate > 0 else "#3498db")})
            fig_b.update_traces(textposition='auto', insidetextanchor='middle')
            fig_b.update_layout(height=450, uniformtext_minsize=11, uniformtext_mode='show')
            st.plotly_chart(fig_b, use_container_width=True)
    
    # [우측: 채팅 영역 - 전문 재무 컨설턴트 페르소나 적용]
    with col_chat3:
        st.subheader("💬 재무 상담가 코멘트")
        sys_prompt_3 = f"""
        너는 사회초년생의 자산 형성을 돕는 전문 재무 컨설턴트야.
        세후 실수령액 375만 원을 기준으로, 현재 설정된 고정 지출({total_fixed}원), 투자액({amt_save}원), 남은 생활비({amt_flex}원)의 비율을 분석해 줘.
        무리한 절약을 강요하거나 비난하지 말고, 현재의 예산 분배가 장기적으로 안정적인지 객관적으로 진단한 뒤 실용적인 자산 관리 전략을 제안해 줘.
        """
        greeting_3 = "첫 월급의 설렘을 넘어, 본격적인 자산 관리를 시작할 때입니다. 현재 설정하신 예산 분배와 고정 지출 내역을 바탕으로 안정적인 재무 포트폴리오를 점검해 드릴까요?"
        
        if "messages_3" not in st.session_state:
            st.session_state.messages_3 = [{"role": "assistant", "content": greeting_3}]
            
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
# 탭 4: 소비 패턴 분석 
# ==========================================
with tab4:
    col_vis4, col_chat4 = st.columns([6, 4])
    
    categories = ["고정지출", "식비", "교통비", "쇼핑/생활", "문화/여가", "건강/미용"]
    if "monthly_expenses" not in st.session_state:
        st.session_state.monthly_expenses = {
            "1월": [174000, 845200, 125400, 452300, 215000, 85400],
            "2월": [174000, 712500, 110500, 310500, 150000, 65000],
            "3월": [174000, 550300, 95000, 185200, 120500, 45000],
            "4월": [174000, 520100, 98000, 150400, 95000, 40000],
            "5월": [174000, 680500, 130200, 380500, 175000, 95500],
            "6월": [174000, 920500, 145800, 620500, 280000, 110500],
            "7월": [0, 0, 0, 0, 0, 0],
            "8월": [0, 0, 0, 0, 0, 0],
            "9월": [0, 0, 0, 0, 0, 0],
            "10월": [0, 0, 0, 0, 0, 0],
            "11월": [0, 0, 0, 0, 0, 0],
            "12월": [0, 0, 0, 0, 0, 0]
        }
        
    with col_vis4:
        st.subheader("💸 소비 패턴 분석")
        
        months_list = [f"{i}월" for i in range(1, 13)]
        selected_month = st.selectbox("분석할 월을 선택하세요", options=months_list, index=5)
        
        with st.expander(f"✍️ {selected_month} 지출 내역 편집 (항목 변경 시 실시간 반영)", expanded=False):
            df_current = pd.DataFrame({
                "카테고리": categories,
                "금액": st.session_state.monthly_expenses[selected_month]
            })
            edited_df = st.data_editor(df_current, use_container_width=True, key=f"editor_{selected_month}")
            st.session_state.monthly_expenses[selected_month] = edited_df["금액"].tolist()
            
        st.write("")
        
        monthly_totals = [sum(st.session_state.monthly_expenses[m]) for m in months_list]
        df_trend = pd.DataFrame({"월": months_list, "지출액": monthly_totals})
        
        df_trend_filtered = df_trend[df_trend["지출액"] > 0].copy()
        df_trend_filtered["지출액(만)"] = df_trend_filtered["지출액"] / 10000
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<p style='font-size:14px; font-weight:bold; margin-bottom:0;'>📅 연간 총 지출 추이</p>", unsafe_allow_html=True)
            
            if not df_trend_filtered.empty:
                colors = ["#e74c3c" if m == selected_month else "#3498db" for m in df_trend_filtered["월"]]
                fig_trend = px.bar(df_trend_filtered, x="월", y="지출액(만)", color="월", color_discrete_sequence=colors)
                fig_trend.update_traces(texttemplate='%{y:,.0f}만', textposition='outside')
                fig_trend.update_layout(
                    height=280, margin=dict(t=25, b=10, l=0, r=0), 
                    showlegend=False, yaxis=dict(title="지출액 (만 원)")
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("데이터가 집계된 달이 없습니다.")
            
        with c2:
            st.markdown(f"<p style='font-size:14px; font-weight:bold; margin-bottom:0;'>🥧 {selected_month} 카테고리 분포</p>", unsafe_allow_html=True)
            
            current_total = edited_df["금액"].sum()
            if current_total > 0:
                df_pie = edited_df[edited_df["금액"] > 0]
                fig_pie = px.pie(df_pie, values="금액", names="카테고리", hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(height=280, margin=dict(t=25, b=10, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning(f"🚫 {selected_month} 지출 내역이 아직 집계되지 않았습니다.")
                
        st.markdown("---")
        
        curr_idx = months_list.index(selected_month)
        if curr_idx > 0:
            prev_month = months_list[curr_idx - 1]
            st.markdown(f"##### 📈 지출 증감 원인 분석 ({prev_month} ➔ {selected_month})")
            
            prev_total = sum(st.session_state.monthly_expenses[prev_month])
            curr_total = sum(st.session_state.monthly_expenses[selected_month])
            
            if curr_total == 0 and prev_total == 0:
                st.info("비교할 지출 데이터가 없습니다.")
            else:
                diffs = []
                diff_dict = {}
                for i, cat in enumerate(categories):
                    curr_val = st.session_state.monthly_expenses[selected_month][i]
                    prev_val = st.session_state.monthly_expenses[prev_month][i]
                    diff_val = (curr_val - prev_val) / 10000 
                    diffs.append(diff_val)
                    if diff_val != 0:
                        diff_dict[cat] = diff_val
                
                total_diff_man = (curr_total - prev_total) / 10000
                
                if total_diff_man > 0:
                    increase_dict = {k: v for k, v in diff_dict.items() if v > 0}
                    if increase_dict:
                        max_inc_cat = max(increase_dict, key=increase_dict.get)
                        max_inc_val = increase_dict[max_inc_cat]
                        st.error(f"🚨 **알림:** 전체 지출이 전월 대비 **{total_diff_man:,.1f}만 원** 늘었습니다. 주원인은 **'{max_inc_cat}'**(+{max_inc_val:,.1f}만 원) 입니다.")
                    else:
                        st.error(f"🚨 **알림:** 전체 지출이 전월 대비 **{total_diff_man:,.1f}만 원** 늘었습니다.")
                        
                elif total_diff_man < 0:
                    decrease_dict = {k: v for k, v in diff_dict.items() if v < 0}
                    if decrease_dict:
                        max_dec_cat = min(decrease_dict, key=decrease_dict.get)
                        max_dec_val = abs(decrease_dict[max_dec_cat])
                        st.success(f"🎉 **훌륭합니다!** 전체 지출이 전월 대비 **{abs(total_diff_man):,.1f}만 원** 감소했습니다. 특히 **'{max_dec_cat}'**(-{max_dec_val:,.1f}만 원) 절약이 컸습니다!")
                    else:
                        st.success(f"🎉 **훌륭합니다!** 전체 지출이 전월 대비 **{abs(total_diff_man):,.1f}만 원** 감소했습니다.")
                else:
                    st.info("⚖️ 전체 지출 금액이 전월과 정확히 동일합니다.")
                
                x_labels = [f"{prev_month} 총지출"] + categories + [f"{selected_month} 총지출"]
                measure_list = ["absolute"] + ["relative"] * len(categories) + ["total"]
                y_values = [prev_total/10000] + diffs + [curr_total/10000]
                text_values = [f"{prev_total/10000:,.0f}만"] + [f"{x:+.1f}만" if x!=0 else "-" for x in diffs] + [f"{curr_total/10000:,.0f}만"]
                
                fig_waterfall = go.Figure(go.Waterfall(
                    name="20", orientation="v",
                    measure=measure_list,
                    x=x_labels,
                    textposition="outside",
                    text=text_values,
                    y=y_values,
                    connector={"line":{"color":"rgb(63, 63, 63)"}},
                    decreasing={"marker":{"color":"#2ecc71"}},
                    increasing={"marker":{"color":"#e74c3c"}},
                    totals={"marker":{"color":"#3498db", "line":{"color":"blue", "width":2}}}
                ))
                
                fig_waterfall.update_layout(
                    height=320, 
                    margin=dict(t=30, b=10, l=0, r=0),
                    showlegend=False,
                    yaxis=dict(title="지출액 (만 원)")
                )
                st.plotly_chart(fig_waterfall, use_container_width=True)
        else:
            st.markdown("##### 📈 지출 증감 원인 분석")
            st.info("1월은 이전 데이터가 없어 증감 비교를 제공하지 않습니다.")

    # [우측: 채팅 영역 - 스마트 소비 분석가 페르소나 적용]
    with col_chat4:
        st.subheader("💬 지출 분석 상담가")
        
        df_variable = edited_df[edited_df["카테고리"] != "고정지출"]
        if not df_variable.empty and df_variable["금액"].sum() > 0:
            max_expense = df_variable.loc[df_variable["금액"].idxmax()]["카테고리"]
            greeting_4 = f"{selected_month} 소비 내역을 분석한 결과, '{max_expense}' 항목의 비중이 가장 높게 나타났습니다. 이번 달 지출 흐름을 진단하고 다음 달을 위한 스마트한 소비 전략을 세워볼까요?"
        else:
            max_expense = "지출 없음"
            greeting_4 = f"{selected_month} 지출 내역이 아직 집계되지 않았습니다. 새로운 달을 맞이하여 미리 예산 분배 계획을 세워볼까요?"
            
        sys_prompt_4 = f"""
        너는 데이터 기반으로 소비 습관을 교정해 주는 스마트 소비 분석가야.
        {selected_month}에 가장 지출이 컸던 '{max_expense}' 카테고리를 중심으로 지출 패턴을 분석해 줘. (만약 '지출 없음'이라면 예산 계획을 세워줘)
        비난조의 팩트 폭격은 배제하고, 왜 해당 지출이 늘었는지 객관적으로 진단하게 만든 뒤 다음 달 예산 방어를 위한 현명하고 실용적인 전략을 제안해 줘.
        """
        
        chat_key = f"messages_4_{selected_month}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = [{"role": "assistant", "content": greeting_4}]
            
        chat_container_4 = st.container(height=550)
        with chat_container_4:
            for msg in st.session_state[chat_key]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
        user_input_4 = st.chat_input(f"{selected_month} 지출 관리에 대해 질문하기...", key=f"chat_in_4_{selected_month}")
        if user_input_4:
            with chat_container_4:
                with st.chat_message("user"): st.write(user_input_4)
                st.session_state[chat_key].append({"role": "user", "content": user_input_4})
                with st.chat_message("assistant"):
                    response_4 = model.generate_content(f"{sys_prompt_4}\n\n사용자 질문: {user_input_4}")
                    st.write(response_4.text)
                st.session_state[chat_key].append({"role": "assistant", "content": response_4.text})
