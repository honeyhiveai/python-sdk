#!/usr/bin/env python3
"""
Simple HTTP server to serve the built Sphinx documentation locally.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path


def main():
    """Serve the built documentation on localhost."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    build_dir = script_dir / "_build" / "html"

    if not build_dir.exists():
        print(f"Error: Documentation build directory not found at {build_dir}")
        print("Please run 'tox -e docs' first to build the documentation.")
        sys.exit(1)

    # Change to the build directory
    os.chdir(build_dir)

    # Set up the server
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Documentation server started at http://localhost:{PORT}")
        print(f"Serving documentation from: {build_dir.absolute()}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
