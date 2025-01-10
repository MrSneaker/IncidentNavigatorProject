import logging
from flask import request, redirect
import re
import json

from ..llm_config.models import LLMConfig

from . import llm
from .model import LLM



@llm.route("/")
def redirect_root_to_docs():
    return redirect("/docs")

def get_json_from_markdown(markdown_text):
    try:
        json_match = re.search(r'```json(.*?)```', markdown_text, re.DOTALL)
        if json_match:
            json_string = json_match.group(1).strip()
            json_data = json.loads(json_string)
            return json_data
        else:
            print("No JSON block found in the Markdown text.")
            return json.loads(markdown_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return markdown_text

@llm.route("/invoke", methods=["POST"])
async def invoke_chain():
    """
    Endpoint to invoke the runnable chain with the given input.
    """
    try:
        payload = request.json
        logging.error(f'payload : {payload}')
        llm_config = LLMConfig.get_selected_llm()
        
        logging.error(f'config: {llm_config}')
        llm = LLM(llm_config)
        return await llm.invoke_chain(payload), 200
    except Exception as e:
        return {"error": 500, "message": str(e)}, 500
        
