import os
import sys
import subprocess
import threading
import shutil
import time
import queue

class LilithDisplay:
    def __init__(self, base_dir, config):
        self.base_dir = base_dir
        self.config = config
        self.ASSETS_PATH = config.get('lilith_display', 'assets_path', fallback='assets/')
        self.CURRENT_IMG = os.path.join(base_dir, self.ASSETS_PATH, "current.png")
        self.VIEWER_SCRIPT = os.path.join(base_dir, "viewer.py")
        self.REVERT_DELAY = config.getint('lilith_display', 'revert_delay', fallback=5)
        self.BLINK_MIN = config.getint('lilith_display', 'blink_min_interval', fallback=2)
        self.BLINK_MAX = config.getint('lilith_display', 'blink_max_interval', fallback=4)
        self.BLINK_DURATION = config.getfloat('lilith_display', 'blink_duration', fallback=0.25)
        self.LAST_SHOWN_STATE = None
        self.LAST_CHANGE_TIME = 0
        subprocess.Popen([sys.executable, self.VIEWER_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    
    def _proc_is_running(pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True
    
    def show_lilith(self, state, schedule_revert=True):
        state_img = os.path.join(self.base_dir, self.ASSETS_PATH, f"{state}.png")
        if not os.path.exists(state_img):
            print(f"Image for state '{state}' not found at {state_img}.")
            return

        try:
            os.remove(self.CURRENT_IMG)
        except Exception:
            pass
            shutil.copyfile(state_img, self.CURRENT_IMG)
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