
import logging
logger = logging.getLogger(__name__)

class Populator(object):
    def fetch_page(self, url):
        raise NotImplementedError

    def pop_stock_list(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
