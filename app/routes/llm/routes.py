import logging
from flask import request, redirect

from ..llm_config.models import LLMConfig
from . import llm
from .model import LLM

# Define the route for the root endpoint to redirect to the documentation page.
@llm.route("/")
def redirect_root_to_docs():
    """
    Redirect the root URL to the documentation page.
    """
    return redirect("/docs")

# Define the route for the '/invoke' endpoint to invoke the chain with input data.
@llm.route("/invoke", methods=["POST"])
async def invoke_chain():
    """
    Endpoint to invoke the runnable chain with the given input.
    Handles incoming POST requests to trigger the chain of operations.
    """
    try:
        # Get the JSON payload from the incoming POST request.
        payload = request.json
        # Log the payload to help with debugging.
        logging.info(f'Payload: {payload}')
        
        # Retrieve the configuration for the selected LLM (Large Language Model).
        llm_config = LLMConfig.get_selected_llm()
        
        # Log the configuration for debugging purposes.
        logging.info(f'LLM Configuration: {llm_config}')
        
        # Instantiate the LLM object using the selected configuration.
        llm_instance = LLM(llm_config)
        
        # Invoke the chain with the provided payload and return the result asynchronously.
        return await llm_instance.invoke_chain(payload), 200
    
    except Exception as e:
        # If an error occurs, return an error message and a 500 status code.
        return {"error": 500, "message": str(e)}, 500
