import sys, json
import click
from genescape import __version__
from genescape import resources, utils, nexus

# Valid choices for root
ROOT_CHOICES = [utils.NS_BP, utils.NS_MF, utils.NS_CC, utils.NS_ALL]

HELP  = f"Gene function visualization (v{__version__})."

@click.group(help=HELP)
def run():
    pass

@run.command()
@click.argument("fname", default=None, required=False)
@click.option("-i", "--idx", "idx_fname", metavar="TEXT", help="Genescape index file.")
@click.option("-o", "--out", "out_fname", default="", metavar="TEXT", help="Output file (default: screen).")
@click.option("-m", "--match", "match", metavar="REGEX", default='', help="Regular expression match on function")
@click.option("-c", "--count", "count", metavar="INT", default=1, type=int, help="The minimal count for a GO term (1)")
@click.option("-t", "--test", "test", is_flag=True, help="Run with test data")
@click.option( '-r', '--root',
    type=click.Choice(ROOT_CHOICES, case_sensitive=False),
    default=utils.NS_ALL,
    help='Select a category: BP, MF, CC, or ALL.',
)
@click.option("-v", "verbose", is_flag=True, help="Verbose output.")
@click.help_option("-h", "--help")
def annotate(fname, out_fname='', idx_fname=None, root=utils.NS_ALL, verbose=False, test=False, match="", count=1):
    """
    Generates GO terms annotations for a list of genes.
    """
    res = resources.init()
    idx_fname = idx_fname or res.INDEX_FILE

    if test:
        fname = res.TEST_GENES
        utils.info(f"input: {fname}")

    targets = utils.parse_genes(fname)

    pd, tree, ann = nexus.run(genes=targets, idx_fname=idx_fname, root=root,  pattern=match, mincount=count)

    if out_fname:
        utils.info(f"output: {out_fname}")
        with open(out_fname, "wt") as fp:
            fp.write(ann)
    else:
        print(ann, end='')

@run.command()
@click.argument("fname", default=None, required=False)
@click.option("-i", "--idx", "idx_fname", metavar="TEXT", help="Genescape index file.")
@click.option("-o", "--out", "out_fname", default="output.pdf", metavar="TEXT", help="Output image file.")
@click.option("-m", "--match", "match", metavar="REGEX", default='', help="Regular expression match on function")
@click.option("-c", "--count", "count", metavar="INT", default=1, type=int, help="The minimal count for a GO term (1)")
@click.option("-t", "--test", "test", is_flag=True, help="Run with test data")
@click.option( '-r', '--root',
    type=click.Choice(ROOT_CHOICES, case_sensitive=False),
    default=utils.NS_ALL,
    help='Select a category: BP, MF, CC, or ALL.',
)
@click.option("-v", "verbose", is_flag=True, help="Verbose output.")
@click.help_option("-h", "--help")
def tree(fname, out_fname='', idx_fname=None, root=utils.NS_ALL, verbose=False, test=False, match="", count=1):
    """
    Generates GO terms annotations for a list of genes.
    """
    res = resources.init()
    idx_fname = idx_fname or res.INDEX_FILE

    if test:
        fname = res.TEST_GENES
        utils.info(f"input: {fname}")

    targets = utils.parse_genes(fname)

    pd, tree, ann = nexus.run(genes=targets, idx_fname=idx_fname, root=root,  pattern=match, mincount=count)

    nexus.save_graph(pd, fname=out_fname, imgsize=2048)


@run.command()
@click.option("-b", "--obo", "obo_fname", help="Input OBO file (go-basic.obo)")
@click.option("-g", "--gaf", "gaf_fname", help="Input GAF file (goa_human.gaf.gz)")
@click.option("-i", "--idx", "idx_fname", default="genescape.json.gz", help="Output index file (genescape.json.gz)")
@click.option("-s", "--stats", "stats", is_flag=True, help="Print the index stats")
@click.option("-d", "--dump", "dump", is_flag=True, help="Print the index file to the screen")
@click.help_option("-h", "--help")
def build(idx_fname=None, obo_fname=None, gaf_fname=None, stats=False, dump=False):
    """
    Builds index file from an OBO and GAF file.
    """
    res = resources.init()
    obo_fname = obo_fname or res.OBO_FILE
    gaf_fname = gaf_fname or res.GAF_FILE
    utils.info(f"index: {idx_fname}")

    if stats:
        idx = nexus.load_index(idx_fname)
        nexus.stats(idx)
    elif dump:
        idx = nexus.load_index(idx_fname)
        text = json.dumps(idx, indent=4)
        print(text)
    else:
        utils.info(f"obo: {obo_fname}")
        utils.info(f"gaf: {gaf_fname}")
        nexus.build_index(obo_fname=obo_fname, gaf_fname=gaf_fname, idx_fname=idx_fname)
        utils.info(f"idx: {idx_fname}")

if __name__ =='__main__':
    #sys.argv.extend( ("build", "--stats"))

    cmd = "tree -t"

    sys.argv.extend(cmd.split())
    run()
