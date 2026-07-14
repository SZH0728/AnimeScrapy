# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义所有解析器的抽象基类
@details ParserBase 采用与 RequesterBase、SiteGatewayBase 完全对称的 Template Method 模式：
         handle() 作为纯兜底保护，捕获未预期异常后以 logger.error 记录并丢弃任务；
         子类在 _do_parse() 中实现实际解析逻辑，产出新的请求任务或落库数据。
         禁止在子类中使用 yield 生成器语法，必须构造完整列表后 return。
"""

from abc import ABC, abstractmethod
from logging import getLogger

from base import HandlerBase
from data.parse import ParseBaseData
from data.request import RequestBaseData
from data.store import StoreBaseData

logger = getLogger(__name__)


class ParserBase[T: ParseBaseData](HandlerBase[T], ABC):
    """
    @brief 所有解析器的抽象基类
    @details 继承 HandlerBase 参与总线调度，继承 ABC 强制子类实现 _do_parse()。
             handle() 是具体方法，作为纯兜底保护；解析逻辑由子类在 _do_parse() 中完成。
             解析器是框架中产出最多样化结果的处理单元，可同时产出新请求与落库数据。
    """

    async def handle(self, task: T) -> list[RequestBaseData | StoreBaseData] | RequestBaseData | StoreBaseData | None:
        """
        @brief 兜底保护：透传 _do_parse() 结果，捕获未预期异常后丢弃任务
        @param task 携带 HTTP 响应信息的解析输入数据包
        @return _do_parse() 的返回值；发生未预期异常时返回 None
        """
        try:
            return await self._do_parse(task)
        except Exception as e:
            logger.error(f'解析任务 {type(task).__name__} 时发生未预期异常，任务已丢弃：{e}', exc_info=True)
            return None

    @abstractmethod
    async def _do_parse(self, task: T) -> list[RequestBaseData | StoreBaseData] | RequestBaseData | StoreBaseData | None:
        """
        @brief 执行实际解析逻辑（子类实现）
        @details 子类须在此方法中完成 HTML/JSON 解析，并构造完整结果列表后 return：
                 - 新爬取请求：构造 RequestBaseData 子类放入结果列表
                 - 落库数据：构造 StoreBaseData 子类放入结果列表
                 两者可同时产出。正常业务异常（如页面结构变更）须在此方法内部处理，不向上抛出。
                 禁止使用 yield 生成器语法，必须构造完整列表后 return。
        @param task 携带 HTTP 响应信息的解析输入数据包，通过双继承可访问 task.response
        @return list[RequestBaseData | StoreBaseData] 解析产出的后续任务列表；
                None 无任何产出或解析失败
        """


if __name__ == '__main__':
    pass
