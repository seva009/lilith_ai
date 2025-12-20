import modules.lilith_memory as lilith_memory
import modules._iface as _iface
import logging

logger = logging.getLogger(__name__)

class LilithAI:
    def __init__(self, Lilith_display, config, BASE_DIR="", DEFAULT_USER_NAME="", NO_AI=False):
        self.Lilith_display = Lilith_display
        self.Lilith_mem = lilith_memory.LilithMemory(BASE_DIR, config, DEFAULT_USER_NAME)
        self.config = config
        self.persona = self.Lilith_mem.load_persona()
        self.memory = self.Lilith_mem.load_memory()
        self.user_name = self.Lilith_mem.get_user_name(self.memory)
        self.last_reply = ""

        # Ensure memory uses the new multiple-conversation layout
        self._ensure_conversations()

        if NO_AI:
            self.client = None
            logger.info("LilithAI initialized in NO_AI mode.")
            return
        else:
            self.client = _iface.AIInterface(
                model=config["ai_config"].get('ai_model'),
                temperature=config["ai_config"].getfloat('temperature', fallback=0.85),
                max_tokens=config["ai_config"].getint('max_tokens', fallback=120),
                base_url=config['server']['base_url'],
                api_key=config['server']['api_key']
            )

        logger.info("LilithAI initialized successfully.")

    def _ensure_conversations(self):
        # Migrate older single "conversation" to "conversations" structure if necessary
        if "conversations" not in self.memory:
            if "conversation" in self.memory:
                logger.warning("Migrating old conversation format to new.")
                self.memory["conversations"] = {"default": self.memory.get("conversation", []) or []}
            else:
                logger.warning("No conversation found, initializing empty default.")
                self.memory["conversations"] = {"default": []}
        # Ensure current conversation key exists
        if "current_conversation" not in self.memory:
            logger.warning("Current conversation not found, initializing to default.")
            self.memory["current_conversation"] = self.memory.get("current_conversation", "default")
        # Ensure meta exists
        if "meta" not in self.memory:
            logger.warning("Meta information not found, initializing default meta.")
            self.memory["meta"] = {}
        # Save migrated memory
        self.Lilith_mem.save_memory(self.memory)

    def _get_current_conv_list(self):
        name = self.memory.get("current_conversation", "default")
        convs = self.memory.setdefault("conversations", {})
        return name, convs.setdefault(name, [])

    def lilith_reply(self, prompt):
        if self.client is None:
            logger.error("LilithAI in NO_AI mode, no reply generated.")
            return "..."
        conv_name, conv = self._get_current_conv_list()

        # Initialize system persona message if conversation is empty
        if not conv:
            conv.extend([
                {
                    "role": "system",
                    "content": self.persona + f"\n\nhis name is {self.user_name}.",
                },
            ])

        conv.append({"role": "user", "content": prompt})

        response = self.client.get_response(conv)

        reply = response.strip()
        reply = reply.split(". ")
        reply = ". ".join(reply[:2]).strip()

        conv.append({"role": "assistant", "content": reply})

        # persist
        self.memory["conversations"][conv_name] = conv
        self.Lilith_mem.save_memory(self.memory)
        self.last_reply = reply
        return reply

    # Conversation management APIs
    def create_conversation(self, name, switch_to=True):
        if not name:
            return False
        convs = self.memory.setdefault("conversations", {})
        if name in convs:
            return False
        convs[name] = []
        if switch_to:
            self.memory["current_conversation"] = name
        self.Lilith_mem.save_memory(self.memory)
        return True

    def list_conversations(self):
        return list(self.memory.get("conversations", {}).keys())

    def switch_conversation(self, name, create_if_missing=False):
        convs = self.memory.setdefault("conversations", {})
        if name not in convs:
            if create_if_missing:
                convs[name] = []
            else:
                return False
        self.memory["current_conversation"] = name
        self.Lilith_mem.save_memory(self.memory)
        return True

    def delete_conversation(self, name):
        logger.info(f"Deleting conversation: {name}")
        convs = self.memory.get("conversations", {})
        if name not in convs:
            return False
        # prevent deleting the last conversation
        if len(convs) == 1:
            logger.warning("Attempted to delete the last conversation.")
            return False
        del convs[name]
        # if deleted the current, switch to any existing
        if self.memory.get("current_conversation") == name:
            self.memory["current_conversation"] = next(iter(convs.keys()))
        self.Lilith_mem.save_memory(self.memory)
        return True

    def get_current_conversation_name(self):
        return self.memory.get("current_conversation", "default")

    def set_user_name(self, name):
        self.Lilith_mem.set_user_name(self.memory, name)
        # keep user_name in sync
        self.user_name = self.Lilith_mem.get_user_name(self.memory)
        self.Lilith_mem.save_memory(self.memory)

    def get_user_name(self):
        return self.Lilith_mem.get_user_name(self.memory)

    def has_user_name(self):
        return self.memory.get("meta", {}).get("user_name_set", False)

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
