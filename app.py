import streamlit as st
import google.generativeai as genai

# 웹 페이지 기본 설정
st.set_page_config(page_title="SK하이닉스 AI 에이전트", page_icon="🤖")
st.title("🤖 반도체 데이터 분석 마스터봇")
st.write("SK하이닉스 신입사원을 위한 데이터 분석 및 코딩 조수입니다.")

# 1. 사이드바에서 API 키 입력받기 (보안용)
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("발급받은 Gemini API Key를 입력하세요", type="password")

# 2. 대화 기록을 저장하기 위한 설정
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 이전 대화 기록을 화면에 모두 띄우기
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 4. 사용자 입력창
user_input = st.chat_input("질문을 입력하세요 (예: Pandas로 결측치 처리하는 방법 알려줘)")

if user_input:
    # 사용자의 질문을 화면에 띄우고 기록에 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # API 키가 입력되지 않았을 때의 경고
    if not api_key:
        st.warning("👈 왼쪽 사이드바에 Gemini API 키를 먼저 입력해주세요!")
    else:
        # 5. Gemini AI 두뇌 연결 및 답변 생성
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.5-flash')
        
        with st.chat_message("assistant"):
            # 시스템 프롬프트(페르소나)를 주입하여 답변 요청
            prompt = f"너는 SK하이닉스의 친절한 데이터 분석 선배야. 다음 질문에 다정하고 전문적으로 답해줘: {user_input}"
            response = model.generate_content(prompt)
            st.write(response.text)
            
        # AI의 답변을 기록에 저장
        st.session_state.messages.append({"role": "assistant", "content": response.text})