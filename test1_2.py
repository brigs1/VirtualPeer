import json
import requests
import time

def get_synonyms(term):
    base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/entity/autocomplete/"
    params = {"query": term}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        results = response.json()
        synonyms = [result['name'] for result in results]
        print(f"Synonyms for {term}: {synonyms}")
        return synonyms
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return []

def get_pubtator_annotations(pmids):
    base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocjson"
    pmids_str = [str(pmid) for pmid in pmids]  # pmids 리스트의 모든 항목을 문자열로 변환
    params = {"pmids": ",".join(pmids_str), "full": "true"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        results = response.json()
        print(f"PubTator annotations for PMIDs {pmids}: {results}")  # 디버깅 정보 추가
        return results
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return {}

# 사용자로부터 검색어 입력 받기
search_term = input("Enter search term: ")
synonyms = get_synonyms(search_term)
search_terms = [search_term] + synonyms

# PubTator3 API를 사용하여 검색어와 동의어를 포함한 논문 정보 가져오기
pmids = []
for term in search_terms:
    search_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/search/"
    params = {"text": term}

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_results = response.json()
        pmids.extend([result['pmid'] for result in search_results.get('results', [])])
        print(f"Search results for {term}: {search_results}")
        time.sleep(0.33)  # 각 요청 후 0.33초 대기 (1초에 3회 호출 제한)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

# 중복된 PMID 제거
pmids = list(set(pmids))

# PubTator3 API를 사용하여 논문 정보 가져오기
annotations = get_pubtator_annotations(pmids)

# 스키마에 맞게 데이터 변환
research_data = []
for document in annotations.get('PubTator3', []):
    title = ""
    abstract = ""
    authors = []
    keywords = []
    year = 0
    journal = ""

    for passage in document.get('passages', []):
        if passage.get('infons', {}).get('type') == 'title':
            title = passage.get('text', '')
        elif passage.get('infons', {}).get('type') == 'abstract':
            abstract = passage.get('text', '')

    for infon in document.get('infons', {}).values():
        if infon.get('type') == 'author':
            authors.append(infon.get('name', ''))
        elif infon.get('type') == 'journal':
            journal = infon.get('name', '')
        elif infon.get('type') == 'year':
            year = int(infon.get('name', 0))

    research_data.append({
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "keywords": keywords,
        "year": year,
        "journal": journal
    })

    print(f"Processed document: {research_data[-1]}")

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