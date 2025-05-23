import logging
from werkzeug.exceptions import ClientDisconnected
import requests
from flask import request


class LLMResponse:
    """
    LLMResponse is a helper class to manage the response from a Language Learning Model (LLM).
    
    Attributes:
        error (int): Represents the error status. Default is -1.
        answer (str): Contains the response answer from the LLM.
        references (list[dict]): Contains the references related to the response.
    
    Methods:
        __init__(response: requests.Response, is_bad_request: bool, bad_req_error_msg: dict):
            Initializes the object, processes the response, and sets attributes accordingly.
        
        is_valid() -> bool:
            Checks if the response is valid (error == 0).
        
        check_response(json_response: dict) -> dict:
            Static method that validates the structure of the response JSON.
    """
    error = -1
    answer: str = ''
    references: list[dict] = []
    
    def __init__(self, response: requests.Response, is_bad_request=False, bad_req_error_msg=None):
        """
        Initializes an instance of LLMResponse.

        Args:
            response (requests.Response): The HTTP response object from the LLM.
            is_bad_request (bool): Flag indicating if the request was invalid.
            bad_req_error_msg (dict): A dictionary containing error information for a bad request.
        """
        if is_bad_request:
            self.error = bad_req_error_msg['error']
            self.answer = bad_req_error_msg['message']
            return
        
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
        """
        Checks if the LLM response is valid.

        Returns:
            bool: True if the response is valid (error == 0), False otherwise.
        """
        return self.error == 0
    
    @staticmethod
    def check_response(json_response) -> dict:
        """
        Validates the structure and content of the LLM JSON response.

        Args:
            json_response (dict): The JSON response to validate.

        Returns:
            dict: A dictionary indicating the validation result. Contains 'error' and 'message'.
        """
        error_string = 'It seems the LLM of your configuration did not succeed in making a well done response, please retry or ask for a better LLM. Error is : '
        # response as 'answer' and 'references'
        if 'answer' not in json_response:
            return {'error': 1, 'message': f'{error_string}Missing answer field'}
        if 'references' not in json_response:
            return {'error': 2, 'message': f'{error_string}Missing references field'}
        
        # check if answer is valid
        if not isinstance(json_response['answer'], str):
            return {'error': 3, 'message': f'{error_string}Answer is not a string'}
        # check if references is valid
        if not isinstance(json_response['references'], list):
            return {'error': 4, 'message': f'{error_string}References is not a list'}
        
        # check if each reference is valid
        for ref in json_response['references']:
            if not isinstance(ref, dict):
                return {'error': 5, 'message': f'{error_string}Reference is not a dictionary'}
            if 'accident_id' not in ref:
                return {'error': 6, 'message': f'{error_string}Missing accident_id field'}
            if 'event_type' not in ref:
                return {'error': 7, 'message': f'{error_string}Missing event_type field'}
            if 'industry_type' not in ref:
                return {'error': 8, 'message': f'{error_string}Missing industry_type field'}
            if 'accident_title' not in ref:
                return {'error': 9, 'message': f'{error_string}Missing accident_title field'}
            if 'url' not in ref:
                return {'error': 10, 'message': f'{error_string}Missing url field'}
            if 'color' not in ref:
                return {'error': 11, 'message': f'{error_string}Missing color field'}
            
        # response is valid
        return {'error': 0, 'message': 'Response is valid'}


def invoke_llm(user_id: str, chat_id: str, req_message: str, hist_message: list, industries: list):
    """
    Invokes the Language Learning Model (LLM) with the specified parameters.

    Args:
        user_id (str): The ID of the user making the request.
        chat_id (str): The ID of the chat.
        req_message (str): The question or message being sent to the LLM.
        hist_message (list): A list of historical messages in the conversation.
        industries (list): A list of industries associated with the user.

    Returns:
        LLMResponse: An instance of the LLMResponse class containing the result.
    """
    try:
        if not industries or industries == []:
            error = {"error": 12, "message": "You don't have any industries affiliated, please contact your administrator to get you at least one."}
            return LLMResponse(None, True, error)
        # Request to LLM
        response = requests.post('http://localhost:5000/llm/invoke', json={
            'user_id': user_id,
            'chat_id': chat_id,
            'history': hist_message, 
            'question': req_message,
            'industries': industries
        })
        
        # Raise an exception if the request failed
        response.raise_for_status()
        return LLMResponse(response)

    except ClientDisconnected as e:
        print("Client aborted the request.")
        raise
    
    except requests.exceptions.HTTPError as e:
        logging.error(f'Error while invoking LLM : {e}')
        if response.status_code == 401:
            return LLMResponse(None, True, {"error": 13, "message": "Your credentials for the selected LLM configuration are incorrect. Please ask an administrator to correct them."})
        elif response.status_code == 404:
            return LLMResponse(None, True, {"error": 14, "message": "Your URI for the selected LLM configuration is incorrect. Please ask an administrator to correct it."})
        elif response.status_code == 400:
            return LLMResponse(None, True, {"error": 15, "message": "The model name for the selected LLM configuration is incorrect. Please ask an administrator to correct it."})
    except requests.exceptions.RequestException as e:
        print(f"Error while invoking LLM: {e}")
        # Return a fake response
        r = requests.Response()
        r.status_code = 500
        return LLMResponse(r)





