import streamlit as st
from chatbot_base import ChatbotBase
from langchain_community.chat_models import ChatOllama

class CameraChatbotMistral7b(ChatbotBase):
    def __init__(self):
        super().__init__()
        # 사용 가능한 모델 목록 정의
        self.available_models = [
            "mistral:7b",
            "gemma2:latest",
            "llama3.2:latest",
        ]
        # 기본 설정
        self.selected_model = "mistral:7b"
        self.temperature = 0.7  # 기본 temperature 값
        self.llm = None
    
    def initialize_llm(self):
        """선택된 모델과 temperature로 LLM 초기화"""
        self.llm = ChatOllama(
            model=self.selected_model,
            temperature=self.temperature
        )

    def render(self):
        st.header("💬 OpenSource Chatbot")
        
        # Sidebar에 모델 설정 추가
        with st.sidebar:
            st.header("Model Settings")
            
            # 모델 선택
            self.selected_model = st.selectbox(
                "Choose LLM Model",
                options=self.available_models,
                index=self.available_models.index(self.selected_model)
            )
            
            # Temperature 조절 슬라이더
            self.temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="Higher values make the output more creative and diverse, lower values make it more focused and deterministic"
            )
            
            # Temperature 값에 따른 설명 표시
            temp_description = (
                "Conservative 🎯" if self.temperature < 0.5
                else "Balanced ⚖️" if self.temperature < 1.0
                else "Creative 🎨" if self.temperature < 1.5
                else "Experimental 🔬"
            )
            st.caption(f"Current Temperature Style: {temp_description}")
            
            # 현재 설정 정보 표시
            st.info(f"Model: {self.selected_model}\nTemperature: {self.temperature}")
            
            # 모델이나 temperature가 변경되면 LLM 재초기화
            settings_changed = (
                st.session_state.get('last_model') != self.selected_model or
                st.session_state.get('last_temperature') != self.temperature
            )
            
            if not self.llm or settings_changed:
                self.initialize_llm()
                st.session_state['last_model'] = self.selected_model
                st.session_state['last_temperature'] = self.temperature

        # 파일 선택 (ChatbotBase에서 제공)
        self.select_file()

        # 세션 상태에 메시지 저장소가 없으면 초기화
        self.initialize_messages()

        # 기존 대화 기록을 화면에 표시
        self.display_messages()

        # 사용자 질문 입력 처리
        if prompt := st.chat_input():
            # 파일 내용을 포함한 질문 생성 (ChatbotBase에서 제공)
            combined_prompt = self.prepare_combined_prompt(prompt)

            # 질문에 대한 응답 생성 (파일 내용 기반)
            response = self.generate_response(combined_prompt)

            # 응답을 화면에 표시하고 대화 기록에 추가
            st.session_state["messages"].append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

    def generate_response(self, user_prompt):
        """
        선택된 Ollama 모델을 사용하여 응답을 생성하는 함수
        Args:
            user_prompt: 사용자가 입력한 질문
        """
        try:
            response = self.llm.invoke(user_prompt)
            return response.content
        except Exception as e:
            return f"Error: {str(e)}"