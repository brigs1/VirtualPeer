from serpapi import GoogleSearch
import json
import requests
from bs4 import BeautifulSoup

def get_synonyms(term):
    base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/entity/autocomplete/"
    params = {"query": term}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        results = response.json()
        synonyms = [result['name'] for result in results]  # results가 리스트일 경우 처리
        print(f"Synonyms for {term}: {synonyms}")
        return synonyms
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return []

def get_pubmed_abstract(pmid):
    base_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        abstract = soup.find('div', class_='abstract-content').text.strip()
        return abstract
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return ""

# 사용자로부터 검색어 입력 받기
search_term = input("Enter search term: ")
synonyms = get_synonyms(search_term)
search_terms = [search_term] + synonyms

params = {
    "engine": "google_scholar",
    "q": " OR ".join(search_terms),  # 검색어와 동의어를 OR로 연결
    "api_key": "a93cea1cff7c2d17fa6af11d740dc06f4d9fb400471185a9527a5469453f86b1",
    "num": 20  # 한 번의 요청으로 가져올 결과 수
}

all_results = []
page = 1

while True:
    params["start"] = (page - 1) * params["num"]
    search = GoogleSearch(params)
    results = search.get_dict()
    
    if "organic_results" in results:
        all_results.extend(results["organic_results"])
        page += 1
    else:
        break

    # 페이지네이션을 위한 조건 (예: 5페이지까지만 가져오기)
    if page > 5:
        break

# 결과를 JSON 파일로 저장
with open('results.json', 'w') as f:
    json.dump(all_results, f, indent=4, ensure_ascii=False)

# 스키마에 맞게 데이터 변환
research_data = []
for result in all_results:
    title = result.get('title', '')
    snippet = result.get('snippet', '')  # snippet 필드를 초록으로 사용
    pub_id = result.get('pub_id', '')  # PubMed ID 추출 (가능한 경우)
    abstract = snippet  # 기본적으로 snippet을 사용

    # PubMed ID가 있는 경우 PubMed API를 통해 전체 초록 가져오기
    if pub_id:
        pubmed_abstract = get_pubmed_abstract(pub_id)
        if pubmed_abstract:
            abstract = pubmed_abstract

    authors = [author['name'] for author in result.get('publication_info', {}).get('authors', [])]
    keywords = []  # 키워드 정보가 없으므로 빈 리스트로 설정
    year = result.get('publication_info', {}).get('year', 0)
    journal = result.get('publication_info', {}).get('journal', '')

    research_data.append({
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "keywords": keywords,
        "year": year,
        "journal": journal
    })

schema = {
    "classes": [{
        "class": "Research",
        "vectorizer": "none",
        "vectorIndexType": "hnsw",
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
        ]
    }]
}

# 데이터와 스키마를 JSON 파일로 저장
output_data = {
    "schema": schema,
    "data": research_data
}

with open('research_data.json', 'w') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

print("Research data saved to research_data.json")