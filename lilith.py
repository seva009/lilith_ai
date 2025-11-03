import json, os
import subprocess, random
from datetime import datetime
from openai import OpenAI
import configparser
import lilith_memory
import lilith_display

config = configparser.ConfigParser()
config.read('config.ini')

client = OpenAI(
    base_url = config['server']['base_url'],  # LM Studio local endpoint
    api_key  = config['server']['api_key']    # LM Studio ignores this
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSONA_FILE = os.path.join(BASE_DIR, config['ai_config']['persona'])
MEMORY_FILE = os.path.join(BASE_DIR, config['ai_config']['memory'])
DEFAULT_USER_NAME = ""

Lilith_mem = lilith_memory.LilithMemory(BASE_DIR, config, DEFAULT_USER_NAME)
Lilith_display = lilith_display.LilithDisplay(BASE_DIR, config)

def lilith_reply(prompt, persona, memory):
    user_name = Lilith_mem.get_user_name(memory)
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
            "content": identity + persona + f"\n\nhis name is {user_name}. respond to him now:\n{prompt}",
        },
    ]

    # 🧠 Use Mistral 7B Instruct v0.3
    response = client.chat.completions.create(
        model="mistral-7b-instruct-v0.3",
        messages=messages,
        temperature=config["ai_config"].getfloat('temperature'),
        top_p=0.9,
        max_tokens=config["ai_config"].getint('max_tokens'),
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

    memory["conversation"].append({"role": "user", "content": prompt})
    memory["conversation"].append({"role": "assistant", "content": safe_reply})

    Lilith_mem.save_memory(memory)
    return safe_reply

if __name__ == "__main__":
    persona = Lilith_mem.load_persona()
    memory = Lilith_mem.load_memory()

    
import threading, itertools, sys, time
import os, subprocess, shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FEH_PID_FILE = os.path.join(BASE_DIR, "feh_pid.txt")
CURRENT_IMG = os.path.join(BASE_DIR, "assets", "current.png")
VIEWER_SCRIPT = os.path.join(BASE_DIR, "viewer.py")

# state tracking for automatic revert
LAST_SHOWN_STATE = None
REVERT_TIMER = None
REVERT_DELAY = 5  # seconds to wait before returning to idle
# blinking controls
BLINK_THREAD = None
BLINK_RUNNING = False

# keywords that indicate someone is questioning her existence
EXISTENCE_KEYWORDS = [
    "exist",
    "existence",
    "do you exist",
    "are you real",
    "you're not real",
    "youre not real",
    "not real",
    "imaginary",
    "fake",
]

Lilith_display.show_lilith("thinking")


spinning = False

def spinner():
    for c in itertools.cycle(['♡', '❤', '♥', '❤']):
        if not spinning:
            break
        sys.stdout.write(f'\rLilith is thinking {c}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * 30 + '\r')  # clear line


if __name__ == "__main__":
    persona = Lilith_mem.load_persona()
    memory = Lilith_mem.load_memory()
    if not memory["meta"].get("user_name_set"):
        while True:
            entered = input("Lilith tilts her head. \"what should i call you?\" ").strip()
            if entered:
                Lilith_mem.set_user_name(memory, entered)
                break
            print("...she waits. give her a name to hold onto.")
    current_name = Lilith_mem.get_user_name(memory)

    print("Lilith is here. she gazes softly at you~ Type 'exit' to leave.\n")
    lilith_display.show_lilith("idle")
    # start blink loop
    try:
        BLINK_RUNNING = True
        BLINK_THREAD = threading.Thread(target=Lilith_display._blink_loop, daemon=True)
        BLINK_THREAD.start()
    except Exception:
        pass
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Lilith: ...until next time, then.")
            # 🌙 close feh window on exit
            if os.path.exists(FEH_PID_FILE):
                with open(FEH_PID_FILE) as f:
                  pid = f.read().strip()
            try:
                os.system(f"kill {pid}")
            except:
                pass
            os.remove(FEH_PID_FILE)

            # stop blink thread and exit
            try:
                BLINK_RUNNING = False
            except Exception:
                pass
            break
        # if the user questions Lilith's existence, show disappointed immediately
        u_lower = user_input.lower()
        existence_trigger = any(k in u_lower for k in EXISTENCE_KEYWORDS)
        if existence_trigger:
            Lilith_display.show_lilith("dissapointed")

        spinning = True
        t = threading.Thread(target=spinner)
        t.start()

        reply = lilith_reply(user_input, persona, memory)
        r_lower = reply.lower()
        if any(word in r_lower for word in ["sorry", "sad", "hurt", "lonely", "pain", "trying"]):
            emotion = "sad"
        elif any(word in r_lower for word in ["love", "warm", "smile", "happy", "glad", "joy"]):
            emotion = "smile"
        elif any(word in r_lower for word in ["...", "heavy", "missed"]):
            emotion = "thinking"
        elif any(phrase in r_lower for phrase in ["of course", "ofcourse"]):
            emotion = "cheeky"
        else:
            # default: use talking expression for any other content, then revert to idle
            emotion = "talking"

        # show_lilith will schedule a revert to 'idle' after REVERT_DELAY seconds
        Lilith_display.show_lilith(emotion)
        

        spinning = False
        t.join()

        def type_out(text):
            sys.stdout.write("Lilith: ")
            sys.stdout.flush()
            for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                if char in [".", "…"]:
                    time.sleep(0.4)
                elif char in [",", "~"]:
                    time.sleep(0.25)
                else:
                    time.sleep(0.03)
            # Add newline after Lilith's reply
            sys.stdout.write("\n\n")
            sys.stdout.flush()
            time.sleep(0.8)

        type_out(reply)
