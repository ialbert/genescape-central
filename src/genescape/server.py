import functools
import os
import pprint
import sys
import threading
import time
import webbrowser
from random import random

import toml

from genescape import __version__, annot, bottle, resources, tree, utils
from genescape.bottle import TEMPLATE_PATH, Bottle, get, post, redirect, request, response, static_file, template, view

DEVMODE = True

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
        TEMPLATE_PATH.insert(0, res.WEB_DIR)

    return res


app = Bottle()


def debugger(func):
    """
    Decorator that prints the execution time of the function it decorates.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if DEVMODE:

            # print(f"# method: {request.method}")

            # for header, value in request.headers.items():
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


def safe_int(value, default=1):
    try:
        return int(value)
    except ValueError as exc:
        return default


def webapp(res, config, devmode=False, host="localhost", port=8000):

    @app.route('/')
    @view('index.html')
    @debugger
    def index():
        dbs = get_dbs(res.config)
        param = dict(title="GeneScape", version=__version__, rand=random(), dbs=dbs)
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
        root = get_param(request, name='root')
        count = get_param(request, name='count')
        count = safe_int(count, default=1)
        db = get_param(request, name='db')

        #resources.clear_cache()

        # Choose a different index
        index = res.get_index(db)

        utils.info(f"code={db}, file={index!s}")

        # Generate the output.
        graph, ann = tree.parse_input(inp=inp, index=index, pattern=patt, root=root, mincount=count)

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
        print(f"#\n# GeneScape version: {__version__}")
        app.run(host=host, port=port, reloader=devmode)
    except Exception as e:
        print(f"Server Error: {e}", sys.stderr)


def get_dbs(config):
    dbs = []
    for value in config.get("index", []):
        code = value.get("code", "?")
        name = value.get("name", "?")
        selected = value.get("selected", '')
        dbs.append((code, name, selected))
    return dbs


def start(devmode=False, reset=False, index=None, host="localhost", port=8000, proto="http", config=None):
    global TEMPLATE_PATH, DEVMODE

    # Update the global debug flag.
    DEVMODE = devmode

    # Get the configuration file
    cnf = resources.get_config()

    # Resets the resources.
    if reset:
        resources.reset_dir(cnf)

    # Initialize the resources.
    res = resources.init(config=cnf, devmode=devmode)

    # Insert template path.
    TEMPLATE_PATH.insert(0, res.WEB_DIR)

    # The URL of the server.
    url = f"{proto}://{host}:{port}/"

    # Start the server.
    utils.info(f"server url: {url}")
    utils.info(f"server dir: {res.WEB_DIR}")

    webapp(res=res, devmode=devmode, host=host, port=port, config=config)


if __name__ == "__main__":
    start()
