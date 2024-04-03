import gzip
import json
import os
import pprint
import shutil
from importlib import resources as rsc
from pathlib import Path

import toml

from genescape import utils

CURR_DIR = Path(os.path.dirname(__file__))

CACHE = {}


def cache(key, func):
    global CACHE

    #key = str(key)

    utils.info(f"cache key: {key}")

    if key not in CACHE:
        CACHE[key] = func()

    return CACHE[key]


def clear_cache():
    global CACHE
    CACHE = {}


class Resource:

    def __init__(self, config):

        # Save the configuration.
        self.config = config

        # Store the files separately.
        self.files = dict()

        # Populate the resource files.
        targets = config.get("index", []) + config.get("files", [])
        for value in targets:
            self.files[value["target"]] = value["path"]

        def get(name):
            return self.files.get(name, name)

        self.INDEX = get("genescape.hs.json.gz")
        self.OBO_FILE = get("go-basic.obo.gz")

        # Initialize test data files.
        self.TEST_GOIDS = get("test_goids.txt")
        self.TEST_GENES = get("test_genes.txt")
        self.TEST_INPUT_CSV = get("test_input.csv")
        self.TEST_INPUT_JSON = get("test_input.json")

        # The GAF demo data.
        self.GAF_FILE = get("goa_human.gaf.gz")

        # Webserver related directories
        self.WEB_DIR = get("index.html").parent
        self.STATIC_DIR = self.WEB_DIR / "static"

    def get_index(self, code):
        for value in self.config.get("index", []):
            if value.get("code", "") == code:
                return value["path"]
        utils.error("index code not found: {code}")
        return self.INDEX


# Reset the resource directory
def reset_dir(config):
    """
    Deletes the storage directory.
    """
    path = get_storedir(config)
    if os.path.isdir(path):
        utils.info(f"deleting path: {path}")
        shutil.rmtree(path)


def get_config(fname=None):
    """
    Reads a configuration file.
    """
    if fname:
        config = toml.load(fname)
    else:
        with rsc.path(package="genescape.data", resource="config.toml") as path:
            config = toml.load(path)
    return config


def get_storedir(config):
    """
    The storage directory to the config file.
    """
    tag = config.get("tag", "v1")
    store = config.get("store", '~/.tmpdir')
    path = Path(os.path.expanduser(store)) / Path(tag)
    return path


def get_path(package, target, subdir=None, config=None, devmode=False):
    """
    Returns a file path to a resource.
    """

    if not target:
        utils.stop("missing target in configuration file record")

    # If the package is not defined, return the target as filepath.
    if not package:
        return Path(target)

    # The paths during devmode are the local files
    if devmode:
        parts = package.split('.')[1:]
        path = Path(CURR_DIR, *parts) / target
        if not os.path.isfile(path):
            utils.warn(f"missing devmode resource: {path}")
        return path

    # Set a sane default for the configuration.
    config = config or {}

    # Static files need to be in a separate directory.
    subdir = subdir or []

    # Get the complete path to the resource.
    path = get_storedir(config) / Path(*subdir) / Path(target)

    if not os.path.isdir(path.parent):
        # Creates local directory.
        utils.info(f"creating path: {path.parent}")

        # Ensure the target directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        # Create the resource if it does not exist.

    with rsc.path(package, target) as src:
        # The condition to copy the resource
        cond = not os.path.isfile(path) or os.path.getmtime(src) > os.path.getmtime(path)
        if cond:
            # Copy the resource to the target directory
            shutil.copy(src, path)
            utils.info(f'copy: {path}')

    return path


def init(config, devmode=False):
    """
    Initializes the data the configuration file points to.
    """
    # Initialize the targets in the config
    targets = config.get("index", []) + config.get("files", [])

    # Get the path to each resource.
    for value in targets:
        package = value.get("package", None)
        target = value.get("target", None)
        subdir = value.get("subdir", [])
        path = get_path(package=package, target=target, subdir=subdir, config=config, devmode=devmode)
        if path:
            value['path'] = path

    res = Resource(config)

    return res


def get_json(path):

    # Open JSON data
    if path.name.endswith(".gz"):
        stream = gzip.open(str(path), mode="rt", encoding="UTF-8")
    else:
        stream = open(str(path), encoding="utf-8-sig")

    # Load the  index.
    data = json.load(stream)

    return data


def get_index(index, res):
    index = Path(index) if index else res.INDEX

    if not index or not os.path.exists(index):
        utils.stop(f"Index not found: {index}")

    return index


if __name__ == "__main__":
    utils.verbosity(True)

    cnf = get_config()

    # reset_dir(config)

    res = init(config=cnf, devmode=False)

    print(res.WEB_DIR)

    print(res.get_index("mm"))

    print("-" * 80)
