import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from stocks.db import Base
from stocks.db.models import Company, Indicators

from stocks.config import connection_string

logger = logging.getLogger(__name__)


def cast_float(value):
    """
    Handle bad data.
    """
    if not value:
        return None

    try:
        ret = float(value)
        return ret
    except ValueError:
        # return 0.0
        # This should be okay... as long as our columns accept NULL
        return None


def populate_indicators(stock_values):
    """
    Populate the associated indicators for each stock.  There should be only
    one indicator per stock, per day.  This is hardcoded to match the values we
    pull in, and then translated to our own internal representation of each
    indicator.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    # for symbol, vals in stock_values.items():
    for symbol, indicators in stock_values:
        try:
            company = session.query(Company).filter_by(symbol=symbol).one()
        except NoResultFound:
            company = Company(symbol=symbol)
            session.add(company)
        else:
            if not company:
                company = Company(symbol=symbol)
                session.add(company)

        query = session.query(Company).filter_by(symbol=symbol)
        count = query.filter(Company.indicators.any(Indicators.date ==
                             datetime.today().date())).count()

        if count >= 1:
            # We already have today's numbers
            logger.debug("Skipping {0}".format(symbol))
            continue
        else:
            logger.debug("Count for {0} is {1}".format(symbol, count))

        inds = {}
        for ind, val in indicators.items():
            if ind.startswith("Checked"):
                if val == 'X':
                    count += 1
                    inds['buy'] = True
                else:
                    inds['buy'] = False
            elif ind.startswith("ROE"):
                inds['roe'] = cast_float(val)
            elif ind.startswith("Free Cash Flow"):
                if val[-1] == "B":
                    cval = float(val[:-1]) * 1000000000.0
                elif val[-1] == "M":
                    cval = float(val[:-1]) * 1000000.0
                elif val[-1] == "K":
                    cval = float(val[:-1]) * 1000.0
                else:
                    cval = cast_float(val)

                inds['fcf'] = cval
            elif ind.startswith("Profit Margin"):
                inds['pm'] = cast_float(val)
            elif ind.startswith("Operating Margin"):
                inds['om'] = cast_float(val)
            elif ind.startswith("Total Debt/Equity"):
                inds['tde'] = cast_float(val)
            elif ind.startswith("P/E"):
                inds['pe'] = cast_float(val)
            elif ind.startswith("cr"):
                inds['cr'] = cast_float(val)
            elif ind.startswith("PEG"):
                inds['peg'] = cast_float(val)
            elif ind.startswith("Diluted EPS"):
                inds['eps'] = cast_float(val)
            elif ind.startswith("Dividend"):
                inds['div'] = cast_float(val)
            elif ind.startswith("Past 5 Years"):
                inds['pfy'] = cast_float(val)
            elif ind.startswith("Next 5 Years"):
                inds['nfy'] = cast_float(val)
            elif ind.startswith("Curr Price"):
                inds['cp'] = cast_float(val)
            elif ind.startswith("Future Price"):
                inds['fp'] = cast_float(val)
            elif ind.startswith("15% Buy"):
                inds['b15'] = cast_float(val)
            elif ind.startswith("12% Buy"):
                inds['b12'] = cast_float(val)

        indicator = Indicators(date=datetime.today(), **inds)
        company.indicators.append(indicator)
        session.add(company)
        session.commit()

engine = create_engine(connection_string, echo=False)
Base.metadata.create_all(engine)
