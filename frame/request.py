# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file request.py
@brief HTTP请求处理模块
@details 提供HTTP请求处理功能，包括请求重试、错误处理和响应处理等功能
"""

from logging import getLogger
from asyncio import sleep

from httpx import Request, Response, AsyncClient, HTTPError

from frame.bridge import Client
from frame.config import Config, RequestConfig

logger = getLogger(__name__)


class Requester(object):
    """
    @brief 负责处理HTTP请求的类
    
    该类封装了异步HTTP请求的处理逻辑，包括请求重试、错误处理和响应处理等功能
    """
    
    def __init__(self, client: Client[Response | None, Request | None], config: Config):
        """
        @brief 初始化Requester实例
        
        @param client 用于获取请求和发送响应的客户端通道
        @param config 包含请求相关配置的配置对象
        """
        self.config: RequestConfig = config.REQUEST
        self._channel: Client[Response | None, Request | None] = client

    async def loop(self):
        """
        @brief 主循环函数，持续处理请求
        
        创建异步HTTP客户端并进入循环，不断从通道获取请求并处理，
        直到接收到关闭信号（None请求）为止。每次请求后会根据配置进行延时。
        """
        user_agent: dict[str, str] = self.config.DEFAULT_REQUEST_HEADERS
        user_agent['user-agent'] = self.config.USER_AGENT

        async with AsyncClient(headers=user_agent, timeout=self.config.DOWNLOAD_DELAY) as client:
            while True:
                request: Request | None = await self._channel.get()

                if request is None:
                    logger.info('receive close signal, stopping program')
                    break

                logger.debug(f'requesting {request.url} ...')
                response: Response | None = await self.handle_request(request, client)
                await  self.handle_response(response, request.url)

                logger.debug(f'sleeping for {self.config.DOWNLOAD_DELAY} seconds...')
                await sleep(self.config.DOWNLOAD_DELAY)

    async def handle_request(self, request: Request, client: AsyncClient) -> Response | None:
        """
        @brief 处理单个HTTP请求，包含重试机制
        
        @param request 需要发送的HTTP请求对象
        @param client 用于发送请求的异步HTTP客户端
        @return Response|None 成功时返回响应对象，失败时返回None
        """
        for i in range(self.config.MAX_RETRY):
            try:
                response: Response = await client.send(request)
                response.raise_for_status()
            except HTTPError as e:
                logger.warning(f'{request.url} failed because of {e}, retrying...', exc_info=True)
            else:
                return  response

        return None

    async def handle_response(self, response: Response | None, url: str):
        """
        @brief 处理HTTP响应结果
        
        @param response HTTP响应对象，如果请求失败则为None
        @param url 请求的URL地址
        @exception TypeError 当response类型不符合预期时抛出
        """
        if response is None:
            logger.error(f'{url} failed to the maximum number of retries')
        elif isinstance(response, Response):
            logger.debug(f'{url} succeeded')
            await self._channel.put(response)
        else:
            raise TypeError(f'response must be a Response or None, {type(response)} given')



if __name__ == '__main__':
    pass