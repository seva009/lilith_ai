import socket
import struct

class LilithClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.conn = None

    def connect(self):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((self.host, self.port))
            return True
        except Exception:
            return False
    
    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def set_image_path(self, image_path):
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            path_bytes = image_path.encode('utf-8')
            self.conn.send(struct.pack('I', len(path_bytes)))
            self.conn.sendall(path_bytes)
            
            ack = self.conn.recv(1)
            return ack == b'\x01'
        except Exception:
            self.disconnect()
            return False
