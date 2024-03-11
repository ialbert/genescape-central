import sys, os

from genescape.bottle import Bottle, static_file, template, view
from genescape.bottle import TEMPLATE_PATH
from genescape import bottle
from genescape.bottle import get, post, request, response, redirect

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

app = Bottle()

def runner(reloader=False, debug=False):

    @app.route(path='/image/', method='POST')
    @view('htmx/image.html')
    def image():
        print ("generating image")
        text = request.forms.get('input')
        print (request.forms.keys())
        print (f"input: {text}")
        for key, value in request.forms.items():
            print (f"{key}: {value}")

        param = dict()
        time.sleep(1)
        return param

    @app.route(path='/test/', method='GET')
    @view('htmx/test.html')
    def test():
        print ("Incoming request ...")
        print(request.forms.keys())
        param = dict(msg="Hello World")
        return param

    @app.route('/show/', method='POST')
    def show():

        textarea_content = request.forms.get('myTextarea')

        # Process the content as needed
        print(textarea_content)

        print ("Query check...")
        for key in request.query.keys():
            print(f"{key}: {request.query.getall(key)}")

        print ("Form check...")
        for key in request.forms.keys():
            print(f"{key}: {request.forms.getall(key)}")



        msg = "OK"
        return msg

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
    runner(reloader=True, debug=True)
