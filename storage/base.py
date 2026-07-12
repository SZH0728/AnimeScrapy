# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义所有存储器的抽象基类
@details StorageBase 采用与 RequesterBase 完全对称的 Template Method 模式：
         handle() 作为纯兜底保护，捕获未预期异常后以 logger.error 记录并返回 None；
         子类在 _do_store() 中实现实际写入逻辑和内部类型分发。
         存储器是总线链路的终端处理单元，handle() 始终返回 None，不产出任何后续任务。
"""

from abc import ABC, abstractmethod
from logging import getLogger

from base import HandlerBase
from data.store import StoreBaseData

logger = getLogger(__name__)


class StorageBase[T: StoreBaseData](HandlerBase[T], ABC):
    """
    @brief 所有存储器的抽象基类
    @details 继承 HandlerBase 参与总线调度，继承 ABC 强制子类实现 _do_store()。
             handle() 是具体方法，作为纯兜底保护；实际写入逻辑由子类在 _do_store() 中完成。
             存储器是总线链路的终端单元，始终返回 None，不产出任何后续任务。
    """

    async def handle(self, task: T) -> None:
        """
        @brief 兜底保护：调用 _do_store()，捕获未预期异常后记录并返回 None
        @details I/O 异常（OSError）由子类在 _do_store() 内部处理，不向此处抛出。
                 此处仅处理极端情况下的未预期异常，如子类出现编程错误或运行时崩溃。
        @param task 携带待落库数据的存储数据包
        @return None 存储器始终返回 None，链路在此终止
        """
        try:
            await self._do_store(task)
        except Exception as e:
            logger.error(f'存储任务 {type(task).__name__} 时发生未预期异常，任务已丢弃：{e}', exc_info=True)

    @abstractmethod
    async def _do_store(self, task: T) -> None:
        """
        @brief 执行实际写入操作（子类实现）
        @details 子类须在此方法中完成数据的实际落库逻辑。建议使用 match...case
                 按 StoreBaseData 子类型进行分发，以支持多种数据结构写入同一后端。
                 子类内部须捕获 OSError，不重新向上抛出。
        @param task 携带待落库数据的存储数据包
        @return None
        @throws OSError 子类内部处理，不向 handle() 抛出
        """


if __name__ == '__main__':
    pass
