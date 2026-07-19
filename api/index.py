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


def create_fallback_svg(theme='dark', message="Yo! Rendering issues you know, please keep refreshing to see the full picture!"):
    bg_color = "#161b22" if theme == 'dark' else "#ffffff"
    text_color = "#ffa657" if theme == 'dark' else "#d97706"
    sub_color = "#a5d6ff" if theme == 'dark' else "#0969da"
    border_color = "#30363d" if theme == 'dark' else "#d0d7de"

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1080px" height="180px" viewBox="0 0 1080 180">
  <rect width="1080" height="180" fill="{bg_color}" rx="15" stroke="{border_color}" stroke-width="2"/>
  <text x="540" y="80" fill="{text_color}" font-family="Consolas, monospace" font-size="20px" font-weight="bold" text-anchor="middle">
    ⚠️ {message}
  </text>
  <text x="540" y="120" fill="{sub_color}" font-family="Consolas, monospace" font-size="14px" text-anchor="middle">
    [ Status: Dynamic rendering temporarily unavailable • Click refresh or try again in a few seconds ]
  </text>
</svg>'''


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)

        theme = params.get('theme', ['dark'])[0].lower()
        if theme not in ['dark', 'light']:
            theme = 'dark'

        user_name = params.get('user', [None])[0]

        if generate_svg_string is None:
            svg_content = create_fallback_svg(theme=theme)
        else:
            try:
                svg_content = generate_svg_string(theme=theme, user_name=user_name)
            except Exception:
                # Fallback to pre-generated static SVG or custom fallback card
                svg_file = os.path.join(base_dir, f"{theme}_mode.svg")
                if os.path.exists(svg_file):
                    try:
                        with open(svg_file, 'r', encoding='utf-8') as f:
                            svg_content = f.read()
                    except Exception:
                        svg_content = create_fallback_svg(theme=theme)
                else:
                    svg_content = create_fallback_svg(theme=theme)

        self.send_response(200)
        self.send_header('Content-Type', 'image/svg+xml; charset=utf-8')
        # Instruct GitHub Camo proxy and browsers never to cache the SVG image
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0, s-maxage=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(svg_content.encode('utf-8'))
