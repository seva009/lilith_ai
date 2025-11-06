import os
import json


class LilithMemory:
    def __init__(self, base_dir, config, def_user_name=""):
        self.base_dir = base_dir
        self.config = config
        self.PERSONA_FILE = os.path.join(base_dir, config['ai_config']['persona'])
        self.MEMORY_FILE = os.path.join(base_dir, config['ai_config']['memory'])
        self.DEFAULT_USER_NAME = def_user_name
        return
    
    def load_persona(self):
        with open(self.PERSONA_FILE, "r", encoding="utf-8") as f:
            return f.read()
        
    def load_memory(self):
        data = {}
        if os.path.exists(self.MEMORY_FILE):
            with open(self.MEMORY_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        data.setdefault("meta", {})
        data.setdefault("conversation", [])
        data["meta"].setdefault("user_name_set", False)
        return data
    
    def save_memory(self, memory):
        with open(self.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)

    def get_user_name(self, memory, default=None):
        if default is None:
            default = self.DEFAULT_USER_NAME
        meta = memory.setdefault("meta", {})
        name = meta.get("user_name")
        if isinstance(name, str) and name.strip():
            return name.strip()
        meta["user_name"] = default
        meta.setdefault("user_name_set", False)
        return default
    
    def set_user_name(self, memory, name):
        memory.setdefault("meta", {})
        memory["meta"]["user_name"] = name.strip()
        memory["meta"]["user_name_set"] = True
        self.save_memory(memory)
