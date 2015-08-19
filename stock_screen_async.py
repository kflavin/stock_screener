
import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
import sys
import csv

symbol_file = "./symbols"
results_file = "./stock_screener2"

abbr = {
    'pb': "Price/Book",
    'ps': "Price/Sales"
}

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
        stock_list = [line.split(",")[0] for line in stocks if line]
    else:
        for stock in stocks:
            stock = stock.strip()
            if stock and not stock.startswith("#"):
                stock_list.append(stock)

    return stock_list

#symbol = sys.argv[1]
@asyncio.coroutine
def get_values(symbol):
    stock_values = {}
    url = "http://finance.yahoo.com/q/ks?s=%s+Key+Statistics" % symbol
    response = yield from aiohttp.request('GET', url)
    #body = yield from response.yield_and_close(decode=True)
    body = yield from response.read()

    soup = bs(body)

    for td in soup.findAll("td"):
        if td.text.startswith(abbr['pb']):
            # price to book
            pb = td.findNext().text
            stock_values['pb'] = pb
            #values[stock]['pb'] = pb
            #print "%s Price/Book: " % symbol, pb
        elif td.text.startswith(abbr['ps']):
            # price to sales
            ps = td.findNext().text
            stock_values['ps'] = ps
            #print "%s Price/Sales: " % symbol, ps
    print(stock_values)
    return stock_values

@asyncio.coroutine
def init(loop):
    values = {}
    for stock in stocks:
        values[stock] = get_values(stock)

    with open(results_file, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # get header vlaues
        headers = values[values.keys()[0]].keys()
        headers.insert(0, "Symbol")
        writer.writerow(headers)

        for n,d in values.iteritems():
            stats = []
            for v in d.values():
                stats.append(v)
            #writer.writerow(n + values)
            stats.insert(0, n)
            writer.writerow(stats)
        print("localc", results_file)
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("Usage: %s <stock filename>" % sys.argv[0])
        sys.exit(1)

    stocks = get_stock_list(filename)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))




