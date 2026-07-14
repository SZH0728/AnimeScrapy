# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief BangumiSubjectMetaStorage：番剧基础信息存储器
@details 将 BangumiSubjectMetaStoreData 写入 subjects 表，ON CONFLICT DO NOTHING
         处理重复写入，成功写入后返回携带 db_id 的封面图下载请求。
"""

from datetime import date
from logging import getLogger

import httpx
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from data.request import SingleHttpxRequestData
from data.store import BangumiSubjectMetaStoreData
from database import SeasonType, Subject, get_session
from storage.base import StorageBase

logger = getLogger(__name__)


class BangumiSubjectMetaStorage(StorageBase[BangumiSubjectMetaStoreData]):
    """
    @brief 番剧基础信息存储器
    @details 将 BangumiSubjectMetaStoreData 写入 subjects 表。
             ON CONFLICT DO NOTHING 处理并发或重复触发场景；
             成功写入后返回 SingleHttpxRequestData（meta 含 db_id）触发封面图下载。
    """

    async def _do_store(self, task: BangumiSubjectMetaStoreData) -> SingleHttpxRequestData | None:
        """
        @brief 写入番剧基础信息并返回封面图下载请求
        @details 推导 year/season 后执行 INSERT ON CONFLICT DO NOTHING；
                 写入成功时返回携带 db_id 的封面图请求，已存在时静默返回 None 终止链路。
        @param task 待写入的番剧基础信息数据包
        @return 携带 db_id 的 SingleHttpxRequestData；bgm_id 已存在时返回 None
        """
        year, season = self._derive_year_season(task.air_date)
        async with get_session() as session:
            row = await self._insert_subject(session, task, year, season)

        if not row:
            return None

        logger.info(f"写入 1 条 {type(task).__name__} 数据")

        if task.cover_url.strip() in ('', 'http://', 'https://'):
            return None

        return self._build_cover_request(task.cover_url, row[0])

    @staticmethod
    def _derive_year_season(air_date: date | None) -> tuple[int | None, SeasonType | None]:
        """
        @brief 根据首播日期推导播出年份与季节
        @param air_date 首播日期，为 None 时年份与季节均返回 None
        @return (year, season) 元组；air_date 为 None 时返回 (None, None)
        """
        if air_date is None:
            return None, None

        match air_date.month:
            case m if 1 <= m <= 3:
                return air_date.year, SeasonType.winter
            case m if 4 <= m <= 6:
                return air_date.year, SeasonType.spring
            case m if 7 <= m <= 9:
                return air_date.year, SeasonType.summer
            case _:
                return air_date.year, SeasonType.fall

    @staticmethod
    async def _insert_subject(session: AsyncSession, task: BangumiSubjectMetaStoreData, year: int | None, season: SeasonType | None):
        """
        @brief 执行 INSERT ON CONFLICT DO NOTHING RETURNING id
        @param session 异步数据库会话
        @param task 番剧基础信息数据包
        @param year 推导出的播出年份，可为 None
        @param season 推导出的播出季节，可为 None
        @return 含 subjects.id 的 Row 对象；bgm_id 冲突时返回 None
        """
        result = await session.execute(
            insert(Subject).values(
                bgm_id=task.bgm_id,
                url=task.url,
                name=task.name,
                translation=task.translation,
                air_date=task.air_date,
                year=year,
                season=season,
                summary=task.summary,
                aliases=list(task.aliases),
                tags=list(task.tags),
                infobox=task.infobox,
                cover_url=task.cover_url,
            ).on_conflict_do_nothing(index_elements=['bgm_id'])
            .returning(Subject.id)
        )

        await session.commit()
        return result.fetchone()

    @staticmethod
    def _build_cover_request(cover_url: str, db_id: int) -> SingleHttpxRequestData:
        """
        @brief 构造封面图下载请求
        @param cover_url 封面图原始 URL
        @param db_id subjects 表自增主键，写入 meta 供后续存储器定位目标行
        @return 携带 db_id 的 SingleHttpxRequestData
        """
        return SingleHttpxRequestData(
            retry=config.getint('bangumi', 'retry'),
            request=httpx.Request(
                'GET',
                cover_url,
                headers={'User-Agent': config.get('bangumi', 'user_agent')},
            ),
            meta={'db_id': db_id},
        )


if __name__ == '__main__':
    pass
