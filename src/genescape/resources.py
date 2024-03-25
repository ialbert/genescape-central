from genescape import utils
import shutil, os, gzip, json
from pathlib import Path
from importlib import resources as rsc

CURR_DIR = Path(os.path.dirname(__file__))


# For Windows we package a prebuilt dot.exe
DOT_EXE = None
INDEX = None
OBO_FILE = None

# Initialize test data files.
TEST_GOIDS = None
TEST_GENES = None
TEST_INPUT_CSV = None
TEST_INPUT_JSON = None

# The GAF demo data.
GAF_FILE = None

# WEB related resources
RESOURCES = [

    # Default files needed for operations.
    ("INDEX", "genescape.data", "genescape.hs.index.json.gz", ),
    ("OBO_FILE", "genescape.data", "go-basic.obo.gz"),
    ("GAF_FILE", "genescape.data", "genescape.hs.index.json.gz"),
    ("TEST_GOIDS",  "genescape.data", "test_goids.txt"),
    ("TEST_GENES", "genescape.data", "test_genes.txt"),
    ("TEST_INPUT_CSV", "genescape.data", "test_input.csv"),
    ("TEST_INPUT_JSON", "genescape.data", "test_input.json"),

    # Web related resources
    (None, "genescape.data.web", "index.html"),
    (None, "genescape.data.web", "draw.html"),
    (None, "genescape.data.web.static", "genescape.css"),
    (None,"genescape.data.web.static", "genescape.js"),
    (None,"genescape.data.web.static", "genescape.js"),
    (None,"genescape.data.web.static", "htmx.min.js.gz"),
    (None,"genescape.data.web.static", "viz-standalone.js"),
    (None,"genescape.data.web.static", "mini-default.css"),
    (None,"genescape.data.web.static", "sailboat.png"),
]

# Get the resource directory
def resource_dir(dirname=".genescape", tag=utils.TAG):
    path = Path.home() / dirname / tag
    return path

# Reset the resource directory
def reset_resource(dirname=".genescape", tag=utils.TAG):
    path = resource_dir(dirname=dirname, tag=tag)
    shutil.rmtree(path)

# Initialize a resource that may be in home directory.
def init_resource(package=None, target='', tag=utils.TAG, dirname=".genescape", path='', devmode=False):

    # The path during devmode are the local files
    if devmode:
        parts = package.split('.')[1:]
        dest = Path(CURR_DIR, *parts) / target
        return dest

    # The filesystem directory
    dest = resource_dir(dirname=dirname, tag=tag) / path / target

    # Ensure the target directory exists
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Get the path to a resource
    if not package or not target:
        return dest

    # Create the resource if it does not exist.
    if not os.path.isfile(dest):
        with rsc.path(package, target) as src:
            # Copy the resource to the target directory
            shutil.copy(src, dest)
            utils.info(f'# init resource: {dest}')

    return dest

def init_all(devmode=False, path="web", tag=utils.TAG):
    for name, package, target in RESOURCES:
        respath = init_resource(package=package,
                             target=target,
                             tag=tag, path=path, devmode=devmode)
        if name is not None:
            if name not in globals():
                utils.warn(f"possibly undefined resource {name}")
            globals()[name] = respath

        utils.debug(f"init resource: {respath}")

def get_json(path=INDEX):

    # Open JSON data
    if path.name.endswith(".gz"):
        stream = gzip.open(path, mode="rt", encoding="UTF-8")
    else:
        stream = open(path, encoding="utf-8-sig")

    # Load the  index.
    data = json.load(stream)

    return data


if __name__ == "__main__":
    init_all()

