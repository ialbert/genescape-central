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
@click.option("--name", "-n", default="JOE", help="Name parameter for query.")
@click.option("--obo", default=utils.OBO, help="Input OBO file")
def run(name, obo=obo):
    """
    Subcommand for query operations.
    """
    if not os.path.exists(obo):
        utils.stop(f"OBO file {obo} not found!")
    utils.info(f"Using name={name}")


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
