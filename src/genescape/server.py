import sys, os, functools, webbrowser, threading
from random import random
import tempfile
from genescape import tree, annot, utils
from genescape.bottle import Bottle, static_file, template, view
from genescape.bottle import TEMPLATE_PATH
from genescape import bottle
from genescape.bottle import get, post, request, response, redirect

# WEB related resources
WEB_RES = [
    ("genescape.data.web", "index.html"),
    ("genescape.data.web", "draw.html"),
    ("genescape.data.web.static", "genescape.css"),
    ("genescape.data.web.static", "genescape.js"),
    ("genescape.data.web.static", "genescape.js"),
    ("genescape.data.web.static", "htmx.min.js.gz"),
    ("genescape.data.web.static", "viz-standalone.js"),
    ("genescape.data.web.static", "mini-default.css"),
]

# Initialize web related resources.
for pack, res in WEB_RES:
    path = utils.init_resource(package=pack, resource=res, path="web", overwrite=True)

# Debug mode.
DEBUG = True

# The webserver directory.
WEB_DIR = utils.init_resource(path="web")

# Add the template directory to the template path.
TEMPLATE_PATH.insert(0, WEB_DIR)

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


def graph2text(graph):
    nodes = filter(lambda x: graph.nodes[x].get(utils.INPUT), graph.nodes)
    pairs = map(lambda x: (x, graph.nodes[x].get(utils.NAME, '')), nodes)
    lines = map(lambda x: f"{x[0]}, {x[1]}", pairs)
    text = "\n".join(lines)
    return text

def webapp(reloader=False, debug=False):

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

    @app.route(path='/check/', method='POST')
    @view('htmx/check.html')
    @debugger
    def check():
        # Read the parameters from the request.
        terms = textarea(request)

        # Generate the output.
        graph = tree.run(terms=terms, index=tree.utils.INDEX, out=None)

        # Convert the graph to a list of terms.
        text = graph2text(graph)

        # Fill in the parameters for the template.
        param = dict(text=text)

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

        time.sleep(1)

        msg = "OK"
        return msg

    @app.route('/static/<name:path>')
    def static(name):
        print(f"serve static: {name}")
        return static_file(name, root=WEB_DIR)

    @app.route('/draw/', method='POST')
    @view('draw.html')
    @debugger
    def draw():
        # Read the parameters from the request.
        inp = textarea(request)
        patt = get_param(request, name='pattern')

        print(f"terms: {inp}")

        # Generate the output.
        graph, ann = tree.parse_input(inp=inp, index=tree.utils.INDEX, pattern=patt)

        # The dot string
        dot = tree.write_tree(graph, ann, out=None)

        # Convert the graph to a list of terms.
        text = graph2text(graph)

        param = dict(dot=dot, input=text)

        return param

    # Setting the debug mode.
    if debug:
        bottle.debug(True)

    try:
        print ("Server running on http://localhost:8080")
        app.run(host='localhost', port=8000, reloader=reloader)
    except Exception as e:
        print(f"Server Error: {e}", sys.stderr)

def open_browser(host="127.0.0.1", port=8000, proto="http"):
    url = f"{proto}://{host}:{port}/"
    threading.Timer(interval=1, function=lambda: webbrowser.open_new(url)).start()


def start_server():
    threading.Thread(target=open_browser).start()
    webapp(reloader=True, debug=True)

if __name__ == "__main__":
    start_server()
