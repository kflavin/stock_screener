import logging
from sqlalchemy import Sequence
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from sqlalchemy.orm import relationship, backref
from stocks.db import Base

logger = logging.getLogger(__name__)

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
                " pm='%s',"
                " om='%s',"
                " fcf='%s',"
                " cr='%s',"
                " pe='%s',"
                " tde='%s',"
                " b15='%s',"
                " b12='%s',"
                ")>" % (self.company.symbol,
                        self.date,
                        self.buy,
                        self.roe,
                        self.pm,
                        self.om,
                        self.fcf,
                        self.cr,
                        self.pe,
                        self.tde,
                        self.b15,
                        self.b12,
                        )
                )
