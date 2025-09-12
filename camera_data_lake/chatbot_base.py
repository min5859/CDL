import streamlit as st
from file_manager import FileManager

class ChatbotBase:
    def __init__(self, base_dir="./project/CDL/"):
        self.file_manager = FileManager(base_dir)
        self.file_content = None  # 파일 내용을 저장할 변수

        # session_state에 file_content가 없으면 초기화
        if "file_content" not in st.session_state:
            st.session_state.file_content = None

    def load_file_content(self, selected_folder, selected_file):
        """
        파일을 로드하여 st.session_state.file_content에 저장하는 함수
        Args:
            selected_folder: 선택된 폴더 경로
            selected_file: 선택된 파일 이름
        """
        file_path = f"{selected_folder}/{selected_file}"
        st.session_state.file_content = self.file_manager.load_file(file_path)

    def initialize_messages(self):
        """
        세션 상태에 메시지 저장소가 없으면 초기화하는 함수
        """
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    def display_messages(self):
        """
        기존 대화 기록을 화면에 표시하는 함수
        """
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

    def select_file(self):
        """
        사이드바에서 폴더와 파일을 선택할 수 있는 UI 제공
        """
        st.sidebar.subheader("파일 선택")
        folders = self.file_manager.get_all_folders_in_directory()

        if folders:
            selected_folder = st.sidebar.selectbox("폴더를 선택하세요", [""] + folders)
            files = self.file_manager.get_files_in_folder(selected_folder)

            if files:
                selected_file = st.sidebar.selectbox("파일을 선택하세요", [""] + files)

                if st.sidebar.button("Attach"):
                    self.load_file_content(selected_folder, selected_file)

    def prepare_combined_prompt(self, user_prompt):
        """
        파일 내용을 포함한 질문을 생성하고, 메시지에 추가하는 공통 함수
        Args:
            user_prompt: 사용자가 입력한 질문
        Returns:
            str: 파일 내용을 포함한 질문 또는 일반 질문
        """
        # 사용자의 질문을 대화 히스토리에 추가
        st.session_state["messages"].append({"role": "user", "content": user_prompt})
        st.chat_message("user").write(user_prompt)

        if st.session_state.file_content:
            combined_prompt = f"파일 내용: {st.session_state.file_content}\n\n질문: {user_prompt}"
        else:
            combined_prompt = user_prompt

        messages = st.session_state.messages.copy() if "messages" in st.session_state else []
        messages.append({"role": "user", "content": combined_prompt})

        return messages
