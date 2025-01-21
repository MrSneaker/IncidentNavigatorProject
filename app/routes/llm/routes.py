import logging
from flask import request, redirect

from .utils.llm_exception_handler import LLMInvocationError

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
        payload = request.json
        logging.info(f'Payload: {payload}')
        
        llm_config = LLMConfig.get_selected_llm()
        
        logging.info(f'LLM Configuration: {llm_config}')
        
        llm_instance = LLM(llm_config)
        
        response = await llm_instance.invoke_chain(payload)
        
        return response, 200
    
    except LLMInvocationError as e:
        logging.error(f'LLM Invocation Error: {e}')
        return {
            "error": e.error_code,
            "message": e.message
        }, e.error_code
    except Exception as e:
        return {"error": 500, "message": str(e)}, 500


