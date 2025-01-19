from collections import defaultdict 
from threading import Lock
from langchain.memory import ConversationBufferWindowMemory

# Define a class to manage conversation memories
class MemoryManager:
    
    # Initialize the MemoryManager object
    def __init__(self):
        # The 'user_chat_memories' is a defaultdict of defaultdicts, 
        # where the outer defaultdict uses user IDs and the inner defaultdict stores 
        # ConversationBufferWindowMemory instances keyed by chat IDs.
        self.user_chat_memories = defaultdict(
            lambda: defaultdict(ConversationBufferWindowMemory))  
        
        # A Lock object to synchronize access to the memory in a multi-threaded environment.
        self.lock = Lock()

    # Method to retrieve memory for a specific user and chat.
    def get_memory(self, user_id, chat_id):
        # Use the lock to ensure that only one thread accesses this section at a time.
        with self.lock:
            # Return the ConversationBufferWindowMemory object for the specified user and chat.
            return self.user_chat_memories[user_id][chat_id]
