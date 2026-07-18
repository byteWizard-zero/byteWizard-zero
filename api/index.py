from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import os
import sys

# Ensure project root directory is in sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from today import generate_svg_string
except Exception as e:
    generate_svg_string = None
    import_error = str(e)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if generate_svg_string is None:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Server initialization error: {import_error}".encode('utf-8'))
            return

        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)

        theme = params.get('theme', ['dark'])[0].lower()
        if theme not in ['dark', 'light']:
            theme = 'dark'

        user_name = params.get('user', [None])[0]

        try:
            svg_content = generate_svg_string(theme=theme, user_name=user_name)
        except Exception as e:
            # Fallback to pre-generated static SVG if API rate limit or error occurs
            svg_file = os.path.join(base_dir, f"{theme}_mode.svg")
            if os.path.exists(svg_file):
                with open(svg_file, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error generating SVG: {str(e)}".encode('utf-8'))
                return

        self.send_response(200)
        self.send_header('Content-Type', 'image/svg+xml; charset=utf-8')
        # Cache-Control: max-age=0, s-maxage=60, stale-while-revalidate=300 for GitHub proxy compatibility
        self.send_header('Cache-Control', 'max-age=0, s-maxage=60, stale-while-revalidate=300')
        self.end_headers()
        self.wfile.write(svg_content.encode('utf-8'))
