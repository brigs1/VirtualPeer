from flask import render_template, jsonify, request, current_app
import requests
import time

def get_entity_id(entity_name, concept_type=None, limit=10):
    base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/entity/autocomplete/"
    params = {"query": entity_name, "limit": limit}
    if concept_type:
        params["concept"] = concept_type

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
        results = response.json()
        print("리저트::", results)
        if results:
            entity_id = results[0].get("_id")
            print(f"Found entity ID: {entity_id} for entity: {entity_name}")
            return entity_id
        else:
            print(f"No results found for entity: {entity_name}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return None

def find_related_entities(entity_id):
    base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/relations"
    params = {"e1": entity_id}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
        related_entities = response.json()
        print(f"Found {len(related_entities)} related entities for ID: {entity_id}")

        # 논문 번호를 가져오는 로직 추가
        for entity in related_entities:
            if 'publications' in entity and isinstance(entity['publications'], int):
                pmid_count = entity['publications']
                pmids = fetch_pmids_for_relation(entity_id, entity['source'], entity['target'], pmid_count)
                entity['publications'] = pmids
                time.sleep(0.5)  # 각 요청 후 0.5초 대기

        return related_entities
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return []

@current_app.route('/')
def home():
    return render_template('index.html')

@current_app.route('/api/graph/<entity_name>', methods=['GET'])
def get_graph_data(entity_name):
    entity_id = get_entity_id(entity_name, concept_type="gene")
    if not entity_id:
        return jsonify({"error": "Entity ID not found"}), 404

    related_entities = find_related_entities(entity_id)
    elements = []

    # 각 노드의 type 속성을 포함하고 pmid를 추가하여 데이터 생성
    for item in related_entities:
        source_id = item['source']
        target_id = item['target']
        relation_type = item['type']
        pmid_list = item.get('publications', [])

        print(f"Processing source_id: {source_id}")
        source_type, source_name = source_id.split("_", 1)
        source_type = source_type[1:].capitalize()  # '@gene' -> 'Gene'
        print(f"source_type: {source_type}, source_name: {source_name}")

        print(f"Processing target_id: {target_id}")
        target_type, target_name = target_id.split("_", 1)
        target_type = target_type[1:].capitalize()  # '@chemical' -> 'Chemical'
        print(f"target_type: {target_type}, target_name: {target_name}")

        # 노드 추가 (type과 pmid 포함)
        if not any('id' in node['data'] and node['data']['id'] == source_id for node in elements):
            node_data = {
                "id": source_id,
                "label": source_name,
                "type": source_type,
                "pmid": pmid_list  # 관련 논문의 pmid 추가
            }
            elements.append({"data": node_data})
            print(f"Node data: {node_data}")  # 노드 데이터 출력

        if not any('id' in node['data'] and node['data']['id'] == target_id for node in elements):
            node_data = {
                "id": target_id,
                "label": target_name,
                "type": target_type,
                "pmid": pmid_list  # 관련 논문의 pmid 추가
            }
            elements.append({"data": node_data})
            print(f"Node data: {node_data}")  # 노드 데이터 출력

        # 엣지 추가 (relation 정보 포함)
        edge_data = {
            "source": source_id,
            "target": target_id,
            "relationship": relation_type,
            "publications": pmid_list  # 엣지에 pmid 추가
        }
        elements.append({"data": edge_data})
        print(f"Edge data: {edge_data}")  # 엣지 데이터 출력

    return jsonify(elements)

def fetch_pmids_for_relation(entity_id, source_id, target_id, pmid_count):
    # 논문 번호를 가져오는 로직
    base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocjson"
    params = {"pmids": ",".join([str(i) for i in range(1, pmid_count + 1)])}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
        results = response.json()
        pmids = [result['pmid'] for result in results.get('documents', [])]
        return pmids
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return []