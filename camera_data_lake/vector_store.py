from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS  # 벡터 데이터베이스 사용 (예: FAISS)

# Hugging Face의 SentenceTransformer 모델 로드 (무료 모델 사용)
embeddings = SentenceTransformer('all-MiniLM-L6-v2')

# 예시 데이터 (텍스트 목록)
documents = ["문서 1 내용", "문서 2 내용", "문서 3 내용"]

# 문서 임베딩 생성
document_embeddings = embeddings.encode(documents)

# FAISS 벡터 스토어 생성
vector_store = FAISS.from_documents(documents, embeddings)

# 로컬에 벡터 스토어 저장 (예: 'vector_store' 디렉터리)
vector_store.save_local("vector_store")


######################## chat bot ####################
# 벡터 스토어 로드
index = faiss.read_index('faiss_index.idx')

# 코드 매핑 로드
with open('code_id_mapping.pkl', 'rb') as f:
    code_id_mapping = pickle.load(f)

# 임베딩 모델 로드
model = SentenceTransformer('microsoft/codebert-base')

# 로그 데이터 로드
log_data = parse_log_file('path_to_log_file.log')

# 챗봇 인터페이스 실행
while True:
    question = input("질문을 입력하세요 (종료하려면 'exit'):")
    if question.lower() == 'exit':
        break

    # 질문 임베딩 생성
    question_embedding = model.encode([question], convert_to_numpy=True)

    # 유사한 코드 스니펫 검색
    k = 5
    D, I = index.search(question_embedding, k)
    retrieved_codes = [code_id_mapping[i] for i in I[0]]

    # LLM 입력 생성
    context = "\n".join(retrieved_codes)
    llm_input = f"질문: {question}\n\n로그 데이터:\n{log_data}\n\n관련 코드:\n{context}"

    # 답변 생성
    response = llm(llm_input)
    print(f"답변: {response}")
