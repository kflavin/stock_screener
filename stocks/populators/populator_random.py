
import logging
import requests
import csv
import random
from functools import wraps
from bs4 import BeautifulSoup as bs
from collections import OrderedDict
# from stocks.populators.populator_base import Populator
from stocks.populators.populator_r3k import IndexPopulator

logger = logging.getLogger(__name__)


class PopDec(object):
    """
    Decorator to only return the first "n" stocks.  Right now it
    pulls from the S&P500 index, but this could be easily changed
    to the R3K by changing the IndexPopulator imported.
    """
    def __init__(self, n=10):
        self.n = n

    def __call__(self, f):
        @wraps(f)
        def wrapped_func(*args):
            """
            Returns "n" stocks to the user.
            """
            stock_list = f(*args)
            keys = list(stock_list.keys())
            random.shuffle(keys)
            short_stock_list = {keys[i]:
                                stock_list[keys[i]]
                                for i in range(0, self.n)}
            return short_stock_list
        return wrapped_func


class IndexPopulator(IndexPopulator):
    """
    Debug Populator:
    Take only the first 25 securities from the S&P500.
    Otherwise, identical.
    """

    @PopDec()
    def pop_stock_list(self, *args, **kwargs):
        """
        Take the HTML page and pull out the values we want, returning a dict
        of stocks.
        """
        return super().pop_stock_list(*args, **kwargs)
