import sys, os, functools, webbrowser, threading
from random import random
import tempfile
from genescape import tree, annot, utils, resources
from genescape.bottle import Bottle, static_file, template, view
from genescape.bottle import TEMPLATE_PATH
from genescape import bottle
from genescape.bottle import get, post, request, response, redirect

DEBUG = True

CURR_DIR = os.path.dirname(os.path.realpath(__file__))

def init_server(devmode=False):

    res = resources.init(devmode=devmode)

    if devmode:
        utils.info("running in development mode.")
        res.WEB_DIR = str(os.path.join(CURR_DIR, "data", "web"))
        TEMPLATE_PATH.insert(0, res.WEB_DIR)
        utils.info(f"web dir: {res.WEB_DIR}")
        utils.info(f"template path: {TEMPLATE_PATH}")
    else:
        res.WEB_DIR = str(res.HOME.parent)
        TEMPLATE_PATH.insert(0, res.WEB_DIR)

    return res


import time

app = Bottle()

def debugger(func):
    """
    Decorator that prints the execution time of the function it decorates.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if DEBUG:

            #print(f"# method: {request.method}")

            #for header, value in request.headers.items():
            #    print(f"# header: {header}: {value}")

            for key in request.query.keys():
                print(f"# query.key {key}: {request.query.getall(key)}")

            for key in request.forms.keys():
                print(f"# form.key {key}: {request.forms.getall(key)}")

        result = func(*args, **kwargs)
        return result
    return wrapper

def textarea(request, name='input'):
    text = request.forms.get(name, '')
    terms = map(lambda x: x.strip(), text.splitlines())
    terms = filter(None, terms)
    terms = list(terms)
    return terms

def get_param(request, name='param'):
    value = request.forms.get(name, '')
    value = value.strip()
    return value


def webapp(res, devmode=False, host="localhost", port=8000):

    @app.route('/')
    @view('index.html')
    @debugger
    def index():
        param = dict(title="GeneScape", rand=random())
        return param

    @app.route('/upload/', method='POST')
    @debugger
    def upload():
        stream = request.files.get('file')
        content = stream.file.read().decode('utf-8', errors="ingore")
        return content

    @app.route('/static/<name:path>')
    def static(name):
        utils.debug(f"loading {name}")
        return static_file(name, root=f"{res.WEB_DIR}/static/")

    @app.route('/draw/', method='POST')
    @view('draw.html')
    @debugger
    def draw():
        # Read the parameters from the request.
        inp = textarea(request)
        patt = get_param(request, name='pattern')

        print(f"terms: {inp}")

        # Generate the output.
        graph, ann = tree.parse_input(inp=inp, index=res.INDEX, pattern=patt)

        # The dot string
        dot = tree.write_tree(graph, ann, out=None)

        # Convert the graph to a list of terms.
        text = annot.ann2csv(ann)

        # The parameters for the template.
        param = dict(dot=dot, input=text)

        return param

    # Setting the debug mode.
    if devmode:
        bottle.debug(True)

    try:
        app.run(host=host, port=port, reloader=devmode)
    except Exception as e:
        print(f"Server Error: {e}", sys.stderr)

def start(devmode=False, reset=False, index=None, popwin=True, host="127.0.0.1", port=8000, proto="http"):

    # Resets the resources.
    if reset:
        resources.reset_dir()

    # Initialize the server.
    res = init_server(devmode=devmode)

    # Override the default INDEX file.
    res.INDEX = resources.get_index(index=index, res=res)

    # The URL of the server.
    url = f"{proto}://{host}:{port}/"

    def open_browser():
        threading.Timer(interval=1, function=lambda: webbrowser.open_new(url)).start()

    # Open the browser.
    if popwin:
        threading.Thread(target=open_browser).start()

    # Start the server.
    utils.info(f"server url: {url}")
    utils.info(f"server dir: {res.WEB_DIR}")
    webapp(res=res, devmode=devmode, host=host, port=port)

if __name__ == "__main__":
    start()
