import sys, os

from genescape.bottle import Bottle, static_file, template, view
from genescape.bottle import TEMPLATE_PATH
from genescape import bottle

# The current directory.
CURR_DIR = os.path.dirname(os.path.realpath(__file__))


# Web related content.
WEB_DIR = os.path.join(CURR_DIR, "web")

# Static content directory.
STATIC_DIR = os.path.join(WEB_DIR, "static")

# The name of the demo image.
DEMO_IMG = os.path.join(STATIC_DIR, "img", "demo.png")
DEMO_PATH = os.path.dirname(DEMO_IMG)

# The directory containing the templates.
TEMPLATE_DIR = WEB_DIR

# Add the template directory to the template path.
TEMPLATE_PATH.insert(0, TEMPLATE_DIR)

# The user's home directory.
HOME_DIR = os.path.expanduser("~")

# Default genescape directory
GENESCAPE_DIR = os.path.join(HOME_DIR, "genescape")

import time

def run(reloader=False, debug=False):

    app = Bottle()

    @app.route('/image/')
    @view('htmx/image.html')
    def image():
        print ("generating image")
        param = dict()
        time.sleep(1)
        return param

    @app.route('/test/')
    @view('htmx/test.html')
    def test():
        print ("test content")
        param = dict(msg="Hello World")
        time.sleep(1)
        return param

    @app.route('/static/<name:path>')
    def send_static(name):
        print(f"serve static: {name}")
        return static_file(name, root=STATIC_DIR)

    @app.route('/')
    @view('index.html')
    def home():
        param = dict(title="GeneScape")
        return param

    # Setting the debug mode.
    if debug:
        bottle.debug(True)

    try:
        print ("Server running on http://localhost:8080")
        app.run(host='localhost', port=8000, reloader=reloader)
    except Exception as e:
        print(f"Server Error: {e}", sys.stderr)

if __name__ == "__main__":
    run(reloader=True, debug=True)
