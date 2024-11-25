import requests
import json
from urllib.parse import quote

def get_umls_synonyms(term, api_key):
    base_url = "https://uts-ws.nlm.nih.gov/rest"
    
    # 검색 URL
    search_url = f"{base_url}/search/current?string={quote(term)}&apiKey={api_key}"
    
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('result', {}).get('results', [])
        
        synonyms = set()
        
        for result in results[:5]:  # 상위 5개 결과만 처리
            cui = result.get('ui')
            if cui:
                # 각 개념에 대한 동의어 가져오기
                atom_url = f"{base_url}/content/current/CUI/{cui}/atoms?apiKey={api_key}"
                atom_response = requests.get(atom_url)
                atom_response.raise_for_status()
                atom_data = atom_response.json()
                
                for atom in atom_data.get('result', []):
                    name = atom.get('name')
                    if name:
                        synonyms.add(name)
        
        return list(synonyms)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

# 사용 예시
# api_key = "your-api-key-here"  # UMLS API 키가 필요합니다
# synonyms = get_umls_synonyms("breast cancer", api_key)