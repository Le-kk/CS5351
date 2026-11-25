"""Deploy the exported frontend and real backend on one loopback origin."""
from __future__ import annotations

import argparse
import hmac
import json
import mimetypes
import secrets
import webbrowser
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from tradingagents.runapi.result import InputError

from .console_service import ConsoleService
from .server import Handler
from .service import ROOT, DemoError


class ConsoleServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, service, frontend):
        if address[0] != '127.0.0.1':
            raise ValueError('The presentation console is local-only.')
        self.frontend = Path(frontend).resolve()
        if not (self.frontend / 'index.html').is_file():
            raise ValueError('Frontend build missing. Run npm run build in the nocode folder first.')
        self.service, self.csrf_token = service, secrets.token_urlsafe(32)
        super().__init__(address, ConsoleHandler)


class ConsoleHandler(Handler):
    def _reply(self, status, body, mime='application/json; charset=utf-8', *, filename=None):
        if not isinstance(body, bytes):
            body = json.dumps(body, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy',
                         "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                         "img-src 'self' data:; connect-src 'self'; frame-src 'self' blob:; "
                         "object-src 'none'; base-uri 'none'; frame-ancestors 'self'")
        if filename:
            safe = ''.join(c for c in filename if c.isascii() and (c.isalnum() or c in '-_.'))
            self.send_header('Content-Disposition', f'attachment; filename="{safe or "artifact"}"')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self._local_request():
            return
        path = urlsplit(self.path).path
        service = self.server.service
        try:
            if path == '/api/config':
                self._reply(200, {**service.configuration(), 'csrfToken': self.server.csrf_token})
            elif path == '/api/runs/history':
                self._reply(200, {'runs': service.run_history()})
            elif path == '/api/benchmark/historical':
                self._reply(200, service.benchmark())
            elif path.startswith('/api/runs/'):
                parts = path.split('/')
                if len(parts) == 5:
                    run_id, kind = parts[3:]
                    routes = {'status': service.status, 'discussions': service.discussion_list,
                              'events': service.events, 'files': service.file_list}
                    if kind not in routes:
                        raise DemoError('Endpoint not found.')
                    self._reply(200, routes[kind](run_id))
                elif len(parts) == 7 and parts[4] == 'files' and parts[6] == 'download':
                    artifact = service.file_path(parts[3], parts[5])
                    mime = mimetypes.guess_type(artifact.name)[0] or 'text/plain'
                    self._reply(200, artifact.read_bytes(), mime + '; charset=utf-8', filename=artifact.name)
                else:
                    raise DemoError('Endpoint not found.')
            elif path.startswith('/api/'):
                raise DemoError('Endpoint not found.')
            else:
                candidate = self.server.frontend / ('index.html' if path == '/' else path.lstrip('/'))
                candidate = candidate.resolve()
                if (not candidate.is_relative_to(self.server.frontend) or not candidate.is_file() or
                        candidate.suffix not in ('.html', '.js', '.css', '.svg', '.png', '.ico', '.woff', '.woff2')):
                    raise DemoError('Page not found.')
                mime = mimetypes.guess_type(candidate.name)[0] or 'application/octet-stream'
                self._reply(200, candidate.read_bytes(), mime + '; charset=utf-8')
        except DemoError as exc:
            self._reply(404, {'error': str(exc)})
        except (ValueError, OSError, KeyError, TypeError):
            self._reply(500, {'error': 'Presentation data is unavailable. No run outcome is inferred.'})

    def do_POST(self):
        if not self._local_request():
            return
        if not hmac.compare_digest(self.headers.get('X-Demo-Token', ''), self.server.csrf_token):
            self._reply(403, {'error': 'Reload this page to authorize the local presentation session.'})
            return
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            self._reply(415, {'error': 'JSON is required.'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 65536:
                self._reply(413, {'error': 'Request is too large or empty.'})
                return
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise DemoError('A JSON object is required.')
            path = urlsplit(self.path).path
            if path == '/api/runs/prepare':
                self._reply(200, self.server.service.prepare_console(payload))
            elif path == '/api/runs/start':
                self._reply(200, self.server.service.start_console(payload))
            else:
                raise DemoError('Endpoint not found.')
        except InputError as exc:
            self._reply(400, {'error': exc.detail, 'kind': exc.kind, 'field': exc.field})
        except DemoError as exc:
            self._reply(400, {'error': str(exc)})
        except (ValueError, TypeError):
            self._reply(400, {'error': 'Invalid JSON or configuration.'})
        except Exception:
            self._reply(500, {'error': 'Could not prepare or start the run. No successful outcome is claimed.'})


def main(argv=None):
    parser = argparse.ArgumentParser(description='Real-model presentation console, local deployment.')
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--frontend-dir', type=Path, default=ROOT / 'src/frontend/build')
    parser.add_argument('--state-dir', type=Path, default=ROOT / '.local-review/presentation-console')
    parser.add_argument('--open', action='store_true')
    parser.add_argument('--compact-evidence-handoff', action='store_true',
                        help='Use the opt-in compact intermediate evidence format')
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error('Choose a port between 0 and 65535.')
    try:
        service = ConsoleService(args.state_dir)
        if args.compact_evidence_handoff:
            service.defaults['compact_evidence_handoff'] = True
        server = ConsoleServer(('127.0.0.1', args.port), service, args.frontend_dir)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Research Presentation Console: {url}', flush=True)
    print('Real model execution only. API calls start only after explicit confirmation.', flush=True)
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
