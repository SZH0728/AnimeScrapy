# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief requester 包初始化
@details 导出请求器基类、三个具体 HTTP 请求器、注册表及工厂函数。
         DISPATCH_REGISTRY 可直接用于 Bus 的 dispatch_registry；
         build_http_requesters() 一次性实例化全部请求器，返回值可 ** 解包合并。
"""

from base import HandlerBase
from data.base import TaskBaseData
from data.request import SingleHttpxRequestData, BatchHttpxRequestData, ThrottledHttpxRequestData
from requester.base import RequesterBase
from requester.http import SingleHttpRequester, BatchHttpRequester, ThrottledHttpRequester

DISPATCH_REGISTRY: dict[type[TaskBaseData], type[HandlerBase]] = {
    SingleHttpxRequestData: SingleHttpRequester,
    BatchHttpxRequestData: BatchHttpRequester,
    ThrottledHttpxRequestData: ThrottledHttpRequester,
}


def build_http_requesters() -> dict[type[TaskBaseData], HandlerBase]:
    """
    @brief 实例化并返回全部 HTTP 请求器的映射字典
    @details 返回值可直接用 ** 解包合并到 main.py 的 dispatch_registry。
    @return 类型 → 实例的映射，包含三种 httpx 请求策略的 Handler
    """
    return {cls: parser_cls() for cls, parser_cls in DISPATCH_REGISTRY.items()}


__all__ = [
    'RequesterBase',
    'SingleHttpRequester',
    'BatchHttpRequester',
    'ThrottledHttpRequester',
    'DISPATCH_REGISTRY',
    'build_http_requesters',
]

if __name__ == '__main__':
    pass
