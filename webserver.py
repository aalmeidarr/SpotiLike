import json
import ure
import urequests as requests
import socket

class WebServer:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def listen(self):
        self.s.bind(("0.0.0.0", 80))
        self.s.listen(1)
        completed = False
        while not completed:
            conn, addr = self.s.accept()
            req = str(conn.recv(1024))
            if req.find("/login") == 6:
                with open("config/spotify.json", "r") as f:
                    spotify_config = json.load(f)
                auth_url = (
                    "https://accounts.spotify.com/authorize"
                    f"?client_id={spotify_config['client_id']}"
                    f"&response_type=code"
                    f"&redirect_uri=http://127.0.0.1:80/callback"
                    f"&scope=user-read-playback-state user-library-modify"
                )
                response = f"""HTTP/1.1 302 Found\r\nLocation: {auth_url}\r\n\r\n"""
                conn.send(response.encode())
            elif req.find("/callback") == 6:
                code = ure.search(r"GET /callback\?code=([^ ]+)", req).group(1)
                conn.send("HTTP/1.1 200\n")
                conn.send("Content-Type: text/html\n")
                conn.send("Connection: close\n\n")
                conn.send("<h1>Success</h1>")
                completed = True
            conn.close()
        self.s.close()
        return code
        
