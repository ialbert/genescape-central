import os

import click

from genescape import utils


@click.group()
def cli():
    """
    genescape: visualize genomic functions
    """
    pass


@cli.command()
@click.argument("fname", default=None, required=False)
@click.option("-o", "out", metavar="TEXT", default="genescape.pdf", help="output graph file")
@click.option("-i", "index", metavar="FILE", default=utils.INDEX, help="OBO index file", )
@click.option("-d", "demo", is_flag=True, help="run with demo data")
@click.option( "-v", "verbose", is_flag=True, help="verbose output")
@click.help_option("-h", "--help")
def tree(fname, index, out, verbose, demo=False):
    """
    Draws a tree from GO terms.
    """

    # Check if the input file exists.if
    if not os.path.exists(index):
        utils.stop(f"OBO file {index} not found!")

    # Import the tree module.
    from genescape import tree

    # Set the verbosity level.
    if verbose:
        utils.logger.setLevel(utils.DEBUG)

    # Override the fname if demo is set.
    if demo:
        fname = utils.GO_LIST
        utils.info(f"input {fname}")

    # Run the tree command.
    tree.run(index=utils.INDEX, fname=fname, out=out)

@cli.command()
@click.argument("fname", default=None, required=False)
@click.option("-n", "top", metavar="TEXT", default=10, help="Limit to top N terms (default=10).")
@click.option("-i", "index", metavar="TEXT", default=utils.INDEX, help="OBO index file.")
@click.option("-m", "match", metavar="REGEX", default='', help="Regular expression match on function")
@click.option("-c", "minc", metavar="INT", default=1,  type=int, help="The minimal count for a GO term (1)")
@click.option("-d", "demo", is_flag=True, help="Run with demo data")
@click.option( "-v", "verbose", is_flag=True, help="Verbose output.")
@click.help_option("-h", "--help")
def annotate(fname, index, verbose=False, demo=False, top=10, match="", minc=1):
    """
    Generates the GO terms for a list of genes.
    """
    from genescape import annot
    if demo:
        fname = utils.GENE_LIST
        utils.info(f"input {fname}")

    # Set the verbosity level.
    if verbose:
        utils.logger.setLevel(utils.DEBUG)

    utils.debug(f"params n={top} c={minc} m={match}")
    annot.run(fname=fname, index=index, top=top, verbose=verbose, match=match, minc=minc)


@cli.command()
@click.option("-i", default="go-basic.obo", help="Input OBO file")
@click.option("-o", default="genescape.json.gz", help="Output JSON file (gzipped)")
@click.help_option("-h", "--help")
def build(inp, out):
    """
    Builds a JSON index file from an OBO file.
    """
    # click.echo(f"Running with parameter {inp} {out}")
    from genescape.gs_build import make_json

    make_json(obo=inp, index=out)


@cli.command()
@click.argument("fname", default=None, required=False)
@click.option("-c", "mcol", metavar="TEXT", default="term_id", help="column name to extract")
@click.option("-p", "pcol", metavar="TEXT", help="p-value column name")
@click.option("-v", "pval", default=0.05, type=float, metavar="TEXT", help="p-value treshold (0.05)")
@click.option("-m", "match", metavar="TEXT", help="regex match on line")
@click.option("-t", "tab", is_flag=True, help="tab delimited file")
@click.option("-d", "demo", is_flag=True, help="run with demo data")
@click.help_option("-h", "--help")
def filter(fname="", mcol="source", pcol="", pval="", match="", tab=False, demo=False):
    """
    Filters a CSV/TSV file by columns.
    """

    from genescape import gs_filter

    # Override the fname if demo is set.
    if demo:
        fname = utils.DEMO_CSV
        match = "BP"
        utils.info(f"input {fname}")

    delim = "\t" if tab else ","
    gs_filter.run(fname=fname, mcol=mcol, pcol=pcol, pval=pval, match=match, delim=delim)


if __name__ == "__main__":
    tree()
