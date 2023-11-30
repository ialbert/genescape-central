import os

import click

from genescape import obo, utils


@click.group()
def cli():
    """
    GeneScape: ontology based functional analysis
    """
    pass


@cli.command()
@click.option("--obo", default=utils.OBO, help="input OBO file")
@click.option("--out", "-o", default="output.pdf", help="output file")
@click.option("--category", "-c", default="MF", help="GO category")
@click.option("--pcol", default="pval", help="p-value column")
@click.option("--pval", default=0.05, help="p-value threshold")
@click.option('--verbose', "-v", is_flag=False)
@click.argument("fname", default=utils.DEMO_DATA)
def tree(fname, obo, out, pcol, pval, category, verbose):
    """
    Subcommand for query operations.
    """
    if not os.path.exists(obo):
        utils.stop(f"OBO file {obo} not found!")
    from genescape import tree

    if verbose:
        utils.logger.setLevel(utils.DEBUG)

    tree.run(json_obo=obo, fname=fname, out=out, cat=category)


@cli.command()
@click.option("--inp", "-i", default="tmp/go-basic.obo", help="Input OBO file")
@click.option("--out", "-o", default="tmp/go-basic.json.gz", help="Output JSON file (gzipped)")
def build(inp, out):
    """
    Build a JSON file from an OBO file.
    """
    # click.echo(f"Running with parameter {inp} {out}")
    from genescape.obo import make_json

    make_json(obo_name=inp, json_name=out)


if __name__ == "__main__":
    cli()
