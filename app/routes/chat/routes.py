import logging
import os
import json
import time
import datetime
from flask import request, Response, current_app
import google.generativeai as genai
import requests

from . import chat
from .models import Chat, Message, Ticket
from .utils.jwt_utils import token_required, verify_jwt

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

LLM_URI = "http://localhost:8000/invoke"

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
    
    messages: Message = chat.get_messages()
    message_list = [{
        'source': 'user' if message.source else 'model',
        'parts': {
            "answer": message.message,
            "references": [
                {
                    "accident_id": ticket.accident_id,
                    "event_type": ticket.event_type,
                    "industry_type": ticket.industry_type,
                    "accident_title": ticket.title,
                    "url": ticket.url,
                    "color": ticket.color
                } for ticket in message.tickets
            ]
            
        }
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
    
    # history : is a list of messages of all the chat history before the current message
    # msg     : is the current message that the user sent
    
    payload = {
        "user_id": user_id,
        "chat_id": chat_id,
        "question": message,
        "industries": ['all'] # TODO : Add industries in User account information
    }

    try:
        response = requests.post(LLM_URI, json=payload)

        logging.error(f'Model response = {response}')
        
        if response.status_code == 200:
            logging.error(f'Model response = {response.json()}')
            
            manage_model_response(response, user_id, chat_id, chat)
            
            return response.json(), 200
        else:
            return {
                'error': 7,
                'message': 'Failed to invoke chain',
                'data': response.json()
            }, response.status_code

    except Exception as e:
        logging.error(e)
        return {
            'error': 8,
            'message': 'An error occurred while invoking the chain',
            'data': str(e)
        }, 500
    
def test_response(_, user_id, chat_id, ctx):
    import random
    respose_json = [
        {
            "answer": "<span style='color: #0000ff'>To prevent the contamination of metal products during the processing stage in a metal processing facility, several measures can be taken, focusing on handling chemicals, mitigating risks from sharp metal edges, and preventing fires or explosions.</span> <span style='color: #008000'>Firstly, ensuring proper procedures for handling and storing chemicals, as highlighted by accident 351 where the overfilling of a tank caused a hydrogen fluoride leak, is crucial. This includes adequate ventilation, proper tank maintenance, and employee training on chemical handling.</span> <span style='color: #ff0000'>Secondly, implementing safety measures to prevent injuries from sharp metal edges, such as guarding sharp edges and using proper handling tools, can minimize contamination risks, as well as protect employee safety.</span> <span style='color: #0000ff'>Thirdly, to mitigate the risk of fires or explosions, implementing safety protocols such as ensuring proper ventilation, using explosion-proof equipment, and controlling ignition sources is essential, as seen in accidents like 93 where a destructive fire occurred at a metal production plant during maintenance work.</span> <span style='color: #008000'>Additionally, regular maintenance of equipment, proper employee training, and the implementation of comprehensive safety protocols are vital in preventing workplace accidents and ensuring a safe working environment, as highlighted by lessons learned from past accidents such as carbon monoxide leaks during blower maintenance.</span> <span style='color: #0000ff'>By integrating these practices and learning from past incidents, metal processing facilities can significantly reduce the risk of contamination and accidents during the processing stage.</span>",
            "references": [
                {
                    "accident_id": 351,
                    "event_type": "Major Accident",
                    "industry_type": "Processing of metals",
                    "accident_title": "Overfilling of a tank caused a hydrogen fluoride flow through the vent pipes",
                    "url": "https://emars.jrc.ec.europa.eu/en/emars/accident/view/fca342a4-1cb8-b4c6-cae6-cf94c06d7018",
                    "color": "#008000"
                },
                {
                    "accident_id": 93,
                    "event_type": "Major Accident",
                    "industry_type": "Processing of ferrous metals (foundries, smelting, etc.)",
                    "accident_title": "Destructive fire at a metal production plant during maintenance work",
                    "url": "https://emars.jrc.ec.europa.eu/en/emars/accident/view/e41e5302-a931-5764-1f0d-d006b475614a",
                    "color": "#008000"
                },
                {
                    "accident_id": 345,
                    "event_type": "Major Accident",
                    "industry_type": "Processing of metals",
                    "accident_title": "Carbon monoxide leak during maintenance to a blower in a metal processing plant and installation of a complementary CO-warning",
                    "url": "https://emars.jrc.ec.europa.eu/en/emars/accident/view/20989023-a1ed-6874-e80c-7981156cc906",
                    "color": "#ff0000"
                }
            ]
        },
        {
            "answer": "<span style='color: #0000ff'>To mitigate the risk of explosion or fire in areas where metals are being cut, ground, or polished within a metal processing facility, several safety protocols can be implemented based on lessons learned from past accidents and best practices in the industry.</span> <span style='color: #008000'>Implementing safety measures such as ensuring proper ventilation, using explosion-proof equipment and lighting, and controlling the presence of ignition sources can significantly reduce the risk of fires and explosions, as seen in accidents like 93 where a destructive fire occurred at a metal production plant during maintenance work.</span> <span style='color: #ff0000'>Additionally, the use of personal protective equipment, proper training for employees, and regular maintenance of machinery can also minimize risks, as highlighted in accident 951 where a hydrogen explosion occurred in a hydrochloric acid tank.</span> <span style='color: #0000ff'>Furthermore, considering specific accident prevention measures, such as those applied after accidents like the overfilling of a tank causing a hydrogen fluoride leak or a carbon monoxide leak during maintenance, can provide valuable insights into preventive actions.</span> <span style='color: #008000'>Maintaining a clean and organized workspace, adhering to strict housekeeping practices to prevent the accumulation of dust and debris, and ensuring the proper handling and storage of materials are also crucial, as seen in accident 345 where a carbon monoxide leak occurred during maintenance of a blower.</span> <span style='color: #0000ff'>By integrating these practices and learning from past incidents, metal processing facilities can significantly lower the risk of explosions and fires during metal cutting, grinding, and polishing operations.</span>",
            "references": [
                {
                    "accident_id": 93,
                    "event_type": "Major Accident",
                    "industry_type": "Processing of ferrous metals (foundries, smelting, etc.)",
                    "accident_title": "Destructive fire at a metal production plant during maintenance work",
                    "url": "https://emars.jrc.ec.europa.eu/en/emars/accident/view/e41e5302-a931-5764-1f0d-d006b475614a",
                    "color": "#008000"
                },
                {
                    "accident_id": 951,
                    "event_type": "Major Accident",
                    "industry_type": "Processing of metals using electrolytic or chemical processes",
                    "accident_title": "Hydrogen explosion in hydrochloric acid tank",
                    "url": "https://emars.jrc.ec.europa.eu/en/emars/accident/view/bc285a60-cd32-409c-4f50-2a328a3cea93",
                    "color": "#ff0000"
                },
                {
                    "accident_id": 345,
                    "event_type": "Major Accident",
                    "industry_type": "Processing of metals",
                    "accident_title": "Carbon monoxide leak during maintenance to a blower in a metal processing plant and installation of a complementary CO-warning",
                    "url": "https://emars.jrc.ec.europa.eu/en/emars/accident/view/20989023-a1ed-6874-e80c-7981156cc906",
                    "color": "#008000"
                }
            ]
        },
        {
            "answer": "<span style='color: #0000ff'>To resolve quality control issues such as metal defects or irregularities during the metal processing stage, several steps can be taken, focusing on safety protocols and lessons learned from past accidents.</span> <span style='color: #008000'>Firstly, implementing a thorough inspection process to identify defects or irregularities early on is crucial, as seen in accidents like 800 where the release of nitrous gas occurred due to a lack of information about the modification of the alloy composition.</span> <span style='color: #ff0000'>Secondly, ensuring that all employees are properly trained on quality control procedures and safety protocols is essential, as highlighted by accidents like 1086 where the explosion in a metal recycling plant was caused by insufficient risk assessment and scrap receiving procedures.</span> <span style='color: #0000ff'>Additionally, maintaining a safe working environment by controlling potential hazards such as sharp metal edges, fire, or explosion risks, and ensuring that all necessary safety equipment is available and used, is vital.</span> <span style='color: #008000'>Implementing corrective actions to address quality control issues, such as rework or repair of defective products, and continuously monitoring and evaluating the effectiveness of these actions, can also help to prevent future defects.</span> <span style='color: #ff0000'>Furthermore, considering the lessons learned from past accidents, such as the importance of proper communication between subcontractors and customers, and the need for adequate risk assessment and safety procedures, can provide valuable insights into preventive actions.</span> <span style='color: #0000ff'>By integrating these practices and learning from past incidents, metal processing facilities can significantly improve the quality of their products while maintaining a safe working environment.</span>",
            "references": [
                {
                    "accident_id": 800,
                    "event_type": "Other Event",
                    "industry_type": "Processing of metals",
                    "accident_title": "Release of Nitrous gas in the air from a finishing treatment of metals plant",
                    "url": "https://emars.jrc.ec.europa.eu/en/emars/accident/view/66183944-a5f1-b4d8-51ac-55724cc1f752",
                    "color": "#008000"
                },
                {
                    "accident_id": 1086,
                    "event_type": "Major Accident",
                    "industry_type": "Processing of non-ferrous metals (foundries, smelting, etc.)",
                    "accident_title": "Accident in metal recycling plant",
                    "url": "https://emars.jrc.ec.europa.eu/en/emars/accident/view/04558cdd-4ed6-11e8-a5bf-005056ad0167",
                    "color": "#ff0000"
                }
            ]
        }
        
    ][random.randint(0, 2)]
    response_str = json.dumps(respose_json)
    
    class Chunk:
        def __init__(self, text):
            self.text = text
            
    # split into sentence of 64 words
    response = [Chunk(response_str)]
    return convert_response(response, user_id, chat_id, ctx)
    
        
def check_response(json_response) -> dict:
    # response as 'answer' and 'references'
    if 'answer' not in json_response:
        return {'error': 1, 'message': 'Missing answer field'}
    if 'references' not in json_response:
        return {'error': 2, 'message': 'Missing references field'}  
    # check if answer is valid
    if not isinstance(json_response['answer'], str):
        return {'error': 3, 'message': 'Answer is not a string'}
    # check if references is valid
    if not isinstance(json_response['references'], list):
        return {'error': 4, 'message': 'References is not a list'}
    else:
        for ref in json_response['references']:
            if not isinstance(ref, dict):
                return {'error': 5, 'message': 'Reference is not a dictionary'}
            if 'accident_id' not in ref:
                return {'error': 6, 'message': 'Missing accident_id field'}
            if 'event_type' not in ref:
                return {'error': 7, 'message': 'Missing event_type field'}
            if 'industry_type' not in ref:
                return {'error': 8, 'message': 'Missing industry_type field'}
            if 'accident_title' not in ref:
                return {'error': 9, 'message': 'Missing accident_title field'}
            if 'url' not in ref:
                return {'error': 10, 'message': 'Missing url field'}
            if 'color' not in ref:
                return {'error': 11, 'message': 'Missing color field'}
    return {'error': 0, 'message': 'Response is valid'}


def manage_model_response(response, user_id, chat_id, chat):
    data = response.json()
    assistant_msg = Message(user_id=user_id, chat_id=chat_id, message=data['answer'], source=False)
    chat.add_message(assistant_msg)
            
    for ticket_data in data['references']:
        ticket = Ticket(
            message_id=assistant_msg.id,
            accident_id=ticket_data.get('accident_id', -1),
            event_type=ticket_data.get('event_type', 'Not available'),
            industry_type=ticket_data.get('industry_type', 'Not available'),
            title=ticket_data.get('accident_title', 'Not available'),
            url=ticket_data.get('url', 'Not available'),
            color=ticket_data.get('color', '#FFFFFF')
        )
        ticket.save()
            
    

def convert_response(response, user_id, chat_id, ctx):
    full_response = ''
    for chunk in response:
        full_response += chunk.text
        # Split the response into words to make the response more human-like (optional)
        msg = {"choices": [{"delta": {"content": f"{chunk.text}"}, "finish_reason": None}]}
        yield f"data: {json.dumps(msg)}\n\n"

    # Save the response on the database
    try:
        json_response = json.loads(full_response)
        # Check if the response is valid
        error = check_response(json_response)
        if error.get('error', 0) != 0:
            raise Exception(error['message'])
        
        with ctx:
            tickets = []
            message = Message(user_id=user_id, chat_id=chat_id, message=json_response['answer'], source=False)
            for ref in json_response['references']:
                ticket = Ticket(
                    message_id=message.id,
                    # Content
                    accident_id=ref['accident_id'],
                    event_type=ref['event_type'],
                    industry_type=ref['industry_type'],
                    title=ref['accident_title'],
                    url=ref['url'],
                    color=ref['color']
                )
                tickets.append(ticket)
            
            message.tickets = tickets
            
            # Save the message and tickets
            for ticket in tickets:
                ticket.save()
            message.save()
            
        print('Response saved')
        
    except json.JSONDecodeError:
        raise Exception('Invalid response from the model')
    
    
    # Final message to stop the conversation
    final_chunk = {
        "choices": [{"delta": {"content": ""}, "finish_reason": "stop"}]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    
    
    
    
    