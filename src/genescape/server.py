import sys, os

from genescape.bottle import Bottle, static_file, template, view
from genescape.bottle import TEMPLATE_PATH
from genescape import bottle

# The current directory.
CURR_DIR = os.path.dirname(os.path.realpath(__file__))

DEMO_PATH = os.path.join(CURR_DIR, "data")
DEMO_IMG = os.path.join(CURR_DIR, "data", "demo.png")

WEB_DIR = os.path.join(CURR_DIR, "web")
STATIC_DIR = os.path.join(WEB_DIR, "static")

# The directory containing the templates.
TEMPLATE_DIR = WEB_DIR

# Add the template directory to the template path.
TEMPLATE_PATH.insert(0, TEMPLATE_DIR)

# The user's home directory.
HOME_DIR = os.path.expanduser("~")

# Default genescape directory
GENESCAPE_DIR = os.path.join(HOME_DIR, "genescape")



def run(reloader=False):

    print ("Making the server")

    app = Bottle()

    @app.route('/img/result.png')
    def img():
        print ("serve image", DEMO_IMG)
        return static_file("demo.png", root=DEMO_PATH)

    @app.route('/static/<name:path>')
    def send_static(name):
        print(f"serve static: {name}")
        return static_file(name, root=STATIC_DIR)

    @app.route('/')
    @view('index.html')
    def home():
        param = dict(title="GeneScape")
        return param

    # You need to restart the server on each request to check the global variable
    # This is a workaround and might not be the most efficient way to handle this.
    bottle.debug(True)
    try:
        print ("Server running on http://localhost:8080")
        app.run(host='localhost', port=8000, reloader=reloader)
    except Exception as e:
        print(f"Server Error: {e}", sys.stderr)

if __name__ == "__main__":
    run(reloader=True)
