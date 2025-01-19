import logging
import os
import re
import json
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

from .utils.memory import MemoryManager
from .utils.prompts import CONTEXT_PROMPT, SYSTEM_PROMPT
from .utils.retriever import retrieve


load_dotenv()
API_KEY = os.getenv("API_KEY")

# Function to extract JSON data from markdown formatted text.
def get_json_from_markdown(markdown_text):
    try:
        # Search for content enclosed in ```json``` in markdown text.
        json_match = re.search(r'```json(.*?)```', markdown_text, re.DOTALL)
        if json_match:
            # If a match is found, extract the JSON string, remove leading/trailing spaces.
            json_string = json_match.group(1).strip()
            # Parse the JSON string and return the corresponding data.
            json_data = json.loads(json_string)
            return json_data
        else:
            # If no json block is found, try to parse the entire markdown text as JSON.
            return json.loads(markdown_text)
    except json.JSONDecodeError as e:
        # If an error occurs while decoding JSON, log the error and return the original markdown.
        print(f"Error decoding JSON: {e}")
        return markdown_text
        
# Class for interacting with a large language model (LLM) like ChatOpenAI.
class LLM:
    def __init__(self, config: dict):
        """
        Initialize the LLM object with user configuration.

        :param config: Dictionary containing parameters for configuring ChatOpenAI.
        """
        self.config = config
        # Create an instance of the model using the provided configuration.
        self.model = self.create_model()
        # Initialize a memory manager for this model.
        self.memory = MemoryManager()

    def create_model(self):
        """
        Creates an instance of ChatOpenAI using the configuration dictionary.

        :return: A configured ChatOpenAI instance.
        """
        return ChatOpenAI(
            openai_api_base=self.config.get("uri", "").strip(),
            model=self.config.get("model", "llama-3.3-70b-versatile").strip(),
            temperature=1,  # Set temperature (controls randomness in response).
            api_key=self.config.get("api_key", os.getenv("API_KEY")),
        )

    def get_memory(self, user_id, chat_id):
        """
        Retrieve memory of the user from the memory manager.

        :param user_id: The ID of the user.
        :param chat_id: The ID of the chat session.
        :return: User's memory for the given chat session.
        """
        return self.memory.get_memory(user_id, chat_id)

    async def invoke_chain(self, payload: dict):
        """
        Invokes a chain of processes to handle a request, such as querying a language model.
        
        :param payload: Dictionary containing request data (user ID, chat ID, question, etc.).
        :return: The result of invoking the chain.
        """
        # Get user memory based on user ID and chat ID from the payload.
        user_id = payload.get("user_id")
        chat_id = payload.get("chat_id")
        user_mem = self.get_memory(user_id, chat_id)
        if user_mem is None:
            raise ValueError("User memory not found.")
        
        # Define the context of the request by fetching chat history from user memory.
        context = RunnablePassthrough.assign(
            chat_history=RunnableLambda(
                user_mem.load_memory_variables) | itemgetter("history")
        ) | CONTEXT_PROMPT | self.model | StrOutputParser()
        
        # Define the entire chain of operations to process the request.
        runnable = (
            RunnablePassthrough.assign(
                question=context,
                memory=RunnableLambda(user_mem.load_memory_variables) | itemgetter("history"),
                industries=RunnableLambda(lambda x: x.get("industries"))
            )
            | retrieve
            | SYSTEM_PROMPT 
            | self.model
            | StrOutputParser()
            | get_json_from_markdown
        )
        # Await the result of the chain invocation.
        result = await runnable.ainvoke(payload)

        # Update user memory with the new interaction.
        user_mem.chat_memory.add_user_message(payload.get("question"))
        user_mem.chat_memory.add_ai_message(str(result))

        return result
