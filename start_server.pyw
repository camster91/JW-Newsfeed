import http.server
import socketserver
import os

os.chdir(r"C:\Users\camst\JW-Newsfeed")

PORT = 8888

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logging

with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
    httpd.serve_forever()
