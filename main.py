import click
import pandas as pd


@click.command(no_args_is_help=True)
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.Path(exists=False))
def csv_to_parquet(input, output):
    df = pd.read_csv(input, delimiter=';')
    df.to_parquet(output)


if __name__ == '__main__':
    csv_to_parquet()
