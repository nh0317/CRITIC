import os
import shutil
import tempfile

import pandas as pd
import streamlit as st
from chatbot.custom_chatbot import CodeChatbot

# 페이지 설정
st.set_page_config(page_icon="🤖", page_title="공시데이터 분석 챗봇")


# 캐시 디렉토리 생성 함수
def ensure_cache_dir():
    cache_dir = os.path.join(tempfile.gettempdir(), "streamlit_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


# 파일 캐시 저장 함수
def save_uploaded_file(uploaded_file, file_type):
    cache_dir = ensure_cache_dir()
    file_extension = os.path.splitext(uploaded_file.name)[1]
    cached_path = os.path.join(cache_dir, f"{file_type}_{uploaded_file.name}")

    with open(cached_path, "wb") as f:
        f.write(uploaded_file.read())
    return cached_path


# 사이드바 설정
with st.sidebar:
    st.title("📁 업로드된 파일")

    # 초기화 버튼
    if st.button("🔄 Reset"):
        # 캐시 파일 삭제
        cache_dir = ensure_cache_dir()
        shutil.rmtree(cache_dir, ignore_errors=True)
        # 모든 세션 상태 초기화
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("### 💻 코드 입력")
    if "code" in st.session_state:
        st.success(f"✅ 코드 입력 완료")
    else:
        st.info("질문을 입력해주세요")

# 메인 콘텐츠
st.title("코드 분석 도우미 챗봇")

# 세션 상태 초기화
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "code_entered" not in st.session_state:
    st.session_state.code_entered = False
if "code_upload" not in st.session_state:
    st.session_state.code_upload = False

if not st.session_state.code_entered:
    st.markdown("### 코드를 입력해주세요")
    code = st.text_input(
        "프로젝트 코드", key="code_input", placeholder=""
    )
    col1, col2 = st.columns([4, 1])  # 비율을 4:1로 설정하여 버튼의 크기 조절
    with col2:
        if st.button("확인", use_container_width=True):
            if code.strip():  # 공백만 입력된 경우 제외
                st.session_state.code = code
                st.session_state.code_entered = True
                st.rerun()
            else:
                st.error("코드를 입력해주세요")

# 챗봇 초기화 및 시작
else:

    @st.cache_resource
    def init_chatbot(code, code_path=None):
        chatbot = CodeChatbot(
            # code_path=code_path,
            code = code,
            code_uploaded=st.session_state.code_upload,
        )
        return chatbot

    if st.session_state.chatbot is None:
        with st.spinner("챗봇을 초기화 중입니다."):
            st.session_state.chatbot = init_chatbot(
                # st.session_state.get("code_path"),
                # st.session_state.code_path,
                # st.session_state.code_description,
                st.session_state.code,
            )
        st.success("챗봇 초기화가 완료되었습니다.")

    # 대화 기록 표시
    for conversation in st.session_state.messages:
        with st.chat_message(conversation["role"]):
            st.write(conversation["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input(f"질문을 입력해주세요"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        if prompt is not None:
            response = st.session_state.chatbot.invoke(prompt)
            generation = response["generation"]
            with st.chat_message("assistant"):
                st.markdown(generation)
            st.session_state.messages.append(
                {"role": "assistant", "content": generation}
            )
