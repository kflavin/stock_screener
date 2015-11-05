from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from stocks.db import Indicators, Company, Base


class TestDatabase(object):
    def setup(self):
        # print("running setup")
        # self.base = declarative_base()
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def teardown(self):
        # print("running tearddown")
        Base.metadata.drop_all(self.engine)

    def add_one_stock(self, name, symbol, sector, industry):
        company = Company(name=name, symbol=symbol, sector=sector,
                          industry=industry)
        self.session.add(company)
        self.session.commit()
        return company

    def add_one_indicator(self, **kwargs):
        indicator = Indicators(date=kwargs['date'], buy=kwargs['buy'],
                                fcf=kwargs['fcf'], roe=kwargs['roe'])
        self.session.add(indicator)
        self.session.commit()
        return indicator

    def query_for_company(self, symbol):
        return self.session.query(Company).filter_by(symbol=symbol).all()

    def query_for_indicator(self, symbol, date):
        indicator = self.session.query(Indicators).filter_by(date = date).filter(Company.symbol == symbol).all()
        return indicator

    def test_create_stock(self):
        self.add_one_stock("Apple", "AAPL", "Technology", "Technology")
        query = self.query_for_company("AAPL")
        assert len(query) == 1
        assert query[0].name == "Apple"

    def test_create_indicator(self):
        company = self.add_one_stock("Apple", "AAPL", "Technology", "Technology")
        date = datetime.today().date()
        indicator = self.add_one_indicator(date=date, buy=True, roe=10.0, fcf=15.0)
        company.indicators.append(indicator)

        query = self.query_for_indicator("AAPL", date)
        assert len(query) == 1

