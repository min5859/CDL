# app.py
import streamlit as st
from sidebar_utils import Sidebar
from TabTimingDiagram import TabTimingDiagram
from TabMemoryFootprint import TabMemoryFootprint
from TabGPTChatbot import TabGPTChatbot
from CameraChatbotMistral7b import CameraChatbotMistral7b
from TabFunctionMap import TabFunctionMap

# 페이지 설정
st.set_page_config(
    page_title="Camera Data Lake",
    page_icon=":camera:",
    layout="wide",
    initial_sidebar_state="auto"
)
# 사이드바를 렌더링하고 선택된 탭 반환
str_td = "타이밍 다이어그램"
str_mf = "메모리"
str_fm = "Function Map Loader"
str_cb_gpt = "GPT Chatbot"
str_cb_os = "OpenSource Chatbot"
tabs = [str_td,str_mf,str_fm,str_cb_gpt,str_cb_os]

#st.title("CDL")

# 사이드바 클래스 생성
sidebar = Sidebar(base_dir=".")

# 탭 상태 관리: 현재 활성화된 탭의 키를 세션에 저장하여 관리
if 'current_tab_key' not in st.session_state:
    st.session_state['current_tab_key'] = 'tab1'  # 기본값은 tab1

selected_tab = sidebar.render(tabs, st.session_state['current_tab_key'])

# 탭1: 타이밍 다이어그램
if selected_tab == tabs[0]:
    tab1 = TabTimingDiagram()
    tab1.render()

# 탭2: 메모리 데이터
elif selected_tab == tabs[1]:
    tab2 = TabMemoryFootprint()
    tab2.render()

# Function Map Loader 탭 추가
elif selected_tab == tabs[2]:
    tab_function_map = TabFunctionMap()
    tab_function_map.render()

# 탭3: GPT Chatbot
elif selected_tab == tabs[3]:
    tab3 = TabGPTChatbot()
    tab3.render()

# Camera Chatbot Mistral 7B 탭 추가
elif selected_tab == tabs[4]:
    chatbot = CameraChatbotMistral7b()
    chatbot.render()