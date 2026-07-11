# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义所有处理单元的统一接口抽象基类
@details HandlerBase 是整个事件总线框架中 Requester、SiteRouter、SiteHandler、
         Parser、Storage 等所有处理单元共同遵守的接口契约。
         Bus 调度器的注册表值类型均为 HandlerBase，子协程通过统一调用
         handle() 方法完成任务分发与处理，实现各处理单元之间的解耦。
         本文件为纯接口定义，不含任何运行时逻辑。
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable

from data import TaskBaseData


class HandlerBase[T: TaskBaseData](ABC):
    """
    @brief 所有处理单元的根接口（抽象基类）
    @details 纯接口类，不含任何实现逻辑。所有具体处理单元
             均须继承此类并实现 handle() 方法，以保证 Bus 调度器
             可通过统一接口调用全部处理单元。
    """

    @abstractmethod
    async def handle(self, task: T) -> Iterable[TaskBaseData | None] | TaskBaseData | None:
        """
        @brief 处理一个总线数据包并返回后续任务
        @details Bus 子协程从队列取出数据包后调用此方法。子类须根据任务类型
                 完成实际处理逻辑，并将产生的后续任务以返回值形式交还给 Bus。
                 Bus 对返回值的处理规则：
                 - 可迭代对象：逐一将其中的数据包投回队列；
                 - 单个 TaskBaseData：直接投回队列；
                 - None：链路终止，无后续操作。
        @param task 从总线队列取出的数据包，实际类型为 TaskBaseData 的某个子类
        @return Iterable[TaskBaseData] 多个后续任务，由 Bus 逐一投回队列；
                TaskBaseData 单个后续任务，由 Bus 直接投回队列；
                None 无后续任务，当前处理链路终止
        """


if __name__ == '__main__':
    pass
