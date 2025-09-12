# TabMemoryFootprint.py
import streamlit as st
import json
import json_utils as ju  # JSON 관련 유틸리티
import os

class TabMemoryFootprint:
    def __init__(self):
        self.default_json = '''{
        "memory": [
            { "address": "0x00", "data": "0xA1" },
            { "address": "0x01", "data": "0xB2" },
            { "address": "0x02", "data": "0xC3" }
        ]
        }'''
        self.current_tab_key = 'tab2'
        self.current_dir = 'memory_footprint'

    def render(self):
        # 폴더 목록 가져오기
        folder_options = ju.get_folder_options(self.current_dir)
        selected_folder = st.sidebar.selectbox("폴더 선택", folder_options)

        # 파일 이름 입력 (확장자를 제외한 파일명 추출)
        file_name = st.sidebar.text_input("파일 이름 입력")
        base_file_name = os.path.splitext(file_name)[0]

        # JSON 저장 버튼 (현재 탭의 JSON 저장)
        if st.sidebar.button("JSON 저장"):
            json_filename = f"{base_file_name}.json"
            json_data = st.session_state.get(f'json_input_{self.current_tab_key}')
            if json_data:
                ju.save_json(json_filename, json_data, selected_folder)
 
        # JSON 파일 다운로드 버튼
        json_path = os.path.join(selected_folder, f"{base_file_name}.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as file:
                st.sidebar.download_button(
                    label="Download JSON",
                    data=file.read(),
                    file_name=f"{base_file_name}.json",
                    mime="application/json"
                )

        st.header("메모리 데이터 에디터")

        # JSON 입력 에디터 호출 (자동 교정 적용)
        json_input_raw = ju.json_editor(self.default_json, self.current_tab_key)

        # 메모리 데이터를 표로 표시 (예시로 JSON을 파싱하여 메모리 데이터를 보여줍니다)
        try:
            json_object = json.loads(json_input_raw)
            memory_data = json_object.get("memory", [])
            st.table(memory_data)

        except json.JSONDecodeError as e:
            st.stop()
        except Exception as e:
            st.error("메모리 데이터 렌더링 중 오류 발생: {}".format(e))
            st.text("변환된 JSON:")
            st.code(json_input_raw, language='json')

        # 현재 탭을 "tab2"으로 설정
        st.session_state['current_tab_key'] = self.current_tab_key
