from pathlib import Path
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os


class AIInterface_HF:
    def __init__(
        self,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 150,
        local_dir: str = "models/",
        base_url: str = None,
        api_key: str = None,
    ):
        self.model_id = model
        self.model_name = model.split("/")[-1]
        self.model_path = Path(local_dir) / self.model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.top_p = 0.9
        self.top_k = 50
        self.token = os.getenv("HF_API_TOKEN")

    def download_if_needed(self):
        if self.model_path.exists():
            return

        snapshot_download(
            repo_id=self.model_id,
            local_dir=self.model_path,
            local_dir_use_symlinks=False,
            token=self.token,
        )

    def load(self):
        self.download_if_needed()

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            use_fast=False,              
            trust_remote_code=True,
            local_files_only=True,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            low_cpu_mem_usage=True,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if self.device is None else None,
            local_files_only=True,
        )

        if self.device:
            self.model.to(self.device)

        self.model.eval()

        return self.model, self.tokenizer

    def get_response(self, messages: list) -> str:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model and tokenizer must be loaded before getting a response.")

        inputs = self.tokenizer(
            messages,
            return_tensors="pt"
        ).to(self.model.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=self.max_tokens,
                do_sample=True,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        return self.tokenizer.decode(output[0], skip_special_tokens=True)
