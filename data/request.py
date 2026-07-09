# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义请求相关数据包
@details 包含请求根基类 RequestBaseData 及两个具体子类。
         SingleHttpxRequestData 对应单条 HTTP 请求，
         BatchHttpxRequestData 对应同一任务下的多条并发请求。
         含 httpx.Request 字段的类使用 Httpx 前缀以标明第三方依赖。
"""

from dataclasses import dataclass, field
from logging import getLogger

import httpx

from data.base import TaskBaseData

logger = getLogger(__name__)


@dataclass(frozen=True)
class RequestBaseData(TaskBaseData):
    """
    @brief 请求数据包根基类
    @details 仅携带重试计数，不含任何第三方类型字段。
             所有具体请求子类继承此类并添加实际请求载体。
    @param retry 剩余重试次数，耗尽后 Requester 将丢弃该任务
    """
    retry: int  # 剩余重试次数


@dataclass(frozen=True)
class ExampleRequestData(RequestBaseData):
    """
    @brief RequestBaseData 继承示例
    @details 展示最简继承写法，不添加任何字段。
    """


@dataclass(frozen=True)
class SingleHttpxRequestData(RequestBaseData):
    """
    @brief 单条 httpx HTTP 请求数据包
    @details 一个任务对应一条 HTTP 请求。request 字段持有完整的
             httpx.Request 对象，排除哈希与比较以兼容 frozen dataclass。
    @param request httpx 请求对象
    """
    # httpx.Request 不可哈希，排除该字段的哈希与比较
    request: httpx.Request = field(hash=False, compare=False)


@dataclass(frozen=True)
class BatchHttpxRequestData(RequestBaseData):
    """
    @brief 批量 httpx HTTP 请求数据包
    @details 一个任务对应多条并发 HTTP 请求，适用于分页批量拉取等场景。
             requests 列表中的每个元素均为独立的 httpx.Request 对象。
    @param requests httpx 请求对象列表
    """
    # list[httpx.Request] 不可哈希，排除该字段的哈希与比较
    requests: list[httpx.Request] = field(hash=False, compare=False)


if __name__ == '__main__':
    pass
