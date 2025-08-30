# -*- coding:utf-8 -*-
# AUTHOR: Sun

from logging import getLogger
from json import dumps

from sqlalchemy import func
from sqlalchemy.orm import Session

from database.model import Cache, Detail, Score, SessionFactory
from summarize.priority import WebPriority

logger = getLogger(__name__)


class Collect(object):
    def __init__(self):
        self._web_priority: WebPriority = WebPriority()

    def main(self) -> list[tuple[str, str]]:
        logger.info('Start to collect data')
        pictures: list[tuple[str, str]] = []
        with SessionFactory() as session:
            while True:
                urls: list[tuple[str, str]] = self.cycle(self._web_priority.current_web_id, session)
                pictures.extend(urls)

                condition: bool = self._web_priority.next()
                if not condition:
                    logger.info('All data has been collected')
                    break
        return pictures

    def cycle(self, web_id: int, session: Session) -> list[tuple[str, str]]:
        logger.debug(f'Start to collect data from {self._web_priority.current_web_name}')
        caches: list[Cache] = session.query(Cache).filter(Cache.web == web_id).all()  # type: ignore

        pictures: list[tuple[str, str]] = []
        for cache in caches:
            detail: Detail | None = session.query(Detail).filter(
                func.json_overlaps(Detail.all, dumps([i for i in cache.all if i]))
            ).first()

            if detail is None:
                logger.debug(f'detail {cache.name} is None, create detail')
                detail, _ = self.create_score(cache, session)
                pictures.append((str(detail.id), detail.picture))
            else:
                logger.debug(f'detail {cache.name} exists, update detail')
                self.update_score(cache, detail, session)

            # session.delete(cache)
            # session.commit()

        return pictures

    @staticmethod
    def update_score(cache: Cache, detail: Detail, session: Session):
        score: Score = session.query(Score).filter(Score.detailId == detail.id).first()  # type: ignore

        score.detailScore[cache.webId] = [float(cache.score), cache.vote]
        score.vote = 0

        summarize: float = 0
        for i in score.detailScore.values():
            score.vote += i[1]
            summarize += i[0] * i[1]
        score.score = summarize / score.vote if score.vote else 0

        session.commit()

    def create_score(self, cache: Cache, session: Session) -> tuple[Detail, Score]:
        detail, score = self.split_cache_to_detail_and_score(cache, session)

        session.add(score)

        session.commit()

        return detail, score

    @staticmethod
    def split_cache_to_detail_and_score(cache: Cache, session: Session) -> tuple[Detail, Score]:
        # 创建Detail对象并填充相应字段
        detail = Detail(
            name=cache.name,
            translation=cache.translation,
            all=cache.all,
            year=cache.year,
            season=cache.season,
            time=cache.time,
            tag=cache.tag,
            description=cache.description,
            web=cache.web,
            webId=cache.webId,
            picture=cache.picture
        )

        session.add(detail)
        session.flush()

        # 创建Score对象并填充相应字段
        score = Score(
            detailScore={cache.web: [float(cache.score), cache.vote]},
            detailId=detail.id,
            score=cache.score,
            vote=cache.vote,
            date=cache.date
        )

        return detail, score


if __name__ == '__main__':
    from logging import basicConfig, DEBUG

    basicConfig(level=DEBUG)

    collect = Collect()
    collect.main()
