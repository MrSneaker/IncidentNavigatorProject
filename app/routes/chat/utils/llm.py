import logging
from werkzeug.exceptions import ClientDisconnected
import requests
from flask import request


class LLMResponse:
    error = -1
    answer: str = ''
    references: list[dict] = []
    
    def __init__(self, response: requests.Response):
        if response.status_code != 200:
            self.error = 1
            self.answer = f'Error {response.status_code}'
            return
        
        json_response = response.json()
        check = LLMResponse.check_response(json_response)
        if check['error'] != 0:
            self.error = check['error']
            self.answer = check['message']
            return
        
        self.error = 0
        self.answer = json_response['answer']
        self.references = json_response['references']

    def is_valid(self) -> bool:
        return self.error == 0
    
    @staticmethod
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
        
        # check if each reference is valid
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
            
        # response is valid
        return {'error': 0, 'message': 'Response is valid'}


def invoke_llm(user_id: str, chat_id: str, req_message: str, hist_message: list, industries: list):
    try:
        # Request to LLM
        response = requests.post('http://localhost:5000/llm/invoke', json={
            'user_id': user_id,
            'chat_id': chat_id,
            'history': hist_message, 
            'question': req_message,
            'industries': industries
        })
        
        logging.error(f'industries : {industries}')

        # Raise an exception if the request failed
        response.raise_for_status()
        return LLMResponse(response)

    except ClientDisconnected as e:
        print("Client aborted the request.")
        raise

    except requests.exceptions.RequestException as e:
        print(f"Error while invoking LLM: {e}")
        # Return a fake respons
        r = requests.Response()
        r.status_code = 500
        return LLMResponse(r)





