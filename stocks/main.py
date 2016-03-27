
import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
import csv
from collections import namedtuple, OrderedDict
import logging

from stocks.db.main import populate_indicators
from stocks.config import *

logger = logging.getLogger(__name__)

sem = asyncio.Semaphore(20)


def get_field(line, field, delimiter=","):
    """
    Need something smarter than split,
    because commas could be embedded inside quotes.
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
    Return a list of stocks to be operated on,
    either from CSV file or text file.
    """
    f = open(filename, "r")
    stocks = f.read().split("\n")
    f.close()

    stock_list = []

    try:
        ext = filename.split(".")[-1]
    except:
        ext = ""

    # This namedtuple is probably not necessary anymore.  The sector
    # and subsector fields won't get filled in...  we pull this data
    # later.
    if ext == "csv":
        stock_list = [Stock(symbol=get_field(line, 0),
                            sector=get_field(line, 3),
                            subsector=get_field(line, 4))
                      for line in stocks if line]
    else:
        for stock in stocks:
            stock = stock.strip()
            if stock and not stock.startswith("#"):
                stock_list.append(stock)

    return stock_list


def build_values(key_stats, industry_details, estimates, stock):
    """
    Take values given from HTTP queries
    and build a dictionary for the given stock
    """

    stock_values = OrderedDict()
    stock_values['Checked'] = ""

    # Get the values we need from industry details page
    soup = bs(industry_details, "html.parser")
    for td in soup.findAll("th"):
        if td.text.startswith("Sector:"):
            value = td.findNextSibling().text
            stock_values["Sector"] = value.strip("%")
        elif td.text.startswith("Industry:"):
            value = td.findNextSibling().text
            stock_values["Industry"] = value.strip("%")

    # Cleanup any values that were missed, by setting them to ''
    stock_keys = stock_values.keys()

    if "Industry" not in stock_keys:
        stock_values["Industry"] = "-"
    if "Sector" not in stock_keys:
        stock_values["Sector"] = "-"

    # Get the values we need from the key statistics page
    soup = bs(key_stats, "html.parser")

    try:
        curr_price = soup.findAll("span",
                                  {"class":
                                   "time_rtq_ticker"}
                                  )[0].find_next().get_text()
    except IndexError:
        logger.info("Failed to build values %s" % str(stock))
        curr_price = "-"

    # Find all matches from the data
    consumed = False
    for k, v in stats.items():
        search = v['search']
        # Because of a typo on Yahoo finance, make sure we only consume
        #  the first value (Dividend Yield is listed twice.  We want the rate.)
        for td in soup.findAll("td"):
            if td.text.startswith(search) and not consumed:
                value = td.findNextSibling().text
                stock_values[k] = value.strip("%")
                consumed = True
        consumed = False

    # If the data is missing some matches, put in placeholders
    # If there is no valid data, don't bother using the stock
    valid = False
    for k, v in stats.items():
        if k not in stock_keys:
            stock_values[k] = "-"
        else:
            if not valid:
                valid = True

    # Get the values we need from the Analyst estimate page
    soup = bs(estimates, "html.parser")
    for td in soup.findAll("td"):
        if td.text.startswith("Past 5 Years (per annum)"):
            value = td.findNextSibling().text
            stock_values["Past 5 Years (%)"] = value.strip("%")
        elif td.text.startswith("Next 5 Years (per annum)"):
            value = td.findNextSibling().text
            stock_values["Next 5 Years (%)"] = value.strip("%")

    # Cleanup any empty values
    if "Past 5 Years (%)" not in stock_keys:
        stock_values["Past 5 Years (%)"] = "-"
    if "Next 5 Years (%)" not in stock_keys:
        stock_values["Next 5 Years (%)"] = "-"

    stock_values["Curr Price"] = curr_price

    return stock_values


@asyncio.coroutine
def do_work(stock):
    """
    Retrieve data on each stock ticker symbol.
    """
    global stock_values, sem, start_worker_threads, end_worker_threads, total_threads
    start_worker_threads += 1

    with (yield from sem):
        try:
            # Request data
            key_response = yield from aiohttp.request('GET', url % stock.symbol)
            industry_response = yield from aiohttp.request('GET', id_url % stock.symbol)
            estimate_response = yield from aiohttp.request('GET', ae_url % stock.symbol)

            # Read data
            key_stats = yield from key_response.read()
            industry_details = yield from industry_response.read()
            estimates = yield from estimate_response.read()
        except Exception as e:
            logger.info("Failed to stock %s" % str(stock))
            key_stats = ""
            industry_details = ""
            estimates = ""

    # Pass all the HTML values, plus the stock to build_values, to construct our dict
    values = build_values(key_stats, industry_details, estimates, stock)
    if values is not None:
        stock_values[stock.symbol] = values

    end_worker_threads += 1
    #print("Finished %s of %s" % (worker_threads, total_threads))

def get_calculated_values():
    """
    Projected EPS and P/E
    """
    global stock_values
    calculated_values = {}

    for k,v in stock_values:
        calculated_values[k] = {}
        try:
            if float(v['Past 5 Years (%)']) > 15.0:
                calculated_values[k]['projected_eps'] = .15
            else:
                calculated_values[k]['projected_eps'] = .10
        except ValueError:
            calculated_values[k]['projected_eps'] = "-"

        try:
            if float(v['P/E (ttm)']) > 20.0:
                calculated_values[k]['projected_pe'] = 17
            else:
                calculated_values[k]['projected_pe'] = 12
        except ValueError:
            calculated_values[k]['projected_pe'] = "-"

    return calculated_values

def calculate_future_price(cv):
    """
    Calculate projected future price of the stock
    """
    global stock_values

    # Calculated compounded growth over 5 years
    for sv in stock_values:
        stock, value = sv

        eps = value['Diluted EPS']
        eps_5_yrs = eps
        try:
            growth = float(cv[stock]['projected_eps']) + 1.0
        except:
            growth = "-"

        pe = cv[stock]['projected_pe']
        dividend = value['Dividend']

        total_eps_5_yrs = 0

        #print("projected price for", stock)
        logger.debug("Project price for %s" % stock)
        for i in range(5):
            #print("eps_5_yrs = %s * %s, cum eps %s" % (eps_5_yrs, growth, total_eps_5_yrs))
            logger.debug("eps_5_yrs: %s + %s, cum eps: %s" % (eps_5_yrs, growth, total_eps_5_yrs))

            try:
                eps_5_yrs = float(eps_5_yrs) * float(growth)
                total_eps_5_yrs += eps_5_yrs
            except (ValueError, ZeroDivisionError) as e:
                eps_5_yrs = "-"
                break

        # Calculate dividend, if any
        try:
            payout_ratio = float(dividend) / float(eps)
        except (ValueError, ZeroDivisionError) as e:
            payout_ratio = 0

        total_paid_dividends = total_eps_5_yrs * payout_ratio

        # Calculate pricing data
        try:
            future_price = float(eps_5_yrs) * float(pe) + total_paid_dividends
            value['Future Price'] = '{:.4f}'.format(future_price)
            #print("final future_price = %s, eps in 5 years = %s, total eps in 5 years = %s, dividends paid = %s" % (future_price, eps_5_yrs, total_eps_5_yrs, total_paid_dividends))
            logger.debug("Future price: %s, eps in 5 years: %s, cum eps in 5 years: %s, dividends paid: %s" % (future_price, eps_5_yrs, total_eps_5_yrs, total_paid_dividends))
        except ValueError:
            value['Future Price'] = "-"
            value['15% Buy'] = "-"
            value['12% Buy'] = "-"
            value['Checked'] = "-"
            #print("final future_price = %s, eps in 5 years = %s, total eps in 5 years = %s, dividends paid = %s" % ("-", eps_5_yrs, total_eps_5_yrs, total_paid_dividends))
            logger.debug("Future price: %s, eps in 5 years: %s, cum eps in 5 years: %s, dividends paid: %s" % ("-", eps_5_yrs, total_eps_5_yrs, total_paid_dividends))
        else:
            # Calculate 12% and 15% purchase prices
            buy_price = future_price
            for i in range(5):
                buy_price = buy_price / 1.15

            value['15% Buy'] = "%.02f" % buy_price

            buy_price = future_price
            for i in range(5):
                buy_price = buy_price / 1.12

            value['12% Buy'] = "%.02f" % buy_price

            if float(value['Curr Price'].replace(",", "")) < float(value['12% Buy'].replace(",", "")):
                value['Checked'] = "X"
            else:
                value['Checked'] = ""


def compare_values(val1, op, val2):
    try:
        v1 = float(val1)
        v2 = float(val2)
    except:
        return False

    expr = ("%s %s %s" % (v1, op, v2))
    return eval(expr)


@asyncio.coroutine
def progressbar(total_threads):
    """Simple progress bar for visual feedback"""
    global worker_threads, start_worker_threads, end_worker_threads

    while True:
        yield from asyncio.sleep(0.1)
        print ("\r",  "Populating stocks: %s/%s" % (end_worker_threads+1,
                                                    total_threads), end="")

def main(filename):
    global stock_values
    global start_worker_threads
    global end_worker_threads
    global total_threads

    # stocks is a list of namedtuples
    stocks = get_stock_list(filename)

    # initialize our counters
    total_threads = len(stocks)
    start_worker_threads = 0
    end_worker_threads = 0

    # Pull down all the data we'll need via HTTP
    loop = asyncio.get_event_loop()
    f = asyncio.wait([do_work(stock) for stock in stocks])
    asyncio.async(progressbar(total_threads))
    loop.run_until_complete(f)

    # Sort the stocks
    stock_values = sorted(stock_values.items(), key=lambda x: (x[1]['Sector'], x[1]['Industry'], x[1]['ROE (%)'], x[1]['Profit Margin (%)']))

    # project EPS and P/E over next 5 years
    calculated_values = get_calculated_values()
    calculate_future_price(calculated_values)

    # Prior to filtering out the stocks we want, store the indicators in the
    # database
    print("\nPopulating database...")
    populate_indicators(stock_values)
    print("Done.")

    # Apply filtering.  Keep the stocks we want in stock_picks
    keep, found_labels = True, True
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

        # Keep "good" companies here
        if keep and found_labels:
            stock_picks[stock] = values

        # Keep all companies here
        stock_all[stock] = values

        # Each iteration assumes we're keeping the stock, until we filter it out.
        keep = True
        found_labels = True

    print("\nWriting values to file...")
    write_picks(stock_all, all_file)
    write_picks(stock_picks, picks_file)

    if stock_picks:
        print("Found {0} results: localc {1}".format(len(stock_picks),
                                                     picks_file))
    else:
        print("No results.")

    print("All results: localc {0}".format(all_file))
    print("\nDone.\n")

def write_picks(stock_values, results_file):
    """
    Given stocks and an output file, write the CSV
    """
    if stock_values:
        # Write out values to CSV file
        with open(results_file, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            # get header values
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

if __name__ == '__main__':
    main("sp1.csv")
