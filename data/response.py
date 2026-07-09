# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义响应相关数据包
@details 包含响应根基类 ResponseBaseData 及具体子类 HttpxResponseData。
         ResponseBaseData 不含第三方类型，持有原始请求任务引用。
         HttpxResponseData 携带 httpx.Response 对象，使用 Httpx 前缀标明依赖。
"""

from dataclasses import dataclass, field
from logging import getLogger

import httpx

from data.base import TaskBaseData
from data.request import RequestBaseData

logger = getLogger(__name__)


@dataclass(frozen=True)
class ResponseBaseData(TaskBaseData):
    """
    @brief 响应数据包根基类
    @details 持有产生此响应的原始请求任务，不含任何第三方类型字段。
             Bus 据此类型路由到 SiteRouter。
    @param task 产生此响应的原始请求任务
    """
    task: RequestBaseData  # 产生此响应的原始请求任务


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
             由 SiteRouter 消费。response 字段排除哈希与比较以兼容 frozen dataclass。
    @param response httpx 原始响应对象
    """
    # httpx.Response 不可哈希，排除该字段的哈希与比较
    response: httpx.Response = field(hash=False, compare=False)


if __name__ == '__main__':
    pass
