import os

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import Sequence

print("Inside database creation")

dbfile = "stocks.db"

Base = declarative_base()
engine = create_engine('sqlite:///stocks.db')


class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, Sequence('company_id_seq'), primary_key=True)
    symbol = Column(String(50))
    name = Column(String(50))
    sector = Column(String(50))
    industry = Column(String(50))

    def __repr__(self):
        return "<Company(name='%s', sector='%s', industry='%s')>" % (
        self.name, self.sector, self.industry)

class Indicators(Base):
    __tablename__ = 'indicators'
    id = Column(Integer, Sequence('indicator_id_seq'), primary_key=True)
    date = Column(Date)     # Date
    buy = Column(Boolean)   # Is it a buy?
    roe = Column(Float)     # Return on Equity
    fcf = Column(Float)     # Free Cash Flow
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
    company = relationship("Company", backref=backref('indicators',
        order_by=id))

    def __repr__(self):
        return "<Indicators(date='%s', buy='%s')>" % (self.date, self.buy)

def populate_indicators(stock_values):
    Session = sessionmaker(bind=engine)
    session = Session()


    for symbol,vals in stock_values.items():
        company = session.query(Company).filter_by(symbol=symbol).one()

        if not company:
            company = Company(symbol=symbol)
            session.add(company)
            session.commit()

        indicator = Indicators(date=datetime.today())
        if k.startswith("Checked"):
        elif k.startswith("ROE"):
        elif k.startswith("Free Cash Flow"):

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







