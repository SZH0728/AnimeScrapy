# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义所有站点处理器的抽象基类
@details SiteGatewayBase 是两段路由第二段（站点层）的处理器基类，采用与
         RequesterBase 完全对称的 Template Method 模式：
         handle() 作为纯兜底保护，捕获未预期异常后丢弃任务；
         子类在 _do_handle() 中实现路径路由逻辑，根据 URL 路径判断页面类型，
         返回对应的 ParseBaseData 子类实例。
"""

from abc import ABC, abstractmethod
from logging import getLogger
from collections.abc import Iterable

from base import HandlerBase
from data.gateway import SiteGatewayBaseData
from data.parse import ParseBaseData

logger = getLogger(__name__)


class SiteGatewayBase[T: SiteGatewayBaseData](HandlerBase[T], ABC):
    """
    @brief 所有站点处理器的抽象基类
    @details 继承 HandlerBase 参与总线调度，继承 ABC 强制子类实现 _do_handle()。
             handle() 是具体方法，作为纯兜底保护；路径路由逻辑由子类在 _do_handle() 中完成。
    """

    async def handle(self, task: T) -> Iterable[ParseBaseData] | ParseBaseData | None:
        """
        @brief 兜底保护：透传 _do_handle() 结果，捕获未预期异常后丢弃任务
        @param task 携带站点响应信息的数据包
        @return _do_handle() 的返回值；发生未预期异常时返回 None
        """
        try:
            return await self._do_handle(task)
        except Exception as e:
            logger.warning(f'处理站点任务 {type(task).__name__} 时发生未预期异常，任务已丢弃：{e}', exc_info=True)
            return None

    @abstractmethod
    async def _do_handle(self, task: T) -> Iterable[ParseBaseData] | ParseBaseData | None:
        """
        @brief 执行路径路由逻辑（子类实现）
        @details 子类须在此方法中根据 URL 路径判断页面类型，返回对应的 ParseBaseData 子类实例。
                 建议使用 match...case 语法处理多路径分支。
                 路径不匹配任何已知类型时，须在方法内部记录 logger.warning 并返回 None，
                 不向上抛出异常。
        @param task 携带站点响应信息的数据包，子类可访问 task.response 和 task.task
        @return Iterable[TaskBaseData] 多个后续任务；
                TaskBaseData 单个后续任务；
                None 路径未命中或处理终止
        """


if __name__ == '__main__':
    pass
