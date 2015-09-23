
import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
import sys
import csv
import pdb
from collections import namedtuple, OrderedDict

results_file = "./stocks_screened.csv"

# Filters
filters = {'ROE (%)': ">19", 'Profit Margin (%)': '>9', 'Operating Margin (%)': '>9', 'Total Debt/Equity': '<100'}

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

# Stock values is a dictionary of named tuples
#stock_values = {}
stock_values = OrderedDict()
Stock = namedtuple('Stock', 'symbol sector subsector')

stock_picks = OrderedDict()

url = "http://finance.yahoo.com/q/ks?s=%s+Key+Statistics"
bs_url = "http://finance.yahoo.com/q/bs?s=%s+Balance+Sheet&annual"
is_url = "http://finance.yahoo.com/q/is?s=%s+Income+Statement&annual"
cf_url = "http://finance.yahoo.com/q/cf?s=%s+Cash+Flow&annual"
id_url = "http://finance.yahoo.com/q/in?s=%s+Industry"
ae_url = "http://finance.yahoo.com/q/ae?s=%s+Analyst+Estimates"

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
    Return a list of stocks to be operated on, either from CSV file or text file.
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

def build_values(key_stats, industry_details, estimates, stock):
    """
    Take values given from HTTP queries and build a dictionary for the given stock
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




    # Get the values we need from the Analyst estimate page
    soup = bs(estimates, "html.parser")
    for td in soup.findall("td"):
        if td.text.startswith("Past 5 Years (per annum)"):
            value = td.findNextSibling().text
            stock_values["Past 5 Years"] = value.strip("%")
        elif td.text.startswith("Next 5 Years (per annum)"):
            value = td.findNextSibling().text
            stock_values["Next 5 Years"] = value.strip("%")


    # Cleanup any values that were missed, by setting them to ''
    stock_keys = stock_values.keys()

    if "Industry" not in stock_keys:
        stock_values["Industry"] = "-"
    if "Sector" not in stock_keys:
        stock_values["Sector"] = "-"
    if "Past 5 Years" not in stock_keys:
        stock_values["Past 5 Years"] = "-"
    if "Next 5 Years" not in stock_keys:
        stock_values["Next 5 Years"] = "-"


    # Get the values we need from the key statistics page
    soup = bs(key_stats, "html.parser")

    # Find all matches from the data
    for k,v in stats.items():
        search = v['search']
        for td in soup.findAll("td"):
            if td.text.startswith(search):
                value = td.findNextSibling().text
                stock_values[k] = value.strip("%")

    # If the data is missing some matches, put in placeholders
    for k,v in stats.items():
        if k not in stock_keys:
            stock_values[k] = "-"

    return stock_values

@asyncio.coroutine
def do_work(stock):
    """
    Retrieve data on each stock ticker symbol.
    """
    global stock_values, sem
    with (yield from sem):
        #print("grabbed sem", sem, stock.symbol)
        try:
            # Requet data
            key_response = yield from aiohttp.request('GET', url % stock.symbol)
            industry_response = yield from aiohttp.request('GET', id_url % stock.symbol)
            estimate_response = yield from aiohttp.request('GET', ae_url % stock.symbol)

            # Read data
            key_stats = yield from key_response.read()
            industry_details = yield from industry_response.read()
            estimates = yield from estimate_response.read()
        except:
            print("Failed to retrieve %s" % str(stock))
            key_stats = ""
            industry_details = ""
            estimates = ""

    # Pass all the HTML values, plus the stock to build_values, to construct our dict
    stock_values[stock.symbol] = build_values(key_stats, industry_details, estimates, stock)

def compare_values(val1, op, val2):
    try:
        v1 = float(val1)
        v2 = float(val2)
    except:
        return False

    expr = ("%s %s %s" % (v1, op, v2))
    return eval(expr)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("Usage: %s <stock filename>" % sys.argv[0])
        sys.exit(1)

    # stocks is a list of namedtuples
    stocks = get_stock_list(filename)

    # Pull down all the data we'll need via HTTP
    loop = asyncio.get_event_loop()
    f = asyncio.wait([do_work(stock) for stock in stocks])
    loop.run_until_complete(f)

    # Sort the stocks
    stock_values = sorted(stock_values.items(), key=lambda x: (x[1]['Sector'], x[1]['Industry'], x[1]['ROE (%)'], x[1]['Profit Margin (%)']))


    # Apply filtering.  Keep the stocks we want in stock_picks
    for stock,values in stock_values:
        # iterate over all filters and check if the stock's value is acceptable
        for label in values:
            if label in filters.keys():
                actual = values[label]
                op = filters[label][0]
                compare = filters[label][1:]
                if not compare_values(actual, op, compare):
                    keep = False

        # If the stock didn't have the label we were looking for, exclude it
        for label in filters.keys():
            if label not in values:
                found_labels = False

        if keep and found_labels:
            stock_picks[stock] = values

        # Each iteration assumes we're keeping the stock, until we filter it out.
        keep = True
        found_labels = True


    ## Apply filtering.  Keep the stocks we want in stock_picks
    #keep = True
    #found_labels = True
    #for key,value in stock_values.items():
    #    for label in stock_values[key]:
    #        if label in filters.keys():
    #            # Get values to compare
    #            actual = stock_values[key][label]
    #            op = filters[label][0]
    #            compare = filters[label][1:]
    #            if not compare_values(actual, op, compare):
    #                keep = False

    #    for label in filters.keys():
    #        if label not in stock_values[key]:
    #            found_labels = False

    #    if keep and found_labels:
    #        stock_picks[key] = value
    #    keep = True
    #    found_labels = True

    # stock_values = entire S&P500
    # stock_picks = filtered stocks
    # I'm just blowing away stock_values for now.
    stock_values = stock_picks

    # Write out values to CSV file
    with open(results_file, 'w') as csvfile:
        #writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        # get header values
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
