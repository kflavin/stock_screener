
import logging
logger = logging.getLogger(__name__)


class Populator(object):
    def fetch_data(self, url):
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

    def write_csv(self):
        """
        Write a CSV file. Required fields:
        ticker symbol,company name

        Other fields are optional.
        """
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
