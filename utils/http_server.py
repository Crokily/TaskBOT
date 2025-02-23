import http.server
import socketserver
import threading

PORT = 10000

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    # 重写 GET 请求处理方法，返回 "OK"
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")
    
    # 对其他请求方法统一调用 do_GET
    def do_POST(self):
        self.do_GET()

    def do_PUT(self):
        self.do_GET()

    def do_DELETE(self):
        self.do_GET()

def start_http_server():
    """启动一个最简单的 HTTP 服务器，监听 10000 端口"""
    handler = SimpleHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    # 使用线程启动 HTTP 服务器，守护线程保证主程序退出时自动关闭
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    print(f"HTTP server started on port {PORT}")
