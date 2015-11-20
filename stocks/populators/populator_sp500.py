
import logging
import requests
import csv
from bs4 import BeautifulSoup as bs
from collections import OrderedDict
from stocks.populators.populator_base import Populator

logger = logging.getLogger(__name__)


class IndexPopulator(Populator):
    """
    Populator for the S&P500.  Pulls all S&P500 stocks from Wikipedia.
    """

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    def __init__(self, outfile, count=None):
        """
        Name of CSV file to write out and a max count of stocks to return.
        If count is None, return all.
        """
        self.count = count
        self.outfile = outfile

    def fetch_data(self, url):
        """
        Fetch the page
        """
        return requests.get(url).text

    def pop_stock_list(self, page):
        """
        Take the HTML page and pull out the values we want, returning a dict
        of stocks.
        """
        soup = bs(page, 'html5lib')
        table = soup('table', {'class':
                               ['sortable',
                                'wikitable',
                                'jquery-tablesorter']})[0]

        stock_list = OrderedDict()

        # Grab the headers
        headers = [self.filter_headers(th.text) for th in table('tr')[0]('th')]

        for idx,tr in enumerate(table('tr')):
            # If we specified a maximum number of stocks.
            if self.count and idx >= self.count:
                break

            if tr.td:
                symbol = tr.td.text

                stock_list[symbol] = {headers[i]: td.text.strip()
                                      for i, td in enumerate(tr('td'))}

        return stock_list

    def filter_headers(self, header):
        """
        Change the headers to some of our fields.
        """
        if header == "Ticker symbol":
            return "symbol"
        elif header == "GICS Sector":
            return "sector"
        elif header == "Security":
            return "name"
        elif header == "GICS Sub Industry":
            return "industry"
        else:
            return header

    def write_csv(self, stock_list):
        """
        Take a list of stocks and write them out to file.
        """

        with open(self.outfile, 'w') as outfile:
            writer = csv.writer(outfile, delimiter=',',
                                quoting=csv.QUOTE_MINIMAL)
            for symbol, values in stock_list.items():
                # Need to find a better way to handle this...
                writer.writerow([values['symbol'], values['name']])

    def run(self):
        """
        Fetch the stocks, populate, write CSV
        """
        page = self.fetch_data(self.url)
        stock_list = self.pop_stock_list(page)
        self.write_csv(stock_list)
