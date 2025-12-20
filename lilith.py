import os
import configparser
import modules.lilith_ai as lilith_ai
import modules.lilith_display as lilith_display
import threading
import itertools
import sys
import time
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    filemode="a",
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

### --------------------------------Argument parser for config editing
parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="cmd")
sub.add_parser("edit")
sub.add_parser("conv_edit")
args = parser.parse_args()
if args.cmd == "edit":
    from modules import config_edit
    config_edit.run_config_editor()
    sys.exit(0)
elif args.cmd == "conv_edit":
    from modules import conv_mgmt
    config = configparser.ConfigParser()  # Create a config parser
    config.read('config.ini')
    conv_mgmt.run_conversation_manager(lilith_ai.LilithAI(None, config, NO_AI=True))
    sys.exit(0)
### --------------------------------End argument parser--------------------------------

config = configparser.ConfigParser()  # Create a config parser
config.read('config.ini')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Base directory of the application

Lilith_display = lilith_display.LilithDisplay(BASE_DIR, config)  # Initialize LilithDisplay
Lilith_AI = lilith_ai.LilithAI(Lilith_display, config, BASE_DIR)  # Initialize LilithAI

is_extended = config['lilith_display'].get('place') == 'room'
if is_extended:
    Lilith_display.show_lilith("thinking_happy")
else:
    Lilith_display.show_lilith("thinking")

spinning = False # Spinner control variable


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
