import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import numpy as np

# ----------------------------------------------------------------------
# 1. 페이지 기본 설정 (와이드 레이아웃 적용)
# ----------------------------------------------------------------------
st.set_page_config(page_title="SK하이닉스 성장 파트너", page_icon="🚀", layout="wide")

# ----------------------------------------------------------------------
# 2. API 키 설정 (Streamlit Secrets 사용)
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
if d_day_join > 0:
    join_str = f"D-{d_day_join}"
elif d_day_join == 0:
    join_str = "D-Day (입사일! 🎉)"
else:
    join_str = f"D+{-d_day_join}"

# [월급날 D-Day 계산] - 매달 25일 (주말 보정)
year, month = today.year, today.month
payday = date(year, month, 25)

if today > payday: # 이번 달 월급날이 지났으면 다음 달로
    month += 1
    if month > 12:
        month = 1
        year += 1
    payday = date(year, month, 25)

# 주말 보정 로직 (토요일=5, 일요일=6)
if payday.weekday() == 5: 
    payday = payday - timedelta(days=1) # 금요일로 앞당김
elif payday.weekday() == 6:
    payday = payday - timedelta(days=2) # 금요일로 앞당김

d_day_pay = (payday - today).days
pay_str = f"D-{d_day_pay}" if d_day_pay > 0 else "D-Day (월급날! 💸)"

# ----------------------------------------------------------------------
# 4. 사이드바 구성 (프로필 및 위젯)
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("🏢 SK하이닉스 성장 파트너")
    
    # 4-1. 프로필 영역
    st.markdown("---")
    st.markdown("### 👤 Profile")
    st.markdown("**Name:** 안태경")
    st.markdown("**Team:** 양산기술")
    
    # 4-2. D-Day 카운터
    st.markdown("---")
    st.markdown("### ⏳ D-Day")
    st.info(f"**SK하이닉스 입사:** {join_str}")
    st.success(f"**다음 월급날:** {pay_str}")
    
    # 4-3. 컨디션 체크 및 시간
    st.markdown("---")
    st.markdown("### 🌡️ 오늘의 컨디션")
    condition = st.radio("오늘 기분이 어떠신가요?", ["😀 최고예요!", "😐 그저 그래요", "😥 피곤해요"], horizontal=True)
    
    st.markdown("---")
    st.markdown("### 🕒 현재 시간")
    st.write(now.strftime("%Y년 %m월 %d일 %H:%M"))
    st.markdown("---")
    
    # 4-4. 핵심 기능 네비게이션
    st.markdown("### 🎯 기능 선택")
    mode = st.radio("메뉴를 선택하세요:", 
                    ["🏠 홈 (메인 화면)", 
                     "🎯 목표 달성 코치", 
                     "📚 학습 코치", 
                     "💰 소비 습관 코치", 
                     "🏃‍♂️ 운동 코치", 
                     "📰 반도체 기술 뉴스"])

# ----------------------------------------------------------------------
# 5. 메인 화면 로직 (기능별 화면 분할 및 시각화)
# ----------------------------------------------------------------------
if mode == "🏠 홈 (메인 화면)":
    st.title(f"환영합니다, 안태경 님! 👋")
    st.write("SK하이닉스 양산기술 엔지니어님의 일상과 성장을 응원합니다.")
    st.write(f"오늘의 컨디션: **{condition}**")
    
    st.markdown("---")
    st.subheader("📊 성장 대시보드 오버뷰")
    
    # 요약 위젯 (Metrics)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="🎯 이번 주 목표 달성률", value="75%", delta="5% 상승")
    col2.metric(label="📚 이번 주 학습 시간", value="12시간", delta="2시간 증가")
    col3.metric(label="💰 예산 잔여 비율", value="42%", delta="-8% 지출")
    col4.metric(label="🏃‍♂️ 이번 주 운동 횟수", value="3회", delta="목표 달성")
    
    st.markdown("---")
    st.subheader("💡 오늘의 동기부여 명언")
    st.info("우리가 반복적으로 하는 행동이 바로 우리 자신이다. 그렇다면 탁월함은 행동이 아니라 습관이다. - 아리스토텔레스")

else:
    # ------------------------------------------------------------------
    # 6. 기능별 2분할 화면 구성 (왼쪽: 시각화, 오른쪽: 채팅창)
    # ------------------------------------------------------------------
    st.title(f"{mode}")
    
    # 화면을 6:4 비율로 분할
    col_visual, col_chat = st.columns([6, 4])
    
    # ------------------------------------------------------------------
    # [왼쪽 영역] 데이터 시각화 및 대시보드
    # ------------------------------------------------------------------
    with col_visual:
        st.subheader("📊 데이터 대시보드")
        
        if mode == "🎯 목표 달성 코치":
            st.write("이번 달 핵심 프로젝트 진행률")
            st.progress(70)
            st.markdown("- [x] 파이썬 데이터 분석 기초 완강\n- [ ] 대시보드 시각화 프로젝트 기획\n- [ ] SK하이닉스 양산 공정 프로세스 스터디")
            
        elif mode == "📚 학습 코치":
            st.write("최근 7일 학습 시간 흐름")
            chart_data = pd.DataFrame(np.random.randint(1, 4, size=(7, 1)), columns=['학습 시간(시간)'])
            st.bar_chart(chart_data)
            st.warning("📌 복습 키워드: Pandas 결측치 처리, 반도체 8대 공정")
            
            # ✨ 추가된 기능: 영단어 & 퀴즈 퀵 버튼
            st.markdown("---")
            st.subheader("💡 오늘의 스마트 학습")
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("📖 직무 영단어 3개 보기"):
                    st.session_state.quick_action = "글로벌 비즈니스 및 반도체 실무에 자주 쓰이는 필수 영단어 3개를 뜻과 예문과 함께 알려줘."
            with btn_col2:
                if st.button("📝 반도체/코딩 퀴즈 풀기"):
                    st.session_state.quick_action = "내가 복습할 수 있도록 파이썬(Pandas)이나 반도체 관련 객관식 퀴즈를 1개 내줘."
            
        elif mode == "💰 소비 습관 코치":
            st.write("카테고리별 지출 현황")
            chart_data = pd.DataFrame({"지출 금액": [400000, 250000, 150000, 100000]}, index=["식비", "교통비", "쇼핑", "기타"])
            st.bar_chart(chart_data)
            st.success("💡 AI 분석: 이번 주는 배달 음식 지출이 줄어 절약 포인트 50점을 획득하셨습니다!")
            
        elif mode == "🏃‍♂️ 운동 코치":
            st.write("주간 체중 및 달리기 거리 변화")
            chart_data = pd.DataFrame(np.random.randn(7, 2) / [50, 50] + [75.5, 3], columns=['체중(kg)', '달리기(km)'])
            st.line_chart(chart_data)
            
        elif mode == "📰 반도체 기술 뉴스":
            st.write("이번 주 핵심 반도체 트렌드 키워드")
            st.info("**1. HBM(고대역폭 메모리) 수요 폭발**\n\nAI 서버 수요 증가로 인해 SK하이닉스의 HBM 시장 점유율이 돋보이고 있습니다.")
            st.warning("**2. 차세대 미세 공정 경쟁 심화**\n\n수율(Yield) 안정화와 양산기술의 중요성이 그 어느 때보다 대두되고 있습니다.")

    # ------------------------------------------------------------------
    # [오른쪽 영역] AI 에이전트 채팅 (환영 메시지 기능 추가)
    # ------------------------------------------------------------------
    with col_chat:
        st.subheader("💬 AI 코치 1:1 상담")
        
        # 기능별 페르소나 및 환영 메시지 세팅
        agent_setup = {
            "🎯 목표 달성 코치": {
                "persona": "너는 목표를 세분화하고 일정 관리를 돕는 전략적 코치야. 안태경님의 목표를 작고 구체적인 할 일로 분해해 줘.",
                "greeting": "안녕하세요, 안태경 님! 🚀 이번 주 목표를 달성하기 위해 어떤 프로젝트를 준비 중이신가요? 막막한 일이 있다면 제가 작게 쪼개어 드릴게요!"
            },
            "📚 학습 코치": {
                "persona": "너는 체계적인 학습 전문가야. 반도체 관련 영단어와 파이썬 퀴즈를 내주고 피드백을 제공해 줘.",
                "greeting": "학습 코치입니다! 📚 오늘 공부할 파이썬 문법이나 반도체 공정 개념이 있나요? 영단어 공부나 복습 퀴즈가 필요하다면 왼쪽 버튼을 누르거나 편하게 말씀해 주세요!"
            },
            "💰 소비 습관 코치": {
                "persona": "너는 재무 상담가야. 소비 패턴을 분석하고, 예산 관리 및 절약을 위한 따끔하면서도 따뜻한 피드백을 제공해 줘.",
                "greeting": "이번 달 꼼꼼한 예산 관리를 도와드릴 재무 조수입니다. 💸 최근 지출 중 가장 아깝거나 잘 샀다고 생각하는 항목은 무엇인가요?"
            },
            "🏃‍♂️ 운동 코치": {
                "persona": "너는 건강 및 운동 전문가야. 사용자의 수준에 맞는 운동 루틴을 추천하고, 기록을 분석하여 점진적 목표를 제시해 줘.",
                "greeting": "오늘도 활기찬 하루! 🏃‍♂️ 오늘 예정된 운동 부위나 현재 컨디션을 알려주시면, 딱 맞는 운동 루틴을 추천해 드릴게요."
            },
            "📰 반도체 기술 뉴스": {
                "persona": "너는 반도체 산업 분석가야. 최신 반도체 기술 이슈를 데이터 기반으로 요약하고 양산기술 직무와 엮어 트렌드를 알려 줘.",
                "greeting": "최신 반도체 트렌드를 배달해 드립니다. 📰 오늘 화면 왼쪽에 뜬 뉴스 중 특별히 더 깊게 알아보고 싶은 이슈나 키워드가 있나요?"
            }
        }
        
        system_prompt = agent_setup[mode]["persona"]
        greeting_msg = agent_setup[mode]["greeting"]

        # 💡 모드가 변경되면 채팅 기록을 초기화하고 환영 메시지를 첫 대화로 삽입!
        if "current_mode" not in st.session_state or st.session_state.current_mode != mode:
            st.session_state.messages = [{"role": "assistant", "content": greeting_msg}]
            st.session_state.current_mode = mode

        chat_container = st.container(height=400)
        
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        # 💡 버튼 클릭(quick_action)이 발생했거나, 사용자가 텍스트를 입력했거나 판별
        user_input = None
        if "quick_action" in st.session_state:
            user_input = st.session_state.quick_action
            del st.session_state.quick_action # 실행 후 삭제
        else:
            user_input = st.chat_input(f"{mode}에게 질문하기...")

        # 질문 입력 및 응답 로직
        if user_input:
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_input)
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                with st.chat_message("assistant"):
                    prompt = f"{system_prompt}\n(참고로 현재 사용자의 기분은 '{condition}' 상태야.)\n\n사용자 질문: {user_input}"
                    response = model.generate_content(prompt)
                    st.write(response.text)
                    
                st.session_state.messages.append({"role": "assistant", "content": response.text})
