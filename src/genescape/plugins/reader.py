from genescape import utils
from genescape.plugins import enrichr, gprofiler

plugins = [gprofiler, enrichr]


def csv(fname):
    """
    Selects the stream based on plugins.
    """
    for plugin in plugins:
        # First valid plugin wins.
        if plugin.check_format(fname):
            utils.info(f"plugin: {plugin.__name__}")
            stream = plugin.get_stream(fname)
            relabel = plugin.relabel
            return stream, relabel

    utils.stop(f"Unknown input format: {fname}")
