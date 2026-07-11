# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义请求相关数据包
@details 包含请求根基类 RequestBaseData 及三个具体子类，分别对应三种请求策略：
         SingleHttpxRequestData 对应单条 HTTP 请求；
         BatchHttpxRequestData 对应并发发送的多条请求，并发量在数据类中声明；
         ThrottledHttpxRequestData 对应间隔发送的多条请求，间隔在数据类中声明。
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
class MultiHttpxRequestData(RequestBaseData):
    """
    @brief 多条 httpx 请求数据包的中间基类
    @details Batch 与 Throttled 两种策略共享 requests 字段，在此统一声明。
             子类仅需声明各自的并发控制参数（max_concurrent 或 interval）。
    @param requests httpx 请求对象列表
    """
    # list[httpx.Request] 不可哈希，排除该字段的哈希与比较
    requests: list[httpx.Request] = field(hash=False, compare=False)


@dataclass(frozen=True)
class BatchHttpxRequestData(MultiHttpxRequestData):
    """
    @brief 批量并发 httpx HTTP 请求数据包
    @details 一个任务对应多条并发 HTTP 请求，适用于分页批量拉取等场景。
             max_concurrent 控制本批次内的最大并发请求数，与 Bus 信号量相互独立。
    @param max_concurrent 本批次最大并发请求数
    """
    max_concurrent: int  # 本批次最大并发请求数


@dataclass(frozen=True)
class ThrottledHttpxRequestData(MultiHttpxRequestData):
    """
    @brief 间隔发送 httpx HTTP 请求数据包
    @details 一个任务对应多条顺序发送的 HTTP 请求，每条请求完成后等待指定间隔再发下一条。
             interval 语义为"上一条请求完成后开始计时"，末条请求完成后不等待。
    @param interval 每条请求完成后的等待时间（秒），末条不等待
    """
    interval: float  # 每条请求完成后的等待时间（秒）


if __name__ == '__main__':
    pass
