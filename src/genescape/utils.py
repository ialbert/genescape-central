import logging, functools, time
import os, gzip, json, csv
import sys, pathlib
from logging import DEBUG, ERROR, INFO, WARNING
from itertools import tee
import io, shutil


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

# Set the log level
def verbosity(flag=False):
    global logger
    if flag:
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)

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

# The keys in the data annotation object.
STATUS_FIELD, DATA_FIELD, CODE_FIELD, ERROR_FIELD, INVALID_FIELD = "status", "data", "code", "errors", "unknown_terms"

# The name of the columns in the annotation CSV file
GID, LABEL, SOURCE = "gid", "label", "source"

# A few handy constants
DEGREE, COUNT_DESC, INPUT, NAME, NAMESPACE = "degree", "count_desc", "input", "name", "namespace"

# Default background color
BG_COLOR = "#FFFFFF"

# Selection color
INPUT_COLOR = "#A3F6A2"

# Leaf color
LEAF_COLOR = "#17DA15"

# Default shape
SHAPE = "box"

# Set the default attributes for the nodes
NODE_ATTRS = dict(fillcolor=BG_COLOR, shape=SHAPE, style="filled")

# Namespace categories
NS_BP, NS_MF, NS_CC, NS_ALL = "BP", "MF", "CC", "ALL"

# Map the GO categories namespaces.
NAMESPACE_MAP = {
    "biological_process": NS_BP,
    "molecular_function": NS_MF,
    "cellular_component": NS_CC,
}

# Revers namespace map
NAMESPACE_MAP_REV = dict( (y, x) for x,y in NAMESPACE_MAP.items() )

# Map colors to the namespaces.
NAMESPACE_COLORS = {
     NS_BP: "#F6CBA2",
     NS_MF: "#A2CDF6",
     NS_CC: "#F5A2F6",
}

# The index names
IDX_OBO = "obo"
IDX_gene2go = "gene2go"
IDX_prot2go = "prot2go"
IDX_go2gene = "go2gene"
IDX_go2prot = "go2prot"


def parse_terms(iterable):
    """
    Reads an iterator and returns a list of dictionaries keyed by header.
    """

    # Get the stream from the file
    stream1, stream2, stream3 = tee(iterable, 3)

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
