import os
import logging
from datetime import datetime

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import Sequence

print("Inside database creation")

logger = logging.getLogger(__name__)

dbfile = "stocks.db"

Base = declarative_base()
engine = create_engine('sqlite:///stocks.db', echo=False)


class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, Sequence('company_id_seq'), primary_key=True)
    symbol = Column(String(50))
    name = Column(String(50))
    sector = Column(String(50))
    industry = Column(String(50))

    def __repr__(self):
        return "<Company(symbol='%s', name='%s', sector='%s', industry='%s')>" % (
        self.symbol, self.name, self.sector, self.industry)

class Indicators(Base):
    __tablename__ = 'indicators'
    id = Column(Integer, Sequence('indicator_id_seq'), primary_key=True)
    date = Column(Date)     # Date
    buy = Column(Boolean)   # Is it a buy?
    roe = Column(Float)     # Return on Equity
    fcf = Column(String)     # Free Cash Flow
    #pm = Column(Float)      # Profit Margin(%)
    #om = Column(Float)      # Operating Margin (%)
    #tde = Column(Float)     # Total Debt/Equity (%)
    #pe = Column(Float)      # Price / Earnings
    #cr = Column(Float)      # Current Ratio
    #peg = Column(Float)     # PEG
    #eps = Column(Float)     # Diluted EPS
    #div = Column(Float)     # Dividend
    #pfy = Column(Float)     # Growth Past 5 Years (%)
    #nfy = Column(Float)     # Growth Next 5 Years (%)
    #cp = Column(Float)      # Current Price
    #fp = Column(Float)      # Future Price
    #b15 = Column(Float)     # 15% Buy
    #b12 = Column(Float)     # 12% Buy
    company_id = Column(Integer, ForeignKey('company.id'))
    company = relationship("Company", backref=backref('indicators',
        order_by=id))

    def __repr__(self):
        return "<Indicators(date='%s', buy='%s', roe='%s', fcf='%s')>" % (self.date, 
                self.buy, self.roe, self.fcf)

def populate_indicators(stock_values):
    Session = sessionmaker(bind=engine)
    session = Session()

    for symbol,vals in stock_values.items():
        try:
            company = session.query(Company).filter_by(symbol=symbol).one()
        except NoResultFound as e:
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
            logger.info("Skipping %s" % symbol)
            next;
        else:
            logger.info("Count for %s is %s" % (symbol, count))

        inds = {}
        for ind,val in vals.items():
            if ind.startswith("Checked"):
                if val:
                    inds['buy'] = True
                else:
                    inds['buy'] = False
            elif ind.startswith("ROE"):
                inds['roe'] = val
            elif ind.startswith("Free Cash Flow"):
                inds['fcf'] = val

        indicator = Indicators(date=datetime.today(), **inds)
        company.indicators.append(indicator)
        session.add(company)
        session.commit()


#Checked
#Sector
#Industry
#ROE (%)
#Free Cash Flow
#Profit Margin (%)
#Operating Margin (%)
#Total Debt/Equity
#P/E (ttm)
#P/E (forward)
#Current Ratio
#PEG
#Diluted EPS
#Dividend
#Past 5 Years (%)
#Next 5 Years (%)
#Curr Price
#Future Price
#15% Buy
#12% Buy


Base.metadata.create_all(engine)







