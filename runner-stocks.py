from stocks.main import main
import logging
import click


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
@click.option('--infile', '-i', default="sp1.csv", help='The filename of the input file')
def fetch(infile):
    main(infile)

@click.command()
def populate():
    print("hello, world!")

start.add_command(fetch)
start.add_command(populate)

if __name__ == '__main__':
    start()
