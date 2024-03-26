import os
from pathlib import Path
import click

from genescape import utils, resources


@click.group()
def cli():
    """
    Genomic function visualization.
    """
    pass



@cli.command()
@click.argument("fname", default=None, required=False)
@click.option("-o", "--out", "out", metavar="TEXT", default="genescape.pdf", help="output graph file")
@click.option("-i", "--index", "index", metavar="FILE", help="OBO index file", )
@click.option("-m", "--match", "match", metavar="REGEX", default='', help="Regular expression match on function")
@click.option("-c", "--count", "count", metavar="INT", default=1, type=int, help="The minimal count for a GO term (1)")
@click.option("-t", "--test", "test", is_flag=True, help="run with demo data")
@click.option("-v", "verbose", is_flag=True, help="verbose output")
@click.help_option("-h", "--help")
def tree(fname, out=None, index=None, match=None, count=1, verbose=False, test=False):
    """
    Draws a tree from GO terms.
    """
    # Import the tree module.
    from genescape import tree

    # Initialize the resources.
    res = resources.init()

    # Get the index
    index = resources.get_index(index=index, res=res)

    # Set the verbosity level.
    utils.verbosity(verbose)

    # Override the fname if demo is set.
    if test:
        fname = res.TEST_GOIDS
        utils.info(f"input {fname}")

    # Run the tree command.
    graph, ann = tree.parse_input(inp=fname, index=index, pattern=match, mincount=count)

    # Write the tree to a file.
    tree.write_tree(graph, ann, out=out)


@cli.command()
@click.argument("fname", default=None, required=False)
@click.option("-i", "--index", "index", metavar="TEXT", help="OBO index file.")
@click.option("-m", "--match", "match", metavar="REGEX", default='', help="Regular expression match on function")
@click.option("-c", "--count", "count", metavar="INT", default=1, type=int, help="The minimal count for a GO term (1)")
@click.option("-t", "--test", "test", is_flag=True, help="Run with test data")
@click.option("--csv", "csvout", is_flag=True, help="Produce CSV output instead of JSON")
@click.option("-v", "verbose", is_flag=True, help="Verbose output.")
@click.help_option("-h", "--help")
def annotate(fname, index=None, verbose=False, test=False, csvout=False, match="", count=1):
    """
    Generates the GO terms for a list of genes.
    """
    from genescape import annot

    # Initialize the resources.
    res = resources.init()

    # Get the index
    index = resources.get_index(index=index, res=res)

    if test:
        fname = res.TEST_GENES
        utils.info(f"input {fname}")

    # Set the verbosity level.
    utils.verbosity(verbose)

    # Open the input file
    stream = utils.get_stream(inp=fname)

    # Parse the input into a list
    data = utils.parse_terms(stream)

    # Print the input parameters.
    utils.debug(f"params c={count} m={match}")

    # Get the annotation output
    out = annot.run(data=data, index=index, pattern=match, mincount=count, csvout=csvout)

    # Print the annotation aoutput.
    print(out)


@cli.command()
@click.option("--obo", "obo", help="Input OBO file (go-basic.obo)")
@click.option("--gaf", "gaf", help="Input GAF file (goa_human.gaf.gz)")
@click.option("-i", "--index", "index", default="genescape.json.gz", help="Output index file (genescape.json.gz)")
@click.help_option("-h", "--help")
def build(index=None, obo=None, gaf=None, ):
    """
    Builds a JSON index file from an OBO file.
    """
    # click.echo(f"Running with parameter {inp} {out}")
    from genescape import build

    res = resources.init()

    obo = Path(obo) if obo else res.OBO_FILE
    gaf = Path(gaf) if gaf else res.GAF_FILE

    build.make_index(obo=obo, gaf=gaf, index=index)


@cli.command()
@click.option("--devmode", "devmode", is_flag=True, help="run in development mode")
@click.option("--reset", "reset", is_flag=True, help="reset the resources")
@click.option("-i", "--index", "index",  help="Genescape index file")
@click.option("-n", "--nobrowser", "nopop", is_flag=True, help="Don't pop a browser window.")
@click.option("-v", "verbose", is_flag=True, help="Verbose output.")
@click.help_option("-h", "--help")
def web(devmode=False, reset=False, verbose=False, index=None, nopop=False):
    """
    Run the web interface.
    """
    from genescape import server

    # Set the verbosity level.
    utils.verbosity(verbose)

    # Start the server.
    server.start(devmode=devmode, reset=reset, index=index, popwin=not nopop)


if __name__ == "__main__":
    cli()
