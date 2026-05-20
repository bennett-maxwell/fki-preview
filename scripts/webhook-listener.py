#!/usr/bin/env python3
"""Blueprint AI Pipeline — Lightweight Webhook Listener
Receives POST from GHL form submission, delegates to ghl-webhook-handler.sh
Runs on port 8090. No external dependencies required.
"""
import http.server
import subprocess
import os
import sys

PORT = int(os.environ.get('WEBHOOK_PORT', '8090'))
HANDLER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ghl-webhook-handler.sh')

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''

        import datetime
        payload_log = os.path.expanduser('~/.openclaw/logs/blueprint-webhook-payloads.jsonl')
        os.makedirs(os.path.dirname(payload_log), exist_ok=True)
        with open(payload_log, 'a') as log_f:
            import json as _json
            log_f.write(_json.dumps({"ts": datetime.datetime.utcnow().isoformat()+"Z", "path": self.path, "body_len": len(body), "body_preview": body[:200]}) + "\n")
        try:
            result = subprocess.run(
                ['bash', HANDLER_SCRIPT],
                input=body,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=os.path.dirname(HANDLER_SCRIPT)
            )
            # Parse response from handler (it outputs HTTP-like response)
            output = result.stdout
            if 'HTTP/1.1 4' in output or 'HTTP/1.1 5' in output:
                self.send_response(400)
            else:
                self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            # Strip HTTP headers from handler output, send just the JSON body
            lines = output.split('\n')
            json_start = False
            response_body = []
            for line in lines:
                if json_start or line.strip().startswith('{'):
                    json_start = True
                    response_body.append(line)
            self.wfile.write('\n'.join(response_body).encode('utf-8') if response_body else b'{"ok":true}')
        except subprocess.TimeoutExpired:
            self.send_response(504)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":"handler timeout"}')
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"error":"{str(e)}"}}'.encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"service":"blueprint-ai-webhook","status":"healthy"}')

    def log_message(self, format, *args):
        sys.stderr.write(f"[webhook] {self.client_address[0]} - {format % args}\n")

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    print(f'Blueprint webhook listener on port {PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
