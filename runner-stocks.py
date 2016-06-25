import logging
import click
import sys
from stocks.main import main
from stocks.populate import populate_index
from requests import ConnectionError

# Get rid of this...
default_file = "sp10.csv"

@click.group()
@click.option('--debug', is_flag=True, default=False)
def start(debug):
    """
    Initialization function.
    """
    if debug:
        debug_level = "DEBUG"
    else:
        debug_level = "INFO"

    global logger
    logger = logging.getLogger("stocks")
    logger.setLevel(level=debug_level)
    sh = logging.StreamHandler()
    sh.setLevel(logging.WARNING)
    logger.addHandler(sh)
    fh = logging.FileHandler("screener.log")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)


@click.command()
@click.option('--outfile', '-o',
              default="indexdata.csv",
              help='Outfile for index data.')
@click.option('--index', '-i',
              default="sp500",
              help='The index to import [sp500|r3k]')
def fetch(index, outfile):
    """
    Fetch the stocks into a CSV file, given an index.
    """
    populate_index(index, outfile=outfile)


@click.command()
@click.option('--infile', '-i',
              default=default_file,
              help='The filename of the input csv')
def populate(infile):
    """
    Populate the given stocks with their key indicators.
    """
    main(infile)


@click.command()
@click.option('--index', '-i',
              default="sp500",
              help='The index [sp500|r3k|random]')
@click.option('--ofile', '-o',
              default=None,
              help='Specify an output file to save index data.')
@click.option('--count', '-c',
              type=click.INT,
              help='Number of stocks to import.  An index of random is fixed at 10')
def run(index, ofile, count):
    """
    Full run.  Fetch the index, populate index, populate database.
    """
    stock_file = populate_index(index, ofile, count)
    main(stock_file)


# Add all of our actions
start.add_command(populate)
start.add_command(fetch)
start.add_command(run)

if __name__ == '__main__':
    try:
        start()
    except ConnectionError as e:
        print("Populator could not connect.  Exiting.")
        raise
