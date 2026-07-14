# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义解析器输入数据包
@details ParseBaseData 是纯路由标记基类，字段为空。
         具体解析器子类通过双继承同时获得路由标识（来自 ParseBaseData）
         和数据字段（来自 ResponseBaseData 或其子类）。
"""

from dataclasses import dataclass
from logging import getLogger

from data.base import TaskBaseData
from data.response import HttpxResponseData, ResponseBaseData

logger = getLogger(__name__)


@dataclass(frozen=True)
class ParseBaseData(TaskBaseData):
    """
    @brief 解析器输入数据包根基类
    @details 纯路由标记类，无任何字段。Bus 据此类型路由到对应 Parser。
             具体解析器子类通过双继承获得实际数据字段。
    """


@dataclass(frozen=True)
class ExampleParseData(ParseBaseData, ResponseBaseData):
    """
    @brief ParseBaseData 双继承示例
    @details 示范标准双继承写法：
               - ParseBaseData 提供总线路由标识
               - ResponseBaseData 提供 task 字段
             实际解析器子类通常将第二个父类替换为 HttpxResponseData 以携带响应体。
    """


@dataclass(frozen=True)
class BangumiCalendarParseData(ParseBaseData, HttpxResponseData):
    """
    @brief /calendar 响应解析输入
    @details 由 BangumiApiGateway 在命中 /calendar 路径时产出，
             路由到 BangumiCalendarParser。
             字段全部由继承链提供，无额外字段。
    """


@dataclass(frozen=True)
class BangumiSubjectDetailParseData(ParseBaseData, HttpxResponseData):
    """
    @brief /v0/subjects/{id} 响应解析输入
    @details 由 BangumiApiGateway 在命中 /v0/subjects/ 路径时产出，
             路由到 BangumiSubjectDetailParser。
             字段全部由继承链提供，无额外字段。
    """


@dataclass(frozen=True)
class BangumiCoverParseData(ParseBaseData, HttpxResponseData):
    """
    @brief 封面图响应解析输入
    @details 由 BangumiCoverGateway 产出，路由到 BangumiCoverParser。
             db_id 通过 meta['db_id'] 从请求链路透传，无需额外字段。
             字段全部由继承链提供，无额外字段。
    """


if __name__ == '__main__':
    pass
