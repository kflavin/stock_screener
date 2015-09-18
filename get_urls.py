
import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
import sys
import csv
import pdb
from collections import namedtuple, OrderedDict

results_file = "./stocks_screened.csv"

# key is the label, value is the search string
abbr = OrderedDict()
abbr['ROE (%)'] = "Return on Equity"
abbr['Free Cash Flow'] = "Levered Free Cash Flow"
abbr['Profit Margin (%)'] = "Profit Margin"
abbr['Operating Margin (%)'] = "Operating Margin"
abbr['Total Debt/Equity'] = "Total Debt/Equity"
abbr['P/E (ttm)'] = "Trailing P/E"
abbr['P/E (forward)'] = "Forward P/E"
abbr['Current Ratio'] = "Current Ratio"
abbr['PEG'] = "PEG Ratio"

#stock_values = {}
stock_values = OrderedDict()
Stock = namedtuple('Stock', 'symbol sector subsector')

url = "http://finance.yahoo.com/q/ks?s=%s+Key+Statistics"
bs_url = "http://finance.yahoo.com/q/bs?s=%s+Balance+Sheet&annual"
is_url = "http://finance.yahoo.com/q/is?s=%s+Income+Statement&annual"
cf_url = "http://finance.yahoo.com/q/cf?s=%s+Cash+Flow&annual"
id_url = "http://finance.yahoo.com/q/in?s=%s+Industry"

sem = asyncio.Semaphore(20)

def get_field(line, field, delimiter=","):
    """
    Need something smarter than split, because commas could be embedded inside quotes.
    """

    flag = False
    token = ""
    field_no = 0
    for ch in line:
        if ch == '"':
            flag = not flag
            continue

        if not flag:
            if ch == delimiter:
                if field_no == field:
                    return token
                else:
                    field_no += 1
                    token = ""
                    continue
        token += ch
                


def get_stock_list(filename):
    """
    Return a list of stocks, either from CSV file or text file.
    """
    f = open(filename, "r")
    stocks = f.read().split("\n")
    f.close()

    stock_list = []

    try:
        ext = filename.split(".")[1]
    except:
        ext = ""

    if ext == "csv":
        stock_list = [Stock(symbol=get_field(line, 0),
                            sector=get_field(line, 3),
                            subsector=get_field(line, 4)) for line in stocks if line]
    else:
        for stock in stocks:
            stock = stock.strip()
            if stock and not stock.startswith("#"):
                stock_list.append(stock)

    return stock_list

def build_values(key_stats, industry_details, stock):
    """
    Take values and build a dictionary for the given stock
    """
    
    stock_values = OrderedDict()

    # Get the values we need from industry details page
    soup = bs(industry_details, "html.parser")
    for td in soup.findAll("th"):
        if td.text.startswith("Sector:"):
            value = td.findNextSibling().text
            stock_values["Sector"] = value.strip("%")
        elif td.text.startswith("Industry:"):
            value = td.findNextSibling().text
            stock_values["Industry"] = value.strip("%")

    if "Industry" not in stock_values.keys():
        stock_values["Industry"] = ""
    if "Sector" not in stock_values.keys():
        stock_values["Sector"] = ""

    # Get the values we need from the key statistics page
    soup = bs(key_stats, "html.parser")


    for k,v in abbr.items():
        for td in soup.findAll("td"):
            if td.text.startswith(v):
                value = td.findNextSibling().text
                stock_values[k] = value.strip("%")

    #for td in soup.findAll("td"):
    #    for k,v in abbr.items():
    #        if td.text.startswith(v):
    #            value = td.findNextSibling().text
    #            stock_values[k] = value.strip("%")

    return stock_values


@asyncio.coroutine
def do_work(stock):
    """
    Retrieve data on each stock ticker symbol.
    """
    global stock_values, sem
    with (yield from sem):
        print("grabbed sem", sem, stock.symbol)
        key_response = yield from aiohttp.request('GET', url % stock.symbol)
        industry_response = yield from aiohttp.request('GET', id_url % stock.symbol)
        #income_response = yield from aiohttp.request('GET', is_url % stock.symbol)
        #balance_response = yield from aiohttp.request('GET', bs_url % stock.symbol)
        #cash_flow_response = yield from aiohttp.request('GET', cf_url % stock.symbol)

    key_stats = yield from key_response.read()
    industry_details = yield from industry_response.read()
    #income = yield from income_response.read()
    #balance = yield from balance_response.read()
    #cash_flow = yield from cash_flow_response.read()
    #stock_values[stock.symbol] = build_values(key_stats, income, balance, cash_flow, stock)
    stock_values[stock.symbol] = build_values(key_stats, industry_details, stock)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("Usage: %s <stock filename>" % sys.argv[0])
        sys.exit(1)

    # stocks is a list of namedtuples
    stocks = get_stock_list(filename)

    loop = asyncio.get_event_loop()
    f = asyncio.wait([do_work(stock) for stock in stocks])
    loop.run_until_complete(f)
    #print("your stocks", stocks)
    #print("your values", stock_values)

    with open(results_file, 'w') as csvfile:
        #writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        # get header vlaues
        print(stock_values[list(stock_values.keys())[0]])
        headers = list(stock_values[list(stock_values.keys())[0]].keys())
        headers.insert(0, "Symbol")
        writer.writerow(headers)

        for n,d in stock_values.items():
            stats = []
            for v in d.values():
                stats.append(v)
            #writer.writerow(n + values)
            stats.insert(0, n)
            writer.writerow(stats)
        print("localc", results_file)
