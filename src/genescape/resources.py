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

    utils.debug(f"cache: {key}")

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
        targets = config.get("files", [])
        for value in targets:
            self.files[value["target"]] = value["path"]

        def get(name):
            return self.files.get(name, name)

        self.OBO_FILE = get("go-basic.obo.gz")

        # Initialize test data files.
        self.TEST_GOIDS = get("test_goids.txt")
        self.TEST_GENES = get("test_genes.txt")
        self.TEST_INPUT_CSV = get("test_input.csv")
        self.TEST_INPUT_JSON = get("test_input.json")

        # The GAF demo data.
        self.GAF_FILE = get("goa_human.gaf.gz")

        # The CSS and JS files.
        self.GENESCAPE_CSS = get("genescape.css")
        self.GENESCAPE_JS = get("genescape.js")
        self.VIZ_JS = get("viz-standalone.js")

        self.INDEX_MAP = {}


        def pieces(elem):
            return (elem.get("code", "CODE"), elem.get("label", "LABEL"), elem.get("path", "PATH"))

        values = self.config.get("files", [])
        values = filter(lambda x: x.get("type", "") == "index", values)
        values = map(lambda x: pieces(x), values)
        for code, label, path in values:
            self.INDEX_MAP[code] = (code, label, path)

        # Default code is the first file.
        self.DEFAULT_CODE = list(self.INDEX_MAP.keys())[0]

        # The default index.
        self.INDEX_FILE = self.find_index()

    def find_index(self, code=None):
        code = code or self.DEFAULT_CODE
        if code not in self.INDEX_MAP:
            raise Exception(f"Code not found: {code}")
        return self.INDEX_MAP[code][2]

    def index_choices(self):
        choices = dict(map(lambda x: (x[0], x[1]), self.INDEX_MAP.values()))
        return choices

    def update_from_env(self, key="GENESCAPE_INDEX"):
        """
        Need to put the new keys first
        """
        value = os.environ.get(key, None)
        if value:

            code, label, path = value.split(":")

            path = Path(path)
            # Check that path exists
            if not path.exists():
                utils.stop(f"Index does not exist: {path}")

            # Change the order
            current = list(self.INDEX_MAP.values())
            current.insert(0, (code, label, path))

            # Recreate the index map
            self.INDEX_MAP = dict(map(lambda x: (x[0], x), current))

# Reset the resource directory
def reset_dir(cnf=None):
    """
    Deletes the storage directory.
    """
    cnf = cnf or get_config()
    path = get_storage_dir(cnf)
    if os.path.isdir(path):
        utils.info(f"deleting path: {path}")
        shutil.rmtree(path)


def update_config(fname, cnf=None):
    """
    Updates a parsed toml object with a configuration file.
    """
    cnf = cnf or {}
    obj = get_config(fname)
    cnf.update(obj)
    return cnf

def get_config(fname=None):
    """
    Reads a configuration file.
    """
    if fname:
        config = toml.load(fname)
    else:
        with rsc.files("genescape.data").joinpath("config.toml").open() as path:
            config = toml.load(path)
    return config


def get_storage_dir(config):
    """
    The storage directory to the config file.
    """
    tag = config.get("tag", "v1")
    store = config.get("store", '~/.tmpdir')
    path = Path(os.path.expanduser(store)) / Path(tag)
    return path


def get_path(package='', target='', subdir=None, config=None):
    """
    Returns a file path to a resource.
    """

    if not target:
        utils.stop("missing target in configuration file record")

    # If the package is not defined, return the target as filepath.
    if not package:
        return Path(target)

    # Set a sane default for the configuration.
    config = config or {}

    # Static files need to be in a separate directory.
    subdir = subdir or []

    # Get the complete path to the resource.
    path = get_storage_dir(config) / Path(*subdir) / Path(target)

    # Ensure the target directory exists
    if not os.path.isdir(path.parent):

        # Creates local directory.
        utils.info(f"creating path: {path.parent}")

        path.parent.mkdir(parents=True, exist_ok=True)

    # Copy the resource to the target directory if it is not there or newer.
    with rsc.files(package).joinpath(target).open('rb') as src:
        # The condition to copy the resource
        cond = not os.path.isfile(path) or os.path.getmtime(src.fileno()) > os.path.getmtime(path)
        if cond:
            with open(path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            utils.info(f'copy: {path}')

    return path


def init(config=None):
    """
    Initializes resources from a configuration file.
    """

    # Initialize the configuration.
    config = config or get_config()

    # Initialize the targets in the config
    targets = config.get("files", [])

    # Adds a path to each target.
    for value in targets:
        package = value.get("package", None)
        target = value.get("target", None)
        subdir = value.get("subdir", [])
        path = get_path(package=package, target=target, subdir=subdir, config=config)
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

    os.environ['GENESCAPE_INDEX'] = "idx:GO:resources.py"

    cnf = get_config()

    res = init()
    res.update_from_env()

    ind = res.INDEX_MAP

    print (ind)

    print("-" * 80)
