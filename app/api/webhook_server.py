import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class OAuthCallbackData:
    def __init__(self):
        self.code = None
        self.state = None
        self.error = None
        self.received = threading.Event()


class WebhookEventStore:
    def __init__(self):
        self.events = []
        self.lock = threading.Lock()

    def add_event(self, event_data: dict):
        with self.lock:
            self.events.append(event_data)

    def get_events(self):
        with self.lock:
            return list(self.events)

    def clear(self):
        with self.lock:
            self.events.clear()


class AppWebhookHandler(BaseHTTPRequestHandler):
    oauth_callback_data = None
    webhook_event_store = None
    webhook_callback = None

    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/callback":
            self._handle_oauth_callback(parsed_url)
            return

        if parsed_url.path == "/health":
            self._send_json_response(
                status_code=200,
                payload={
                    "status": "ok",
                    "message": "SOFTWARE ML webhook server online",
                },
            )
            return

        self._send_json_response(
            status_code=404,
            payload={"error": "Rota não encontrada"},
        )

    def do_POST(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/webhook":
            self._handle_webhook()
            return

        self._send_json_response(
            status_code=404,
            payload={"error": "Rota não encontrada"},
        )

    def _handle_oauth_callback(self, parsed_url):
        query = parse_qs(parsed_url.query)

        if AppWebhookHandler.oauth_callback_data is not None:
            AppWebhookHandler.oauth_callback_data.code = query.get("code", [None])[0]
            AppWebhookHandler.oauth_callback_data.state = query.get("state", [None])[0]
            AppWebhookHandler.oauth_callback_data.error = query.get("error", [None])[0]
            AppWebhookHandler.oauth_callback_data.received.set()

        html = """
        <html>
            <head>
                <meta charset="utf-8">
                <title>SOFTWARE ML</title>
            </head>
            <body style="background:#07111f;color:#f4f1e8;font-family:Arial;padding:40px;">
                <h1>SOFTWARE ML</h1>
                <p>Autorização recebida com sucesso.</p>
                <p>Você já pode fechar esta aba e voltar ao app.</p>
            </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _handle_webhook(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b""

        body_text = raw_body.decode("utf-8", errors="ignore")

        try:
            body_json = json.loads(body_text) if body_text else {}
        except json.JSONDecodeError:
            body_json = {"raw_body": body_text}

        event_data = {
            "method": "POST",
            "path": self.path,
            "headers": dict(self.headers),
            "body": body_json,
        }

        if AppWebhookHandler.webhook_event_store is not None:
            AppWebhookHandler.webhook_event_store.add_event(event_data)

        print("\n[WEBHOOK RECEBIDO]")
        print(json.dumps(event_data, indent=2, ensure_ascii=False))

        if AppWebhookHandler.webhook_callback is not None:
            try:
                AppWebhookHandler.webhook_callback(event_data)
            except Exception as error:
                print(f"Erro ao processar webhook: {error}")

        self._send_json_response(
            status_code=200,
            payload={
                "status": "received",
                "message": "Webhook recebido com sucesso",
            },
        )

    def _send_json_response(self, status_code: int, payload: dict):
        response_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def log_message(self, format, *args):
        return


class AppWebhookServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.oauth_callback_data = OAuthCallbackData()
        self.webhook_event_store = WebhookEventStore()
        self.httpd = None
        self.server_thread = None

    def start(self, webhook_callback=None):
        AppWebhookHandler.oauth_callback_data = self.oauth_callback_data
        AppWebhookHandler.webhook_event_store = self.webhook_event_store
        AppWebhookHandler.webhook_callback = webhook_callback

        self.httpd = ThreadingHTTPServer((self.host, self.port), AppWebhookHandler)

        self.server_thread = threading.Thread(
            target=self.httpd.serve_forever,
            daemon=True,
        )
        self.server_thread.start()

        print(f"Webhook server iniciado em http://{self.host}:{self.port}")

    def stop(self):
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
            print("Webhook server finalizado.")

    def wait_for_oauth_callback(self, timeout: int = 180):
        self.oauth_callback_data.received.wait(timeout=timeout)
        return self.oauth_callback_data

    def get_received_events(self):
        return self.webhook_event_store.get_events()