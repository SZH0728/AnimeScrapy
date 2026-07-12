# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义所有请求器的抽象基类
@details RequesterBase 是框架中唯一使用 Template Method 模式的处理单元。
         handle() 作为纯兜底保护，捕获子类未预期异常后丢弃任务；
         子类在 _do_request() 中自行完成实际网络请求、异常处理与重试逻辑，
         使用 dataclasses.replace() 创建 frozen dataclass 副本实现重试递减。
"""

from abc import ABC, abstractmethod
from logging import getLogger
from collections.abc import Iterable

from base import HandlerBase
from data.request import RequestBaseData
from data.response import ResponseBaseData

logger = getLogger(__name__)


class RequesterBase[T: RequestBaseData](HandlerBase[T], ABC):
    """
    @brief 所有请求器的抽象基类
    @details 继承 HandlerBase 参与总线调度，继承 ABC 强制子类实现 _do_request()。
             handle() 是具体方法，作为纯兜底保护；重试逻辑由各具体子类在 _do_request() 中自行管理。
    """

    async def handle(self, task: T) -> Iterable[ResponseBaseData | T | None] | ResponseBaseData | T | None:
        """
        @brief 兜底保护：透传 _do_request() 结果，捕获未预期异常后丢弃任务
        @details 不含任何重试逻辑。正常的请求失败与重试由子类在 _do_request() 内部处理，
                 不应向此处抛出异常。此处仅处理网络栈崩溃等极端情况。
        @param task 携带请求信息的请求数据包
        @return _do_request() 的返回值；发生未预期异常时返回 None
        """
        try:
            return await self._do_request(task)
        except Exception as e:
            logger.warning(f'处理任务 {type(task).__name__} 时发生未预期异常，任务已丢弃：{e}', exc_info=True)
            return None

    @abstractmethod
    async def _do_request(self, task: T) ->  Iterable[ResponseBaseData | T | None] | ResponseBaseData | T | None:
        """
        @brief 执行实际网络请求（子类实现）
        @details 子类须在此方法中完成完整的请求生命周期，包括：
                 执行 HTTP 请求、捕获请求异常、管理重试递减（使用 dataclasses.replace()）。
                 正常的请求失败不应向上抛出，应在此方法内部处理。
        @param task 携带请求信息的请求数据包
        @return ResponseBaseData 单条请求成功的响应；
                Iterable[ResponseBaseData | T] 批次结果（可含重试任务）；
                T retry 递减后的重试任务；
                None 请求失败且重试耗尽
        """


if __name__ == '__main__':
    pass
