import logging
import click
from stocks.main import main
from stocks.populate import populate_index

@click.group()
@click.option('--debug', is_flag=True, default=False)
def start(debug):
    if debug:
        debugLevel="DEBUG"
    else:
        debugLevel="INFO"

    logger = logging.getLogger("stocks")
    logger.setLevel(level=debugLevel)
    sh = logging.StreamHandler()
    #fmt = logging.Formatter('%(asctime)s %(levelname)s %(filename)s - %(message)s')
    #sh.setFormatter(fmt)
    logger.addHandler(sh)

@click.command()
@click.option('--index', '-i', default="sp500", help='The index to import (sp500)')
def populate(index):
    """
    Populate the given index.
    """
    populate_index(index)
        
@click.command()
@click.option('--infile', '-i', default="sp1.csv", help='The filename of the input file')
def fetch(infile):
    """
    Fetch stats for symbols given in infile
    """
    main(infile)


start.add_command(populate)
start.add_command(fetch)

if __name__ == '__main__':
    start()
