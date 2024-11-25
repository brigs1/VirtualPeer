import weaviate
from weaviate.auth import AuthApiKey
import json  # json 모듈 임포트
from transformers import AutoTokenizer, AutoModel
import torch, os
from dotenv import load_dotenv  # python-dotenv 라이브러리 임포트

# .env 파일에서 환경 변수 읽기
load_dotenv()

# 환경 변수에서 Weaviate 클러스터 URL 및 API 키 설정
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

# Weaviate 클라이언트 설정
client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=AuthApiKey(WEAVIATE_API_KEY)
)

# 모델 및 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained("pritamdeka/S-PubMedBert-MS-MARCO")
model = AutoModel.from_pretrained("pritamdeka/S-PubMedBert-MS-MARCO")

# 텍스트 벡터화 함수
def embed_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy().tolist()  # numpy 배열을 리스트로 변환

# 검색할 텍스트 (예시로 첫 번째 객체의 텍스트를 사용)
search_text = "organ axis having influence on brain"  # 실제 검색할 텍스트를 사용해야 합니다.
search_vector = embed_text(search_text)

# GraphQL 쿼리 작성
query = """
{
  Get {
    Research(
      nearVector: {
        vector: %s
        distance: 0.7
      }
    ) {
      title
      abstract
      authors
      keywords
      year
      journal
      _additional {
        id
        certainty
      }
    }
  }
}
""" % json.dumps(search_vector)

# 데이터 쿼리
result = client.query.raw(query)

# 결과 출력 및 매칭된 청크 조회
for item in result['data']['Get']['Research']:
    print(f"Title: {item['title']}")
    print(f"Abstract: {item['abstract']}")
    print(f"Authors: {', '.join(item['authors'])}")
    print(f"Keywords: {', '.join(item['keywords'])}")
    print(f"Year: {item['year']}")
    print(f"Journal: {item['journal']}")
    print(f"Certainty: {item['_additional']['certainty']}")
    print(f"ID: {item['_additional']['id']}")
    
    # 매칭된 청크의 텍스트 내용 조회
    object_id = item['_additional']['id']
    object_data = client.data_object.get_by_id(object_id)
    print(f"Matched Chunk Text: {object_data['properties']['abstract']}")
    print("-" * 80)