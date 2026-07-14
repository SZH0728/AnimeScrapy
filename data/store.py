# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义存储数据包
@details StoreBaseData 是所有落库数据包的根基类，字段为空。
         具体存储子类继承此类并自定义所需字段。
"""

from dataclasses import dataclass, field
from datetime import date
from logging import getLogger

from data.base import TaskBaseData

logger = getLogger(__name__)


@dataclass(frozen=True)
class StoreBaseData(TaskBaseData):
    """
    @brief 存储数据包根基类
    @details 纯标记基类，无任何字段。Bus 据此类型路由到对应 Storage。
             各站点存储子类继承此类并定义自身所需的结构化字段。
    """


@dataclass(frozen=True)
class ExampleStoreData(StoreBaseData):
    """
    @brief StoreBaseData 继承示例
    @details 展示最简继承写法，不添加任何字段。
             实际存储子类应在此基础上添加具体的业务字段。
    """


@dataclass(frozen=True)
class BangumiCalendarEntry(object):
    """
    @brief 单个日历条目的评分快照值对象
    @details 不继承 StoreBaseData，由 BangumiCalendarBatchStoreData 组合持有，
             不直接投入总线。所有字段均为不可变基本类型。
    @param bgm_id Bangumi subject ID
    @param score 综合评分，无评分时为 None
    @param total 总投票数
    @param count_1 至 count_10 各分段票数
    @param rank 站内排名，未上榜时为 None
    """
    bgm_id: int           # Bangumi subject ID
    score: float | None   # 综合评分，无评分时为 None
    total: int            # 总投票数
    count_1: int          # 1分票数
    count_2: int          # 2分票数
    count_3: int          # 3分票数
    count_4: int          # 4分票数
    count_5: int          # 5分票数
    count_6: int          # 6分票数
    count_7: int          # 7分票数
    count_8: int          # 8分票数
    count_9: int          # 9分票数
    count_10: int         # 10分票数
    rank: int | None      # 站内排名，未上榜时为 None


@dataclass(frozen=True)
class BangumiCalendarBatchStoreData(StoreBaseData):
    """
    @brief 日历全量条目批次落库包
    @details 每次 /calendar 请求产出一个批次，包含当日所有在播番剧的评分快照。
             BangumiCalendarStorage 负责批量写入 ratings 表并检测新番剧。
    @param date 采集日期
    @param entries 全量日历条目元组
    """
    date: date                                 # 采集日期快照
    entries: tuple[BangumiCalendarEntry, ...]  # 全量条目


@dataclass(frozen=True)
class BangumiSubjectMetaStoreData(StoreBaseData):
    """
    @brief 番剧基础信息落库包
    @details 由 BangumiSubjectDetailParser 从 /v0/subjects/{id} 响应产出，
             BangumiSubjectMetaStorage 写入 subjects 表并 RETURNING id 获取 db_id，
             随后产出封面图请求（db_id 通过 meta 透传）。
    @param bgm_id Bangumi subject ID
    @param url 番剧页面 URL
    @param name 原名
    @param translation 中文译名（无则为空串）
    @param air_date 首播日期，解析失败时为 None
    @param summary 简介
    @param aliases 别名元组
    @param tags 标签名元组
    @param infobox infobox 原始列表（来自 API，直接存 JSONB）
    @param cover_url 封面图 URL
    """
    bgm_id: int               # Bangumi subject ID
    url: str                  # 番剧页面 URL
    name: str                 # 原名
    translation: str          # 中文译名（无则为空串）
    air_date: date | None     # 首播日期，解析失败时为 None
    summary: str              # 简介
    aliases: tuple[str, ...]  # 别名列表
    tags: tuple[str, ...]     # 标签名列表
    infobox: list[dict]       # infobox 原始列表（直接写入 JSONB 列）
    cover_url: str            # 封面图 URL


@dataclass(frozen=True)
class BangumiCoverStoreData(StoreBaseData):
    """
    @brief 封面图字节落库包
    @details 由 BangumiCoverParser 产出，BangumiCoverStorage 执行
             UPDATE subjects SET cover_image = ? WHERE id = ?。
             image_bytes 排除哈希与比较以兼容 frozen dataclass。
    @param db_id subjects 表自增主键（由 meta['db_id'] 透传）
    @param image_bytes 封面图原始字节
    """
    db_id: int                                              # subjects 表自增主键
    image_bytes: bytes = field(hash=False, compare=False)  # 封面图原始字节


if __name__ == '__main__':
    pass
