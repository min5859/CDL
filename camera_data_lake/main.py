# app.py
import streamlit as st
from sidebar_utils import Sidebar
from TabTimingDiagram import TabTimingDiagram
from TabMemoryFootprint import TabMemoryFootprint
from TabGPTChatbot import TabGPTChatbot
from CameraChatbotMistral7b import CameraChatbotMistral7b
from TabFunctionMap import TabFunctionMap
from TabImageViewer import TabImageViewer

# 페이지 설정
st.set_page_config(
    page_title="Camera Data Lake",
    page_icon=":camera:",
    layout="wide",
    initial_sidebar_state="auto"
)

# Tab definitions
TABS = {
    "타이밍 다이어그램": TabTimingDiagram,
    "메모리": TabMemoryFootprint,
    "Function Map Loader": TabFunctionMap,
    "GPT Chatbot": TabGPTChatbot,
    "OpenSource Chatbot": CameraChatbotMistral7b,
    "Image Viewer": TabImageViewer,
}

#st.title("CDL")

# 사이드바 클래스 생성
sidebar = Sidebar(base_dir=".")

# 탭 상태 관리: 현재 활성화된 탭의 키를 세션에 저장하여 관리
if 'current_tab_key' not in st.session_state:
    st.session_state['current_tab_key'] = 'tab1'  # 기본값은 tab1

selected_tab = sidebar.render(list(TABS.keys()), st.session_state['current_tab_key'])

# Render the selected tab
if selected_tab in TABS:
    tab_class = TABS[selected_tab]
    tab_instance = tab_class()
    tab_instance.render()
