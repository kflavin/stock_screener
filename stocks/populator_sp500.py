
import logging
import requests
from bs4 import BeautifulSoup as bs

from stocks.populator_base import Populator

logger = logging.getLogger(__name__)


class SP500_Populator(Populator):
    sp_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    def __init__(self):
        pass

    def fetch_page(self, url):
        return requests.get(url).text

    def pop_stock_list(self, page):
        data = bs(page, 'html5lib')
        table = soup('table', {'class': ['sortable', 'wikitable', 'jquery-tablesorter']})[0]

        stock_list = {}
        keys = []

        for tr in table('tr'):
            if tr.th:
                for th in tr:
                    keys.append(th)
            elif tr.td:
                for td in enumerate(tr('td')):
                    
            elif tr.th:



    def run(self):
        page = self.fetch_data(self.sp_url)
        stock_list = self.pop_stock_list(page)
