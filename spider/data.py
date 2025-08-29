# -*- coding:utf-8 -*-
# AUTHOR: Sun

from datetime import date
from dataclasses import dataclass, field
from enum import Enum

from spider.model import Cache, Detail, Score, Web


class Season(Enum):
    SPRING = 'spring'
    SUMMER = 'summer'
    AUTUMN = 'autumn'
    WINTER = 'winter'


@dataclass
class DetailData:
    name: str
    translation: str | None = None
    names: list[str] = field(default=list)

    year: int | None = None
    season: Season | None = None

    time: date | None = None
    tag: list[str] = field(default=list)
    description: str | None = None

    web: int | None = None
    webId: int | None = None

    picture: str | None = None

    id: int | None = None

    def to_orm(self) -> Detail:
        from spider.model import Detail
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
        return cls(
            id=detail.id,
            name=detail.name,
            translation=detail.translation,
            names=detail.all,
            year=detail.year,
            season=detail.season,
            time=detail.time,
            tag=detail.tag,
            description=detail.description,
            web=detail.web,
            webId=detail.webId,
            picture=detail.picture
        )


@dataclass
class ScoreData:
    detailId: int | None = None

    detailScore: dict[int, tuple[float, int]] = field(default=None)
    score: float | None  = None
    vote: int | None = None

    date: date | None = None

    id: int | None = None

    def to_orm(self) -> Score:
        from spider.model import Score
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
    name: str | None = None
    host: str | None = None

    format: str | None = None
    priority: int | None = None

    id: int | None = None

    def to_orm(self) -> Web:
        from spider.model import Web
        return Web(
            id=self.id,
            name=self.name,
            host=self.host,
            format=self.format,
            priority=self.priority
        )

    @classmethod
    def from_orm(cls, web: Web) -> 'WebData':
        return cls(
            id=web.id,
            name=web.name,
            host=web.host,
            format=web.format,
            priority=web.priority
        )


@dataclass
class CacheData:
    name: str | None = None
    translation: str | None = None
    all_data: list[str] = field(default=list)

    year: int | None = None
    season: Season | None = None

    time: date | None = None
    tag: list[str] = field(default=list)
    description: str | None = None

    score: float | None = None
    vote: int | None = None
    date: date | None = None

    web: int | None = None
    webId: int | None = None

    picture: str | None = None

    id: int | None = None

    def to_orm(self) -> Cache:
        from spider.model import Cache
        return Cache(
            id=self.id,
            name=self.name,
            translation=self.translation,
            all=self.all_data,
            year=self.year,
            season=self.season,
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
