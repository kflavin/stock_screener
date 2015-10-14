import logging
import click
from stocks.main import main
from stocks.populator_sp500 import IndexPopulator as SP5IP

@click.group()
@click.option('--debug', is_flag=True, default=False)
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
@click.option('--infile', '-i', default="sp1.csv", help='The filename of the input file')
def fetch(infile):
    main(infile)

@click.command()
@click.option('--index', '-i', default="sp500", help='The index to import (sp500)')
def populate(index):
    print("Importing", index)
    if index == "sp500":
        populator = SP5IP("%s.new.csv" % index)
    else:
        populator = SP5IP("%s.new.csv" % index)

    populator.run()

        

start.add_command(fetch)
start.add_command(populate)

if __name__ == '__main__':
    start()
