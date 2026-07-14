# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief BangumiSubjectDetailParser 实现
@details 解析 /v0/subjects/{id} 的 JSON 响应，产出 BangumiSubjectMetaStoreData。
         由 BangumiApiGateway 路由产出的 BangumiSubjectDetailParseData 进入本解析器，
         解析完成后由 BangumiSubjectMetaStorage（task-09）写入 subjects 表。
"""

from datetime import date
from logging import getLogger

from data.parse import BangumiSubjectDetailParseData
from data.store import BangumiSubjectMetaStoreData
from parser.base import ParserBase

logger = getLogger(__name__)


class BangumiSubjectDetailParser(ParserBase[BangumiSubjectDetailParseData]):
    """
    @brief /v0/subjects/{id} 响应解析器
    @details 从 API 响应中提取番剧基础信息，构造 BangumiSubjectMetaStoreData。
             别名从 infobox 的 '别名' 条目提取，标签只保留 name 字段，
             首播日期若格式异常则置为 None。
    """

    async def _do_parse(self, task: BangumiSubjectDetailParseData) -> BangumiSubjectMetaStoreData:
        """
        @brief 解析 subject 详情响应
        @param task 包含 /v0/subjects/{id} HTTP 响应的解析数据包
        @return BangumiSubjectMetaStoreData 对象
        """
        subject: dict = task.response.json()
        infobox: list[dict] = subject.get('infobox') or []

        store = BangumiSubjectMetaStoreData(
            bgm_id=subject['id'],
            url=f"https://bgm.tv/subject/{subject['id']}",
            name=subject['name'],
            translation=subject.get('name_cn', ''),
            air_date=self._parse_air_date(subject.get('date')),
            summary=subject.get('summary', ''),
            aliases=self._extract_aliases(infobox),
            tags=tuple(t['name'] for t in subject.get('tags', [])),
            infobox=infobox,
            cover_url=(subject.get('images') or {}).get('large') or '',
        )

        logger.info(f"解析 {type(task).__name__} 产出 1 个后续任务")
        return store

    @staticmethod
    def _parse_air_date(raw: str | None) -> date | None:
        """
        @brief 将 API 返回的日期字符串解析为 date 对象
        @param raw YYYY-MM-DD 格式的日期字符串，或 None
        @return 解析成功返回 date，格式异常或空值返回 None
        """
        if not raw:
            return None

        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None

    @staticmethod
    def _extract_aliases(infobox: list[dict]) -> tuple[str, ...]:
        """
        @brief 从 infobox 列表中提取 '别名' 条目的值
        @details value 为列表时提取每个字典的 'v' 字段；value 为字符串时直接包装为单元素元组。
        @param infobox API 返回的 infobox 原始列表
        @return 别名字符串元组，无别名时返回空元组
        """
        for entry in infobox:
            if entry.get('key') == '别名':
                value = entry.get('value', [])
                if isinstance(value, list):
                    return tuple(v['v'] for v in value if isinstance(v, dict) and 'v' in v)
                elif isinstance(value, str):
                    return (value,)

        return ()


if __name__ == '__main__':
    pass
