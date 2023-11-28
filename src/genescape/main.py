import click


@click.group()
def cli():
    """GeneScape: ontology based functional analysis"""
    pass


@cli.command()
@click.option("--name", "-n", required=True, help="Name parameter for query.")
def query(name):
    """Subcommand for query operations."""
    click.echo(f"Querying for {name}")


@cli.command()
@click.option("--param", "-p", required=True, help="Parameter for run.")
def run(param):
    """Subcommand for run operations."""
    click.echo(f"Running with parameter {param}")


if __name__ == "__main__":
    cli()
