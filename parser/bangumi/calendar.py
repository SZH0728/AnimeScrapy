# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 实现 Bangumi /calendar 响应解析器
@details 将 /calendar API 响应解析为 BangumiCalendarBatchStoreData，
         包含当日所有在播番剧的评分快照，不访问数据库。
"""

from datetime import date
from logging import getLogger

from data.parse import BangumiCalendarParseData
from data.request import RequestBaseData
from data.store import BangumiCalendarBatchStoreData, BangumiCalendarEntry, StoreBaseData
from parser.base import ParserBase

logger = getLogger(__name__)


class BangumiCalendarParser(ParserBase[BangumiCalendarParseData]):
    """
    @brief /calendar 响应解析器
    @details 解析 Bangumi 每周放送日历 API 响应，提取所有番剧的评分快照，
             产出单个 BangumiCalendarBatchStoreData 批次落库包。
    """

    async def _do_parse(self, task: BangumiCalendarParseData) -> list[RequestBaseData | StoreBaseData] | None:
        """
        @brief 解析 /calendar JSON 响应，产出评分批次落库包
        @param task 携带 /calendar HTTP 响应的解析输入数据包
        @return 含单个 BangumiCalendarBatchStoreData 的列表；解析失败时返回 None
        @throws 无；所有解析异常由 handle() 兜底捕获
        """
        weekday_list: list[dict] = task.response.json()

        entries: list[BangumiCalendarEntry] = []
        for weekday in weekday_list:
            for item in weekday.get('items', []):
                entries.append(self._build_entry(item))

        batch = BangumiCalendarBatchStoreData(date=date.today(), entries=tuple(entries),)
        logger.info(f"解析 {type(task).__name__} 共 {len(entries)} 条条目，产出 1 个后续任务")
        return [batch]

    @staticmethod
    def _build_entry(item: dict) -> BangumiCalendarEntry:
        """
        @brief 从单个 item 字典构造评分快照值对象
        @param item /calendar 响应中单个番剧条目字典
        @return BangumiCalendarEntry 值对象
        """
        rating = item.get('rating') or {}
        count = rating.get('count', {})
        return BangumiCalendarEntry(
            bgm_id=item['id'],
            score=rating.get('score', 0),
            total=rating.get('total', 0),
            count_1=count.get('1', 0),
            count_2=count.get('2', 0),
            count_3=count.get('3', 0),
            count_4=count.get('4', 0),
            count_5=count.get('5', 0),
            count_6=count.get('6', 0),
            count_7=count.get('7', 0),
            count_8=count.get('8', 0),
            count_9=count.get('9', 0),
            count_10=count.get('10', 0),
            rank=item.get('rank'),
        )


if __name__ == '__main__':
    pass
