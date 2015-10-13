from stocks.main import main
import logging
import click



@click.command()
@click.option('--input', default="sp1.csv", help='The filename of the input file')
@click.option('--debug', is_flag=True, default=False)
def start(input, debug):
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
    main(input)

if __name__ == '__main__':
    start()
