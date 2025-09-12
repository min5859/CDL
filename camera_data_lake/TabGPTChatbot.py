import streamlit as st
from chatbot_base import ChatbotBase
from openai import OpenAI

class TabGPTChatbot(ChatbotBase):
    def __init__(self):
        super().__init__()

    def render(self):
        st.header("💬 Chatbot (GPT)")

        # 사이드바에서 OpenAI API 키 입력
        openai_api_key = st.text_input(
            "OpenAI API Key",
            key="chatbot_api_key",
            type="password",
            value=""
            )

        # 파일 선택 (ChatbotBase에서 제공)
        self.select_file()

        # 세션 상태에 메시지 저장소가 없으면 초기화
        self.initialize_messages()

        # 기존 대화 기록을 화면에 표시
        self.display_messages()

        # 사용자 질문 입력 처리
        if prompt := st.chat_input():
            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()

            # 파일 내용을 포함한 질문 생성 (ChatbotBase에서 제공)
            combined_prompt = self.prepare_combined_prompt(prompt)

            # 질문에 대한 응답 생성 (파일 내용 기반)
            response = self.generate_response(openai_api_key, combined_prompt)

            # GPT 응답을 화면에 표시하고 대화 기록에 추가
            st.session_state["messages"].append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

    def generate_response(self, openai_api_key, user_prompt):
        """
        OpenAI GPT 모델을 사용하여 응답을 생성하는 함수
        Args:
            api_key: OpenAI API 키
            user_prompt: 사용자가 입력한 질문
        """
        client = OpenAI(api_key=openai_api_key)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=user_prompt
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
