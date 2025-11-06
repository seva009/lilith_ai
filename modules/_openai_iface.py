from openai import OpenAI
import configparser

class AIInterface_OpenAI:
    def __init__(self, model:str, temperature:float=0.7, max_tokens:int=150, base_url:str=str(), api_key:str=str()):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def get_response(self, messages: list) -> str | None:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content