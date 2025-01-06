import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from utils.retriever import retrieve
from utils.prompts import CONTEXT_PROMPT, SYSTEM_PROMPT
from operator import itemgetter
import re
import json
import warnings
from collections import defaultdict
from threading import Lock
import logging

warnings.filterwarnings('ignore')


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

load_dotenv()
API_KEY = os.getenv("API_KEY")


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


class MemoryManager:
    def __init__(self):
        self.user_chat_memories = defaultdict(
            lambda: defaultdict(ConversationBufferWindowMemory))
        self.lock = Lock()

    def get_memory(self, user_id, chat_id):
        with self.lock:
            return self.user_chat_memories[user_id][chat_id]


memory_manager = MemoryManager()


def get_industry(input):
    return input['industries']


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


llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1/",
    model="llama-3.3-70b-versatile",
    temperature=1,
    api_key=API_KEY
)


@app.post("/invoke")
async def invoke_chain(request: Request):
    """
    Endpoint to invoke the runnable chain with the given input.
    """
    try:
        body = await request.json()
        user_id = body.get("user_id")
        chat_id = body.get("chat_id")
        if not user_id:
            return {"error": "Missing user_id in request."}
        if not chat_id:
            return {"error": "Missing chat_id in request."}

        memory = memory_manager.get_memory(user_id, chat_id)

        runnable_context = RunnablePassthrough.assign(
            chat_history=RunnableLambda(
                memory.load_memory_variables) | itemgetter("history")
        ) | CONTEXT_PROMPT | llm | StrOutputParser()

        runnable = (
            RunnablePassthrough.assign(
                question=runnable_context,
                memory=RunnableLambda(
                    memory.load_memory_variables) | itemgetter("history"),
                industries=RunnableLambda(get_industry)
            )
            | retrieve
            | SYSTEM_PROMPT
            | llm
            | StrOutputParser()
            | get_json_from_markdown
        )

        result = await runnable.ainvoke(body)
        memory.chat_memory.add_user_message(body.get("question"))
        memory.chat_memory.add_ai_message(str(result))
        logger.info(f'Model Result : {result}')
        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
