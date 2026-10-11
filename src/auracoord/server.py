"""AuraCoord Microservice Server.
Provides REST API endpoints for coordinate conversion and spatial search.
Runs standalone using Python standard library http.server.
"""

import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from auracoord.converter import parse_any_coordinate, format_result


class AuraCoordHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/health":
            self._send_json(200, {
                "status": "Healthy",
                "service": "AuraCoord",
                "version": "1.0.0",
                "standards": ["WGS84", "MGRS", "UTM", "DMS"]
            })
            return

        if parsed.path == "/api/coord/convert":
            lat_str = params.get("lat", [None])[0]
            lon_str = params.get("lon", [None])[0]
            if lat_str is None or lon_str is None:
                self._send_json(400, {"error": "Query parameters 'lat' and 'lon' are required."})
                return
            try:
                lat = float(lat_str)
                lon = float(lon_str)
                res = format_result(lat, lon, "DecimalDegrees")
                self._send_json(200, res)
            except ValueError:
                self._send_json(400, {"error": "Invalid numerical latitude or longitude."})
            return

        if parsed.path == "/api/coord/search":
            q = params.get("q", [None])[0]
            if not q:
                self._send_json(400, {"error": "Query parameter 'q' is required."})
                return
            res = parse_any_coordinate(q)
            if res:
                self._send_json(200, res)
            else:
                self._send_json(404, {"error": f"Unable to parse coordinate: '{q}'"})
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/coord/parse":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
                text = data.get("text", "")
                res = parse_any_coordinate(text)
                if res:
                    self._send_json(200, res)
                else:
                    self._send_json(400, {"error": f"Unrecognized coordinate format: '{text}'"})
            except Exception as ex:
                self._send_json(400, {"error": f"Invalid JSON payload: {str(ex)}"})
            return

        self._send_json(404, {"error": "Endpoint not found"})


def run_server(port: int = 7087, host: str = "0.0.0.0"):
    server_address = (host, port)
    httpd = HTTPServer(server_address, AuraCoordHandler)
    print(f"[AuraCoord] Microservice listening on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
