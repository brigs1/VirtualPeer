# # from flask import Flask, jsonify
# # from flask_cors import CORS
# # import requests

# # app = Flask(__name__)
# # CORS(app)  # CORS 활성화

# # def get_entity_id(bioconcept_name, concept_type=None, limit=10):
# #     base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/entity/autocomplete/"
# #     params = {"query": bioconcept_name, "limit": limit}
# #     if concept_type:
# #         params["concept"] = concept_type

# #     response = requests.get(base_url, params=params)
# #     if response.status_code == 200:
# #         results = response.json()
# #         if results:
# #             entity_id = results[0].get("_id")
# #             print(f"Found entity ID: {entity_id} for concept: {bioconcept_name}")
# #             return entity_id
# #     print(f"No entity ID found for concept: {bioconcept_name}")
# #     return None

# # def find_related_entities(entity_id):
# #     base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/relations"
# #     params = {"e1": entity_id}

# #     response = requests.get(base_url, params=params)
# #     if response.status_code == 200:
# #         related_entities = response.json()
# #         print(f"Found {len(related_entities)} related entities for ID: {entity_id}")
# #         return related_entities
# #     print(f"No related entities found for ID: {entity_id}")
# #     return []

# # @app.route('/')
# # def home():
# #     return "Welcome to the PubTator3 Graph API. Use /api/graph/<bioconcept_name> to get graph data."

# # @app.route('/api/graph/<bioconcept_name>', methods=['GET'])
# # def get_graph_data(bioconcept_name):
# #     entity_id = get_entity_id(bioconcept_name, concept_type="gene")
# #     if not entity_id:
# #         return jsonify({"error": "Entity ID not found"}), 404

# #     related_entities = find_related_entities(entity_id)
# #     elements = []

# #     # 각 노드의 type 속성을 포함하여 데이터 생성
# #     for item in related_entities:
# #         source_id = item['source']
# #         target_id = item['target']
# #         relation_type = item['type']
# #         publications_count = item.get('publications', 0)

# # # `@GENE` 같은 접두사를 제거하고 단순화
# #         source_type, source_name = source_id.split("_", 1)
# #         source_type = source_type[1:].capitalize()  # '@gene' -> 'Gene' (접두사 제거 후 첫 글자 대문자화)

# #         target_type, target_name = target_id.split("_", 1)
# #         target_type = target_type[1:].capitalize()  # '@chemical' -> 'Chemical'

# #         # 노드 추가 (type 포함)
# #         elements.append({"data": {"id": source_id, "label": source_name, "type": source_type}})
# #         elements.append({"data": {"id": target_id, "label": target_name, "type": target_type}})

# #         # 엣지 추가
# #         elements.append({
# #             "data": {
# #                 "source": source_id,
# #                 "target": target_id,
# #                 "relationship": relation_type,
# #                 "publications": publications_count
# #             }
# #         })

# #     return jsonify(elements)

# # if __name__ == '__main__':
# #     app.run(debug=True, port=5001)

# from flask import Flask, jsonify
# from flask_cors import CORS
# import requests

# app = Flask(__name__)
# CORS(app)  # CORS 활성화

# # def get_entity_id(bioconcept_name, concept_type=None, limit=10):
# #     base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/entity/autocomplete/"
# #     params = {"query": bioconcept_name, "limit": limit}
# #     if concept_type:
# #         params["concept"] = concept_type

# #     response = requests.get(base_url, params=params)
# #     if response.status_code == 200:
# #         results = response.json()
# #         if results:
# #             entity_id = results[0].get("_id")
# #             print(f"Found entity ID: {entity_id} for concept: {bioconcept_name}")
# #             return entity_id
# #     print(f"No entity ID found for concept: {bioconcept_name}")
# #     return None

# def get_entity_id(bioconcept_name, concept_type=None, limit=10):
#     base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/entity/autocomplete/"
#     params = {"query": bioconcept_name, "limit": limit}
#     if concept_type:
#         params["concept"] = concept_type

#     try:
#         response = requests.get(base_url, params=params)
#         response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
#         results = response.json()
#         if results:
#             entity_id = results[0].get("_id")
#             print(f"Found entity ID: {entity_id} for concept: {bioconcept_name}")
#             return entity_id
#         else:
#             print(f"No results found for concept: {bioconcept_name}")
#     except requests.exceptions.HTTPError as http_err:
#         print(f"HTTP error occurred: {http_err}")
#     except Exception as err:
#         print(f"Other error occurred: {err}")

#     return None


# def find_related_entities(entity_id):
#     base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/relations"
#     params = {"e1": entity_id}

#     response = requests.get(base_url, params=params)
#     if response.status_code == 200:
#         related_entities = response.json()
#         print(f"Found {len(related_entities)} related entities for ID: {entity_id}")
#         return related_entities
#     print(f"No related entities found for ID: {entity_id}")
#     return []

# @app.route('/')
# def home():
#     return "Welcome to the PubTator3 Graph API. Use /api/graph/<bioconcept_name> to get graph data."

# @app.route('/api/graph/<bioconcept_name>', methods=['GET'])
# def get_graph_data(bioconcept_name):
#     entity_id = get_entity_id(bioconcept_name, concept_type="gene")
#     if not entity_id:
#         return jsonify({"error": "Entity ID not found"}), 404

#     related_entities = find_related_entities(entity_id)
#     elements = []

#     # 각 노드의 type 속성을 포함하고 pmid를 추가하여 데이터 생성
#     for item in related_entities:
#         source_id = item['source']
#         target_id = item['target']
#         relation_type = item['type']
#         pmid_list = item.get('publications', [])

#         source_type, source_name = source_id.split("_", 1)
#         source_type = source_type[1:].capitalize()  # '@gene' -> 'Gene'

#         target_type, target_name = target_id.split("_", 1)
#         target_type = target_type[1:].capitalize()  # '@chemical' -> 'Chemical'

#         # 노드 추가 (type과 pmid 포함)
#         elements.append({
#             "data": {
#                 "id": source_id, 
#                 "label": source_name, 
#                 "type": source_type,
#                 "pmid": pmid_list  # 관련 논문의 pmid 추가
#             }
#         })
#         elements.append({
#             "data": {
#                 "id": target_id, 
#                 "label": target_name, 
#                 "type": target_type,
#                 "pmid": pmid_list  # 관련 논문의 pmid 추가
#             }
#         })

#         # 엣지 추가
#         elements.append({
#             "data": {
#                 "source": source_id,
#                 "target": target_id,
#                 "relationship": relation_type,
#                 "publications": pmid_list  # 엣지에 pmid 추가
#             }
#         })

#     return jsonify(elements)

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)

from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # CORS 활성화

def get_entity_id(entity_name, concept_type=None, limit=10):
    base_url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/entity/autocomplete/"
    params = {"query": entity_name, "limit": limit}
    if concept_type:
        params["concept"] = concept_type

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
        results = response.json()
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

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        related_entities = response.json()
        print(f"Found {len(related_entities)} related entities for ID: {entity_id}")
        return related_entities
    print(f"No related entities found for ID: {entity_id}")
    return []

@app.route('/')
def home():
    return "Welcome to the PubTator3 Graph API. Use /api/graph/<entity_name> to get graph data."

@app.route('/api/graph/<entity_name>', methods=['GET'])
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

        source_type, source_name = source_id.split("_", 1)
        source_type = source_type[1:].capitalize()  # '@gene' -> 'Gene'

        target_type, target_name = target_id.split("_", 1)
        target_type = target_type[1:].capitalize()  # '@chemical' -> 'Chemical'

        # 노드 추가 (type과 pmid 포함)
        elements.append({
            "data": {
                "id": source_id, 
                "label": source_name, 
                "type": source_type,
                "pmid": pmid_list  # 관련 논문의 pmid 추가
            }
        })
        elements.append({
            "data": {
                "id": target_id, 
                "label": target_name, 
                "type": target_type,
                "pmid": pmid_list  # 관련 논문의 pmid 추가
            }
        })

        # 엣지 추가
        elements.append({
            "data": {
                "source": source_id,
                "target": target_id,
                "relationship": relation_type,
                "publications": pmid_list  # 엣지에 pmid 추가
            }
        })

    return jsonify(elements)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
