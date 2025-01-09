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

model = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1/",
    model="llama-3.3-70b-versatile",
    temperature=1,
    api_key=API_KEY
)

memory = MemoryManager()

def get_json_from_markdown(markdown_text):
    try:
        json_match = re.search(r'```json(.*?)```', markdown_text, re.DOTALL)
        if json_match:
            json_string = json_match.group(1).strip()
            json_data = json.loads(json_string)
            return json_data
        else:
            return json.loads(markdown_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return markdown_text


class LLM:
    def __init__(self):
        self.model = model
        self.memory = memory

    def get_memory(self, user_id, chat_id):
        return self.memory.get_memory(user_id, chat_id)

    async def invoke_chain(self, payload: dict):
        try:
            # Get user memory
            user_id = payload.get("user_id")
            chat_id = payload.get("chat_id")
            user_mem = self.get_memory(user_id, chat_id)
            
            # Define the context
            context = RunnablePassthrough.assign(
                chat_history=RunnableLambda(
                    user_mem.load_memory_variables) | itemgetter("history")
            ) | CONTEXT_PROMPT | self.model | StrOutputParser()
            
            # Create the runnable chain to invoke
            runnable = (
                RunnablePassthrough.assign(
                    question=context,
                    memory=RunnableLambda(
                        user_mem.load_memory_variables) | itemgetter("history"),
                    industries=RunnableLambda(lambda x: x.get("industries"))
                )
                | retrieve
                | SYSTEM_PROMPT
                | self.model
                | StrOutputParser()
                | get_json_from_markdown
            )
            result = await runnable.ainvoke(payload)
            print(result)
            user_mem.chat_memory.add_user_message(payload.get("question"))
            user_mem.chat_memory.add_ai_message(str(result))
            return result
        except Exception as e:
            print(f"Error invoking chain: {e}")
            return {"error": str(e)}
        
        