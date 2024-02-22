import logging
import os
import sys
from logging import DEBUG, ERROR, INFO, WARNING

# Current directory.
CURR_DIR = os.path.dirname(os.path.realpath(__file__))

# Data file paths.
OBO_JSON = os.path.join(CURR_DIR, "data", "go-basic.json.gz")

# Demo data.
DEMO_CSV = os.path.join(CURR_DIR, "data", "gprofiler.csv")

# The GO ids to draw.
DEMO_DATA = os.path.join(CURR_DIR, "data", "goids.txt")

# The GOF demo data.
GAF_REF_DATA = os.path.join(CURR_DIR, "data", "goa_human.gaf.gz")
GAF_GENE_LIST = os.path.join(CURR_DIR, "data", "genelist.txt")

# The name of the columns in the annotation CSV file
GOID, LABEL = "goid", "label"

# Selection color
FG_COLOR = "#90EE90"

# Leaf color
LF_COLOR = "#ADD8E6"

# Background color
BG_COLOR = "#FFFFFF"

# Default shape
SHAPE = "box"

# Set the default attributes for the nodes
NODE_ATTRS = dict(fillcolor=BG_COLOR, shape=SHAPE, style="filled")

# Loggin format
LOG_FORMAT = "# %(levelname)s\t%(module)s.%(funcName)s\t%(message)s"

# Map the GO categories to the short names
NAMESPACE_MAP = {
    "biological_process": "BP",
    "molecular_function": "MF",
    "cellular_component": "CC",
}


# A callable to initialize the logger
def init_logger(logger):
    formatter = logging.Formatter(LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Get the logger.
logger = logging.getLogger(__name__)

# Set the default loglevel.
logger.setLevel(INFO)

# Initialize the logger
init_logger(logger)

debug = logger.debug
info = logger.info
warn = logger.warning
error = logger.error


def stop(msg):
    logger.error(msg)
    sys.exit(1)


def get_stream(fname):
    stream = None

    if fname:
        debug(f"Reading: {fname}")
        stream = open(fname, encoding="utf-8-sig")
    elif not sys.stdin.isatty():
        stream = sys.stdin
    else:
        stop("No input found. A filename or stream is required.")

    stream = map(lambda x: x.strip(), stream)
    stream = filter(lambda x: x, stream)
    stream = filter(lambda x: not x.startswith("#"), stream)

    return stream
