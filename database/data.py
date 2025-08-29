# -*- coding:utf-8 -*-
# AUTHOR: Sun

from datetime import date as date_type
from dataclasses import dataclass, field
from enum import Enum

from pytz import timezone

from database.model import Cache, Detail, Score, Web

DEFAULT_TZ = timezone('Asia/Shanghai')  # 默认时区设置为上海时区


class Season(Enum):
    SPRING = 'spring'   # 春季
    SUMMER = 'summer'   # 夏季
    AUTUMN = 'autumn'   # 秋季
    WINTER = 'winter'   # 冬季


@dataclass
class DetailData:
    # 动画详细信息数据类
    name: str                           # 动画名称
    translation: str | None = None      # 动画译名
    names: list[str] = field(default=list)  # 所有相关名称列表

    year: int | None = None             # 发布年份
    season: Season | None = None        # 发布季节

    time: date_type | None = None       # 发布日期
    tag: list[str] = field(default=list)  # 标签列表
    description: str | None = None      # 动画描述

    web: int | None = None              # 来源网站ID
    webId: int | None = None            # 在来源网站的ID

    picture: str | None = None          # 封面图片URL

    id: int | None = None               # 主键ID

    def to_orm(self) -> Detail:
        # 将DetailData对象转换为Detail ORM对象
        from database.model import Detail
        return Detail(
            name=self.name,
            translation=self.translation,
            all=self.names,
            year=self.year,
            season=self.season,
            time=self.time,
            tag=self.tag,
            description=self.description,
            web=self.web,
            webId=self.webId,
            picture=self.picture
        )

    @classmethod
    def from_orm(cls, detail: Detail) -> 'DetailData':
        # 从Detail ORM对象创建DetailData对象
        return cls(
            id=detail.id,
            name=detail.name,
            translation=detail.translation,
            names=detail.all,
            year=detail.year,
            season=detail.season.value,
            time=detail.time,
            tag=detail.tag,
            description=detail.description,
            web=detail.web,
            webId=detail.webId,
            picture=detail.picture
        )


@dataclass
class ScoreData:
    # 评分数据类
    detailId: int | None = None         # 关联的Detail表ID

    detailScore: dict[int, tuple[float, int]] = field(default=dict)  # 详细评分信息
    score: float | None  = None         # 总评分
    vote: int | None = None             # 总投票人数

    date: date_type | None = None       # 评分日期

    id: int | None = None               # 主键ID

    def to_orm(self) -> Score:
        # 将ScoreData对象转换为Score ORM对象
        from database.model import Score
        return Score(
            id=self.id,
            detailId=self.detailId,
            detailScore=self.detailScore,
            score=self.score,
            vote=self.vote,
            date=self.date
        )

    @classmethod
    def from_orm(cls, score_: Score) -> 'ScoreData':
        # 从Score ORM对象创建ScoreData对象
        return cls(
            id=score_.id,
            detailId=score_.detailId,
            detailScore=score_.detailScore,
            score=float(score_.score) if score_.score is not None else None,
            vote=score_.vote,
            date=score_.date
        )


@dataclass
class WebData:
    # 网站数据类
    name: str | None = None             # 网站名称
    host: str | None = None             # 网站主机地址

    format: str | None = None           # 网站数据格式
    priority: int | None = None         # 网站优先级

    id: int | None = None               # 主键ID

    def to_orm(self) -> Web:
        # 将WebData对象转换为Web ORM对象
        from database.model import Web
        return Web(
            id=self.id,
            name=self.name,
            host=self.host,
            format=self.format,
            priority=self.priority
        )

    @classmethod
    def from_orm(cls, web: Web) -> 'WebData':
        # 从Web ORM对象创建WebData对象
        return cls(
            id=web.id,
            name=web.name,
            host=web.host,
            format=web.format,
            priority=web.priority
        )


@dataclass
class CacheData:
    # 缓存数据类
    name: str | None = None             # 动画名称
    translation: str | None = None      # 动画译名
    all_data: list[str] = field(default=list)  # 所有相关名称列表

    year: int | None = None             # 发布年份
    season: Season | None = None        # 发布季节

    time: date_type | None = None       # 发布日期
    tag: list[str] = field(default=list)  # 标签列表
    description: str | None = None      # 动画描述

    score: float | None = None          # 评分
    vote: int | None = None             # 投票人数
    date: date_type | None = None       # 缓存日期

    web: int | None = None              # 来源网站ID
    webId: int | None = None            # 在来源网站的ID

    picture: str | None = None          # 封面图片URL

    id: int | None = None               # 主键ID

    def to_orm(self) -> Cache:
        # 将CacheData对象转换为Cache ORM对象
        from database.model import Cache
        return Cache(
            id=self.id,
            name=self.name,
            translation=self.translation,
            all=self.all_data,
            year=self.year,
            season=self.season.value,
            time=self.time,
            tag=self.tag,
            description=self.description,
            score=self.score,
            vote=self.vote,
            date=self.date,
            web=self.web,
            webId=self.webId,
            picture=self.picture
        )

    @classmethod
    def from_orm(cls, cache: Cache) -> 'CacheData':
        # 从Cache ORM对象创建CacheData对象
        return cls(
            id=cache.id,
            name=cache.name,
            translation=cache.translation,
            all_data=cache.all,
            year=cache.year,
            season=cache.season,
            time=cache.time,
            tag=cache.tag,
            description=cache.description,
            score=float(cache.score) if cache.score is not None else None,
            vote=cache.vote,
            date=cache.date,
            web=cache.web,
            webId=cache.webId,
            picture=cache.picture
        )

if __name__ == '__main__':
    pass
