import click
from pathlib import Path
from genescape import __version__
from genescape import resources, utils


HELP  = f"Gene function visualization (v{__version__})."

@click.group(help=HELP)
def cli():
    pass


ROOT_CHOICES = [utils.NS_BP, utils.NS_MF, utils.NS_CC, utils.NS_ALL]


@cli.command()
@click.argument("fname", default=None, required=False)
@click.option("-o", "--out", "out", metavar="TEXT", default="genescape.pdf", help="output graph file")
@click.option(
    "-i",
    "--index",
    "index",
    metavar="FILE",
    help="OBO index file",
)
@click.option("-m", "--match", "match", metavar="REGEX", default='', help="Regular expression match on function")
@click.option("-c", "--count", "count", metavar="INT", default=1, type=int, help="The minimal count for a GO term (1)")
@click.option(
    '-r',
    '--root',
    type=click.Choice(ROOT_CHOICES, case_sensitive=False),
    default=utils.NS_ALL,
    help='Select a category: BP, MF, CC, or ALL.',
)
@click.option("-t", "--test", "test", is_flag=True, help="run with demo data")
@click.option("-v", "verbose", is_flag=True, help="verbose output")
@click.help_option("-h", "--help")
def tree(fname, out=None, index=None, root=utils.NS_ALL, match=None, count=1, verbose=False, test=False):
    """
    Draws a tree from GO terms.
    """
    # Import the tree module.
    from genescape import tree

    # Get the configuration file
    cnf = resources.get_config()

    # Initialize the resources.
    res = resources.init(cnf)

    # Get the index
    index = resources.get_index(index=index, res=res)

    # Set the verbosity level.
    utils.verbosity(verbose)

    # Override the fname if demo is set.
    if test:
        fname = res.TEST_GENES
        utils.info(f"input: {fname}")

    # Run the tree command.
    graph, ann = tree.parse_input(inp=fname, index=index, pattern=match, mincount=count, root=root)

    # Write the tree to a file.
    tree.write_tree(graph, ann, out=out)


@cli.command()
@click.argument("fname", default=None, required=False)
@click.option("-i", "--index", "index", metavar="TEXT", help="OBO index file.")
@click.option("-o", "--out", "out", metavar="TEXT", default="", help="output graph file")
@click.option("-m", "--match", "match", metavar="REGEX", default='', help="Regular expression match on function")
@click.option("-c", "--count", "count", metavar="INT", default=1, type=int, help="The minimal count for a GO term (1)")
@click.option("-t", "--test", "test", is_flag=True, help="Run with test data")
@click.option(
    '-r',
    '--root',
    type=click.Choice(ROOT_CHOICES, case_sensitive=False),
    default=utils.NS_ALL,
    help='Select a category: BP, MF, CC, or ALL.',
)
@click.option("--csv", "csvout", is_flag=True, help="Produce CSV output instead of JSON")
@click.option("-v", "verbose", is_flag=True, help="Verbose output.")
@click.help_option("-h", "--help")
def annotate(fname, index=None, root=utils.NS_ALL, verbose=False, test=False, csvout=False, match="", count=1, out=''):
    """
    Generates the GO terms for a list of genes.
    """
    from genescape import annot

    # Get the configuration file
    cnf = resources.get_config()

    # Initialize the resources.
    res = resources.init(cnf)

    # Get the index
    index = resources.get_index(index=index, res=res)

    if test:
        fname = res.TEST_GENES
        utils.info(f"input: {fname}")

    # Set the verbosity level.
    utils.verbosity(verbose)

    # Open the input file
    stream = utils.get_stream(inp=fname)

    # Parse the input into a list
    data = utils.parse_terms(stream)

    # Print the input parameters.
    utils.debug(f"params c={count} m={match}")

    # Get the annotation output
    text = annot.run(data=data, index=index, pattern=match, mincount=count, csvout=csvout, root=root)

    # How to deal with outputs.
    if not out:
        print(text)
    else:
        with open(out, "wt",  newline='') as fp:
            fp.write(text)


@cli.command()
@click.option("-b", "--obo", "obo", help="Input OBO file (go-basic.obo)")
@click.option("-g", "--gaf", "gaf", help="Input GAF file (goa_human.gaf.gz)")
@click.option("-i", "--index", "index", default="genescape.json.gz", help="Output index file (genescape.json.gz)")
@click.option("-s", "--synonms", "synon", is_flag=True, help="Include synonyms in the index")
@click.option("-d", "--dump", "dump", is_flag=True, help="Print the index to stdout")
@click.help_option("-h", "--help")
def build(index=None, obo=None, gaf=None, synon=False, dump=False):
    """
    Builds a JSON index file from an OBO file.
    """
    # click.echo(f"Running with parameter {inp} {out}")
    from genescape import build

    # Get the configuration file
    cnf = resources.get_config()

    # Initialize the resources.
    res = resources.init(cnf)

    # Set the input files.
    obo = Path(obo) if obo else res.OBO_FILE
    gaf = Path(gaf) if gaf else res.GAF_FILE
    ind = Path(index)

    if dump:

        @utils.timer
        def load_index():
            retval = resources.get_json(ind)
            return retval

        obj = load_index()
        meta = obj[utils.IDX_META_DATA]
        print(f"# {meta}")
        sym2go = obj[utils.IDX_SYM2GO]
        for key, value in sym2go.items():
            row = [key] + value
            print("\t".join(row))

    else:
        # Run the build command.
        build.make_index(obo=obo, gaf=gaf, index=ind, with_synonyms=synon)


@cli.command()
@click.option("--devmode", "devmode", is_flag=True, help="run in development mode")
@click.option("--reset", "reset", is_flag=True, help="reset the resources")
@click.option("-i", "--index", "index", help="Genescape index file")
@click.option("-v", "verbose", is_flag=True, help="Verbose output.")
@click.help_option("-h", "--help")
def web(devmode=False, reset=False, verbose=False, index=None):
    """
    Run the web interface.
    """
    from genescape import server

    # Set the verbosity level.
    utils.verbosity(verbose)

    # Start the server.
    server.start(devmode=devmode, reset=reset, index=index)


if __name__ == "__main__":
    cli()
