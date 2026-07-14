# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief ORM 模型定义模块
@details 定义 SQLAlchemy 2.0 映射类 Subject 与 Rating，映射 task-01 DDL 建立的
         subjects 表与 ratings 表。本模块不负责建表，不调用 Base.metadata.create_all()，
         也不持有任何数据库连接或会话工厂。
"""

import enum
from datetime import date
from decimal import Decimal
from logging import getLogger

from sqlalchemy import Date, Integer, Numeric, SmallInteger, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, BYTEA, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = getLogger(__name__)


class Base(DeclarativeBase):
    pass


class SeasonType(enum.Enum):
    """
    @brief 番剧季度枚举
    @details 与 task-01 DDL 中 CREATE TYPE season_type AS ENUM 的值完全对应。
             由 BangumiSubjectMetaStorage 根据 air_date 月份推算写入。
    """
    winter = 'winter'
    spring = 'spring'
    summer = 'summer'
    fall   = 'fall'


class Subject(Base):
    """
    @brief 番剧基础信息 ORM 映射类
    @details 映射 subjects 表，每个 bgm_id 唯一。字段全部来自 /v0/subjects/{id} 接口，
             封面图字节（cover_image）通过后续图片下载流程写入，初始为 NULL。
             枚举列 season 引用已存在的 season_type 类型，ORM 不负责创建该类型。
    """
    __tablename__ = 'subjects'

    id:          Mapped[int]               = mapped_column(Integer, primary_key=True)
    bgm_id:      Mapped[int]               = mapped_column(Integer, nullable=False, unique=True)
    url:         Mapped[str]               = mapped_column(Text, nullable=False)

    name:        Mapped[str]               = mapped_column(Text, nullable=False)
    translation: Mapped[str]               = mapped_column(Text, nullable=False, default='')

    air_date:    Mapped[date | None]       = mapped_column(Date, nullable=True)
    year:        Mapped[int | None]        = mapped_column(SmallInteger, nullable=True)
    season:      Mapped[SeasonType | None] = mapped_column(SAEnum(SeasonType, name='season_type'), nullable=True)

    summary:     Mapped[str]               = mapped_column(Text, nullable=False, default='')
    aliases:     Mapped[list[str]]         = mapped_column(ARRAY(Text), nullable=False, default=list)
    tags:        Mapped[list[str]]         = mapped_column(ARRAY(Text), nullable=False, default=list)

    infobox:     Mapped[list]              = mapped_column(JSONB, nullable=False, default=list)

    cover_url:   Mapped[str]               = mapped_column(Text, nullable=False, default='')
    cover_image: Mapped[bytes | None]      = mapped_column(BYTEA, nullable=True)


class Rating(Base):
    """
    @brief 每日评分快照 ORM 映射类
    @details 映射 ratings 表，以 (bgm_id, date) 为业务唯一键，无外键约束。
             允许评分记录先于 subjects 记录写入，不强制顺序。
             score 使用 NUMERIC(4,2) 映射为 Python Decimal，无评分时为 NULL。
    """
    __tablename__ = 'ratings'

    id:       Mapped[int]            = mapped_column(Integer, primary_key=True)
    bgm_id:   Mapped[int]            = mapped_column(Integer, nullable=False)

    date:     Mapped[date]           = mapped_column(Date, nullable=False)
    score:    Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    total:    Mapped[int]            = mapped_column(Integer, nullable=False, default=0)

    count_1:  Mapped[int]            = mapped_column(Integer, nullable=False, default=0)
    count_2:  Mapped[int]            = mapped_column(Integer, nullable=False, default=0)
    count_3:  Mapped[int]            = mapped_column(Integer, nullable=False, default=0)
    count_4:  Mapped[int]            = mapped_column(Integer, nullable=False, default=0)
    count_5:  Mapped[int]            = mapped_column(Integer, nullable=False, default=0)
    count_6:  Mapped[int]            = mapped_column(Integer, nullable=False, default=0)
    count_7:  Mapped[int]            = mapped_column(Integer, nullable=False, default=0)
    count_8:  Mapped[int]            = mapped_column(Integer, nullable=False, default=0)
    count_9:  Mapped[int]            = mapped_column(Integer, nullable=False, default=0)
    count_10: Mapped[int]            = mapped_column(Integer, nullable=False, default=0)

    rank:     Mapped[int | None]     = mapped_column(Integer, nullable=True)

    __table_args__ = (UniqueConstraint('bgm_id', 'date'),)


if __name__ == '__main__':
    pass
