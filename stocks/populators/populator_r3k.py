
import logging
import requests
import csv
from collections import OrderedDict
import os
import subprocess
import atexit
from io import BytesIO
from tempfile import NamedTemporaryFile as NTF

from stocks.populators.populator_base import Populator

logger = logging.getLogger(__name__)


class IndexPopulator(Populator):
    """
    Russell 3000 populator.  Pulls all symbols from a PDF on the Russell page.
    """

    url = 'http://www.russell.com/documents/indexes/membership/membership-russell-3000.pdf'

    def __init__(self, outfile):
        """
        Name of CSV file to write out.
        """
        self.outfile = outfile

    def fetch_data(self, url):
        """
        Fetch the page
        """
        return requests.get(url).content

    def pop_stock_list(self, page):
        """
        Take the PDF page and pull out the values we want, returning a dict.
        """
        pdf_command = "pdftotext"

        pdf_file = NTF(delete=False)
        pdf_file.write(page)
        pdf_file.close()

        output = subprocess.Popen([pdf_command, "-raw", pdf_file.name, self.outfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        if output[1]:
            raise(output[1])


        with open(self.outfile, "r") as f:
            data = f.read().split("\n")

        stock_list = OrderedDict()
        headers = ['name', 'symbol',]

        #with open(out_file, 'w') as csvfile:
            #writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        for line in data:
            if line.startswith("As of ") or \
                line.startswith("As of ") or \
                line.startswith("Russell 3000") or \
                line.startswith("Index membership") or \
                line.startswith("Company Ticker"):
                pass

            elif line.startswith("For more information about Russell Indexes call us"):
                break
            else:
                symbol = line.split()[-1]
                name = " ".join(line.split()[0:-1])
                stock_list[symbol] = {'name': name, 'symbol': symbol,}
                #writer.writerow((ticker, company))

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

    def run(self):
        """
        Fetch page, build list, write CSV
        """
        page = self.fetch_data(self.url)
        stock_list = self.pop_stock_list(page)
        self.write_csv(stock_list)
