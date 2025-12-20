from ollama import chat
from ollama import ChatResponse

class AIInterface_Ollama:
    def __init__(self, model:str, temperature:float = 0.7, max_tokens:int =150, **kwargs):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        pass

    def get_response(self, messages : list) -> str: # idk how to set temp and max tokens with ollama api
        response: ChatResponse = chat(
            model=self.model,
            messages=messages,
        )
        return response['message']['content']