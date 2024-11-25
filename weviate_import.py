import json
import os
import weaviate
from weaviate.auth import AuthApiKey
from transformers import AutoTokenizer, AutoModel
import torch
from tqdm import tqdm  # tqdm 라이브러리 임포트
from dotenv import load_dotenv  # python-dotenv 라이브러리 임포트

# .env 파일에서 환경 변수 읽기
load_dotenv()

# 환경 변수에서 Weaviate 클러스터 URL 및 API 키 설정
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

# Weaviate 클라우드에 연결
client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=AuthApiKey(WEAVIATE_API_KEY)
)

# Weaviate 클라이언트가 준비되었는지 확인
if not client.is_ready():
    raise Exception("Weaviate 클라이언트가 준비되지 않았습니다.")

# 기존 클래스 삭제 (필요한 경우)
try:
    client.schema.delete_class("Research")
except weaviate.exceptions.UnexpectedStatusCodeException as e:
    if e.status_code != 404:
        raise e

# Weaviate 스키마 정의
schema = {
    "classes": [{
        "class": "Research",
        "vectorizer": "none",  # 외부 벡터화 모델 사용
        "vectorIndexType": "hnsw",
        "vectorIndexConfig": {
            "vectorCacheMaxObjects": 1000000,
            "distance": "cosine"
        },
        "properties": [
            {
                "name": "title",
                "dataType": ["text"]
            },
            {
                "name": "abstract",
                "dataType": ["text"]
            },
            {
                "name": "authors",
                "dataType": ["text[]"]
            },
            {
                "name": "keywords",
                "dataType": ["text[]"]
            },
            {
                "name": "year",
                "dataType": ["int"]
            },
            {
                "name": "journal",
                "dataType": ["text"]
            }
        ],
        "vectorIndexSize": 768  # 벡터 차원 설정
    }]
}

# Weaviate에 스키마 추가
client.schema.create(schema)

# 모델 및 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained("pritamdeka/S-PubMedBert-MS-MARCO")
model = AutoModel.from_pretrained("pritamdeka/S-PubMedBert-MS-MARCO")

# 텍스트 벡터화 함수
def embed_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy().tolist()  # numpy 배열을 리스트로 변환

# research_data.json 파일 읽기
with open('research_data.json', 'r') as f:
    data = json.load(f)

# 데이터 임베딩 및 Weaviate에 저장
for item in tqdm(data['data'], desc="Embedding and uploading data"):
    # 텍스트 데이터 벡터화
    title_vector = embed_text(item['title'])
    abstract_vector = embed_text(item['abstract'])
    
    # 제목과 초록 벡터의 평균 계산
    combined_vector = [(t + a) / 2 for t, a in zip(title_vector, abstract_vector)]
    
    # Weaviate에 데이터 저장
    client.data_object.create(
        {
            "title": item['title'],
            "abstract": item['abstract'],
            "authors": item['authors'],
            "keywords": item['keywords'],
            "year": item['year'],
            "journal": item['journal']
        },
        "Research",
        vector=combined_vector  # 벡터를 명시적으로 지정
    )

print("Data imported to Weaviate successfully.")