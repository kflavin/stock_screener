
import logging
logger = logging.getLogger(__name__)


class Populator(object):
    """
    Parent class to be overridden by individual populators.  A populator is
    responsible for pulling all symbols associated with an index, and any
    required information for those securities.
    """
    def fetch_data(self):
        """
        Fetch the data
        """
        raise NotImplementedError

    def pop_stock_list(self):
        """
        Process fetched data and return a dictionary of stocks

        stock_list = {SYMBOL: {'NAME': COMPANY_NAME, 'SYMBOL' SYMBOL ...}
        """
        raise NotImplementedError

    def filter_headers(self):
        """
        Handle any modifications to the header names
        """
        raise NotImplementedError

    def write_csv(self, stock_list):
        """
        Write a CSV file. Required fields:
        ticker symbol,company name

        Other fields are optional.
        """
        import csv
        with open(self.outfile, 'w') as outfile:
            writer = csv.writer(outfile, delimiter=',',
                                quoting=csv.QUOTE_MINIMAL)
            for symbol, values in stock_list.items():
                # Need to find a better way to handle this...
                writer.writerow([values['symbol'], values['name']])

    def run(self):
        """
        Run the populator
        """
        raise NotImplementedError
