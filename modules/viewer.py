import os
import tkinter as tk
from PIL import Image, ImageTk
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_IMG = os.path.join(BASE_DIR, '../assets', "current.png")

def main():
    print("Starting Lilith viewer...")
    root = tk.Tk()
    root.title("Lilith")
    root.configure(bg='black')
    root.geometry("400x600+1200+200")
    root.resizable(True, True)
    root.wm_attributes("-topmost", True)
    
    lbl = tk.Label(root, bg='black')
    lbl.pack(fill=tk.BOTH, expand=True)

    last_mtime = img_obj = orig_img = None
    resize_job = None

    def rescale_to_window():
        nonlocal img_obj
        w, h = lbl.winfo_width(), lbl.winfo_height()
        if w > 1 and h > 1 and orig_img:
            iw, ih = orig_img.size
            scale = min(w/iw, h/ih)
            new_size = (int(iw*scale), int(ih*scale))
            img = orig_img.resize(new_size, Image.Resampling.LANCZOS)
            img_obj = ImageTk.PhotoImage(img)
            lbl.config(image=img_obj)


    def on_resize(event):
        nonlocal resize_job
        if resize_job:
            root.after_cancel(resize_job)
        resize_job = root.after(100, rescale_to_window)


    def load_image():
        nonlocal last_mtime, img_obj, orig_img
        if os.path.exists(CURRENT_IMG):
            try:
                mtime = os.path.getmtime(CURRENT_IMG)
                if last_mtime != mtime:
                    last_mtime = mtime
                    orig_img = Image.open(CURRENT_IMG).convert('RGBA')
                    rescale_to_window()
            except Exception as e:
                print(f"Load error: {e}")

    def poll():
        load_image()
        root.after(200, poll)

    root.bind('<Configure>', on_resize)
    poll()
    root.mainloop()


if __name__ == "__main__":
    main()
