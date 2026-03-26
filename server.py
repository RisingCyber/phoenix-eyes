"""
PHOENIX EYES v2 - Self-contained server
Run from anywhere: python3 server.py
"""
import json, time, threading, sys, os
import urllib.request, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ── Resolve paths relative to THIS script, not cwd ──────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'templates', 'index.html')

# ── In-memory cache ──────────────────────────────────────────────
_cache = {}
_lock  = threading.Lock()

def fetch(url, ttl=30, headers=None):
    now = time.time()
    with _lock:
        if url in _cache:
            data, ts = _cache[url]
            if now - ts < ttl:
                return data
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 PhoenixEyes/2.0')
    req.add_header('Accept', 'application/json, image/*, */*')
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            data = r.read()
        with _lock:
            _cache[url] = (data, now)
        return data
    except Exception as e:
        print(f'  [fetch error] {url}  →  {e}')
        return None


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f'  [{self.address_string()}] {fmt % args}')

    def cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

    def do_OPTIONS(self):
        self.send_response(200); self.cors(); self.end_headers()

    def do_GET(self):
        p = urlparse(self.path)
        path, qs = p.path, parse_qs(p.query)

        if   path in ('/', '/index.html'):    self.serve_html()
        elif path == '/api/flights':          self.api_flights()
        elif path == '/api/cameras':          self.api_cameras()
        elif path == '/api/camera-image':     self.api_cam_image(qs)
        elif path == '/api/earthquakes':      self.api_quakes()
        elif path == '/api/health':           self.json({'status':'ok','ts':int(time.time())})
        else:
            self.send_response(404)
            self.send_header('Content-Type','text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')

    # ── Serve the main HTML ──────────────────────────────────────
    def serve_html(self):
        try:
            with open(HTML_FILE, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'ERROR: Cannot find {HTML_FILE}'.encode())

    # ── Flights: adsb.fi global → OpenSky fallback ───────────────
    def api_flights(self):
        data = fetch('https://api.adsb.fi/v1/aircraft', ttl=12)
        if not data:
            raw = fetch('https://opensky-network.org/api/states/all', ttl=15)
            if raw:
                try:
                    parsed = json.loads(raw)
                    ac = [
                        {'hex':s[0],'flight':(s[1] or '').strip(),
                         'lat':s[6],'lon':s[5],
                         'alt_baro':round((s[7] or 0)*3.281),
                         'track':s[10] or 0,'gs':round((s[9] or 0)*1.944)}
                        for s in (parsed.get('states') or []) if s[6] and s[5]
                    ]
                    data = json.dumps({'aircraft':ac,'source':'opensky'}).encode()
                except:
                    data = b'{"aircraft":[]}'
        self.send_response(200)
        self.cors()
        self.send_header('Content-Type','application/json')
        self.send_header('Cache-Control','max-age=10')
        self.end_headers()
        self.wfile.write(data or b'{"aircraft":[]}')

    # ── NYC DOT cameras ──────────────────────────────────────────
    def api_cameras(self):
        data = fetch('https://webcams.nyctmc.org/api/cameras', ttl=300)
        self.send_response(200)
        self.cors()
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(data or b'[]')

    def api_cam_image(self, qs):
        cam_id = qs.get('id',[''])[0]
        if not cam_id or not all(c in '0123456789abcdefABCDEF-' for c in cam_id):
            self.send_response(400); self.end_headers(); return
        data = fetch(f'https://webcams.nyctmc.org/api/cameras/{cam_id}/image',
                     ttl=4, headers={'Accept':'image/jpeg,image/*'})
        if not data:
            self.send_response(502); self.end_headers(); return
        self.send_response(200)
        self.cors()
        self.send_header('Content-Type','image/jpeg')
        self.send_header('Cache-Control','max-age=3')
        self.end_headers()
        self.wfile.write(data)

    # ── USGS earthquakes ─────────────────────────────────────────
    def api_quakes(self):
        data = fetch('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson', ttl=120)
        self.send_response(200)
        self.cors()
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(data or b'{"type":"FeatureCollection","features":[]}')

    def json(self, obj):
        data = json.dumps(obj).encode()
        self.send_response(200); self.cors()
        self.send_header('Content-Type','application/json')
        self.end_headers(); self.wfile.write(data)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

    # Verify HTML exists before starting
    if not os.path.exists(HTML_FILE):
        print(f'\n  ERROR: Cannot find {HTML_FILE}')
        print(  '  Make sure server.py is inside the phoenix-eyes-v2/ folder.')
        sys.exit(1)

    print(f'''
  ██████╗ ██╗  ██╗ ██████╗ ███████╗███╗   ██╗██╗██╗  ██╗    ███████╗██╗   ██╗███████╗███████╗
  ██╔══██╗██║  ██║██╔═══██╗██╔════╝████╗  ██║██║╚██╗██╔╝    ██╔════╝╚██╗ ██╔╝██╔════╝██╔════╝
  ██████╔╝███████║██║   ██║█████╗  ██╔██╗ ██║██║ ╚███╔╝     █████╗   ╚████╔╝ █████╗  ███████╗
  ██╔═══╝ ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║██║ ██╔██╗     ██╔══╝    ╚██╔╝  ██╔══╝  ╚════██║
  ██║     ██║  ██║╚██████╔╝███████╗██║ ╚████║██║██╔╝ ██╗    ███████╗   ██║   ███████╗███████║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝    ╚══════╝   ╚═╝   ╚══════╝╚══════╝

  PHOENIX EYES v2  —  Multi-Layer Global Intelligence Platform
  ─────────────────────────────────────────────────────────────
  Serving:   http://localhost:{port}
  HTML:      {HTML_FILE}
  ─────────────────────────────────────────────────────────────
  Layers:    ✈ ADS-B  ⚓ AIS  ⚡ GPSJam  📡 RFI  🌍 USGS  📹 NYC Cams  🌬 Windy
  Press Ctrl+C to stop.
''')

    try:
        server = HTTPServer(('0.0.0.0', port), Handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Shutting down. Goodbye.')
        server.shutdown()
