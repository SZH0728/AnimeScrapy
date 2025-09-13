# -*- coding:utf-8 -*-
# AUTHOR: Sun

from sqlalchemy import create_engine, Index
from sqlalchemy import Column, Integer, String, Text, Date, JSON, Enum, DECIMAL
from sqlalchemy.dialects.mysql import TINYINT, YEAR
from sqlalchemy.orm import sessionmaker, declarative_base

from constant import USERNAME, PASSWORD, HOST, PORT


DB_URI: str = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/anime'
Base = declarative_base()
Engine = create_engine(DB_URI, pool_pre_ping=True)
SessionFactory = sessionmaker(bind=Engine, autoflush=False)


class Detail(Base):
    __tablename__ = 'detail'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID，自增

    name = Column(String(64), nullable=False)  # 动画名称
    translation = Column(String(64))  # 动画译名
    all = Column(JSON)  # 所有名称组成的JSON字符串数组

    year = Column(YEAR)  # 发布年份
    season = Column(Enum('spring', 'summer', 'autumn', 'winter'))  # 发布季节

    time = Column(Date)  # 发布日期
    tag = Column(JSON)  # 标签信息，以JSON字符串数组格式存储
    description = Column(Text)  # 动画描述信息

    web = Column(TINYINT)  # 来源网站ID
    webId = Column(Integer)  # 在来源网站的ID

    picture = Column(String(128))  # 封面图片URL

    __table_args__ = (
        Index('index_year_season', 'year', 'season'),
    )


class Score(Base):
    __tablename__ = 'score'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID，自增
    detailId = Column(Integer)  # 关联的Detail表ID

    detailScore = Column(JSON)  # 详细评分信息，以JSON格式存储
    score = Column(DECIMAL(4, 2))  # 总评分
    vote = Column(Integer)  # 投票人数

    date = Column(Date)  # 评分日期

    __table_args__ = (
        Index('idx_score_detail_date', 'detailId', 'date'),
        Index('idx_score_date', 'date'),
        Index('idx_score_rank', 'score', 'vote'),
    )


class Web(Base):
    __tablename__ = 'web'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID，自增

    name = Column(String(16))  # 网站名称
    host = Column(String(16))  # 网站主机地址

    format = Column(String(16))  # 网站URL格式

    priority = Column(TINYINT)  # 网站优先级


class NameMap(Base):
    __tablename__ = 'name_map'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID，自增
    name = Column(String(64), nullable=False, unique=True)  # 动画名称，唯一
    detailId = Column(Integer, nullable=False)  # 关联的Detail表ID

    __table_args__ = (
        Index('index_name', 'name'),
    )


class Cache(Base):
    __tablename__ = 'cache'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID，自增

    name = Column(String(64))  # 动画名称
    translation = Column(String(64))  # 动画译名
    all = Column(JSON)  # 所有相关信息的JSON格式存储

    year = Column(YEAR)  # 发布年份
    season = Column(Enum('spring', 'summer', 'autumn', 'winter'))  # 发布季节

    time = Column(Date)  # 发布日期
    tag = Column(JSON)  # 标签信息，以JSON格式存储
    description = Column(Text)  # 动画描述信息

    score = Column(DECIMAL(4, 2))  # 评分
    vote = Column(Integer)  # 投票人数
    date = Column(Date, nullable=False)  # 缓存日期

    web = Column(TINYINT)  # 来源网站ID
    webId = Column(Integer)  # 在来源网站的ID

    picture = Column(String(128))  # 封面图片URL

    __table_args__ = (
        Index('idx_cache_web', 'web'),
    )


if __name__ == '__main__':
    pass
