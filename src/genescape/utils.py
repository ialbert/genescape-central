import logging
import os
import sys
from logging import DEBUG, ERROR, INFO, WARNING

# Current directory.
CURR_DIR = os.path.dirname(os.path.realpath(__file__))

# Data file paths.
INDEX = os.path.join(CURR_DIR, "data", "genescape.index.json.gz")

# The OBO file.
OBO_FILE = os.path.join(CURR_DIR, "data", "go-basic.obo")

# Demo data.
DEMO_CSV = os.path.join(CURR_DIR, "data", "gprofiler.csv")

# The GO ids to draw.
DEMO_DATA = os.path.join(CURR_DIR, "data", "goids.txt")

# The GAF demo data.
GAF_FILE = os.path.join(CURR_DIR, "data", "goa_human.gaf.gz")

# The default gene list.
GENE_LIST = os.path.join(CURR_DIR, "data", "genelist.txt")

# The name of the columns in the annotation CSV file
GOID, LABEL = "goid", "label"

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

# Loggin format
LOG_FORMAT = "# %(levelname)s\t%(module)s.%(funcName)s\t%(message)s"

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

logging.addLevelName(logging.WARNING, "WARN")

# Initialize the logger
init_logger(logger)

debug = logger.debug
info = logger.info
warn = logger.warning
error = logger.error

# Stops the process with an error.
def stop(msg):
    logger.error(msg)
    sys.exit(1)

# Attempts to get a stream from a filename or the stdin.
def get_stream(fname):
    stream = None

    if fname:
        debug(f"Reading: {fname}")
        stream = open(fname, encoding="utf-8-sig")
    elif not sys.stdin.isatty():
        debug(f"Reading stdin")
        stream = sys.stdin
    else:
        stop("No input found. A filename or stream is required.")

    # Filter strip the lines, filter out empty and commented lines.
    stream = map(lambda x: x.strip(), stream)
    stream = filter(lambda x: x, stream)
    stream = filter(lambda x: not x.startswith("#"), stream)

    return stream
