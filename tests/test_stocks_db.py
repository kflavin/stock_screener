from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

import pytest
from stocks.db import Indicators, Company, Base


class TestDatabase(object):
    def setup(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def teardown(self):
        Base.metadata.drop_all(self.engine)

    def add_one_stock(self, name, symbol, sector, industry):
        company = Company(name=name, symbol=symbol, sector=sector,
                          industry=industry)
        self.session.add(company)
        self.session.commit()
        return company

    def add_one_indicator(self, **kwargs):
        indicator = Indicators(date=kwargs['date'], buy=kwargs['buy'],
                               fcf=kwargs['fcf'], roe=kwargs['roe'],
                               pm=kwargs['pm'], om=kwargs['om'],
                               tde=kwargs['tde'], pe=kwargs['pe'],
                               cr=kwargs['cr'], peg=kwargs['peg'],
                               eps=kwargs['eps'], div=kwargs['div'],
                               pfy=kwargs['pfy'], nfy=kwargs['nfy'],
                               cp=kwargs['cp'], fp=kwargs['fp'],
                               b15=kwargs['b15'], b12=kwargs['b12']
                               )
        self.session.add(indicator)
        self.session.commit()
        return indicator

    def query_for_company(self, symbol):
        return self.session.query(Company).filter_by(symbol=symbol).all()

    def query_for_indicator(self, symbol, date):
        indicator = self.session.query(Indicators).filter_by(date=date).\
            filter(Company.symbol == symbol).all()
        return indicator

    def test_create_stock(self):
        self.add_one_stock("Apple", "AAPL", "Technology", "Technology")
        query = self.query_for_company("AAPL")
        assert len(query) == 1
        assert query[0].name == "Apple"

    def test_create_indicator(self):
        company = self.add_one_stock("Apple",
                                     "AAPL",
                                     "Technology",
                                     "Technology")
        date = datetime.today().date()
        indicator = self.add_one_indicator(date=date,
                                           buy=True,
                                           roe=10.0,
                                           fcf="150M",
                                           pm=15.0,
                                           om=15.0,
                                           tde=15.0,
                                           pe=15.0,
                                           cr=15.0,
                                           peg=15.0,
                                           eps=15.0,
                                           div=15.0,
                                           pfy=15.0,
                                           nfy=15.0,
                                           cp=15.0,
                                           fp=15.0,
                                           b15=15.0,
                                           b12=15.0,
                                           )
        company.indicators.append(indicator)

        query = self.query_for_indicator("AAPL", date)
        assert len(query) == 1

    def test_dupe_company(self):
        self.add_one_stock("Apple", "AAPL", "Technology", "Technology")

        with pytest.raises(IntegrityError):
            self.add_one_stock("Apple", "AAPL", "Technology", "Technology")
            query = self.query_for_company("AAPL")
            assert len(query) == 1
            assert query[0].name == "Apple"

    def test_dupe_indicator(self):
        company = self.add_one_stock("Apple",
                                     "AAPL",
                                     "Technology",
                                     "Technology")
        date = datetime.today().date()
        indicator = self.add_one_indicator(date=date,
                                           buy=True,
                                           roe=10.0,
                                           fcf="150M",
                                           pm=15.0,
                                           om=15.0,
                                           tde=15.0,
                                           pe=15.0,
                                           cr=15.0,
                                           peg=15.0,
                                           eps=15.0,
                                           div=15.0,
                                           pfy=15.0,
                                           nfy=15.0,
                                           cp=15.0,
                                           fp=15.0,
                                           b15=15.0,
                                           b12=15.0,
                                           )
        company.indicators.append(indicator)
        company.indicators.append(indicator)

        query = self.query_for_indicator("AAPL", date)
        assert len(query) == 1
