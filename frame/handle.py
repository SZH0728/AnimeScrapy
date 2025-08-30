# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file handle.py
@brief 处理HTTP响应并生成新请求的核心模块
@details 该模块包含处理HTTP响应、路由匹配、请求生成等功能，是爬虫框架的核心组件之一
"""

from typing import Callable, Iterable
from dataclasses import dataclass, field
from re import compile, Pattern
from logging import getLogger

from httpx import Request, Response

from frame.config import Config, HandleConfig
from frame.bridge import Client
from frame.counter import AsyncCounter

logger = getLogger(__name__)


@dataclass
class Methods(object):
    """
    @brief 存储URL路由方法的数据类
    @details 包含固定路径和正则表达式两种路由方式的处理方法映射
    """
    #: 固定路径路由映射，键为URL路径，值为处理函数
    FIX: dict[str, Callable[[Response], Request | Iterable[Request] | None]] = field(default_factory=dict)
    #: 正则表达式路由映射，键为正则表达式模式，值为处理函数
    REGEX: dict[str, Callable[[Response], Request | Iterable[Request] | None]] = field(default_factory=dict)


class MethodDict(object):
    """
    @brief 方法字典类，用于处理URL路由匹配
    @details 将Methods对象转换为可高效匹配的路由表，支持固定路径和正则表达式两种匹配方式
    """
    
    def __init__(self, methods: Methods):
        """
        @brief 初始化MethodDict对象
        @param methods Methods对象，包含FIX和REGEX路由映射
        """
        self._fix_path: dict[str, Callable[[Response], Request | Iterable[Request] | None]] = methods.FIX
        self._regex_path: list[tuple[Pattern, Callable[[Response], Request | Iterable[Request] | None]]] = []
        for regex, func in methods.REGEX.items():
            self._regex_path.append((compile(regex), func))

    def handle(self, response: Response) -> list[Request]:
        """
        @brief 根据响应的URL匹配处理方法并执行
        @param response HTTP响应对象
        @return 生成的请求列表
        """
        url: str = f'{response.url.host}{response.url.path}'

        if url in self._fix_path.keys():
            method = self._fix_path[url]
            logger.debug(f'{url} match fix path: {url}, handle with {method.__name__}')
            return self.handle_method(response, method)

        for regex, method in self._regex_path:
            if regex.match(url):
                logger.debug(f'{url} match regex: {regex}, handle with {method.__name__}')
                return self.handle_method(response, method)

        logger.warning(f'{url} not match any route, dropped')
        return []

    @staticmethod
    def handle_method(response: Response, method: Callable[[Response], Request | Iterable[Request] | None]) -> list[Request]:
        """
        @brief 执行具体的处理方法并规范化返回结果
        @param response HTTP响应对象
        @param method 处理函数
        @return 标准化后的请求列表
        @exception TypeError 当处理函数返回不支持的类型时抛出
        """
        result: Request | Iterable[Request] | None = method(response)

        if result is None:
            return []

        elif isinstance(result, Request):
            return [result]

        elif isinstance(result, Iterable):
            return list(result)

        else:
            raise TypeError(f'{method.__name__} return type error')


class Spider(object):
    """
    @brief 爬虫路由装饰器类
    @details 提供装饰器方式注册URL处理函数，构建路由映射表
    """
    
    def __init__(self):
        """
        @brief 初始化Spider对象
        """
        self._methods: Methods = Methods()
        self.config: Config = Config()

    def route(self, url: str, regex: bool = False):
        """
        @brief 路由装饰器，用于注册URL处理函数
        @param url URL路径或正则表达式
        @param regex 是否使用正则表达式匹配，默认为False
        @return 装饰器函数
        """
        def decorator(func: Callable[[Response], Request | Iterable[Request] | None]):
            """
            @brief 装饰器内部函数
            @param func 处理函数
            @return 原始处理函数
            """
            if regex:
                self._methods.REGEX[url] = func
            else:
                self._methods.FIX[url] = func
            return func

        return decorator

    def construct(self) -> MethodDict:
        """
        @brief 构建MethodDict对象
        @return MethodDict实例
        """
        return MethodDict(self._methods)


class Handle(object):
    """
    @brief 响应处理主类
    @details 负责从通道获取响应，调用对应处理函数，并将生成的新请求放回通道
    """
    
    def __init__(self, client: Client[Request | None, Response | None], config: Config, counter: AsyncCounter, methods: MethodDict):
        """
        @brief 初始化Handle对象
        @param client 通信通道客户端
        @param config 配置对象
        @param counter 异步计数器
        @param methods 方法字典对象
        """
        self.config: HandleConfig = config.HANDLE

        self._channel: Client[Request | None, Response | None] = client
        self._counter: AsyncCounter = counter

        self._methods: MethodDict =  methods

    async def loop(self):
        """
        @brief 主循环处理函数
        @details 持续从通道获取响应，处理后将新请求放回通道，直到收到关闭信号
        """
        init_requests = self.config.INIT_URLS
        for request in init_requests:
            await self._channel.put(request)

        while True:
            response: Response | None = await self._channel.get()

            if response is None:
                logger.info('receive close signal, stopping program')
                break

            logger.debug(f'handle response: {response.url}')
            requests: list[Request] = self.handle_response(response)

            logger.debug(f'add requests: {requests}')
            await self.handle_number(requests)

            for request in requests:
                self._channel.put_nowait(request)


    def handle_response(self, response: Response) -> list[Request]:
        """
        @brief 处理单个响应
        @param response HTTP响应对象
        @return 生成的请求列表
        """
        try:
            requests: list[Request] = self._methods.handle(response)
        except Exception as e:
            logger.error(f'Error occur when handle response: {e}', exc_info=True)
        else:
            return requests

        return []

    async def handle_number(self, requests: list[Request]):
        """
        @brief 处理计数器更新
        @param requests 请求列表
        """
        number: int = len(requests)

        if number:
            await self._counter.increment(number)

        await self._counter.decrement()

        left: int = await self._counter.value()
        logger.info(f'{left} webpage left to handle')


if __name__ == '__main__':
    pass