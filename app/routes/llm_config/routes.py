import logging
from flask import request, session
from . import llmConf
from .models import LLMConfig
from ..auth.models import User

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

@llmConf.route('/llms', methods=['GET'])
def get_all_llm():
    """Fetch all LLM configurations from the database."""
    llm_models = LLMConfig.query.all()
    data = [model.to_dict() for model in llm_models]
    return {'error': 0, 'message': 'LLM models retrieved', 'llms': data}, 200

@llmConf.route('/llm/<llm_id>', methods=['GET'])
def get_llm(llm_id):
    """
    Fetch a specific LLM configuration by ID.
    Returns 404 if the LLM model is not found.
    """
    llm_model = LLMConfig.query.get(llm_id)
    if not llm_model:
        return {'error': 1, 'message': 'LLM model not found', 'data': None}, 404
    return {'error': 0, 'message': 'LLM model retrieved', 'data': llm_model.to_dict()}, 200

@llmConf.route('/llm', methods=['POST'])
def add_llm_route():
    """
    Create a new LLM configuration.
    Requires admin authentication.
    
    Expected JSON body:
    {
        "uri": "API endpoint URI",
        "api_key": "API key for authentication",
        "model": "Name of the model"
    }
    """
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

    return LLMConfig.add_llm(uri, api_key, model, False)

@llmConf.route('/llm/<llm_id>', methods=['PUT'])
def update_llm(llm_id):
    """
    Update an existing LLM configuration.
    Requires admin authentication.
    
    Expected JSON body (all fields optional):
    {
        "uri": "New API endpoint URI",
        "api_key": "New API key"
    }
    """
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 401

    user = User.get_user(id=user_id)
    if user is None or not user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    llm_model = LLMConfig.query.get(llm_id)
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

@llmConf.route('/llm/<llm_id>', methods=['DELETE'])
def delete_llm(llm_id):
    """
    Delete an existing LLM configuration.
    Requires admin authentication.
    """
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 401

    user = User.get_user(id=user_id)
    if user is None or not user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    llm_model = LLMConfig.query.get(llm_id)
    if not llm_model:
        return {'error': 3, 'message': 'LLM model not found', 'data': None}, 404

    LLMConfig.delete_llm(llm_model.id)
    return {'error': 0, 'message': 'LLM model deleted', 'data': None}, 200

@llmConf.route('/llm/<llm_id>/partial-api-key', methods=['GET'])
def get_partial_api_key(llm_id):
    """
    Retrieve a partially masked version of the API key for display purposes.
    Returns 404 if the LLM model is not found.
    """
    llm_model = LLMConfig.query.get(llm_id)
    if not llm_model:
        return {'error': 1, 'message': 'LLM model not found', 'data': None}, 404

    partial_api_key = llm_model.get_partial_api_key()
    return {'error': 0, 'message': 'Partial API key retrieved', 'data': {'partial_api_key': partial_api_key}}, 200

@llmConf.route('/select/<id>', methods=['POST'])
def select_llm(id):
    """Select a specific LLM configuration as the active model."""
    return LLMConfig.select_llm(id)