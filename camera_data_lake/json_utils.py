# json_utils.py
import os
import json
import re
import streamlit as st
from streamlit_ace import st_ace

BASE_DIR = "."

def get_folder_options(current_dir):
    folder_options = []
    for root, dirs, files in os.walk(current_dir):
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            # 상대 경로로 표시
            relative_folder_path = os.path.relpath(folder_path, BASE_DIR)
            folder_options.append(relative_folder_path)
    # 루트 디렉토리도 추가
    folder_options.insert(0, current_dir)
    return folder_options

def save_json(file_name, content, selected_folder="."):
    save_path = os.path.join(BASE_DIR, selected_folder, file_name)
    with open(save_path, "w") as f:
        f.write(content)
    st.success(f"파일 저장 완료: {save_path}")

def load_json(file_name, selected_folder="."):
    load_path = os.path.join(BASE_DIR, selected_folder, file_name)
    with open(load_path, "r") as f:
        return f.read()

# JSON 교정 함수
def correct_json(json_input_raw):
    """
    입력된 JSON 문자열을 교정하여 잘못된 형식을 수정하고
    포맷팅된 JSON 문자열을 반환합니다.
    """
    try:
        # 탭 문자를 스페이스로 변환
        json_input_raw = json_input_raw.replace('\t', '    ')

        # 작은따옴표를 큰따옴표로 변경
        json_input_raw = json_input_raw.replace("'", '"')

        # 주석 및 트레일링 콤마 제거 함수
        def preprocess_json(json_str):
            # 주석 제거
            def remove_comments(s):
                pattern = r'/\*.*?\*/'
                return re.sub(pattern, '', s, flags=re.DOTALL)

            json_str = remove_comments(json_str)

            # 객체의 마지막 속성 뒤의 쉼표 제거
            json_str = re.sub(r',\s*}', '}', json_str)
            # 배열의 마지막 요소 뒤의 쉼표 제거
            json_str = re.sub(r',\s*\]', ']', json_str)
            return json_str

        # 큰따옴표 추가 함수 수정 (모든 키에 적용)
        def add_quotes_to_json_keys(json_str):
            # 큰따옴표로 감싸지 않은 키에 큰따옴표 추가
            # 문자열 리터럴은 그대로 둠
            pattern = r'(?<![\\"])'  # 앞에 백슬래시나 큰따옴표가 없는 위치
            pattern += r'([^\s"\'{},\[\]:]+)'  # 키로 사용할 수 있는 문자열 (공백, 따옴표, 구두점 제외)
            pattern += r'\s*:'  # 콜론과 공백
            json_str = re.sub(pattern, r'"\1":', json_str)
            return json_str

        # JSON 전처리: 작은따옴표를 큰따옴표로 변경, 주석 및 트레일링 콤마 제거
        json_input_preprocessed = preprocess_json(json_input_raw)
        # 큰따옴표 추가 (모든 키에 대해)
        corrected_json = add_quotes_to_json_keys(json_input_preprocessed)

        ## JSON 문자열을 파싱 (잘못된 형식이 있을 경우 오류 발생)
        json_object = json.loads(corrected_json)

        ## 교정된 JSON 문자열을 반환 (들여쓰기 4칸)
        #corrected_json = json.dumps(json_object, indent=4)

        # Streamlit을 통해 교정 완료 메시지 출력
        st.success("JSON 교정이 완료되었습니다!")
        return corrected_json

    except json.JSONDecodeError as e:
        st.error("JSON 구문 오류: {}".format(e))
        st.text("변환된 JSON:")
        st.code(corrected_json, language='json')
        return corrected_json

# JSON 입력 에디터 함수 (자동 교정 기능 추가)
def json_editor(default_json, tab_key, height=300):
    """
    Ace 에디터를 사용하여 JSON 입력을 위한 UI를 제공하고,
    자동으로 JSON을 교정하는 함수.
    """
    if f'json_input_{tab_key}' not in st.session_state:
        st.session_state[f'json_input_{tab_key}'] = default_json

    # Streamlit Ace 에디터
    json_input_raw = st_ace(
        value=st.session_state[f'json_input_{tab_key}'],
        language='json',
        theme='monokai',
        height=height,
        auto_update="True"
    )

    # 자동으로 JSON 교정
    return correct_json(json_input_raw)
