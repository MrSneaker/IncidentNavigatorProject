import logging
from flask import request, session
from . import llm
from ..config_llm.models import LLM
from ..auth.models import User

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

@llm.route('/llms', methods=['GET'])
def get_all_llm():
    llm_models = LLM.query.all()
    data = [model.to_dict() for model in llm_models]
    return {'error': 0, 'message': 'LLM models retrieved', 'llms': data}, 200

@llm.route('/llm/<llm_id>', methods=['GET'])
def get_llm(llm_id):
    llm_model = LLM.query.get(llm_id)
    if not llm_model:
        return {'error': 1, 'message': 'LLM model not found', 'data': None}, 404
    return {'error': 0, 'message': 'LLM model retrieved', 'data': llm_model.to_dict()}, 200

@llm.route('/llm', methods=['POST'])
def add_llm_route():
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 401

    user = User.get_user(id=user_id)
    if user is None or not user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    uri = request.json.get('uri', None)
    api_key = request.json.get('api_key', None)
    model = request.json.get('model', None)
    
    logging.error(f'body post llm : {request.json}')

    if not uri or not api_key or not model:
        return {'error': 3, 'message': 'URI, API key and model name are required', 'data': None}, 400

    return LLM.add_llm(uri, api_key, model)

@llm.route('/llm/<llm_id>', methods=['PUT'])
def update_llm(llm_id):
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 401

    user = User.get_user(id=user_id)
    if user is None or not user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    llm_model = LLM.query.get(llm_id)
    if not llm_model:
        return {'error': 3, 'message': 'LLM model not found', 'data': None}, 404

    uri = request.json.get('uri', None)
    api_key = request.json.get('api_key', None)

    if not uri and not api_key:
        return {'error': 4, 'message': 'No data to update', 'data': None}, 400

    if uri:
        llm_model.update_uri(uri)
    if api_key:
        llm_model.update_api_key(api_key)

    return {'error': 0, 'message': 'LLM model updated', 'data': llm_model.to_dict()}, 200

@llm.route('/llm/<llm_id>', methods=['DELETE'])
def delete_llm(llm_id):
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 401

    user = User.get_user(id=user_id)
    if user is None or not user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    llm_model = LLM.query.get(llm_id)
    if not llm_model:
        return {'error': 3, 'message': 'LLM model not found', 'data': None}, 404

    LLM.delete_llm(llm_model.id)

    return {'error': 0, 'message': 'LLM model deleted', 'data': None}, 200

@llm.route('/llm/<llm_id>/partial-api-key', methods=['GET'])
def get_partial_api_key(llm_id):
    llm_model = LLM.query.get(llm_id)
    if not llm_model:
        return {'error': 1, 'message': 'LLM model not found', 'data': None}, 404

    partial_api_key = llm_model.get_partial_api_key()
    return {'error': 0, 'message': 'Partial API key retrieved', 'data': {'partial_api_key': partial_api_key}}, 200
