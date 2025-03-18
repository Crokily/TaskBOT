import http.server
import socketserver
import threading

PORT = 10000

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")
    
    def do_POST(self):
        self.do_GET()

    def do_PUT(self):
        self.do_GET()

    def do_DELETE(self):
        self.do_GET()

def start_http_server():
    """Starts a simple HTTP server, listening on port 10000"""
    handler = SimpleHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    # Start the HTTP server in a thread, using a daemon thread to ensure it closes automatically when the main program exits.
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    print(f"HTTP server started on port {PORT}")
