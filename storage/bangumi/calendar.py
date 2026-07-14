# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief BangumiCalendarStorage：评分快照存储器
@details 批量写入每日评分快照至 ratings 表（冲突静默跳过），
         随后在数据库层面查询 subjects 表找出尚未收录的新番 bgm_id，
         对新番产出 ThrottledHttpxRequestData 以驱动后续详情抓取链路。
         无新番时返回 None，链路在此终止。
"""

from logging import getLogger

import httpx
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from config import config
from data.request import ThrottledHttpxRequestData
from data.store import BangumiCalendarBatchStoreData
from database import Rating, Subject, get_session
from storage.base import StorageBase

logger = getLogger(__name__)


class BangumiCalendarStorage(StorageBase[BangumiCalendarBatchStoreData]):
    """
    @brief 评分快照存储器
    @details 批量写入 ratings 表后，通过一条 SQL 差集查询定位新番，
             对新番产出节流请求任务；无新番时终止链路。
    """

    async def _do_store(self, task: BangumiCalendarBatchStoreData) -> ThrottledHttpxRequestData | None:
        """
        @brief 写入评分快照并检测新番
        @param task 包含日期与评分条目元组的存储数据包
        @return 有新番时返回 ThrottledHttpxRequestData，否则返回 None
        """
        async with get_session() as session:
            await self._insert_ratings(session, task)
            new_ids = await self._find_new_ids(session, task)

        if not new_ids:
            return None

        return self._build_requests(new_ids)

    @staticmethod
    async def _insert_ratings(session, task: BangumiCalendarBatchStoreData) -> None:
        """
        @brief 批量写入评分快照，重复 (bgm_id, date) 静默跳过
        @param session 当前数据库会话
        @param task 存储数据包
        """
        await session.execute(
            insert(Rating).values([
                {
                    'bgm_id':   e.bgm_id,
                    'date':     task.date,
                    'score':    e.score,
                    'total':    e.total,
                    'count_1':  e.count_1,
                    'count_2':  e.count_2,
                    'count_3':  e.count_3,
                    'count_4':  e.count_4,
                    'count_5':  e.count_5,
                    'count_6':  e.count_6,
                    'count_7':  e.count_7,
                    'count_8':  e.count_8,
                    'count_9':  e.count_9,
                    'count_10': e.count_10,
                    'rank':     e.rank,
                }
                for e in task.entries
            ]).on_conflict_do_nothing(index_elements=['bgm_id', 'date'])
        )

        await session.commit()
        logger.info(f"写入 {len(task.entries)} 条 {type(task).__name__} 数据")

    @staticmethod
    async def _find_new_ids(session, task: BangumiCalendarBatchStoreData) -> list[int]:
        """
        @brief 查询 subjects 表，返回尚未收录的 bgm_id 列表
        @param session 当前数据库会话
        @param task 存储数据包
        @return 不在 subjects 表中的 bgm_id 列表
        """
        all_ids = [e.bgm_id for e in task.entries]

        result = await session.execute(
            select(Subject.bgm_id).where(Subject.bgm_id.in_(all_ids))
        )

        existing_ids = {row.bgm_id for row in result}
        return [i for i in all_ids if i not in existing_ids]

    @staticmethod
    def _build_requests(new_ids: list[int]) -> ThrottledHttpxRequestData:
        """
        @brief 为新番列表构造节流请求数据包
        @param new_ids 尚未收录的 bgm_id 列表
        @return ThrottledHttpxRequestData 实例
        """
        requests = [
            httpx.Request(
                'GET',
                f'https://api.bgm.tv/v0/subjects/{bgm_id}',
                headers={'User-Agent': config.get('bangumi', 'user_agent')},
            )
            for bgm_id in new_ids
        ]

        return ThrottledHttpxRequestData(
            retry=config.getint('bangumi', 'retry'),
            requests=requests,
            interval=config.getfloat('bangumi', 'throttle_interval_seconds'),
        )


if __name__ == '__main__':
    pass
