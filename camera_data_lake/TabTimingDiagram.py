# TabTimingDiagram.py
import streamlit as st
import wavedrom
import json
import json_utils as ju  # JSON 관련 유틸리티
import image_utils as iu
import os

class TabTimingDiagram:
    def __init__(self):
        self.default_json = '''{
        "signal": [
            { "name": "clk",  "wave": "p.....|..." },
            { "name": "data", "wave": "x.345x|=.x", "data": "A B C D" },
            { "name": "req",  "wave": "0.1..0|1.0" }
        ],
        "head": {
            "text": ["tspan", ["tspan", {"class":"info h3"}, "DDE"] ],
            "tock":0
        }
        }'''
        self.current_tab_key = 'tab1'
        self.current_dir = './project/CDL/timing_diagram'

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

        # 선택한 폴더의 파일 목록 가져오기
        if os.path.exists(selected_folder):
            files_in_folder = [f for f in os.listdir(selected_folder) if os.path.isfile(os.path.join(selected_folder, f))]
            if files_in_folder:
                selected_file = st.sidebar.selectbox("파일 선택", files_in_folder)
                if st.sidebar.button("선택한 JSON 파일 로드"):
                    load_path = os.path.join(selected_folder, selected_file)
                    try:
                        with open(load_path, "r", encoding="utf-8") as f:
                            json_input_loaded = f.read()
                        st.session_state[f'json_input_{self.current_tab_key}'] = json_input_loaded  # 세션 상태 업데이트
                        st.sidebar.success(f"{selected_file} 파일을 {selected_folder} 폴더에서 불러왔습니다.")
                    except Exception as e:
                        st.error(f"파일 로드 중 오류 발생: {e}")
            else:
                st.info("선택한 폴더에 파일이 없습니다.")
        else:
            st.error("선택한 폴더가 존재하지 않습니다.")


        # 이미지 저장 버튼 추가 (SVG & PNG)
        if st.sidebar.button("이미지 저장 (SVG & PNG)"):
            svg_filename = f"{base_file_name}.svg"
            png_filename = f"{base_file_name}.png"

            svg_path = os.path.join(selected_folder, svg_filename)
            png_path = os.path.join(selected_folder, png_filename)

            # SVG 저장
            svg_content = st.session_state.get('svg_content')
            if svg_content:
                iu.save_svg(svg_content, svg_path)
                st.sidebar.success(f"SVG 저장 완료: {svg_path}")

            # PNG 저장
            iu.convert_svg_to_png(svg_content, png_path)
            st.sidebar.success(f"PNG 저장 완료: {png_path}")

        # SVG 파일 다운로드 버튼
        svg_path = os.path.join(selected_folder, f"{base_file_name}.svg")
        if os.path.exists(svg_path):
            with open(svg_path, "r") as file:
                st.sidebar.download_button(
                    label="Download SVG",
                    data=file.read(),
                    file_name=f"{base_file_name}.svg",
                    mime="image/svg+xml"
                )

        # PNG 파일 다운로드 버튼
        png_path = os.path.join(selected_folder, f"{base_file_name}.png")
        if os.path.exists(png_path):
            with open(png_path, "rb") as file:
                st.sidebar.download_button(
                    label="Download PNG",
                    data=file,
                    file_name=f"{base_file_name}.png",
                    mime="image/png"
                )

        st.header("타이밍 다이어그램 에디터")

        # JSON 입력 에디터 호출 (자동 교정 적용)
        json_input_raw = ju.json_editor(self.default_json, self.current_tab_key)

        # 다이어그램 렌더링 및 표시
        try:
            json_object = json.loads(json_input_raw)
            diagram = wavedrom.render(json_input_raw)
            svg_content = diagram.tostring()
            st.markdown(svg_content, unsafe_allow_html=True)

            # SVG 콘텐츠를 세션에 저장 (이미지 저장에 사용)
            st.session_state['svg_content'] = svg_content

        except json.JSONDecodeError as e:
            st.stop()
        except Exception as e:
            st.error("다이어그램 렌더링 중 오류 발생: {}".format(e))
            st.text("변환된 JSON:")
            st.code(json_input_raw, language='json')

        # 현재 탭을 "tab1"으로 설정
        st.session_state['current_tab_key'] = self.current_tab_key
