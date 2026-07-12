# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义所有站点路由器的抽象基类
@details SiteRouterBase 采用 Template Method 模式，与 requester/base.py 的
         RequesterBase 风格一致：handle() 为具体方法提供兜底保护，
         _do_route() 为抽象方法由子类实现域名提取、匹配与包装的完整流程。
"""

from abc import ABC, abstractmethod
from logging import getLogger

from base import HandlerBase
from data.response import ResponseBaseData
from data.gateway import SiteGatewayBaseData

logger = getLogger(__name__)


class SiteRouterBase[T: ResponseBaseData](HandlerBase[T], ABC):
    """
    @brief 所有站点路由器的抽象基类
    @details 继承 HandlerBase 参与总线调度，继承 ABC 强制子类实现 _do_route()。
             handle() 是具体方法，作为纯兜底保护；路由逻辑由子类在 _do_route() 中完成。
    """

    async def handle(self, task: T) -> SiteGatewayBaseData | None:
        """
        @brief 兜底保护：透传 _do_route() 结果，捕获未预期异常后丢弃任务
        @param task 携带响应信息的响应数据包
        @return _do_route() 的返回值；发生未预期异常时返回 None
        """
        try:
            return await self._do_route(task)
        except Exception as e:
            logger.warning(f'路由任务 {type(task).__name__} 时发生未预期异常，任务已丢弃： {e}',exc_info=True,)
            return None

    @abstractmethod
    async def _do_route(self, task: T) -> SiteGatewayBaseData | None:
        """
        @brief 执行实际路由逻辑（子类实现）
        @details 子类须在此方法中完成：域名提取、注册表匹配、数据包包装。
                 域名未注册时应在方法内记录 warning 并返回 None，不向上抛出异常。
        @param task 携带响应信息的响应数据包
        @return SiteHandleBaseData 子类：命中域名，包装成功；None：域名未注册，任务丢弃
        """


if __name__ == '__main__':
    pass
