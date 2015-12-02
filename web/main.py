import os
from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, \
        Sequence, ForeignKey, create_engine

from stocks.db.models import Company, Indicators

user = os.environ.get("STOCKS3_USER")
password = os.environ.get("STOCKS3_PASSWORD")
db = os.environ.get("STOCKS3_DB")
host = "localhost"

engine = create_engine("postgres://{0}:{1}@{2}/{3}".format(user, password,
                                                           host, db))
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

DATABASE="MYDATABASE"

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'postgres://stocks3:stocks3@localhost/stocks3'
db = SQLAlchemy(app)


@app.route("/")
def index():
    return "Hello World, you have {0} companies"\
           .format(session.query(Company).count())


if __name__ == "__main__":
    print(app.config['DATABASE'])
    app.run()
