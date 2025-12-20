import modules.lilith_memory as lilith_memory
import modules._iface as _iface

class LilithAI:
    def __init__(self, Lilith_display, config, BASE_DIR="", DEFAULT_USER_NAME=""):
        self.client = _iface.AIInterface(
            model=config["ai_config"].get('ai_model'),
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

    def lilith_reply(self, prompt):
        if not self.memory["conversation"]:
            self.memory["conversation"] = [
                {
                    "role": "system",
                    "content":  self.persona + f"\n\nhis name is {self.user_name}.",
                },
            ]
        
        self.memory["conversation"].append({"role": "user", "content": prompt})
        
        response = self.client.get_response(self.memory["conversation"])
        
        reply = response.strip()
        reply = reply.split(". ")
        reply = ". ".join(reply[:2]).strip()
        
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

        safe_reply = _sanitize(reply)

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
    
    def get_current_emotion(self, extended_emotions=False):
        r_lower = self.last_reply.lower()
        
        if extended_emotions:
            if any(word in r_lower for word in ["confused", "not sure", "don't know", "dunno", "what?", "huh?", "what do you mean", "i don't understand", "confusion", "puzzled"]):
                return "confused"
            elif any(word in r_lower for word in ["happy", "happiness", "joy", "great", "fantastic", "awesome", "excited", "thrilled", "overjoyed", "ecstatic", "delighted", "wonderful"]):
                return "happy"
            elif any(word in r_lower for word in ["playful", "play", "joking", "kidding", "teasing", "funny", "laugh", "lol", "haha", "hehe", "joke", "wit", "humor"]):
                return "playful"
            elif any(word in r_lower for word in ["sad", "sadness", "unhappy", "depressed", "miserable", "sorrow", "grief", "heartbroken", "down", "blue", "melancholy", "gloomy"]):
                return "sad"
            elif any(word in r_lower for word in ["sleep", "tired", "exhausted", "bed", "nap", "drowsy", "yawn", "fatigue", "weary", "rest", "zzz", "asleep"]):
                return "sleep"
            elif any(word in r_lower for word in ["smile", "smiling", "grin", "smiled", "grinning", "beaming", "bright", " cheerful"]):
                return "smile"
            elif any(word in r_lower for word in ["thinking happy", "positive thought", "good idea", "bright idea", "optimistic", "hopeful", "thinking positively"]):
                return "thinking_happy"
            elif any(word in r_lower for word in ["thinking sad", "negative thought", "bad idea", "worried thought", "pessimistic", "concerned", "thinking negatively"]):
                return "thinking_sad"
            else:
                return "idle"
        else:
            if any(word in r_lower for word in ["sorry", "sad", "hurt", "lonely", "pain", "trying", "apologize", "regret", "mourn", "grieve", "heartache", "disappointed"]):
                return "sad"
            elif any(word in r_lower for word in ["love", "warm", "smile", "happy", "glad", "joy", "cherish", "dear", "fond", "sweet", "adore", "bliss", "content", "pleased"]):
                return "smile"
            elif any(word in r_lower for word in ["...", "heavy", "missed", "miss", "longing", "alone", "quiet", "ponder", "contemplate", "reflect", "consider", "meditate", "ruminate"]):
                return "thinking"
            elif any(phrase in r_lower for phrase in ["of course", "ofcourse", "certainly", "definitely", "absolutely", "surely", "without doubt"]):
                return "cheeky"
            else:
                return "talking"
