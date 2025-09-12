import os
import glob
import sys
import faiss
import numpy as np
#from langchain.embeddings import OllamaEmbeddings
#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from sentence_transformers import SentenceTransformer

# .c 파일들이 저장된 디렉토리 경로
c_files_directory = '/root/project/wk_work/project/kafka-3.4.0-src'  # 실제 경로로 변경하세요.

# .c 파일들의 전체 경로 리스트 가져오기 (재귀적으로 검색)
c_file_paths = glob.glob(os.path.join(c_files_directory, '**', '*.py'), recursive=False)

# 디버깅을 위해 파일 경로 출력
print("찾은 .c 파일 경로들:", c_file_paths)

# 코드 스니펫 리스트 초기화
code_snippets = []

# 각 .c 파일의 내용을 읽어서 리스트에 추가
for file_path in c_file_paths:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
            code_snippets.append(code)
    except Exception as e:
        print(f"파일 {file_path} 읽기 중 오류 발생: {e}")

# code_snippets 리스트가 비어있는지 확인
if not code_snippets:
    print("코드 스니펫이 없습니다. 디렉토리 경로와 .c 파일의 존재 여부를 확인하세요.")
    sys.exit(1)

# 확인을 위해 첫 번째 코드 스니펫 출력
#print("첫 번째 코드 스니펫:\n", code_snippets[0])

## 임베딩 모델 로드
#model = SentenceTransformer('microsoft/codebert-base')
#
## 코드 스니펫에 대한 임베딩 생성
#embeddings = model.encode(code_snippets, convert_to_tensor=True)
#
## 벡터 스토어 생성 및 저장
#dimension = embeddings.shape[1]
#index = faiss.IndexFlatL2(dimension)
#index.add(embeddings)
#faiss.write_index(index, 'faiss_index.idx')
#
## 코드 매핑 저장
#import pickle
#code_id_mapping = {i: code for i, code in enumerate(code_snippets)}
#with open('code_id_mapping.pkl', 'wb') as f:
#    pickle.dump(code_id_mapping, f)

################### mistral #################
## 임베딩 함수 설정
#embedding_function = OllamaEmbeddings(model="mistral:7b")
#
## 임베딩 생성
#embeddings = embedding_function.embed_documents(code_snippets)
#
## 4. code_snippets와 embeddings를 결합하여 text_embeddings 생성
#text_embeddings = list(zip(code_snippets, embeddings))
#
## 벡터 스토어 생성
#vector_store = FAISS.from_embeddings(embeddings, code_snippets)
#
## 벡터 스토어 저장
#vector_store.save_local("faiss_vector_store")



