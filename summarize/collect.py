# -*- coding:utf-8 -*-
# AUTHOR: Sun

from logging import getLogger
from typing import Iterable

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from database.model import Cache, Detail, Score, NameMap, SessionFactory
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
            session.commit()
            session.delete(cache)

            detail: Detail | None = session.query(Detail).join(
                NameMap, Detail.id == NameMap.detailId
            ).filter(
                NameMap.name.in_([i for i in cache.all if i])
            ).first()

            if detail is None:
                logger.debug(f'detail {cache.name} is None, create detail')
                detail, _ = self.create_detail(cache, session)
                self.create_map(detail.all, detail, session)
                pictures.append((str(detail.id), detail.picture))
                continue

            logger.debug(f'detail {cache.name} exists, update detail')
            detail.all = list(set(detail.all + cache.all))
            self.create_map(detail.all, detail, session)
            flag_modified(detail, 'all')

            score: Score = session.query(Score).filter(Score.detailId == detail.id, Score.date == cache.date).first()  # type: ignore

            if score is None:
                logger.debug(f'score {detail.id} is None, create score')
                self.create_score(cache, detail, session)
                continue

            logger.debug(f'score {detail.id} exists, update score')
            self.update_score(cache, score)

        session.commit()

        return pictures

    @staticmethod
    def update_score(cache: Cache, score: Score):
        """
        @brief 更新已存在的动漫条目的评分信息

        根据缓存中的数据更新评分表中的详细评分和总评分

        @param cache 缓存数据对象
        @param score 评分对象
        """
        score.detailScore[str(cache.web)] = [float(cache.score), cache.vote]
        flag_modified(score, 'detailScore')
        score.vote = 0

        summarize: float = 0
        for i in score.detailScore.values():
            score.vote += i[1]
            summarize += i[0] * i[1]
        score.score = summarize / score.vote if score.vote else 0

    def create_detail(self, cache: Cache, session: Session) -> tuple[Detail, Score]:
        """
        @brief 为新的动漫条目创建详细信息和评分记录

        @param cache 缓存数据对象
        @param session 数据库会话对象
        @return 返回新创建的详细信息对象和评分对象
        @retval tuple[Detail, Score] 包含详细信息对象和评分对象的元组
        """
        detail, score = self.split_cache_to_detail_and_score(cache, session)
        return detail, score

    @staticmethod
    def create_score(cache: Cache, detail: Detail, session: Session) -> Score:
        """
        @brief 创建一个新的评分记录

        根据缓存数据为指定的详细信息条目创建一个新的评分对象，并将其添加到数据库会话中。
        评分信息包括详细评分（按网站区分）、总评分、投票数和日期。

        @param cache 缓存对象，包含从网站获取的原始评分数据
        @param detail 详细信息对象，与新创建的评分相关联
        @param session 数据库会话对象，用于添加新的评分记录

        @return 返回新创建的评分对象
        @retval Score 新创建的评分对象
        """
        score = Score(
            detailScore={cache.web: [float(cache.score), cache.vote]},
            detailId=detail.id,
            score=cache.score,
            vote=cache.vote,
            date=cache.date
        )

        session.add(score)

        return score

    @staticmethod
    def create_map(names: Iterable[str], detail: Detail, session: Session) -> list[NameMap]:
        """
        @brief 为新的动漫条目创建名称映射记录

        @param names 映射名称列表
        @param detail 详细信息对象，与新创建的映射相关联
        @param session 数据库会话对象，用于添加新的映射记录

        @return 创建的映射对象列表
        @retval list[NameMap] 新创建的映射对象列表
        """
        name_objects = []

        for name in names:
            # 检查记录是否已存在
            name_object = session.query(NameMap).filter(NameMap.name == name).first()

            if not name_object:
                name_object = NameMap(name=name, detailId=detail.id)
                session.add(name_object)

            name_objects.append(name_object)

        return name_objects

    def split_cache_to_detail_and_score(self, cache: Cache, session: Session) -> tuple[Detail, Score]:
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
            all=list(set(cache.all)),
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
        score = self.create_score(cache, detail, session)

        return detail, score


if __name__ == '__main__':
    from logging import basicConfig, DEBUG

    basicConfig(level=DEBUG)

    collect = Collect()
    collect.main()
