from serpapi import GoogleSearch
import json
import requests

def get_synonyms(term):
    base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/annotations"
    params = {"concept": term}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        results = response.json()
        synonyms = [result['synonym'] for result in results.get('annotations', [])]
        print(f"Synonyms for {term}: {synonyms}")
        return synonyms
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return []

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
    json.dump(all_results, f, indent=4)

# HTML 파일로 저장
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Google Scholar Search Results</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6; /* 줄 간격 설정 */
        }}
        .highlight {{
            background-color: yellow;
        }}
        .result h2 {{
            font-weight: normal; /* 제목 글씨 가늘게 */
        }}
        .result p {{
            font-weight: lighter; /* 본문 글씨 더 가늘게 */
        }}
    </style>
</head>
<body>
    <h1>Google Scholar Search Results for <span class="highlight">{search_term}</span></h1>
    <h2>Synonyms: {', '.join(synonyms)}</h2>
    <div id="results">
"""

# 검색 결과를 HTML로 변환
for index, result in enumerate(all_results):
    title = result.get('title', '').replace(search_term, f'<span class="highlight">{search_term}</span>')
    snippet = result.get('snippet', '').replace(search_term, f'<span class="highlight">{search_term}</span>')
    link = result.get('link', '#')
    authors = ', '.join([author['name'] for author in result.get('publication_info', {}).get('authors', [])])
    year = result.get('publication_info', {}).get('year', '')
    journal = result.get('publication_info', {}).get('journal', '')
    citations = result.get('inline_links', {}).get('cited_by', {}).get('total', 0)
    pdf_link = result.get('resources', [{}])[0].get('link', '')
    related_link = result.get('inline_links', {}).get('related_pages_link', '')

    html_content += f"""
    <div class="result" data-index="{index}" data-citations="{citations}">
        <h2><a href="{link}" target="_blank">{title}</a></h2>
        <p>{snippet}</p>
        <p>Authors: {authors}</p>
        <p>Year: {year}</p>
        <p>Journal: {journal}</p>
        <p>Citations: {citations}</p>
        <p><a href="{pdf_link}" target="_blank">PDF Link</a></p>
        <p><a href="{related_link}" target="_blank">Related Articles</a></p>
    </div>
    <hr>
    """

html_content += """
    </div>
</body>
</html>
"""

# HTML 파일로 저장
with open('results.html', 'w') as f:
    f.write(html_content)

print("Results saved to results.html")