import logging
import click
import atexit
import os
import tempfile
from stocks.main import main
from stocks.populate import populate_index

# Get rid of this...
default_file = "sp10.csv"

@click.group()
@click.option('--debug', is_flag=True, default=False)
def start(debug):
    if debug:
        debugLevel = "DEBUG"
    else:
        debugLevel = "INFO"

    logger = logging.getLogger("stocks")
    logger.setLevel(level=debugLevel)
    sh = logging.StreamHandler()
    logger.addHandler(sh)


@click.command()
@click.option('--index', '-i',
              default="sp500",
              help='The index to import [sp500|r3k]')
def populate(index):
    """
    Populate the given index with our stocks.
    """
    _ = populate_index(index)


@click.command()
@click.option('--infile', '-i',
              default=default_file,
              help='The filename of the input csv')
def fetch(infile):
    """
    Fetch key stats for symbols given in infile
    """
    main(infile)

@click.command()
@click.option('--index', '-i',
              default="sp500",
              help='The index [sp500|r3k|random]')
@click.option('--ofile', '-o',
              default=None,
              help='Specify an output file to save index data.')
def full_run(index, ofile):
    """
    Fetch key stats for symbols given in infile
    """
    stock_file = populate_index(index, ofile)
    main(stock_file)


# Add all of our actions
start.add_command(populate)
start.add_command(fetch)
start.add_command(full_run)

if __name__ == '__main__':
    start()
