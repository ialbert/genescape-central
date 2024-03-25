from genescape import utils
import shutil, os, gzip, json
from pathlib import Path
from importlib import resources as rsc

CURR_DIR = Path(os.path.dirname(__file__))

class Resource(object):
    def __init__(self):
        self.INDEX = None
        self.OBO_FILE = None

        # Initialize test data files.
        self.TEST_GOIDS = None
        self.TEST_GENES = None
        self.TEST_INPUT_CSV = None
        self.TEST_INPUT_JSON = None

        # The GAF demo data.
        self.GAF_FILE = None

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

# Reset the resource directory
def reset_dir(dirname=".genescape", tag=utils.TAG):
    path = resource_dir(dirname=dirname, tag=tag)

    if os.path.isdir(path):
        utils.info(f"deleting path: {path}")
        shutil.rmtree(path)


# Get the resource directory
def resource_dir(dirname=".genescape", tag=utils.TAG):
    path = Path.home() / dirname / tag
    return path

# Initialize a resource that may be in home directory.
def init_resource(package=None, target='', tag=utils.TAG, dirname=".genescape", path='', devmode=False):

    # The path during devmode are the local files
    if devmode:
        parts = package.split('.')[1:]
        dest = Path(CURR_DIR, *parts) / target
        if not os.path.isfile(dest):
            utils.warn(f"missing devmode resource: {dest}")
        return dest

    # The filesystem directory
    dest = resource_dir(dirname=dirname, tag=tag) / path / target

    if not os.path.isdir(dest.parent):
        # Creates local directory.
        utils.info(f"creating path: {dest}")

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
            utils.info(f'copy resource: {dest}')

    return dest

# Initialize all resources
def init(devmode=False, path="web", tag=utils.TAG):

    res = Resource()

    for name, package, target in RESOURCES:
        value = init_resource(package=package,
                             target=target,
                             tag=tag, path=path, devmode=devmode)
        if name is not None:
            if not hasattr(res, name):
                utils.warn(f"possibly undefined resource {name}")
            setattr(res, name, value)

        utils.debug(f"init resource {value}")

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


if __name__ == "__main__":
    #utils.verbosity(True)
    #reset_dir()
    init()

    print ("-" * 80)


