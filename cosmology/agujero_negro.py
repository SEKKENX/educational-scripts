#!/usr/bin/env python3
"""Open the local black hole simulation without external dependencies."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from urllib.parse import urlsplit
import webbrowser


def puerto_valido(texto):
    """Port 0 lets the system choose an available port."""
    try:
        puerto = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError("the port must be an integer")
    if not 0 <= puerto <= 65535:
        raise argparse.ArgumentTypeError("the port must be between 0 and 65535")
    return puerto


def crear_handler(archivo):
    """Serve only the simulation; never publish other files in the folder."""

    class SimulacionHandler(BaseHTTPRequestHandler):
        def enviar_simulacion(self, incluir_cuerpo):
            try:
                ruta = urlsplit(self.path).path
            except ValueError:
                self.send_error(400, "Invalid request")
                return
            if ruta not in ("/", "/agujero_negro.html"):
                self.send_error(404, "File not available")
                return
            try:
                contenido = archivo.read_bytes()
            except OSError:
                self.send_error(500, "Could not read the simulation")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(contenido)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if incluir_cuerpo:
                self.wfile.write(contenido)

        def do_GET(self):
            self.enviar_simulacion(True)

        def do_HEAD(self):
            self.enviar_simulacion(False)

        def log_message(self, formato, *argumentos):
            # Keep the terminal clean while presenting the simulation.
            pass

    return SimulacionHandler


def main():
    parser = argparse.ArgumentParser(
        description="Start the visual black hole simulation in your browser."
    )
    parser.add_argument(
        "--no-browser", action="store_true",
        help="start the server without opening the browser",
    )
    parser.add_argument(
        "--port", type=puerto_valido, default=0, metavar="PORT",
        help="local port; 0 chooses an available port (default)",
    )
    argumentos = parser.parse_args()
    archivo = Path(__file__).resolve().with_name("agujero_negro.html")
    try:
        with archivo.open("rb"):
            pass
    except OSError as error:
        print("Could not read the simulation: {}".format(archivo), file=sys.stderr)
        print(str(error), file=sys.stderr)
        return 1

    try:
        servidor = ThreadingHTTPServer(
            ("127.0.0.1", argumentos.port), crear_handler(archivo)
        )
    except OSError as error:
        print("Could not start the local server: {}".format(error), file=sys.stderr)
        return 1

    servidor.daemon_threads = True
    url = "http://127.0.0.1:{}/".format(servidor.server_port)
    print("Simulation available at: {}".format(url), flush=True)
    print("Keep this terminal open. Press Ctrl+C to stop.", flush=True)
    try:
        if not argumentos.no_browser:
            try:
                abierto = webbrowser.open(url)
            except webbrowser.Error:
                abierto = False
            if not abierto:
                print("Open the link above in your browser.", flush=True)
        servidor.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\nSimulation stopped.", flush=True)
    finally:
        servidor.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
