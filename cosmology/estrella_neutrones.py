#!/usr/bin/env python3
"""Open the local neutron star simulation without external dependencies."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from urllib.parse import urlsplit
import webbrowser


def valid_port(text):
    """Port 0 lets the system choose an available port."""
    try:
        port = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("the port must be an integer")
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("the port must be between 0 and 65535")
    return port


def make_handler(html_path):
    """Serve only the simulation; never publish other files in the folder."""

    class SimulationHandler(BaseHTTPRequestHandler):
        def send_simulation(self, include_body):
            try:
                route = urlsplit(self.path).path
            except ValueError:
                self.send_error(400, "Invalid request")
                return
            if route not in ("/", "/estrella_neutrones.html"):
                self.send_error(404, "File not available")
                return
            try:
                content = html_path.read_bytes()
            except OSError:
                self.send_error(500, "Could not read the simulation")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if include_body:
                self.wfile.write(content)

        def do_GET(self):
            self.send_simulation(True)

        def do_HEAD(self):
            self.send_simulation(False)

        def log_message(self, format, *args):
            # Keep the terminal clean while presenting the simulation.
            pass

    return SimulationHandler


def main():
    parser = argparse.ArgumentParser(
        description="Start the visual neutron star simulation in your browser."
    )
    parser.add_argument(
        "--no-browser", action="store_true",
        help="start the server without opening the browser",
    )
    parser.add_argument(
        "--port", type=valid_port, default=0, metavar="PORT",
        help="local port; 0 chooses an available port (default)",
    )
    args = parser.parse_args()
    html_path = Path(__file__).resolve().with_name("estrella_neutrones.html")
    try:
        with html_path.open("rb"):
            pass
    except OSError as error:
        print("Could not read the simulation: {}".format(html_path), file=sys.stderr)
        print(str(error), file=sys.stderr)
        return 1

    try:
        server = ThreadingHTTPServer(
            ("127.0.0.1", args.port), make_handler(html_path)
        )
    except OSError as error:
        print("Could not start the local server: {}".format(error), file=sys.stderr)
        return 1

    server.daemon_threads = True
    url = "http://127.0.0.1:{}/".format(server.server_port)
    print("Simulation available at: {}".format(url), flush=True)
    print("Keep this terminal open. Press Ctrl+C to stop.", flush=True)
    try:
        if not args.no_browser:
            try:
                opened = webbrowser.open(url)
            except webbrowser.Error:
                opened = False
            if not opened:
                print("Open the link above in your browser.", flush=True)
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\nSimulation stopped.", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
