"""Loopback-only HTTP adapter for the presentation, without new dependencies."""
from __future__ import annotations

import argparse
import hmac
import json
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from tradingagents.runapi.result import InputError

from .service import DemoError, DemoService

STATIC = Path(__file__).with_name('static')


class DemoServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, service):
        if address[0] != '127.0.0.1':
            raise ValueError('The demo binds only to 127.0.0.1.')
        self.service, self.csrf_token = service, secrets.token_urlsafe(32)
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Never print uploaded input or provider diagnostics.
        return

    def _reply(self, status, body, mime='application/json; charset=utf-8', *, filename=None):
        if not isinstance(body, bytes):
            body = json.dumps(body, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        policy = ("default-src 'self'; script-src 'self'; style-src 'self'; "
                  "img-src 'self' data:; frame-src 'self'; object-src 'none'; base-uri 'none'")
        if mime.startswith('text/html') and self.path.split('?')[0] != '/':
            # Production reports contain trusted inline CSS and prohibit scripts.
            policy = "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'"
        self.send_header('Content-Security-Policy', policy)
        if filename:
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def _local_request(self):
        port = self.server.server_port
        allowed = {f'127.0.0.1:{port}', f'localhost:{port}'}
        if self.headers.get('Host') not in allowed:
            self._reply(403, {'error': 'Only the local demo origin is allowed.'})
            return False
        origin = self.headers.get('Origin')
        if origin and origin not in {f'http://{host}' for host in allowed}:
            self._reply(403, {'error': 'Cross-origin requests are not allowed.'})
            return False
        return True

    def do_GET(self):
        if not self._local_request():
            return
        path = urlsplit(self.path).path
        try:
            static = {'/': ('index.html', 'text/html; charset=utf-8'),
                      '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                      '/style.css': ('style.css', 'text/css; charset=utf-8')}
            if path in static:
                filename, mime = static[path]
                self._reply(200, (STATIC / filename).read_bytes(), mime)
            elif path == '/api/bootstrap':
                self._reply(200, {**self.server.service.bootstrap(), 'csrf_token': self.server.csrf_token})
            elif path.startswith('/api/runs/'):
                parts = path.split('/')
                if len(parts) == 4:
                    self._reply(200, self.server.service.get(parts[3]).snapshot())
                elif len(parts) == 5:
                    kind = parts[4]
                    artifact = self.server.service.artifact(parts[3], kind)
                    mime = {'html': 'text/html; charset=utf-8', 'markdown': 'text/markdown; charset=utf-8',
                            'manifest': 'application/json; charset=utf-8'}[kind]
                    self._reply(200, artifact.read_bytes(), mime,
                                filename=artifact.name if kind != 'html' else None)
                else:
                    self._reply(404, {'error': 'Not found.'})
            else:
                self._reply(404, {'error': 'Not found.'})
        except DemoError as exc:
            self._reply(404, {'error': str(exc)})
        except (OSError, ValueError, KeyError):
            self._reply(500, {'error': 'The requested presentation artifact could not be read.'})

    def do_POST(self):
        if not self._local_request():
            return
        if not hmac.compare_digest(self.headers.get('X-Demo-Token', ''), self.server.csrf_token):
            self._reply(403, {'error': 'Reload the page to authorize this local demo session.'})
            return
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            self._reply(415, {'error': 'A JSON request is required.'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 65536:
                self._reply(413, {'error': 'Request must be between 1 and 65,536 bytes.'})
                return
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise DemoError('A JSON object is required.')
            path = urlsplit(self.path).path
            if path == '/api/prepare':
                response = self.server.service.prepare(payload)
            elif path == '/api/start':
                response = self.server.service.start(payload.get('run_id'), consent=payload.get('consent'))
            elif path == '/api/cancel':
                response = self.server.service.cancel(payload.get('run_id'))
            else:
                self._reply(404, {'error': 'Not found.'})
                return
            self._reply(200, response)
        except InputError as exc:
            self._reply(400, {'error': exc.detail, 'kind': exc.kind, 'field': exc.field,
                              'model_dispatches': 0})
        except (DemoError, ValueError, UnicodeDecodeError) as exc:
            message = str(exc) if isinstance(exc, DemoError) else 'Invalid JSON request.'
            self._reply(400, {'error': message})
        except Exception:
            self._reply(500, {'error': 'Demo request failed. No successful run is claimed.'})


def main(argv=None):
    parser = argparse.ArgumentParser(description='English TradingAgents presentation, loopback only.')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--allow-live', action='store_true', help='Enable opt-in paid model/vendor execution.')
    parser.add_argument('--open', action='store_true', help='Open the presentation in a browser.')
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error('Port must be between 0 and 65535.')
    service = DemoService(allow_live=args.allow_live)
    server = DemoServer(('127.0.0.1', args.port), service)
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'TradingAgents English Demo: {url}', flush=True)
    print('Default: scripted analysis, real application checks, zero remote model requests.', flush=True)
    if args.allow_live:
        print('Live mode is enabled; explicit confirmation can incur API costs.', flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
