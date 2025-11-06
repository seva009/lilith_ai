import os
import threading
import shutil
import sys
import subprocess
import time
import random
import modules.viewer as viewer_module


class LilithDisplay:
    def __init__(self, base_dir, config):
        self.base_dir = base_dir
        self.config = config
        self.ASSETS_PATH = config.get('lilith_display', 'assets_path', fallback='assets/')
        self.CURRENT_IMG = os.path.join(base_dir, self.ASSETS_PATH, "current.png")
        self.VIEWER_SCRIPT = os.path.join(base_dir, config.get('lilith_display', 'display_path', fallback='modules/viewer.py'))
        self.REVERT_DELAY = config.getint('lilith_display', 'revert_delay', fallback=5)
        self.BLINK_MIN = config.getint('lilith_display', 'blink_min_interval', fallback=2)
        self.BLINK_MAX = config.getint('lilith_display', 'blink_max_interval', fallback=4)
        self.BLINK_DURATION = config.getfloat('lilith_display', 'blink_duration', fallback=0.25)
        self.LAST_SHOWN_STATE = None
        self.LAST_CHANGE_TIME = 0
        self.can_blink = True
        self._blink_stop_event = threading.Event()
        # Start the viewer process
        subprocess.Popen([sys.executable, self.VIEWER_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def show_lilith(self, state, schedule_revert=True):
        state_img = os.path.join(self.base_dir, self.ASSETS_PATH, f"{state}.png")
        if not os.path.exists(state_img):
            print(f"Image for state '{state}' not found at {state_img}.")
            return

        try:
            shutil.copy(state_img, self.CURRENT_IMG)
            self.LAST_SHOWN_STATE = state
            self.LAST_CHANGE_TIME = time.time()
        except Exception as e:
            print(f"Error updating image: {e}")
            return

        if schedule_revert:
            def revert_after_delay():
                time.sleep(self.REVERT_DELAY)
                if time.time() - self.LAST_CHANGE_TIME >= self.REVERT_DELAY:
                    self.show_lilith("idle", schedule_revert=False)

            threading.Thread(target=revert_after_delay, daemon=True).start()

    def set_blinking(self, enable):
        if enable:
            def blink_loop():
                while True:
                    interval = random.uniform(self.BLINK_MIN, self.BLINK_MAX)
                    time.sleep(interval)
                    prev_state = self.LAST_SHOWN_STATE
                    self.show_lilith("blinking", schedule_revert=False)
                    time.sleep(self.BLINK_DURATION)
                    if prev_state != "blinking":
                        self.show_lilith(prev_state, schedule_revert=False)

            threading.Thread(target=blink_loop, daemon=True).start()
