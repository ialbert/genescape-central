import sys, json, os
from pathlib import Path
import click
from genescape import __version__
from genescape import resources, utils, gs_graph, gs_index
from pprint import pprint

# Valid choices for root
ROOT_CHOICES = [utils.NS_BP, utils.NS_MF, utils.NS_CC, utils.NS_ALL]

HELP = f"Gene function visualization (v{__version__})."


def require_params(it):
    errflag = False
    for name, fname in it:
        if not fname:
            utils.error(f"parameter --{name} must be specified")
            errflag = True
    if errflag:
        sys.exit(1)


def check_files(it):
    errflag = False

    for name, fname in it:
        if not fname:
            utils.error(f"parameter --{name} must be specified")
            errflag = True
        elif not os.path.isfile(fname):
            utils.error(f"file for --{name} not found: {fname}")
            errflag = True

    # Check that the files are present
    if errflag:
        sys.exit(1)


class HelpFormatter(click.Group):
    def format_help(self, ctx, fmt):
        super().format_help(ctx, fmt)
        # Here you add your additional usage examples
        with fmt.section('Examples'):
            fmt.write_text('genescape web')
            fmt.write_text('genescape annotate genelist.txt')
            fmt.write_text('genescape tree genelist.txt -o output.pdf')
            fmt.write_text('genescape show GO:0005737')


@click.group(help=HELP, cls=HelpFormatter)
def run():
    pass


@run.command()
@click.argument("fname", default=None, required=False)
@click.option("-i", "--idx", "idx_fname", metavar="TEXT", help="Genescape index file.")
@click.option("-o", "--out", "out_fname", default="", metavar="TEXT", help="Output file (default: screen).")
@click.option("-m", "--match", "match", metavar="REGEX", default='', help="Regular expression match on function")
@click.option("-c", "--mincov", "coverage", metavar="INT", default=0, type=int,
              help="The minimal coverage for a GO term (1)")
@click.option("-t", "--test", "test", is_flag=True, help="Run with test data")
@click.option('-r', '--root',
              type=click.Choice(ROOT_CHOICES, case_sensitive=False),
              default=utils.NS_ALL,
              help='Select a category: BP, MF, CC, or ALL.',
              )
@click.option("-v", "verbose", is_flag=True, help="Verbose output.")
@click.help_option("-h", "--help")
def annotate(fname, out_fname='', idx_fname=None, root=utils.NS_ALL, verbose=False, test=False, match="", coverage=0):
    """
    Generates GO terms annotations for a list of genes.
    """
    res = resources.init()
    idx_fname = idx_fname or res.INDEX_FILE

    if test:
        fname = res.TEST_GENES
        utils.info(f"input: {fname}")

    targets = utils.parse_genes(fname)

    idg = gs_graph.load_index_graph(idx_fname)

    # Estimate the count if not provided
    if coverage < 1:
        coverage = gs_graph.estimate(idg, targets=targets, pattern=match, root=root)

    run = gs_graph.subgraph(idg, targets=targets, root=root, coverage=coverage, pattern=match)

    utils.info(f"graph: {run.tree.number_of_nodes()} nodes, {run.tree.number_of_edges()} edges")

    df = run.as_df()

    text = df.to_csv(index=False)

    if out_fname:
        utils.info(f"output: {out_fname}")
        with open(out_fname, "wt") as fp:
            fp.write(text)
    else:
        print(text, end='')


@run.command()
@click.argument("fname", default=None, required=False)
@click.option("-i", "--idx", "idx_fname", metavar="TEXT", help="Genescape index file.")
@click.option("-o", "--out", "out_fname", default="output.pdf", metavar="TEXT", help="Output image file.")
@click.option("-m", "--match", "match", metavar="REGEX", default='', help="Regular expression match on function")
@click.option("-c", "--mincov", "coverage", metavar="INT", default=0, type=int,
              help="The minimal coverage for a GO term (1)")
@click.option("-t", "--test", "test", is_flag=True, help="Run with test data")
@click.option('-r', '--root',
              type=click.Choice(ROOT_CHOICES, case_sensitive=False),
              default=utils.NS_ALL,
              help='Select a category: BP, MF, CC, or ALL.',
              )
@click.option("-v", "verbose", is_flag=True, help="Verbose output.")
@click.help_option("-h", "--help")
def tree(fname, out_fname='', idx_fname=None, root=utils.NS_ALL, verbose=False, test=False, match="", coverage=0):
    """
    Generates GO terms annotations for a list of genes.
    """
    res = resources.init()
    idx_fname = idx_fname or res.INDEX_FILE

    if test:
        fname = res.TEST_GENES
        utils.info(f"input: {fname}")

    targets = utils.parse_genes(fname)

    idg = gs_graph.load_index_graph(idx_fname)

    # Estimate the count if not provided
    if coverage < 1:
        coverage = gs_graph.estimate(idg, targets=targets, pattern=match, root=root)

    run = gs_graph.subgraph(idg, targets=targets, root=root, coverage=coverage, pattern=match)

    pg = run.as_pydot()

    utils.info(f"graph: {run.tree.number_of_nodes()} nodes, {run.tree.number_of_edges()} edges")

    gs_graph.save_graph(pg, fname=out_fname, imgsize=4096)


@run.command()
@click.option("-b", "--obo", "obo_fname", help="Input OBO file (go-basic.obo)")
@click.option("-g", "--gaf", "gaf_fname", help="Input GAF file (goa_human.gaf.gz)")
@click.option("-i", "--idx", "idx_fname", default="genescape.index.gz", help="Output index file (genescape.json.gz)")
@click.option("-s", "--stats", "stats", is_flag=True, help="Print the index stats")
@click.option("-d", "--dump", "dump", is_flag=True, help="Print the index file to the screen")
@click.option("-t", "--test", "test", is_flag=True, help="Run with test data")
@click.help_option("-h", "--help")
def build(idx_fname=None, obo_fname=None, gaf_fname=None, stats=False, dump=False, test=False):
    """
    Builds index file from an OBO and GAF file.
    """
    res = resources.init()

    if stats:
        idg = gs_graph.load_index_graph(idx_fname)
        print(idg)
        return

    if dump:
        idg = gs_graph.load_index_graph(idx_fname)
        text = json.dumps(idg.idx.data, indent=4)
        print(text)
        return

    # Runs with test data
    if test:
        obo_fname = res.OBO_FILE
        gaf_fname = res.GAF_FILE

    fnames = [
        ('obo', obo_fname),
        ('gaf', gaf_fname),
    ]

    check_files(fnames)

    utils.info(f"obo: {obo_fname}")
    utils.info(f"gaf: {gaf_fname}")
    utils.info(f"index: {idx_fname}")
    idx = gs_index.build_index(obo_fname=obo_fname, gaf_fname=gaf_fname, fname=idx_fname)
    gs_index.save_index(idx, idx_fname)

    utils.info(str(idx))

    # Print file size in megabytes
    size = Path(idx_fname).stat().st_size / 1024 / 1024
    utils.info(f"index: {idx_fname} ({size:.2f} MB)")


@run.command()
@click.option("-i", "--idx", "idx_fname", default="", help="Index file")
@click.option("--host", "host", default="127.0.0.1", help="Hostname to bind to")
@click.option("--port", "port", default=8000, type=int, help="Port number")
@click.option("-r", "--reload", "reload", is_flag=True, help="Reload the webserver on changes")
@click.option("-t", "--test", "test", is_flag=True, help="Test mode (autgenerates gene lists)")
@click.help_option("-h", "--help")
def web(idx_fname='', host='localhost', port=8000, reload=False, test=False):
    """
    Runs the web interface
    """
    import shiny

    # Insert the index into the environment.
    if idx_fname:
        if not os.path.isfile(idx_fname):
            utils.stop(f"# Index not found: {idx_fname}")
        key = "idx"
        label = str(Path(idx_fname).name).split(".")[0].title()
        os.environ['GENESCAPE_INDEX'] = f'{key}:{label}:{idx_fname}'

    # Set the testing enviroment.
    if test:
        os.environ['GENESCAPE_TEST'] = '1'

    shiny.run_app("genescape.shiny.tree.app:app", host=host, port=port, reload=reload)


if __name__ == '__main__':
    # sys.argv.extend( ("build", "--stats"))

    cmd = "show GO:0005737"

    sys.argv.extend(cmd.split())
    run()
