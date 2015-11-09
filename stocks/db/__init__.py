import logging
from datetime import datetime

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import Sequence

logger = logging.getLogger(__name__)

Base = declarative_base()
engine = create_engine('sqlite:///stocks.db', echo=False)


class Company(Base):
    """
    Model for storing companies.
    """
    __tablename__ = 'company'
    id = Column(Integer, Sequence('company_id_seq'), primary_key=True)
    symbol = Column(String(50), nullable=False, unique=True)
    # name = Column(String(50), nullable=False, unique=True)
    name = Column(String(50), unique=True)
    sector = Column(String(50))
    industry = Column(String(50))

    def __repr__(self):
        return ("< Company(symbol='%s',"
                " name='%s',"
                " sector='%s',"
                " industry='%s,'"
                ")>"
                ) % (self.symbol,
                     self.name,
                     self.sector,
                     self.industry,
                     )


class Indicators(Base):
    """
    Model for storing stock indicators.
    Definitions are commented below.
    """
    __tablename__ = 'indicators'
    id = Column(Integer, Sequence('indicator_id_seq'), primary_key=True)
    date = Column(Date)     # Date
    buy = Column(Boolean)   # Is it a buy?
    roe = Column(Float)     # Return on Equity
    fcf = Column(String)    # Free Cash Flow (may contain 'M' or 'B')
    pm = Column(Float)      # Profit Margin(%)
    om = Column(Float)      # Operating Margin (%)
    tde = Column(Float)     # Total Debt/Equity (%)
    pe = Column(Float)      # Price / Earnings
    cr = Column(Float)      # Current Ratio
    peg = Column(Float)     # PEG
    eps = Column(Float)     # Diluted EPS
    div = Column(Float)     # Dividend
    pfy = Column(Float)     # Growth Past 5 Years (%)
    nfy = Column(Float)     # Growth Next 5 Years (%)
    cp = Column(Float)      # Current Price
    fp = Column(Float)      # Future Price
    b15 = Column(Float)     # 15% Buy
    b12 = Column(Float)     # 12% Buy
    company_id = Column(Integer, ForeignKey('company.id'))
    company = relationship("Company",
                           backref=backref('indicators', order_by=id))

    def __repr__(self):
        return ("<Indicators("
                " company='%s',"
                " date='%s',"
                " buy='%s',"
                " roe='%s',"
                " fcf='%s',"
                " pm='%s',"
                " b15='%s',"
                " b12='%s',"
                ")>" % (self.company.symbol,
                        self.date,
                        self.buy,
                        self.roe,
                        self.fcf,
                        self.pm,
                        self.b15,
                        self.b12,
                        )
                )


def cast_float(value):
    """
    Handle bad data.
    """
    try:
        ret = float(value)
        return ret
    except ValueError:
        return 0.0


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
            logger.debug("Skipping %s" % symbol)
            continue
        else:
            logger.debug("Count for %s is %s" % (symbol, count))

        inds = {}
        for ind, val in indicators.items():
            if ind.startswith("Checked"):
                if val:
                    inds['buy'] = True
                else:
                    inds['buy'] = False
            elif ind.startswith("ROE"):
                inds['roe'] = cast_float(val)
            elif ind.startswith("Free Cash Flow"):
                inds['fcf'] = val
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

Base.metadata.create_all(engine)
