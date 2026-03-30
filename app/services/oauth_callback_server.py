from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class OAuthCallbackData:
    def __init__(self):
        self.code: str | None = None
        self.state: str | None = None
        self.error: str | None = None
        self.received = threading.Event()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    callback_data: OAuthCallbackData | None = None

    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path != "/callback":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        query = parse_qs(parsed_url.query)

        if self.callback_data is not None:
            self.callback_data.code = query.get("code", [None])[0]
            self.callback_data.state = query.get("state", [None])[0]
            self.callback_data.error = query.get("error", [None])[0]
            self.callback_data.received.set()

        html = """
        <html>
            <head>
                <meta charset="utf-8">
                <title>SOFTWARE ML</title>
            </head>
            <body style="background:#07111f;color:#f4f1e8;font-family:Arial;padding:40px;">
                <h1>SOFTWARE ML</h1>
                <p>Autorização recebida.</p>
                <p>Você já pode fechar esta janela e voltar ao app.</p>
            </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        return


class OAuthCallbackServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.callback_data = OAuthCallbackData()
        self.httpd: HTTPServer | None = None
        self.server_thread: threading.Thread | None = None

    def start(self):
        OAuthCallbackHandler.callback_data = self.callback_data
        self.httpd = HTTPServer((self.host, self.port), OAuthCallbackHandler)

        self.server_thread = threading.Thread(
            target=self.httpd.serve_forever,
            daemon=True,
        )
        self.server_thread.start()

    def wait_for_callback(self, timeout: int = 180) -> OAuthCallbackData:
        self.callback_data.received.wait(timeout=timeout)
        return self.callback_data

    def stop(self):
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None