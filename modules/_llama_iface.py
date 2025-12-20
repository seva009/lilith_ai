from llama_cpp import Llama
import configparser
import logging

logger = logging.getLogger(__name__)

class AIInterface_Llama:
    def __init__(
        self,
        temperature: float = 0.7,
        max_tokens: int = 150,
        n_ctx: int = 8192,
        n_threads: int = 4,
        n_batch: int = 256,
        **kwargs
    ):
        config = configparser.ConfigParser()
        config.read("config.ini")

        self.model_path = config.get("ai_config", "model_path") + config.get("ai_config", "local_model")
        logger.info(f"Initializing Llama model from path: {self.model_path} with n_ctx={n_ctx}, n_threads={n_threads}, n_batch={n_batch}")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_history_messages = config.getint("ai_config", "max_history_messages", fallback=40)

        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_batch=n_batch,
            verbose=False,
        )



    def _trim_messages(self, messages: list) -> list:
        logger.info(f"Trimming messages to the last {self.max_history_messages} messages.")
        system = [m for m in messages if m["role"] == "system"]
        others = [m for m in messages if m["role"] != "system"]

        if len(others) > self.max_history_messages:
            others = others[-self.max_history_messages :]

        return system + others

    def _messages_to_prompt(self, messages: list) -> str:
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt += f"<<SYS>>\n{content}\n<</SYS>>\n\n"
            elif role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"

        prompt += "Assistant: "
        return prompt

    def get_response(self, messages: list) -> str:
        prompt = self._messages_to_prompt(self._trim_messages(messages))

        output = self.llm(
            prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=0.9,
            stop=["User:", "</s>"],
        )

        return output["choices"][0]["text"].strip()
