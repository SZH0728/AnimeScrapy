# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 异步事件总线核心模块
@details Bus 是框架的中枢调度器，持有一个无界 asyncio.Queue，
         通过类型 → HandlerBase 实例的映射表（dispatch_registry）
         将任务分发给对应处理单元，自身不含任何业务逻辑。
         信号量（Semaphore）限制并发子协程数，确保资源可控。
"""

import asyncio
from collections.abc import Iterable
from dataclasses import dataclass, field
from logging import getLogger
from typing import TYPE_CHECKING

from base import HandlerBase
from data.base import TaskBaseData

if TYPE_CHECKING:
    from scheduler import Scheduler

logger = getLogger(__name__)


@dataclass(frozen=True)
class BusConfig(object):
    """
    @brief 事件总线配置
    @details frozen=True 防止配置在运行时被意外修改。
             dispatch_registry 为 dict，不可哈希，使用 field(hash=False) 排除在 __hash__ 之外。
    """
    dispatch_registry: dict[type[TaskBaseData], HandlerBase] = field(hash=False)  # 类型到处理器实例的映射表
    max_concurrent_tasks: int                                                      # 信号量上限，控制并发子协程数


class Bus(object):
    """
    @brief 异步事件总线
    @details 框架核心调度器。持有 asyncio.Queue，主协程永远运行，
             仅负责将任务按类型路由到注册表中对应的 HandlerBase 实例，
             不包含任何业务逻辑。
    """

    def __init__(self, config: BusConfig) -> None:
        """
        @brief 初始化事件总线
        @param config 总线配置，包含类型注册表和最大并发数
        """
        self._registry: dict[type[TaskBaseData], HandlerBase] = config.dispatch_registry
        self._queue: asyncio.Queue[TaskBaseData] = asyncio.Queue()
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(config.max_concurrent_tasks)

    async def run(self, scheduler: Scheduler) -> None:
        """
        @brief 启动总线，并发运行 _dispatch 主协程和 scheduler.run
        @details 两个协程均为永久运行，使用 gather 同时启动
        @param scheduler 调度器实例，负责产生初始任务并注入队列
        """
        await asyncio.gather(self._dispatch(), scheduler.run(self))

    async def put(self, task: TaskBaseData) -> None:
        """
        @brief 向总线队列注入任务
        @details 供 Scheduler 及外部调用方使用
        @param task 待处理的任务数据包
        """
        await self._queue.put(task)

    async def _dispatch(self) -> None:
        """
        @brief 主分发协程，永不结束
        @details while True 循环从队列取任务，查找注册表，
                 为每个任务创建独立子协程（create_task），不阻塞主循环。
                 若注册表中无对应类型，记录警告后丢弃该任务。
        """
        while True:
            task: TaskBaseData = await self._queue.get()
            handler: HandlerBase | None = self._registry.get(type(task))

            if handler is None:
                logger.warning(f"注册表中找不到类型 {type(task).__name__} 对应的处理器，任务已丢弃")
                continue

            asyncio.create_task(self._run_handler(handler, task))

    async def _run_handler(self, handler: HandlerBase, task: TaskBaseData) -> None:
        """
        @brief 子协程：受信号量控制，调用处理器并将返回值投回队列
        @details 信号量限制同时运行的子协程数。对 handle() 的三种返回值
                 进行标准化处理：Iterable 逐一入队，单个 TaskBaseData 直接入队，
                 None 则链路终止。异常只记录日志，不重抛，保证总线不崩溃。
        @param handler 注册表中匹配到的处理器实例
        @param task 待处理的任务数据包
        """
        async with self._semaphore:
            try:
                result: Iterable[TaskBaseData | None] | TaskBaseData | None = await handler.handle(task)
            except Exception as e:
                logger.error(
                    f"处理器 {type(handler).__name__} 处理任务 {type(task).__name__} 时发生异常：{e}",
                    exc_info=True,
                )
                return

            if not isinstance(result, Iterable):
                result = [result]

            result_without_none: Iterable[TaskBaseData] = [i for i in result if i is not None]

            for item in result_without_none:
                await self._queue.put(item)


if __name__ == '__main__':
    pass
