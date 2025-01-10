from app.routes.chat.utils.llm import LLMResponse, invoke_llm

def main():
    response: LLMResponse = invoke_llm(user_id='10ad0fbf0ed04449903583354992beaa', chat_id='53c049c88e4c4443927c2247c3e9cea1',
                                       req_message='Hello, how can I help you?', hist_message=[])
    
    print(f"Error: {response.error}")
    print(f"Answer: {response.answer}")
    print(f"References: {response.references}")
    
if __name__ == '__main__':
    main()