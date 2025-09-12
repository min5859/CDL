import os
import pickle
import streamlit as st

class FileManager:
    def __init__(self, base_dir="./project/CDL"):
        """
        base_dir: 네트워크 디바이스의 경로 또는 로컬 경로
        """
        self.base_dir = base_dir  # 네트워크 디바이스 또는 로컬 경로 설정

    def get_all_folders_in_directory(self):
        """
        base_dir에서 모든 폴더 목록을 반환하는 함수
        """
        folder_paths = []
        try:
            # base_dir의 하위 폴더들 탐색
            for root, dirs, files in os.walk(self.base_dir):
                for dir_name in dirs:
                    full_path = os.path.relpath(os.path.join(root, dir_name), self.base_dir)
                    folder_paths.append(full_path)

            if not folder_paths:
                st.sidebar.warning("선택할 폴더가 없습니다.")
            return folder_paths
        except Exception as e:
            st.sidebar.error(f"폴더 목록을 불러오는 중 오류가 발생했습니다: {e}")
            return []

    def get_files_in_folder(self, folder_path):
        """
        선택한 폴더의 파일 목록을 반환하는 함수
        Args:
            folder_path: 사용자가 선택한 폴더의 경로
        """
        try:
            files = [f for f in os.listdir(os.path.join(self.base_dir, folder_path)) if os.path.isfile(os.path.join(self.base_dir, folder_path, f))]
            return files
        except Exception as e:
            st.sidebar.error(f"파일 목록을 불러오는 중 오류가 발생했습니다: {e}")
            return []

    def load_file(self, file_path):
        """
        파일을 로드하여 내용을 반환하는 함수
        Args:
            file_path: 사용자가 선택한 파일의 경로 (네트워크 경로 포함)
        """
        try:
            file_extension = file_path.split('.')[-1].lower()
            full_path = os.path.join(self.base_dir, file_path)

            if file_extension == "txt":
                # 텍스트 파일 로드
                with open(full_path, "r", encoding="utf-8") as file:
                    return file.read()

            elif file_extension == "pkl":
                # 피클 파일 로드
                with open(full_path, "rb") as file:
                    return pickle.load(file)

            else:
                # 다른 파일 형식은 바이너리로 처리
                with open(full_path, "rb") as file:
                    return file.read()

        except Exception as e:
            st.sidebar.error(f"파일을 로드하는 중 오류가 발생했습니다: {e}")
            return None

