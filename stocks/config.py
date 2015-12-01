import sys
from configparser import ConfigParser

from collections import OrderedDict, namedtuple

import logging
logger = logging.getLogger("stocks")

picks_file = "./stocks_screened.csv" # Good companies
all_file = "./stocks_all.csv"        # Full list of stocks

# Filters
filters = {'ROE (%)': ">19", 'Profit Margin (%)': '>9', 'Operating Margin (%)': '>9', 'Total Debt/Equity': '<100', 'Past 5 Years (%)': '>9'}
#filters = {'ROE (%)': ">10", 'Profit Margin (%)': '>5', 'Operating Margin (%)': '>5', 'Total Debt/Equity': '<100', 'Past 5 Years (%)': '>5'}

# Values to fetch from finance page
# key is the label, value is the search string
stats = OrderedDict()
stats['ROE (%)'] = {"search": "Return on Equity", "filter": ">15"}
stats['Free Cash Flow'] = {"search": "Levered Free Cash Flow"}
stats['Profit Margin (%)'] = {"search": "Profit Margin", "filter": ">10"}
stats['Operating Margin (%)'] = {"search": "Operating Margin", "filter": ">10"}
stats['Total Debt/Equity'] = {"search": "Total Debt/Equity"}
stats['P/E (ttm)'] = {"search": "Trailing P/E"}
stats['P/E (forward)'] = {"search": "Forward P/E"}
stats['Current Ratio'] = {"search": "Current Ratio"}
stats['PEG'] = {"search": "PEG Ratio"}
stats['Diluted EPS'] = {"search": "Diluted EPS (ttm):"}
stats['Dividend'] = {"search": "Trailing Annual Dividend Yield"}

# Stock values is a dictionary of named tuples
# stock_values = {}
stock_values = OrderedDict()
Stock = namedtuple('Stock', 'symbol sector subsector')

stock_picks = OrderedDict()
stock_all = OrderedDict()

# URL's we need to pull the data we want
url = "http://finance.yahoo.com/q/ks?s=%s+Key+Statistics"
bs_url = "http://finance.yahoo.com/q/bs?s=%s+Balance+Sheet&annual"
is_url = "http://finance.yahoo.com/q/is?s=%s+Income+Statement&annual"
cf_url = "http://finance.yahoo.com/q/cf?s=%s+Cash+Flow&annual"
id_url = "http://finance.yahoo.com/q/in?s=%s+Industry"
ae_url = "http://finance.yahoo.com/q/ae?s=%s+Analyst+Estimates"

config = ConfigParser()
config.read("./stocks.conf")
connection_string = ""
if 'database' not in config:
    raise Exception("No config file defined.")
    sys.exit(1)
else:
    engine = config['database']['engine']
    if engine == "sqlite":
        connection_string = "sqlite:///{0}".format(config['database']['file'])
    else:
        database = config['database']
        connection_string = "{0}://{1}:{2}@{3}/{4}".format(database['engine'],
                                                      database['user'],
                                                      database['password'],
                                                      database['host'],
                                                      database['database'])
