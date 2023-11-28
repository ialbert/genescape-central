import logging
import os
import sys

DIR = os.path.dirname(os.path.realpath(__file__))
OBO = os.path.join(DIR, "data", "go-basic.json.gz")

LOG_FORMAT = f"# %(levelname)s\t{__package__}.%(module)s.%(funcName)s\t%(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
)

logger = logging.getLogger(__name__)

info = logger.info
error = logger.error


def stop(msg):
    logger.error(msg)
    sys.exit(1)
