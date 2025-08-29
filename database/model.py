# -*- coding:utf-8 -*-
# AUTHOR: Sun

from os import name, getenv

from sqlalchemy import create_engine, Index
from sqlalchemy import Column, Integer, String, Text, Date, JSON, Enum, DECIMAL
from sqlalchemy.dialects.mysql import TINYINT, YEAR
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URI: str = ''
if name == 'nt':
    DB_URI = f'mariadb+pymysql://root:123456@localhost:3306/anime'
elif name == 'posix':
    DB_URI = f'mariadb+pymysql://{getenv("USERNAME")}:{getenv("PASSWORD")}@{getenv("HOST")}:{getenv("PORT")}/anime'
else:
    raise Exception('Unknown OS')

Base = declarative_base()
Engine = create_engine(DB_URI, pool_pre_ping=True)
Session = sessionmaker(bind=Engine, autoflush=False)


class Detail(Base):
    __tablename__ = 'detail'

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(64), nullable=False)
    translation = Column(String(64))
    all = Column(JSON)

    year = Column(YEAR)
    season = Column(Enum('spring', 'summer', 'autumn', 'winter'))

    time = Column(Date)
    tag = Column(JSON)
    description = Column(Text)

    web = Column(TINYINT)
    webId = Column(Integer)

    picture = Column(String(128))

    __table_args__ = (
        Index('index_year_season', 'year', 'season'),
    )


class Score(Base):
    __tablename__ = 'score'

    id = Column(Integer, primary_key=True, autoincrement=True)
    detailId = Column(Integer)

    detailScore = Column(JSON)
    score = Column(DECIMAL(4, 2))
    vote = Column(Integer)

    date = Column(Date)


class Web(Base):
    __tablename__ = 'web'

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(16))
    host = Column(String(16))

    format = Column(String(16))

    priority = Column(TINYINT)


class Cache(Base):
    __tablename__ = 'cache'

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(64))
    translation = Column(String(64))
    all = Column(JSON)

    year = Column(YEAR)
    season = Column(Enum('spring', 'summer', 'autumn', 'winter'))

    time = Column(Date)
    tag = Column(JSON)
    description = Column(Text)

    score = Column(DECIMAL(4, 2))
    vote = Column(Integer)
    date = Column(Date, nullable=False)

    web = Column(TINYINT)
    webId = Column(Integer)

    picture = Column(String(128))


if __name__ == '__main__':
    pass
