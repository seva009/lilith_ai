import os
import sys
import subprocess
import threading
import shutil
import time

class LilithDisplay:
    def __init__(self, base_dir, config):
        self.base_dir = base_dir
        self.config = config
        self.FEH_PID_FILE = os.path.join(base_dir, "feh_pid.txt")
        self.CURRENT_IMG = os.path.join(base_dir, "assets", "current.png")
        self.VIEWER_SCRIPT = os.path.join(base_dir, "viewer.py")
        self.REVERT_DELAY = config.getint('lilith_display', 'revert_delay', fallback=5)
        self.BLINK_MIN = config.getint('lilith_display', 'blink_min_interval', fallback=2)
        self.BLINK_MAX = config.getint('lilith_display', 'blink_max_interval', fallback=4)
        self.BLINK_DURATION = config.getfloat('lilith_display', 'blink_duration', fallback=0.25)
        return
    
    def _proc_is_running(pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True
    
    def show_lilith(self, state, schedule_revert=True):
        """Display Lilith's portrait.

        Starts a single detached feh process that watches `assets/current.png` with
        --reload enabled. Subsequent calls simply overwrite `current.png` with the
        desired state image so feh reloads instead of launching a new window.
        """
        img_path = os.path.join(self.base_dir, "assets", f"{state}.png")
        if not os.path.exists(img_path):
            print(f"[⚠️ Image not found: {img_path}]")
            return

        # capture current active window so we can restore focus (if xdotool exists)
        active_win = None
        try:
            xdotool = shutil.which("xdotool")
            if xdotool:
                active_win = subprocess.check_output([xdotool, "getactivewindow"], stderr=subprocess.DEVNULL).decode().strip()
        except Exception:
            active_win = None

        # ensure assets/current.png exists and is the requested image
        try:
            # copy (atomic-ish) to the watched filename
            shutil.copyfile(img_path, self.CURRENT_IMG)
        except Exception:
            # fallback to symlink if copy fails
            try:
                if os.path.exists(self.CURRENT_IMG):
                    os.remove(self.CURRENT_IMG)
                os.symlink(img_path, self.CURRENT_IMG)
            except Exception:
                # last resort: leave the original image path (may cause a new feh launch)
                pass

        # if feh is not running yet, start it watching the fixed current.png
        need_start = True
        if os.path.exists(self.FEH_PID_FILE):
            try:
                with open(self.FEH_PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                if self._proc_is_running(pid):
                    need_start = False
            except Exception:
                need_start = True

        if need_start:
            # prefer a bundled Tkinter viewer that tends not to steal focus; if
            # that isn't available, try feh as a fallback.
            proc = None
            try:
                if os.path.exists(self.VIEWER_SCRIPT):
                    proc = subprocess.Popen([sys.executable, self.VIEWER_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
            except Exception:
                proc = None

            if proc is None:
                # start detached feh process (watching CURRENT_IMG)
                proc = subprocess.Popen([
                    "feh",
                    "--title", "Lilith",
                    "--geometry", "400x600+1200+200",
                    "--no-fullscreen",
                    "--borderless",
                    "--scale-down",
                    "--auto-zoom",
                    "--zoom", "20%",
                    "--reload", "0.5",
                    self.CURRENT_IMG,
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
            with open(self.FEH_PID_FILE, "w") as f:
                f.write(str(proc.pid))
            # restore focus to previous window (usually the terminal)
            try:
                if active_win and xdotool:
                    subprocess.Popen([xdotool, "windowactivate", "--sync", active_win], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

        else:
            # try to restore focus after updating the image so the terminal remains active
            try:
                if active_win and xdotool:
                    subprocess.Popen([xdotool, "windowactivate", "--sync", active_win], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass


    # update last shown state and optionally schedule revert to idle
        global LAST_SHOWN_STATE, REVERT_TIMER
        LAST_SHOWN_STATE = state
        # cancel any existing revert timer
        try:
            if REVERT_TIMER is not None and REVERT_TIMER.is_alive():
                REVERT_TIMER.cancel()
        except Exception:
            pass

        if schedule_revert and state != "idle":
            # schedule a revert back to idle after REVERT_DELAY seconds
            try:
                REVERT_TIMER = threading.Timer(self.REVERT_DELAY, lambda: self.show_lilith("idle", schedule_revert=False)) # its very bad to call yourself
                REVERT_TIMER.daemon = True
                REVERT_TIMER.start()
            except Exception:
                REVERT_TIMER = None
        
    def _blink_loop(self):
        """Background loop that triggers blinking when Lilith is idle."""
        global BLINK_RUNNING
        import random
        while BLINK_RUNNING:
            # sleep a random interval
            wait = random.uniform(self.BLINK_MIN, self.BLINK_MAX)
            for _ in range(int(wait * 10)):
                if not BLINK_RUNNING:
                    return
                time.sleep(0.1)
            # only blink when idle and no other revert timer is active
            try:
                if LAST_SHOWN_STATE == "idle":
                    # show blinking briefly without scheduling another revert
                    self.show_lilith("blinking", schedule_revert=False)
                    # after BLINK_DURATION, revert to idle
                    timer = threading.Timer(self.BLINK_DURATION, lambda: self.show_lilith("idle", schedule_revert=False))
                    timer.daemon = True
                    timer.start()
            except Exception:
                pass