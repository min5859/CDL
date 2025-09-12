# sidebar_utils.py
import os
import streamlit as st
import json_utils as ju
import image_utils as iu
from datetime import datetime

def find_file(filename, search_path):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

class Sidebar:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir

    def render(self, tabs, current_tab_key):
        """
        사이드바 UI를 렌더링하고, 폴더 및 파일 이름을 선택하는 기능을 제공합니다.
        current_tab_key: 현재 활성화된 탭의 키를 받아서 해당 탭의 JSON을 저장하도록 처리
        """
        # 사이드바에 로고 이미지 추가
        logo_file = "IT_logo.webp"
        logo_path = find_file(logo_file, self.base_dir)

        if logo_path:
            st.sidebar.image(logo_path)
        else:
            st.write(f"File '{logo_file}' not found.")

        st.sidebar.header("탭 및 저장 설정")

        # 탭 선택 드롭다운 (LLM Chatbot 탭 추가)
        selected_tab = st.sidebar.selectbox("탭 선택", tabs, index=0)

        # 선택된 탭을 반환
        return selected_tab
