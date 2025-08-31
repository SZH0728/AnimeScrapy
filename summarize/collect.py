# -*- coding:utf-8 -*-
# AUTHOR: Sun

from logging import getLogger
from json import dumps

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from database.model import Cache, Detail, Score, SessionFactory
from summarize.priority import WebPriority

logger = getLogger(__name__)


class Collect(object):
    """
    @brief 数据收集和处理类

    该类负责从缓存中收集动漫数据，处理并存储到详细信息表和评分表中
    """
    def __init__(self):
        """
        @brief 初始化Collect对象

        创建WebPriority对象用于处理不同网站的数据优先级
        """
        self._web_priority: WebPriority = WebPriority()

    def main(self) -> list[tuple[str, str]]:
        """
        @brief 主循环函数，收集所有网站的数据

        通过循环遍历所有网站，收集数据并处理

        @return 返回一个元组列表，每个元组包含detail ID和图片URL
        @retval list[tuple[str, str]] 包含(detail_id, picture_url)的元组列表
        """
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
        """
        @brief 处理单个网站的数据收集周期

        查询指定网站的缓存数据，检查是否已存在对应的详细信息，如果不存在则创建，否则更新

        @param web_id 网站ID
        @param session 数据库会话对象
        @return 返回图片URL列表，格式为(detail_id, picture_url)元组
        @retval list[tuple[str, str]] 包含(detail_id, picture_url)的元组列表
        """
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

            #TODO: 当构建项目时，记得启用删除缓存数据

            session.delete(cache)
            session.commit()

        return pictures

    @staticmethod
    def update_score(cache: Cache, detail: Detail, session: Session):
        """
        @brief 更新已存在的动漫条目的评分信息

        根据缓存中的数据更新评分表中的详细评分和总评分

        @param cache 缓存数据对象
        @param detail 详细信息对象
        @param session 数据库会话对象
        """
        score: Score = session.query(Score).filter(Score.detailId == detail.id).first()  # type: ignore

        score.detailScore[str(cache.web)] = [float(cache.score), cache.vote]
        flag_modified(score, 'detailScore')
        score.vote = 0

        summarize: float = 0
        for i in score.detailScore.values():
            score.vote += i[1]
            summarize += i[0] * i[1]
        score.score = summarize / score.vote if score.vote else 0

        session.commit()

    def create_score(self, cache: Cache, session: Session) -> tuple[Detail, Score]:
        """
        @brief 为新的动漫条目创建详细信息和评分记录

        @param cache 缓存数据对象
        @param session 数据库会话对象
        @return 返回新创建的详细信息对象和评分对象
        @retval tuple[Detail, Score] 包含详细信息对象和评分对象的元组
        """
        detail, score = self.split_cache_to_detail_and_score(cache, session)

        session.add(score)

        session.commit()

        return detail, score

    @staticmethod
    def split_cache_to_detail_and_score(cache: Cache, session: Session) -> tuple[Detail, Score]:
        """
        @brief 将缓存数据分割为详细信息和评分两个对象

        @param cache 缓存数据对象
        @param session 数据库会话对象
        @return 返回详细信息对象和评分对象
        @retval tuple[Detail, Score] 包含详细信息对象和评分对象的元组
        """
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
