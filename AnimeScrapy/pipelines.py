# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, JSON, Index, CHAR, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMINT


HOST = 'localhost'
PORT = 3306
USERNAME = 'root'
PASSWORD = 'root'
DB = 'anime'

DB_URI = f'mariadb+mariadbconnector://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}'
Engine = create_engine(DB_URI)
Base = declarative_base(Engine)
SessionFactory = sessionmaker(bind=Engine)
Session = scoped_session(SessionFactory)


class Detail(Base):
    __tablename__ = 'detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    translation = Column(String(64))
    alias = Column(JSON)
    season = Column(String(3))
    time = Column(Date)
    tag = Column(JSON)
    director = Column(String(16))
    cast = Column(JSON)
    description = Column(Text)
    web = Column(TINYINT)
    webId = Column(MEDIUMINT)
    picture = Column(String(64))

    # 添加索引
    __table_args__ = (
        {'extend_existing': True},
        Index('season', 'season')
    )


class NameID(Base):
    __tablename__ = 'nameid'

    name = Column(String(64), primary_key=True)
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


class AnimescrapyPipeline:
    def process_item(self, item, spider):
        return item
