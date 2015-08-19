
import requests
from BeautifulSoup import BeautifulSoup as bs
import sys
import csv

symbol_file = "./symbols"
results_file = "./stock_screener"


values = {}
abbr = {
    'pb': "Price/Book",
    'ps': "Price/Sales"
}

def get_stock_list(filename):
    f = open(filename, "r")
    stocks = f.read().split("\n")
    f.close()

    stock_list = []

    if filename.split(".")[1] == "csv":
        stock_list = [line.split(",")[0] for line in stocks if line]
    else:
        for stock in stocks:
            stock = stock.strip()
            if stock and not stock.startswith("#"):
                stock_list.append(stock)

    return stock_list

#symbol = sys.argv[1]
def get_values(symbol):
    global values
    soup = bs(requests.get("http://finance.yahoo.com/q/ks?s=%s+Key+Statistics" % symbol).text)

    for td in soup.findAll("td"):
        if td.text.startswith(abbr['pb']):
            pb = td.findNext().text
            values[stock]['pb'] = pb
            #print "%s Price/Book: " % symbol, pb
        elif td.text.startswith(abbr['ps']):
            ps = td.findNext().text
            values[stock]['ps'] = ps
            #print "%s Price/Sales: " % symbol, ps

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print "Usage: %s <stock filename>" % sys.argv[0]
        sys.exit(1)

    stocks = get_stock_list(filename)

    for stock in stocks:
        values[stock] = {}
        get_values(stock)

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
        print "localc", results_file



