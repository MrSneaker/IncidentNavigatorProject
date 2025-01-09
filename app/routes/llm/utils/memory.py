from collections import defaultdict
from threading import Lock
from langchain.memory import ConversationBufferWindowMemory

class MemoryManager:
    def __init__(self):
        self.user_chat_memories = defaultdict(
            lambda: defaultdict(ConversationBufferWindowMemory))
        self.lock = Lock()

    def get_memory(self, user_id, chat_id):
        with self.lock:
            return self.user_chat_memories[user_id][chat_id]