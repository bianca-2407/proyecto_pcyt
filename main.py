"""Small static server to preview the site locally.

Run: python main.py

It will serve files from the current directory at http://localhost:8000
"""

import http.server
import socketserver
import os
import argparse


def run(host: str = "127.0.0.1", port: int = 8000):
	os.chdir(os.path.dirname(__file__) or '.')
	handler = http.server.SimpleHTTPRequestHandler
	with socketserver.TCPServer((host, port), handler) as httpd:
		print(f"Serving at http://{host}:{port} (CTRL+C to stop)")
		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			print("Shutting down")
			httpd.server_close()


def main():
	parser = argparse.ArgumentParser(description="Serve the static site locally")
	parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
	parser.add_argument("--port", default=8000, type=int, help="Port to listen on")
	args = parser.parse_args()
	run(host=args.host, port=args.port)


if __name__ == "__main__":
	main()
