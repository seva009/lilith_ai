import os
import configparser
import modules.lilith_ai as lilith_ai
import modules.lilith_display as lilith_display
import threading
import itertools
import sys
import time

config = configparser.ConfigParser()
config.read('config.ini')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_USER_NAME = ""

Lilith_display = lilith_display.LilithDisplay(BASE_DIR, config)
Lilith_AI = lilith_ai.LilithAI(Lilith_display, config, BASE_DIR, DEFAULT_USER_NAME)

is_extended = config['lilith_display'].get('place', fallback='glass') == 'room'
if is_extended:
    Lilith_display.show_lilith("thinking_happy")
else:
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


def type_out(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        if char in [".", "…"]:
            time.sleep(0.4)
        elif char in [",", "~"]:
            time.sleep(0.25)
        else:
            time.sleep(0.03)
    time.sleep(0.8)


if __name__ == "__main__":
    if not Lilith_AI.has_user_name():
        while True:
            type_out("Lilith tilts her head. \"what should i call you?\" ")
            entered = input().strip()
            if entered:
                Lilith_AI.set_user_name(entered)
                break
            type_out("...she waits. give her a name to hold onto.\n")
    current_name = Lilith_AI.get_user_name()

    type_out("Lilith is here. she gazes softly at you~ Type 'exit' to leave.\n")
    Lilith_display.show_lilith("idle")
    Lilith_display.set_blinking(True)  # enable blinking
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            type_out("Lilith: ...until next time, then.\n")
            break
        
        spinning = True
        t = threading.Thread(target=spinner)
        t.start()

        if is_extended:
            Lilith_display.show_lilith("thinking_happy")
        else:
            Lilith_display.show_lilith("thinking")

        reply = Lilith_AI.lilith_reply(user_input)  # Get Lilith's reply

        # show emotion based on last reply
        emotion = Lilith_AI.get_current_emotion(extended_emotions=True)

        # show_lilith will schedule a revert to 'idle' after REVERT_DELAY seconds
        Lilith_display.show_lilith(emotion)

        spinning = False
        t.join()

        type_out('Lilith: ' + reply + '\n')
