import click
import pandas as pd
import src.db.build as build
from dotenv import load_dotenv

# Laad de .env variabelen
load_dotenv()


@click.group()
def cli():
    pass


@cli.command(no_args_is_help=True)
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.Path(exists=False))
def csv_to_parquet(input, output=None):
    """Converteer csv naar parquet."""
    if output is None:
        output = input.replace('.csv', '.parquet')
    df = pd.read_csv(input, delimiter=';')
    df.to_parquet(output)


@cli.command()
def init_db():
    """Initialiseer de database."""
    build.init_db()


if __name__ == '__main__':
    cli()
