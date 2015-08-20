
import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
import sys
import csv
import pdb
from collections import namedtuple

symbol_file = "./symbols"
results_file = "./stocks_screened.csv"

abbr = {
    'pb': "Price/Book",
    'ps': "Price/Sales",
    'peg': "PEG Ratio",
}

stock_values = {}
Stock = namedtuple('Stock', 'symbol sector subsector')

url = "http://finance.yahoo.com/q/ks?s=%s+Key+Statistics"

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

def build_values(body, stock):
    """
    Grab Values from 
    """
    stock_values = {}
    #for field in stock._fields:
        #stock_values[field] = getattr(stock, field)
    print(stock_values)
    sys.exit()

    soup = bs(body, "html.parser")
    for td in soup.findAll("td"):
        if td.text.startswith(abbr['pb']):
        # price to book
            #pb = td.findNext().text
            pb = td.findNextSibling().text
            stock_values['pb'] = pb
            #values[stock]['pb'] = pb
            #print "%s Price/Book: " % symbol, pb
        elif td.text.startswith(abbr['ps']):
        # price to sales
            #ps = td.findNext().text
            ps = td.findNextSibling().text
            stock_values['ps'] = ps
            #print "%s Price/Sales: " % symbol, ps
        elif td.text.startswith(abbr['peg']):
        # peg
            peg = td.findNextSibling().text
            stock_values['peg'] = peg
            #print "%s Price/Sales: " % symbol, ps
    return stock_values


@asyncio.coroutine
def do_work(stock):
    global stock_values, sem
    with (yield from sem):
        print("grabbed sem", sem, stock.symbol)
        response = yield from aiohttp.request('GET', url % stock.symbol)

    body = yield from response.read()
    stock_values[stock.symbol] = build_values(body, stock)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("Usage: %s <stock filename>" % sys.argv[0])
        sys.exit(1)

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
