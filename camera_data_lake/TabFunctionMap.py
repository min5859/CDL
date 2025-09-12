# TabFunctionMap.py
import streamlit as st
import pandas as pd
import pickle
import os

class TabFunctionMap:
    def __init__(self, base_dir="./project/CDL/function_map"):
        self.base_dir = base_dir

    def render(self):
        st.header("📂 Function Map Loader (Pickle 파일)")

        # 현재 디렉토리 및 하위 디렉토리에서 피클 파일 목록 불러오기
        pickle_files = self.get_pickle_files_with_dirs()

        # 사이드바에서 피클 파일 선택
        selected_file = st.sidebar.selectbox("피클 파일 선택", pickle_files)

        # 피클 파일 로드 버튼
        if st.sidebar.button("피클 파일 로드"):
            try:
                # 선택한 파일을 로드하여 데이터프레임 형식으로 출력
                with open(selected_file, "rb") as f:
                    data = pickle.load(f)

                # 로드된 데이터가 여러 시트로 구성된 경우 (dict로 DataFrame이 저장된 경우)
                if isinstance(data, dict):
                    # 시트(탭) 목록 생성
                    sheet_names = list(data.keys())
                    tabs = st.tabs(sheet_names)

                    # 각 시트(탭)에 데이터를 표시
                    for i, sheet_name in enumerate(sheet_names):
                        with tabs[i]:
                            st.write(f"### {sheet_name} 데이터")
                            st.dataframe(data[sheet_name])

                # 로드된 데이터가 단일 DataFrame인 경우
                elif isinstance(data, pd.DataFrame):
                    st.write("### 데이터 프레임 미리보기")
                    st.dataframe(data)

                else:
                    st.error("로드된 데이터는 데이터프레임 형식이 아닙니다.")

            except Exception as e:
                st.error(f"피클 파일을 로드하는 중 오류가 발생했습니다: {e}")

    def get_pickle_files_with_dirs(self):
        """
        현재 디렉토리 및 하위 디렉토리에서 피클 파일 목록을 반환하는 함수
        Returns:
            list: 피클 파일의 전체 경로 목록
        """
        pickle_files = []
        try:
            # 재귀적으로 디렉토리와 하위 디렉토리 탐색
            for root, dirs, files in os.walk(self.base_dir):
                for file in files:
                    if file.endswith('.pkl') or file.endswith('.pickle'):
                        full_path = os.path.join(root, file)
                        pickle_files.append(full_path)
            return pickle_files
        except Exception as e:
            st.error(f"피클 파일 목록을 불러오는 중 오류가 발생했습니다: {e}")
            return []
