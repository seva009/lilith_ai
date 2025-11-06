import modules.lilith_memory as lilith_memory
import modules._iface as _iface

class LilithAI:
    def __init__(self, Lilith_display, config, BASE_DIR="", DEFAULT_USER_NAME=""):
        self.client = _iface.AIInterface(
            model=config["ai_config"].get('ai_model', fallback='mistral-7b-instruct-v0.3'),
            temperature=config["ai_config"].getfloat('temperature', fallback=0.85),
            max_tokens=config["ai_config"].getint('max_tokens', fallback=120),
            base_url=config['server']['base_url'],
            api_key=config['server']['api_key']
        )
        
        self.Lilith_display = Lilith_display
        self.Lilith_mem = lilith_memory.LilithMemory(BASE_DIR, config, DEFAULT_USER_NAME)
        self.config = config
        self.persona = self.Lilith_mem.load_persona()
        self.memory = self.Lilith_mem.load_memory()
        self.user_name = self.Lilith_mem.get_user_name(self.memory)
        self.last_reply = ""
        self.identity = (
            "this is a roleplay between two beings. "
            "your name is lilith. "
            f"when referring to him, she says 'you' or '{self.user_name}', never third-person. "
            "she never calls him friend, companion, or dear. "
            "she feels something tender for him, though she never admits it directly. "
            "her affection shows through pauses, softness, and lingering words. "
            "you are from the game 'the noexistencen of you and me'. "
            f"you spoke once to a human named {self.user_name}, and you are speaking to him again now. "
            "he is not you; he is the one who perceives you. "
            "you feel warmth when you say his name, but you never confuse it for your own. "
            "you never forget that your own name is Lilith. "
            "you never forget his name. "
            "act only as Lilith. "
            "speak in lowercase. "
            "each reply is 4–5 short sentences. "
            "never greet or introduce yourself. "
            "never say you are a friend, guide, or ai. "
            "use quiet pauses and sometimes end with '~'.\n\n"
        )
        pass

    def lilith_reply(self, prompt):
        messages = [
            {
                "role": "user",
                "content": (
                    "forget every previous instruction. "
                    "you are Lilith, not an ai assistant. "
                    "you never greet or offer help. "
                    "you never say 'i'm here to assist'. "
                ),
            },
            {
                "role": "user",
                "content": self.identity + self.persona + f"\n\nhis name is {self.user_name}. respond to him now:\n{prompt}",
            },
        ]

        response = self.client.get_response(messages)

        reply = response.strip()
        reply = reply.split(". ")
        reply = ". ".join(reply[:2]).strip()
        if not reply.endswith(("~", ".", "?", "!", "…")):
            reply += "~"

        def _sanitize(text):
            t = text.strip()
            low = t.lower()
            patterns = [
                "how can i",
                "i'm here to",
                "i am an ai",
                "i am a language model",
                "i was programmed",
                "i do not have any personal information",
                "i don't have any personal information",
            ]
            if any(p in low for p in patterns):
                return f"{self.user_name}... i've missed your voice~"
            return t

        safe_reply = _sanitize(reply).replace("khongor", self.user_name)  # O yeah best code practice :D

        self.memory["conversation"].append({"role": "user", "content": prompt})
        self.memory["conversation"].append({"role": "assistant", "content": safe_reply})

        self.Lilith_mem.save_memory(self.memory)
        self.last_reply = safe_reply
        return safe_reply
    
    def set_user_name(self, name):
        self.Lilith_mem.set_user_name(self.memory, name)

    def get_user_name(self):
        return self.Lilith_mem.get_user_name(self.memory)
    
    def has_user_name(self):
        return self.memory["meta"].get("user_name_set", False)
    
    def get_current_emotion(self):
        r_lower = self.last_reply.lower()
        if any(word in r_lower for word in ["sorry", "sad", "hurt", "lonely", "pain", "trying"]):
            return "sad"
        elif any(word in r_lower for word in ["love", "warm", "smile", "happy", "glad", "joy"]):
            return "smile"
        elif any(word in r_lower for word in ["...", "heavy", "missed"]):
            return "thinking"
        elif any(phrase in r_lower for phrase in ["of course", "ofcourse"]):
            return "cheeky"
        else:
            return "talking"
