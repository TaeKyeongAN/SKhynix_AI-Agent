import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="SK하이닉스 성장 파트너", page_icon="🚀")
st.title("🚀 SK하이닉스 주니어 성장 파트너")

# 2. API 키 설정 (Streamlit Secrets 사용)
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.5-flash')

# 3. 사이드바에서 기능 선택
mode = st.sidebar.selectbox("필요한 코치를 선택하세요", 
    ["목표 달성 코치", "학습 코치", "소비 습관 코치", "운동 코치", "반도체 기술 뉴스 큐레이터"])

# 기능별 페르소나 설정
personas = {
    "목표 달성 코치": "너는 목표를 세분화하고 일정 관리를 돕는 전략적 코치야. 사용자의 목표를 작고 구체적인 할 일로 분해해 줘.",
    "학습 코치": "너는 체계적인 학습 전문가야. 공부 계획을 생성하고, 효율적인 복습 타이밍을 추천하며, 관련 퀴즈를 만들어 줘.",
    "소비 습관 코치": "너는 재무 상담가야. 소비 패턴을 분석하고, 예산 관리 및 절약을 위한 따끔하면서도 따뜻한 피드백을 제공해 줘.",
    "운동 코치": "너는 건강 및 운동 전문가야. 사용자의 수준에 맞는 운동 루틴을 추천하고, 기록을 분석하여 점진적 목표를 제시해 줘.",
    "반도체 기술 뉴스 큐레이터": "너는 반도체 산업 분석가야. 최신 반도체 기술 이슈를 데이터 기반으로 요약하고 핵심 트렌드를 알려 줘."
}

system_prompt = personas[mode]

# 4. 대화 기록 관리
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기능이 바뀌면 대화 초기화
if "current_mode" not in st.session_state or st.session_state.current_mode != mode:
    st.session_state.messages = []
    st.session_state.current_mode = mode

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. 질문 입력 및 AI 응답 생성
if user_input := st.chat_input(f"{mode}에게 무엇을 도와드릴까요?"):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        prompt = f"{system_prompt}\n\n사용자 질문: {user_input}"
        response = model.generate_content(prompt)
        st.write(response.text)
        
    st.session_state.messages.append({"role": "assistant", "content": response.text})
