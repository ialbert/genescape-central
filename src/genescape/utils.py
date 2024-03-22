import logging, functools, time
import os, gzip, json, csv
import sys, pathlib
from logging import DEBUG, ERROR, INFO, WARNING
from itertools import tee
import io, shutil

from importlib import resources
from pathlib import Path

# Get the logger.
logger = logging.getLogger(__name__)

# Set the default loglevel.
logger.setLevel(INFO)

# Rename the log levels.
logging.addLevelName(logging.WARNING, "WARN")

# Data format version.
TAG= 'v1'

# Loggin format
LOG_FORMAT = "# %(levelname)s\t%(module)s.%(funcName)s\t%(message)s"

# A callable to initialize the logger
def init_logger(logger):
    formatter = logging.Formatter(LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Initialize the logger
init_logger(logger)

# A wrapper with additional callback
def wrapper(logfunc, callback=None):
    def func(msg):
        logfunc(msg)
        if callback:
            callback(msg)

    return func


debug = wrapper(logger.debug)
info = wrapper(logger.info)
warn = wrapper(logger.warning)
error = wrapper(logger.error)

# Stops the process with an error.
def stop(msg):
    logger.error(msg)
    sys.exit(1)

def init_resource(package=None, resource='', tag=TAG, dirname=".genescape", path='', overwrite=False):

    # The filesystem directory
    dest = Path.home() / dirname / tag / path / resource

    # Ensure the target directory exists
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Get the path to a resource
    if not package or not resource:
        return dest

    # Create the resource if it does not exist.
    if not os.path.isfile(dest) or overwrite:
        with resources.path(package, resource) as src:
            # Copy the resource to the target directory
            shutil.copy(src, dest)
            info(f'# init resource: {dest}')

    return dest

# For Windows we package a prebuilt dot.exe
DOT_EXE = init_resource(package='genescape.bin', resource="dot.exe") if os.name == "nt" else "dot"

INDEX = init_resource(package='genescape.data', resource='genescape.hs.index.json.gz')

OBO_FILE = init_resource(package='genescape.data', resource='go-basic.obo.gz')

# Initialize test data files.
TEST_GOIDS = init_resource(package='genescape.data', resource="test_goids.txt")
TEST_GENES = init_resource(package='genescape.data', resource="test_genes.txt")
TEST_INPUT_CSV = init_resource(package='genescape.data', resource="test_input.csv")
TEST_INPUT_JSON = init_resource(package='genescape.data', resource="test_input.json")

# The GAF demo data.
GAF_FILE = init_resource(package='genescape.data', resource="goa_human.gaf.gz")

# The keys in the data annotation object.
STATUS_FIELD, DATA_FIELD, CODE_FIELD, ERROR_FIELD, INVALID_FIELD = "status", "data", "code", "errors", "unknown_terms"

# The name of the columns in the annotation CSV file
GID, LABEL, SOURCE = "gid", "label", "source"

# A few handy constants
DEGREE, COUNT_DESC, INPUT, NAME = "degree", "count_desc", "input", "name"

# Default background color
BG_COLOR = "#FFFFFF"

# Selection color
FG_COLOR = "#90EE90"

# Leaf color
LF_COLOR = "#ADD8E6"

# Default shape
SHAPE = "box"

# Set the default attributes for the nodes
NODE_ATTRS = dict(fillcolor=BG_COLOR, shape=SHAPE, style="filled")

# Map the GO categories to the short names
NAMESPACE_MAP = {
    "biological_process": "BP",
    "molecular_function": "MF",
    "cellular_component": "CC",
}

# The index names
IDX_OBO = "obo"
IDX_gene2go = "gene2go"
IDX_prot2go = "prot2go"
IDX_go2gene = "go2gene"
IDX_go2prot = "go2prot"

def get_json(path=INDEX):

    # Open JSON data
    if path.name.endswith(".gz"):
        stream = gzip.open(path, mode="rt", encoding="UTF-8")
    else:
        stream = open(path, encoding="utf-8-sig")

    # Load the  index.
    data = json.load(stream)

    return data

def parse_terms(iter):
    """
    Reads an iterator and returns a list of dictionaries keyed by header.
    """

    # Get the stream from the file
    stream1, stream2, stream3 = tee(iter, 3)

    # Try to parse the input as JSON.
    try:
        terms = json.loads("".join(stream1))
        return terms
    except json.JSONDecodeError:
        debug("Input is not JSON")
        pass

    # The resulting data dictionary.
    data = dict()

    # Open stream as CSV file
    reader2 = csv.reader(stream2)

    # Detect whether the file is header delimiter CSV or not
    headers = next(reader2)

    if GID in headers and LABEL in headers:
        # Has headers, read the specified columns
        debug("reading annotations as CSV")
        reader3 = csv.DictReader(stream3)

        def build(x):
            return {GID: x[GID], LABEL: x[LABEL]}

        terms = list(map(build, reader3))

    else:
        # No headers, read the first column.
        debug("reading first column of the file")
        reader3 = csv.reader(stream3)

        def build(x):
            return {GID: x[0]}

        terms = list(map(build, reader3))

    data[DATA_FIELD] = terms

    return data


# Attempts to get a stream of lines from a filename or the stdin.
def get_stream(inp=None):
    stream = []

    # Turn paths into strings.
    if isinstance(inp, pathlib.Path):
        inp = str(inp)

    if type(inp) == list:
        text = "\n".join(inp)
        stream = io.StringIO(text)
    elif type(inp) == str:
        if not os.path.isfile(inp):
            stop(f"file not found: {inp}")
        if inp.endswith(".gz"):
            debug(f"Reading gzip: {inp}")
            stream = gzip.open(inp, mode="rt", encoding="UTF-8")
        else:
            debug(f"Reading: {inp}")
            stream = open(inp, encoding="utf-8-sig")
    elif not sys.stdin.isatty():
        debug(f"Reading stdin")
        stream = sys.stdin
    else:
        stop("No input found. A filename or stream is required.")

    # Strip the lines, filter out empty and commented lines.
    stream = map(lambda x: x.strip(), stream)
    stream = filter(lambda x: x, stream)
    stream = filter(lambda x: not x.startswith("#"), stream)

    return stream


def get_goterms(graph):
    """
    Returns a list of GO terms from a graph.
    """

    def get_node(node):
        """
        Returns a node, name pair
        """
        return (node, graph.nodes[node].get('name', ''))

    def keep_node(node):
        """
        Keep nodes marked as input.
        """
        return graph.nodes[node].get(INPUT)

    nodes = filter(keep_node, graph.nodes)
    goterms = map(get_node, nodes)
    goterms = dict(goterms)

    return goterms


def timer(func):
    """
    Decorator that prints the execution time of the function it decorates.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"# Timer: {func.__name__}: took {elapsed:.2f} seconds")
        return result

    return wrapper
