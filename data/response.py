# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义响应相关数据包
@details 包含响应根基类 ResponseBaseData 及具体子类 HttpxResponseData。
         ResponseBaseData 不含第三方类型，持有原始请求任务引用及上下文字段 meta。
         meta 由 Requester 从对应的 RequestBaseData.meta 复制，确保上下文在整条链路中不丢失。
         HttpxResponseData 携带 httpx.Response 对象，使用 Httpx 前缀标明依赖。
"""

from dataclasses import dataclass, field
from logging import getLogger
from typing import Any

import httpx

from data.base import TaskBaseData
from data.request import RequestBaseData

logger = getLogger(__name__)


@dataclass(frozen=True)
class ResponseBaseData(TaskBaseData):
    """
    @brief 响应数据包根基类
    @details 持有产生此响应的原始请求任务，不含任何第三方类型字段。
             meta 字段由 Requester 从对应的 RequestBaseData.meta 复制，
             确保请求上下文在 Router → Gateway → Parser 链路中不丢失。
             Bus 据此类型路由到 SiteRouterBase。
    @param task 产生此响应的原始请求任务
    @param meta 请求上下文，由 Requester 从 RequestBaseData.meta 复制；
               不参与哈希与比较，默认空字典
    """
    task: RequestBaseData  # 产生此响应的原始请求任务
    # dict 不可哈希，kw_only 规避子类必填字段的排序约束
    meta: dict[str, Any] = field(default_factory=dict, hash=False, compare=False, kw_only=True)


@dataclass(frozen=True)
class ExampleResponseData(ResponseBaseData):
    """
    @brief ResponseBaseData 继承示例
    @details 展示最简继承写法，不添加任何字段。
    """


@dataclass(frozen=True)
class HttpxResponseData(ResponseBaseData):
    """
    @brief httpx HTTP 响应数据包
    @details 持有单个 httpx.Response 对象，由 HttpRequester 产出后投入总线，
             由 HttpxSiteRouter 消费。response 字段排除哈希与比较以兼容 frozen dataclass。
    @param response httpx 原始响应对象
    """
    # httpx.Response 不可哈希，排除该字段的哈希与比较
    response: httpx.Response = field(hash=False, compare=False)


if __name__ == '__main__':
    pass
