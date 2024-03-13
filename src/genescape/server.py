import sys, os
from random import random
import tempfile
from genescape import tree, annot, utils
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

# Temporary directory
TMP_PATH = os.path.join(STATIC_DIR, "tmp")

# Make the temporary directory if it does not exist.
if not os.path.isdir(TMP_PATH):
    os.makedirs(TMP_PATH)

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

def textarea(request, name='input'):
    text = request.forms.get(name, '')

    # print(f"input: {text}")

    terms = map(lambda x: x.strip(), text.splitlines())
    terms = list(terms)
    terms = utils.parse_terms(terms)

    # print (terms)

    return terms

def temp_name(prefix="image-", suffix=".png"):
    fname = tempfile.NamedTemporaryFile(dir=TMP_PATH, prefix=prefix, suffix=suffix, delete=False).name
    sname = f"/static/tmp/{os.path.basename(fname)}"
    return (fname, sname)

def graph2text(graph):
    nodes = filter(lambda x: graph.nodes[x].get(utils.INPUT), graph.nodes)
    pairs = map(lambda x: (x, graph.nodes[x].get(utils.NAME, '')), nodes)
    lines = map(lambda x: f"{x[0]}, {x[1]}", pairs)
    text = "\n".join(lines)
    return text

def runner(reloader=False, debug=False):

    @app.route(path='/image/', method='POST')
    @view('htmx/image.html')
    def image():
        # Read the parameters from the request.
        terms = textarea(request)

        # Generate temporary names
        fname, sname = temp_name()

        # Generate the output.
        graph = tree.run(terms=terms, index=tree.utils.INDEX, out=fname)

        # Convert the graph to a list of terms.
        text = graph2text(graph)

        # Fill in the parameters for the template.
        param = dict(src=sname, input=text, rand=random())

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
        return static_file(name, root=STATIC_DIR)

    @app.route('/')
    @view('index.html')
    def home():
        param = dict(title="GeneScape", rand=random())
        return param

    @app.route('/dot/', method='POST')
    @view('htmx/dot.html')
    def dot():
        # Read the parameters from the request.
        terms = textarea(request)

        print(f"terms: {terms}")

        # Generate temporary names
        fname, sname = temp_name(suffix=".dot")

        # Generate the output.
        graph = tree.run(terms=terms, index=tree.utils.INDEX, out=fname)

        # Convert the graph to a list of terms.
        text = graph2text(graph)

        # Read the dot file.
        with open(fname) as fp:
            dot = fp.read()

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

if __name__ == "__main__":
    runner(reloader=True, debug=True)
