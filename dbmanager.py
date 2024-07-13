# -*- coding:utf-8 -*-
# AUTHOR: SUN
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, JSON, CHAR, DECIMAL
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMINT

HOST = 'localhost'
PORT = 3306
USERNAME = 'root'
PASSWORD = 'root'
DB = 'anime'

# 构造数据库URI
DB_URI = f'mariadb+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}'

# SQLAlchemy ORM基类
Base = declarative_base()

# 创建数据库引擎
Engine = create_engine(DB_URI)

# 创建sessionmaker绑定到数据库引擎
SessionFactory = sessionmaker(bind=Engine)

# 创建scoped_session以确保每个线程都有独立的session实例
Session = scoped_session(SessionFactory)


class Detail(Base):
    __tablename__ = 'detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    translation = Column(String(64))
    alias = Column(JSON)
    season = Column(String(3), index=True)
    time = Column(Date)
    tag = Column(JSON)
    director = Column(String(32))
    cast = Column(JSON)
    description = Column(Text)
    web = Column(TINYINT)
    webId = Column(MEDIUMINT)
    picture = Column(String(64))


class NameID(Base):
    __tablename__ = 'nameid'

    name = Column(String(128), primary_key=True)
    id = Column(Integer)


class Score(Base):
    __tablename__ = 'score'

    id = Column(Integer, primary_key=True, autoincrement=True)
    detailId = Column(Integer, nullable=False)
    detailScore = Column(JSON, nullable=False)
    score = Column(DECIMAL(3, 1))
    vote = Column(Integer)
    date = Column(Date, nullable=False)


class Web(Base):
    __tablename__ = 'web'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(CHAR(16), nullable=False)
    host = Column(CHAR(16), nullable=False)
    url_format = Column('format', String(16), nullable=False)


if __name__ == '__main__':
    Base.metadata.drop_all(Engine)
    Base.metadata.create_all(Engine)

    session = Session()
    session.add_all((
        Web(name='Bangumi', host='bangumi.tv', url_format='/subject/{}'),
        Web(name='Anikore', host='www.anikore.jp', url_format='/anime/{}'),
        Web(name='aniDB', host='anidb.net', url_format='/anime/{}'),
        Web(name='MyAnimeList', host='myanimelist.net', url_format='/anime/{}'),
    ))

    session.commit()
    session.close()
