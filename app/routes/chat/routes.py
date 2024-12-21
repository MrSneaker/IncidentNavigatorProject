import os
import json
import time
import datetime
from flask import request, Response, current_app
import google.generativeai as genai

from . import chat
from .models import Chat, Message
from .utils.jwt_utils import token_required, verify_jwt

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def get_uid():
    """
    Get user ID from JWT token
    """
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        payload = verify_jwt(token)['payload']
        return payload['uid']
    except Exception as e:
        return None
    
@chat.route('/list', methods=['GET'])
@token_required
def list_chat():
    """
    List all chats
    """
    
    # Get user ID
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    
    # Get all chats
    chats: list[Chat] = Chat.query.filter_by(user_id=user_id).all()
    # Convert to list of dictionaries
    chat_list = [{
        'id': chat.id,
        'name': chat.name,
        'created_at': int(chat.created_at.timestamp() * 1000),
        'updated_at': int(chat.last_updated().timestamp() * 1000)
    } for chat in chats]
    
    # Return the list of chats
    return {'error': 0, 'message': 'Chats found', 'data': chat_list}, 200


@chat.route('/new', methods=['POST'])   
@token_required
def new_chat():
    # Get user ID
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    
    # Create a new chat
    name = request.json.get('name', 'New Chat')
    chat = Chat.create(user_id, name)
    
    return {'error': 0, 'message': 'Chat created', 'data': {'id': chat.id}}, 201


# Delete chat
@chat.route('/delete', methods=['DELETE'])
@token_required
def delete_chat():
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    
    chat_id = request.json.get('id', None)
    if chat_id is None:
        return {'error': 4, 'message': 'Chat ID is required', 'data': None}, 400
    
    chat: Chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    if chat is None:
        return {'error': 5, 'message': 'Chat not found', 'data': None}, 404
    
    chat.delete()
    
    return {'error': 0, 'message': 'Chat deleted', 'data': None}, 200


@chat.route('/info', methods=['GET'])
@token_required
def get_chat():
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    
    chat_id = request.args.get('id', None)
    if chat_id is None:
        return {'error': 4, 'message': 'Chat ID is required', 'data': None}, 400
    
    print(chat_id, user_id)
    chat: Chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    if chat is None:
        return {'error': 5, 'message': 'Chat not found', 'data': None}, 404
    
    data = chat.to_dict()
    data.pop('user_id')
    return {'error': 0, 'message': 'Chat found', 'data': data}, 200

@chat.route('/rename', methods=['PUT'])
@token_required
def rename_chat():
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    
    chat_id = request.json.get('id', None)
    name = request.json.get('name', None)
    if chat_id is None:
        return {'error': 4, 'message': 'Chat ID is required', 'data': None}, 400
    if name is None:
        return {'error': 5, 'message': 'Name is required', 'data': None}, 400
    
    chat: Chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    if chat is None:
        return {'error': 6, 'message': 'Chat not found', 'data': None}, 404
    
    chat.rename(name)
    
    return {'error': 0, 'message': 'Chat renamed', 'data': None}, 200

# List messages
@chat.route('/msgs', methods=['GET'])
@token_required
def list_msgs():
    user_id = get_uid()
    chat_id = request.args.get('chat_id', None)
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    if chat_id is None:
        return {'error': 4, 'message': 'Chat ID is required', 'data': None}, 400
    
    chat: Chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    if chat is None:
        return {'error': 5, 'message': 'Chat not found', 'data': None}, 404
    
    messages = chat.get_messages()
    message_list = [{
        'source': 'user' if message.source else 'model',
        'parts': message.message
    } for message in messages]
    
    return {'error': 0, 'message': 'Messages found', 'data': {'chat_id': chat.id, 'messages': message_list}}, 200
    
    
@chat.route('/send', methods=['POST'])
@token_required
def send_msg():
    user_id = get_uid()
    chat_id = request.json.get('chat_id', None)
    message = request.json.get('parts', None)
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    if chat_id is None:
        return {'error': 4, 'message': 'Chat ID is required', 'data': None}, 400
    if message is None:
        return {'error': 5, 'message': 'Message is required', 'data': None}, 400
    
    chat: Chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    if chat is None:
        return {'error': 6, 'message': 'Chat not found', 'data': None}, 404
    
    history = chat.history()
    msg: Message = Message(user_id=user_id, chat_id=chat_id, message=message, source=True)
    chat.add_message(msg)
    
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=[""])
    gemini_chat = model.start_chat(history=history)
    response = gemini_chat.send_message(
        message,
        stream=True,
        generation_config=genai.types.GenerationConfig(
            temperature=1
        ))
    
    # return a stream of responses
    
    app = current_app._get_current_object()
    ctx = app.app_context()
    return app.response_class(
        convert_response(response, user_id, chat_id, ctx),
        mimetype="text"
    )
    

def convert_response(response, user_id, chat_id, ctx):
    full_response = ''
    for chunk in response:
        full_response += chunk.text
        # Split the response into words to make the response more human-like (optional)
        words = chunk.text.split(' ')
        for word in words:
            msg = {"choices": [{"delta": {"content": f"{word} "}, "finish_reason": None}]}
            yield f"data: {json.dumps(msg)}\n\n"
            time.sleep(0.1)

    final_chunk = {
        "choices": [{"delta": {"content": ""}, "finish_reason": "stop"}]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    
    with ctx:
        chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
        if chat:
            msg = Message(user_id=user_id, chat_id=chat_id, message=full_response, source=False)
            chat.add_message(msg)
    
    
    
    