from typing import List
import requests
from flask import request, Response, current_app
from werkzeug.exceptions import ClientDisconnected

from . import chat
from .utils.token import token_required, verify_jwt
from .utils.models import Chat, Message, Ticket
from .utils.llm import LLMResponse, invoke_llm



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

@chat.route('/new', methods=['POST'])   
@token_required
def new():
    # Get user ID
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401

    # Create a new chat
    name = request.json.get('name', 'New Chat')
    if Chat.create(user_id, name) is not None:
        return {'error': 0, 'message': 'Chat created', 'data': None}, 200
    return {'error': 4, 'message': 'Failed to create chat', 'data': None}, 500

@chat.route('/delete', methods=['DELETE'])
@token_required
def delete():
    # Get user ID
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    
    # Get Chat
    chat_id = request.json.get('id', None)
    chat = Chat.get(user_id, chat_id)
    if chat is None:
        return {'error': 4, 'message': f"Chat \'{chat_id}\' not found", 'data': None}, 404
    
    # Delete chat
    if chat.delete():
        return {'error': 0, 'message': 'Chat deleted', 'data': None}, 200
    return {'error': 5, 'message': "Failed to delete chat", 'data': None}, 500


@chat.route('/list', methods=['GET'])
@token_required
def list():
    # Get user ID
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    
    # Get all chats
    chats = Chat.list(user_id)
    
    # Extract chat information
    chat_list = [{
        'id': chat.id,
        'name': chat.name,
        'created_at': int(chat.created_at.timestamp() * 1000),
        'updated_at': int(chat.last_updated().timestamp() * 1000)
    } for chat in chats]
    
    # Return the list of chats
    return {'error': 0, 'message': 'Chats found', 'data': chat_list}, 200


@chat.route('/info', methods=['GET'])
@token_required
def info():
    # Get user ID
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    
    # Get chat 
    chat_id = request.args.get('id', None)
    chat = Chat.get(user_id, chat_id)
    if chat is None:
        return {'error': 4, 'message': f"Chat \'{chat_id}\' not found", 'data': None}, 404
    
    # Return chat information
    data = chat.to_dict()
    data.pop('user_id')
    return {'error': 0, 'message': 'Chat found', 'data': data}, 200


@chat.route('/rename', methods=['PUT'])
@token_required
def rename():
    # Get user ID
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    
    # Get chat ID and name from request
    chat_id = request.json.get('id', None)
    chat = Chat.get(user_id, chat_id)
    if chat is None:
        return {'error': 4, 'message': f"Chat \'{chat_id}\' not found", 'data': None}, 404
    
    # Get new name
    name = request.json.get('name', None)
    if name is None:
        return {'error': 5, 'message': 'Name is required', 'data': None}, 400
    
    # Rename chat
    if chat.rename(name):
        return {'error': 0, 'message': 'Chat renamed', 'data': None}, 200
    return {'error': 6, 'message': 'Failed to rename chat', 'data': None}, 500


@chat.route('/msgs', methods=['GET'])
@token_required
def list_msgs():
    # Get user ID
    user_id = get_uid()
    if user_id is None:
        return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
    
    # Get chat ID
    chat_id = request.args.get('chat_id', None)
    chat = Chat.get(user_id, chat_id)
    if chat is None:
        return {'error': 4, 'message': f"Chat \'{chat_id}\' not found", 'data': None}, 404
    
    messages: List[Message] = chat.messages()
    message_list = [{
        'source': 'user' if message.source else 'model',
        'status': message.status,
        'parts': {
            # Answer
            "answer": message.message,
            
            # References
            "references": [
                {
                    "accident_id": ticket.accident_id,
                    "event_type": ticket.event_type,
                    "industry_type": ticket.industry_type,
                    "accident_title": ticket.title,
                    "url": ticket.url,
                    "color": ticket.color
                } for ticket in message.list_tickets()
            ]
            
        }
    } for message in messages]
    
    return {'error': 0, 'message': 'Messages found', 'data': {'chat_id': chat.id, 'messages': message_list}}, 200
    
    
@chat.route('/send', methods=['POST'])
@token_required
def send():
    try:
        # Get user ID
        user_id = get_uid()
        if user_id is None:
            return {'error': 3, 'message': 'Unauthorized', 'data': None}, 401
        
        # Get chat
        chat_id = request.json.get('chat_id', None)
        chat = Chat.get(user_id, chat_id)
        if chat is None:
            return {'error': 4, 'message': f"Chat \'{chat_id}\' not found", 'data': None}, 404
        
        # Get message
        message = request.json.get('message', None)
        if message is None:
            return {'error': 5, 'message': 'Message is required', 'data': None}, 400
        
        # Retrieve chat history
        history = chat.history()
        
        # Add message to chat database
        request_message: Message = Message(
            user_id=user_id, 
            chat_id=chat_id, 
            message=message, 
            source=Message.SOURCE_USER, 
            status=Message.STATUS_SUCCESS
            )
        chat.add_message(request_message)
        
        # Add message to LLM with STATUS_PENDING
        response_message = Message(user_id=user_id, chat_id=chat_id, message='', source=Message.SOURCE_MODEL, status=Message.STATUS_PENDING)
        chat.add_message(response_message)
        
        # Invoke LLM
        try:
            response: LLMResponse = invoke_llm(user_id, chat_id, message, history)
            if response.is_valid():
                response_message.status = Message.STATUS_SUCCESS
            else:
                response_message.status = Message.STATUS_ERROR
        except Exception as e:
            r = requests.Response()
            r.status_code = 500
            response = LLMResponse(r)
            response_message.status = Message.STATUS_ERROR
            
            
        # Save response to database
        response_message.message = response.answer
        tickets: List[Ticket] = [
            Ticket(
                message_id=response_message.id,
                accident_id=ref['accident_id'],
                event_type=ref['event_type'],
                industry_type=ref['industry_type'],
                title=ref['accident_title'],
                url=ref['url'],
                color=ref['color']
            ) for ref in response.references
        ]
        for ticket in tickets:
            ticket.save()    
        response_message.tickets = tickets
        response_message.save() 
        
        return {
            'error': 0, 
            'message': 'Message sent', 
            'data': {
                'source': 'model',
                'status': response_message.status,
                'parts': {
                    'answer': response_message.message,
                    'references': [ticket.to_dict() for ticket in response_message.list_tickets()]
                    }
            }
        }
    except ClientDisconnected as e:
        print("Client aborted the request (exception caught).")
        return {'error': 6, 'message': 'Client disconnected', 'data': None}, 499
        
        
    

    
    