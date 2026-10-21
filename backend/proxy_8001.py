import http.server
import socketserver
import urllib.request
import urllib.error
import sys

TARGET = 'http://127.0.0.1:8000'
PORT = 8001

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()

    def do_DELETE(self):
        self._proxy()

    def do_PATCH(self):
        self._proxy()

    def do_OPTIONS(self):
        origin = self.headers.get('Origin', 'http://localhost:5174')
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, Accept, X-Requested-With, Origin')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _proxy(self):
        url = TARGET + self.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else None

        req = urllib.request.Request(url, data=body, method=self.command)
        for k, v in self.headers.items():
            if k.lower() not in ('host', 'content-length'):
                req.add_header(k, v)

        client_origin = self.headers.get('Origin', 'http://localhost:5174')

        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                has_origin = False
                for k, v in resp.getheaders():
                    if k.lower() != 'transfer-encoding':
                        if k.lower() == 'access-control-allow-origin':
                            has_origin = True
                        self.send_header(k, v)
                if not has_origin:
                    self.send_header('Access-Control-Allow-Origin', client_origin)
                    self.send_header('Access-Control-Allow-Credentials', 'true')
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            has_origin = False
            for k, v in e.headers.items():
                if k.lower() != 'transfer-encoding':
                    if k.lower() == 'access-control-allow-origin':
                        has_origin = True
                    self.send_header(k, v)
            if not has_origin:
                self.send_header('Access-Control-Allow-Origin', client_origin)
                self.send_header('Access-Control-Allow-Credentials', 'true')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', client_origin)
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

if __name__ == '__main__':
    with socketserver.TCPServer(('', PORT), ProxyHandler) as httpd:
        print(f"Proxying port {PORT} -> {TARGET}")
        httpd.serve_forever()
