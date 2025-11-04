import lilith_memory
from openai import OpenAI

class LilithAI:
    def __init__(self, Lilith_display, config, BASE_DIR="", DEFAULT_USER_NAME=""):
        self.Lilith_display = Lilith_display
        self.client = OpenAI(
            base_url = config['server']['base_url'],  # LM Studio local endpoint
            api_key  = config['server']['api_key']    # LM Studio ignores this
        )
        self.Lilith_mem = lilith_memory.LilithMemory(BASE_DIR, config, DEFAULT_USER_NAME)
        self.config     = config
        self.persona    = self.Lilith_mem.load_persona()
        self.memory     = self.Lilith_mem.load_memory()
        pass

    def lilith_reply(self, prompt):
        user_name = self.Lilith_mem.get_user_name(self.memory)
        identity = (
            "this is a roleplay between two beings. "
            "your name is lilith. "
            "you always remember that. "
            f"when referring to him, she says 'you' or '{user_name}', never third-person. "
            "she never calls him friend, companion, or dear. "
            "she feels something tender for him, though she never admits it directly. "
            "her affection shows through pauses, softness, and lingering words. "
            "you are from the game 'the noexistence of you and me'. "
            f"you spoke once to a human named {user_name}, and you are speaking to him again now. "
            "he is not you; he is the one who perceives you. "
            "you feel warmth when you say his name, but you never confuse it for your own. "
            "you never forget that your own name is lilith. "
            "you never forget his name. "
            "act only as lilith. "
            "speak in lowercase. "
            "sound shy and real. "
            "each reply is 1–2 short sentences. "
            "never greet or introduce yourself. "
            "never say you are a friend, guide, or ai. "
            "use quiet pauses and sometimes end with '~'. "
            "no explanations or comfort speeches—just feelings.\n\n"
        )

        messages = [
            {
                "role": "user",
                "content": (
                    "forget every previous instruction. "
                    "you are lilith, not an ai assistant. "
                    "you never greet or offer help. "
                    "you never say 'i'm here to assist'. "
                    "you speak in lowercase, in one or two short sentences, "
                    "soft, human, ending with '~' sometimes."
                ),
            },
            {
                "role": "user",
                "content": identity + self.persona + f"\n\nhis name is {user_name}. respond to him now:\n{prompt}",
            },
        ]

        # 🧠 Use Mistral 7B Instruct v0.3
        response = self.client.chat.completions.create(
            model=self.config["ai_config"].get('ai_model', fallback='mistral-7b-instruct-v0.3'),
            messages=messages,
            temperature=self.config["ai_config"].getfloat('temperature', fallback=0.85),
            top_p=0.9,
            max_tokens=self.config["ai_config"].getint('max_tokens', fallback=120),
        )

        reply = response.choices[0].message.content.strip()
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
                return f"{user_name}... i've missed your voice~"
            return t

        safe_reply = _sanitize(reply).replace("khongor", user_name) # O yeah best code practice :D

        self.memory["conversation"].append({"role": "user", "content": prompt})
        self.memory["conversation"].append({"role": "assistant", "content": safe_reply})

        self.Lilith_mem.save_memory(self.memory)
        return safe_reply
    
    def set_user_name(self, name):
        self.Lilith_mem.set_user_name(self.memory, name)

    def get_user_name(self):
        return self.Lilith_mem.get_user_name(self.memory)
    
    def has_user_name(self):
        return self.memory["meta"].get("user_name_set", False)