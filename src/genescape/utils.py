import logging
import os
import sys

# Default paths.
DIR = os.path.dirname(os.path.realpath(__file__))

# Data file paths.
OBO = os.path.join(DIR, "data", "go-basic.json.gz")

# Demo data.
DEMO_DATA = os.path.join(DIR, "data", "gprofiler-demo.csv")

# Colors and shapes
FG_COLOR = "lightgreen"
BG_COLOR = "white"
SHAPE = "box"

# Set the default attributes for the nodes
NODE_ATTRS = dict(fillcolor=BG_COLOR, shape=SHAPE, style="filled")

# Loggin format
LOG_FORMAT = "# %(levelname)s\t%(module)s.%(funcName)s\t%(message)s"


# A callable to initialize the logger
def init_logger(logger):
    formatter = logging.Formatter(LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Get the logger.
logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

# Initialize the logger
init_logger(logger)

info = logger.info
error = logger.error
warn = logger.warning


def stop(msg):
    logger.error(msg)
    sys.exit(1)
