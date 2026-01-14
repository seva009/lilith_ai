# A small excuse: I. TRIED. EVERY. OTHER. WAY. There is no normal way to do this in tkinter.
# So here we are, a socket server in the viewer process receiving images from the main process. 
# It works. Don't judge me.
import os
import tkinter as tk
from PIL import Image, ImageTk
import socket
import threading
import struct
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

def main():
    root = tk.Tk()
    root.title("Lilith")
    root.configure(bg='black')
    root.geometry("400x600+1200+200")
    root.resizable(True, True)
    root.wm_attributes("-topmost", True)
    
    lbl = tk.Label(root, bg='black')
    lbl.pack(fill=tk.BOTH, expand=True)

    img_obj = orig_img = None
    current_image_path = None
    resize_timer = None

    def update_display():
        nonlocal img_obj
        if orig_img:
            w, h = lbl.winfo_width(), lbl.winfo_height()
            if w > 1 and h > 1:
                iw, ih = orig_img.size
                scale = min(w/iw, h/ih)
                new_size = (int(iw*scale), int(ih*scale))
                img = orig_img.resize(new_size, Image.Resampling.LANCZOS)
                img_obj = ImageTk.PhotoImage(img)
                lbl.config(image=img_obj)

    def on_resize(event):
        nonlocal resize_timer
        if event.widget == root:
            if resize_timer:
                root.after_cancel(resize_timer)
            resize_timer = root.after(100, update_display)

    def load_image(path):
        nonlocal orig_img, current_image_path
        try:
            if os.path.exists(path):
                current_image_path = path
                orig_img = Image.open(path).convert('RGBA')
                update_display()
                return True
        except Exception:
            pass
        return False

    def handle_client(conn, addr):
        try:
            while True:
                path_size_data = conn.recv(4)
                if not path_size_data:
                    break
                
                path_size = struct.unpack('I', path_size_data)[0]
                
                path_data = b''
                while len(path_data) < path_size:
                    chunk = conn.recv(min(4096, path_size - len(path_data)))
                    if not chunk:
                        break
                    path_data += chunk
                
                if len(path_data) == path_size:
                    path_str = path_data.decode('utf-8')
                    success = load_image(path_str)
                    conn.send(b'\x01' if success else b'\x00')
        except Exception:
            pass
        finally:
            conn.close()

    def socket_server():
        HOST = config['viewer_socket'].get('host', fallback='localhost')
        PORT = config['viewer_socket'].getint('port', fallback=8888)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            
            while True:
                try:
                    conn, addr = s.accept()
                    client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                    client_thread.start()
                except Exception:
                    pass

    server_thread = threading.Thread(target=socket_server, daemon=True)
    server_thread.start()

    root.bind('<Configure>', on_resize)
    root.mainloop()

if __name__ == "__main__":
    main()
